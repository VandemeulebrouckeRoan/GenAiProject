"""
Resume PDF Text Extraction
Extracts text from PDF resumes and saves to CSV for ChromaDB ingestion
"""

import os
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# Configuration
DATA_PATH = Path(__file__).parent.parent / "Data"
CV_SAMPLES_PATH = DATA_PATH / "raw" / "cv_samples" / "data" / "data"
OUTPUT_CSV_PATH = DATA_PATH / "resumes_extracted.csv"
BATCH_SIZE = 50


class ResumeExtractor:
    """Extracts text from PDF resumes using available libraries."""
    
    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize the extractor.
        
        Args:
            use_pdfplumber: Prefer pdfplumber if available (better for formatted PDFs)
        """
        self.use_pdfplumber = use_pdfplumber and HAS_PDFPLUMBER
        self.use_pypdf2 = HAS_PYPDF2
        
        if not (self.use_pdfplumber or self.use_pypdf2):
            raise ImportError("Neither PyPDF2 nor pdfplumber installed. Install with: pip install PyPDF2 pdfplumber")
        
        print(f"Using PDF extraction: pdfplumber={self.use_pdfplumber}, PyPDF2={self.use_pypdf2}")
    
    def extract_text_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """Extract text using pdfplumber (better for formatted PDFs)."""
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts) if text_parts else None
        except Exception as e:
            print(f"  Error extracting with pdfplumber: {e}")
            return None
    
    def extract_text_pypdf2(self, pdf_path: str) -> Optional[str]:
        """Extract text using PyPDF2 (fallback method)."""
        try:
            text_parts = []
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return "\n".join(text_parts) if text_parts else None
        except Exception as e:
            print(f"  Error extracting with PyPDF2: {e}")
            return None
    
    def extract(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using best available method.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text or None if extraction fails
        """
        if not os.path.exists(pdf_path):
            return None
        
        # Try preferred method first
        if self.use_pdfplumber:
            text = self.extract_text_pdfplumber(pdf_path)
            if text:
                return text
        
        # Fallback to PyPDF2
        if self.use_pypdf2:
            text = self.extract_text_pypdf2(pdf_path)
            if text:
                return text
        
        return None


def find_resume_files(cv_path: Optional[str] = None) -> Dict[str, List[Tuple[str, str]]]:
    """
    Find all resume PDFs organized by category.
    
    Args:
        cv_path: Path to CV samples root directory
    
    Returns:
        Dictionary mapping category to list of (category, pdf_path) tuples
    """
    if cv_path is None:
        cv_path = CV_SAMPLES_PATH
    
    cv_path = Path(cv_path)
    
    if not cv_path.exists():
        print(f"Warning: CV path not found: {cv_path}")
        return {}
    
    resumes_by_category = {}
    
    # Walk through category directories
    for category_dir in cv_path.iterdir():
        if not category_dir.is_dir():
            continue
        
        category_name = category_dir.name
        pdf_files = list(category_dir.glob("*.pdf"))
        
        if pdf_files:
            resumes_by_category[category_name] = [
                (category_name, str(pdf_path))
                for pdf_path in sorted(pdf_files)
            ]
            print(f"Found {len(pdf_files)} PDFs in {category_name}")
    
    total = sum(len(files) for files in resumes_by_category.values())
    print(f"\nTotal resume PDFs found: {total} across {len(resumes_by_category)} categories\n")
    
    return resumes_by_category


def extract_all_resumes(output_path: Optional[str] = None, cv_path: Optional[str] = None) -> int:
    """
    Extract text from all resume PDFs and save to CSV.
    
    Args:
        output_path: Path to save extracted resumes CSV
        cv_path: Path to CV samples root directory
    
    Returns:
        Number of successfully extracted resumes
    """
    if output_path is None:
        output_path = OUTPUT_CSV_PATH
    
    # Find resumes
    resumes_by_category = find_resume_files(cv_path)
    
    if not resumes_by_category:
        print("No resume PDFs found!")
        return 0
    
    # Initialize extractor
    try:
        extractor = ResumeExtractor()
    except ImportError as e:
        print(f"Error: {e}")
        return 0
    
    # Extract and save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    extracted_count = 0
    error_count = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['resume_id', 'category', 'file_path', 'resume_text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for category, resumes in resumes_by_category.items():
            print(f"Processing {category}...")
            
            for resume_id, (cat, pdf_path) in enumerate(resumes, start=1):
                # Extract text
                text = extractor.extract(pdf_path)
                
                if text and len(text.strip()) > 20:
                    # Write to CSV
                    writer.writerow({
                        'resume_id': Path(pdf_path).stem,  # Use filename as ID
                        'category': cat,
                        'file_path': pdf_path,
                        'resume_text': text
                    })
                    extracted_count += 1
                    
                    if extracted_count % BATCH_SIZE == 0:
                        print(f"  ✓ Extracted {extracted_count} resumes...")
                else:
                    error_count += 1
                    if error_count <= 5:  # Show first 5 errors
                        print(f"  ✗ Failed to extract: {pdf_path}")
        
        # Summary
        print(f"\n--- Extraction Summary ---")
        print(f"✓ Successfully extracted: {extracted_count} resumes")
        print(f"✗ Failed to extract: {error_count} resumes")
        print(f"Saved to: {output_file}\n")
    
    return extracted_count


if __name__ == "__main__":
    print("=" * 60)
    print("Resume PDF Text Extraction")
    print("=" * 60)
    
    # Extract all resumes
    count = extract_all_resumes()
    
    if count > 0:
        print(f"✓ Extraction complete! {count} resumes ready for ChromaDB ingestion")
    else:
        print("✗ No resumes extracted. Please check:")
        print(f"  - CV samples path: {CV_SAMPLES_PATH}")
        print(f"  - PDF extraction libraries installed")
