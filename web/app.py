import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# Try to import core functions dynamically (graceful fallback)
try:
    from core.solar import solar_longitude_from_datetime  # type: ignore
except Exception:  # pragma: no cover
    solar_longitude_from_datetime = None  # type: ignore

try:
    from core import equinox  # hypothetical future module
except Exception:  # pragma: no cover
    equinox = None  # type: ignore

app = FastAPI(title="Astronomical Watch API", version="0.1.0")
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# Mount static directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root_page():
    index_file = STATIC_DIR / "index.html"
    return index_file.read_text(encoding="utf-8")


def compute_now_payload(include_longitude: bool = True):
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Placeholder astronomical frame logic until core implementation is finished
    # TODO: Replace with real astronomical frame computations
    year = now.year
    # Basic milli-day computation (UTC-based for placeholder)
    seconds_since_midnight = (
        now - now.replace(hour=0, minute=0, second=0, microsecond=0)
    ).total_seconds()
    milli_day = int((seconds_since_midnight / 86400) * 1000)

    payload = {
        "utc_iso": now.isoformat().replace("+00:00", "Z"),
        "frame_year": year,  # will become equinox frame year
        "day_index": None,  # placeholder until implemented
        "milli_day": milli_day,
        "timestamp_proposed": f"{year}eq:000.{milli_day:03d}",
        "note": "Placeholder values until astronomical frame implemented.",
    }

    if include_longitude:
        if solar_longitude_from_datetime:
            try:
                lon_deg = float(solar_longitude_from_datetime(now))
                payload["solar_longitude_deg"] = lon_deg
            except Exception as e:  # pragma: no cover
                payload["solar_longitude_error"] = str(e)
        else:
            payload["solar_longitude_deg"] = None
            payload["solar_longitude_note"] = "solar_longitude_from_datetime not available"

    return payload


@app.get("/api/now")
async def api_now(include_longitude: bool = True):
    return compute_now_payload(include_longitude=include_longitude)


@app.get("/api/equinox/{year}")
async def api_equinox(year: int, include_longitude: bool = False):
    # Placeholder equinox endpoint
    if equinox and hasattr(equinox, "compute_vernal_equinox"):
        try:
            dt = equinox.compute_vernal_equinox(year)  # type: ignore
            data = {"year": year, "equinox_utc": dt.isoformat().replace("+00:00", "Z")}
            if include_longitude and solar_longitude_from_datetime:
                data["solar_longitude_deg"] = float(solar_longitude_from_datetime(dt))
            return data
        except Exception as e:  # pragma: no cover
            raise HTTPException(status_code=500, detail=f"Computation error: {e}")
    else:
        raise HTTPException(status_code=501, detail="Equinox computation not implemented yet")


@app.get("/api/ping")
async def api_ping():
    return {"status": "ok"}


# Serve manifest explicitly (some browsers look at /manifest.webmanifest)
@app.get("/manifest.webmanifest")
async def manifest_redirect():
    mf = STATIC_DIR / "manifest.webmanifest"
    if mf.exists():
        return FileResponse(mf)
    raise HTTPException(status_code=404, detail="Manifest not found")


# Health endpoint (for deployment probes)
@app.get("/healthz")
async def healthz():
    return {"status": "healthy"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=True)
