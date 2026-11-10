from pathlib import Path


def load_markdown(path: Path):
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError(f"Empty document: {path}")
    return {"content": content, "source": str(path)}


def chunk_markdown(document: dict, chunk_size: int, overlap: int):
    content = document["content"]
    chunks = []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than 0.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be non-negative and less than chunk size.")
    content_length = len(content)
    step = chunk_size - overlap
    source = document["source"]

    for index, start in enumerate(range(0, content_length, step)):
        end = min(start + chunk_size, content_length)
        chunk = content[start:end]

        chunks.append(
            {
                "content": chunk,
                "source": source,
                "index": index,
            }
        )

        if end == content_length:
            break
    return chunks
