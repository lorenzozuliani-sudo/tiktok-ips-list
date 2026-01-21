import requests
import re
import json
from datetime import datetime

def scrape_and_update():
    # URL delle fonti (Udger e IPInfo per AS138699)
    urls = [
        "https://udger.com/resources/ua-list/bot-detail?bot=ByteDance+crawler",
        "https://ipinfo.io/AS138699"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    all_entries = set()

    try:
        for url in urls:
            response = requests.get(url, headers=headers)
            # Regex migliorata: cerca IP singoli (1.2.3.4) E range CIDR (1.2.3.4/24)
            found = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b', response.text)
            all_entries.update(found)

        # Pulizia e ordinamento
        final_list = sorted(list(all_entries))

        output = {
            "bot_name": "ByteDance crawler", #
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), #
            "total": len(final_list), #
            "ip_ranges_and_addresses": final_list #
        }

        with open('bytedance_ips.json', 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Aggiornamento completato! Trovati {len(final_list)} elementi tra IP e Range.")
        
    except Exception as e:
        print(f"Errore: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
