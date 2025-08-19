
# `MDFile` (mdf)
A utility that dynamically imports content from external files or commands into your Markdown documents. 
Perfect for keeping code samples, data, and command outputs in sync with your documentation.

## Key Features

- **Live Synchronization**: Automatically updates your Markdown when source files change
- **Multiple Import Methods**: Import files directly or capture command outputs
- **Smart Formatting**: Automatically applies correct syntax highlighting based on file extension
- **Table Formatting**: Converts CSV data into well-formatted Markdown tables
- **JSON Prettification**: Properly formats and highlights JSON data


## Quick Example

**Source file (example.py):**
```python
def hello_world():
    return "Hello, world!"
```

**In your README.md:**
```markdown
# My Project

Check out this function:

<!--file example.py-->
<!--file end-->
```

**After running `mdfile`:**
````markdown
# My Project

Check out this function:

<!--file example.py-->
```python
def hello_world():
    return "Hello, world!"
 ```
<!--file end-->
````

To make markdown with the output from the `cat factorial.py` shell command.  This can be difficult
to get just right depending on the tool you are trying to use to pipe data from.  In the example
below the `cat` command is used to copy the data into the Markdown file, but any command can be used.
Keep in mind that some tools act differently when they are generating data for a tty compared to 
when they are piping data into a file.

`<!--process cat factorial.py-->`
```text
def factorial(n:int):
    """Return factorial of n"""
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
```
`<!--process end-->`

## Overview
`MDFile` (`mfm`) 'converts' different file types to properly formatted Markdown, supporting:
- Code files (.py, .java, .js, and many more)
- Multiple files can be displayed using file globs such as `<!--file *.py-->`.
- CSV files (with table formatting)
- JSON files (pretty printed,with syntax highlighting)
- Markdown files inserted inline.
- Text files (plain text conversion)
- Basic variable substitution.


**USEFUL NOTE: Paths are relative to the file that you are processing, so if files are in other folders please
reference them to the Markdown file that you are reading from.**


## Installation

If you are interested in development you can just go to github and clone the repository.

``` bash
# Clone the repository
git clone https://github.com/hucker/mdfile.git
cd mdfile

# Install the package
pip install -e .
```

**RECOMMENDED INSTALLATION**
If you are just interested in using `mdfile` as a tool the very best way to do it
is to just install `uv` and run:

```shell
(.venv) chuck@Chucks-Mac-mini mdfile % uv tool install mdfile 
Resolved 9 packages in 20ms
Installed 9 packages in 10ms
 + click==8.2.1
 + markdown-it-py==4.0.0
 + mdfile==0.5.0
 + mdurl==0.1.2
 + pygments==2.19.2
 + rich==14.1.0
 + shellingham==1.5.4
 + typer==0.16.0
 + typing-extensions==4.14.1
Installed 1 executable: mdfile
```

And then test it:

```shell
(.venv) chuck@Chucks-Mac-mini mdfile % uvx mdfile --help   

Usage: mdfile [OPTIONS] [FILE_NAME]

  Convert a file to Markdown based on its extension.

Arguments:
  [FILE_NAME]  The file to convert to Markdown  \[default: README.md]

Options:
  -o, --output TEXT               Output file (if not specified, prints to
                                  stdout)
  -b, --bold TEXT                 Comma-separated values to make bold (for CSV
                                  files)
  --auto-break / --no-auto-break  Disable automatic line breaks in CSV headers
                                  \[default: auto-break]
  --plain                         Output plain markdown without rich
                                  formatting
  --version     -v                Show version and exit   
  --help                          Show this message and exit.
```

and you should be off and running using this as a tool to update Markdown files anywhere.

## Basic Usage


The basic command for converting files is:
``` bash
uvx mdfile [FILE_PATH] [OPTIONS]
```
If you don't specify a file, it defaults to `README.md`.
### Command Line Options
``` bash
# Convert a file and print to stdout
uvx mdfile README.md

# Disable automatic line breaks in CSV headers
uvx mdfile README.md --no-auto-break
```
## Examples
### CSV to Markdown Table Conversion
#### Original CSV File: `sales_data.csv`
``` 
Region,Q1 Sales,Q2 Sales,Q3 Sales,Q4 Sales,Total
North,125000,133000,158000,175000,591000
South,105000,130000,115000,163000,513000
East,143000,123000,132000,145000,543000
West,117000,142000,138000,162000,559000
Total,490000,528000,543000,645000,2206000
```
#### Markdown Document with Inclusion: `report.md`
``` markdown
# Quarterly Sales Report

## Regional Sales Data

Here's a breakdown of our quarterly sales by region:

<!--file sales_data.csv-->
<!--file end-->

As we can see from the data, Q4 had the strongest performance across all regions.
```
#### After Running `MDFile`:
``` bash
uvx mdfile report.md --bold "Total" -o final_report.md
```

---

#### Resulting Markdown: `final_report.md`

# Quarterly Sales Report

## Regional Sales Data

Here's a breakdown of our quarterly sales by region:

| Region    | Q1 Sales   | Q2 Sales   | Q3 Sales   | Q4 Sales   | Total       |
|-----------|------------|------------|------------|------------|-------------|
| North     | 125000     | 133000     | 158000     | 175000     | 591000      |
| South     | 105000     | 130000     | 115000     | 163000     | 513000      |
| East      | 143000     | 123000     | 132000     | 145000     | 543000      |
| West      | 117000     | 142000     | 138000     | 162000     | 559000      |
| **Total** | **490000** | **528000** | **543000** | **645000** | **2206000** |


As we can see from the data, Q4 had the strongest performance across all regions.

---

### Including JSON Configuration

```json
{"name":"John Doe","age":30,"isStudent":false,"grades":[78,85,90],"address":{"street":"123 Main St","city":"New York","zip":"10001"}}
```

``` markdown
## Configuration

The default configuration is:

<!--file path/to/config.json-->
<!--file end-->
```

The updated `README.md` file is shown below with the JSON pretty printed.

```` markdown
## Configuration

The default configuration is:

<!--file path/to/config.json-->
```json
{
    "name": "John Doe",
    "age": 30,
    "isStudent": false,
    "grades": [
        78,
        85,
        90
    ],
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "zip": "10001"
    }
}
```
<!--file end-->
````

## File Type Support
`MDFile` supports numerous file extensions allowing MarkDown to correctly syntax highlight:
- Python: `.py`, `.pyw`, `.pyx`, `.pyi`
- JavaScript: `.js`, `.mjs`, `.cjs`
- TypeScript: `.ts`, `.tsx`
- Java: `.java`
- C/C++: `.c`, `.h`, `.cpp`, `.cc`, `.hpp`
- Web: `.html`, `.htm`, `.css`, `.scss`
- Data: `.json`, `.yaml`, `.yml`, `.csv`
- Configuration: `.ini`, `.cfg`, `.conf`
- Shell: `.sh`, `.bash`, `.zsh`
- And many more!

These file extensions map use the standard triple back tick text blocks available in Markdown.

## Options for CSV Files
When converting CSV files, you have additional options:
- `--bold VALUE1,VALUE2,...` - Make specific columns bold in the table
- `--auto-break/--no-auto-break` - Control automatic line breaks in CSV headers

## Variable Substitution
`mdfile` supports a basic form of variable substitution.  At this time the following are supported:

| Variable     | Description          |
|--------------|----------------------|
| `{{$name}}`    | `mdfile`             |
| `{{$date}}`    | current date         |
| `{{$time}}`    | current time         |
| `{{$version}}` | build version        |

These values are imported directly into the markdown file with no special markdown tags, just raw text
this allows you to have text such as

```App **{{$name}}** version **{{$version}}** was created on {{$date}```

To get the text

App **mdfile** version **0.10.0** was created on 1/1/2024

### UV Run
If you installed `mdfile` as a `uv` tool then you can run `mdfile` from anywhere.

```bash
uvx mdfile ../README_template.md --output ../README.md
```


### Convert a CSV file with bold totals

``` bash
uvx mdfile sales_data.csv --bold "Total,Sum" -o sales_report.md
```
### Update embedded references in a Markdown file

``` bash
uvx mdfile documentation.md -o updated_docs.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## License
[MIT License](LICENSE)
