from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.chains import RetrievalQA

def load_rag():

    embeddings = OpenAIEmbeddings()

    db = FAISS.load_local("vector_db", embeddings)

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        retriever=db.as_retriever()
    )

    return qa