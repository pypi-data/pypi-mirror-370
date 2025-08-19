from kallia_core.documents import Documents


def test_pdf_to_markdown():
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
    assert len(markdown_content) > 0
