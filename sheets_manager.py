import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# GEGEVENS VOOR DE SPREADSHEET
SPREADSHEET_NAME = "https://docs.google.com/spreadsheets/d/1S0ZpBX9067r0rsjjwWpcwIAYYw0X9Dgix8YObPAaGLI/edit?gid=2015825906#gid=2015825906T"  # <-- VERVANG DIT door de exacte naam van je Google Sheet!
TABBLAD_NAME = "Growing Chess Shards Ledger"  # <-- Pas dit aan als je tabblad anders heet (bijv. Sheet1)

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

def update_spreadsheet_speler(username, shards_to_add=25):
    """Controleert de sheet en voegt Shards toe als de speler bestaat."""
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
        
        # Haal alle gebruikersnamen op uit Kolom A (Member Name)
        gebruikersnamen_kolom = [name.lower() for name in sheet.col_values(1)]
        target_username = username.lower()
        
        if target_username in gebruikersnamen_kolom:
            # De speler is gevonden! Bepaal op welke rij hij staat
            rij_nummer = gebruikersnamen_kolom.index(target_username) + 1
            
            # Haal de huidige Shards op uit Kolom B (Shards Balance)
            huidige_shards_tekst = sheet.cell(rij_nummer, 2).value
            
            try:
                huidige_shards = int(huidige_shards_tekst) if huidige_shards_tekst else 0
            except ValueError:
                huidige_shards = 0
                
            nieuwe_shards = huidige_shards + shards_to_add
            
            # Huidige datum/tijd voor Kolom C (Last Updated)
            nu_tekst = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            
            # Update Kolom B (Shards Balance) en Kolom C (Last Updated)
            sheet.update_cell(rij_nummer, 2, nieuwe_shards)
            sheet.update_cell(rij_nummer, 3, nu_tekst)
            
            print(f"💰 Spreadsheet geüpdatet voor {username}: {huidige_shards} ➡️ {nieuwe_shards} Shards!")
            return True
        else:
            print(f"⚠️ {username} staat niet in de spreadsheet onder 'Member Name'. Niets aangepast.")
            return False
            
    except Exception as e:
        print(f"❌ Fout bij het communiceren met Google Sheets: {e}")
        return False
