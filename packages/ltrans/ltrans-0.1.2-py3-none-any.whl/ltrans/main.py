import json
import os
from pathlib import Path
import typer
import asyncio
from typing_extensions import Annotated
from typing import Optional, List, Dict, Any

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
import logging
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv

# --- 初始设置 ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
console = Console()

# --- App and Config ---
app = typer.Typer(
    help="一个使用AI将Jupyter Notebook翻译成中文的CLI工具。",
    install_completion_help="为当前 shell 安装命令补全功能。",
    show_completion_help="显示命令补全脚本，用于手动安装。"
)
CONFIG_DIR = Path.home() / ".ltrans"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config: dict):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# --- LLM和翻译器设置 ---
def initialize_translators(providers: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    translators = []
    
    if "google" in providers and config.get("google_api_key"):
        try:
            llm_google = ChatGoogleGenerativeAI(model=config.get("gemini_model", "gemini-1.5-flash"), temperature=0, api_key=config.get("google_api_key"))
            translators.append({"name": "Google Gemini", "chain": llm_google, "provider": "google"})
        except Exception as e:
            console.print(f"  [bold red]Error: 初始化 Google Gemini 时出错: {e}[/]")

    if "qwen" in providers and config.get("qwen_api_key") and config.get("qwen_base_url"):
        try:
            llm_qwen = ChatOpenAI(model=config.get("qwen_model", "qwen-turbo"), api_key=config.get("qwen_api_key"), base_url=config.get("qwen_base_url"), temperature=0)
            translators.append({"name": "通义千问(Qwen)", "chain": llm_qwen, "provider": "qwen"})
        except Exception as e:
            console.print(f"  [bold red]Error: 初始化通义千问 (Qwen) 时出错: {e}[/]")
            
    return translators

# --- 翻译提示和链 ---
prompt_template_str = """
你是一位专业的翻译专家，擅长将技术文档翻译成中文。
请根据以下规则翻译收到的文本：

**翻译规则:**
1.  **对于Markdown文本:** 
    *   请翻译所有文字内容。
    *   请保留所有的Markdown格式，如标题 (`#`)、列表 (`-`, `*`)、链接等。

2.  **对于代码块 (Code):**
    *   **不要**翻译任何代码本身（例如，变量名、函数名、类名、关键字等）。
    *   **只**翻译代码中的注释部分（通常以 `#`, `//`, `/* ... */` 等开头）。
    *   保持代码的原始结构、缩进和格式不变。

3.  **通用规则:**
    *   请使用在中国开发者社区中通用的技术术语。
    *   请仅返回翻译后的文本，不要加任何额外的解释或介绍。

**待翻译的英文原文:**
---
{text_to_translate}
---
"""
prompt = ChatPromptTemplate.from_template(prompt_template_str)
output_parser = StrOutputParser()

# --- 核心翻译逻辑 ---
async def translate_content(text, translator_chain):
    chain = prompt | translator_chain | output_parser
    return await chain.ainvoke({"text_to_translate": text})

async def translate_cell_with_fallback(source, translators, semaphore, model_provider, max_retries=3, initial_delay=5):
    async with semaphore:
        preferred_order = sorted(translators, key=lambda t: 0 if model_provider in t['name'].lower() else 1)
        for translator in preferred_order:
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    if attempt > 0: console.print(f"[bold blue]Info: 正在使用 {translator['name']} 重试...[/]")
                    return await translate_content(source, translator["chain"])
                except ResourceExhausted:
                    console.print(f"[yellow]Warning: {translator['name']} 达到速率限制。将在 {delay} 秒后重试...[/]")
                    await asyncio.sleep(delay)
                    delay *= 2
                except Exception as e:
                    console.print(f"[red]Error: {translator['name']} 翻译时发生错误: {str(e)[:100]}...[/]")
                    await asyncio.sleep(delay)
                    delay *= 2
            console.print(f"[bold red]Error: {translator['name']} 翻译失败。[/]")
        console.print(f"[bold red]Error: 所有翻译引擎均失败，返回原文。[/]")
        return source

async def run_and_update_progress(awaitable, progress, task_id):
    result = await awaitable
    progress.update(task_id, advance=1)
    return result

async def process_notebook_content(notebook_content, translators, progress, task_id, semaphore, model_provider):
    notebook = json.loads(notebook_content)
    cells = notebook.get("cells", [])
    tasks = []
    for cell in cells:
        if cell.get("cell_type") in ["markdown", "code"] and "".join(cell.get("source", [])).strip():
            source_text = "".join(cell.get("source", []))
            translation_task = translate_cell_with_fallback(source_text, translators, semaphore, model_provider)
            tasks.append(run_and_update_progress(translation_task, progress, task_id))
        else:
            original_task = asyncio.sleep(0, result=cell)
            tasks.append(run_and_update_progress(original_task, progress, task_id))
    translated_results = await asyncio.gather(*tasks)
    final_md_parts = []
    for i, result in enumerate(translated_results):
        cell = cells[i]
        if isinstance(result, str):
            cleaned_result = result.strip().strip('-').strip()
            if cell.get("cell_type") == "code":
                lang = notebook.get("metadata", {}).get("language_info", {}).get("name", "python")
                original_source = "".join(cell.get("source", []))
                if original_source.startswith("!") or original_source.startswith("%%"):
                    lang = "shell"
                final_md_parts.append("```" + lang + "\n" + cleaned_result + "\n```")
            else:
                final_md_parts.append(cleaned_result)
        else:
            source = "".join(result.get("source", []))
            if result.get("cell_type") == "code":
                lang = notebook.get("metadata", {}).get("language_info", {}).get("name", "python")
                if source.startswith("!") or source.startswith("%%"):
                    lang = "shell"
                final_md_parts.append("```" + lang + "\n" + source + "\n```")
            else:
                final_md_parts.append(source)
    return "\n\n---\n\n".join(final_md_parts)

async def process_file(job, progress, task_id, translators, target_dir, semaphore, model_provider):
    try:
        translated_content = await process_notebook_content(job["content"], translators, progress, task_id, semaphore, model_provider)
        if not translated_content.strip():
            progress.console.print(f"[yellow]Info: 已跳过 (无内容): {job['path'].name}[/]")
            return
        target_path = target_dir / f"{job['path'].stem}.md"
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(translated_content)
        progress.console.print(f"[green]Success: {job['path'].name} -> {target_path.name}[/]")
    except Exception as e:
        progress.console.print(f"[bold red]Error: 处理 {job['path'].name} 时出错:\n{e}[/]")

# --- CLI 命令 ---

@app.command()
def config(
    google_api_key: Annotated[Optional[str], typer.Option(help="设置 Google Gemini API Key")] = None,
    qwen_api_key: Annotated[Optional[str], typer.Option(help="设置通义千问 API Key")] = None,
    qwen_base_url: Annotated[Optional[str], typer.Option(help="设置通义千问 API Base URL")] = None,
):
    """
    配置翻译服务提供商的凭据。

    如果未提供任何参数，则显示当前配置。
    """
    config_data = load_config()
    updated = False
    if google_api_key is not None: config_data["google_api_key"] = google_api_key; updated = True
    if qwen_api_key is not None: config_data["qwen_api_key"] = qwen_api_key; updated = True
    if qwen_base_url is not None: config_data["qwen_base_url"] = qwen_base_url; updated = True
    
    if updated:
        save_config(config_data)
        console.print(f"[green]Success: 配置已更新并保存到: {CONFIG_FILE}[/]")
    else:
        console.print("[bold]当前配置:[/bold]")
        if not config_data:
            console.print("[yellow]当前没有任何配置。使用 'ltrans config --help' 查看如何设置。[/]")
        else:
            console.print(json.dumps(config_data, indent=4, ensure_ascii=False))

async def check_service(name: str, chain: BaseChatModel) -> Dict[str, str]:
    """通过发送一个简单的请求来检查单个服务。"""
    try:
        await chain.ainvoke("hello")
        return {"name": name, "status": "[green]成功[/]"}
    except Exception as e:
        error_message = str(e).split('\n')[0]
        return {"name": name, "status": f"[red]失败[/red]", "reason": error_message}

@app.command()
def check():
    """检查已配置的翻译服务的连接性和凭据。"""
    console.print(Rule("[bold cyan]服务连接性检查[/bold cyan]"))
    config_data = load_config()
    
    providers_to_check = []
    if config_data.get("google_api_key"): providers_to_check.append("google")
    if config_data.get("qwen_api_key"): providers_to_check.append("qwen")

    if not providers_to_check:
        console.print("[yellow]未找到任何已配置的服务。请使用 'ltrans config' 命令进行配置。[/]")
        raise typer.Exit()

    full_config = {**os.environ, **config_data}
    translators = initialize_translators(providers_to_check, full_config)

    if not translators:
        console.print("[bold red]Error: 无法初始化任何翻译器实例。[/bold red]")
        raise typer.Exit(code=1)

    async def run_checks():
        tasks = [check_service(t["name"], t["chain"]) for t in translators]
        return await asyncio.gather(*tasks)

    results = asyncio.run(run_checks())

    table = Table(title="服务连接状态")
    table.add_column("服务名称", style="cyan", justify="right")
    table.add_column("状态", style="magenta")
    table.add_column("信息", style="white")

    for res in results:
        table.add_row(res["name"], res["status"], res.get("reason", "-"))
    
    console.print(table)

@app.command()
def translate(
    source_dir: Annotated[Path, typer.Argument(help=".ipynb 文件源目录。", exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True)],
    target_dir: Annotated[Optional[Path], typer.Argument(help=".md 文件目标目录。[默认: <源目录>-translated]", file_okay=False, dir_okay=True, writable=True, resolve_path=True)] = None,
    model_provider: Annotated[str, typer.Option("--provider", "-p", help="翻译服务提供商")] = "google",
    gemini_model: Annotated[str, typer.Option("--gemini-model", help="Gemini 模型")] = "gemini-1.5-flash",
    qwen_model: Annotated[str, typer.Option("--qwen-model", help="Qwen 模型")] = "qwen-turbo",
    google_api_key_opt: Annotated[Optional[str], typer.Option("--google-key", help="Google API Key (覆盖配置和环境变量)")] = None,
    qwen_api_key_opt: Annotated[Optional[str], typer.Option("--qwen-key", help="通义千问 API Key (覆盖配置和环境变量)")] = None,
    qwen_base_url_opt: Annotated[Optional[str], typer.Option("--qwen-url", help="通义千问 Base URL (覆盖配置和环境变量)")] = None,
    concurrency: Annotated[int, typer.Option("--concurrency", "-c", help="并发请求数量。")] = 5,
    force: Annotated[bool, typer.Option("--force", help="强制重新翻译所有文件，即使目标文件已存在。")] = False,
):
    """翻译Jupyter Notebook (.ipynb) 文件从英文到中文。"""
    config_data = load_config()
    
    google_api_key = google_api_key_opt or config_data.get("google_api_key") or os.getenv("GOOGLE_API_KEY")
    qwen_api_key = qwen_api_key_opt or config_data.get("qwen_api_key") or os.getenv("QWEN_API_KEY")
    qwen_base_url = qwen_base_url_opt or config_data.get("qwen_base_url") or os.getenv("QWEN_BASE_URL")

    full_config = {
        "google_api_key": google_api_key,
        "qwen_api_key": qwen_api_key,
        "qwen_base_url": qwen_base_url,
        "gemini_model": gemini_model,
        "qwen_model": qwen_model,
    }

    asyncio.run(run_translation(source_dir, target_dir, concurrency, model_provider, full_config, force))

async def run_translation(source_dir: Path, target_dir: Optional[Path], concurrency: int, model_provider: str, config: Dict[str, Any], force: bool):
    if not target_dir:
        target_dir = Path(f"{source_dir}-translated")
    target_dir.mkdir(exist_ok=True)
    
    console.print(Rule("[bold magenta]开始翻译任务[/bold magenta]"))
    
    table = Table(box=None, show_header=False, pad_edge=False, width=80)
    table.add_column(style="dim cyan", justify="right")
    table.add_column(style="white")
    table.add_row("源目录", str(source_dir))
    table.add_row("目标目录", str(target_dir))
    table.add_row("翻译服务", model_provider)
    table.add_row("并发数", str(concurrency))
    console.print(table)

    console.print(Rule("[bold cyan]初始化[/bold cyan]"))
    translators = initialize_translators([model_provider], config)
    if not translators:
        console.print("[bold red]Error: 无法初始化任何翻译器。请检查凭据配置。[/]")
        return

    console.print(Rule("[bold cyan]文件处理[/bold cyan]"))
    notebook_files = sorted(list(source_dir.glob("*.ipynb")))
    if not notebook_files:
        console.print(f"[yellow]Warning: 在目录 {source_dir} 中未找到 .ipynb 文件。[/]")
        return

    if force:
        files_to_process = notebook_files
    else:
        existing_md_files = {f.stem for f in target_dir.glob("*.md")}
        files_to_process = [f for f in notebook_files if f.stem not in existing_md_files]
    
    skipped_count = len(notebook_files) - len(files_to_process)
    if skipped_count > 0:
        console.print(f"[bold blue]Info: 已跳过 {skipped_count} 个已翻译的文件。使用 --force 强制重翻。[/]")

    if not files_to_process:
        console.print(Panel("[bold green]所有文件都已是最新版本，无需翻译！[/]", expand=False, border_style="green", title="任务完成"))
        return

    jobs = []
    total_cells = 0
    for file in files_to_process:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            notebook = json.loads(content)
            num_cells = len(notebook.get("cells", []))
            jobs.append({"path": file, "content": content, "cell_count": num_cells})
            total_cells += num_cells

    console.print(Rule("[bold cyan]执行翻译[/bold cyan]"))
    progress_columns = [
        SpinnerColumn('aesthetic'),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="bold magenta", complete_style="bold green"),
        TextColumn("[bold cyan]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed} of {task.total} 个单元格)"),
        TimeRemainingColumn(),
    ]
    semaphore = asyncio.Semaphore(concurrency)
    with Progress(*progress_columns, console=console) as progress:
        task = progress.add_task("[bold green]总单元格进度...", total=total_cells)
        await asyncio.gather(
            *[process_file(job, progress, task, translators, target_dir, semaphore, model_provider) for job in jobs]
        )

    console.print(Panel("[bold green]翻译完成！[/]", expand=False, border_style="green", title="任务结束"))
    console.print(f"Info: 翻译后的文件保存在: [link=file://{target_dir}]{target_dir}[/link]")

if __name__ == "__main__":
    app()