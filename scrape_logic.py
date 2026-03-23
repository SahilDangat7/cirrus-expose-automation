from playwright.sync_api import sync_playwright
import json
import os
from pathlib import Path

with open("output/extracted_data.json", "r", encoding="utf-8") as f:
    extracted_data = json.load(f)

# ── Static test data from the exposé
PLZ         = str(extracted_data["plz"])
BAUJAHR     = str(extracted_data["baujahr"])
STRASSE     = extracted_data["strasse"]
NR          = str(extracted_data["hausnummer"])
avg_flaeche = int(extracted_data["wohnflaeche_gesamt_qm"] / extracted_data["anzahl_wohneinheiten"])
WOHNFLAECHE = str(avg_flaeche) 
ZIMMER      = "2"
BADEZIMMER  = "1"
ZUSTAND     = "gut erhalten"    
AUSSTATTUNG = "normal"          
VORHABEN    = "verkaufen"
ZEITRAUM    = "1-3 Monate"

URL = "https://www.check24.de/baufinanzierung/immobilienbewertung/"

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Opening Check24")
        page.goto(URL, timeout=30000)
        page.wait_for_timeout(3000)

        #Accept cookies 
        page.get_by_text("geht klar", exact=True).click(timeout=8000)
        print("Cookies accepted")
        page.wait_for_timeout(2000)

        #Click zur Immobilienbewertung
        page.locator("xpath=//*[@id='__layout']/main/aside[1]/div[2]/section/form/button").click(timeout=8000)
        print("Navigated to form")
        page.wait_for_timeout(3000)

        #Select Eigentumswohnung
        page.locator("xpath=//*[@id='c24-content']/main/div[2]/div/div/div[2]/div/form/div/fieldset[1]/div/div[1]/div/div/section/div/div/div/div/div/label/div/select").select_option(value="1")
        print("Selected Eigentumswohnung")
        page.wait_for_timeout(500)

        #Fill Baujahr 
        page.locator("xpath=//*[@id='c24-content']/main/div[2]/div/div/div[2]/div/form/div/fieldset[1]/div/div[5]/div/div/section/div/div/div/div/div/label/span/input").fill(BAUJAHR)
        print(f"Filled Baujahr: {BAUJAHR}")
        page.wait_for_timeout(500)

        #Fill PLZ
        page.locator("input[qa-ref='control-element']").nth(0).click()
        page.keyboard.type(PLZ, delay=100)
        page.keyboard.press("Enter") 
        print(f"Filled PLZ: {PLZ}")
        page.wait_for_timeout(8000)  # wait for city dropdown to appear

        #Select city
        page.locator("xpath=//*[@id='c24-content']/main/div[2]/div/div/div[2]/div/form/div/fieldset[1]/div/div[2]/div/div/section/div/div/div/div/div/div/div/div[2]/label/div/select").select_option(index=1)
        print("Selected city: Bernau bei Berlin")
        page.wait_for_timeout(5000)

        #Fill Straße AFTER city is selected
        strasse_input = page.locator("input[qa-ref='control-element']").nth(1)
        strasse_input.click()
        page.wait_for_timeout(500)
        page.keyboard.type(STRASSE, delay=100)
        page.keyboard.press("Enter")  # ← add this
        print(f"Filled Straße: {STRASSE}")
        page.wait_for_timeout(1000)

        #Fill Nr.
        nr_input = page.locator("input[qa-ref='control-element']").nth(2)
        nr_input.click()
        page.wait_for_timeout(500)
        page.keyboard.type(NR, delay=100)
        page.keyboard.press("Enter")  # ← add this
        print(f"Filled Nr.: {NR}")
        page.wait_for_timeout(1000)

        #Select Zustand → gut erhalten
        page.locator("select[id*='zustand'], select").filter(has_text="gut erhalten").first.select_option(index=1)
        print("Selected Zustand: gut erhalten")
        page.wait_for_timeout(500)

        #Gesamte Wohnfläche
        wohnflaeche_input = page.locator("input[qa-ref='control-element']").nth(3)
        wohnflaeche_input.click()
        page.wait_for_timeout(300)
        page.keyboard.type(WOHNFLAECHE, delay=100)
        page.keyboard.press("Enter")  # ← add this
        print(f"Filled Wohnfläche: {WOHNFLAECHE}m²")
        page.wait_for_timeout(500)

        #Ausstattung → normal
        page.locator("xpath=//*[@id='c24-content']/main/div[2]/div/div/div[2]/div/form/div/fieldset[1]/div/div[7]/div[1]/div/section/div/div/div/div/div/label/div/select").select_option(index=2)
        print("Selected Ausstattung: normal")
        page.wait_for_timeout(500)

        #Fill Zimmer
        zimmer_input = page.locator("input[qa-ref='control-element']").nth(5)
        zimmer_input.click()
        page.wait_for_timeout(300)
        page.keyboard.type(ZIMMER, delay=100)
        page.keyboard.press("Enter")  # ← add this
        print(f"✓ Filled Zimmer: {ZIMMER}")
        page.wait_for_timeout(500)

        #Select Badezimmer → 1
        page.locator("xpath=//*[@id='c24-content']/main/div[2]/div/div/div[2]/div/form/div/fieldset[2]/div/div[1]/div/section/div/div/div/div/section[2]/div/div/div/div/div/label/div/select").select_option(index=1)
        print("Selected Badezimmer: 1")
        page.wait_for_timeout(500)

        #Click Verkaufen 
        page.get_by_text("Verkaufen", exact=True).click()
        print("Selected Verkaufen")
        page.wait_for_timeout(500)

        #Select Zeitraum → 1-3 Monate 
        page.get_by_text("1-3 Monate", exact=True).click()
        print("Selected Zeitraum: 1-3 Monate")
        page.wait_for_timeout(500)

       #Click submit
        page.locator("xpath=//*[@id='c24-content']/main/div[2]/div/div/div[2]/div/form/button").click(timeout=8000)
        print("Clicked submit")
        page.wait_for_timeout(5000)

        #Extract price using exact XPath
        page.wait_for_timeout(5000)

       
        # ── Extract price
        page.wait_for_timeout(15000)  # increase wait to 15 seconds
        page.screenshot(path="output/check24_result.png")
        try:
    # Check if result is inside an iframe
            frames = page.frames
            print(f"  Frames found: {len(frames)}")
            for i, frame in enumerate(frames):
                print(f"  Frame {i}: {frame.url}")

            # Try extracting from each frame
            for frame in page.frames:
                try:
                    result = frame.evaluate("""
                        () => {
                            const spans = document.querySelectorAll('dib-price span span');
                            return Array.from(spans).map(el => el.innerText);
                        }
                    """)
                    if result and any(result):
                        print(f"\n Found in frame: {frame.url}")
                        print(f" All price values: {result}")
                        if len(result) >= 2:
                            marktwert = result[0]
                            price_per_sqm = result[1]
                            print(f"Marktwert: {marktwert} €")
                            print(f" Price per m²: {price_per_sqm} €/m²")
                            
                            Path("output").mkdir(exist_ok=True)
                            price_data = {
                                "marktwert": marktwert,
                                "price_per_sqm": price_per_sqm,
                                "source": "check24.de"
                            }
                            with open("output/check24_price.json", "w") as f:
                                json.dump(price_data, f, indent=2)
                            print(f"Price saved → output/check24_price.json")
                        break
                except Exception:
                    continue

        except Exception as e:
            print(f"Failed: {e}")

    print("\nBrowser staying open — press Enter to close")
    input()

       
if __name__ == "__main__":
    scrape()