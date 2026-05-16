import os
import requests
import json

# CONFIGURATIE
# Het token wordt straks veilig uit de GitHub Instellingen gehaald
LICHESS_TOKEN = os.getenv("LICHESS_TOKEN")
TEAM_ID = "growing-chess-variants-masters"

HEADERS = {
    "Authorization": f"Bearer {LICHESS_TOKEN}",
    "Accept": "application/x-ndjson"
}

def accepteer_nieuwe_leden():
    if not LICHESS_TOKEN:
        print("❌ Fout: LICHESS_TOKEN is niet gevonden in de GitHub Instellingen!")
        return

    url = f"https://lichess.org/api/team/{TEAM_ID}/requests"
    print(f"Bot is online! Controleren op nieuwe aanvragen voor team: {TEAM_ID}...")
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        regels = response.text.strip().split('\n')
        
        if not regels or regels == ['']:
            print("Geen openstaande aanvragen gevonden. Alles is bijgewerkt!")
            return

        for regel in regels:
            if not regel.strip():
                continue
                
            aanvraag = json.loads(regel)
            user_id = aanvraag.get("user", {}).get("id")
            username = aanvraag.get("user", {}).get("name")
            
            if user_id:
                print(f"Nieuw lid ontdekt: {username}. Automatisch toelaten...")
                
                accept_url = f"https://lichess.org/api/team/{TEAM_ID}/request/{user_id}/accept"
                accept_response = requests.post(accept_url, headers=HEADERS)
                
                if accept_response.status_code == 200:
                    print(f"🥳 Succes! {username} is nu automatisch toegelaten tot het team.")
                else:
                    print(f"❌ Kon {username} niet toevoegen. Statuscode: {accept_response.status_code}")
    else:
        print(f"❌ Lichess weigert de verbinding. Statuscode: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("--- Lichess Systeem Account Gestart ---")
    accepteer_nieuwe_leden()
