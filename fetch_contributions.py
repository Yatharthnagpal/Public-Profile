import os
import requests
import json
from datetime import datetime

# Configuration
USERNAME = "Yatharthnagpal"
START_DATE = "2022-01-01"
OUTPUT_DIR = "public"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "contributions.json")

def get_contributions(username, start_date, end_date):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    total_contributions = 0
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    
    # GraphQL can only fetch one year at a time
    for year in range(start_year, end_year + 1):
        from_date = f"{year}-01-01T00:00:00Z"
        if year == end_year:
            to_date = end_date + "T23:59:59Z"
        else:
            to_date = f"{year}-12-31T23:59:59Z"
            
        if year == start_year and start_date.startswith(str(start_year)):
            from_date = f"{start_date}T00:00:00Z"

        query = """
        query($username: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        """
        variables = {
            "username": username,
            "from": from_date,
            "to": to_date
        }

        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print(f"Error fetching data for {year}: {data['errors']}")
                continue
            total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            total_contributions += total
            print(f"Year {year} contributions: {total}")
        else:
            print(f"Request failed: {response.status_code}")
            print(response.text)
            
    return total_contributions

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    total = get_contributions(USERNAME, START_DATE, today)
    print(f"\nTotal contributions from {START_DATE} to {today}: {total}")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Format for Shields.io custom endpoint
    badge_data = {
        "schemaVersion": 1,
        "label": "Contributions (2022-Present)",
        "message": f"{total}",
        "color": "success"
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(badge_data, f, indent=2)
    print(f"Saved badge data to {OUTPUT_FILE}")
