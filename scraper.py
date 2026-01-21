import requests
import re
import json
from datetime import datetime

def scrape_and_update():
    # URL delle due fonti
    url_udger = "https://udger.com/resources/ua-list/bot-detail?bot=ByteDance+crawler"
    url_ipinfo = "https://ipinfo.io/AS138699"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    all_ips = set()

    try:
        # 1. Recupero da Udger
        res_udger = requests.get(url_udger, headers=headers)
        ips_udger = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', res_udger.text)
        all_ips.update(ips_udger)

        # 2. Recupero da IPInfo (AS138699 - ByteDance)
        res_ipinfo = requests.get(url_ipinfo, headers=headers)
        ips_ipinfo = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', res_ipinfo.text)
        all_ips.update(ips_ipinfo)

        # Pulizia e ordinamento
        final_list = sorted(list(all_ips))

        output = {
            "bot_name": "ByteDance crawler",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(final_list),
            "ip_addresses": final_list
        }

        with open('bytedance_ips.json', 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Successo! Totale IP trovati dalle due fonti: {len(final_list)}")
        
    except Exception as e:
        print(f"Errore: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
