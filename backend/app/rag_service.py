from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# This model runs entirely on your computer (CPU/GPU)
# It's one of the most popular lightweight models for RAG
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_and_chunk_text(text: str):
    """
    Splits text into chunks and generates 384-dimension embeddings locally.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    # This happens on your machine, no API key needed!
    vectors = embeddings.embed_documents(chunks)
    
    return list(zip(chunks, vectors))
