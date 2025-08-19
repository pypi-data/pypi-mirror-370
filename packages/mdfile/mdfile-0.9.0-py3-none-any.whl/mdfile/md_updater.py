import pathlib
import datetime
import re
import shlex
import subprocess
import io
from typing import Optional
from importlib.metadata import version

from rich.console import Console
from rich.panel import Panel

from .md_factory import markdown_factory

def update_file_inserts(content: str, bold: str, auto_break: bool) -> str:
    """
    Replace file insertion placeholders with file contents converted to markdown.

    Args:
        content (str): The Markdown content as a string.
        bold (str): Comma-separated values to bold.
        auto_break (bool): Whether to auto-wrap content.

    Returns:
        str: Updated content with file placeholders replaced.
    """

    # Regex to find <!--file ...--> blocks
    file_pattern = r'<!--file\s+(.+?)-->(.*?)<!--file end-->'
    file_matches = re.finditer(file_pattern, content, re.DOTALL)
    file_matches = list(file_matches)

    new_content = content

    # Process file insertions
    for match in file_matches:
        # Extract options for processing
        kwargs = {
            'bold_vals': bold.split(",") if bold else [],
            'auto_break': auto_break,
        }

        glob_pattern = match.group(1).strip()  # Extract the glob pattern
        old_block = match.group(0)  # Original block

        # Get all matching files using pathlib
        matching_files = list(pathlib.Path().glob(glob_pattern))

        # Generate Markdown for each matching file
        if matching_files:
            markdown_parts = []
            for file_path in matching_files:
                file_name = str(file_path)
                md_gen = markdown_factory(file_name, **kwargs)
                markdown_text = md_gen.to_full_markdown()
                markdown_parts.append(markdown_text)

            # Join all markdown parts with a separator
            all_markdown = "\n\n".join(markdown_parts)
            new_block = f"<!--file {glob_pattern}-->\n{all_markdown}\n<!--file end-->"
        else:
            # No files found - add a comment indicating that
            new_block = f"<!--file {glob_pattern}-->\n<!-- No files found matching pattern '{glob_pattern}' -->\n<!--file end-->"

        new_content = new_content.replace(old_block, new_block,1)

    return new_content

def update_file_placeholders(content: str, bold: Optional[str] = None, auto_break: bool = False) -> str:
    """
    Replace {{file file_name.ext}} placeholders with file contents converted to markdown.
    If no files match the given pattern, a warning message is provided in place of the placeholder.

    Args:
        content (str): The Markdown content containing file placeholders.
        bold (Optional[str]): Comma-separated values to bold.
        auto_break (bool): Whether to auto-wrap content.

    Returns:
        str: Updated content with file placeholders replaced, or warnings if no files are found.
    """
    # Regex to find {{file file_name.ext}} placeholders
    placeholder_pattern = r"\{\{file\s+(.+?)\}\}"
    placeholders = re.finditer(placeholder_pattern, content)

    new_content = content

    # Process each file placeholder
    for placeholder in placeholders:
        file_pattern = placeholder.group(1).strip()  # Extract file pattern
        full_placeholder = placeholder.group(0)  # The complete `{{file ...}}` block

        # Prepare options for file processing
        kwargs = {
            'bold_vals': bold.split(",") if bold else [],
            'auto_break': auto_break,
        }

        # Get matching files based on the pattern
        matching_files = list(pathlib.Path().glob(file_pattern))

        if matching_files:
            # Process found files and convert them to markdown
            markdown_parts = []
            for file_path in matching_files:
                file_name = str(file_path)
                md_gen = markdown_factory(file_name, **kwargs)  # Use existing markdown factory
                markdown_text = md_gen.to_full_markdown()  # Convert to full markdown
                markdown_parts.append(markdown_text)

            # Concatenate all processed markdown parts
            all_markdown = "\n\n".join(markdown_parts)
        else:
            # Generate a warning message if no files are found
            all_markdown = f"**Warning:** No files found matching the pattern '{file_pattern}'."

        # Replace the placeholder with the generated markdown or warning message
        new_content = new_content.replace(full_placeholder, all_markdown, 1)

    return new_content

def update_process_inserts(content: str, timeout_sec=30) -> str:
    """
    Replace process execution placeholders with command output using Rich for formatting.

    Args:
        content (str): The Markdown content as a string.
        timeout_sec (int): Timeout in seconds for each process execution. Default is 30 seconds.

    Returns:
        str: Updated content with process placeholders replaced with command output.
    """

    # Process pattern handling
    proc_pattern = r'^<!--process\s+(.+?)-->(.*?)<!--process end-->'
    proc_matches = re.finditer(proc_pattern, content, re.DOTALL)
    proc_matches = list(proc_matches)

    new_content = content

    # Process command executions
    for match in proc_matches:
        command = match.group(1).strip()  # Extract the command
        old_block = match.group(0)  # Original block

        # Create a string buffer to capture Rich output
        string_io = io.StringIO()
        console = Console(file=string_io, width=100, highlight=False)

        try:
            # Execute the command and capture output
            args = shlex.split(command)
            result = subprocess.run(
                args,
                capture_output=True,
                shell=False,
                text=True,
                check=True,
                timeout=timeout_sec
            )

            # Format the output using Rich
            console.print(result.stdout.strip())
            output = string_io.getvalue()

            # Create new block with command output
            new_block = f"<!--process {command}-->\n```text\n{output}\n```\n<!--process end-->"


        except subprocess.TimeoutExpired:
            console.print(Panel.fit(
                f"Command execution timed out after {timeout_sec} seconds",
                title="Timeout Error",
                style="bold red"
            ))
            output = string_io.getvalue()
            new_block = f"<!--process {command}-->\n{output}\n<!--process end-->"

        new_content = new_content.replace(old_block, new_block,1)

    return new_content


def update_process_placeholders(content: str, timeout_sec=30) -> str:
    """
    Replace process execution placeholders with command output using Rich for formatting.

    Args:
        content (str): The Markdown content as a string.
        timeout_sec (int): Timeout in seconds for each process execution. Default is 30 seconds.

    Returns:
        str: Updated content with process placeholders replaced with command output.
    """

    # Process pattern handling
    proc_pattern = r"\{\{process\s+(.+?)\}\}"
    proc_matches = re.finditer(proc_pattern, content, re.DOTALL)
    proc_matches = list(proc_matches)

    new_content = content

    # Process command executions
    for match in proc_matches:
        command = match.group(1).strip()  # Extract the command
        old_block = match.group(0)  # Original block

        # Create a string buffer to capture Rich output
        string_io = io.StringIO()
        console = Console(file=string_io, width=100, highlight=False)

        try:
            # Execute the command and capture output
            args = shlex.split(command)
            result = subprocess.run(
                args,
                capture_output=True,
                shell=False,
                text=True,
                check=True,
                timeout=timeout_sec
            )

            # Format the output using Rich
            console.print(result.stdout.strip())
            output = string_io.getvalue()

            # Create new block with command output
            new_block = f"```text\n{output}```"


        except subprocess.TimeoutExpired:
            console.print(Panel.fit(
                f"Command execution timed out after {timeout_sec} seconds",
                title="Timeout Error",
                style="bold red"
            ))
            output = string_io.getvalue()
            new_block = f"<!--process {command}-->\n{output}\n<!--process end-->"

        new_content = new_content.replace(old_block, new_block,1)

    return new_content


def update_var_placeholders(content: str, vars: dict = {}) -> str:
    """
    Replace {{$var}} placeholders with corresponding values from the vars dictionary.
    If a placeholder does not have a matching variable in vars, it replaces it with 'Var {var} not found'.

    Args:
        content (str): The input content containing `{{$var}}` placeholders.
        vars (dict): A dictionary of variables and their values.

    Returns:
        str: The updated content with placeholders replaced.
    """
    # Regex to find {{$var}} placeholders
    placeholder_pattern = r'\{\{\$([a-zA-Z][a-zA-Z0-9_]*)\}\}'

    # Match placeholders and replace them with corresponding values or a default message
    def replacer(match):
        var_name = match.group(1)  # Extract the variable name (e.g., "version")
        # Replace with the value from vars if it exists, otherwise use the default value
        return str(vars.get(var_name, f"Var {var_name} not found"))

    # Perform replacement using re.sub
    return re.sub(placeholder_pattern, replacer, content)


def update_markdown_from_string(content: str, bold: str, auto_break: bool,vars:dict={}) -> str:
    """
    Parse a Markdown string and replace special placeholders with actual file contents
    or process output.

    Supported placeholders:
        1. <!--file <glob_pattern>--> : Replaces with the Markdown tables based on file extension
           for all files matching the glob pattern
        2. <!--process <command>--> : Executes the command and inserts its stdout output

    Args:
        content (str): The Markdown content as a string.
        bold (str): Whether to apply bold styling for certain values.
        auto_break (bool): Whether to auto-wrap content.

    Returns:
        str: The updated Markdown content with placeholders replaced.
    """
    try:
        # Apply file insertions
        content = update_file_inserts(content, bold, auto_break)

        # Apply file placeholder insertions
        content = update_file_placeholders(content, bold, auto_break)

        # Apply process insertions
        content = update_process_inserts(content)

        content = update_process_placeholders(content)

        content = update_var_placeholders(content,vars={'version':version("mdfile"),
                                                        'name':'mdfile',
                                                        'date':datetime.datetime.now().strftime("%Y-%m-%d"),
                                                        'time':datetime.datetime.now().strftime("%H:%M:%S")})

        return content

    except Exception as e:
        return content  # Return original content in the case of error


def update_markdown_file(
        md_file: str,
        bold: str = '',
        auto_break: bool = False,
        out_file: str | None = None,
) -> str:
    """
    Updates a Markdown (.md) file with specified modifications (handled by
    update_markdown_from_string). The file update can be overridden by providing an out_file
    parameter. The normal use case is to update a Markdown file in place.

    Args:
        md_file (str): Path to the Markdown file to be read.
        bold (str, optional): String to be added in bold text format. Defaults to an empty string.
        auto_break (bool): If True, applies automatic line breaking within the content.
        out_file (str, optional): If provided, writes the updated Markdown content to this file.
            Otherwise, updates the original file.

    Returns:
        str: Updated content of the Markdown file after modifications.

    Raises:
        FileNotFoundError: If the specified `md_file` is not found.
        Exception: If an unexpected error occurs during the update process.
    """
    try:
        # Read file content
        with open(md_file, 'r', encoding='utf8') as file:
            content = file.read()

        # Call the string-based update function
        updated_content = update_markdown_from_string(content, bold, auto_break)

        # Write updated content to the specified output file
        out_file = out_file or md_file
        with open(out_file, 'w', encoding='utf8') as file_out:
            file_out.write(updated_content)

        return updated_content

    except FileNotFoundError as fnf_error:
        raise FileNotFoundError(f"File '{md_file}' not found.") from fnf_error

