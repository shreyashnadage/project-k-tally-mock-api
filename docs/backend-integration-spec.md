# Backend Integration Spec: Test Mode with Simulated Data

**From:** Tally Data Simulator team
**To:** project-k-backend-service coding agent
**Date:** 2026-06-29
**Status:** Proposed
**Backend repo:** `D:\project-k-backend-service`

---

## Context

We have a **Tally Data Simulator** service that generates realistic MSME financial data and serves it via a TDML/XML API identical to TallyPrime. It will be deployed to AWS and accessible online.

The backend (`project-k-backend-service`) is a **cloud ingest platform** — it does NOT pull from Tally directly. An external agent extracts data from TallyPrime and POSTs it to the backend's `/v1/ledgers`, `/v1/vouchers`, etc. endpoints.

**The goal:** Allow the simulator's data to be ingested into the same backend — tagged so it never mixes with real client data — and provide a UI toggle to switch the dashboard between live and test views.

---

## Architecture: How It Fits Together

```
┌──────────────────┐       POST /v1/ledgers        ┌───────────────────────┐
│  Real Tally       │  ──→  (agent extracts)  ──→   │                       │
│  (port 9000)      │       data_source='live'      │  project-k-backend    │
└──────────────────┘                                │  (cloudplatform/)     │
                                                    │                       │
┌──────────────────┐       POST /v1/test/ingest     │  ┌─────────────────┐  │
│  Tally Simulator  │  ──→  (new endpoint)    ──→   │  │  Same DB tables │  │
│  (AWS, port 9001) │       data_source='sim:42'    │  │  + data_source  │  │
└──────────────────┘                                │  └─────────────────┘  │
                                                    │                       │
                                                    │  Dashboard filters    │
                                                    │  by data_source       │
                                                    └───────────────────────┘
```

The simulator already has a JSON management API (`GET /api/simulations`, `GET /api/data/{sim_id}/ledgers`, etc.) that returns data in a structured format. The new backend endpoint will pull from that API and ingest it with tagging.

---

## Changes Required

### 1. Schema: Add `data_source` Column

**File:** `cloudplatform/db/models.py`

Add a `data_source` column to these 6 tables:

| Model | Table | Current dedup index |
|-------|-------|-------------------|
| `Ledger` | `ledgers` | `ix_ledger_dedup` (tenant_id, company_guid, ledger_guid) |
| `Voucher` | `vouchers` | `ix_voucher_dedup` (tenant_id, company_guid, voucher_guid) |
| `AccountGroup` | `account_groups` | `ix_group_dedup` (tenant_id, company_guid, group_guid) |
| `StockItem` | `stock_items` | `ix_stock_dedup` (tenant_id, company_guid, item_guid) |
| `StockGroup` | `stock_groups` | `ix_stockgroup_dedup` (tenant_id, company_guid, group_guid) |
| `SyncAuditLog` | `sync_audit_log` | (none — append-only) |

**Column definition (add to each model):**

```python
data_source = Column(String(50), nullable=False, default="live", index=True)
# Values: 'live' | 'sim:<simulation_id>'
# Examples: 'live', 'sim:42', 'sim:7'
```

**Important:** The existing dedup indexes do NOT need to change. Simulated data uses deterministic GUIDs (uuid5-based) from the simulator, which will never collide with real Tally GUIDs. The `data_source` column is for query filtering, not dedup.

**Migration:** Add the column with `DEFAULT 'live'` so all existing records are automatically tagged as live data. No backfill needed.

---

### 2. Config: Add Simulator URL

**File:** `cloudplatform/db/database.py` (or wherever env vars are read)

```python
SIMULATOR_URL = os.getenv("SIMULATOR_URL", "")  # e.g. "http://simulator.example.com:9001"
```

This is the URL of the AWS-hosted Tally Data Simulator. When empty, test mode features are disabled.

---

### 3. New Model: TestModeState

**File:** `cloudplatform/db/models.py`

```python
class TestModeState(Base):
    """Tracks whether the dashboard is viewing live or simulated data."""
    __tablename__ = "test_mode_state"

    id = Column(Integer, primary_key=True, default=1)  # singleton row
    tenant_id = Column(String(36), nullable=False, index=True)
    mode = Column(String(10), nullable=False, default="live")  # 'live' or 'test'
    active_simulation_id = Column(Integer, nullable=True)  # sim ID from simulator
    simulation_name = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

---

### 4. New API: Test Mode Endpoints

**File:** Create `cloudplatform/api/test_mode.py`

```python
router = APIRouter(prefix="/v1/test", tags=["test-mode"])
```

#### 4a. Toggle Mode

```
GET  /v1/test/mode
  Headers: X-Api-Key (existing auth)
  Response: {
    "mode": "live" | "test",
    "simulation_id": 42 | null,
    "simulation_name": "Pharma Growing Test" | null,
    "simulator_url": "http://..." | null,
    "simulator_available": true | false
  }

POST /v1/test/mode
  Headers: X-Api-Key
  Body: { "mode": "test", "simulation_id": 42 }
    OR: { "mode": "live" }
  Response: { "mode": "test", "simulation_id": 42 }
```

When switching to `"live"`, set `active_simulation_id = null`.

#### 4b. List Available Simulations (proxy to simulator)

```
GET  /v1/test/simulations
  Headers: X-Api-Key
  Response: proxied from GET {SIMULATOR_URL}/api/simulations
  → [{ "id": 1, "name": "Pharma Growing Test", "company_name": "MedLife Pharma Pvt Ltd", "status": "completed", ... }]
```

This proxies to the simulator so the dashboard doesn't need to know the simulator URL.

#### 4c. Ingest Simulated Data

```
POST /v1/test/ingest
  Headers: X-Api-Key
  Body: { "simulation_id": 42 }
  Response: {
    "simulation_id": 42,
    "data_source": "sim:42",
    "ingested": {
      "ledgers": 42,
      "vouchers": 129,
      "stock_items": 10,
      "stock_groups": 1,
      "account_groups": 12
    }
  }
```

**Implementation logic:**

1. Call `GET {SIMULATOR_URL}/api/data/{simulation_id}/ledgers` to fetch all ledgers
2. Call `GET {SIMULATOR_URL}/api/data/{simulation_id}/vouchers` to fetch all vouchers
3. Call `GET {SIMULATOR_URL}/api/data/{simulation_id}/stock-items` to fetch stock items
4. For each record, create the ORM model instance with `data_source = f"sim:{simulation_id}"`
5. Use the same dedup logic as existing ingest (IntegrityError → skip)
6. The `tenant_id` should be the authenticated tenant's ID
7. The `company_guid` should come from the simulator data (it generates deterministic GUIDs)

**The simulator's JSON API returns data in this shape:**

```json
// GET /api/data/{sim_id}/ledgers
[
  {
    "id": 1,
    "name": "Fortis Medical Supply",
    "group_name": "Sundry Debtors",
    "guid": "843a779f-9645-51de-8a2c-f51cf66324d2",
    "opening_balance": -13599.84,
    "closing_balance": 0.0,
    "gst_registration_type": "Regular",
    "gst_number": "10QKUTM4794S4ZX",
    "state": "Bihar",
    "is_bill_wise": true,
    "credit_period": 30,
    "alter_id": 1,
    "company_id": 1
  },
  ...
]

// GET /api/data/{sim_id}/vouchers
[
  {
    "id": 1,
    "voucher_type": "Purchase",
    "voucher_number": "PR/202404/001",
    "date": "2024-04-06",
    "party_ledger_name": "Sun Pharma Wholesale",
    "amount": 620274.23,
    "narration": "Purchase from Sun Pharma Wholesale",
    "guid": "85e86fa6-7009-5676-b8fb-b7c9439a3c1b",
    "alter_id": 6,
    "company_id": 1
  },
  ...
]

// GET /api/data/{sim_id}/stock-items
[
  {
    "id": 1,
    "name": "Dettol Antiseptic 500ml",
    "group_name": "Pharma Products",
    "guid": "51ab32a6-c092-5878-90f5-a88d55c798a9",
    "unit": "Nos",
    "opening_quantity": 414,
    "opening_rate": 189.91,
    "opening_value": 78622.74,
    "gst_rate": 18.0,
    "hsn_code": "3808",
    "alter_id": 1,
    "company_id": 1
  },
  ...
]
```

**Field mapping from simulator → backend models:**

| Simulator field | Backend Ledger column |
|---|---|
| `guid` | `ledger_guid` |
| `name` | `name` |
| `group_name` | `parent` |
| `group_name` | `ledger_type` |
| `opening_balance` | `opening_balance` (convert to string) |
| `closing_balance` | `closing_balance` (convert to string) |
| (from company) | `company_guid` — get from `GET /api/data/{sim_id}/company` |

| Simulator field | Backend Voucher column |
|---|---|
| `guid` | `voucher_guid` |
| `voucher_type` | `voucher_type` |
| `voucher_number` | `voucher_number` |
| `date` | `date` (already YYYY-MM-DD) |
| `party_ledger_name` | `party` |
| `narration` | `narration` |
| `amount` | `amount` (convert to string) |
| (from company) | `company_guid` |

| Simulator field | Backend StockItem column |
|---|---|
| `guid` | `item_guid` |
| `name` | `name` |
| `group_name` | `parent` |
| `unit` | `base_units` |
| `opening_value` | `opening_balance` (convert to string) |
| `hsn_code` | `hsn_code` |
| `gst_rate` | `gst_rate` (convert to string) |
| (from company) | `company_guid` |

#### 4d. List Ingested Test Datasets

```
GET  /v1/test/datasets
  Headers: X-Api-Key
  Response: [
    {
      "simulation_id": 42,
      "data_source": "sim:42",
      "simulation_name": "Pharma Growing Test",
      "ledgers": 42,
      "vouchers": 129,
      "stock_items": 10,
      "ingested_at": "2026-06-29T10:30:00Z"
    }
  ]
```

Query: `SELECT data_source, COUNT(*) FROM ledgers WHERE tenant_id=? AND data_source LIKE 'sim:%' GROUP BY data_source`

#### 4e. Purge Test Dataset

```
DELETE /v1/test/datasets/{simulation_id}
  Headers: X-Api-Key
  Response: { "deleted": { "ledgers": 42, "vouchers": 129, ... } }
```

Delete all records where `data_source = f'sim:{simulation_id}'` across all 6 tables. Also delete the `TestModeState` row if it references this simulation.

---

### 5. Dashboard Query Changes

**File:** `cloudplatform/api/dashboard.py`

**Every query** in this file that filters by `tenant_id` must ALSO filter by `data_source`. This affects:

| Endpoint | Current filter | Add |
|---|---|---|
| `GET /api/dashboard/kpis` | `Ledger.tenant_id == tenant.id` | `+ Ledger.data_source == active_source` |
| `GET /api/dashboard/vouchers` | `Voucher.tenant_id == tenant.id` | `+ Voucher.data_source == active_source` |
| `GET /api/dashboard/cash-flow` | `Voucher.tenant_id == tenant.id` | `+ Voucher.data_source == active_source` |
| `GET /api/dashboard/ledgers` | `Ledger.tenant_id == tenant.id` | `+ Ledger.data_source == active_source` |
| `GET /api/dashboard/ledgers/groups` | `Ledger.tenant_id == tenant.id` | `+ Ledger.data_source == active_source` |
| `get_sync_health()` | `SyncAuditLog.tenant_id == tenant_id` | `+ SyncAuditLog.data_source == active_source` |

**File:** `cloudplatform/api/ingest.py`

| Endpoint | Current filter | Add |
|---|---|---|
| `GET /v1/stats` | `Model.tenant_id == tenant.id` | `+ Model.data_source == active_source` |
| `GET /v1/data/{resource}` | `model.tenant_id == tenant.id` | `+ model.data_source == active_source` |

**Helper function to add (put in a shared location):**

```python
def get_active_data_source(tenant_id: str, db: Session) -> str:
    """Returns 'live' or 'sim:<id>' based on current test mode state."""
    state = db.query(TestModeState).filter(
        TestModeState.tenant_id == tenant_id
    ).first()
    if state and state.mode == "test" and state.active_simulation_id:
        return f"sim:{state.active_simulation_id}"
    return "live"
```

Use this in every dashboard/stats query. **Do not add it to the ingest endpoints** (`POST /v1/ledgers`, `POST /v1/vouchers`, etc.) — those always write `data_source='live'` because they come from the real agent.

---

### 6. Existing Ingest Endpoints: Tag as Live

**File:** `cloudplatform/api/ingest.py`

In `ingest_ledgers()`, `ingest_vouchers()`, `ingest_groups()`, `ingest_stock_items()`, `ingest_stock_groups()` — when creating ORM model instances, explicitly set:

```python
row = Ledger(
    tenant_id=tenant.id,
    company_guid=ledger.company_guid,
    # ... existing fields ...
    data_source="live",  # ← ADD THIS
)
```

This is technically redundant with the column default, but makes the intent explicit and protects against future default changes.

---

### 7. Frontend: Test Mode Toggle

The dashboard frontend needs a toggle control. Here is the spec:

**Location:** Top navigation bar, right side (next to tenant name/logo)

**States:**

```
LIVE MODE (default):
┌──────────────────────────────────┐
│  🟢 Live    [Switch to Test ▾]  │
└──────────────────────────────────┘

TEST MODE:
┌───────────────────────────────────────────────────────────────┐
│  🟠 Test Mode   Simulation: [Pharma Growing Test ▾]          │
│  [Ingest Data]  [Purge]  [← Back to Live]                    │
└───────────────────────────────────────────────────────────────┘
+ Thin orange border across top of entire page
+ Semi-transparent watermark: "TEST DATA" (rotated, center of page)
```

**API calls the toggle makes:**

1. On mount: `GET /v1/test/mode` → set initial state
2. Clicking "Switch to Test":
   - `GET /v1/test/simulations` → populate dropdown
   - User selects a simulation
   - `POST /v1/test/mode` with `{ mode: "test", simulation_id: X }`
   - All dashboard queries automatically return test data (backend handles filtering)
3. Clicking "Ingest Data":
   - `POST /v1/test/ingest` with `{ simulation_id: X }`
   - Show progress/spinner, then result counts
4. Clicking "Purge":
   - Confirm dialog: "Delete all simulated data for [simulation name]?"
   - `DELETE /v1/test/datasets/{simulation_id}`
5. Clicking "Back to Live":
   - `POST /v1/test/mode` with `{ mode: "live" }`
   - Dashboard immediately shows real data again

**Critical UX rule:** When in test mode, the visual cues (orange border, watermark) must be unmissable. Nobody should ever confuse test data for real client data.

---

## Summary: Files to Change

| File | What to do |
|------|-----------|
| `cloudplatform/db/models.py` | Add `data_source` column to 6 models. Add `TestModeState` model. |
| `cloudplatform/db/database.py` | Add `SIMULATOR_URL` env var. |
| `cloudplatform/db/migrations.py` | Migration to add `data_source` column + index to existing tables. |
| `cloudplatform/api/test_mode.py` | **New file.** All test mode endpoints (toggle, ingest, list, purge, simulation proxy). |
| `cloudplatform/api/ingest.py` | Add `data_source="live"` to all ORM inserts. Add `data_source` filter to `get_stats()` and `query_data()`. |
| `cloudplatform/api/dashboard.py` | Add `data_source` filter to every query (kpis, vouchers, cash-flow, ledgers, sync-health). |
| `cloudplatform/main.py` | Mount the new `test_mode.router`. |
| Frontend | Add test mode toggle component in top nav. |

---

## What NOT to Change

- **Do NOT modify the existing agent ingest flow.** `POST /v1/ledgers`, `/v1/vouchers`, etc. continue to work exactly as before. The agent doesn't know about test mode.
- **Do NOT create a separate database.** Isolation is via the `data_source` column, not separate storage.
- **Do NOT modify the simulator.** It already has all the APIs needed.

---

## Environment Variables

```env
# Add to .env
SIMULATOR_URL=http://<aws-simulator-host>:9001   # Empty = test mode disabled
```

---

## Questions

1. Do you have an Alembic or manual migration setup? The `data_source` column needs a migration for existing tables.
2. Is there a shared query helper or base repository pattern, or are all queries inline in the route handlers? (From what I can see, they're inline — so each endpoint needs the filter added individually.)
3. Is the frontend in a separate repo? If so, which one? The toggle component needs to be built there.
