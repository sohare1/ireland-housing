"""
Scheduler for Ireland Housing Schemes Scraper
Runs weekly automatically, or can be triggered ad-hoc via command line or API.
"""

import schedule
import time
import threading
import logging
import sys
import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))
from scraper import run_scraper, DATA_FILE
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

scrape_status = {
    "is_running": False,
    "last_run": None,
    "last_status": "Never run",
    "schemes_count": 0
}


def do_scrape():
    if scrape_status["is_running"]:
        logger.warning("Scraper already running, skipping.")
        return
    scrape_status["is_running"] = True
    scrape_status["last_status"] = "Running..."
    try:
        schemes = run_scraper()
        scrape_status["last_run"] = datetime.now().isoformat()
        scrape_status["last_status"] = "Success"
        scrape_status["schemes_count"] = len(schemes)
        logger.info(f"✅ Scrape complete: {len(schemes)} schemes")
    except Exception as e:
        scrape_status["last_status"] = f"Error: {str(e)}"
        logger.error(f"Scraper failed: {e}")
    finally:
        scrape_status["is_running"] = False


@app.route("/api/status")
def status():
    data_info = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            d = json.load(f)
        data_info = {
            "last_scraped": d.get("last_scraped"),
            "total_schemes": d.get("total_schemes", 0)
        }
    return jsonify({**scrape_status, **data_info})


@app.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    if scrape_status["is_running"]:
        return jsonify({"message": "Scraper already running", "status": "busy"}), 409
    thread = threading.Thread(target=do_scrape, daemon=True)
    thread.start()
    return jsonify({"message": "Scrape started", "status": "started"})


@app.route("/api/schemes")
def get_schemes():
    if not os.path.exists(DATA_FILE):
        return jsonify({"error": "No data yet. Run scraper first.", "schemes": []}), 404
    with open(DATA_FILE) as f:
        data = json.load(f)
    return jsonify(data)


def run_scheduler():
    """Run weekly scrape every Monday at 6am"""
    schedule.every().monday.at("06:00").do(do_scrape)
    logger.info("⏰ Scheduler started: will scrape every Monday at 06:00")

    # Run immediately on first start if no data
    if not os.path.exists(DATA_FILE):
        logger.info("No data found, running initial scrape...")
        threading.Thread(target=do_scrape, daemon=True).start()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ireland Housing Scraper")
    parser.add_argument("--scrape-now", action="store_true", help="Run scraper immediately and exit")
    parser.add_argument("--serve", action="store_true", help="Start API server + weekly scheduler")
    parser.add_argument("--port", type=int, default=5000, help="API server port")
    args = parser.parse_args()

    if args.scrape_now:
        do_scrape()
    elif args.serve:
        sched_thread = threading.Thread(target=run_scheduler, daemon=True)
        sched_thread.start()
        logger.info(f"🚀 API server starting on port {args.port}")
        app.run(host="0.0.0.0", port=args.port, debug=False)
    else:
        parser.print_help()
