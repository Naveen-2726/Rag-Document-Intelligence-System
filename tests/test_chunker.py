from backend.text_chunker import split_text


def test_split_text():
    raw_text = "This is a test sentence that is repeated. " * 50
    documents = split_text(
        text=raw_text,
        source="test_source.txt",
        chunk_size=100,
        chunk_overlap=20,
    )

    assert len(documents) > 1, "Should generate multiple chunks"
    
    first_chunk = documents[0]
    assert "source" in first_chunk.metadata
    assert first_chunk.metadata["source"] == "test_source.txt"
    assert "chunk_id" in first_chunk.metadata
    assert first_chunk.metadata["chunk_id"] == 0
    assert len(first_chunk.page_content) <= 100
