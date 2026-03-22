import json, sys, os
from pathlib import Path
import fitz
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def extract_pdf(pdf_path: str, images_dir: str) -> tuple:
    """Returns (full_text, list_of_saved_image_paths)"""
    Path(images_dir).mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    full_text = ""
    image_paths = []

    for page_num, page in enumerate(doc):
        full_text += page.get_text()
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            ext = base_image["ext"]
            img_path = os.path.join(images_dir, f"page{page_num+1}_img{img_index+1}.{ext}")
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            image_paths.append(img_path)

    doc.close()
    return full_text, image_paths


def extract_with_groq(pdf_text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = """Extract the following fields from this German property exposé text. 
Return ONLY valid JSON. If a field is missing use null. All numbers must be numbers not strings.

{
  "plz": "the postal code (Postleitzahl) of the property",
  "baujahr": "the year the building was constructed (Baujahr)",
  "strasse": "the street name only, without the house number",
  "hausnummer": "the house number only",
  "wohnflaeche_gesamt_qm": "total living area in square meters",
  "kaufpreis": "purchase price in euros as number",
  "anzahl_wohneinheiten": "total number of residential units",
  "anzahl_stellplaetze": "total number of parking spaces",
  "units": [
    {
      "nr": 1,
      "etage": "EG",
      "lage": "li",
      "flaeche_qm": 46.95,
      "nkm_monat": 417.83,
      "nkm_qm": 8.90,
      "mietbeginn": "01.11.2015"
    }
  ]
}

Return the actual extracted values, not the descriptions above.

Exposé text:
""" + pdf_text[:12000]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else "Case Study Exposé (1).pdf"

    # Output paths
    output_dir = Path("output")
    images_dir = str(output_dir / "images")

    # Step 1 — Extract text + images
    text, image_paths = extract_pdf(pdf, images_dir)
    print(f"✓ Extracted {len(image_paths)} images → {images_dir}")

    # Step 2 — Extract structured data
    data = extract_with_groq(text)

    # Step 3 — Save JSON
    out = output_dir / "extracted_data.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n✓ Data saved → {out}")
    print(f"✓ Images saved → {images_dir} ({len(image_paths)} files)")