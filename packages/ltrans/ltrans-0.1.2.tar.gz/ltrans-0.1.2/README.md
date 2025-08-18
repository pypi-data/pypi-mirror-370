<!-- Logo -->
<p align="center">
  <h1 align="center">ltrans</h1>
  <p align="center">
    Jupyter Notebook AI Translator CLI
    <br />
    <br />
    <a href="https://github.com/xyz-liu15/ltrans/issues">Report Bug</a>
    ·
    <a href="https://github.com/xyz-liu15/ltrans/issues">Request Feature</a>
  </p>
</p>

<!-- Badges -->
<p align="center">
  <a href="https://pypi.org/project/ltrans/"><img src="https://img.shields.io/pypi/v/ltrans.svg" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/ltrans/"><img src="https://img.shields.io/pypi/pyversions/ltrans.svg" alt="Python Versions"></a>
  <a href="https://github.com/xyz-liu15/ltrans/blob/main/LICENSE"><img src="https://img.shields.io/github/license/xyz-liu15/ltrans" alt="License"></a>
</p>

[Read this in Chinese (简体中文)](README.zh.md)

---

`ltrans` is a powerful command-line interface (CLI) tool designed to translate Jupyter Notebook (`.ipynb`) files from English to Chinese. It leverages advanced AI models (like Google Gemini and Qwen) to provide accurate translations while preserving the original notebook structure, code, and only translating comments within code blocks.

## ✨ Key Features

*   **Intelligent Translation**: Translates Markdown cells and comments within code cells, leaving the code itself untouched.
*   **AI-Powered**: Utilizes leading AI models (Google Gemini, Qwen) for high-quality, context-aware translation.
*   **Efficient & Concurrent**: Processes multiple notebooks and cells concurrently for maximum speed.
*   **CLI Interface**: Easy-to-use command-line tool for seamless integration into your workflow.
*   **Smart Caching**: Skips already translated files. Use `--force` to re-translate.
*   **Configurable**: Manage API keys and settings via a simple `config` command.
*   **Connectivity Check**: Verify your API credentials and service connectivity with the `check` command.
*   **Rich Output**: Beautiful and informative console output powered by `rich`.

## 🚀 Getting Started

Follow these steps to get `ltrans` up and running.

### 1. Installation

You can install `ltrans` directly from PyPI:

```bash
pip install ltrans
```

Alternatively, for development, you can install from the source:

```bash
git clone https://github.com/xyz-liu15/ltrans.git
cd ltrans
pip install -e .
```

### 2. Configuration

Before you can translate, you need to configure your AI service API keys.

**For Google Gemini:**

```bash
ltrans config --google-api-key YOUR_GOOGLE_API_KEY
```

**For Qwen (通义千问):**

```bash
ltrans config --qwen-api-key YOUR_QWEN_API_KEY --qwen-base-url YOUR_QWEN_BASE_URL
```

You can also set keys via environment variables (`GOOGLE_API_KEY`, `QWEN_API_KEY`).

### 3. Run Your First Translation

Once configured, you can start translating!

```bash
ltrans translate path/to/your/notebooks
```

The translated Markdown files will be saved in `path/to/your/notebooks-translated/`.

## 📖 Command Reference

### `translate`

The core command to perform translations.

```bash
ltrans translate SOURCE_DIR [TARGET_DIR] [OPTIONS]
```

**Arguments:**

*   `SOURCE_DIR`: (Required) The directory containing your `.ipynb` files.
*   `TARGET_DIR`: (Optional) The directory where translated `.md` files will be saved. Defaults to `<SOURCE_DIR>-translated`.

**Options:**

*   `--provider`, `-p`: The translation service provider. `google` (default) or `qwen`.
*   `--concurrency`, `-c`: Number of concurrent requests. Defaults to `5`.
*   `--force`: Force re-translation of all files, even if they already exist in the target directory.
*   `--gemini-model`: Specify the Gemini model to use (e.g., `gemini-1.5-pro`). Defaults to `gemini-1.5-flash`.
*   `--qwen-model`: Specify the Qwen model to use. Defaults to `qwen-turbo`.
*   `--google-key`: Temporarily use a specific Google API key, overriding config.
*   `--qwen-key`: Temporarily use a specific Qwen API key, overriding config.
*   `--qwen-url`: Temporarily use a specific Qwen Base URL, overriding config.

### `config`

Manage API credentials.

```bash
ltrans config [OPTIONS]
```

If run without options, it displays the current configuration.

**Options:**

*   `--google-api-key TEXT`: Set your Google Gemini API Key.
*   `--qwen-api-key TEXT`: Set your Qwen API Key.
*   `--qwen-base-url TEXT`: Set your Qwen API Base URL.

### `check`

Verify connectivity to the configured AI services.

```bash
ltrans check
```

This command tests your API keys and reports whether the services are reachable.

## 🏛️ Architecture Overview

`ltrans` is built with Python using the Typer framework for its CLI. Here's a high-level overview of the translation process:

1.  **File Discovery**: The tool scans the source directory for `.ipynb` files.
2.  **Content Parsing**: Each notebook is read and its cells (both Markdown and code) are extracted.
3.  **Task Scheduling**: Translation tasks for each cell are created and managed by an `asyncio` event loop for concurrent processing.
4.  **Prompt Engineering**: Cell content is embedded in a carefully crafted prompt that instructs the AI model to translate only natural language text (prose and code comments) while preserving code and formatting.
5.  **AI Translation**: The `langchain` library sends the prompts to the configured AI service (Google Gemini or Qwen). The tool includes retry logic and rate limit handling.
6.  **Markdown Assembly**: The translated cell contents are assembled into a single, clean Markdown file.
7.  **File Output**: The final Markdown file is saved to the target directory.

## 🤝 Contributing

Contributions are welcome! Please feel free to open an issue to report a bug or suggest a feature, or submit a pull request with your improvements.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
