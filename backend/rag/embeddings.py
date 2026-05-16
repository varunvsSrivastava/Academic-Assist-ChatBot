from langchain_openai import OpenAIEmbeddings
from backend.app.config import config

def get_embeddings():
    return OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)