# For more info: https://huggingface.co/nomic-ai/nomic-embed-text-v1

import os
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    def __init__(self, documents_path: str = "data/documents"):
        """Initialize the embedding 
        
        Args:
            documents_path: Path to the documents directory
        """
        self.documents_path = Path(documents_path)
        
        self.model = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1",
            trust_remote_code=True
        )
        
        self.document_cache: Dict[str, str] = {}
        self.embeddings_cache: Dict[str, np.ndarray] = {}
    
    def read_document(self, file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        except Exception as e:
            return str(e)
    
    def load_all_documents(self) -> Dict[str, str]:
        
        if not self.documents_path.exists():
            print(f"Documents path {self.documents_path} does not exist")
            return {}
        
        documents = {}
        for file_path in self.documents_path.glob("*.md"):
            content = self.read_document(file_path)
            if content:
                documents[file_path.name] = content
                print(f"Loaded: {file_path.name} ({len(content)} characters)")
        
        self.document_cache = documents
        return documents
    
    def create_embeddings_for_all_documents(self) -> Dict[str, np.ndarray]:
        """Create embeddings for all documents in the documents directory.
        """
        if not self.document_cache:
            self.load_all_documents()
        
        if not self.document_cache:
            print("No documents found to process")
            return {}
        
        print(f"embeddings for {len(self.document_cache)} documents.")
        
        filenames = list(self.document_cache.keys())
        documents = list(self.document_cache.values())
        
        embeddings = self.model.encode(documents)
        
        for filename, embedding in zip(filenames, embeddings):
            self.embeddings_cache[filename] = embedding
            print(f"Generated embedding for {filename} (shape: {embedding.shape})")
        
        return self.embeddings_cache
    
    def encode_query(self, query: str) -> np.ndarray:
        return self.model.encode([query])[0]
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search documents using a query and return the most relevant ones.
        """

        if not self.embeddings_cache:
            print("No embeddings available. Creating embeddings first...")
            return []
        
        query_embedding = self.encode_query(query)
        
        results = []
        for filename, doc_embedding in self.embeddings_cache.items():
            score = float(query_embedding @ doc_embedding.T)
            results.append({
                "filename": filename,
                "score": score,
                "content": self.document_cache.get(filename, "")
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Top results after sorted
        return results[:top_k]
    
    def get_embeddings_stats(self) -> Dict:
        return {
            "total_documents": len(self.document_cache),
            "total_embeddings": len(self.embeddings_cache),
            "documents": list(self.document_cache.keys()),
            "embedding_dimension": self.embeddings_cache[list(self.embeddings_cache.keys())[0]].shape[0] if self.embeddings_cache else 0
        }


# Singleton
embedding_service = EmbeddingService()


