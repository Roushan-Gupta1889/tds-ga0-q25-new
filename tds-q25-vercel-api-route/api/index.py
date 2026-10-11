"""TDS GA0 Q25: Vercel POST analytics endpoint."""
from statistics import mean
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from telemetry_data import RECORDS

app = FastAPI(title="eShopCo Regional Analytics API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

class AnalyticsRequest(BaseModel):
    regions: list[str] = Field(min_length=1)
    threshold_ms: float


def percentile_linear(values: list[float], percentile: float) -> float:
    """Linear-interpolated percentile (same convention as NumPy default)."""
    if not values:
        raise ValueError("Cannot calculate percentile of an empty list")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * percentile / 100.0
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


@app.get("/")
def health() -> dict[str, str]:
    return {"message": "eShopCo analytics API is running", "post_endpoint": "/api/latency"}


@app.post("/api/latency")
def analytics(payload: AnalyticsRequest) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    for raw_region in payload.regions:
        region = raw_region.strip().lower()
        if not region:
            raise HTTPException(status_code=422, detail="Region name cannot be empty")
        rows = [r for r in RECORDS if str(r["region"]).lower() == region]
        if not rows:
            raise HTTPException(status_code=422, detail=f"No telemetry records for region '{raw_region}'")
        latencies = [float(r["latency_ms"]) for r in rows]
        uptimes = [float(r["uptime_pct"]) for r in rows]
        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": percentile_linear(latencies, 95),
            "avg_uptime": mean(uptimes),
            "breaches": sum(v > payload.threshold_ms for v in latencies),
        }
    return result
