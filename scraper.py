import requests
import re
import json
from datetime import datetime

def scrape_and_update():
    # Target URLs: Udger for known bots and IPInfo for the AS138699 (ByteDance)
    urls = [
        "https://udger.com/resources/ua-list/bot-detail?bot=ByteDance+crawler",
        "https://ipinfo.io/AS138699"
    ]
    
    # Header to simulate a real browser request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    all_entries = set()

    try:
        for url in urls:
            # Send HTTP request to the source
            response = requests.get(url, headers=headers)
            # Regex to find both single IP addresses and CIDR ranges (e.g., 1.2.3.4 or 1.2.3.4/24)
            found = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b', response.text)
            # Update the set with found entries to ensure uniqueness
            all_entries.update(found)

        # Sort the list alphabetically/numerically for a clean output
        final_list = sorted(list(all_entries))

        # Build the final dictionary following the requested structure
        output = {
            "bot_name": "ByteDance crawler",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(final_list),
            "ip_ranges_and_addresses": final_list
        }

        # Save the data into a JSON file
        with open('bytedance_ips.json', 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Update successful! Found {len(final_list)} entries.")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
