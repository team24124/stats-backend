import requests

BASE = "http://localhost:5000"

if __name__ == '__main__':
    res = requests.get(f"{BASE}/api/teams/24124")
    data = res.json()
    for epa in data['historical_epa']:
        print(epa)