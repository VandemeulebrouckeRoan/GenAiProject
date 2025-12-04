#!/usr/bin/env python3
"""
Verify ChromaDB population and system readiness
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chroma_setup import get_or_create_db, COLLECTION_RESUMES, COLLECTION_JOBS

def verify_setup():
    """Verify that ChromaDB is properly populated."""
    print("\n" + "=" * 60)
    print("ChromaDB Verification Report")
    print("=" * 60)
    
    try:
        # Get database
        print("\n1. Connecting to ChromaDB...")
        client, resumes_col, jobs_col = get_or_create_db()
        print(f"   [OK] Connection successful")
        
        # Check resume collection
        print("\n2. Resume Collection:")
        resume_count = resumes_col.count()
        print(f"   - Documents: {resume_count}")
        if resume_count > 0:
            print("   [OK] Resumes populated")
            # Show sample metadata
            sample = resumes_col.get(limit=1, include=["metadatas", "documents"])
            if sample and sample.get("metadatas"):
                print(f"   - Sample resume ID: {sample['metadatas'][0].get('resume_id', 'N/A')}")
                print(f"   - Category: {sample['metadatas'][0].get('category', 'N/A')}")
        else:
            print("   [WARNING] No resumes found (ingestion may be in progress)")
        
        # Check jobs collection
        print("\n3. Job Collection:")
        job_count = jobs_col.count()
        print(f"   - Documents: {job_count}")
        if job_count > 0:
            print("   [OK] Jobs populated")
            # Show sample metadata
            sample = jobs_col.get(limit=1, include=["metadatas", "documents"])
            if sample and sample.get("metadatas"):
                print(f"   - Sample job title: {sample['metadatas'][0].get('job_title', 'N/A')}")
        else:
            print("   [WARNING] No jobs found (ingestion may be in progress)")
        
        # Overall status
        print("\n4. System Status:")
        if resume_count > 100 and job_count > 100:
            print("   [OK] System READY - Both collections populated")
            print(f"\n   Total: {resume_count} resumes + {job_count} jobs")
            return True
        elif resume_count > 0 or job_count > 0:
            print("   [IN_PROGRESS] Ingestion in progress...")
            print(f"   Current: {resume_count} resumes, {job_count} jobs")
            return False
        else:
            print("   [ERROR] Collections are empty - ingestion not started")
            return False
    
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return False
    
    finally:
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    ready = verify_setup()
    sys.exit(0 if ready else 1)
