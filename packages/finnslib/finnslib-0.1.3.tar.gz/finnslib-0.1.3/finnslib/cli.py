#!/usr/bin/env python3
import sys
import argparse
from typing import Optional


def cli_write_repo_tree():
    """cli wrapper for write_repo_tree"""
    from finnslib.repo.tree import write_repo_tree
    
    parser = argparse.ArgumentParser(description="write a plain repository tree")
    parser.add_argument("root_dir", nargs="?", default=".", help="root directory to scan (default: current directory)")
    parser.add_argument("--output", "-o", help="output filename (default: repo_tree.txt)")
    parser.add_argument("--no-gitignore", action="store_true", help="exclude .gitignore file from tree")
    
    args = parser.parse_args()
    
    try:
        result = write_repo_tree(
            root_dir=args.root_dir,
            output_file=args.output,
            include_gitignore_file=not args.no_gitignore
        )
        print(f"tree saved at: {result}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_summarise_file():
    """cli wrapper for summarise_file"""
    try:
        from finnslib.summarise.file import summarise_file
    except ImportError as e:
        print(f"error: openai dependency not installed. install with: pip install openai", file=sys.stderr)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="summarize a file using openai")
    parser.add_argument("path", help="path to the file to summarize")
    parser.add_argument("--apikey", help="openai api key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--level", choices=["short", "medium", "long"], default="medium", 
                       help="summary detail level (default: medium)")
    parser.add_argument("--output", "-o", help="output filename")
    parser.add_argument("--model", default="gpt-4o-mini", help="openai model to use")
    
    args = parser.parse_args()
    
    try:
        result = summarise_file(
            path=args.path,
            apikey=args.apikey,
            level=args.level,
            output_file=args.output,
            model=args.model
        )
        print(f"summary saved at: {result}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_summarise_function():
    """cli wrapper for summarise_function"""
    try:
        from finnslib.summarise.function import summarise_function
    except ImportError as e:
        print(f"error: openai dependency not installed. install with: pip install openai", file=sys.stderr)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="summarize a function within a file using openai")
    parser.add_argument("path", help="path to the file containing the function")
    parser.add_argument("func_name", help="exact name of the function to summarize")
    parser.add_argument("--apikey", help="openai api key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--level", choices=["short", "medium", "long"], default="medium",
                       help="summary detail level (default: medium)")
    parser.add_argument("--output", "-o", help="output filename")
    parser.add_argument("--model", default="gpt-4o-mini", help="openai model to use")
    parser.add_argument("--max-chars", type=int, default=12000, help="max characters to read from file")
    
    args = parser.parse_args()
    
    try:
        result = summarise_function(
            path=args.path,
            func_name=args.func_name,
            apikey=args.apikey,
            level=args.level,
            output_file=args.output,
            model=args.model,
            max_chars=args.max_chars
        )
        print(f"function summary saved at: {result}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_summarise_repo_tree():
    """cli wrapper for summarise_repo_tree"""
    try:
        from finnslib.summarise.tree_with_files import summarise_repo_tree
    except ImportError as e:
        print(f"error: openai dependency not installed. install with: pip install openai", file=sys.stderr)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="create a repository tree with summaries using openai")
    parser.add_argument("root_dir", nargs="?", default=".", help="root directory to scan (default: current directory)")
    parser.add_argument("--apikey", help="openai api key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--level", choices=["short", "medium", "long"], default="short",
                       help="summary detail level (default: short)")
    parser.add_argument("--output", "-o", help="output filename")
    parser.add_argument("--model", default="gpt-4o-mini", help="openai model to use")
    parser.add_argument("--no-folders", action="store_true", help="skip folder summaries")
    parser.add_argument("--folder-depth", type=int, default=2, help="max depth for folder summaries")
    
    args = parser.parse_args()
    
    try:
        result = summarise_repo_tree(
            root_dir=args.root_dir,
            apikey=args.apikey,
            level=args.level,
            output_file=args.output,
            model=args.model,
            summarise_folders=not args.no_folders,
            folder_depth=args.folder_depth
        )
        print(f"repo tree with summaries saved at: {result}")
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
