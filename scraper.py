"""
Ireland Housing Schemes Scraper
Scrapes housing scheme information from:
- Citizens Information (citizensinformation.ie)
- Housing.gov.ie
- hap.ie
- rebuilding-ireland.gov.ie
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "../frontend/data/schemes.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; IrelandHousingBot/1.0; +https://github.com/your-repo)"
}

@dataclass
class HousingScheme:
    id: str
    name: str
    category: str
    description: str
    eligibility: list[str]
    benefits: list[str]
    how_to_apply: str
    url: str
    source: str
    last_updated: str
    tags: list[str]
    icon: str = "🏠"
    status: str = "Active"


def safe_get(url: str, retries: int = 3) -> Optional[BeautifulSoup]:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            time.sleep(2 ** attempt)
    return None


def scrape_citizens_information() -> list[HousingScheme]:
    """Scrape housing schemes from Citizens Information"""
    schemes = []
    now = datetime.now().strftime("%Y-%m-%d")

    pages = [
        {
            "url": "https://www.citizensinformation.ie/en/housing/owning-a-home/help-with-buying-a-home/help-to-buy-incentive/",
            "name": "Help to Buy (HTB) Scheme",
            "category": "Buying",
            "icon": "🏡",
            "tags": ["first-time buyer", "new build", "tax rebate", "buying"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/owning-a-home/help-with-buying-a-home/first-home-scheme/",
            "name": "First Home Scheme",
            "category": "Buying",
            "icon": "🔑",
            "tags": ["first-time buyer", "shared equity", "buying"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/owning-a-home/help-with-buying-a-home/local-authority-affordable-purchase-scheme/",
            "name": "Local Authority Affordable Purchase Scheme",
            "category": "Buying",
            "icon": "🏘️",
            "tags": ["affordable", "local authority", "buying"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/renting-a-home/help-with-renting/housing-assistance-payment/",
            "name": "Housing Assistance Payment (HAP)",
            "category": "Renting",
            "icon": "💶",
            "tags": ["rental support", "social housing", "renting"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/renting-a-home/help-with-renting/rent-supplement/",
            "name": "Rent Supplement",
            "category": "Renting",
            "icon": "📋",
            "tags": ["rental support", "social welfare", "renting"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/social-housing/applying-for-local-authority-housing/",
            "name": "Social Housing (Local Authority)",
            "category": "Social Housing",
            "icon": "🏢",
            "tags": ["social housing", "local authority", "council"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/owning-a-home/home-loans/local-authority-mortgages/",
            "name": "Local Authority Home Loan",
            "category": "Buying",
            "icon": "🏦",
            "tags": ["mortgage", "local authority", "buying", "first-time buyer"],
        },
        {
            "url": "https://www.citizensinformation.ie/en/housing/housing-grants-and-schemes/grants-for-home-renovations-and-improvements/housing-for-all-retrofitting-scheme/",
            "name": "National Home Energy Upgrade Scheme",
            "category": "Renovation & Grants",
            "icon": "⚡",
            "tags": ["retrofitting", "energy upgrade", "grants", "renovation"],
        },
    ]

    for page_info in pages:
        logger.info(f"Scraping: {page_info['name']}")
        soup = safe_get(page_info["url"])
        if not soup:
            logger.warning(f"Could not fetch {page_info['url']}, using fallback data")
            schemes.append(_fallback_scheme(page_info, now))
            continue

        description = ""
        eligibility = []
        benefits = []
        how_to_apply = ""

        # Try to extract main article content
        article = soup.find("article") or soup.find("div", class_="article-body") or soup.find("main")
        if article:
            # Description - first meaningful paragraph
            for p in article.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 80:
                    description = text[:400] + ("..." if len(text) > 400 else "")
                    break

            # Extract lists as eligibility/benefits
            lists = article.find_all("ul")
            for i, ul in enumerate(lists[:4]):
                items = [li.get_text(strip=True) for li in ul.find_all("li") if li.get_text(strip=True)]
                if i == 0:
                    eligibility = items[:6]
                elif i == 1:
                    benefits = items[:6]

            # How to apply section
            for heading in article.find_all(["h2", "h3"]):
                if "apply" in heading.get_text(strip=True).lower():
                    next_el = heading.find_next_sibling()
                    if next_el:
                        how_to_apply = next_el.get_text(strip=True)[:300]
                    break

        if not description:
            description = f"Government housing support scheme. Visit the official page for full details."

        scheme = HousingScheme(
            id=page_info["name"].lower().replace(" ", "-").replace("(", "").replace(")", ""),
            name=page_info["name"],
            category=page_info["category"],
            description=description,
            eligibility=eligibility or ["Check official website for eligibility criteria"],
            benefits=benefits or ["Check official website for full benefits"],
            how_to_apply=how_to_apply or "Visit the official Citizens Information page to apply.",
            url=page_info["url"],
            source="Citizens Information",
            last_updated=now,
            tags=page_info["tags"],
            icon=page_info["icon"],
            status="Active"
        )
        schemes.append(scheme)
        time.sleep(1)  # Be polite

    return schemes


def _fallback_scheme(page_info: dict, now: str) -> HousingScheme:
    """Returns a fallback scheme when scraping fails"""
    fallbacks = {
        "Help to Buy (HTB) Scheme": {
            "description": "The Help to Buy incentive is a scheme for first-time buyers of newly built homes. It allows you to claim a refund of income tax and DIRT that you paid over the previous 4 tax years.",
            "eligibility": ["First-time buyer only", "Property must be newly built", "Property value up to €500,000", "Mortgage must be at least 70% of property value", "Must live in the property as your main home"],
            "benefits": ["Tax rebate of up to €30,000", "Applies to income tax and DIRT paid", "Can be used towards deposit"],
            "how_to_apply": "Apply through Revenue's myAccount or ROS. Complete the HTB claim through Revenue Online Services."
        },
        "First Home Scheme": {
            "description": "The First Home Scheme is a shared equity scheme helping first-time buyers purchase a new home. The government and participating lenders pay up to 30% of the cost of a new home.",
            "eligibility": ["First-time buyer", "New build properties only", "Must have mortgage approval", "Property price limits apply by county", "Income limits apply"],
            "benefits": ["Government equity share up to 30%", "Reduces mortgage required", "No interest for first 5 years on government portion"],
            "how_to_apply": "Apply at firsthomescheme.ie after getting mortgage approval from a participating lender."
        },
        "Housing Assistance Payment (HAP)": {
            "description": "HAP is a social housing support scheme for people with a long-term housing need. Your local authority pays your rent directly to your landlord and you pay a contribution to the local authority.",
            "eligibility": ["Must be on social housing list", "Income limits apply", "Property must meet HAP standards", "Landlord must agree to HAP"],
            "benefits": ["Rent paid directly to landlord", "Flexibility to find own accommodation", "Can work and still receive HAP"],
            "how_to_apply": "Apply through your local authority housing department."
        },
        "Rent Supplement": {
            "description": "Rent Supplement is a means-tested payment to help with rental costs if you are renting privately and have limited income.",
            "eligibility": ["Must meet income limits", "Must have been renting for at least 6 months (some exceptions)", "Rent must be within rent limits", "Must be habitually resident in Ireland"],
            "benefits": ["Weekly payment towards rent", "Paid directly to you or landlord"],
            "how_to_apply": "Apply at your local Intreo Centre or Social Welfare Branch Office."
        },
    }

    data = fallbacks.get(page_info["name"], {
        "description": "Visit the official website for full details about this scheme.",
        "eligibility": ["Check official website for eligibility criteria"],
        "benefits": ["Check official website for benefits"],
        "how_to_apply": "Visit the official page to apply."
    })

    return HousingScheme(
        id=page_info["name"].lower().replace(" ", "-").replace("(", "").replace(")", ""),
        name=page_info["name"],
        category=page_info["category"],
        description=data["description"],
        eligibility=data["eligibility"],
        benefits=data["benefits"],
        how_to_apply=data["how_to_apply"],
        url=page_info["url"],
        source="Citizens Information",
        last_updated=now,
        tags=page_info["tags"],
        icon=page_info["icon"],
        status="Active"
    )


def scrape_additional_schemes() -> list[HousingScheme]:
    """Additional hardcoded/scraped schemes"""
    now = datetime.now().strftime("%Y-%m-%d")
    return [
        HousingScheme(
            id="croí-cónaithe-cities",
            name="Croí Cónaithe (Cities) Scheme",
            category="Renovation & Grants",
            description="A grant of up to €50,000 (€70,000 for deep retrofit) to renovate a vacant property in cities. Designed to bring empty homes back into use.",
            eligibility=["Property must be vacant for 2+ years", "Must be in eligible urban area", "Must become your principal private residence", "Refurbishment work must meet standards"],
            benefits=["Grant up to €50,000", "Up to €70,000 for deep energy retrofit", "Brings vacant properties back into use"],
            how_to_apply="Apply through your local authority. Check housing.gov.ie for participating local authorities.",
            url="https://www.gov.ie/en/service/f9f3f-croi-conaithe-cities-scheme/",
            source="housing.gov.ie",
            last_updated=now,
            tags=["renovation", "grant", "vacant", "cities"],
            icon="🔨",
            status="Active"
        ),
        HousingScheme(
            id="croí-cónaithe-towns",
            name="Croí Cónaithe (Towns) Fund",
            category="Renovation & Grants",
            description="A grant of up to €50,000 to renovate a vacant property in towns and villages, encouraging rural repopulation and revitalisation.",
            eligibility=["Property must be vacant for 2+ years", "Must be in an eligible town or village", "Must become principal private residence", "Town must have population under 30,000"],
            benefits=["Grant up to €50,000", "Supports rural living", "Revitalises town centres"],
            how_to_apply="Apply through your local authority. Check gov.ie for eligibility of your town.",
            url="https://www.gov.ie/en/service/croi-conaithe-towns/",
            source="housing.gov.ie",
            last_updated=now,
            tags=["renovation", "grant", "rural", "towns", "vacant"],
            icon="🏚️",
            status="Active"
        ),
        HousingScheme(
            id="secure-tenancy-affordable-rental",
            name="Secure Tenancy Affordable Rental (STAR)",
            category="Renting",
            description="STAR provides long-term affordable rental accommodation to middle-income earners who earn too much for social housing but cannot afford private market rents.",
            eligibility=["Income limits apply (typically €35,000–€120,000)", "Must not own a property", "Must be unable to afford private rent", "Must meet household size requirements"],
            benefits=["Rents set at below market rates", "Long-term security of tenure", "Suitable for middle-income earners"],
            how_to_apply="Properties advertised through local authorities and Approved Housing Bodies.",
            url="https://www.citizensinformation.ie/en/housing/renting-a-home/help-with-renting/",
            source="Citizens Information",
            last_updated=now,
            tags=["affordable rental", "middle income", "renting"],
            icon="🔐",
            status="Active"
        ),
        HousingScheme(
            id="warms-homes-scheme",
            name="Warmer Homes Scheme",
            category="Renovation & Grants",
            description="Free energy efficiency upgrades for homeowners in receipt of certain social welfare payments. Includes insulation, heating upgrades, and more at no cost.",
            eligibility=["Must own your home", "Must receive qualifying social welfare payment (e.g., Fuel Allowance, Job Seekers)", "Home must be pre-2006 build", "Must meet SEAI criteria"],
            benefits=["Completely free upgrades", "Insulation, heating, windows", "Reduces energy bills", "SEAI approved contractors"],
            how_to_apply="Apply online at seai.ie or call SEAI directly at 1800 250 204.",
            url="https://www.seai.ie/grants/home-energy-grants/fully-funded-upgrades-for-eligible-homes/",
            source="SEAI",
            last_updated=now,
            tags=["free", "energy", "insulation", "renovation", "grants"],
            icon="🌡️",
            status="Active"
        ),
        HousingScheme(
            id="home-renovation-incentive",
            name="SEAI Home Energy Grants",
            category="Renovation & Grants",
            description="SEAI offers grants for homeowners to improve their home's energy efficiency, including insulation, heat pumps, solar panels, and more.",
            eligibility=["Homeowner or landlord", "Home built before 2011 for most grants", "Work done by SEAI registered contractors"],
            benefits=["Grants from €400 to €24,000+", "Multiple measures covered", "Reduces carbon footprint and bills"],
            how_to_apply="Apply at seai.ie before starting work. Choose an SEAI registered contractor.",
            url="https://www.seai.ie/grants/home-energy-grants/",
            source="SEAI",
            last_updated=now,
            tags=["energy", "insulation", "solar", "heat pump", "grants", "renovation"],
            icon="☀️",
            status="Active"
        ),
        HousingScheme(
            id="mortgage-to-rent",
            name="Mortgage to Rent Scheme",
            category="Social Housing",
            description="If you are at risk of losing your home due to mortgage arrears, the Mortgage to Rent scheme lets you sell your home to a housing association and stay in it as a social housing tenant.",
            eligibility=["Mortgage in arrears", "Property is main home", "Must qualify for social housing", "Property value within limits", "Lender must agree"],
            benefits=["Stay in your home as tenant", "Mortgage debt resolved", "Long-term housing security"],
            how_to_apply="Contact your lender or the Money Advice & Budgeting Service (MABS) at mabs.ie.",
            url="https://www.citizensinformation.ie/en/housing/owning-a-home/mortgage-arrears/mortgage-to-rent-scheme/",
            source="Citizens Information",
            last_updated=now,
            tags=["mortgage", "arrears", "social housing", "tenant"],
            icon="🔄",
            status="Active"
        ),
        HousingScheme(
            id="disability-adaptation-grant",
            name="Housing Adaptation Grant",
            category="Renovation & Grants",
            description="A grant to help with the cost of changes needed to make a home more suitable for a person with a physical, sensory or intellectual disability.",
            eligibility=["Person with disability living in home", "Work must be medically necessary", "Income limits apply", "Private homeowner or tenant (with landlord consent)"],
            benefits=["Grant up to €30,000", "Covers ramps, stairlifts, wet rooms, widened doors", "Improves independence"],
            how_to_apply="Apply through your local authority housing department with an Occupational Therapist report.",
            url="https://www.citizensinformation.ie/en/housing/housing-grants-and-schemes/housing-supports-for-older-people-and-people-with-disabilities/housing-adaptation-grant-for-people-with-disability/",
            source="Citizens Information",
            last_updated=now,
            tags=["disability", "adaptation", "grant", "accessibility"],
            icon="♿",
            status="Active"
        ),
    ]


def run_scraper():
    """Main scraper function"""
    logger.info("="*50)
    logger.info("Starting Ireland Housing Schemes Scraper")
    logger.info("="*50)

    all_schemes = []

    logger.info("Scraping Citizens Information...")
    ci_schemes = scrape_citizens_information()
    all_schemes.extend(ci_schemes)
    logger.info(f"Got {len(ci_schemes)} schemes from Citizens Information")

    logger.info("Adding additional schemes...")
    extra_schemes = scrape_additional_schemes()
    all_schemes.extend(extra_schemes)
    logger.info(f"Added {len(extra_schemes)} additional schemes")

    # Save to JSON
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    output = {
        "last_scraped": datetime.now().isoformat(),
        "total_schemes": len(all_schemes),
        "schemes": [asdict(s) for s in all_schemes]
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Saved {len(all_schemes)} schemes to {DATA_FILE}")
    return all_schemes


if __name__ == "__main__":
    run_scraper()
