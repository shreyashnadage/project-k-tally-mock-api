# Tally Data Simulator

## What This Is
A standalone tool that generates realistic MSME (Indian small business) financial data and serves it via a Tally-compatible TDML/XML API on port 9001. Used to test the `tally-shayak` agent locally without needing a real TallyPrime instance.

## Architecture
- **Backend**: Python 3.12+ / FastAPI on port 9001
- **Frontend**: React + Vite + TypeScript on port 5173
- **Storage**: SQLite (`data/simulator.db`)
- **TDML API**: POST to `/` with XML body — mimics TallyPrime's HTTP API exactly (UTF-16 LE responses)
- **JSON API**: `/api/simulations`, `/api/data/{sim_id}/*`, `/api/health`

## Quick Start
```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn backend.main:app --port 9001 --reload

# In another terminal:
cd frontend && npm install && npm run dev
```

## Key Directories
- `backend/simulator/` — Data generation engine (schemas, sector templates, voucher/ledger/stock generators)
- `backend/tdml/` — TDML XML protocol layer (request parser, response builder, entity exporters)
- `backend/api/` — FastAPI routes (TDML endpoint + JSON management API)
- `backend/models/` — SQLAlchemy ORM models
- `frontend/src/` — React dashboard

## TDML Protocol
- Single POST endpoint at `/` parses XML request body to determine what to export
- Responses are UTF-16 LE encoded with BOM (`\xff\xfe`)
- Date format: `YYYYMMDD` (no separators)
- Amount convention: credit-positive (Tally standard)
- Tag names include dots: `ALLLEDGERENTRIES.LIST`, `ALLINVENTORYENTRIES.LIST`

## Simulation Parameters
Sector (retail/manufacturing/trading/services/pharma/fmcg), business size, date range, seasonality, revenue range, customer/vendor/product counts, payment terms, bad debt %, cash sale %, GST rate, gross margin, growth trend.

## Testing with tally-shayak
Set `TALLY_URL=http://localhost:9001` in the shayak agent's `.env` to point it at the simulator instead of real Tally.
