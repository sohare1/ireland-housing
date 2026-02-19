# 🍀 Ireland Housing Schemes Finder

A complete website + scraper for finding Irish government housing schemes, grants, and supports.

## 📁 Project Structure

```
ireland-housing/
├── frontend/
│   ├── index.html          ← The website (open this in a browser)
│   └── data/
│       └── schemes.json    ← Housing data (auto-updated by scraper)
│
└── scrapers/
    ├── scraper.py          ← Core scraper logic
    ├── scheduler.py        ← Scheduler + API server
    └── requirements.txt    ← Python dependencies
```

---

## 🚀 Quick Start

### Option 1: Just open the website (no backend)
The website works standalone with bundled data:
```bash
open frontend/index.html
```
Or serve it locally:
```bash
cd frontend
python3 -m http.server 8080
# Visit http://localhost:8080
```

---

### Option 2: Full setup with live scraping

**Step 1: Install Python dependencies**
```bash
cd scrapers
pip install -r requirements.txt
```

**Step 2: Run the scraper now (ad-hoc)**
```bash
python3 scheduler.py --scrape-now
```
This fetches the latest data from government websites and saves it to `frontend/data/schemes.json`.

**Step 3: Start the API + weekly scheduler**
```bash
python3 scheduler.py --serve
```
This starts:
- A **REST API** on `http://localhost:5000`
- A **weekly scheduler** that auto-scrapes every Monday at 6am

**Step 4: Open the website**
```bash
cd frontend
python3 -m http.server 8080
# Visit http://localhost:8080
```
The website will detect the running API and enable the "Refresh Data Now" button.

---

## 🔌 API Endpoints (when running --serve)

| Endpoint | Method | Description |
|---|---|---|
| `/api/schemes` | GET | Get all housing schemes |
| `/api/scrape` | POST | Trigger an ad-hoc scrape |
| `/api/status` | GET | Check scraper status |

---

## 📅 Scheduling

The scheduler runs automatically **every Monday at 6am**. To change the schedule, edit `scheduler.py`:

```python
# Change from weekly Monday to daily at 8am:
schedule.every().day.at("08:00").do(do_scrape)

# Change to every 3 days:
schedule.every(3).days.do(do_scrape)
```

---

## 🌐 Data Sources

| Source | URL |
|---|---|
| Citizens Information | citizensinformation.ie |
| Department of Housing | housing.gov.ie |
| SEAI | seai.ie |

---

## 🏠 Schemes Covered

### Buying
- Help to Buy (HTB) Scheme — up to €30,000 tax rebate
- First Home Scheme — shared equity up to 30%
- Local Authority Home Loan — government-backed mortgage
- Local Authority Affordable Purchase

### Renting
- Housing Assistance Payment (HAP)
- Rent Supplement
- Cost Rental / Affordable Rental

### Social Housing
- Social Housing (Local Authority)
- Mortgage to Rent Scheme

### Renovation & Grants
- Croí Cónaithe (Cities) Grant — up to €50,000
- Croí Cónaithe (Towns) Grant — up to €50,000
- SEAI Home Energy Upgrade Grants
- Warmer Homes Scheme (FREE upgrades)
- Housing Adaptation Grant — up to €30,000
- Mobility Aids Housing Grant — up to €6,000

---

## 🛠️ Deployment

### GitHub Pages (free, no backend)
```bash
# Push the frontend/ folder to a GitHub repo
# Enable GitHub Pages in repo settings → use main branch / root or /frontend
```

### With a server (full scraping)
Run `scheduler.py --serve` on a VPS or cloud server. Use nginx or a reverse proxy to serve the frontend and proxy API requests to port 5000.

---

## 📝 Notes
- Always verify scheme details on official government websites before applying
- Schemes change — the scraper keeps data current
- The scraper is polite: adds delays between requests and uses a proper User-Agent
