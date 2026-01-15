from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools.retriever import create_retriever_tool
import os

def get_doc_tool():
    """ persistentence connection to ChromaDB and returns a LangChain Retriever Tool.
    """
    # Uses local embeddings to match embedding.py and avoid API keys
    embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1",
        model_kwargs={"trust_remote_code": True}
    )

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, "..", "..")
    chroma_db_path = os.path.join(project_root, "data", "chroma_db")

    vector_db = Chroma(
        persist_directory=chroma_db_path,
        embedding_function=embeddings,
        collection_name="technical_docs"
    )


    doc_tool = create_retriever_tool(
        vector_db.as_retriever(search_kwargs={"k": 3}),
        "technical_knowledge_base",
        "Search this tool for any questions regarding AI, RAG, AI Agents, "
        "or technical history (including Archimedes). Use this for conceptual queries."
    )
    
    return doc_tool