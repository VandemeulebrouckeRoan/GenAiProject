"""
ChromaDB Embedding and Ingestion Pipeline
Handles text extraction, embedding generation, and storage in ChromaDB
"""

import os
import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chroma_setup import get_or_create_db, COLLECTION_RESUMES, COLLECTION_JOBS

# Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384-dimensional embeddings, fast & efficient
BATCH_SIZE = 32
DATA_PATH = Path(__file__).parent.parent / "Data"
JOB_CSV_PATH = DATA_PATH / "Job_Descriptions" / "job_title_des_cleaned.csv"


class ChromaEmbedder:
    """Handles embedding generation and ChromaDB ingestion."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedder with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence-transformers model to use
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"✓ Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings
        
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()


def ingest_job_descriptions(csv_path: str, client: chromadb.Client, embedder: ChromaEmbedder):
    """
    Ingest job descriptions from cleaned CSV into ChromaDB.
    
    Args:
        csv_path: Path to cleaned job descriptions CSV
        client: ChromaDB client
        embedder: ChromaEmbedder instance
    """
    jobs_collection = client.get_collection(COLLECTION_JOBS)
    
    print(f"\n--- Ingesting Job Descriptions from {Path(csv_path).name} ---")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Total jobs to process: {len(df)}")
    
    # Prepare batches
    documents = []
    metadatas = []
    ids = []
    
    for idx, row in df.iterrows():
        job_title = str(row.get('Job Title', '')).strip()
        job_desc = str(row.get('Job Description', '')).strip()
        
        if not job_title or not job_desc:
            continue
        
        # Create document combining title and description for better search
        combined_text = f"{job_title}. {job_desc}"
        
        documents.append(combined_text)
        metadatas.append({
            "job_title": job_title[:100],  # Truncate for metadata
            "source": Path(csv_path).name,
            "job_index": str(idx)
        })
        ids.append(f"job_{idx}")
        
        # Process in batches
        if len(documents) >= BATCH_SIZE:
            embeddings = embedder.generate_embeddings(documents)
            jobs_collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print(f"  ✓ Ingested batch: {len(documents)} jobs")
            documents, metadatas, ids = [], [], []
    
    # Process remaining batch
    if documents:
        embeddings = embedder.generate_embeddings(documents)
        jobs_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"  ✓ Ingested final batch: {len(documents)} jobs")
    
    print(f"✓ Job ingestion complete. Total jobs: {jobs_collection.count()}")


def ingest_resumes_from_csv(csv_path: str, client: chromadb.Client, embedder: ChromaEmbedder):
    """
    Ingest resume data from CSV file into ChromaDB.
    
    Note: This assumes resume text has been pre-extracted from PDFs into a CSV.
    
    Args:
        csv_path: Path to resume CSV with extracted text
        client: ChromaDB client
        embedder: ChromaEmbedder instance
    """
    resumes_collection = client.get_collection(COLLECTION_RESUMES)
    
    print(f"\n--- Ingesting Resumes from {Path(csv_path).name} ---")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    print(f"Total resumes to process: {len(df)}")
    
    documents = []
    metadatas = []
    ids = []
    
    for idx, row in df.iterrows():
        resume_id = str(row.get('resume_id', idx))
        resume_text = str(row.get('resume_text', '')).strip()
        category = str(row.get('category', 'unknown')).strip()
        
        if not resume_text or len(resume_text) < 20:
            continue
        
        documents.append(resume_text)
        metadatas.append({
            "resume_id": resume_id,
            "category": category,
            "source": Path(csv_path).name
        })
        ids.append(f"resume_{resume_id}")
        
        # Process in batches
        if len(documents) >= BATCH_SIZE:
            embeddings = embedder.generate_embeddings(documents)
            resumes_collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print(f"  ✓ Ingested batch: {len(documents)} resumes")
            documents, metadatas, ids = [], [], []
    
    # Process remaining batch
    if documents:
        embeddings = embedder.generate_embeddings(documents)
        resumes_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"  ✓ Ingested final batch: {len(documents)} resumes")
    
    print(f"✓ Resume ingestion complete. Total resumes: {resumes_collection.count()}")


def query_similar_jobs(query_text: str, client: chromadb.Client, embedder: ChromaEmbedder, n_results: int = 5):
    """
    Query similar job descriptions.
    
    Args:
        query_text: Query text (e.g., resume or job description)
        client: ChromaDB client
        embedder: ChromaEmbedder instance
        n_results: Number of results to return
    """
    jobs_collection = client.get_collection(COLLECTION_JOBS)
    
    # Generate embedding for query
    query_embedding = embedder.generate_embeddings([query_text])[0]
    
    # Query ChromaDB
    results = jobs_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    return results


def query_similar_resumes(query_text: str, client: chromadb.Client, embedder: ChromaEmbedder, 
                         n_results: int = 5, category_filter: Optional[str] = None):
    """
    Query similar resumes with optional category filtering.
    
    Args:
        query_text: Query text (e.g., job description)
        client: ChromaDB client
        embedder: ChromaEmbedder instance
        n_results: Number of results to return
        category_filter: Optional category to filter by
    """
    resumes_collection = client.get_collection(COLLECTION_RESUMES)
    
    # Generate embedding for query
    query_embedding = embedder.generate_embeddings([query_text])[0]
    
    # Build where filter if category specified
    where_filter = None
    if category_filter:
        where_filter = {"category": {"$eq": category_filter}}
    
    # Query ChromaDB
    results = resumes_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter
    )
    
    return results


if __name__ == "__main__":
    # Initialize
    client, resumes_col, jobs_col = get_or_create_db()
    embedder = ChromaEmbedder()
    
    # Ingest job descriptions
    if JOB_CSV_PATH.exists():
        ingest_job_descriptions(str(JOB_CSV_PATH), client, embedder)
    else:
        print(f"Warning: Job CSV not found at {JOB_CSV_PATH}")
    
    # Example: Query similar jobs
    print("\n--- Example Query ---")
    sample_query = "I have experience in Python, machine learning, and cloud computing"
    results = query_similar_jobs(sample_query, client, embedder, n_results=3)
    
    if results['documents'][0]:
        print(f"Query: {sample_query}")
        print(f"Similar jobs found: {len(results['documents'][0])}")
        for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n  Result {i+1}: {meta.get('job_title', 'Unknown')}")
            print(f"  Distance: {results['distances'][0][i]:.4f}")
            print(f"  Preview: {doc[:150]}...")
