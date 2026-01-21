import requests
import re
import json
from datetime import datetime
import socket
import struct
import ipaddress

def ip_to_int(ip):
    """Helper to convert IPv4 string to integer for proper numerical sorting."""
    try:
        return struct.unpack("!L", socket.inet_aton(ip))[0]
    except:
        return 0

def is_valid_ip(ip_str):
    """Checks if a string is a valid IPv4 or IPv6 address or network."""
    try:
        # Removes CIDR mask for validation if present
        base_ip = ip_str.split('/')[0]
        ipaddress.ip_address(base_ip)
        return True
    except ValueError:
        return False

def scrape_and_update():
    # Target sources
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
            # Improved Regex: avoids catching simple timestamps like 21:05:45
            # Requires at least two colons for IPv6 candidates
            found = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b|(?:[a-fA-F0-9]{1,4}:){2,}[a-fA-F0-9:]+(?:/\d{1,3})?\b', response.text)
            
            # Strict validation: keep only real IP addresses
            for entry in found:
                if is_valid_ip(entry):
                    raw_entries.add(entry)

        # Separate IPv4 and IPv6
        cidrs_v4 = {e for e in raw_entries if '/' in e and '.' in e}
        single_ips_v4 = {e for e in raw_entries if '/' not in e and '.' in e}
        ipv6_entries = {e for e in raw_entries if ':' in e}

        # Remove redundant single IPv4s covered by /24 CIDRs
        filtered_v4 = set()
        for ip in single_ips_v4:
            prefix_check = '.'.join(ip.split('.')[:3]) + '.0/24'
            if prefix_check not in cidrs_v4:
                filtered_v4.add(ip)

        # Numerical sort for IPv4
        v4_sorted = sorted(list(cidrs_v4) + list(filtered_v4), key=lambda x: ip_to_int(x.split('/')[0]))
        # Alphabetical sort for IPv6
        v6_sorted = sorted(list(ipv6_entries))

        # Build prefixes list in Google format
        prefixes = []
        for entry in v4_sorted:
            prefixes.append({"ipv4Prefix": entry if '/' in entry else f"{entry}/32"})
        for entry in v6_sorted:
            prefixes.append({"ipv6Prefix": entry if '/' in entry else f"{entry}/128"})

        output = {
            "creationTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000000"),
            "prefixes": prefixes
        }

        with open('bytedance_ips.json', 'w') as f:
            json.dump(output, f, indent=4)

        print(f"Update successful! Generated {len(prefixes)} valid prefixes.")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_and_update()
