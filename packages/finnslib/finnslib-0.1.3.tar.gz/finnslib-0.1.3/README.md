# finnslib

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

helper functions for working with codebases. main features: summarize files, functions, and repository trees using the openai api.

## table of contents

- [installation](#installation)
- [api key setup](#api-key-setup)
- [functions reference](#functions-reference)
  - [summarise_file](#summarise_file)
  - [summarise_function](#summarise_function)
  - [summarise_repo_tree](#summarise_repo_tree)
  - [write_repo_tree](#write_repo_tree)
- [usage examples](#usage-examples)
- [cli usage](#cli-usage)
- [development](#development)
- [troubleshooting](#troubleshooting)
- [license](#license)

## installation

```bash
pip install finnslib
```

## api key setup

the summarization functions use openai models. you need an api key.

**option 1: environment variable**
```bash
export OPENAI_API_KEY="sk-..."
```

**option 2: pass explicitly**
all summarise functions accept an `apikey` parameter. if not provided, the library will try `OPENAI_API_KEY` from the environment.

## functions reference

### summarise_file

summarizes an entire file using openai.

```python
def summarise_file(
    path: str,                           # required: path to the file
    apikey: Optional[str] = None,        # optional: openai api key
    level: Detail = "medium",            # optional: "short", "medium", or "long"
    output_file: Optional[str] = None,   # optional: custom output filename
    model: str = "gpt-4o-mini",          # optional: openai model to use
    client: Optional[OpenAI] = None,     # optional: openai client instance
) -> str:
```

**parameters:**
- `path` (required): file path to summarize
- `apikey` (optional): openai api key. if not provided, uses `OPENAI_API_KEY` environment variable
- `level` (optional): summary detail level - "short", "medium", or "long" (default: "medium")
- `output_file` (optional): custom output filename. if not provided, uses `{filename}-summary.txt`
- `model` (optional): openai model to use (default: "gpt-4o-mini")
- `client` (optional): openai client instance. if provided, ignores `apikey`

**returns:** path to the generated summary file

### summarise_function

summarizes a specific function within a file using openai.

```python
def summarise_function(
    path: str,                           # required: path to the file containing the function
    func_name: str,                      # required: exact name of the function to summarize
    apikey: Optional[str] = None,        # optional: openai api key
    level: Detail = "medium",            # optional: "short", "medium", or "long"
    output_file: Optional[str] = None,   # optional: custom output filename
    model: str = "gpt-4o-mini",          # optional: openai model to use
    max_chars: int = 12000,              # optional: max characters to read from file
    client: Optional[OpenAI] = None,     # optional: openai client instance
) -> str:
```

**parameters:**
- `path` (required): file path containing the function
- `func_name` (required): exact function name/signature as it appears in the file
- `apikey` (optional): openai api key. if not provided, uses `OPENAI_API_KEY` environment variable
- `level` (optional): summary detail level - "short", "medium", or "long" (default: "medium")
- `output_file` (optional): custom output filename. if not provided, uses `{func_name}-summary.txt`
- `model` (optional): openai model to use (default: "gpt-4o-mini")
- `max_chars` (optional): maximum characters to read from the file (default: 12000)
- `client` (optional): openai client instance. if provided, ignores `apikey`

**returns:** path to the generated summary file

### summarise_repo_tree

creates a repository tree with summaries for files and folders using openai.

```python
def summarise_repo_tree(
    root_dir: str = ".",                 # optional: root directory to scan (default: current directory)
    output_file: Optional[str] = None,   # optional: custom output filename
    apikey: Optional[str] = None,        # optional: openai api key
    level: Detail = "short",             # optional: "short", "medium", or "long"
    client: Optional[OpenAI] = None,     # optional: openai client instance
    model: str = "gpt-4o-mini",          # optional: openai model to use
    summarise_folders: bool = True,      # optional: whether to summarize folders
    folder_depth: int = 2,               # optional: max depth for folder summaries
) -> str:
```

**parameters:**
- `root_dir` (optional): root directory to scan (default: ".")
- `output_file` (optional): custom output filename. if not provided, uses "tree_with_summaries.txt"
- `apikey` (optional): openai api key. if not provided, uses `OPENAI_API_KEY` environment variable
- `level` (optional): summary detail level - "short", "medium", or "long" (default: "short")
- `client` (optional): openai client instance. if provided, ignores `apikey`
- `model` (optional): openai model to use (default: "gpt-4o-mini")
- `summarise_folders` (optional): whether to generate summaries for folders (default: True)
- `folder_depth` (optional): maximum depth for folder summaries (default: 2)

**returns:** path to the generated tree file with summaries

### write_repo_tree

creates a plain repository tree without summaries.

```python
def write_repo_tree(
    root_dir: str = ".",                 # optional: root directory to scan (default: current directory)
    output_file: Optional[str] = None,   # optional: custom output filename
    include_gitignore_file: bool = True, # optional: whether to include .gitignore file in tree
) -> str:
```

**parameters:**
- `root_dir` (optional): root directory to scan (default: ".")
- `output_file` (optional): custom output filename. if not provided, uses "repo_tree.txt"
- `include_gitignore_file` (optional): whether to include .gitignore file in the tree (default: True)

**returns:** path to the generated tree file

## usage examples

### summarize a single file

```python
from finnslib.summarise import summarise_file

# basic usage
out = summarise_file("main.py")
print("summary saved at:", out)

# with custom options
out = summarise_file(
    path="main.py",
    apikey="your-key-here",           # optional
    level="long",                     # optional: "short", "medium", "long"
    output_file="custom_name.txt",    # optional
    model="gpt-4"                     # optional
)
```

**output example:**
```
summary saved at: main.py-summary.txt
```

### summarize a function

```python
from finnslib.summarise import summarise_function

# python function
out = summarise_function(
    path="finnslib/repo/tree.py",
    func_name="write_repo_tree"
)

# typescript function
out = summarise_function(
    path="./src/api/route.ts",
    func_name="export async function POST(req: NextRequest)",
    level="long"
)
```

**output example:**
```
function saved at: write_repo_tree-summary.txt
```

### write a plain repo tree

```python
from finnslib.repo import write_repo_tree

# basic usage
out = write_repo_tree()
print("tree saved at:", out)

# with custom options
out = write_repo_tree(
    root_dir="./src",                    # optional
    output_file="custom_tree.txt",       # optional
    include_gitignore_file=False         # optional
)
```

**output example:**
```
tree saved at: repo_tree.txt
```

### summarize a repo tree

```python
from finnslib.summarise import summarise_repo_tree

# basic usage
out = summarise_repo_tree()
print("repo summary saved at:", out)

# with custom options
out = summarise_repo_tree(
    root_dir="./src",                    # optional
    output_file="custom_summaries.txt",  # optional
    apikey="your-key-here",             # optional
    level="medium",                      # optional: "short", "medium", "long"
    summarise_folders=False,             # optional: skip folder summaries
    folder_depth=3                       # optional: deeper folder summaries
)
```

**output example:**
```
repo summary saved at: tree_with_summaries.txt
```

## cli usage

after install you also get command line tools:

```bash
# write repo tree
finn_tree .                           # basic usage
finn_tree . --output custom.txt       # custom output file
finn_tree . --no-gitignore           # exclude .gitignore file

# summarize repo tree
finn_tree_sum .                       # basic usage
finn_tree_sum . --level long          # detailed summaries
finn_tree_sum . --no-folders          # skip folder summaries
finn_tree_sum . --folder-depth 3      # deeper folder summaries

# summarize file
finn_file_sum main.py                 # basic usage
finn_file_sum main.py --level long    # detailed summary
finn_file_sum main.py --output custom.txt  # custom output file
finn_file_sum main.py --apikey sk-... # explicit api key

# summarize function
finn_func_sum file.py function_name   # basic usage
finn_func_sum file.py "export async function POST(req: NextRequest)"  # complex function name
finn_func_sum file.py func_name --level long  # detailed summary
```

**available options for all commands:**
- `--help, -h`: show help message
- `--output, -o`: custom output filename
- `--apikey`: openai api key (or set OPENAI_API_KEY env var)
- `--level`: summary detail level ("short", "medium", "long")
- `--model`: openai model to use (default: "gpt-4o-mini")

**specific options:**
- `finn_tree`: `--no-gitignore` to exclude .gitignore file
- `finn_tree_sum`: `--no-folders` to skip folder summaries, `--folder-depth` for max depth
- `finn_func_sum`: `--max-chars` for max characters to read from file

**note:** the summarization commands (`finn_file_sum`, `finn_func_sum`, `finn_tree_sum`) require the `openai` package to be installed. if you get an import error, install it with `pip install openai`.

## development

to set up the development environment:

```bash
# clone the repo
git clone <your-repo-url>
cd finnslib

# install in development mode
pip install -e .

# run tests
pytest
```

## troubleshooting

**common issues:**

1. **api key not found**: make sure you've set `OPENAI_API_KEY` or passed the `apikey` parameter
2. **file not found**: check that the file path exists and is accessible
3. **function not found**: verify the function name exists in the specified file
4. **wrong parameter name**: use `path` not `file_path` for `summarise_function`

**getting help:**
- check the output directory for generated files
- ensure your openai api key has sufficient credits
- verify file permissions if writing to output directories

## license

MIT License © 2025 Finn Clancy