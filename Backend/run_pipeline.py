from utils.pdf_reader import pdf_to_text
from utils.bullet_extractor import extract_bullets_with_ollama

def process_cv(pdf_path):
    txt_path = "cv_output.txt"

    # Step 1: Convert PDF → Raw text
    pdf_to_text(pdf_path, txt_path)

    # Step 2: Read the raw text
    with open(txt_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Step 3: Use Ollama to clean and extract bullet points
    print("🤖 Cleaning bullet points with Ollama...")
    bullets = extract_bullets_with_ollama(raw_text)

    print("\n=== CLEAN BULLET POINTS ===\n")
    print(bullets)

    # Save output
    with open("clean_bullets.txt", "w", encoding="utf-8") as f:
        f.write(bullets)

    print("\n[✔] Resultaten opgeslagen in: clean_bullets.txt")

    return bullets


if __name__ == "__main__":
    process_cv("sample_cv.pdf")
