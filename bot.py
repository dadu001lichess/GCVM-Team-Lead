import os
import requests
import re
from sheets_manager import update_spreadsheet_speler

TEAM_ID = "growing-chess-variants-masters"
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

def get_usernames_from_html(html_text):
    """
    Scant de HTML op basis van de exacte Lichess structuur uit de screenshot:
    /team/team-id/request/username@team-id
    """
    # Dit patroon zoekt specifiek naar de tekst tussen /request/ en het @-teken
    pattern = rf"/team/{TEAM_ID}/request/([\w-]+)@{TEAM_ID}"
    found = re.findall(pattern, html_text)
    
    # Mocht Lichess toch ergens de oude url gebruiken, checken we die ook direct mee
    pattern_fallback = rf"/team/{TEAM_ID}/request/([\w-]+)"
    found_fallback = re.findall(pattern_fallback, html_text)
    
    alle_vondsten = found + found_fallback
    cleaned = []
    
    for name in alle_vondsten:
        # Haal eventuele resterende tags of actiewoorden weg
        name_clean = name.replace("/accept", "").replace("/reject", "").strip()
        if name_clean and name_clean.lower() not in ["accept", "reject", "dismiss", "id"]:
            cleaned.append(name_clean)
            
    return list(set(cleaned))

def check_and_accept_requests():
    if not LICHESS_TOKEN:
        print("❌ Fout: LICHESS_TOKEN secret is niet ingesteld!")
        return

    headers = {
        "Authorization": f"Bearer {LICHESS_TOKEN.strip()}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    main_team_url = f"https://lichess.org/team/{TEAM_ID}"
    
    try:
        print(f"🔄 Openbare teampagina scannen...")
        response = requests.get(main_team_url, headers=headers)
        
        if response.status_code == 200:
            wachtrij_spelers = get_usernames_from_html(response.text)
            
            if not wachtrij_spelers:
                print("ℹ️ Geen actieve verzoeken herkend op de hoofdpagina. De wachtrij is leeg!")
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
                        print(f"✅ {username} succesvol toegevoegd!")
                    else:
                        print(f"❌ Kon {username} niet accepteren. Code: {accept_response.status_code}")
        else:
            print(f"❌ Kon de pagina niet laden. Statuscode: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Er ging iets mis tijdens het scannen: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot (Screenshot-Gekalibreerde Scanner) ---")
    check_and_accept_requests()
