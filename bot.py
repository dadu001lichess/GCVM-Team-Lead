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
    
    # TEST: Vraag aan Lichess wie dit account is
    try:
        me_response = requests.get("https://lichess.org/api/account", headers=headers)
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"👋 Bot is succesvol ingelogd als account: {me_data.get('username')}")
        else:
            print(f"⚠️ Kon accountgegevens niet ophalen. Status: {me_response.status_code}")
    except Exception:
        pass

    # Haal daarna de aanvragen op
    url = f"https://lichess.org/api/team/{TEAM_ID}/requests"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            lines = response.text.strip().split("\n")
            aanvragen = [json.loads(line) for line in lines if line]
            
            if not aanvragen or (len(aanvragen) == 1 and not aanvragen[0]):
                print("ℹ️ Geen openstaande aanvragen gevonden.")
                return

            print(f"👀 {len(aanvragen)} aanvraag/aanvragen gevonden!")
            
            for aanvraag in aanvragen:
                username = aanvraag.get("user", {}).get("id")
                if username:
                    print(f"⚙️ Verwerken van speler: {username}...")
                    sheet_succes = update_spreadsheet_speler(username)
                    
                    if sheet_succes:
                        accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{username}/accept"
                        accept_response = requests.post(accept_url, headers=headers)
                        if accept_response.status_code == 200:
                            print(f"✅ {username} succesvol toegelaten tot het team!")
                        else:
                            print(f"❌ Kon {username} niet accepteren op Lichess. Code: {accept_response.status_code}")
        
        elif response.status_code == 403:
            print("❌ Lichess weigert de verbinding. Statuscode: 403")
            print("⚠️ Controleer of het token geen spaties bevat en team:lead rechten heeft!")
        else:
            print(f"❌ Fout bij ophalen van aanvragen. Statuscode: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Er ging iets mis: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot ---")
    print(f"Bot actief! Controleren op team: {TEAM_ID}...")
    check_and_accept_requests()
