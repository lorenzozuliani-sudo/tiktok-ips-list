import requests
import re
import json
from datetime import datetime
import socket
import struct

def ip_to_int(ip):
    # Helper to convert IP string to integer for proper numerical sorting
    return struct.unpack("!L", socket.inet_aton(ip))[0]

def scrape_and_update():
    # All sources including the new ones provided by your colleague
    urls = [
        "https://udger.com/resources/ua-list/bot-detail?bot=ByteDance+crawler",
        "https://ipinfo.io/AS138699",
        "https://www.ip2location.com/as138699",
        "https://gist.githubusercontent.com/nimroozy/b60988b6592b4da8b8d6801473c49e36/raw"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    raw_entries = set()

    try:
        for url in urls:
            response = requests.get(url, headers=headers)
            # Find both single IPs and CIDR ranges
            found = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b', response.text)
            raw_entries.update(found)

        # Separate CIDRs from single IPs to handle redundancy
        cidrs = {e for e in raw_entries if '/' in e}
        single_ips = {e for e in raw_entries if '/' not in e}

        # Remove single IPs that are already covered by a /24 range in the list
        filtered_ips = set()
        for ip in single_ips:
            # Check if the first three octets + /24 exists in our cidr set
            prefix = '.'.join(ip.split('.')[:3]) + '.0/24'
            if prefix not in cidrs:
                filtered_ips.add(ip)

        # Combine and sort numerically
        # We sort by the IP part (excluding the /mask) using the ip_to_int helper
        combined = list(cidrs) + list(filtered_ips)
        final_list = sorted(combined, key=lambda x: ip_to_int(x.split('/')[0]))

        output = {
            "bot_name": "ByteDance crawler",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(final_list),
            "ip_ranges_and_addresses": final_list
        }

        with open('bytedance_ips.json', 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Update successful! Total unique entries: {len(final_list)}")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
