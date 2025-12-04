"""
ChromaDB Validation & Testing
Test that ChromaDB is set up correctly and functioning
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    
    packages = {
        'chromadb': 'ChromaDB',
        'sentence_transformers': 'Sentence Transformers',
        'pandas': 'Pandas',
        'PyPDF2': 'PyPDF2',
    }
    
    missing = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            missing.append(package)
    
    return len(missing) == 0, missing


def test_data_files():
    """Test that required data files exist."""
    print("\nTesting data files...")
    
    data_dir = Path(__file__).parent.parent / "Data"
    
    required_files = {
        "Job Descriptions CSV": data_dir / "Job_Descriptions" / "job_title_des_cleaned.csv",
        "Resumes Folder": data_dir / "raw" / "cv_samples",
    }
    
    all_exist = True
    
    for name, path in required_files.items():
        if path.exists():
            if path.is_dir():
                pdf_count = len(list(path.rglob("*.pdf")))
                print(f"  ✓ {name} ({pdf_count} PDFs found)")
            else:
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"  ✓ {name} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {name} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_chromadb_initialization():
    """Test ChromaDB can be initialized."""
    print("\nTesting ChromaDB initialization...")
    
    try:
        from chroma_setup import get_or_create_db
        
        client, resumes_col, jobs_col = get_or_create_db()
        
        print(f"  ✓ ChromaDB initialized")
        print(f"  ✓ Resumes collection: {resumes_col.count()} documents")
        print(f"  ✓ Jobs collection: {jobs_col.count()} documents")
        
        return True
    except Exception as e:
        print(f"  ✗ ChromaDB initialization failed: {e}")
        return False


def test_embedding_model():
    """Test embedding model can be loaded."""
    print("\nTesting embedding model...")
    
    try:
        from chroma_ingestion import ChromaEmbedder, EMBEDDING_MODEL
        
        print(f"  Loading model: {EMBEDDING_MODEL}")
        embedder = ChromaEmbedder()
        
        # Test embedding generation
        test_texts = ["Hello world", "Test embedding"]
        embeddings = embedder.generate_embeddings(test_texts)
        
        print(f"  ✓ Model loaded successfully")
        print(f"  ✓ Generated {len(embeddings)} embeddings")
        print(f"  ✓ Embedding dimension: {len(embeddings[0])}")
        
        return True
    except Exception as e:
        print(f"  ✗ Embedding model failed: {e}")
        return False


def test_matcher_api():
    """Test the Career Coach Matcher API."""
    print("\nTesting Career Coach Matcher API...")
    
    try:
        from career_coach_matcher import CareerCoachMatcher
        
        matcher = CareerCoachMatcher()
        
        # Test getting stats
        stats = matcher.get_db_stats()
        print(f"  ✓ Matcher initialized")
        print(f"  ✓ Total resumes in DB: {stats['total_resumes']}")
        print(f"  ✓ Total jobs in DB: {stats['total_jobs']}")
        
        # Test getting categories
        categories = matcher.get_all_categories()
        if categories:
            print(f"  ✓ Found {len(categories)} resume categories")
        
        return True
    except Exception as e:
        print(f"  ✗ Matcher API failed: {e}")
        return False


def run_all_tests():
    """Run all validation tests."""
    
    print("""
╔════════════════════════════════════════════════════════════╗
║         ChromaDB Validation & Testing                      ║
║         AI Career Coach Application                        ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Package Imports", test_imports),
        ("Data Files", test_data_files),
        ("ChromaDB Initialization", test_chromadb_initialization),
        ("Embedding Model", test_embedding_model),
        ("Matcher API", test_matcher_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_name == "Package Imports":
                success, missing = test_func()
                if not success:
                    print(f"\nMissing packages: {', '.join(missing)}")
                    print(f"Install with: pip install {' '.join(missing)}")
            else:
                success = test_func()
            
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ChromaDB is ready to use!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
