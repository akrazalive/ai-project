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


def time_ago(iso_datetime: str) -> str:
    """Convert ISO datetime string to '2 hrs ago', '45 mins ago' etc."""
    if not iso_datetime:
        return ""
    try:
        posted = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - posted
        total_seconds = int(diff.total_seconds())
        if total_seconds < 60:
            return f"{total_seconds}s ago"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}m ago"
        elif total_seconds < 86400:
            return f"{total_seconds // 3600}h ago"
        else:
            return f"{total_seconds // 86400}d ago"
    except Exception:
        return iso_datetime


def get_country_flag(location: str) -> str:
    """Try to match a location string to a country flag."""
    loc = location.lower()
    for name, meta in ALL_COUNTRIES.items():
        if name.lower() in loc or meta["label"].lower() in loc:
            return meta["flag"]
    return "🌐"


def scrape_linkedin(role: str, geo_id: str = "", location_label: str = "",
                    remote: bool = False, country_flag: str = "🌐") -> list[dict]:
    params = {
        "keywords": role,
        "f_TPR": LAST_24H,
        "position": 1,
        "pageNum": 0,
        "sortBy": "DD",
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

        # applicant count — LinkedIn sometimes shows this in a <span>
        applicants_el = card.select_one(
            "span.job-search-card__applicant-count, "
            "span[class*='applicant'], "
            "figcaption.base-search-card__extra-info span"
        )

        # easy apply badge
        easy_apply_el = card.select_one(
            "span.job-posting-benefits__text, "
            "li-icon[type='linkedin-bug'], "
            "span[class*='easy-apply'], "
            "span.base-search-card__benefits"
        )

        title     = title_el.get_text(strip=True)    if title_el    else ""
        company   = company_el.get_text(strip=True)  if company_el  else ""
        location  = location_el.get_text(strip=True) if location_el else location_label
        link      = link_el.get("href", "").split("?")[0] if link_el else ""
        posted_dt = time_el.get("datetime", "")      if time_el     else ""
        applicants = applicants_el.get_text(strip=True) if applicants_el else ""
        easy_apply = bool(easy_apply_el and "easy" in easy_apply_el.get_text(strip=True).lower())

        if not title or not link:
            continue

        # derive flag from location string
        flag = get_country_flag(location) or country_flag

        jobs.append({
            "title":      title,
            "company":    company,
            "location":   location,
            "flag":       flag,
            "url":        link,
            "posted_at":  posted_dt,
            "posted_ago": time_ago(posted_dt),
            "applicants": applicants,
            "easy_apply": easy_apply,
            "source":     "linkedin.com",
        })

    return jobs


def search_jobs(role: str, countries: list[str]) -> dict:
    all_jobs = []
    seen_urls = set()
    searched_labels = []

    def add_jobs(jobs, label):
        for job in jobs:
            if job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                job["search_region"] = label
                all_jobs.append(job)

    # 1. Gulf countries — always
    for name, meta in GULF_COUNTRIES.items():
        results = scrape_linkedin(role, geo_id=meta["geoId"],
                                  location_label=meta["label"],
                                  country_flag=meta["flag"])
        add_jobs(results, f"Gulf – {name}")
        searched_labels.append(name)

    # 2. Worldwide remote — always
    results = scrape_linkedin(role, remote=True, country_flag="🌍")
    add_jobs(results, "Worldwide Remote")
    searched_labels.append("Worldwide Remote")

    # 3. Extra countries user selected
    for country in countries:
        if country in GULF_COUNTRIES:
            continue
        meta = ALL_COUNTRIES.get(country)
        if not meta:
            continue
        results = scrape_linkedin(role, geo_id=meta["geoId"],
                                  location_label=meta["label"],
                                  country_flag=meta["flag"])
        add_jobs(results, country)
        searched_labels.append(country)

    query = f'"{role}" — LinkedIn — last 24 hrs — {", ".join(searched_labels)}'
    return {"query": query, "results": all_jobs}
