# File: main.py
from rag import initialize_buff_rag, create_rag_chain, run_analysis
from formatting import create_dynamic_input_box, display_vector_store_info
from document_manager import DocumentManager

def main():
    openai_api_key = "your_openai_api_key"
    serpapi_api_key = "your_serpapi_api_key"
    
    search_tool, openai_llm, vectorstore, client, doc_manager = initialize_buff_rag(
        openai_api_key, 
        serpapi_api_key
    )
    rag_chain, search_results_store = create_rag_chain(search_tool, openai_llm)
    
    display_vector_store_info(client)
    create_dynamic_input_box(rag_chain, search_results_store)
    
    return rag_chain, vectorstore, client, doc_manager, search_results_store

if __name__ == "__main__":
    main()
    