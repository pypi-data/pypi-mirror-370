# finnslib

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

helper functions for working with codebases. main features: summarize files, functions, and repository trees using the openai api.

## table of contents

- [installation](#installation)
- [api key setup](#api-key-setup)
- [usage](#usage)
  - [summarize a single file](#summarize-a-single-file)
  - [summarize a function](#summarize-a-function)
  - [write a plain repo tree](#write-a-plain-repo-tree)
  - [summarize a repo tree](#summarize-a-repo-tree)
- [cli usage](#cli-usage)
- [parameters](#parameters)
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

## usage

### summarize a single file

```python
from finnslib.summarise import summarise_file

out = summarise_file(
    path="main.py",
    apikey="your-key-here",   # optional if OPENAI_API_KEY is set
    level="short"             # "short" or "long"
)
print("summary saved at:", out)
```

**output example:**
```
summary saved at: output/main.py.summary.txt
```

### summarize a function

```python
from finnslib.summarise import summarise_function

out = summarise_function(
    file_path="finnslib/repo/tree.py",
    func_name="write_repo_tree",
    apikey="your-key-here"
)
print(open(out).read())
```

**output example:**
```
function saved at: output/finnslib/repo/tree.py.write_repo_tree.summary.txt
```

### write a plain repo tree

```python
from finnslib.repo import write_repo_tree

out = write_repo_tree(".", "repo_tree.txt")
print("tree saved at:", out)
```

**output example:**
```
tree saved at: repo_tree.txt
```

### summarize a repo tree

```python
from finnslib.summarise import summarise_repo_tree

out = summarise_repo_tree(
    root_dir=".",
    output_file="tree_with_summaries.txt",
    apikey="your-key-here",
    level="short",
    folder_depth=2
)
print("repo summary saved at:", out)
```

**output example:**
```
repo summary saved at: tree_with_summaries.txt
```

## cli usage

after install you also get command line tools:

```bash
# write repo tree
finn_tree .

# summarize repo tree
finn_tree_sum .

# summarize file
finn_file_sum main.py

# summarize function
finn_func_sum finnslib/repo/tree.py write_repo_tree
```

## parameters

- **apikey**: optional. if not passed, will use `OPENAI_API_KEY` environment variable
- **level**: summary detail ("short" or "long")
- **folder_depth**: depth of subfolders when summarizing repo trees

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

**getting help:**
- check the output directory for generated files
- ensure your openai api key has sufficient credits
- verify file permissions if writing to output directories

## license

MIT License © 2025 Finn Clancy