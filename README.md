# Cirrus Exposé Automation

Automated pipeline for processing real estate exposés. Extracts property data from PDF, scrapes market valuation from Check24, populates Excel template, and uploads everything to Google Drive.

## What it does

Manual process at Cirrus: 20–30 minutes per exposé (read PDF → copy data → look up prices → fill Excel)

Automated process: ~60 seconds end to end

## Pipeline
```
PDF Exposé
    ↓
extract_pdf.py       → Extracts text + 19 images, sends to Groq AI → output/extracted_data.json
    ↓
scrape_logic.py      → Opens Check24, fills form with property data, scrapes price/m² → output/check24_price.json
    ↓
populate_excel.py    → Reads both JSONs, fills Excel template (Stammdaten + Verkaufseinschätzung) → output/filled_template.xlsx
    ↓
upload_drive.py      → Creates Google Drive folder, uploads Excel + images
```

## Tech Stack

| Tool | Purpose |
|---|---|
| PyMuPDF | PDF text + image extraction |
| Groq API (Llama 3.3 70B) | AI-powered structured data extraction from German text |
| Playwright | Headless browser automation for Check24 scraping |
| openpyxl | Excel template population |
| Google Drive API | Cloud storage upload |
| python-dotenv | Environment variable management |

## Setup

**1. Clone the repo:**
```bash
git clone https://github.com/SahilDangat7/cirrus-expose-automation.git
cd cirrus-expose-automation
```

**2. Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**4. Create `.env` file:**
```
GROQ_API_KEY=your-groq-api-key
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id
```
## Note on Wohnfläche
Check24 accepts maximum 500m². Since the total area (594m²) exceeds this,
the script automatically uses average per unit (594 / 11 = 54m²) which is
the correct approach as Check24 valuates individual apartments not whole buildings.

**5. Add Google credentials:**
- `service_account.json` — Google service account key
- `credentials.json` — OAuth client credentials

## Usage

Run each script in order:
```bash
# Step 1 — Extract data from PDF
python extract_pdf.py "your_expose.pdf"

# Step 2 — Scrape market price from Check24
python scrape_logic.py

# Step 3 — Populate Excel template
python populate_excel.py

# Step 4 — Upload to Google Drive
python upload_drive.py
```

## Output

- `output/extracted_data.json` — structured property data
- `output/check24_price.json` — market valuation from Check24
- `output/filled_template.xlsx` — completed Excel template
- `output/images/` — all property images extracted from PDF
- `output/drive_links.json` — Google Drive folder URLs

## Google Drive

Files are automatically uploaded to a shared Google Drive folder:
- Filled Excel template
- Property images subfolder

## Error Handling

- Missing PDF fields → Groq returns `null`, script continues
- Check24 scraping fails → price written as `null`, Excel still generated
- Drive upload fails → local files preserved in `output/`

## Adaptability

All thresholds and configuration values are in `populate_excel.py` at the top. No need to touch the core logic when acquisition criteria change.

## Note on Google Photos

The case study requested Google Photos integration. The Google Photos API requires a paid Google One plan. As a free alternative, property images are uploaded to a `/images` subfolder inside the Google Drive folder — achieving the same result at zero cost.

## Links
- Google Drive: https://drive.google.com/drive/folders/YOUR_FOLDER_ID
- GitHub: https://github.com/SahilDangat7/cirrus-expose-automation

## Sample Output
- Extracted 11 units from PDF
- Check24 market price: 1,956 €/m² 
- Uploaded to Google Drive: Excel + 19 property images