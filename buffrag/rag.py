#rag.py


# File: rag.py
import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from document_manager import DocumentManager
from search_utils import perform_google_search, extract_key_terms, extract_snippets

def initialize_buff_rag(openai_api_key, serpapi_api_key, chunk_size=500, chunk_overlap=0):
    os.environ['OPENAI_API_KEY'] = openai_api_key
    os.environ['SERPAPI_API_KEY'] = serpapi_api_key

    embedding_model = "text-embedding-3-small"
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    # Initialize DocumentManager
    doc_manager = DocumentManager(embeddings, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Dynamically determine the embedding dimension
    sample_text = "This is a sample text to determine embedding dimensions."
    sample_embedding = embeddings.embed_query(sample_text)
    embedding_dim = len(sample_embedding)
    
    # Initialize Qdrant client
    client = QdrantClient(":memory:")
    
    # Check if collection exists, if not, create it
    collection_name = "test"
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
        )
    
    # Load documents and embeddings from DocumentManager
    documents, embeddings_list = doc_manager.get_documents_and_embeddings()
    
    # Add documents to Qdrant
    points = [
        PointStruct(
            id=i,
            vector=embedding,
            payload={"content": doc.page_content if isinstance(doc, Document) else doc,
                     "source": doc.metadata.get("source", "Unknown") if isinstance(doc, Document) else "Unknown"}
        )
        for i, (doc, embedding) in enumerate(zip(documents, embeddings_list))
    ]
    client.upsert(collection_name=collection_name, points=points)
    
    # Initialize Qdrant vector store
    vectorstore = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings,
    )
    
    search_tool = SerpAPIWrapper()
    openai_llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.6)
    doc_manager.client = client  # Attach the client to doc_manager
    return search_tool, openai_llm, vectorstore, client, doc_manager

def create_rag_chain(search_tool, openai_llm):
    output_parser = StrOutputParser()
    search_results_store = {}

    def analyze_news_with_rag(inputs):
        question = inputs["question"]
        search_results = perform_google_search(search_tool, question)
        
        # Store the search results
        search_results_store[question] = search_results

        return {
            "relevant_news": search_results["relevant_news"],
            "question": question
        }

    rag_chain = (
        RunnablePassthrough()
        | analyze_news_with_rag
        | rag_prompt
        | openai_llm
        | output_parser
    )

    return rag_chain, search_results_store

def run_analysis(rag_chain, question, search_results_store):
    result = rag_chain.invoke({"question": question})
    search_results = search_results_store.get(question, {})
    return result, search_results
