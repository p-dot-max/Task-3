import os
import shutil
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def ingest_docs():
    """Ingests documents from data/documents into ChromaDB."""
    script_dir = Path(__file__).parent.parent.parent
    data_dir = script_dir / "data"
    docs_dir = data_dir / "documents"
    db_dir = data_dir / "chroma_db"

    print(f"Checking documents in {docs_dir}...")
    
    if not docs_dir.exists():
        print("Documents directory not found.")
        return

    # Check if DB already exists and has data (simple check)
    if db_dir.exists() and any(db_dir.iterdir()):
        print("VectorDB already exists. Skipping ingestion.")
        return

    print("Ingesting documents...")
    
    loader = DirectoryLoader(str(docs_dir), glob="**/*.md")
    documents = loader.load()
    
    if not documents:
        print("No documents found.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True
    )
    splits = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1",
        model_kwargs={"trust_remote_code": True}
    )

    vector_db = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(db_dir),
        collection_name="technical_docs"
    )
    
    print(f"Ingested {len(splits)} chunks into VectorDB.")
