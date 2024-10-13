# File: setup.py
from setuptools import setup, find_packages

setup(
    name="buff-rag",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'langchain',
        'langchain_openai',
        'PyPDF2',
        'langchain_community',
        'openai',
        'python-dotenv',
        'qdrant-client',
        'google-search-results',
        'ipywidgets',
        'spacy',
        'nltk'
    ],
)
