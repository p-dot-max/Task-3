from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_docs(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)

