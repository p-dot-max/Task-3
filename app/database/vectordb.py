import chromadb
from services.embedding import embedding_service

chroma_client = chromadb.Client()
collection = client.get_or_create_collection("fruit")



