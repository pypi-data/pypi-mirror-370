
import pathlib
import importlib
import tempfile
import datetime

import pytest


from mdfile.csv_to_md import CsvToMarkdown
from mdfile.to_markdown import ToMarkdown
from mdfile.md_updater import update_process_inserts,update_file_inserts
from mdfile.md_updater import  update_markdown_from_string,update_markdown_file
from mdfile.mdfile import app

from typer.testing import CliRunner
runner = CliRunner()






def file_setup(
                md_file:str,
                output_file:str,
                input_folder="input",
                output_folder="output",
):
    input_md_file = pathlib.Path(input_folder) / md_file
    output_md_file = pathlib.Path(output_folder) / output_file

    content = input_md_file.read_text()
    expected = output_md_file.read_text()

    return content, expected

def test_update_proc_insert():
    content, expected = file_setup("example_proc_insert.md", "example_proc_insert.md")
    result = update_markdown_from_string(content, "", False)
    assert result == expected

@pytest.mark.parametrize(
    "template, expected",
    [
        ("{{$version}}", importlib.metadata.version("mdfile")),  # Test for {{$version}}
        ("{{$date}}", datetime.datetime.now().strftime("%Y-%m-%d")),  # Test for {{$date}}
        (       "Version: {{$version}}, Date: {{$date}}",
                f"Version: {importlib.metadata.version('mdfile')}, Date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
        ),
    ],
)
def test_var_version(template, expected):
    result = update_markdown_from_string(template, "", False)
    assert result == expected



def test_update_file_insert():
    content, expected = file_setup("example_python_insert.md", "example_python_insert.md")
    result = update_markdown_from_string(content, "", False)
    assert result == expected



def test_update_markdown_csv_file():
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """
    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example.md",
        output_file="example_output.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=False
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"



def test_update_markdown_csv_numbers_file():
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example_numbers.md",
        output_file="example_output_numbers.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=False
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"


def test_update_markdown_csv_br_file():
    """
    Test the update_markdown_file function using actual Markdown and CSV files.
    """

    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example.md",
        output_file="example_output_br.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold=False,
        auto_break=True  # Note the auto_break change
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"




def test_update_markdown_python_file():
    """
    Test the update_markdown_file function using actual Markdown and Python files.
    """

    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file="example_python.md",
        output_file="example_python.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold='',
        auto_break=False,
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match:\n{result}"



@pytest.mark.parametrize("lang, code_ext", [
    ("junk", "junk"),
    ("json", "json"),
    ("json", "jsonc"),
    ("markdown", "md"),
    ("markdown", "markdown"),
    ("java", "java"),
    ("c", "c"),
    ("python", "py"),

])
def test_update_markdown_code_file(lang, code_ext):
    """
    Test the update_markdown_file function using parameterized Markdown and code files
    for multiple languages.
    """
    # Use file_setup helper to get content and expected values
    content, expected_output = file_setup(
        md_file=f"example_{lang}.md",
        output_file=f"example_{lang}.md",
        input_folder="input",
        output_folder="output"
    )

    # Call the function, processing Markdown with placeholders
    result = update_markdown_from_string(
        content=content,
        bold='',
        auto_break=False,
    )

    # Assert that the result matches the expected output
    assert expected_output == result, f"Output did not match for {lang}:\n{result}"



def test_csv_to_markdown_file_not_found():
    # Define a non-existent file path
    non_existent_file = "non_existent_file.csv"

    # Ensure the file does not exist
    assert not pathlib.Path(non_existent_file).exists()

    # Create an instance of CsvToMarkdown
    converter = CsvToMarkdown(non_existent_file)

    # Check that the error message is correct
    markdown_output = converter.to_markdown()
    assert "Error" in markdown_output
    assert "Error: File 'non_existent_file.csv' not found." in markdown_output


def test_update_process_command():
    """Test that process commands are executed and their output is inserted."""
    # Test input with process placeholder
    test_input = """<!--process ls-->\n<!--process end-->"""

    # Update the markdown
    result = update_process_inserts(test_input)

    # Verify that the process command was executed
    assert "<!--process ls-->" in result
    assert "<!--process end-->" in result

    # The output should contain some files like test_mnm.py
    assert "test_mnm.py" in result

    # The output format should match our expected structure
    # Output is between the process tags, on a separate line
    lines = result.strip().split('\n')
    assert len(lines) >= 3  # At least opening tag, content, closing tag
    assert lines[0] == "<!--process ls-->"
    assert lines[-1] == "<!--process end-->"
    # There should be atleast an input
    assert 'input' in lines
    assert 'test_mnm.py' in lines
    assert 'output' in lines

    # Test using the full markdown_from_string function
    full_result = update_markdown_from_string(test_input, "", False)
    assert "<!--process ls-->" in full_result
    assert "test_mnm.py" in full_result


def test_process_cat_verifies_function_declarations():
    """
    Test that executes a 'cat test_mnm.py' command through the process insertion
    and verifies that expected function declarations are present in the result.
    """

    # Input content with process placeholder for cat command
    test_input = """<!--process cat test_mnm.py-->\n<!--process end-->"""

    # Execute the update_process_inserts function to run the cat command
    result = update_process_inserts(test_input)

    # List of function declarations we expect to find
    expected_functions = [
        "def test_update_file_from_another_file",
        "def test_update_file_with_output_flag",
        "def test_update_markdown_csv_file",
        "def test_update_markdown_csv_br_file",
        "def test_update_markdown_python_file",
        "def test_update_markdown_code_file",
        "def test_csv_to_markdown_file_not_found",
        "def test_update_process_command"
    ]

    # Verify each function declaration is present in the result
    for func_decl in expected_functions:
        assert func_decl in result, f"Function declaration '{func_decl}' not found in cat output"

    assert result.startswith("<!--process cat test_mnm.py-->\n"), "Process command header missing"
    assert "<!--process end-->" in result, "Process command footer missing"

def test_file_not_found_error():
    """
    Test that verifies a FileNotFoundError is properly raised and handled
    when attempting to insert a non-existent file using the file directive.
    """

    # Create a test input with a file directive pointing to a non-existent file
    non_existent_file = "this_file_does_not_exist_xyz789.md"

    # Test that the appropriate FileNotFoundError is raised
    with pytest.raises(FileNotFoundError) as excinfo:
        update_markdown_file(non_existent_file)

    # Verify that the error message contains the file name
    assert non_existent_file in str(excinfo.value), f"Error message should mention '{non_existent_file}'"
    assert "not found" in str(excinfo.value).lower(), "Error message should indicate file not found"


def test_process_command_timeout():
    """
    Test that verifies the process insertion properly handles a timeout
    when a command takes too long to execute.
    """

    # Create a test input with a process that will time out
    # The 'sleep' command will run for 5 seconds, but we set timeout to 1 second
    test_input = """<!--process sleep 5-->\n<!--process end-->"""

    # Execute the update_process_inserts function with a 1-second timeout
    result = update_process_inserts(test_input, timeout_sec=1)

    # Check that the result contains a timeout error message
    assert "Timeout Error" in result, "Timeout error indication missing in result"
    assert "timed out after 1 seconds" in result, "Specific timeout duration message missing"

    # Verify the process command was properly formatted in the result
    assert result.startswith("<!--process sleep 5-->"), "Process command header missing"
    assert "<!--process end-->" in result, "Process command footer missing"

def test_csv_to_markdown_empty_file():
    """
    Test that verifies CsvToMarkdown properly handles an empty CSV file
    and triggers the expected warning message.
    """


    # Create a temporary empty CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_csv:
        temp_csv_path = pathlib.Path(temp_csv.name)
        # File is intentionally left empty

    try:
        # Instantiate CsvToMarkdown with the empty file
        csv_converter = CsvToMarkdown(str(temp_csv_path))

        # Call to_markdown method which should trigger the warning
        result = csv_converter.to_markdown()

        # Check that the result contains the warning
        assert result == "The CSV file is empty."

    finally:
        # Clean up the temporary file
        if temp_csv_path.exists():
            temp_csv_path.unlink()


@pytest.mark.parametrize("input_md_filename", [
    "input/example_python_glob.md",  # First test case
    "input/example_python_glob_insert.md",  # Add more cases as needed
])
def test_glob_pattern_in_file_inserts(input_md_filename):
    """
    Test that glob patterns in file insertion tags work correctly,
    matching multiple files according to the pattern.
    """

    # Convert the filename into a Path object
    input_md = pathlib.Path(input_md_filename)

    # Check if the test file exists
    assert input_md.exists(), f"Input file {input_md_filename} does not exist."

    # Create a test markdown content with a glob pattern
    markdown_content = input_md.read_text()

    # Process the file insertions
    result = update_markdown_from_string(markdown_content, "", False)

    # Verify the results (specific assertions for the filename can be adjusted)
    # Base assertions for all test cases
    assert "```python" in result, "Python code block not found in result"



def test_bad_glob_pattern_error_message():
    """
    Test that when a glob pattern doesn't match any files, an appropriate
    error message is included in the output.
    """
    # Create a Path object for the input file
    input_md = pathlib.Path("input/example_python_bad_glob.md")

    # Read the markdown content from the file
    markdown_content = input_md.read_text()

    # Process the file insertions
    result = update_markdown_from_string(markdown_content, "", False)

    # Verify that the error message is included in the result
    expected_error = f"<!-- No files found matching pattern 'input/XFAF*.py' -->"
    assert expected_error in result, "Error message for no matching files not found in result"

    # Verify that the original tags are preserved
    assert f"<!--file input/XFAF*.py-->" in result, "Original file tag not preserved"
    assert "<!--file end-->" in result, "End file tag not preserved"

    # Make sure no Python code block was included (since no files matched)
    assert "```python" not in result or "```python" in markdown_content, "Python code block should not be added for non-matching glob"



