# Author: Sakthi Santhosh
# Created on: 12/11/2023
#
# Cloudflare DNS A Record Updater for EC2 (https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record)
from datetime import datetime
from dotenv import load_dotenv
from json import dumps
from os import getenv, mkdir, path
from requests import get, put
from time import sleep

def get_instance_public_ipv4() -> None:
    try:
        response = get("https://api.ipify.org?format=json")
        return response.json()["ip"]
    except Exception:
        print("Fatal: Failed to retreive public IPv4 address of this instance.")
        exit(1)

def update_dns_record(public_ipv4: str) -> None:
    load_dotenv("./assets/.env")

    ZONE_IDENTIFIER = getenv("CLOUDFLARE_ZONE_IDENTIFIER")
    IDENTIFIER = getenv("CLOUDFLARE_RECORD_IDENTIFIER")
    ACCESS_TOKEN = getenv("CLOUDFLARE_ACCESS_TOKEN")

    URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_IDENTIFIER}/dns_records/{IDENTIFIER}"
    HEADERS = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    PAYLOAD = {
        "content": public_ipv4,
        "name": "vpn.sakthisanthosh.in",
        "type": 'A',
        "proxied": False,
        "ttl": 1 # Automatic
    }

    with put(url=URL, headers=HEADERS, data=dumps(PAYLOAD)) as response:
        print("Status:", response.status_code)
        print("Response:", response.text)

def main() -> None:
    print(f"Info: Script started at \"{datetime.now()}\".")
    update_dns_record(public_ipv4=get_instance_public_ipv4())

if __name__ == "__main__":
    sleep(10)
    main()
