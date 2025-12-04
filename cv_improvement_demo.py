"""
CV Improvement Demo - Compare your CV with successful ones using RAG
"""

import sys
from pathlib import Path

# Add Rag directory to path
sys.path.insert(0, str(Path(__file__).parent / "Rag"))

from career_coach_matcher import CareerCoachMatcher


def analyze_cv(user_cv_text: str, job_title: str = "Software Engineer"):
    """
    Analyze a CV and provide improvement suggestions based on similar CVs.
    
    Args:
        user_cv_text: The user's CV text
        job_title: Target job title (optional)
    """
    print(f"\n{'='*70}")
    print(f"CV IMPROVEMENT ANALYSIS")
    print(f"{'='*70}\n")
    
    # Initialize matcher
    print("🔄 Loading Career Coach Matcher...")
    matcher = CareerCoachMatcher()
    
    # Find similar CVs
    print(f"\n🔍 Finding similar successful CVs in the database...")
    similar_cvs = matcher.find_resumes_for_job(
        job_title=job_title,
        job_description=user_cv_text,
        n_results=5,
        min_score=0.5
    )
    
    if not similar_cvs:
        print("\n⚠️  No similar CVs found in database.")
        return
    
    print(f"\n✅ Found {len(similar_cvs)} similar CVs\n")
    print(f"{'='*70}")
    print("YOUR CV vs. SUCCESSFUL CVs")
    print(f"{'='*70}\n")
    
    # Extract keywords from successful CVs
    all_keywords = []
    for cv in similar_cvs:
        # Simple keyword extraction (you could make this more sophisticated)
        words = cv.text.lower().split()
        all_keywords.extend(words)
    
    # Count frequency
    from collections import Counter
    keyword_freq = Counter(all_keywords)
    
    # Get user CV words
    user_words = set(user_cv_text.lower().split())
    
    # Find common keywords in successful CVs that user is missing
    common_keywords = [word for word, count in keyword_freq.most_common(30) 
                      if count >= 3 and len(word) > 4 and word not in user_words]
    
    # Display similar CVs
    print("📊 Top Similar CVs:\n")
    for i, cv in enumerate(similar_cvs, 1):
        category = cv.metadata.get('category', 'Unknown')
        similarity = cv.similarity_score * 100
        print(f"{i}. Category: {category}")
        print(f"   Match Score: {similarity:.1f}%")
        print(f"   Preview: {cv.text[:150]}...")
        print()
    
    # Provide suggestions
    print(f"\n{'='*70}")
    print("💡 IMPROVEMENT SUGGESTIONS")
    print(f"{'='*70}\n")
    
    print("1. KEYWORDS YOU MIGHT BE MISSING:")
    print("   (These appear frequently in similar successful CVs)\n")
    for keyword in common_keywords[:10]:
        print(f"   • {keyword}")
    
    print("\n2. BEST MATCHING CV CATEGORY:")
    if similar_cvs:
        best_category = similar_cvs[0].metadata.get('category', 'Unknown')
        print(f"   Your CV is most similar to: {best_category}")
        print(f"   Consider highlighting skills relevant to this field")
    
    print("\n3. STRUCTURE TIPS:")
    print("   • Make sure your CV includes technical skills section")
    print("   • Add specific project examples with measurable results")
    print("   • Include relevant certifications and education")
    print("   • Use action verbs (developed, implemented, managed, etc.)")
    
    print("\n4. NEXT STEPS:")
    print("   • Add missing keywords that are relevant to your experience")
    print("   • Quantify your achievements (increased by X%, reduced by Y%)")
    print("   • Tailor your CV to match the job descriptions you're targeting")
    
    print(f"\n{'='*70}\n")


def main():
    """Main demo function."""
    print("\n" + "="*70)
    print("   CV IMPROVEMENT ANALYZER")
    print("="*70)
    
    # Example user CV (short version for demo)
    sample_cv = """
    John Doe
    Software Developer
    
    Experience:
    - Worked on web applications
    - Used Python and JavaScript
    - Built some APIs
    
    Education:
    - Bachelor in Computer Science
    
    Skills:
    - Python
    - JavaScript
    - HTML/CSS
    """
    
    print("\n📄 Sample CV:")
    print("-" * 70)
    print(sample_cv)
    print("-" * 70)
    
    # Analyze the CV
    analyze_cv(sample_cv, job_title="Software Engineer")
    
    print("\n" + "="*70)
    print("You can modify the 'sample_cv' text to analyze your own CV!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
