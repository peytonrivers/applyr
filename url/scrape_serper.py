import requests
import os
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

# ── ATS domains we target directly with site: operator ───────────────────────
# Each search will be: "{job_type} {state}" site:greenhouse.io OR site:lever.co ...
# This returns direct application pages, zero aggregators.

ATS_DOMAINS = [
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "icims.com",
    "taleo.net",
    "smartrecruiters.com",
    "jobvite.com",
    "ashbyhq.com",
    "breezy.hr",
    "successfactors.com",
    "bamboohr.com",
    "workable.com",
    "recruitee.com",
    "careers.google.com",
    "careers.microsoft.com",
    "careers.amazon.com",
    "careers.apple.com",
    "careers.garmin.com",
    "careers.cisco.com",
    "careers.nutanix.com",
    "careers.netapp.com",
    "careers.hpe.com",
    "careers.l3harris.com",
    "careers.ibm.com",
    "jobs.advanceautoparts.com",
    "jobs.saic.com",
    "jobs.baesystems.com",
    "jobs.mercedes-benz.com",
]

# Build the site: query string once — reused for every search
SITE_QUERY = " OR ".join(f"site:{domain}" for domain in ATS_DOMAINS)


def _headers() -> dict:
    return {
        "X-API-KEY": os.getenv("SERPER_KEY"),
        "Content-Type": "application/json",
    }


def clean_url(url: str) -> str:
    """Strip UTM and tracking params."""
    tracking_params = [
        "utm_source", "utm_medium", "utm_campaign",
        "src", "source", "sourceType", "gh_src", "trk", "refId"
    ]
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    clean_params = {k: v for k, v in params.items() if k not in tracking_params}
    clean_query = urlencode({k: v[0] for k, v in clean_params.items()})
    return parsed._replace(query=clean_query).geturl()


def is_ats_url(url: str) -> bool:
    return any(domain in url for domain in ATS_DOMAINS)


def serper_ats_search(job_type: str, state: str, pages: int = 5) -> list[dict]:
    """
    Search Serper for direct ATS job postings using site: operators.
    Each page = 10 results. pages=5 → up to 50 direct ATS links.
    1 Serper credit per page.
    """
    query = f'"{job_type}" "{state}" {SITE_QUERY}'

    all_results = []

    for page_num in range(1, pages + 1):
        payload = {
            "q": query,
            "gl": "us",
            "hl": "en",
            "page": page_num,
            "num": 10,
        }

        try:
            response = requests.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=_headers(),
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.HTTPError as e:
            print(f"  Page {page_num} HTTP error: {e}")
            break
        except Exception as e:
            print(f"  Page {page_num} error: {e}")
            break

        organic = data.get("organic", [])
        if not organic:
            print(f"  Page {page_num}: no results, stopping.")
            break

        # Filter to only actual ATS URLs (sanity check)
        ats_hits = [r for r in organic if is_ats_url(r.get("link", ""))]
        non_ats  = [r for r in organic if not is_ats_url(r.get("link", ""))]

        print(f"  Page {page_num}: {len(organic)} results → {len(ats_hits)} ATS, {len(non_ats)} filtered out")

        all_results.extend(ats_hits)

    return all_results


def format_jobs(raw_results: list[dict], job_type: str, state: str) -> list[dict]:
    """Convert Serper organic results into clean job dicts."""
    jobs = []
    seen_urls = set()

    for result in raw_results:
        url = clean_url(result.get("link", ""))
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        jobs.append({
            "title":        result.get("title", ""),
            "company_name": result.get("displayedLink", ""),
            "location":     state,
            "job_type":     job_type,
            "apply_url":    url,
            "snippet":      result.get("snippet", ""),
            "source":       "serper_ats",
        })

    return jobs


def print_summary(jobs: list[dict]):
    print(f"\n{'='*60}")
    print(f"Total direct ATS jobs found: {len(jobs)}")
    print(f"{'='*60}\n")

    for i, job in enumerate(jobs):
        print(f"[{i+1}] {job['title']}")
        print(f"     Company : {job['company_name']}")
        print(f"     URL     : {job['apply_url']}")
        print()

    print(f"{'='*60}")
    print(f"All {len(jobs)} URLs are direct ATS links — ready for Browser Use")
    print(f"{'='*60}")


if __name__ == "__main__":
    JOB_TYPE = "Software Engineer Intern"
    STATE    = "North Carolina"
    PAGES    = 5  # 5 credits = up to 50 results

    print(f"Searching Serper (ATS-targeted): '{JOB_TYPE}' in {STATE}...\n")
    raw = serper_ats_search(JOB_TYPE, STATE, pages=PAGES)
    jobs = format_jobs(raw, JOB_TYPE, STATE)
    print_summary(jobs)