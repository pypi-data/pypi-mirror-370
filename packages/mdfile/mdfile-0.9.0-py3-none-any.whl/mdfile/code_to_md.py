"""
Create a Markdown file from a code file.
"""

from .to_markdown import ToMarkdown

class CodeToMarkdown(ToMarkdown):
    """Converts code formatted Markdown based on the file extension of the file."""

    def __init__(self, file_name: str, language: str, **kwargs):
        super().__init__(file_name, **kwargs)
        self.language = language

    def to_markdown(self):
        return f"```{self.language}\n{self.text}\n```"