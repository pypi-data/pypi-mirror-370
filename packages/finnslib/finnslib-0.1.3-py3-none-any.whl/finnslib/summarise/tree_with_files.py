import os
from typing import Optional, Literal, Dict, List
from openai import OpenAI
from finnslib.repo.tree import collect_tree
from .cache import (
    sha256_text,
    sha256_file,
    get_file_summary,
    put_file_summary,
    get_dir_summary,
    put_dir_summary,
)

Detail = Literal["short", "medium", "long"]

_FILE_PROMPTS = {
    "short":  "overview of what this file does. one short line. plain words.",
    "medium": "overview and the most important functions and a basic flow. two or three short lines. plain words.",
    "long":   "full explanation. purpose, flow, key functions and their use cases. as many lines as needed. plain words.",
}
_DIR_PROMPTS = {
    "short":  "overview of what this folder contains and why it exists. one short line. plain words.",
    "medium": "overview and the most important parts inside. two or three short lines. plain words.",
    "long":   "full explanation of this folder role, main subfolders and files, and how they fit the app. as many lines as needed. plain words.",
}
_TOKENS = {"short": 80, "medium": 200, "long": 600}

def _make_client(apikey: Optional[str], client: Optional[OpenAI]) -> Optional[OpenAI]:
    if client is not None:
        return client
    if apikey:
        return OpenAI(api_key=apikey)
    return None

def _is_probably_binary(path: str, sniff_bytes: int = 4096) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(sniff_bytes)
        if b"\x00" in chunk:
            return True
        text_bytes = sum(32 <= b <= 126 or b in (9, 10, 13) for b in chunk)
        return len(chunk) > 0 and text_bytes / max(1, len(chunk)) < 0.8
    except Exception:
        return True

def _summ_file(client: Optional[OpenAI], root: str, rel: str, level: Detail, model: str) -> str:
    if client is None:
        return ""
    full = os.path.join(root, rel)
    if _is_probably_binary(full):
        return ""

    try:
        file_hash = sha256_file(full)
    except Exception:
        file_hash = "unknown"

    cached = get_file_summary(root, rel, model, level, file_hash)
    if cached:
        return cached

    try:
        with open(full, "r", encoding="utf8", errors="strict") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(full, "r", encoding="utf8", errors="ignore") as f:
            content = f.read()
    except Exception:
        content = ""

    if not content:
        return ""

    user = f"{_FILE_PROMPTS[level]}\n\nfile content starts here\n\n{content}"
    rsp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "you write clear code summaries. keep it direct."},
            {"role": "user", "content": user},
        ],
        max_tokens=_TOKENS[level],
        temperature=0.2,
    )
    text = rsp.choices[0].message.content.strip()
    put_file_summary(root, rel, model, level, file_hash, text)
    return text

def _summ_dir(client: Optional[OpenAI], root: str, rel: str, children: List[str], level: Detail, model: str) -> str:
    if client is None:
        return ""
    # hash the child names list
    children_hash = sha256_text("\n".join(children))
    cached = get_dir_summary(root, rel, model, level, children_hash)
    if cached:
        return cached

    user = (
        f"{_DIR_PROMPTS[level]}\n"
        f"folder path: {rel or '.'}\n"
        f"child names:\n" + "\n".join(children[:100])
    )
    rsp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "you explain folder roles simply. keep it direct."},
            {"role": "user", "content": user},
        ],
        max_tokens=_TOKENS[level],
        temperature=0.2,
    )
    text = rsp.choices[0].message.content.strip()
    put_dir_summary(root, rel, model, level, children_hash, text)
    return text

def _summary_below_line(line: str, note: str) -> str:
    if not note:
        return ""
    if "└── " in line:
        base, _ = line.split("└── ", 1)
        indent = base + "    "
    elif "├── " in line:
        base, _ = line.split("├── ", 1)
        indent = base + "    "
    else:
        indent = ""
    return f"{indent}{note}"

def summarise_repo_tree(
    root_dir: str = ".",
    output_file: Optional[str] = None,
    apikey: Optional[str] = None,
    level: Detail = "short",
    client: Optional[OpenAI] = None,
    model: str = "gpt-4o-mini",
    summarise_folders: bool = True,
    folder_depth: int = 2,
) -> str:
    out_name = output_file or "tree_with_summaries.txt"
    root = os.path.abspath(root_dir)

    tree_lines, files_list = collect_tree(root, out_name, include_gitignore_file=True)
    client = _make_client(apikey, client)

    # collect child names per folder
    children_by_dir: Dict[str, list[str]] = {}
    for rel in files_list:
        parent = os.path.dirname(rel)
        children_by_dir.setdefault(parent, []).append(os.path.basename(rel))

    # file summaries
    file_summ: Dict[str, str] = {}
    if client:
        for rel in files_list:
            file_summ[rel] = _summ_file(client, root, rel, level, model)

    # folder summaries
    dir_summ: Dict[str, str] = {}
    if client and summarise_folders:
        for folder_rel, kids in children_by_dir.items():
            depth = 0 if folder_rel == "" else len(folder_rel.split("/"))
            if depth <= folder_depth:
                dir_summ[folder_rel] = _summ_dir(client, root, folder_rel, kids, level, model)

    # render with summary lines below each item
    out_lines: List[str] = []
    header_done = False
    for line in tree_lines:
        s = line.rstrip()
        out_lines.append(s)

        if not header_done and s == "":
            # root summary if any
            root_note = dir_summ.get("", "")
            if root_note:
                out_lines.append(f"  {root_note}")
            header_done = True
            continue

        if s.endswith("/"):
            # folder line
            name = s.split("└── ")[-1].split("├── ")[-1][:-1]
            # find match by tail name
            match_rel = None
            for folder_rel in sorted(dir_summ.keys(), key=len):
                if folder_rel and folder_rel.split("/")[-1] == name:
                    match_rel = folder_rel
            note = dir_summ.get(match_rel or "", "")
            below = _summary_below_line(s, note)
            if below:
                out_lines.append(below)
        else:
            # file line
            name = s.split("└── ")[-1].split("├── ")[-1]
            match_rel = None
            for rel in files_list:
                if rel.endswith("/" + name) or rel == name or rel.endswith(name):
                    match_rel = rel
                    break
            note = file_summ.get(match_rel or "", "")
            below = _summary_below_line(s, note)
            if below:
                out_lines.append(below)

    out_path = os.path.join(root, out_name)
    with open(out_path, "w", encoding="utf8") as f:
        f.write("\n".join(out_lines))
    return out_path