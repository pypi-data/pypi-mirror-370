import json
from abc import ABC, abstractmethod
import pathlib


class ToMarkdown(ABC):
    """Abstract base class for converting files to Markdown format.

    This class provides functionality to load file content and convert it to
    Markdown representation. Concrete subclasses must implement the `to_markdown()`
    method to define specific conversion logic.

    Attributes:
        file_name: Path to the file to be converted.
        text: Content of the loaded file.
        markdown: The Markdown representation after conversion.
        error_str: Error message if file loading fails.
    """

    def __init__(self, file_name: str, **kwargs):
        self.file_name: str = file_name
        self.text: str = self.load_file()
        self.markdown: str = ""
        self.error_str: str = ""
        # Store remaining kwargs if needed
        self.kwargs = kwargs

    def load_file(self, file_name: str | None = None) -> str:
        """Load the content of a file into the text attribute.

        Reads the file specified by file_name (or the instance's file_name if not provided)
        and stores its content in the text attribute. If any file-related error occurs,
        the error message is stored in the error_str attribute and text is set to an empty string.

        Args:
            file_name: Path to the file to load. If None, uses self.file_name.

        Returns:
            The content of the file as a string, or an empty string if an error occurred.

        Side effects:
            - Sets self.text to the file content
            - Sets self.error_str to an error message if any exception occurs

        Exceptions handled:
            - FileNotFoundError: When the file doesn't exist
            - FileExistsError: When there's an issue with file existence
            - IOError: For general I/O errors
            - PermissionError: When access to the file is denied
        """
        file_name = file_name or self.file_name
        try:
            with open(file_name, 'r', encoding='utf8') as file:
                self.text = file.read()
        except (FileNotFoundError, FileExistsError, IOError, PermissionError) as e:
            self.error_str = str(e)
            self.text = ''

        return self.text

    @abstractmethod
    def to_markdown(self):
        """Subclasses must override this method."""

    def to_full_markdown(self):
        """Generate full markdown including any headers and footers that might be configured.

        The method calls to_markdown() and adds timestamp footer if date_stamp is True.

        Returns:
            The complete markdown representation.
        """

        md = self.to_markdown()

        return md



