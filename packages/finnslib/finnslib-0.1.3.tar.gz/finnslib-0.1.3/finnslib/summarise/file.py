import os
from typing import Optional, Literal
from openai import OpenAI
from .cache import sha256_file, get_file_summary, put_file_summary

Detail = Literal["short", "medium", "long"]

_PROMPTS = {
    "short":  "overview of what this file does. one short line. plain words.",
    "medium": "overview and the most important functions and a basic flow. two or three short lines. plain words.",
    "long":   "full explanation. purpose, flow, key functions and their use cases. as many lines as needed. plain words.",
}

_TOKENS = {"short": 80, "medium": 200, "long": 600}

def _is_probably_binary(path: str, sniff_bytes: int = 4096) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(sniff_bytes)
        if b"\x00" in chunk:
            return True
        # many non text bytes means likely binary
        text_bytes = sum(32 <= b <= 126 or b in (9, 10, 13) for b in chunk)
        return len(chunk) > 0 and text_bytes / max(1, len(chunk)) < 0.8
    except Exception:
        return True

def summarise_file(
    path: str,
    apikey: Optional[str] = None,
    level: Detail = "medium",
    output_file: Optional[str] = None,
    model: str = "gpt-4o-mini",
    client: Optional[OpenAI] = None,
) -> str:
    root = os.path.abspath(".")
    rel = os.path.relpath(path, root).replace("\\", "/")

    if _is_probably_binary(path):
        text = "file looks binary or unreadable"
    else:
        if client is None:
            if not apikey:
                raise RuntimeError("no api key or client")
            client = OpenAI(api_key=apikey)

        try:
            file_hash = sha256_file(path)
        except Exception:
            file_hash = "unknown"

        cached = get_file_summary(root, rel, model, level, file_hash)
        if cached:
            text = cached
        else:
            try:
                with open(path, "r", encoding="utf8", errors="strict") as f:
                    content = f.read()
            except UnicodeDecodeError:
                # try soft read as last resort
                with open(path, "r", encoding="utf8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                content = ""

            if not content:
                text = "no readable text found"
            else:
                user = f"{_PROMPTS[level]}\n\nfile content starts here\n\n{content}"
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

    base = os.path.basename(path)
    out_name = output_file or f"{base}-summary.txt"
    out_path = os.path.abspath(out_name)
    with open(out_path, "w", encoding="utf8") as f:
        f.write(text)
    return out_path