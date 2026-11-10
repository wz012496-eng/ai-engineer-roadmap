import pytest

from ai_engineer_roadmap.document_ingestion import load_markdown


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
