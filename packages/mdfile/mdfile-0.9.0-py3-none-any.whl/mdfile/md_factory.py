"""
Factory function to create file converters based on file extension.
"""
import pathlib

from .json_to_md import JsonToMarkdown
from .text_to_md import ToMarkdown
from .csv_to_md import  CsvToMarkdown
from .code_to_md import CodeToMarkdown
from .md_to_md import MarkdownToMarkdown
from .text_to_md import TextToMarkdown

def markdown_factory(filename: str, **kwargs):
    """
    Creates the appropriate markdown converter based on file extension.

    This factory function examines the provided file's extension and instantiates
    the corresponding converter class. All keyword arguments are passed through to
    the converter's constructor, allowing each converter to use parameters relevant
    to its functionality.

    Args:
        filename (str): Path to the file that needs conversion to markdown.
        **kwargs: Additional keyword arguments that will be passed to the converter.
            CSV-specific parameters:
                auto_break (bool): Whether to insert line breaks in CSV headers.
                bold_vals (list): List of values to be bolded in CSV tables.

    Returns:
        ToMarkdown: An instance of the appropriate converter subclass:
            - MarkdownToMarkdown: For .md files
            - CodeToMarkdown: For code files (.py, .java, .js, etc.)
            - CsvToMarkdown: For .csv files
            - JsonToMarkdown: For .json files
            - TextToMarkdown: For unrecognized file types

    """
    # Convert filename to Path object and get the extension
    path = pathlib.Path(filename)
    ext = path.suffix.lower()

    # Map of file extensions to language identifiers for code blocks
    # Some languages have multiple possible extensions
    language_map = {
        # Python
        '.py': 'python',
        '.pyw': 'python',
        '.pyx': 'python',
        '.pyi': 'python',

        # JavaScript
        '.js': 'javascript',
        '.mjs': 'javascript',
        '.cjs': 'javascript',

        # TypeScript
        '.ts': 'typescript',
        '.tsx': 'typescript',

        # INI
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.properties': 'ini',

        # Java
        '.java': 'java',

        # C/C++
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.hpp': 'cpp',
        '.hxx': 'cpp',

        # C#
        '.cs': 'csharp',

        # PHP
        '.php': 'php',
        '.phtml': 'php',
        '.php5': 'php',

        # Ruby
        '.rb': 'ruby',
        '.rake': 'ruby',

        # Go
        '.go': 'go',

        # Rust
        '.rs': 'rust',
        '.rlib': 'rust',

        # Swift
        '.swift': 'swift',

        # Kotlin
        '.kt': 'kotlin',
        '.kts': 'kotlin',

        # SQL
        '.sql': 'sql',

        # Web technologies
        '.html': 'html',
        '.htm': 'html',
        '.xhtml': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'scss',
        '.less': 'less',

        # Shell/Bash
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.fish': 'bash',

        # YAML
        '.yaml': 'yaml',
        '.yml': 'yaml',

        # XML
        '.xml': 'xml',
        '.xsd': 'xml',
        '.xsl': 'xml',

        # Markdown
        '.md': 'markdown',
        '.markdown': 'markdown',

        # JSON
        '.json': 'json',
        '.jsonc': 'json',

        # VB.NET
        '.vb': 'vbnet',

        # Other common languages
        '.r': 'r',
        '.pl': 'perl',
        '.pm': 'perl',
        '.lua': 'lua',
        '.elm': 'elm',
        '.hs': 'haskell',
        '.lhs': 'haskell',
        '.scala': 'scala',
        '.clj': 'clojure',
        '.erl': 'erlang',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.dart': 'dart',
        '.groovy': 'groovy',
        '.jl': 'julia',
        '.m': 'matlab',
        '.ps1': 'powershell',
        '.tf': 'terraform',
        '.dockerfile': 'dockerfile',
    }

    # Special case handlers
    special_handlers = {
        '.md': MarkdownToMarkdown,
        '.markdown': MarkdownToMarkdown,
        '.csv': CsvToMarkdown,
        '.json': JsonToMarkdown,
    }

    # Check for special handlers first
    if ext in special_handlers:
        return special_handlers[ext](filename, **kwargs)

    # For code files with recognized extensions
    if ext in language_map:
        return CodeToMarkdown(filename, language_map[ext], **kwargs)

    # Default case for unrecognized file types
    return TextToMarkdown(filename, **kwargs)