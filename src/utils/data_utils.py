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


def get_vector_db_chroma(docs, embedding):
    vector_db = Chroma.from_documents(documents=docs, embedding=embedding)
    return vector_db
