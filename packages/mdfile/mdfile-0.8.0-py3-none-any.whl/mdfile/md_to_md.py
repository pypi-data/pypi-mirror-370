"""
Directly insert contents of a Markdown file into another Markdown file.
"""

from .to_markdown import ToMarkdown


class MarkdownToMarkdown(ToMarkdown):
    """Directly inserts the contents of a Markdown file into the output."""

    def to_markdown(self):
        return f"\n{self.text}\n"

