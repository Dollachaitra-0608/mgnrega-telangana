# etl_fetch.py
import time, logging, os, math
import requests
from database import SessionLocal, engine, Base
from models import MGNREGAData
from dotenv import load_dotenv
import os

load_dotenv()

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# API config (from data.gov.in page you pasted)
RESOURCE_ID = "ee03643a-ee4c-48c2-ac30-9f2ff26ab722"
API_KEY = os.getenv("579b464db66ec23bdd000001a5153959870449c641b1035ab68e4289")
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

# We'll fetch Telangana only
FILTERS = {"filters[state_name]": "TELANGANA"}
# page size
LIMIT = 5000

logger = logging.getLogger("etl")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def fetch_page(offset=0, limit=LIMIT):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
        **FILTERS
    }
    resp = requests.get(BASE_URL, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()

def normalize_record(r):
    district = r.get("district_name", "Unknown")
    month = r.get("month", "")
    fin_year = r.get("fin_year", "")
    
    # Extract ending year (e.g., "2024-2025" → 2025)
    try:
        year = int(fin_year.split("-")[1])
    except:
        year = 0

    try:
        households = int(r.get("Total_Households_Worked", 0))
    except:
        households = 0

    try:
        persondays = float(r.get("Persondays_of_Central_Liability_so_far", 0))
    except:
        persondays = 0.0

    try:
        wages = float(r.get("Wages", 0))
    except:
        wages = 0.0

    return {
        "district": district.strip(),
        "month": month.strip(),
        "year": year,
        "households": households,
        "persondays": persondays,
        "wages": wages,
        "raw": r
    }


def upsert_records(records):
    db = SessionLocal()
    count = 0
    try:
        for r in records:
            n = normalize_record(r)
            if n["district"] == "Unknown":
                continue
            # upsert by district+year+month
            existing = db.query(MGNREGAData).filter(
                MGNREGAData.district == n["district"],
                MGNREGAData.year == n["year"],
                MGNREGAData.month == n["month"]
            ).first()
            if existing:
                existing.households_worked = n["households"]
                existing.persondays_generated = n["persondays"]
                existing.total_wages = n["wages"]
                existing.raw_json = n["raw"]
            else:
                new = MGNREGAData(
                    district=n["district"],
                    month=n["month"],
                    year=n["year"],
                    households_worked=n["households"],
                    persondays_generated=n["persondays"],
                    total_wages=n["wages"],
                    raw_json=n["raw"]
                )
                db.add(new)
            count += 1
        db.commit()
        logger.info("Upserted %d records", count)
    except Exception as e:
        db.rollback()
        logger.exception("DB error: %s", e)
    finally:
        db.close()

def run_etl():
    logger.info("Starting ETL for Telangana")
    # first page to know total (if returned)
    try:
        first = fetch_page(offset=0, limit=1)
    except Exception as e:
        logger.exception("Failed to contact API: %s", e)
        return

    # If the API returns 'total' use it; otherwise loop until page returns < limit
    total = first.get("total_count") or first.get("total") or None

    if total:
        total = int(total)
        pages = math.ceil(total / LIMIT)
        logger.info("Total records: %s, pages: %s", total, pages)
        for i in range(pages):
            offset = i * LIMIT
            try:
                page = fetch_page(offset=offset, limit=LIMIT)
                records = page.get("records") or page
                upsert_records(records)
                time.sleep(0.5)
            except Exception as e:
                logger.exception("Error fetching page offset=%s: %s", offset, e)
                time.sleep(2)
    else:
        # fallback: fetch pages until empty
        offset = 0
        while True:
            try:
                page = fetch_page(offset=offset, limit=LIMIT)
                records = page.get("records") or page
                if not records:
                    break
                upsert_records(records)
                if len(records) < LIMIT:
                    break
                offset += LIMIT
                time.sleep(0.5)
            except Exception as e:
                logger.exception("Error fetching offset=%s: %s", offset, e)
                break
    logger.info("ETL finished")

if __name__ == "__main__":
    run_etl()
