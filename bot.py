import os
import requests
import re
from sheets_manager import update_spreadsheet_speler

TEAM_ID = "growing-chess-variants-masters"
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

def get_usernames_from_html(html_text):
    """
    Scant de HTML op zoek naar de directe acceptatie-links:
    /team/id/request/username/accept
    """
    pattern = rf"/team/{TEAM_ID}/request/([\w-]+)/accept"
    return re.findall(pattern, html_text)

def check_and_accept_requests():
    if not LICHESS_TOKEN:
        print("❌ Fout: LICHESS_TOKEN secret is niet ingesteld!")
        return

    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN.strip()}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # We richten ons nu direct op de specifieke verzoeken-pagina van het team
    requests_page_url = f"https://lichess.org/team/{TEAM_ID}/requests"
    
    try:
        print(f"🔄 Verzoeken-pagina direct scannen...")
        response = requests.get(requests_page_url, headers=headers)
        
        if response.status_code == 200:
            # Haal de gebruikersnamen uit de pagina
            wachtrij_spelers = get_usernames_from_html(response.text)
            wachtrij_spelers = list(set(wachtrij_spelers))
            
            if not wachtrij_spelers:
                print("ℹ️ Geen openstaande verzoeken gevonden in de HTML. De wachtrij is op dit moment leeg of al verwerkt!")
                return
                
            print(f"👀 {len(wachtrij_spelers)} verzoek(en) ontdekt: {', '.join(wachtrij_spelers)}")
            
            for username in wachtrij_spelers:
                print(f"⚙️ Automatisch verwerken van speler: {username}...")
                
                # 1. Update Google Sheet
                sheet_succes = update_spreadsheet_speler(username)
                
                if sheet_succes:
                    # 2. Accepteer op Lichess
                    accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{username.lower()}/accept"
                    accept_response = requests.post(accept_url, headers=headers)
                    
                    if accept_response.status_code == 200:
                        print(f"✅ {username} succesvol toegevoegd via pagina-scan!")
                    else:
                        print(f"❌ Kon {username} niet accepteren. Code: {accept_response.status_code}")
        else:
            print(f"❌ Kon de pagina niet laden. Statuscode: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Er ging iets mis tijdens het scannen: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot (Directe Scanner Modus) ---")
    check_and_accept_requests()
