import os
import pandas as pd
from sqlalchemy import create_engine
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

# Paths
CSV_DIR = "data/raw_csv"
PDF_DIR = "data/raw_pdf"
SQL_DB_PATH = "data/insights_assistant.db"
CHROMA_PATH = "data/chroma_db"

# 1. Load CSVs into SQLite
def ingest_csvs():
    print("Ingesting CSVs into SQLite...")
    engine = create_engine(f"sqlite:///{SQL_DB_PATH}")
    for file in os.listdir(CSV_DIR):
        if file.endswith(".csv"):
            table_name = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(CSV_DIR, file))
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Loaded {file} into table {table_name}")

# 2. Load PDFs into ChromaDB
def ingest_pdfs():
    print("Ingesting PDFs into ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Using a local embedding function
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="internal_reports", embedding_function=emb_fn)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            print(f"Processing {file}...")
            reader = PdfReader(os.path.join(PDF_DIR, file))
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            chunks = text_splitter.split_text(text)
            ids = [f"{file}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": file} for _ in range(len(chunks))]
            
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Indexed {len(chunks)} chunks from {file}")

if __name__ == "__main__":
    ingest_csvs()
    # Install pypdf and sentence-transformers if needed
    try:
        import pypdf
        import sentence_transformers
        ingest_pdfs()
    except ImportError:
        print("Please install pypdf and sentence-transformers: pip install pypdf sentence-transformers")
    print("Ingestion complete.")
