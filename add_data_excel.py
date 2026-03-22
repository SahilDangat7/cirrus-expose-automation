import json
import shutil
from pathlib import Path
from openpyxl import load_workbook

# ── Load data
with open("output/extracted_data(3).json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("output/check24_price.json", "r", encoding="utf-8") as f:
    price_data = json.load(f)

# Clean price_per_sqm — remove dots and convert to float
price_per_sqm_raw = price_data["price_per_sqm"]
price_per_sqm = float(str(price_per_sqm_raw).replace(".", "").replace(",", "."))

TEMPLATE = "Case Study (Aufteiler).xlsx"
OUTPUT   = "output/filled_template.xlsx"

# ── Copy template 
shutil.copy(TEMPLATE, OUTPUT)
wb = load_workbook(OUTPUT)

# ── Sheet 1: INPUT_Stammdaten
ws1 = wb["INPUT_Stammdaten"]

adresse = f"{data['strasse']} {data['hausnummer']}"
ws1["C10"] = adresse
ws1["C14"] = data["baujahr"]
ws1["C32"] = data["anzahl_wohneinheiten"]
ws1["C33"] = data["wohnflaeche_gesamt_qm"]
ws1["C39"] = data.get("anzahl_stellplaetze", 11)
ws1["D45"] = data["kaufpreis"]

print(f"✓ Stammdaten filled")

# ── Sheet 2: INPUT_Verkaufseinschätzung Mark 
ws2 = wb["INPUT_Verkaufseinschätzung Mark"]

for i, unit in enumerate(data["units"]):
    row = 9 + i  # rows 9 to 19
    ws2[f"B{row}"] = unit["nr"]
    ws2[f"C{row}"] = "Wohnung"
    ws2[f"D{row}"] = unit["etage"]
    ws2[f"F{row}"] = unit["flaeche_qm"]
    ws2[f"G{row}"] = price_per_sqm  # same Check24 price for all units

print(f"✓ Verkaufseinschätzung filled ({len(data['units'])} units)")

# ── Save
wb.save(OUTPUT)
print(f"✓ Excel saved → {OUTPUT}")