"""
Convert JSON files to Markdown.
"""
import json
from .to_markdown import ToMarkdown

class JsonToMarkdown(ToMarkdown):
    """Converts JSON files to formatted Markdown code blocks with syntax highlighting."""

    def to_markdown(self):
        """Returns the JSON content as a formatted, indented block with json syntax."""
        formatted_json = json.dumps(json.loads(self.text), indent=4)
        return f"```json\n{formatted_json}\n```"


