from langchain_text_splitters import CharacterTextSplitter

def split_text(text):

    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(text)

    return chunks