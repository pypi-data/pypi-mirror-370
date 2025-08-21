from unidoc_agent.agent import read_document

def test_read_document_extract():
    result = read_document("demo.pdf")
    assert isinstance(result, str)
    assert len(result) > 0