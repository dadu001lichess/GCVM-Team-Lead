import os
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

# GEGEVENS VOOR DE SPREADSHEET
SPREADSHEET_NAME = "https://docs.google.com/spreadsheets/d/1S0ZpBX9067r0rsjjwWpcwIAYYw0X9Dgix8YObPAaGLI/edit?gid=1943069988#gid=1943069988"  # <-- VERVANG DIT door de exacte naam van je Google Sheet!
TABBLAD_NAME = "Growing Chess Shards Ledger"  # <-- Pas dit aan als je tabblad anders heet (bijv. Sheet1)

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

def update_spreadsheet_speler(username, shards_to_give=25):
    """
    Controleert de sheet. 
    Als de speler er al in staat -> Geen actie.
    Als de speler er nog NIET in staat -> Voeg toe met 25 Shards.
    """
    if not GOOGLE_CREDENTIALS_JSON:
        print("❌ Fout: GOOGLE_CREDENTIALS secret is niet ingesteld!")
        return False

    try:
        # Verbinding maken met Google Sheets
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
