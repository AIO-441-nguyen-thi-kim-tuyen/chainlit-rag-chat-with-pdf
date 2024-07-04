from chainlit.types import AskFileResponse

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_chroma import Chroma


# Create a function to load and split pdf file
def process_file(file: AskFileResponse, text_splitter):
    if file.type == "text/plain":
        Loader = TextLoader
    elif file.type == "application/pdf":
        Loader = PyPDFLoader

    loader = Loader(file.path)
    documents = loader.load()
    docs = text_splitter.split_documents(documents)
    for i, doc in enumerate(docs):
        doc.metadata["source"] = f"source_{i}"
    return docs


# Create a function to get vector database
def get_vector_db(file: AskFileResponse, cl, text_splitter, embedding):
    docs = process_file(file, text_splitter)
    cl.user_session.set("docs", docs)
    vector_db = Chroma.from_documents(documents=docs, embedding=embedding)
    return vector_db
