# 🚀 ChromaDB Getting Started Guide

## What is ChromaDB?

ChromaDB is a lightweight, fast vector database perfect for AI applications. It stores embeddings (numerical representations of text) and enables fast semantic similarity search.

**Perfect for**: Job-resume matching, semantic search, AI recommendations

---

## ⚡ Quick Start (5 Minutes)

### Option 1: Automatic Setup (Recommended)

```powershell
cd "c:\Users\demey\Documents\2025-2026\Gen AI\Gen_AI_Career_Coach"
python Rag\quickstart.py
```

This runs all steps automatically:
1. ✓ Installs dependencies
2. ✓ Initializes ChromaDB
3. ✓ Extracts resume PDFs
4. ✓ Generates embeddings
5. ✓ Stores in database

**Time**: ~10-15 minutes (mostly embedding generation)

### Option 2: Manual Setup (Step-by-step)

**Step 1: Install Dependencies**
```powershell
pip install -r Rag\requirements_chroma.txt
```

**Step 2: Initialize Database**
```powershell
python Rag\chroma_setup.py
```

**Step 3: Extract Resumes**
```powershell
python Rag\extract_resumes.py
```
This extracts text from 1000+ PDFs and saves to `resumes_extracted.csv`

**Step 4: Ingest Data**
```powershell
python Rag\chroma_ingestion.py
```
This generates embeddings and stores everything in ChromaDB

**Step 5: Validate Setup**
```powershell
python Rag\validate_setup.py
```
Checks that everything works correctly

---

## 🧪 Test It Out

### Quick Test 1: Check Database Status

```python
from Rag.career_coach_matcher import CareerCoachMatcher

matcher = CareerCoachMatcher()
stats = matcher.get_db_stats()
print(stats)
```

**Output:**
```
{
  'total_resumes': 1000+,
  'total_jobs': 2277,
  'resume_categories': {...},
  'embedding_model': 'all-MiniLM-L6-v2',
  'embedding_dimension': 384
}
```

### Quick Test 2: Find Jobs for a Resume

```python
from Rag.career_coach_matcher import CareerCoachMatcher

matcher = CareerCoachMatcher()

# Example resume
resume = """
Senior Software Engineer
10 years experience with Python, Java, and AWS
Cloud architecture expert
Led teams of 5-10 engineers
"""

# Find matching jobs
jobs = matcher.find_jobs_for_resume(resume, n_results=5)

# Print results
for job in jobs:
    print(f"• {job.metadata['job_title']}")
    print(f"  Similarity: {job.similarity_score:.1%}")
    print(f"  Preview: {job.text[:100]}...")
    print()
```

### Quick Test 3: Find Resumes for a Job

```python
# Find resumes for a job
resumes = matcher.find_resumes_for_job(
    job_title="Cloud Engineer",
    job_description="We need AWS expertise with Kubernetes knowledge",
    n_results=5,
    category_filter="INFORMATION-TECHNOLOGY"
)

# Print results
for resume in resumes:
    print(f"• {resume.metadata['resume_id']} ({resume.metadata['category']})")
    print(f"  Similarity: {resume.similarity_score:.1%}")
    print()
```

---

## 📁 File Structure

```
Rag/
├── chroma_setup.py              # Initialize ChromaDB
├── chroma_ingestion.py          # Embed & ingest documents
├── extract_resumes.py           # Extract PDF text
├── career_coach_matcher.py      # Matching API
├── quickstart.py                # Automated setup
├── validate_setup.py            # Testing
├── requirements_chroma.txt      # Dependencies
└── CHROMA_SETUP.md              # Detailed guide

Data/
├── chromadb/                    # Vector database (auto-created)
├── resumes_extracted.csv        # Extracted resume text (auto-created)
├── Job_Descriptions/
│   ├── job_title_des_cleaned.csv
│   └── job_descriptions_2_cleaned.csv.gz
└── raw/cv_samples/              # 1000+ resume PDFs
```

---

## 🎯 Common Tasks

### Task 1: Search Jobs by Resume

```python
from Rag.career_coach_matcher import CareerCoachMatcher

matcher = CareerCoachMatcher()

# Read a resume (example)
with open("path/to/resume.txt", "r") as f:
    resume_text = f.read()

# Find matching jobs
results = matcher.find_jobs_for_resume(resume_text, n_results=10)

# Display results
for i, job in enumerate(results, 1):
    print(f"{i}. {job.metadata['job_title']} ({job.similarity_score:.1%})")
```

### Task 2: Filter Resumes by Category

```python
# Find IT professionals
it_resumes = matcher.find_resumes_for_job(
    job_title="Senior Backend Developer",
    job_description="Python, Django, PostgreSQL",
    category_filter="INFORMATION-TECHNOLOGY",
    n_results=20
)
```

### Task 3: Get All Categories

```python
categories = matcher.get_all_categories()
# Output: ['ENGINEERING', 'FINANCE', 'FITNESS', 'HEALTHCARE', 'HR', 'IT', 'PUBLIC-RELATIONS', 'SALES', 'TEACHER']

# Get count per category
stats = matcher.get_category_stats()
# Output: {'ENGINEERING': 100, 'FINANCE': 100, ...}
```

---

## 🔍 Understanding Results

### Similarity Score

- **1.0 (100%)**: Identical texts
- **0.8-0.9**: Highly similar
- **0.6-0.8**: Good match
- **0.4-0.6**: Partial match
- **<0.4**: Weak match

**Example:**
```python
# Only show strong matches
jobs = matcher.find_jobs_for_resume(resume, min_score=0.7)
```

---

## ⚙️ Configuration

Edit settings in `Rag/chroma_ingestion.py`:

```python
# Change embedding model (higher accuracy = slower)
EMBEDDING_MODEL = "all-mpnet-base-v2"  # 768-dim, more accurate but slower

# Change batch size (larger = faster but uses more memory)
BATCH_SIZE = 64  # Default is 32

# Change database location
CHROMA_DB_PATH = Path(__file__).parent.parent / "Data" / "chromadb"
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named chromadb" | `pip install chromadb` |
| "Slow embedding generation" | Reduce BATCH_SIZE or use smaller model |
| "Queries return no results" | Run `chroma_ingestion.py` to populate database |
| "Out of memory" | Use CPU mode (default) or reduce BATCH_SIZE |
| "PDF extraction fails" | Try installing: `pip install pdfplumber` |

---

## 📚 API Reference

### CareerCoachMatcher

```python
# Initialize
matcher = CareerCoachMatcher(db_path=None)

# Methods
matcher.find_jobs_for_resume(resume_text, n_results=10, min_score=0.5)
matcher.find_resumes_for_job(job_title, job_description, n_results=10, 
                             category_filter=None, min_score=0.5)
matcher.get_all_categories()  # Returns list of categories
matcher.get_category_stats()  # Returns dict of counts
matcher.get_db_stats()        # Returns full database stats
```

### SearchResult

```python
# Each result has:
result.id              # Unique identifier
result.text           # Document content
result.metadata       # Dictionary with metadata
result.distance       # Raw distance (lower = better)
result.similarity_score  # 0-1 similarity (higher = better)
```

---

## 🚀 Production Tips

1. **Cache Results**: Store frequent searches to reduce computation
2. **Batch Processing**: Use same embedder instance for multiple queries
3. **Precompute**: Generate embeddings once during setup
4. **Monitor**: Track query times and adjust BATCH_SIZE if needed
5. **Backup**: Periodically backup `Data/chromadb/` folder

---

## 📊 Performance

- **Setup Time**: ~15 minutes (first time)
- **Query Time**: <100ms per search
- **Storage**: ~7 MB total
- **Memory**: ~300 MB during processing

---

## 🎓 Next Steps

1. ✅ Run `python Rag\quickstart.py` to set up
2. ✅ Run `python Rag\validate_setup.py` to test
3. ✅ Try the example scripts
4. 📦 Integrate into your backend API
5. 🎨 Build a frontend UI
6. 🚀 Deploy to production

---

## 📖 Learn More

- Full guide: `Rag/CHROMA_SETUP.md`
- ChromaDB docs: https://docs.trychroma.com/
- Sentence Transformers: https://www.sbert.net/

---

**Ready?** Run: `python Rag\quickstart.py` 🚀
