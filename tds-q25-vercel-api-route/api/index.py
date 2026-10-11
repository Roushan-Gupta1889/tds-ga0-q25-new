
"""TDS GA0 Q25: Vercel POST analytics endpoint with CORS."""

from statistics import mean

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from telemetry_data import RECORDS

app = FastAPI(
    title="eShopCo Regional Analytics API",
    version="1.0.1",
)

# Standard CORS support.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Explicitly add CORS headers to all application responses.
@app.middleware("http")
async def always_include_cors_headers(
    request: Request,
    call_next,
):
    if request.method == "OPTIONS":
        response = Response(status_code=204)
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = (
        "POST, OPTIONS"
    )
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response


class AnalyticsRequest(BaseModel):
    regions: list[str] = Field(min_length=1)
    threshold_ms: float


def percentile_linear(
    values: list[float],
    percentile: float = 95,
) -> float:
    """Calculate percentile using linear interpolation."""
    if not values:
        raise ValueError(
            "Cannot calculate percentile of an empty list"
        )

    ordered = sorted(float(value) for value in values)

    position = (len(ordered) - 1) * percentile / 100.0
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower

    return (
        ordered[lower]
        + (ordered[upper] - ordered[lower]) * fraction
    )


@app.get("/")
def health() -> dict:
    return {
        "message": "eShopCo analytics API is running",
        "post_endpoint": "/api/latency",
    }


@app.post("/api/latency")
def analytics(
    payload: AnalyticsRequest,
) -> dict:
    result = {}

    for raw_region in payload.regions:
        region = raw_region.strip().lower()

        if not region:
            raise HTTPException(
                status_code=422,
                detail="Region name cannot be empty",
            )

        rows = [
            row
            for row in RECORDS
            if str(row["region"]).lower() == region
        ]

        if not rows:
            raise HTTPException(
                status_code=422,
                detail=f"No telemetry records for region '{raw_region}'",
            )

        latencies = [
            float(row["latency_ms"]) for row in rows
        ]
        uptimes = [
            float(row["uptime_pct"]) for row in rows
        ]

        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": percentile_linear(
                latencies, 95
            ),
            "avg_uptime": mean(uptimes),
            "breaches": sum(
                value > payload.threshold_ms
                for value in latencies
            ),
        }

    return result
