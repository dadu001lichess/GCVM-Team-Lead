import os
import requests
import json
from sheets_manager import update_spreadsheet_speler

TEAM_ID = "growing-chess-variants-masters"
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

def check_and_accept_requests():
    if not LICHESS_TOKEN:
        print("❌ Fout: LICHESS_TOKEN secret is niet ingesteld!")
        return

    headers = {"Authorization": f"Bearer {LICHESS_TOKEN.strip()}"}
    
    # We gebruiken nu het 'pm' (public/manage) endpoint of proberen direct de acceptatie 
    # op basis van de openbare join-wachtrij als die er is.
    url = f"https://lichess.org/api/team/{TEAM_ID}/requests"
    
    try:
        response = requests.get(url, headers=headers)
        
        # Als Lichess weer 403 geeft op de wachtrij, gebruiken we de 'Brute Force' methode voor je test-account!
        if response.status_code == 403:
            print("ℹ️ Lichess blokkeert de wachtrij-lijst voor persoonlijke tokens (Status 403).")
            print("🚀 Schakelen over naar directe acceptatie-modus...")
            
            # Vul hier de gebruikersnaam van je test-account in (bijvoorbeeld: "test_account")
            # De bot probeert hem dan direct te accepteren!
            test_username = "Distant_Abyss" 
            
            if test_username != "VUL_HIER_DE_NAAM_VAN_JE_TEST_ACCOUNT_IN":
                accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{test_username.lower()}/accept"
                accept_response = requests.post(accept_url, headers=headers)
                
                if accept_response.status_code == 200:
                    print(f"✅ Het is gelukt! {test_username} is succesvol geaccepteerd via het token!")
                    update_spreadsheet_speler(test_username)
                else:
                    print(f"❌ Lichess weigert ook de directe acceptatie. Code: {accept_response.status_code}")
                    print("⚠️ Dit betekent dat Lichess PERSOONLIJKE tokens van spelersaccounts definitief heeft buitengesloten voor team-beheer.")
            else:
                print("💡 Vul in bot.py even de naam van je test-account in op regel 25 om te kijken of direct accepteren wel mag!")
            return

        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            aanvragen = [json.loads(line) for line in lines if line]
            
            for aanvraag in aanvragen:
                username = aanvraag.get("user", {}).get("id")
                if username:
                    sheet_succes = update_spreadsheet_speler(username)
                    if sheet_succes:
                        accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{username}/accept"
                        requests.post(accept_url, headers=headers)
                        print(f"✅ {username} succesvol toegelaten!")
                        
    except Exception as e:
        print(f"❌ Er ging iets mis: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot ---")
    check_and_accept_requests()
