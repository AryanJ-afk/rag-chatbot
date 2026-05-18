from backend.s3_client import download_file_from_s3
import io
import re
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vector_store import vector_store

def ingest_pdf(s3_key: str, user_id: str) -> dict:
    
    pdf_bytes = download_file_from_s3(s3_key)
    
    pdf_stream = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_stream)
    
    texts = []
    metadata = []
    counter = 1
    for page in reader.pages:
        text = page.extract_text()
        text = re.sub(r'\s+', ' ', text).strip()
        if text.strip():
            texts.append(text)
            metadata.append({"source": s3_key.split('/')[-1], "page": counter, "user_id": user_id})
        counter += 1
       
    splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 150)

    chunks = splitter.create_documents(texts, metadatas=metadata)
    
    vector_store.add_documents(chunks)
    
    return {"chunks_added": len(chunks), "pages": len(texts)}
    