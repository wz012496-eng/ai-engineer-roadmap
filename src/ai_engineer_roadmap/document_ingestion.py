from pathlib import Path


def load_markdown(path: Path):
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"Empty document: {path}")
    return {"content": content, "source": str(path)}
