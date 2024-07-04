import chainlit as cl

from src.utils.data_utils import process_file, get_vector_db
from src.utils.llm_utils import get_huggingface_llm

from chainlit.types import AskFileResponse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain import hub

# Initialize text splitter and embedding
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                               chunk_overlap=100)
embedding = HuggingFaceEmbeddings()

llm = get_huggingface_llm()


def test_pdf_loader():
    file = AskFileResponse()
    file.path = "./data/YOLOv10_Tutorials.pdf"
    file.type == "application/pdf"

    # Initialize text splitter and embedding
    documents = process_file(file, text_splitter)
    print("Number of documents: ", len(documents))
    assert len(documents) == 20


def test_get_vector_db():
    file = AskFileResponse()
    file.path = "./data/YOLOv10_Tutorials.pdf"
    file.type == "application/pdf"
    vector_db = get_vector_db(file, cl, text_splitter, embedding)
    retriever = vector_db.as_retriever()

    QUERY = "YOLOv10 là gì"
    result = retriever.invoke(QUERY)

    print("Number of relevant documents: ", len(result))
    assert len(result) == 4


'''
Only be tested if Github Nvidia powered GPU hosted runner supported

# https://github.blog/changelog/2024-04-02-whats-new-for-github-actions-hosted-runners/
# https://medium.com/@tajinder.singh1985/exploring-github-nvidia-powered-gpu-hosted-runner-32b172a92c7e
'''


def test_prompting_with_rag():
    file = AskFileResponse()
    file.path = "./data/YOLOv10_Tutorials.pdf"
    file.type == "application/pdf"
    vector_db = get_vector_db(file, cl, text_splitter, embedding)
    retriever = vector_db.as_retriever()

    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    USER_QUESTION = "YOLOv10 là gì?"
    output = rag_chain.invoke(USER_QUESTION)
    answer = output.split('Answer:')[1].strip()
    expected = "YOLOv10 là một phiên bản của YOLO (You Only Look Once) - một hệ thống dự đoán hình ảnh được huấn luyện sẵn trên bộ dữ liệu COCO."
    assert expected.lower() in answer.lower()
