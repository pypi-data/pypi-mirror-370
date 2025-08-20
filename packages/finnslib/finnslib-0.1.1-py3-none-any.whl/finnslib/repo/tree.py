import os
import fnmatch
from pathlib import Path
from typing import List, Tuple, Optional

DEFAULT_OUTPUT = "project_structure.txt"

def parse_gitignore(gitignore_path: str) -> List[str]:
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def matches_any_pattern(rel_path: str, patterns: List[str]) -> bool:
    parts = Path(rel_path).parts
    base = os.path.basename(rel_path)
    for p in patterns:
        q = p[:-1] if p.endswith("/") else p
        if p.endswith("/"):
            if any(part == q for part in parts):
                return True
            if rel_path.startswith(q + os.sep):
                return True
        if fnmatch.fnmatch(base, q):
            return True
        if fnmatch.fnmatch(rel_path, q):
            return True
        if any(part == q for part in parts):
            return True
    return False

def collect_tree(
    root_dir: str = ".",
    output_file: str = DEFAULT_OUTPUT,
    include_gitignore_file: bool = True,
) -> Tuple[List[str], List[str]]:
    root = os.path.abspath(root_dir)
    patterns = parse_gitignore(os.path.join(root, ".gitignore"))

    venv_names = {
        ".venv", "venv", "env", ".env", "virtualenv",
        ".python_env", ".tox", ".direnv", "pipenv",
        "envs", "pyenv"
    }

    lines: List[str] = []
    files_list: List[str] = []

    lines.append(f"project structure for: {root}")
    lines.append("=" * 50)
    lines.append("")

    def should_skip(rel_path: str) -> bool:
        rp = rel_path.replace("\\", "/")

        if rp == ".gitignore" and include_gitignore_file:
            return False

        if rp in {output_file, ".project_structure_cache.json"}:
            return True

        if rp == ".git" or rp.startswith(".git/"):
            return True

        top = rp.split("/", 1)[0]
        if top in venv_names:
            return True

        if rp == "__pycache__" or "/__pycache__/" in rp or rp.endswith("/__pycache__"):
            return True
        if rp.endswith((".pyc", ".pyo", ".pyd")):
            return True

        if top == ".pytest_cache" or "/.pytest_cache/" in rp:
            return True

        if top.endswith(".egg-info") or "/.egg-info/" in rp or rp.endswith(".egg-info"):
            return True

        if top in {"build", "dist"}:
            return True

        return matches_any_pattern(rp, patterns)

    def walk(cur: str, prefix: str = "") -> None:
        try:
            items = os.listdir(cur)
        except PermissionError:
            return

        dirs: List[str] = []
        files: List[str] = []

        for name in items:
            ap = os.path.join(cur, name)
            rp = os.path.relpath(ap, root).replace("\\", "/")
            if should_skip(rp):
                continue
            if os.path.isdir(ap):
                dirs.append(name)
            else:
                files.append(name)

        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        all_names = dirs + files

        for i, name in enumerate(all_names):
            ap = os.path.join(cur, name)
            last = i == len(all_names) - 1
            conn = "└── " if last else "├── "
            next_prefix = prefix + ("    " if last else "│   ")
            if os.path.isdir(ap):
                lines.append(f"{prefix}{conn}{name}/")
                walk(ap, next_prefix)
            else:
                lines.append(f"{prefix}{conn}{name}")
                files_list.append(os.path.relpath(ap, root).replace("\\", "/"))

    walk(root)
    return lines, files_list

def write_repo_tree(
    root_dir: str = ".",
    output_file: Optional[str] = None,
    include_gitignore_file: bool = True,
) -> str:
    out_name = output_file or DEFAULT_OUTPUT
    lines, _ = collect_tree(root_dir, out_name, include_gitignore_file)
    out_path = os.path.join(os.path.abspath(root_dir), out_name)
    with open(out_path, "w", encoding="utf8") as f:
        f.write("\n".join(lines))
    return out_path

def generate_repo_tree(root_dir: str = ".", output_file: Optional[str] = None) -> str:
    return write_repo_tree(root_dir=root_dir, output_file=output_file, include_gitignore_file=True)