"""
ChromaDB Query Helper
Simplified interface for common matching and search operations
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from chroma_setup import get_or_create_db
from chroma_ingestion import ChromaEmbedder, EMBEDDING_MODEL
import chromadb


@dataclass
class SearchResult:
    """Container for search results."""
    id: str
    text: str
    metadata: Dict
    distance: float
    similarity_score: float  # 1 - distance (0 to 1 scale)


class CareerCoachMatcher:
    """
    High-level API for resume-job matching in the Career Coach.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the matcher with ChromaDB and embedder.
        
        Args:
            db_path: Optional custom path to ChromaDB
        """
        self.client, self.resumes_col, self.jobs_col = get_or_create_db(db_path)
        self.embedder = ChromaEmbedder(EMBEDDING_MODEL)
        print("✓ Career Coach Matcher initialized")
    
    def find_jobs_for_resume(self, resume_text: str, n_results: int = 10, 
                            min_score: float = 0.5) -> List[SearchResult]:
        """
        Find best-matching jobs for a given resume.
        
        Args:
            resume_text: Resume content (full text)
            n_results: Number of results to return
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of SearchResult objects sorted by similarity
        """
        # Generate embedding
        query_embedding = self.embedder.generate_embeddings([resume_text])[0]
        
        # Query jobs collection
        results = self.jobs_col.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2  # Get extra to filter by min_score
        )
        
        # Convert to SearchResult objects
        search_results = []
        for doc, meta, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            similarity = 1 - distance  # Convert distance to similarity (0-1)
            
            if similarity >= min_score:
                search_results.append(SearchResult(
                    id=meta.get('job_index', 'unknown'),
                    text=doc,
                    metadata=meta,
                    distance=distance,
                    similarity_score=similarity
                ))
        
        # Sort by similarity (highest first)
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return search_results[:n_results]
    
    def find_resumes_for_job(self, job_title: str, job_description: str,
                            n_results: int = 10, category_filter: Optional[str] = None,
                            min_score: float = 0.5) -> List[SearchResult]:
        """
        Find best-matching resumes for a job description.
        
        Args:
            job_title: Job title
            job_description: Job description text
            n_results: Number of results to return
            category_filter: Optional filter by resume category
            min_score: Minimum similarity score (0-1)
        
        Returns:
            List of SearchResult objects sorted by similarity
        """
        # Combine title and description for better search
        combined_text = f"{job_title}. {job_description}"
        
        # Generate embedding
        query_embedding = self.embedder.generate_embeddings([combined_text])[0]
        
        # Build where filter
        where_filter = None
        if category_filter:
            where_filter = {"category": {"$eq": category_filter}}
        
        # Query resumes collection
        results = self.resumes_col.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2,
            where=where_filter
        )
        
        # Convert to SearchResult objects
        search_results = []
        for doc_id, doc, meta, distance in zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            similarity = 1 - distance
            
            if similarity >= min_score:
                search_results.append(SearchResult(
                    id=doc_id,
                    text=doc,
                    metadata=meta,
                    distance=distance,
                    similarity_score=similarity
                ))
        
        # Sort by similarity (highest first)
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return search_results[:n_results]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all resume categories in the database."""
        # Query all resumes and collect unique categories
        all_resumes = self.resumes_col.get()
        categories = set()
        
        for meta in all_resumes['metadatas']:
            if 'category' in meta:
                categories.add(meta['category'])
        
        return sorted(list(categories))
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get count of resumes per category."""
        all_resumes = self.resumes_col.get()
        stats = {}
        
        for meta in all_resumes['metadatas']:
            category = meta.get('category', 'unknown')
            stats[category] = stats.get(category, 0) + 1
        
        return dict(sorted(stats.items()))
    
    def get_db_stats(self) -> Dict:
        """Get overall database statistics."""
        return {
            "total_resumes": self.resumes_col.count(),
            "total_jobs": self.jobs_col.count(),
            "resume_categories": self.get_category_stats(),
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimension": self.embedder.model.get_sentence_embedding_dimension()
        }


def print_search_results(results: List[SearchResult], title: str = "Search Results"):
    """Pretty print search results."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.metadata.get('job_title', result.id)}")
        print(f"   Similarity: {result.similarity_score:.1%} (distance: {result.distance:.4f})")
        print(f"   Preview: {result.text[:120]}...")
        if result.metadata:
            print(f"   Metadata: {result.metadata}")
        print()


if __name__ == "__main__":
    # Initialize matcher
    print("Initializing Career Coach Matcher...")
    matcher = CareerCoachMatcher()
    
    # Get stats
    print("\nDatabase Statistics:")
    stats = matcher.get_db_stats()
    print(f"  Total Resumes: {stats['total_resumes']}")
    print(f"  Total Jobs: {stats['total_jobs']}")
    print(f"  Categories: {len(stats['resume_categories'])}")
    print(f"  Embedding Model: {stats['embedding_model']}")
    
    # Example: Find jobs for a resume
    sample_resume = """
    Senior Software Engineer
    10+ years experience in Python, Java, and cloud technologies
    Expert in AWS, Docker, Kubernetes
    Led teams of 5-10 engineers
    Strong background in backend systems and microservices
    """
    
    print("\n--- Finding Jobs for Resume ---")
    jobs = matcher.find_jobs_for_resume(sample_resume, n_results=5)
    print_search_results(jobs, "Top Matching Jobs")
    
    # Example: Find resumes for a job
    sample_job_title = "Senior Cloud Engineer"
    sample_job_desc = """
    We're looking for an experienced cloud engineer with:
    - 5+ years with AWS or Azure
    - Kubernetes expertise
    - Python and Go experience
    - Team leadership skills
    """
    
    print("\n--- Finding Resumes for Job ---")
    resumes = matcher.find_resumes_for_job(
        sample_job_title,
        sample_job_desc,
        n_results=5,
        category_filter="INFORMATION-TECHNOLOGY"
    )
    print_search_results(resumes, "Top Matching Resumes (IT Category)")
