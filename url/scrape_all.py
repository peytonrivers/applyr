import asyncio
import requests
from playwright.async_api import async_playwright
from urllib.parse import urlparse

# Signals that indicate a job is dead
DEAD_SIGNALS = [
    "job not found",
    "position not found",
    "no longer available",
    "position has been filled",
    "job expired",
    "no longer accepting",
    "posting has closed",
    "job has been removed",
    "this job has expired",
    "this position has been filled",
    "this posting has expired",
    "job listing has expired",
    "no longer accepting applications",
    "this job is closed",
    "this role has been filled",
    "this position is no longer",
    "application closed",
    "recruitment closed",
    "vacancy closed",
    "this opportunity has closed",
    "job is no longer available",
    "page not found",
    "404 not found",
    "job not available",
    "position closed",
]

# Signals that confirm a job is still open
LIVE_SIGNALS = [
    "apply now",
    "submit application",
    "apply for this job",
    "apply for this position",
    "apply for this role",
    "start application",
    "begin application",
    "apply today",
    "apply online",
    "submit your application",
    "apply here",
]

# URL endings that indicate a generic careers page, not a specific job
GENERIC_URL_ENDINGS = [
    "/careers",
    "/careers/",
    "/jobs",
    "/jobs/",
    "/internships",
    "/internships/",
    "/career-opportunities",
    "/career-opportunities/",
    "/work-with-us",
    "/work-with-us/",
    "/join-us",
    "/join-us/",
    "/job-search",
    "/openings",
    "/openings/",
    "/join-our-team",
    "/join-our-team/",
    "/about-royal/careers/internships",
    "/about-your-bank/work-with-us/careers/students.html",
]

# Content signals that indicate a generic listing page not a specific job
GENERIC_PAGE_SIGNALS = [
    "search jobs",
    "filter jobs",
    "all open positions",
    "browse jobs",
    "view all jobs",
    "see all openings",
    "explore careers",
    "find your next role",
    "job search results",
]


def is_generic_url(url: str) -> bool:
    """Check if URL looks like a generic careers homepage rather than a specific job."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()

    for ending in GENERIC_URL_ENDINGS:
        if path.endswith(ending.rstrip("/")):
            return True

    # Also flag if URL has no job-specific identifier
    # Specific jobs usually have IDs, slugs, or long paths
    if len(path.split("/")) <= 2 and not parsed.query:
        return True

    return False


async def check_url_quality(page, url: str) -> dict:
    """
    Check if a job URL is alive, specific, and still open.
    Returns a dict with:
        - is_active: bool
        - reason: str
    """

    # Step 0 — reject generic career homepages immediately
    if is_generic_url(url):
        return {
            "is_active": False,
            "reason": "Generic career page — not a specific job listing"
        }

    # Step 1 — quick HTTP check
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code in [404, 410, 403, 400]:
            return {
                "is_active": False,
                "reason": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "is_active": False,
            "reason": f"HTTP request failed: {str(e)}"
        }

    # Step 2 — Playwright deep check
    try:
        # Use domcontentloaded instead of networkidle to avoid timeouts on heavy pages
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Give JS a moment to render
        await page.wait_for_timeout(2000)
        content = (await page.content()).lower()

        # Check for dead signals
        for signal in DEAD_SIGNALS:
            if signal in content:
                return {
                    "is_active": False,
                    "reason": f"Dead signal found: '{signal}'"
                }

        # Check for generic page signals
        generic_count = sum(1 for signal in GENERIC_PAGE_SIGNALS if signal in content)
        if generic_count >= 2:
            return {
                "is_active": False,
                "reason": f"Generic listing page detected ({generic_count} generic signals)"
            }

        # Check for live signals
        has_live_signal = any(signal in content for signal in LIVE_SIGNALS)
        if has_live_signal:
            return {
                "is_active": True,
                "reason": "Live signal confirmed"
            }

        # No dead signals, no generic signals, no live signals
        # Could be a valid job page with unusual phrasing — mark active but note it
        return {
            "is_active": True,
            "reason": "No dead signals found (unconfirmed — manual review recommended)"
        }

    except Exception as e:
        error_msg = str(e)
        # PDF downloads or other non-HTML content
        if "download" in error_msg.lower():
            return {
                "is_active": False,
                "reason": "Non-HTML content (PDF or download)"
            }
        return {
            "is_active": False,
            "reason": f"Playwright failed: {error_msg[:100]}"
        }


async def run_checker(urls: list[str]):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"\nChecking {len(urls)} URLs...\n")
        print("=" * 70)

        results = []
        for i, url in enumerate(urls):
            print(f"[{i+1}] {url}")
            result = await check_url_quality(page, url)
            status = "✅ ACTIVE" if result["is_active"] else "❌ DEAD"
            print(f"     {status} — {result['reason']}")
            print()
            results.append({"url": url, **result})

        await browser.close()

        active = sum(1 for r in results if r["is_active"])
        print("=" * 70)
        print(f"\nSummary: {active}/{len(urls)} URLs are active")
        return results


if __name__ == "__main__":
    test_urls = [
        "https://jobinabuja.com/job_details.php?id=4933",
        "https://careers.marriott.com/marketing-university-intern-us/job/0BDF03C46E7508578B89DF7A7B0C6FD8",
        "https://henryschein.wd1.myworkdayjobs.com/external_careers/job/united-states---remote/summer-intern--product-marketing_r132871",
        "https://careers.smartrecruiters.com/AlphaIndustriesInc",
        "https://recruiting.paylocity.com/Recruiting/Jobs/Details/3979158",
        "https://simon.wd1.myworkdayjobs.com/en-US/Simon/job/Intern--Marketing_R13271",
        "https://jobs.techstars.com/companies/utopia-global-wellness-2/jobs/68924580-digital-marketing-coordinator-strategist-intern",
        "https://www.vfc.com/careers",
        "https://the-henry-ford.breezy.hr/p/ac8c59f83704-inhub-marketing-intern",
        "https://southwesternadvantage.com/internship-program/",
        "https://dowjones.wd1.myworkdayjobs.com/en-US/New_York_Post_Careers/job/Commerce-Social-Media-Marketing---Distribution-Intern_Job_Req_51870",
        "https://risepoint.wd503.myworkdayjobs.com/en-US/Risepoint/job/Marketing-Strategy---Operations-Intern_JR101173",
        "https://www.commvault.com/careers/jobs/5051667008",  # known dead
        "https://careers.ti.com/en/sites/CX/job/25009264/",
        "https://teamwork-ovg.icims.com/jobs/30306/creative-marketing-intern%2C-social-media-%26-digital-%7C-full-time-%7Cremote/job",
        "https://www.nyc.gov/assets/sbs/downloads/pdf/about/careers/love-your-local-intern.pdf",
        "https://careers-ebscoind.icims.com/jobs/1945/multimedia-marketing-intern/job",
        "https://mymvw.wd5.myworkdayjobs.com/en-US/MVW/job/Marriotts-Grand-Chateau/Direct-Marketing-Events-Internship---June---January-2026---Las-Vegas_JR88434",
        "https://nutrabolt.wd108.myworkdayjobs.com/en-US/Nutrabolt_Careers/job/Influencer-Marketing-Intern_R-100101",
        "https://www.columbiaforestproducts.com/internship",
        "https://job-boards.greenhouse.io/phoenixcontact/jobs/7617793003",
        "https://mymvw.wd5.myworkdayjobs.com/HVOCareers/job/Hyatt-Vacation-Club-at-The-Welk/Direct-Marketing-Operations-Internship---Summer-2026---Escondido--CA_JR88431-1",
        "https://choa.wd12.myworkdayjobs.com/en-US/externalcareers/job/Marketing-Intern_R-34245",
        "https://jobs.ashbyhq.com/omniscient/ae67eeb1-29f1-4a50-a12f-d81974cfaa98/application",
        "https://fenixpestcontrol.com/careers/",
        "https://jobs.disneycareers.com/job/celebration/travel-industry-marketing-intern-summer-fall-2026/391/91555137760",
        "https://job-boards.greenhouse.io/adcouncil/jobs/4003232005",
        "https://sidelineswap.breezy.hr/p/6ee51b5d6835-fall-sports-marketing-internship",
        "https://lego.wd103.myworkdayjobs.com/LEGO_External/job/Boston-Hub/Campaign-Marketing-Intern_0000032078/apply",
        "https://app.eddy.com/careers/axguard/1c8cff4e-0269-40b8-880f-e9377cb41aef/apply",
        "https://circle.wd1.myworkdayjobs.com/en-US/Circle/job/Marketing-Intern--Project-Management_JR100857",
        "https://app.eddy.com/careers/blitzmarketing/3ce13490-b4fe-4320-836c-70bcd55918ae",
        "https://apply.workable.com/j/1412715EB4",
        "https://jacksonhealthcare.wd1.myworkdayjobs.com/en-US/careers-jacksonhealthcare/job/Corporate-Marketing-Intern_JR107811",
        "https://psu.wd1.myworkdayjobs.com/en-US/psu_staff/job/Marketing-and-Fan-Experience-Interns_REQ_0000075685-2",
        "https://resmed.wd3.myworkdayjobs.com/en-US/ResMed_External_Careers/job/Digital-Marketing-Intern_JR_048099",
        "https://careers.aarp.org/careers-home/jobs/7215?lang=en-us",
        "https://razer.wd3.myworkdayjobs.com/en-US/Careers/job/Ecommerce-Marketing-Intern_JR2026006905",
        "https://recruiting.paylocity.com/recruiting/jobs/Details/3946783/GULF-COAST-BANK-TRUST/Intern---Marketing-Assistant",
        "https://4renu.breezy.hr/p/563e02e410ad-2023-sales-and-marketing-internship",
        "https://ozarkregionalveincenter.isolvedhire.com/",
        "https://ttmtech.wd5.myworkdayjobs.com/en-US/jobs/job/Marketing-Internship_R14182",
        "https://simon.wd1.myworkdayjobs.com/en-US/Simon/job/Intern--Marketing_R11943",
        "https://bannerhealth.wd108.myworkdayjobs.com/en-US/Careers/job/UNC-Undergraduate-Marketing-Internship_R4434692",
    ]

    asyncio.run(run_checker(test_urls))