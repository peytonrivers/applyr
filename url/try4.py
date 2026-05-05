import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERPER_KEY = os.getenv("SERPER_KEY")

AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
    "talent.com", "joblist.com", "builtin.com", "wellfound.com",
]

def is_aggregator(url: str) -> bool:
    url = url.lower()
    return any(domain in url for domain in AGGREGATORS)

def google_job_url(name: str):
    url = "https://google.serper.dev/search"

    payload = {
        "q": name,
        "num": 5
    }

    headers = {
        "X-API-KEY": SERPER_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()

    results = data.get("organic", [])

    print("\nFIRST 5 RESULTS:\n" + "-" * 40)
    for i, result in enumerate(results[:5], start=1):
        print(f"{i}. {result.get('title')}")
        print(f"   {result.get('link')}\n")

    if not results:
        return None

    first_link = results[0].get("link")
    if first_link and not is_aggregator(first_link):
        return first_link

    return None


print("\nSELECTED URL:")
print(google_job_url("Advance Auto Parts Software Engineer Jobs in Raleigh, NC"))