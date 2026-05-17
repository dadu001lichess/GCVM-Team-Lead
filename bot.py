import os
import requests
import re
from sheets_manager import update_spreadsheet_speler

TEAM_ID = "growing-chess-variants-masters"
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")

def get_usernames_from_html(html_text):
    """
    Scant de HTML van de centrale Lichess verzoekenpagina.
    Zoekt naar het specifieke patroon: /team/team_id/request/username@team_id
    """
    # Dit patroon zoekt exact naar wat we in de devtools zagen, specifiek voor jouw team
    pattern = rf"/team/{TEAM_ID}/request/([\w-]+)@{TEAM_ID}"
    found = re.findall(pattern, html_text)
    
    # Val terug op een bredere check mocht de structuur iets afwijken
    pattern_fallback = rf"/team/{TEAM_ID}/request/([\w-]+)"
    found_fallback = re.findall(pattern_fallback, html_text)
    
    alle_vondsten = found + found_fallback
    cleaned = []
    
    for name in alle_vondsten:
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
    
    # We sturen de bot nu RECHTSTREEKS naar de pagina uit je screenshot!
    requests_url = "https://lichess.org/team/requests"
    
    try:
        print(f"🔄 Centrale verzoekenpagina ({requests_url}) scannen...")
        response = requests.get(requests_url, headers=headers)
        
        if response.status_code == 200:
            wachtrij_spelers = get_usernames_from_html(response.text)
            
            if not wachtrij_spelers:
                print("ℹ️ Geen actieve verzoeken voor jouw team gevonden op deze pagina. De wachtrij is leeg!")
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
            print(f"❌ Kon de verzoekenpagina niet laden. Statuscode: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Er ging iets mis tijdens het scannen: {e}")

if __name__ == "__main__":
    print("--- Lichess Systeem Bot (Centrale Dashboard Scanner) ---")
    check_and_accept_requests()
