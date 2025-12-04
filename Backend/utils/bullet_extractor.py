import os

import ollama


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

def extract_bullets_with_ollama(raw_text):
    prompt = f"""
    You will receive raw text extracted from a CV. This text may be messy, contain headings,
    long lines, or irrelevant information.

    Your task is:

    ✔ Extract ONLY the meaningful bullet points about:
      - Work experience
      - Education
      - Skills
      - Achievements
      - Strengths

    ✔ Rewrite them into clean, short, professional bullet points.
    ✔ Remove section titles such as 'WERKERVARING', 'OPLEIDING', etc.
    ✔ Remove emails, phone numbers, addresses.
    ✔ DO NOT invent content. Only rewrite what is present.

    Return the result as a list of bullet points like:

    - Example bullet point
    - Another example
    - ...

    === RAW CV TEXT ===
    {raw_text}
    """

    response = ollama.generate(
      model=OLLAMA_MODEL,
      prompt=prompt
    )

    return response["response"]
