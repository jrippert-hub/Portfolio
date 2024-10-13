# Buff RAG

Buff RAG is a Retrieval-Augmented Generation (RAG) system that combines the power of large language models with real-time web search capabilities to provide insightful financial analysis in the style of Warren Buffett.

## Features

- Real-time web search integration
- Document management and vector storage
- Interactive query interface
- Warren Buffett-style financial analysis

## Prerequisites

- Python 3.8+
- OpenAI API key
- SerpAPI key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/buff-rag.git
   cd buff-rag
   ```

2. Install the required packages:
   ```
   pip install -r requirements-txt.txt
   ```

3. Create secret Colab keys for your OpenAI and SerpAPI keys:
   ```
   from google.colab import userdata
   openai_api_key = userdata.get('OPENAI_API_KEY')
   serpapi_api_key = userdata.get('SERP_API_KEY')
   ```

## Usage

### Jupyter Notebook

1. Start Jupyter Notebook:
   ```
   jupyter notebook
   ```

2. Open the `rag_demo.ipynb` notebook.

3. Run the cells in order. The first cell will ensure all required packages are installed.

4. Use the interactive input box to ask financial questions and receive Warren Buffett-style analyses.

### Python Script

You can also use the system as a Python script:

1. Run the main script:
   ```
   python main.py
   ```

2. Follow the prompts to input your financial questions.

## Project Structure

- `rag.py`: Core RAG functionality
- `document_manager.py`: Document processing and management
- `search_utils.py`: Google search and text processing utilities
- `formatting.py`: Display and formatting functions
- `main.py`: Entry point for script usage
- `rag_demo.ipynb`: Jupyter notebook for interactive usage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.