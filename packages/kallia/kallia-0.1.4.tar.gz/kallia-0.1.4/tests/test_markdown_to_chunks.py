from kallia_core.documents import Documents
from kallia_core.chunker import Chunker


def test_markdown_to_chunks():
    url = "https://raw.githubusercontent.com/kallia-project/kallia/refs/tags/v0.1.3/assets/pdf/01.pdf"
    page_number = 1
    temperature = 0.0
    max_tokens = 8192
    markdown_content = Documents.to_markdown(
        source=url,
        page_number=page_number,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    semantic_chunks = Chunker.create(
        text=markdown_content,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    assert len(semantic_chunks) > 0
