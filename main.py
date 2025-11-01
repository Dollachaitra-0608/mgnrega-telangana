from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load cached data
with open("data/mgnrega_data.json", "r") as f:
    data = json.load(f)

@app.get("/districts")
def get_districts():
    districts = sorted(set(item["district_name"] for item in data))
    return districts

@app.get("/performance/{district}")
def get_performance(district: str):
    records = [r for r in data if r["district_name"].lower() == district.lower()]
    if not records:
        return []

    metrics = {
        "Households Worked": sum(float(r.get("Total_Households_Worked", 0)) for r in records),
        "Individuals Worked": sum(float(r.get("Total_Individuals_Worked", 0)) for r in records),
        "Wages": sum(float(r.get("Wages", 0)) for r in records),
        "Works Completed": sum(float(r.get("Number_of_Completed_Works", 0)) for r in records),
    }

    return [{"parameter": k, "value": v} for k, v in metrics.items()]
