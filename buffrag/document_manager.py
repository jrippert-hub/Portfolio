# File: document_manager.py
import os
import pickle
import hashlib
from typing import List, Dict, Union
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
import io
from PyPDF2 import PdfReader

class DocumentManager:
    def __init__(self, embedding_function, cache_file="embeddings_cache.pkl", chunk_size=500, chunk_overlap=0):
        self.embedding_function = embedding_function
        self.cache_file = cache_file
        self.document_dict: Dict[str, Dict] = {}
        self.load_cache()
        self.client = None
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:
                self.document_dict = pickle.load(f)
        else:
            self.document_dict = {}

    def save_cache(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.document_dict, f)

    def hash_document(self, doc: Union[str, Document]) -> str:
        if isinstance(doc, Document):
            text = doc.page_content
        else:
            text = doc
        return hashlib.md5(text.encode()).hexdigest()

    def add_documents(self, documents: List[Union[str, Document, dict]]):
        new_chunks = []
        skipped_documents = []
        for doc in documents:
            if isinstance(doc, dict) and 'url' in doc:
                try:
                    pdf_text = self.download_pdf(doc['url'])
                    new_doc = Document(page_content=pdf_text, metadata={"source": doc['url']})
                except Exception as e:
                    print(f"Error processing PDF from {doc['url']}: {str(e)}")
                    skipped_documents.append(doc['url'])
                    continue
            elif isinstance(doc, str):
                new_doc = Document(page_content=doc, metadata={"source": "user input"})
            elif isinstance(doc, Document):
                new_doc = doc
            else:
                print(f"Unsupported document type: {type(doc)}")
                continue
            
            # Split the document into chunks
            chunks = self.text_splitter.split_documents([new_doc])
            new_chunks.extend(chunks)

        for chunk in new_chunks:
            chunk_hash = self.hash_document(chunk)
            if chunk_hash not in self.document_dict:
                self.document_dict[chunk_hash] = {
                    "document": chunk,
                    "embedding": None
                }

        if new_chunks:
            texts = [chunk.page_content for chunk in new_chunks]
            new_embeddings = self.embedding_function.embed_documents(texts)
            for chunk, embedding in zip(new_chunks, new_embeddings):
                chunk_hash = self.hash_document(chunk)
                self.document_dict[chunk_hash]["embedding"] = embedding

        self.save_cache()

        if self.client:
            self.update_qdrant()

        return len(new_chunks), skipped_documents

    def update_qdrant(self):
        if not self.client:
            raise ValueError("Qdrant client is not initialized")

        chunks, embeddings = self.get_documents_and_embeddings()
        
        points = [
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "content": chunk.page_content,
                    "source": chunk.metadata.get("source", "Unknown"),
                    "chunk_index": chunk.metadata.get("chunk_index", i)
                }
            )
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        self.client.upsert(collection_name="test", points=points)
  
    def summarize_store(self):
        total_chunks = len(self.document_dict)
        sources = {}
        for doc_info in self.document_dict.values():
            source = doc_info['document'].metadata.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        return total_chunks, sources
        
    def get_documents_and_embeddings(self):
        documents = []
        embeddings = []
        for doc_info in self.document_dict.values():
            documents.append(doc_info["document"])
            embeddings.append(doc_info["embedding"])
        return documents, embeddings

    @staticmethod
    def download_pdf(url: str) -> str:
        response = requests.get(url)
        pdf_content = io.BytesIO(response.content)
        pdf_reader = PdfReader(pdf_content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
        