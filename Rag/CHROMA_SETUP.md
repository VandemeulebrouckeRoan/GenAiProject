# ChromaDB Setup Guide for AI Career Coach

## Overview

ChromaDB is a lightweight, fast vector database perfect for your AI Career Coach project. It stores embeddings of resumes and job descriptions, enabling semantic similarity search and matching.

**Key Features:**
- ✅ Persistent local storage (no server required)
- ✅ Built-in embedding support via Hugging Face models
- ✅ Fast similarity search (HNSW indexing)
- ✅ Metadata filtering (filter by category, job title, etc.)
- ✅ Easy Python integration

## Installation

### Step 1: Install Dependencies

```powershell
cd "c:\Users\demey\Documents\2025-2026\Gen AI\Gen_AI_Career_Coach"
pip install -r Rag\requirements_chroma.txt
```

**What gets installed:**
- `chromadb` - Vector database
- `sentence-transformers` - For generating embeddings (384-dimensional)
- `PyPDF2` & `pdfplumber` - For extracting text from resume PDFs
- `pandas` - For CSV handling
- `torch` - Deep learning framework (required by sentence-transformers)

### Step 2: Verify Installation

```powershell
python -c "import chromadb; print(f'ChromaDB version: {chromadb.__version__}')"
```

## Architecture

### Data Flow

```
PDFs (Resumes)        CSVs (Job Descriptions)
     ↓                          ↓
Extract Text          Read & Clean Data
     ↓                          ↓
Generate Embeddings (sentence-transformers)
     ↓
ChromaDB (Persistent Storage)
     ↓
Query & Similarity Search
```

### Collections

**1. `resumes` Collection**
- Contains: Extracted resume text
- Metadata: resume_id, category, source
- Example categories: ENGINEERING, FINANCE, IT, HEALTHCARE, etc.

**2. `job_descriptions` Collection**
- Contains: Job titles + descriptions
- Metadata: job_title, source, job_index
- Sources: job_title_des_cleaned.csv (2,277 jobs)

## Setup Process

### Step 1: Initialize ChromaDB

```powershell
python Rag\chroma_setup.py
```

**Output:**
```
Loading embedding model: all-MiniLM-L6-v2
✓ Model loaded. Embedding dimension: 384
✓ ChromaDB initialized at: ...\Data\chromadb
✓ Collections created: resumes, job_descriptions

--- Collection Statistics ---
{'name': 'resumes', 'document_count': 0}
{'name': 'job_descriptions', 'document_count': 0}
✓ ChromaDB setup complete!
```

### Step 2: Extract Resume Text from PDFs

```powershell
python Rag\extract_resumes.py
```

**Output:**
```
=============================================================
Resume PDF Text Extraction
=============================================================
Found 100 PDFs in ENGINEERING
Found 100 PDFs in FINANCE
...
Total resume PDFs found: 1000+ across 9 categories

Processing ENGINEERING...
  ✓ Extracted 50 resumes...
  ✓ Extracted 100 resumes...
  
--- Extraction Summary ---
✓ Successfully extracted: 1000 resumes
✗ Failed to extract: 5 resumes
Saved to: ...\Data\resumes_extracted.csv
```

**Output file:** `Data/resumes_extracted.csv` with columns:
- `resume_id` - Unique identifier (PDF filename)
- `category` - Professional category (ENGINEERING, FINANCE, etc.)
- `file_path` - Path to source PDF
- `resume_text` - Extracted text content

### Step 3: Ingest Data into ChromaDB

```powershell
python Rag\chroma_ingestion.py
```

**Process:**
1. Reads `Data/Job_Descriptions/job_title_des_cleaned.csv` (~2,277 jobs)
2. Generates embeddings in batches of 32
3. Stores in ChromaDB with metadata
4. Repeats for resumes from `resumes_extracted.csv`

**Output:**
```
✓ ChromaDB initialized at: ...\Data\chromadb
✓ Collections created: resumes, job_descriptions

--- Ingesting Job Descriptions ---
Total jobs to process: 2277
  ✓ Ingested batch: 32 jobs
  ✓ Ingested batch: 32 jobs
  ...
✓ Job ingestion complete. Total jobs: 2277

--- Ingesting Resumes ---
Total resumes to process: 1000
  ✓ Ingested batch: 32 resumes
  ...
✓ Resume ingestion complete. Total resumes: 1000

--- Example Query ---
Query: I have experience in Python, machine learning, and cloud computing
Similar jobs found: 3
  Result 1: Senior Machine Learning Engineer
  Distance: 0.3421
  Preview: We are looking for an experienced ML engineer...
```

## Project Structure

```
Rag/
├── chroma_setup.py           # Initialize ChromaDB & collections
├── chroma_ingestion.py       # Embed & store documents
├── extract_resumes.py        # Extract text from PDFs
├── requirements_chroma.txt   # Python dependencies
└── CHROMA_SETUP.md           # This file

Data/
├── chromadb/                 # ChromaDB persistent storage (auto-created)
│   ├── 0/                    # Chroma internal data
│   └── ...
├── resumes_extracted.csv     # Extracted resume texts (auto-created)
├── Job_Descriptions/
│   ├── job_title_des_cleaned.csv
│   └── job_descriptions_2_cleaned.csv.gz
└── raw/
    └── cv_samples/
        └── data/data/
            ├── ENGINEERING/        # 100 PDFs
            ├── FINANCE/            # 100 PDFs
            ├── FITNESS/            # 100 PDFs
            ├── HEALTHCARE/         # 100+ PDFs
            ├── HR/                 # 100+ PDFs
            ├── INFORMATION-TECHNOLOGY/  # 100+ PDFs
            ├── PUBLIC-RELATIONS/   # 100 PDFs
            ├── SALES/              # 100+ PDFs
            └── TEACHER/            # 100+ PDFs
```

## Usage Examples

### Example 1: Query Similar Jobs for a Resume

```python
from chroma_setup import get_or_create_db
from chroma_ingestion import ChromaEmbedder, query_similar_jobs

# Initialize
client, _, _ = get_or_create_db()
embedder = ChromaEmbedder()

# Query
resume_text = "Senior Software Engineer with 10 years Python experience..."
results = query_similar_jobs(resume_text, client, embedder, n_results=5)

# Results
for job_title, distance in zip(results['metadatas'][0], results['distances'][0]):
    print(f"• {job_title['job_title']} (Distance: {distance:.4f})")
```

### Example 2: Query Resumes in a Specific Category

```python
from chroma_ingestion import query_similar_resumes

# Query with category filter
job_desc = "Looking for an IT professional with cloud experience..."
results = query_similar_resumes(
    job_desc,
    client,
    embedder,
    n_results=10,
    category_filter="INFORMATION-TECHNOLOGY"
)

# Display results
for resume_id, category in zip(results['ids'][0], results['metadatas'][0]):
    print(f"• {resume_id} ({category['category']})")
```

### Example 3: Direct ChromaDB Query

```python
# Get collection
jobs_collection = client.get_collection("job_descriptions")

# Query with custom filter
results = jobs_collection.query(
    query_embeddings=[embedder.generate_embeddings(["Python Django"])[0]],
    n_results=5,
    where={"job_title": {"$contains": "Developer"}}  # Metadata filter
)
```

## Embedding Model

**Model:** `all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Speed:** Fast (good for real-time applications)
- **Accuracy:** Excellent for semantic search
- **Size:** ~22 MB
- **Task:** General semantic search

**Alternative models (higher accuracy, slower):**
- `all-mpnet-base-v2` - 768 dimensions, highest accuracy
- `sentence-transformers/all-roberta-large-v1` - 1024 dimensions
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` - For multiple languages

To use a different model, update `EMBEDDING_MODEL` in `chroma_ingestion.py`:

```python
EMBEDDING_MODEL = "all-mpnet-base-v2"  # Higher accuracy
```

## Performance Optimization

### Batch Processing
Already configured with `BATCH_SIZE = 32` for efficient embedding generation.

### Similarity Search
- **Distance Metric:** Cosine similarity (default)
- **Index Type:** HNSW (Hierarchical Navigable Small World)
- **Typical Query Time:** < 100ms for 1000 documents

### Storage
- **Jobs:** ~2,277 documents → ~3-4 MB
- **Resumes:** ~1000 documents → ~1-2 MB
- **Total:** ~5-7 MB with embeddings

## Troubleshooting

### Issue: "No module named chromadb"
**Solution:** Run `pip install chromadb` or install from requirements:
```powershell
pip install -r Rag\requirements_chroma.txt
```

### Issue: "CUDA out of memory" (if using GPU)
**Solution:** CPU inference works fine. Models default to CPU. To force CPU:
```python
embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
```

### Issue: PDF extraction fails
**Solution:** Try both PyPDF2 and pdfplumber:
```powershell
pip install PyPDF2 pdfplumber
```

### Issue: ChromaDB collection already exists
**Solution:** This is normal. `get_or_create_collection()` handles it safely.

To reset ChromaDB, delete the `Data/chromadb/` folder:
```powershell
Remove-Item "Data\chromadb" -Recurse -Force
python Rag\chroma_setup.py
```

## Next Steps

### 1. **Build Resume-Job Matcher**
Create a matching algorithm that:
- Takes a job description → Finds similar resumes
- Takes a resume → Finds matching jobs
- Filters by category/skills
- Ranks by similarity score

### 2. **Add Skills Extraction**
- Use NLP to extract skills from resumes
- Create skills-based queries
- Add skills metadata to embeddings

### 3. **Build Web Interface**
- Create REST API (FastAPI)
- Frontend for job/resume search
- Real-time similarity display

### 4. **Advanced Features**
- Resume recommendations for jobs
- Skill gap analysis
- Interview preparation guidance
- Salary recommendations

## Resources

- **ChromaDB Docs:** https://docs.trychroma.com/
- **Sentence Transformers:** https://www.sbert.net/
- **Vector Database Concepts:** https://www.deepset.ai/blog/the-complete-guide-to-vector-databases
- **Semantic Search:** https://huggingface.co/blog/semantic-search

## Summary

✅ **ChromaDB is now ready for your AI Career Coach!**

- Store 1000+ resume embeddings
- Store 2,277 job description embeddings  
- Fast semantic similarity search
- Easy metadata filtering by category
- Local persistent storage (no server needed)

**Quick Start Sequence:**
1. `pip install -r Rag\requirements_chroma.txt`
2. `python Rag\chroma_setup.py`
3. `python Rag\extract_resumes.py`
4. `python Rag\chroma_ingestion.py`
5. Start querying!
