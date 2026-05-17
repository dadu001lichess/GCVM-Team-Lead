import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# CONFIGURATIE VIA DE LINK VAN JE SPREADSHEET
# Plak hieronder de VOLLEDIGE weblink van jouw Google Sheet (alles uit je adresbalk)!
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1S0ZpBX9067r0rsjjwWpcwIAYYw0X9Dgix8YObPAaGLI/edit?usp=sharing"
TABBLAD_NAME = "Growing Chess Shards Ledger"  # <-- Pas dit aan naar "Sheet1" als je tabblad onderaan Engels is!

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

def update_spreadsheet_speler(username, shards_to_give=25):
    """
    Controleert de sheet via de URL. 
    Als de speler er al in staat -> Doet niets.
    Als de speler er nog NIET in staat -> Voegt speler toe met 25 Shards.
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
        
        # Open de sheet direct via de unieke URL
        sheet = client.open_by_url(SPREADSHEET_URL).worksheet(TABBLAD_NAME)
        
        # Haal alle bestaande gebruikersnamen op uit Kolom A (Member Name)
        gebruikersnamen_kolom = [name.lower() for name in sheet.col_values(1) if name]
        target_username = username.lower()
        
        if target_username in gebruikersnamen_kolom:
            print(f"ℹ️ {username} staat al in de spreadsheet. Geen wijzigingen aangebracht.")
            return True
        else:
            # Speler staat er nog NIET in! We gaan een nieuwe rij toevoegen onderaan
            nu_tekst = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # Een nieuwe rij met: [Kolom A, Kolom B, Kolom C]
            nieuwe_rij = [username, shards_to_give, nu_tekst]
            sheet.append_row(nieuwe_rij)
            
            print(f"🎉 Nieuwe speler gedetecteerd! {username} toegevoegd aan spreadsheet met {shards_to_give} Shards!")
            return True
            
    except Exception as e:
        print(f"❌ Fout bij het communiceren met Google Sheets: {e}")
        return False
