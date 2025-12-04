<div align="center">

# 🎯 AI Career Coach

### *AI-Powered Resume Enhancement & Job Matching Platform*

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-orange.svg)](https://www.trychroma.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Mistral%207B-red.svg)](https://ollama.ai/)

**Upload your CV, get AI-powered improvements, and find matching jobs using semantic search**

</div>

---

## 🚀 Quick Start with Docker

### 1️⃣ Clone & Navigate

```bash
git clone https://github.com/VandemeulebrouckeRoan/GenAiProject.git
cd GenAiProject
```

### 2️⃣ Launch the Application

```bash
docker compose up --build
```

**That's it!** The application will:
- ✅ Start Ollama service
- ✅ Download Mistral 7B model (~4.1GB, first time only)
- ✅ Launch Gradio web interface
- ✅ Initialize vector database

### 3️⃣ Access the Application

🌐 **Open your browser:** http://localhost:7860

---

## ⏱️ First Time Setup

| Step | Duration | Details |
|------|----------|---------|
| **Docker Build** | 2-3 min | Install Python dependencies |
| **Ollama Startup** | 30-60 sec | Initialize Ollama service |
| **Model Download** | 10-15 min | Download Mistral 7B (one time) |
| **App Launch** | 10-20 sec | Start Gradio interface |

💡 **Total first run**: ~15-20 minutes  
💡 **Subsequent runs**: ~30 seconds

---

## 📦 What's Included

### Services

| Service | Purpose | Port | Status |
|---------|---------|------|--------|
| **Gradio App** | Web interface for CV processing | 7860 | Always runs |
| **Ollama** | LLM inference (Mistral 7B) | 11434 | Background service |
| **ChromaDB** | Vector database for job matching | - | Embedded |

### Features

- 📄 **PDF Upload** - Extract text from resume PDFs
- 🤖 **AI Enhancement** - Improve bullet points with Mistral 7B
- 🔍 **Job Matching** - Semantic search across 2,277+ jobs
- 📊 **Smart Filtering** - Category-based resume search
- 💾 **Persistent Storage** - All data saved locally

---

## 🎯 How to Use

### 1. Upload Your Resume

- Click **"Upload CV (PDF)"** button
- Select your resume PDF file
- Enter target job title (e.g., "Software Engineer")

### 2. Process with AI

- Click **"Process CV"** button
- AI extracts and enhances your bullet points
- View improved suggestions in real-time

### 3. Find Matching Jobs

- Review enhanced bullet points
- System automatically searches for matching jobs
- View ranked results with similarity scores

---

## 🏗️ Project Structure

```
GenAiProject/
├── 🐳 docker-compose.yml       # Multi-service orchestration
├── 📦 Dockerfile               # App container configuration
├── 📋 requirements.txt         # Python dependencies
│
├── 🎨 Frontend/
│   └── app.py                  # Gradio interface (main entry)
│
├── 🔧 Backend/
│   ├── run_pipeline.py         # CV processing pipeline
│   └── utils/
│       ├── pdf_reader.py       # PDF text extraction
│       └── bullet_extractor.py # AI bullet enhancement
│
├── 🧠 Rag/
│   ├── chroma_setup.py         # Vector DB initialization
│   ├── chroma_ingestion.py     # Embedding generation
│   ├── extract_resumes.py      # Batch PDF processing
│   ├── career_coach_matcher.py # Job matching API
│   └── quickstart.py           # Setup automation
│
└── 💾 Data/
    ├── chromadb/               # Vector database storage
    ├── Job_Descriptions/       # 2,277+ job postings
    └── raw/cv_samples/         # 1,000+ resume samples
```


## ⚙️ Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - PORT=7860                    # Gradio web port
  - OLLAMA_HOST=http://ollama:11434
  - OLLAMA_MODEL=mistral         # LLM model (mistral/tinyllama)
  - GRADIO_SERVER_NAME=0.0.0.0  # Bind address
```


## 🗂️ Database Details

### Vector Database (ChromaDB)

| Collection | Documents | Purpose |
|-----------|-----------|---------|
| **Resumes** | 1,000+ | Resume embeddings across 9 categories |
| **Jobs** | 2,277 | Job description embeddings |

### Resume Categories

```
✓ ENGINEERING              ✓ INFORMATION-TECHNOLOGY
✓ FINANCE                  ✓ PUBLIC-RELATIONS  
✓ FITNESS                  ✓ SALES
✓ HEALTHCARE               ✓ TEACHER
✓ HR
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Embeddings** | `all-MiniLM-L6-v2` | 384-dim semantic vectors |
| **Vector DB** | ChromaDB | Fast similarity search |
| **LLM** | Mistral 7B | Text generation & enhancement |
| **Frontend** | Gradio | Web interface |
| **PDF Processing** | PyPDF2 | Text extraction |



## 👥 Team

<table>
<tr>
<td align="center">
<b>Robin De Meyer</b><br>
</td>
<td align="center">
<b>Roan Vandemeulebroucke</b><br>
</td>
</tr>
</table>

---

## 📄 License

**Academic Project** - Howest University (2025-2026)  
Gen AI Course - AI Career Coach Application

---

## 🔗 Resources

- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [Gradio Documentation](https://www.gradio.app/docs/)
- [Sentence Transformers](https://www.sbert.net/)

---

<div align="center">

**Made with ❤️ using Python, Docker, ChromaDB & Ollama**

*Last Updated: December 4, 2025*

</div>
