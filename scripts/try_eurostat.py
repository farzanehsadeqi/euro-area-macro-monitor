"""Find the valid geo codes for une_rt_m."""

import requests

url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m"

# No geo filter at all, so we see every available area
params = {
    "format": "JSON",
    "lang": "EN",
    "s_adj": "SA",
    "age": "TOTAL",
    "sex": "T",
    "unit": "PC_ACT",
    "lastTimePeriod": 1,
}

response = requests.get(url, params=params, timeout=30)
data = response.json()

geo = data["dimension"]["geo"]["category"]
print("Number of areas:", len(geo["index"]))
print()

for code, label in geo["label"].items():
    print(f"{code}: {label}")