import requests
import re
import json
import os
import tempfile
from datetime import datetime, timezone
import socket
import struct
import ipaddress

def ip_to_int(ip):
    try:
        return struct.unpack("!L", socket.inet_aton(ip))[0]
    except:
        return 0

def is_valid_ip(ip_str):
    try:
        base_ip = ip_str.split('/')[0]
        ipaddress.ip_address(base_ip)
        return True
    except ValueError:
        return False

def scrape_and_update():
    urls = [
        "https://udger.com/resources/ua-list/bot-detail?bot=ByteDance+crawler",
        "https://ipinfo.io/AS138699",
        "https://www.ip2location.com/as138699",
        "https://gist.githubusercontent.com/nimroozy/b60988b6592b4da8b8d6801473c49e36/raw"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    raw_entries = set()
    MAX_ENTRIES = 5000  # Safety limit to prevent memory exhaustion or malicious injections

    try:
        for url in urls:
            # FIX 1: Added timeout (10 seconds) to prevent hanging sessions
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Ensure the request was successful
            
            found = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b|(?:[a-fA-F0-9]{1,4}:){2,}[a-fA-F0-9:]+(?:/\d{1,3})?\b', response.text)
            
            for entry in found:
                if is_valid_ip(entry):
                    raw_entries.add(entry)
                
                # FIX 2: Security check on data quantity
                if len(raw_entries) > MAX_ENTRIES:
                    print("Warning: Maximum entry limit reached. Stopping scrape.")
                    break

        # Processing (Deduplication and Sorting)
        cidrs_v4 = {e for e in raw_entries if '/' in e and '.' in e}
        single_ips_v4 = {e for e in raw_entries if '/' not in e and '.' in e}
        ipv6_entries = {e for e in raw_entries if ':' in e}

        filtered_v4 = set()
        for ip in single_ips_v4:
            prefix_check = '.'.join(ip.split('.')[:3]) + '.0/24'
            if prefix_check not in cidrs_v4:
                filtered_v4.add(ip)

        v4_sorted = sorted(list(cidrs_v4) + list(filtered_v4), key=lambda x: ip_to_int(x.split('/')[0]))
        v6_sorted = sorted(list(ipv6_entries))

        prefixes = []
        for entry in v4_sorted:
            prefixes.append({"ipv4Prefix": entry if '/' in entry else f"{entry}/32"})
        for entry in v6_sorted:
            prefixes.append({"ipv6Prefix": entry if '/' in entry else f"{entry}/128"})

        # FIX 3: Replaced deprecated utcnow() with timezone-aware datetime
        output = {
            "creationTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000"),
            "prefixes": prefixes
        }

        # FIX 4: Safe writing using a Temporary File to prevent corruption
        file_path = 'bytedance_ips.json'
        temp_dir = os.path.dirname(os.path.abspath(file_path))
        with tempfile.NamedTemporaryFile('w', dir=temp_dir, delete=False) as tf:
            json.dump(output, tf, indent=4)
            temp_name = tf.name
        
        # Atomic rename: replaces the old file only if the write was successful
        os.replace(temp_name, file_path)

        print(f"Update successful! Generated {len(prefixes)} valid prefixes.")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
