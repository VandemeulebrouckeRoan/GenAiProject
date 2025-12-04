#!/usr/bin/env python3
"""
Simplified data ingestion script for ChromaDB
Directly embeds and stores resumes and jobs without heavy dependencies during import
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

print("Step 1: Importing ChromaDB...")
import chromadb

print("Step 2: Importing Pandas...")
import pandas as pd

print("Step 3: Importing Sentence Transformers (this may take a minute)...")
from sentence_transformers import SentenceTransformer

print("\n✓ All imports successful!\n")

# Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 32
DATA_PATH = Path(__file__).parent.parent / "Data"
DB_PATH = DATA_PATH / "chromadb"
RESUMES_CSV = DATA_PATH / "resumes_extracted.csv"
JOBS_CSV = DATA_PATH / "raw" / "Job_Descriptions" / "job_title_des_cleaned.csv"

def main():
    print("=" * 60)
    print("ChromaDB Data Ingestion")
    print("=" * 60)
    
    # Initialize ChromaDB
    print(f"\n1. Initializing ChromaDB at {DB_PATH}...")
    # Use the new PersistentClient API (required in newer chromadb versions)
    client = chromadb.PersistentClient(path=str(DB_PATH))
    
    # Get or create collections
    print("2. Creating/getting collections...")
    resumes_col = client.get_or_create_collection(name="resumes", metadata={"hnsw:space": "cosine"})
    jobs_col = client.get_or_create_collection(name="job_descriptions", metadata={"hnsw:space": "cosine"})
    
    print(f"   - Resumes collection: {resumes_col.count()} documents")
    print(f"   - Jobs collection: {jobs_col.count()} documents")
    
    # Load embedding model
    print(f"\n3. Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"   ✓ Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    
    # Ingest resumes
    print(f"\n4. Ingesting resumes from {RESUMES_CSV.name}...")
    if RESUMES_CSV.exists():
        ingest_resumes(resumes_col, model, RESUMES_CSV)
        print(f"   ✓ Total resumes in DB: {resumes_col.count()}")
    else:
        print(f"   ✗ File not found: {RESUMES_CSV}")
    
    # Ingest jobs
    print(f"\n5. Ingesting jobs from {JOBS_CSV.name}...")
    if JOBS_CSV.exists():
        ingest_jobs(jobs_col, model, JOBS_CSV)
        print(f"   ✓ Total jobs in DB: {jobs_col.count()}")
    else:
        print(f"   ✗ File not found: {JOBS_CSV}")
    
    print("\n" + "=" * 60)
    print("✓ Ingestion complete!")
    print("=" * 60)
    print(f"Resumes in database: {resumes_col.count()}")
    print(f"Jobs in database: {jobs_col.count()}")
    print(f"Database location: {DB_PATH}")


def ingest_resumes(collection, model, csv_path):
    """Ingest resumes from CSV file."""
    df = pd.read_csv(csv_path)
    print(f"   Total resume records to process: {len(df)}")
    
    documents = []
    metadatas = []
    ids = []
    processed = 0
    
    for idx, row in df.iterrows():
        try:
            resume_id = str(row.get('resume_id', idx))
            resume_text = str(row.get('resume_text', '')).strip()
            category = str(row.get('category', 'unknown')).strip()
            
            if not resume_text or len(resume_text) < 20:
                continue
            
            documents.append(resume_text)
            metadatas.append({
                "resume_id": resume_id,
                "category": category,
            })
            ids.append(f"resume_{resume_id}")
            
            # Process in batches
            if len(documents) >= BATCH_SIZE:
                embeddings = model.encode(documents, show_progress_bar=False)
                collection.add(
                    ids=ids,
                    embeddings=embeddings.tolist(),
                    documents=documents,
                    metadatas=metadatas
                )
                processed += len(documents)
                print(f"     Processed {processed}/{len(df)} resumes...")
                documents, metadatas, ids = [], [], []
        except Exception as e:
            print(f"     Error processing resume {idx}: {e}")
            continue
    
    # Process remaining batch
    if documents:
        embeddings = model.encode(documents, show_progress_bar=False)
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )
        processed += len(documents)
        print(f"     Final batch processed. Total: {processed} resumes")


def ingest_jobs(collection, model, csv_path):
    """Ingest job descriptions from CSV file."""
    df = pd.read_csv(csv_path)
    print(f"   Total job records to process: {len(df)}")
    
    documents = []
    metadatas = []
    ids = []
    processed = 0
    
    for idx, row in df.iterrows():
        try:
            job_title = str(row.get('Job Title', '')).strip()
            job_desc = str(row.get('Job Description', '')).strip()
            
            if not job_title or not job_desc:
                continue
            
            # Combine title and description
            combined_text = f"{job_title}. {job_desc}"
            
            documents.append(combined_text)
            metadatas.append({
                "job_title": job_title[:100],
                "job_index": str(idx)
            })
            ids.append(f"job_{idx}")
            
            # Process in batches
            if len(documents) >= BATCH_SIZE:
                embeddings = model.encode(documents, show_progress_bar=False)
                collection.add(
                    ids=ids,
                    embeddings=embeddings.tolist(),
                    documents=documents,
                    metadatas=metadatas
                )
                processed += len(documents)
                print(f"     Processed {processed}/{len(df)} jobs...")
                documents, metadatas, ids = [], [], []
        except Exception as e:
            print(f"     Error processing job {idx}: {e}")
            continue
    
    # Process remaining batch
    if documents:
        embeddings = model.encode(documents, show_progress_bar=False)
        collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas
        )
        processed += len(documents)
        print(f"     Final batch processed. Total: {processed} jobs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
