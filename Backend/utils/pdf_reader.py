import PyPDF2

def pdf_to_text(pdf_path, output_txt_path):
    """
    Converts a PDF CV to a .txt file.
    Works for any PDF that contains real text (not scanned images).
    """
    reader = PyPDF2.PdfReader(pdf_path)
    full_text = ""

    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        except:
            pass

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"[✔] Tekst succesvol opgeslagen in: {output_txt_path}")


# TEST (run this file directly)
if __name__ == "__main__":
    input_pdf = "sample_cv.pdf"       # jouw CV PDF
    output_txt = "cv_output.txt"      # output bestand

    pdf_to_text(input_pdf, output_txt)
