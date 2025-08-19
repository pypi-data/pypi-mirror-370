"""Create a plain text file into a Markdown text block."""

from .to_markdown import ToMarkdown

class TextToMarkdown(ToMarkdown):
    """Converts plain text files to Markdown code blocks."""

    def __init__(self, file_name: str, **kwargs):
        super().__init__(file_name, **kwargs)

    def to_markdown(self):
        """Returns the text content wrapped in a plain Markdown code block."""
        return f"```\n{self.text}\n```"

