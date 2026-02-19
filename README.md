# 🍀 Ireland Housing Schemes Finder

A complete website + scraper for finding Irish government housing schemes, grants, and supports. Includes a 3-question wizard that guides users to the right schemes for their situation.

## 📁 Project Structure

```
ireland-housing/
├── frontend/
│   ├── index.html          ← The main website
│   ├── wizard.html         ← 3-question scheme finder wizard
│   └── data/
│       └── schemes.json    ← Housing data (auto-updated by scraper)
│
└── scrapers/
    ├── scraper.py          ← Core scraper logic
    ├── scheduler.py        ← Scheduler + API server
    └── requirements.txt    ← Python dependencies
```

---

## 🚀 Quick Start (Full Setup with Live Scraping)

You'll need **3 terminal tabs** running at the same time.

### Step 1: Install Python dependencies
```bash
cd scrapers
pip install -r requirements.txt
```

### Step 2 — Terminal Tab 1: Start the API + weekly scheduler

> ⚠️ **macOS users:** Port 5000 is used by AirPlay Receiver. Use `--port 8080` instead, or disable AirPlay Receiver in **System Settings → General → AirDrop & Handoff**.

```bash
# macOS:
python3 scheduler.py --serve --port 8080

# Linux / Windows (or if you disabled AirPlay):
python3 scheduler.py --serve
```

This starts:
- A **REST API** on `http://localhost:8080` (or 5000)
- A **weekly scheduler** that auto-scrapes every Monday at 6am

### Step 3 — Terminal Tab 2: Run the scraper once to fetch data
```bash
python3 scheduler.py --scrape-now
```
This fetches the latest scheme data from government websites and saves it to `frontend/data/schemes.json`. You'll see `✅ Saved 15 schemes` when complete.

### Step 4 — Terminal Tab 3: Serve the frontend
```bash
cd frontend
python3 -m http.server 3000
```

Now visit **http://localhost:3000** in your browser. 🎉

---

## 🌐 Option: Just open the website (no backend)

The website works standalone using the bundled `data/schemes.json` — no Python needed:
```bash
cd frontend
python3 -m http.server 3000
# Visit http://localhost:3000
```
The "Refresh Data Now" button won't work without the backend running, but all schemes will display correctly.

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
# Change to daily at 8am:
schedule.every().day.at("08:00").do(do_scrape)

# Change to every 3 days:
schedule.every(3).days.do(do_scrape)
```

---

## 🧭 Scheme Finder Wizard

`wizard.html` guides users through 3 questions about their situation (goal, status, income/property type) and recommends the most relevant schemes with personalised explanations. It links back to the main site with the correct category pre-filtered.

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

### GitHub Pages (free, frontend only)
Enable GitHub Pages in your repo settings pointing to the `frontend/` folder. The site will work with the bundled data — no backend required.

### With a server (full live scraping)
Run `scheduler.py --serve --port 8080` on a VPS or cloud server. Use nginx as a reverse proxy to serve the frontend and forward API requests to port 8080.

---

## 📝 Notes
- Always verify scheme details on official government websites before applying
- Schemes change — the scraper keeps data current with weekly auto-updates
- The scraper is polite: adds delays between requests and uses a proper User-Agent
