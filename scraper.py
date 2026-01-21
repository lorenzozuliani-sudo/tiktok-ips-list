import requests
import re
import json
from datetime import datetime

def scrape_and_update():
    # URL che contiene la lista degli IP dei bot ByteDance
    url = "https://udger.com/resources/ua-list/bot-detail?bot=ByteDance+crawler"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(url, headers=headers)
        # Regex per trovare tutti i numeri in formato IP (es. 110.249.201.104)
        ips = sorted(list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', response.text))))

        # Struttura dati richiesta
        output = {
            "bot_name": "ByteDance crawler",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(ips),
            "ip_addresses": ips
        }

        # Crea il file JSON nel tuo repository
        with open('bytedance_ips.json', 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Aggiornamento completato: {len(ips)} IP salvati.")
    except Exception as e:
        print(f"Errore: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
