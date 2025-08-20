import os
from typing import Optional, Literal
from openai import OpenAI

Detail = Literal["short", "medium", "long"]

_PROMPTS = {
    "short":  "overview of what the function does. one or two short lines. plain words.",
    "medium": "what the function does plus its parameters and return. three to six short lines. plain words.",
    "long":   "explain how the function fits in the file, its flow, params, return, side effects, and typical use cases. as many lines as needed. plain words.",
}

_TOKENS = {"short": 80, "medium": 200, "long": 600}

def summarise_function(
    path: str,
    func_name: str,
    apikey: Optional[str] = None,
    level: Detail = "medium",
    output_file: Optional[str] = None,
    model: str = "gpt-4o-mini",
    max_chars: int = 12000,
    client: Optional[OpenAI] = None,
) -> str:
    if client is None:
        if not apikey:
            raise RuntimeError("no api key or client")
        client = OpenAI(api_key=apikey)

    try:
        with open(path, "r", encoding="utf8", errors="ignore") as f:
            content = f.read(max_chars)
    except Exception:
        content = ""

    if not content:
        text = "no readable text found"
    else:
        user = (
            f"{_PROMPTS[level]}\n"
            f"focus only on the function named {func_name}. if not found say not found.\n\n"
            f"file content starts here\n\n{content}"
        )
        rsp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "you explain code simply. keep it direct."},
                {"role": "user", "content": user},
            ],
            max_tokens=_TOKENS[level],
            temperature=0.2,
        )
        text = rsp.choices[0].message.content.strip()

    default_name = f"{func_name}-summary.txt"
    out_name = output_file or default_name
    out_path = os.path.abspath(out_name)
    with open(out_path, "w", encoding="utf8") as f:
        f.write(text)
    return out_path