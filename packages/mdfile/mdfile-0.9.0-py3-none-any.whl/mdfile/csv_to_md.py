"""
Convert a CSV file to a Markdown table.
"""
import csv
from .to_markdown import ToMarkdown


class CsvToMarkdown(ToMarkdown):
    """Converts JSON files to formatted Markdown code blocks with syntax highlighting."""

    def __init__(self, file_name: str, **kwargs):
        # Extract CSV-specific parameters before calling super()
        self.auto_break = kwargs.pop('auto_break', True)
        self.bold_vals = kwargs.pop('bold_vals', [])

        # Pass remaining kwargs to super
        super().__init__(file_name, **kwargs)

    def to_markdown(self):
        try:
            with open(self.file_name, 'r', encoding='utf8') as csv_file:
                reader = csv.reader(csv_file)

                # Read all rows from the CSV
                rows = list(reader)

                if not rows:
                    return "The CSV file is empty."

                # Prepare the Markdown table header
                header = rows[0]

                # Insert line breaks
                if self.auto_break:
                    header = [h.replace(" ", "<br>").replace("_", "<br>") for h in header]

                markdown = "| " + " | ".join(header) + " |\n"
                markdown += "| " + " | ".join(["---"] * len(header)) + " |\n"

                # Add the rows
                for row in rows[1:]:
                    formatted_row = []
                    for item in row:
                        try:
                            if item in self.bold_vals:
                                item = f"-> **{item}** <-"
                            # Check if the item is numeric (can be converted to a float)
                            number = float(item)
                            # Format as a 2-significant-figure float (if it's not an integer)
                            if number.is_integer() and '.' not in str(number):
                                formatted_row.append(f"{int(number)}")  # Keeps integers as they are
                            else:
                                formatted_row.append(f"{number:.02f}")
                        except ValueError:
                            # If not numeric, keep the item as-is
                            formatted_row.append(item)

                    markdown += "| " + " | ".join(formatted_row) + " |\n"

                return markdown
        except FileNotFoundError:
            return f"Error: File '{self.file_name}' not found."
        except Exception as e:
            return f"Error: An error occurred while processing the file: {e}"
