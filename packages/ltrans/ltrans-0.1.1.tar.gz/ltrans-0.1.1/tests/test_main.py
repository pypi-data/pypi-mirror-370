from typer.testing import CliRunner
from main import app

runner = CliRunner()

def main():
    # This script runs the main application with a specific source and target directory.
    # To use this for testing, create a directory named 'test_input' and place one .ipynb file in it.
    # The translated file will be saved in 'test_output'.
    result = runner.invoke(app, ["--source", "test_input", "--target", "test_output"])
    print(result.stdout)

if __name__ == "__main__":
    main()
