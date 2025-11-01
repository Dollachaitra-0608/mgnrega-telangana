import requests
import json
import os

API_URL = "https://api.data.gov.in/resource/ee03643a-ee4c-48c2-ac30-9f2ff26ab722"
API_KEY = "579b464db66ec23bdd000001a5153959870449c641b1035ab68e4289"
LIMIT = 1000

os.makedirs("data", exist_ok=True)

def fetch_data():
    all_data = []
    offset = 0
    while True:
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": LIMIT,
            "offset": offset,
            "filters[state_name]": "TELANGANA"
        }
        print(f"Fetching offset {offset}...")
        r = requests.get(API_URL, params=params)
        data = r.json()

        if "records" not in data or len(data["records"]) == 0:
            break

        all_data.extend(data["records"])
        offset += LIMIT

    with open("data/mgnrega_data.json", "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"✅ Saved {len(all_data)} records to data/mgnrega_data.json")

if __name__ == "__main__":
    fetch_data()
