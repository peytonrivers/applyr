import csv
from jobspy import scrape_jobs

# ─── Config ────────────────────────────────────────────────────────────────────

QUERIES = [
    "entry marketing",
    "entry accountant",
]

LOCATION = "North Carolina"
RESULTS_PER_QUERY = 20

# ─── Main ──────────────────────────────────────────────────────────────────────

all_results = []

for query in QUERIES:
    print(f"\n{'=' * 60}")
    print(f"  Searching: {query} in {LOCATION}")
    print(f"{'=' * 60}")

    jobs = scrape_jobs(
        site_name=["linkedin", "indeed", "zip_recruiter", "google"],
        search_term=query,
        location=LOCATION,
        results_wanted=RESULTS_PER_QUERY,
        hours_old=72,  # last 3 days
        country_indeed="USA",
    )

    found = 0
    for _, job in jobs.iterrows():
        # prefer direct apply URL, fall back to job listing URL
        apply_url = job.get("job_url_direct") or job.get("job_url")

        if not apply_url:
            continue

        result = {
            "title":      job.get("title", ""),
            "company":    job.get("company", ""),
            "location":   job.get("location", ""),
            "salary_min": job.get("min_amount", ""),
            "salary_max": job.get("max_amount", ""),
            "source":     job.get("site", ""),
            "job_url":    job.get("job_url", ""),
            "apply_url":  apply_url,
        }

        all_results.append(result)
        found += 1

        print(f"\n  [{found}] {result['title']} @ {result['company']}")
        print(f"       Location : {result['location']}")
        print(f"       Source   : {result['source']}")
        if result['salary_min']:
            print(f"       Salary   : ${result['salary_min']:,} - ${result['salary_max']:,}")
        print(f"       Apply URL: {result['apply_url']}")

    print(f"\n  Found {found} jobs for '{query}'")

# ─── Summary ───────────────────────────────────────────────────────────────────

print(f"\n{'=' * 60}")
print(f"  Total jobs found: {len(all_results)}")
print(f"{'=' * 60}\n")
for r in all_results:
    print(f"  {r['title']} @ {r['company']} → {r['apply_url']}")