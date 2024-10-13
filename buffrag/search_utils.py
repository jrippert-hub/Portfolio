from langchain_community.utilities import SerpAPIWrapper
import spacy
import nltk
from nltk.corpus import stopwords
from collections import Counter

nlp = spacy.load("en_core_web_sm")
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

def perform_google_search(search_tool, question, skip_search=False):
    if skip_search:
        return {"relevant_news": "", "search_query": "", "raw_results": None}

    # Extract key terms from the user's question
    key_terms = extract_key_terms(question)

    # Construct a search query based on the key terms
    search_query = f"{key_terms} financial news market analysis"

    # Perform the search
    search_results = search_tool.run(query=search_query)

    # Extract and process the search results
    relevant_news = extract_snippets(search_results)

    return {
        "relevant_news": relevant_news,
        "search_query": search_query,
        "raw_results": search_results
    }
def extract_key_terms(question, top_n=5):
    # Tokenize and lemmatize using spaCy
    doc = nlp(question)
    
    # Extract named entities
    named_entities = [ent.text for ent in doc.ents]
    
    # Extract nouns and proper nouns
    pos_tags = nltk.pos_tag(nltk.word_tokenize(question))
    nouns = [word.lower() for word, pos in pos_tags if pos.startswith('NN')]
    
    # Combine named entities and nouns
    key_terms = named_entities + nouns
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    key_terms = [term for term in key_terms if term.lower() not in stop_words]
    
    # Count term frequencies
    term_freq = Counter(key_terms)
    
    # Sort by frequency and select top N terms
    top_terms = [term for term, _ in term_freq.most_common(top_n)]
    
    return ' '.join(top_terms)

def extract_snippets(results):
    snippets = []
    if isinstance(results, str):
        return results
    elif isinstance(results, dict) and 'organic_results' in results:
        for result in results['organic_results'][:5]:
            if 'snippet' in result:
                snippets.append(result['snippet'])
    elif isinstance(results, list):
        for result in results[:5]:
            if isinstance(result, dict) and 'snippet' in result:
                snippets.append(result['snippet'])
    return "\n".join(snippets) if snippets else "No relevant snippets found."
