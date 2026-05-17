import os
import requests
import re
from sheets_manager import update_spreadsheet_speler

TEAM_ID = "growing-chess-variants-masters"
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

def get_usernames_from_html(html_text):
    """
    Scant de HTML van de hoofdpagina op zoek naar join-verzoeken.
    Lichess gebruikt daar vaak links zoals: /team/id/request/username/accept
    of vermeldt de gebruikersnaam in de handmatige review sectie.
    """
    # We zoeken naar patronen waarin een gebruikersnaam gekoppeld is aan het team-verzoek
    pattern = rf"/team/{TEAM_ID}/request/([\w-]+)"
    found = re.findall(pattern, html_text)
    
    # Filter eventuele woorden zoals 'accept' of 'reject' eruit als die zijn meegeleverd
    cleaned_usernames = []
    for name in found:
        clean_name = name.replace("/accept", "").replace("/id", "").strip()
        if clean_name and clean_name not in ["accept", "reject", "dismiss"]:
            cleaned_usernames.append(clean_name)
            
    return list(set(cleaned_usernames))

def check_and_accept_requests():
    if not LICHESS_TOKEN:
        print("❌ Fout: LICHESS_TOKEN secret is niet ingesteld!")
        return

    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN.strip()}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # We laden nu de absolute hoofdpagina van het team (dit kan GEEN 404/403 worden!)
    main_team_url = f"https://lichess.org/team/{TEAM_ID}"
    
    try:
        print(f"🔄 Openbare teampagina scannen...")
        response = requests.get(main_team_url, headers=headers)
        
        if response.status_code == 200:
            # Haal de gebruikersnamen uit de pagina-broncode
            wachtrij_spelers = get_usernames_from_html(response.text)
            
            if not wachtrij_spelers:
                print("ℹ️ Geen actieve verzoeken herkend op de hoofdpagina. De wachtrij is leeg!")
                return
                
            print(f"👀 {len(wachtrij_spelers)} potentieel verzoek/verzoeken ontdekt: {', '.join(wachtrij_spelers)}")
            
            for username in wachtrij_spelers:
                print(f"⚙️ Automatisch verwerken van speler: {username}...")
                
                # 1. Update Google Sheet
                sheet_succes = update_spreadsheet_speler(username)
                
                if sheet_succes:
                    # 2. Accepteer op Lichess via de API-actie die we eerder succesvol hebben getest!
                    accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{username.lower()}/accept"
                    accept_response = requests.post(accept_url, headers=headers)
                    
                    if accept_response.status_code == 200:
                        print(f"✅ {username} succesvol toegevoegd via automatische paginascan!")
                    else:
                        print(f"❌ Kon {username} niet accepteren. Code: {accept_response.status_code}")
        else:
            print(f"❌ Kon de pagina niet laden. Statuscode: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Er ging iets mis tijdens het scannen: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot (Hoofdpagina Scanner) ---")
    check_and_accept_requests()
