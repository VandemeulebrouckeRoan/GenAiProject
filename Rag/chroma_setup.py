"""
ChromaDB Setup and Initialization
Initializes ChromaDB for storing resume and job description embeddings
"""

import os
import chromadb
from pathlib import Path
from typing import Optional

# Configuration
CHROMA_DB_PATH = Path(__file__).parent.parent / "Data" / "chromadb"
COLLECTION_RESUMES = "resumes"
COLLECTION_JOBS = "job_descriptions"

def initialize_chromadb(db_path: Optional[str] = None) -> chromadb.Client:
    """
    Initialize ChromaDB client with persistent storage.
    
    Args:
        db_path: Path to store ChromaDB data. Uses default if None.
    
    Returns:
        ChromaDB client instance
    """
    if db_path is None:
        db_path = str(CHROMA_DB_PATH)
    
    # Create directory if it doesn't exist
    Path(db_path).mkdir(parents=True, exist_ok=True)
    
    # Initialize persistent client
    client = chromadb.PersistentClient(path=db_path)
    print(f"[OK] ChromaDB initialized at: {db_path}")
    
    return client


def create_collections(client: chromadb.Client) -> tuple:
    """
    Create or get ChromaDB collections for resumes and jobs.
    
    Args:
        client: ChromaDB client instance
    
    Returns:
        Tuple of (resumes_collection, jobs_collection)
    """
    # Collection for resumes with metadata filtering
    resumes_collection = client.get_or_create_collection(
        name=COLLECTION_RESUMES,
        metadata={"hnsw:space": "cosine"},
        # Metadata fields: category, resume_id, source_file
    )
    
    # Collection for job descriptions
    jobs_collection = client.get_or_create_collection(
        name=COLLECTION_JOBS,
        metadata={"hnsw:space": "cosine"},
        # Metadata fields: job_title, job_id, source_file
    )
    
    print(f"[OK] Collections created: {COLLECTION_RESUMES}, {COLLECTION_JOBS}")
    
    return resumes_collection, jobs_collection


def get_or_create_db(db_path: Optional[str] = None) -> tuple:
    """
    Get or create ChromaDB instance with collections.
    
    Args:
        db_path: Path to store ChromaDB data
    
    Returns:
        Tuple of (client, resumes_collection, jobs_collection)
    """
    client = initialize_chromadb(db_path)
    resumes_col, jobs_col = create_collections(client)
    
    return client, resumes_col, jobs_col


def get_collection_stats(collection) -> dict:
    """Get statistics about a ChromaDB collection."""
    count = collection.count()
    return {
        "name": collection.name,
        "document_count": count,
    }


if __name__ == "__main__":
    # Initialize ChromaDB
    client, resumes_collection, jobs_collection = get_or_create_db()
    
    # Print collection stats
    print("\n--- Collection Statistics ---")
    print(get_collection_stats(resumes_collection))
    print(get_collection_stats(jobs_collection))
    print("\n[OK] ChromaDB setup complete!")
