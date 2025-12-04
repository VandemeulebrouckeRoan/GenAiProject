"""
Simple RAG Demo - Job Search
Just searches for jobs matching a given job title or description
"""

import sys
from pathlib import Path

# Add Rag directory to path
sys.path.insert(0, str(Path(__file__).parent / "Rag"))

from career_coach_matcher import CareerCoachMatcher


def search_jobs(query: str, n_results: int = 5):
    """
    Search for jobs matching a query.
    
    Args:
        query: Job title or description to search for
        n_results: Number of results to return
    """
    print(f"\n{'='*70}")
    print(f"Searching for: '{query}'")
    print(f"{'='*70}\n")
    
    # Initialize the matcher
    print("🔄 Loading Career Coach Matcher...")
    matcher = CareerCoachMatcher()
    
    # Search for jobs (treating query as a resume/skill description)
    print(f"\n🔍 Searching for matching jobs...")
    results = matcher.find_jobs_for_resume(query, n_results=n_results)
    
    # Display results
    print(f"\n✅ Found {len(results)} matching jobs:\n")
    
    for i, result in enumerate(results, 1):
        job_title = result.metadata.get('job_title', 'Unknown Job')
        similarity = result.similarity_score * 100
        
        print(f"{i}. {job_title}")
        print(f"   Match Score: {similarity:.1f}%")
        print(f"   Description Preview: {result.text[:200]}...")
        print()


def main():
    """Main demo function."""
    print("\n" + "="*70)
    print("   CAREER COACH - SIMPLE JOB SEARCH DEMO")
    print("="*70)
    
    # Example searches
    queries = [
        "Software Engineer with Python and cloud experience",
        "Data Scientist machine learning AI",
        "Marketing Manager digital advertising",
    ]
    
    print("\nThis demo will search for jobs matching different queries.\n")
    
    for query in queries:
        search_jobs(query, n_results=3)
        print("\n" + "-"*70 + "\n")
    
    print("\n✅ Demo complete!")
    print("\nYou can modify the 'queries' list in the code to search for different jobs.")


if __name__ == "__main__":
    main()
