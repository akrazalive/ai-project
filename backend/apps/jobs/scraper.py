import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

LAST_24H = "r86400"

GULF_COUNTRIES = {
    "UAE":          {"geoId": "104305776", "label": "UAE",          "flag": "🇦🇪"},
    "Saudi Arabia": {"geoId": "101004954", "label": "Saudi Arabia", "flag": "🇸🇦"},
    "Qatar":        {"geoId": "104514075", "label": "Qatar",        "flag": "🇶🇦"},
    "Kuwait":       {"geoId": "104514075", "label": "Kuwait",       "flag": "🇰🇼"},
    "Bahrain":      {"geoId": "100016538", "label": "Bahrain",      "flag": "🇧🇭"},
    "Oman":         {"geoId": "102098694", "label": "Oman",         "flag": "🇴🇲"},
}

ALL_COUNTRIES = {
    **GULF_COUNTRIES,
    "United States":  {"geoId": "103644278", "label": "United States",  "flag": "🇺🇸"},
    "United Kingdom": {"geoId": "101165590", "label": "United Kingdom",  "flag": "🇬🇧"},
    "Canada":         {"geoId": "101174742", "label": "Canada",          "flag": "🇨🇦"},
    "Australia":      {"geoId": "101452733", "label": "Australia",       "flag": "🇦🇺"},
    "Germany":        {"geoId": "101282230", "label": "Germany",         "flag": "🇩🇪"},
    "India":          {"geoId": "102713980", "label": "India",           "flag": "🇮🇳"},
    "Pakistan":       {"geoId": "100554890", "label": "Pakistan",        "flag": "🇵🇰"},
    "Netherlands":    {"geoId": "102890719", "label": "Netherlands",     "flag": "🇳🇱"},
    "France":         {"geoId": "105015875", "label": "France",          "flag": "🇫🇷"},
    "Singapore":      {"geoId": "102454443", "label": "Singapore",       "flag": "🇸🇬"},
    "Remote":         {"geoId": "",          "label": "Worldwide",       "flag": "🌍"},
}

COUNTRY_KEYWORDS = {k: [] for k in ALL_COUNTRIES}

# Gulf flags lookup for non-LinkedIn scrapers
GULF_FLAGS = {meta["label"]: meta["flag"] for meta in GULF_COUNTRIES.values()}
GULF_FLAGS["Gulf"] = "🌍"


def time_ago(iso_datetime: str) -> str:
    if not iso_datetime:
        return ""
    try:
        posted = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = int((now - posted).total_seconds())
        if diff < 60:    return f"{diff}s ago"
        if diff < 3600:  return f"{diff // 60}m ago"
        if diff < 86400: return f"{diff // 3600}h ago"
        return f"{diff // 86400}d ago"
    except Exception:
        return iso_datetime


# ─── LinkedIn ────────────────────────────────────────────────────────────────

def scrape_linkedin(role: str, geo_id: str = "", location_label: str = "",
                    flag: str = "🌐", remote: bool = False) -> list[dict]:
    params = {
        "keywords": role, "f_TPR": LAST_24H,
        "position": 1, "pageNum": 0, "sortBy": "DD",
    }
    if remote:
        params["f_WT"] = "2"
        params["location"] = "Worldwide"
    else:
        params["location"] = location_label
        if geo_id:
            params["geoId"] = geo_id

    url = "https://www.linkedin.com/jobs/search?" + urllib.parse.urlencode(params)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for card in soup.select("div.base-card, li.jobs-search__results-list > div"):
        title_el    = card.select_one("h3.base-search-card__title, h3")
        company_el  = card.select_one("h4.base-search-card__subtitle, h4")
        location_el = card.select_one("span.job-search-card__location")
        link_el     = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
        time_el     = card.select_one("time")
        applicants_el = card.select_one("span.job-search-card__applicant-count, span[class*='applicant']")
        easy_el     = card.select_one("span[class*='easy-apply'], span.base-search-card__benefits")

        title    = title_el.get_text(strip=True)    if title_el    else ""
        company  = company_el.get_text(strip=True)  if company_el  else ""
        location = location_el.get_text(strip=True) if location_el else location_label
        link     = link_el.get("href", "").split("?")[0] if link_el else ""
        posted   = time_el.get("datetime", "")      if time_el     else ""
        applicants = applicants_el.get_text(strip=True) if applicants_el else ""
        easy_apply = bool(easy_el and "easy" in easy_el.get_text(strip=True).lower())

        if not title or not link:
            continue
        jobs.append({
            "title": title, "company": company, "location": location,
            "flag": flag, "url": link, "posted_at": posted,
            "posted_ago": time_ago(posted), "applicants": applicants,
            "easy_apply": easy_apply, "source": "LinkedIn",
        })
    return jobs


# ─── NaukriGulf ──────────────────────────────────────────────────────────────

def scrape_naukrigulf(role: str) -> list[dict]:
    query = urllib.parse.quote_plus(role)
    url = f"https://www.naukrigulf.com/{query.replace('+','-')}-jobs"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for card in soup.select("div.jobsearch-SerpJobCard, article.job-card, div[class*='job-listing'], li[class*='job']"):
        title_el   = card.select_one("a.job-title, h3 a, h2 a, a[class*='title']")
        company_el = card.select_one("span.company-name, div[class*='company'], span[class*='company']")
        loc_el     = card.select_one("span.location, span[class*='location'], li[class*='location']")
        time_el    = card.select_one("span[class*='date'], span[class*='time'], li[class*='date']")

        title   = title_el.get_text(strip=True)   if title_el   else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = loc_el.get_text(strip=True)    if loc_el     else "Gulf"
        posted  = time_el.get_text(strip=True)    if time_el    else ""
        link    = title_el.get("href", "")        if title_el   else ""
        if link and not link.startswith("http"):
            link = "https://www.naukrigulf.com" + link

        if not title or not link:
            continue

        flag = next((GULF_FLAGS[k] for k in GULF_FLAGS if k.lower() in location.lower()), "🌍")
        jobs.append({
            "title": title, "company": company, "location": location,
            "flag": flag, "url": link, "posted_at": "",
            "posted_ago": posted, "applicants": "",
            "easy_apply": False, "source": "NaukriGulf",
        })
    return jobs


# ─── Bayt.com ────────────────────────────────────────────────────────────────

def scrape_bayt(role: str) -> list[dict]:
    query = urllib.parse.quote_plus(role)
    url = f"https://www.bayt.com/en/international/jobs/{query.replace('+','-')}-jobs/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for card in soup.select("li[class*='has-pointer-d'], div[class*='media-list-item']"):
        title_el   = card.select_one("h2 a, h3 a, a[class*='job-name']")
        company_el = card.select_one("b[class*='t-default'], span[class*='company']")
        loc_el     = card.select_one("span[class*='location'], li[class*='location']")
        time_el    = card.select_one("span[class*='date'], abbr[class*='timeago']")

        title    = title_el.get_text(strip=True)   if title_el   else ""
        company  = company_el.get_text(strip=True) if company_el else ""
        location = loc_el.get_text(strip=True)     if loc_el     else "Gulf"
        posted   = time_el.get_text(strip=True)    if time_el    else ""
        link     = title_el.get("href", "")        if title_el   else ""
        if link and not link.startswith("http"):
            link = "https://www.bayt.com" + link

        if not title or not link:
            continue

        flag = next((GULF_FLAGS[k] for k in GULF_FLAGS if k.lower() in location.lower()), "🌍")
        jobs.append({
            "title": title, "company": company, "location": location,
            "flag": flag, "url": link, "posted_at": "",
            "posted_ago": posted, "applicants": "",
            "easy_apply": False, "source": "Bayt",
        })
    return jobs


# ─── Indeed ──────────────────────────────────────────────────────────────────

def scrape_indeed(role: str, location: str = "Gulf", flag: str = "🌍") -> list[dict]:
    params = {"q": role, "l": location, "fromage": "1", "sort": "date"}
    url = "https://www.indeed.com/jobs?" + urllib.parse.urlencode(params)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for card in soup.select("div.job_seen_beacon, div[class*='cardOutline'], td.resultContent"):
        title_el   = card.select_one("h2.jobTitle a, a[id*='job_'], span[title]")
        company_el = card.select_one("span.companyName, span[data-testid='company-name']")
        loc_el     = card.select_one("div.companyLocation, div[data-testid='text-location']")
        time_el    = card.select_one("span.date, span[data-testid='myJobsStateDate']")

        title    = title_el.get_text(strip=True)   if title_el   else ""
        company  = company_el.get_text(strip=True) if company_el else ""
        location_str = loc_el.get_text(strip=True) if loc_el     else location
        posted   = time_el.get_text(strip=True)    if time_el    else ""
        href     = title_el.get("href", "")        if title_el   else ""
        link     = ("https://www.indeed.com" + href) if href and not href.startswith("http") else href

        if not title or not link:
            continue
        jobs.append({
            "title": title, "company": company, "location": location_str,
            "flag": flag, "url": link, "posted_at": "",
            "posted_ago": posted, "applicants": "",
            "easy_apply": False, "source": "Indeed",
        })
    return jobs


# ─── Main entry ──────────────────────────────────────────────────────────────

def search_jobs(role: str, countries: list[str]) -> dict:
    all_jobs = []
    seen_urls = set()

    def add(jobs, region):
        for job in jobs:
            if job["url"] and job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                job["search_region"] = region
                all_jobs.append(job)

    # LinkedIn — Gulf countries
    for name, meta in GULF_COUNTRIES.items():
        add(scrape_linkedin(role, geo_id=meta["geoId"],
                            location_label=meta["label"], flag=meta["flag"]),
            f"Gulf – {name}")

    # LinkedIn — Worldwide remote
    add(scrape_linkedin(role, remote=True, flag="🌍"), "Worldwide Remote")

    # LinkedIn — extra countries
    for country in countries:
        if country in GULF_COUNTRIES:
            continue
        meta = ALL_COUNTRIES.get(country)
        if meta:
            add(scrape_linkedin(role, geo_id=meta["geoId"],
                                location_label=meta["label"], flag=meta["flag"]),
                country)

    # NaukriGulf
    add(scrape_naukrigulf(role), "NaukriGulf")

    # Bayt
    add(scrape_bayt(role), "Bayt")

    # Indeed — UAE + Remote
    add(scrape_indeed(role, "United Arab Emirates", "🇦🇪"), "Indeed – UAE")
    add(scrape_indeed(role, "Remote", "🌍"), "Indeed – Remote")

    query = f'"{role}" — LinkedIn + NaukriGulf + Bayt + Indeed — last 24 hrs'
    return {"query": query, "results": all_jobs}
