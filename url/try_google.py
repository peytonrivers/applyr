import httpx
import os
from dotenv import load_dotenv

load_dotenv()
SERPER_KEY = os.getenv("SERPER_KEY")

queries = [
    "accountant jobs Raleigh NC",
    "staff accountant Charlotte NC",
    "accounts payable Durham NC",
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")

    resp = httpx.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_KEY,
            "Content-Type": "application/json",
        },
        json={"q": query, "num": 5},
        timeout=10,
    )

    for result in resp.json().get("organic", []):
        print(f"\n  Title:   {result.get('title')}")
        print(f"  Link:    {result.get('link')}")
        print(f"  Snippet: {result.get('snippet', '')[:80]}")