import os
import requests
import re
from sheets_manager import update_spreadsheet_speler

TEAM_ID = "growing-chess-variants-masters"
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

def get_usernames_from_team_page(html_text):
    """
    Scant de HTML van de Lichess teampagina om gebruikersnamen 
    te vinden van spelers die een openstaande aanvraag hebben.
    """
    # Lichess gebruikt specifieke links voor gebruikers die willen joinen: /team/id/request/username/accept
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
    
    # We vragen de normale, visuele teampagina op waar de aanvragen op staan
    team_page_url = f"https://lichess.org/team/{TEAM_ID}"
    
    try:
        print(f"🔄 Teampagina scannen op openstaande aanvragen...")
        response = requests.get(team_page_url, headers=headers)
        
        if response.status_code == 200:
            # Zoek alle gebruikersnamen in de pagina die in de wachtrij staan
            wachtrij_spelers = get_usernames_from_team_page(response.text)
            
            # Filter dubbele namen eruit mochten die erin staan
            wachtrij_spelers = list(set(wachtrij_spelers))
            
            if not wachtrij_spelers:
                print("ℹ️ Geen openstaande aanvragen gevonden op de pagina. De wachtrij is leeg!")
                return
                
            print(f"👀 {len(wachtrij_spelers)} aanvraag/aanvragen ontdekt: {', '.join(wachtrij_spelers)}")
            
            # Loop door alle gevonden spelers heen en accepteer ze automatisch!
            for username in wachtrij_spelers:
                print(f"⚙️ Automatisch verwerken van speler: {username}...")
                
                # 1. Update de Google Sheet (Geef 25 Shards)
                sheet_succes = update_spreadsheet_speler(username)
                
                if sheet_succes:
                    # 2. Accepteer de speler op Lichess via de actie die wél werkt
                    accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{username.lower()}/accept"
                    accept_response = requests.post(accept_url, headers=headers)
                    
                    if accept_response.status_code == 200:
                        print(f"✅ {username} is succesvol geaccepteerd en toegevoegd!")
                    else:
                        print(f"❌ Kon {username} niet accepteren op Lichess. Code: {accept_response.status_code}")
        else:
            print(f"❌ Kon de teampagina niet laden. Statuscode: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Er ging iets mis tijdens het scannen: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot (Pagina Scanner Modus) ---")
    check_and_accept_requests()
