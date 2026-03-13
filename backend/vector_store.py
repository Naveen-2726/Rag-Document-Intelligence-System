from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def create_vector_store(chunks):

    embeddings = OpenAIEmbeddings()

    vector_db = FAISS.from_texts(chunks, embeddings)

    vector_db.save_local("vector_db")

    return vector_db