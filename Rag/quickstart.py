"""
Quick Start Script for ChromaDB Setup
Run this to set up ChromaDB with one command
"""

import sys
import subprocess
from pathlib import Path
import os

def run_command(description: str, command: str):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"Step: {description}")
    print(f"{'='*60}")
    print(f"Running: {command}\n")
    
    # Use full Python path on Windows to avoid alias conflicts
    if command.startswith("python "):
        python_exe = Path(sys.executable).as_posix()
        command = command.replace("python ", f'"{python_exe}" ', 1)
    
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"\n✗ FAILED: {description}")
        return False
    else:
        print(f"\n✓ SUCCESS: {description}")
        return True


def main():
    """Main quick-start routine."""
    
    print("""
============================================================
  ChromaDB Vector Database - Quick Start Setup
  AI Career Coach Application
============================================================
    """)
    
    # Get script directory
    rag_dir = Path(__file__).parent
    project_dir = rag_dir.parent
    
    print(f"Project Directory: {project_dir}")
    print(f"RAG Directory: {rag_dir}\n")
    
    steps = [
        ("Install Dependencies", 
         f"pip install -r \"{rag_dir / 'requirements_chroma.txt'}\""),
        
        ("Initialize ChromaDB",
         f"python \"{rag_dir / 'chroma_setup.py'}\""),
        
        ("Extract Resume Text from PDFs",
         f"python \"{rag_dir / 'extract_resumes.py'}\""),
        
        ("Ingest Documents into ChromaDB",
         f"python \"{rag_dir / 'chroma_ingestion.py'}\""),
    ]
    
    completed = 0
    
    for description, command in steps:
        if run_command(description, command):
            completed += 1
        else:
            print("\n✗ Setup failed. Please fix the error and run again.")
            sys.exit(1)
    
    # Final summary
    print(f"\n{'='*60}")
    print("✓ ChromaDB Setup Complete!")
    print(f"{'='*60}")
    print(f"\nCompleted {completed}/{len(steps)} steps")
    print(f"""
Next Steps:
1. Verify setup by running:
   python "{rag_dir / 'career_coach_matcher.py'}"

2. Read the setup guide:
   "{rag_dir / 'CHROMA_SETUP.md'}"

3. Start building your Career Coach features!

Database Location: {project_dir / 'Data' / 'chromadb'}
Extracted Resumes: {project_dir / 'Data' / 'resumes_extracted.csv'}
    """)


if __name__ == "__main__":
    main()
