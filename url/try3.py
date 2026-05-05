import httpx

SERPER_KEY = __import__('os').getenv("SERPER_KEY")

# Load .env
from dotenv import load_dotenv
load_dotenv()
SERPER_KEY = __import__('os').getenv("SERPER_KEY")

ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "myworkdayjobs.com",
    "ashbyhq.com", "smartrecruiters.com", "jobvite.com", "icims.com",
    "taleo.net", "successfactors.com", "applytojob.com", "bamboohr.com",
    "paylocity.com", "breezy.hr", "avature.net", "recruitingbypaycor.com",
    "ultipro.com", "oraclecloud.com", "workable.com", "recruitee.com",
    "pinpointhq.com", "dover.com", "careerplug.com", "jazz.co",
    "rippling.com", "kronos.net", "adp.com", "ceridian.com",
    "silkroad.com", "cornerstone", "sap.com",
]


AGGREGATORS = [
    "indeed.com", "linkedin.com", "ziprecruiter.com", "glassdoor.com",
    "simplyhired.com", "monster.com", "careerbuilder.com", "lensa.com",
]

GENERIC_URL_ENDINGS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/internships",
    "/internships/", "/career-opportunities", "/career-opportunities/",
    "/work-with-us", "/work-with-us/", "/join-us", "/join-us/",
    "/job-search", "/openings", "/openings/", "/join-our-team",
    "/join-our-team/", "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
]

TEST_JOBS = [
    ("Controller (CPA or CMA Required)", "AutoTech Solutions"),
    ("Controller, Member Firm", "Crete Professionals Alliance"),
    ("Bus Operations Controller", "Y2Marketing"),
]


def is_aggregator(url): return any(a in url for a in AGGREGATORS)
def is_ats_url(url): return any(d in url for d in ATS_DOMAINS)
def is_generic_url(url):
    from urllib.parse import urlparse
    path = urlparse(url).path.rstrip("/").lower()
    return any(path.endswith(e.rstrip("/")) for e in GENERIC_URL_ENDINGS)

def company_matches_url(company, url):
    if not company or company.lower() == "nan":
        return True
    noise = [" inc"," llc"," ltd"," corp"," co."," group"," services"," solutions"," consulting"," partners"," associates"," company"," &"," and"]
    c = company.lower()
    for n in noise: c = c.replace(n, "")
    words = [w.strip(".,()-") for w in c.split() if len(w.strip(".,()-")) >= 3]
    if not words: return True
    return words[0] in url.lower()


def serper_find(title, company):
    query = f"{title} {company} apply"
    print(f"  Query: {query}")

    resp = httpx.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
        json={"q": query, "num": 10},
        timeout=10,
    )

    results = resp.json().get("organic", [])
    print(f"  Results: {len(results)}")

    for r in results:
        link = r.get("link", "")
        agg = is_aggregator(link)
        ats = is_ats_url(link)
        generic = is_generic_url(link)
        matches = company_matches_url(company, link)
        status = "✓ MATCH" if (not agg and ats and not generic and matches) else "✗"
        print(f"  {status} | agg={agg} ats={ats} generic={generic} match={matches}")
        print(f"         {link}")

    # Return first valid
    for r in results:
        link = r.get("link", "")
        if not is_aggregator(link) and is_ats_url(link) and not is_generic_url(link) and company_matches_url(company, link):
            return link
    return None


for title, company in TEST_JOBS:
    print(f"\n{'='*60}")
    print(f"JOB: {title} @ {company}")
    result = serper_find(title, company)
    print(f"RESULT: {result}")