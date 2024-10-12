from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import os

import warnings

warnings.filterwarnings("ignore")


class IndexesRepository:
    def create_indexes(self, path):

        _, file_extension = os.path.splitext(path)

        print(f"Vectorizando {path}, extension: {file_extension}")

        match file_extension:
            case '.pdf':
                loader = PDFPlumberLoader(path)
                docs = loader.load()
                text_splitter = SemanticChunker(HuggingFaceEmbeddings())
                documents = text_splitter.split_documents(docs)
                vector = FAISS.from_documents(documents, HuggingFaceEmbeddings())
            case '.txt':
                with open(path, "r") as file:
                    text = file.read()

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    texts = splitter.split_text(text)
                    metadata_text = [{'source': path} for doc in texts]

                    # documents = [{'content': text, 'metadata': {'source': path}}]
                    # Extract content and metadata separately
                    # texts = [doc['content'] for doc in documents]
                    # metadata_text = [doc['metadata'] for doc in documents]
                    vector = FAISS.from_texts(texts, HuggingFaceEmbeddings(), metadatas=metadata_text)
            case _:
                raise Exception(f"Invalid input type: {file_extension}")

        return vector

    def save_indexes(self, vector, path):
        vector.save_local(path)

    def load_indexes(self, path):
        print(path)
        return FAISS.load_local(path, HuggingFaceEmbeddings(), allow_dangerous_deserialization=True)

    def delete_indexes(self, path):
        pass

    def update_indexes(self, path):
        pass
