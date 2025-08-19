import importlib
import pathlib

from typer.testing import CliRunner
from mdfile.mdfile import app

runner = CliRunner()

def test_update_file_from_another_file():
    """Tests the convert CLI functionality for updating a Markdown file from another text file.

    This test verifies that the convert command correctly processes a Markdown file containing
    file reference markers and updates the content between those markers with the content from
    the referenced text file, formatted as a code block.

    The test creates temporary test files, runs the CLI command, and verifies the output
    matches the expected result with the content properly inserted between markers.

    No arguments are needed as the test creates and manages its own test files.

    Raises:
        AssertionError: If the CLI command fails or if the output content doesn't match
            the expected result.
    """
    try:
        # Paths for the markdown file and the input text file
        md_file_path = pathlib.Path("123_test.md")
        input_file_path = pathlib.Path("123_test.txt")

        # Write initial content to the markdown file
        md_file_content = f"<!--file 123_test.txt-->\n<!--file end-->"
        md_file_path.write_text(md_file_content)

        # Write initial content to the input text file
        input_file_content = "Hello\nWorld"
        input_file_path.write_text(input_file_content)

        # Ensure the paths are present
        assert md_file_path.exists(), "Markdown file does not exist."
        assert input_file_path.exists(), "Input text file does not exist."

        # Run the Typer CLI app with the `convert` command
        # Pass arguments in a single string with spaces instead of as separate items
        result = runner.invoke(app, [str(md_file_path)])

        # Expected content of the updated markdown file
        expected_md_file_content = f"<!--file 123_test.txt-->\n```\nHello\nWorld\n```\n<!--file end-->"

        # Verify the CLI executed successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        # Verify the file content has been updated correctly
        updated_content = md_file_path.read_text()
        assert updated_content == expected_md_file_content, (
            f"Expected content:\n{expected_md_file_content}\nGot:\n{updated_content}"
        )
    finally:
        md_file_path.unlink(missing_ok=True)
        input_file_path.unlink(missing_ok=True)


def test_version_flag():
    """
    Test the `--version` flag.
    """
    # Call the Typer app with the --version flag
    result = runner.invoke(app, ["--version"])

    # Assert that the process exits successfully
    assert result.exit_code == 0

    # Assert that the expected version is in the output
    assert "mdfile" in result.output
    assert importlib.metadata.version("mdfile") in result.output

def test_update_file_with_output_flag():
    """Tests the convert CLI functionality with the --output flag.

    This test verifies that the convert command correctly processes a Markdown file containing
    file reference markers and writes the updated content to a separate output file when the
    --output flag is used. The original input file should remain unchanged.

    The test creates temporary test files, runs the CLI command with the --output flag,
    and verifies both that the output file has the correct content and that the input file
    remains unchanged.

    Raises:
        AssertionError: If the CLI command fails, if the output content doesn't match
            the expected result, or if the original file is modified.
    """

    # Pre-initialize variables to None to prevent
    md_file_path = None
    input_file_path = None
    output_file_path = None

    try:
        # Paths for the markdown file, input text file, and output file
        md_file_path = pathlib.Path("123_test.md")
        input_file_path = pathlib.Path("123_test.txt")
        output_file_path = pathlib.Path("123_test_output.md")

        # Write initial content to the Markdown file
        md_file_content = f"<!--file 123_test.txt-->\n<!--file end-->"
        md_file_path.write_text(md_file_content)

        # Write initial content to the input text file
        input_file_content = "Hello\nWorld"
        input_file_path.write_text(input_file_content)

        # Ensure the paths are present
        assert md_file_path.exists(), "Markdown file does not exist."
        assert input_file_path.exists(), "Input text file does not exist."

        # Run the Typer CLI app with the `convert` command and output flag
        result = runner.invoke(app, [
            str(md_file_path),
            '--output',
            str(output_file_path)
        ])

        # Expected content of the updated Markdown file
        expected_md_file_content = f"<!--file 123_test.txt-->\n```\nHello\nWorld\n```\n<!--file end-->"

        # Verify the CLI executed successfully
        assert result.exit_code == 0, f"CLI failed: {result.output}"

        # Verify the output file exists and has the correct content
        assert output_file_path.exists(), f"Output file {output_file_path} was not created."
        updated_content = output_file_path.read_text()
        assert updated_content == expected_md_file_content, (
            f"Expected content in output file:\n{expected_md_file_content}\nGot:\n{updated_content}"
        )

    finally:
        # Clean up all created files, only if the variables are not None
        if md_file_path is not None:
            md_file_path.unlink(missing_ok=True)
        if input_file_path is not None:
            input_file_path.unlink(missing_ok=True)
        if output_file_path is not None:
            output_file_path.unlink(missing_ok=True)




def test_nonexistent_file_error():
    """
    Test that passing a nonexistent file triggers an error message and exits with code 1.
    """
    # Simulate running the CLI with a nonexistent file
    result = runner.invoke(app, ["nonexistent_file.md"])

    # Assertions
    assert result.exit_code == 1  # Ensure the exit code is 1 (error)
    assert "Error: File 'nonexistent_file.md' does not exist." in result.stdout  # Check error message
