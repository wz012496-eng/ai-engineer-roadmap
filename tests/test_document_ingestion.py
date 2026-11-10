import pytest

from ai_engineer_roadmap.document_ingestion import chunk_markdown, load_markdown


def test_load_markdown(tmp_path):
    # Create a temporary markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# 测试文档\n\n这是一份测试文档.", encoding="utf-8")

    result = load_markdown(md_file)
    assert result["content"] == "# 测试文档\n\n这是一份测试文档."
    assert result["source"] == str(md_file)


def test_load_empty_markdown(tmp_path):
    # Create a temporary empty markdown file
    md_file = tmp_path / "empty.md"
    md_file.write_text("\n\t", encoding="utf-8")

    with pytest.raises(ValueError) as error:
        load_markdown(md_file)

    assert str(error.value) == f"Empty document: {md_file}"


def test_chunk_markdown(tmp_path):
    # Create a temporary markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("ABCDEFGHIJ", encoding="utf-8")

    document = load_markdown(md_file)
    chunks = chunk_markdown(document, chunk_size=5, overlap=2)

    assert len(chunks) == 3
    assert chunks[0]["content"] == "ABCDE"
    assert chunks[1]["content"] == "DEFGH"
    assert chunks[2]["content"] == "GHIJ"

    assert chunks[0]["index"] == 0
    assert chunks[1]["index"] == 1
    assert chunks[2]["index"] == 2

    assert chunks[0]["source"] == str(md_file)
    assert chunks[1]["source"] == str(md_file)
    assert chunks[2]["source"] == str(md_file)


def test_chunk_markdown_invalid_parameters(tmp_path):
    # Create a temporary markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("ABCDEFGHIJ", encoding="utf-8")

    document = load_markdown(md_file)

    with pytest.raises(ValueError) as error:
        chunk_markdown(document, chunk_size=5, overlap=5)
    assert str(error.value) == "Overlap must be non-negative and less than chunk size."


def test_chunk_markdown_short_document():
    assert chunk_markdown(
        {"content": "AB", "source": "short.md"}, chunk_size=5, overlap=2
    ) == [{"content": "AB", "source": "short.md", "index": 0}]
