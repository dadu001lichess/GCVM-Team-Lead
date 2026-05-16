import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# GEGEVENS VOOR DE SPREADSHEET
SPREADSHEET_NAME = "https://docs.google.com/spreadsheets/d/1S0ZpBX9067r0rsjjwWpcwIAYYw0X9Dgix8YObPAaGLI/edit?gid=2015825906#gid=2015825906"  # <-- VERVANG DIT door de exacte naam van je Google Sheet!
TABBLAD_NAME = "Growing Chess Shards Ledger"  # <-- Pas dit aan als je tabblad anders heet (bijv. Sheet1)

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

def update_spreadsheet_speler(username, shards_to_give=25):
    """
    Controleert de sheet. 
    Als de speler er al in staat -> Doet helemaal niets.
    Als de speler er nog NIET in staat -> Voegt speler toe met exact 25 Shards.
    """
    if not GOOGLE_CREDENTIALS_JSON:
        print("❌ Fout: GOOGLE_CREDENTIALS secret is niet ingesteld!")
        return False

    try:
        # Verbinding maken met Google Sheets
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Open de sheet
        sheet = client.open(SPREADSHEET_NAME).worksheet(TABBLAD_NAME)
        
        # Haal alle bestaande gebruikersnamen op uit Kolom A (Member Name)
        gebruikersnamen_kolom = [name.lower() for name in sheet.col_values(1) if name]
        target_username = username.lower()
        
        if target_username in gebruikersnamen_kolom:
            print(f"ℹ️ {username} staat al in de spreadsheet. Geen wijzigingen aangebracht.")
            return True
        else:
            # Speler staat er nog NIET in! We gaan een nieuwe rij toevoegen onderaan
            nu_tekst = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # Een nieuwe rij met: [Kolom A (Member Name), Kolom B (Shards Balance), Kolom C (Last Updated)]
            nieuwe_rij = [username, shards_to_give, nu_tekst]
            sheet.append_row(nieuwe_rij)
            
            print(f"🎉 Nieuwe speler gedetecteerd! {username} toegevoegd aan spreadsheet met {shards_to_give} Shards!")
            return True
            
    except Exception as e:
        print(f"❌ Fout bij het communiceren met Google Sheets: {e}")
        return False
