import json
import os
import hashlib
from typing import Dict, Any

CACHE_NAME = ".finnslib_cache.json"

def _load_cache(root: str) -> Dict[str, Any]:
    path = os.path.join(root, CACHE_NAME)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(root: str, data: Dict[str, Any]) -> None:
    path = os.path.join(root, CACHE_NAME)
    try:
        with open(path, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf8", errors="ignore")).hexdigest()

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def get_file_summary(root: str, rel: str, model: str, level: str, content_hash: str) -> str | None:
    data = _load_cache(root)
    key = f"file::{rel}::{model}::{level}"
    entry = data.get(key)
    if not entry:
        return None
    if entry.get("hash") != content_hash:
        return None
    return entry.get("text")

def put_file_summary(root: str, rel: str, model: str, level: str, content_hash: str, text: str) -> None:
    data = _load_cache(root)
    key = f"file::{rel}::{model}::{level}"
    data[key] = {"hash": content_hash, "text": text}
    _save_cache(root, data)

def get_dir_summary(root: str, rel: str, model: str, level: str, children_hash: str) -> str | None:
    data = _load_cache(root)
    key = f"dir::{rel}::{model}::{level}"
    entry = data.get(key)
    if not entry:
        return None
    if entry.get("hash") != children_hash:
        return None
    return entry.get("text")

def put_dir_summary(root: str, rel: str, model: str, level: str, children_hash: str, text: str) -> None:
    data = _load_cache(root)
    key = f"dir::{rel}::{model}::{level}"
    data[key] = {"hash": children_hash, "text": text}
    _save_cache(root, data)