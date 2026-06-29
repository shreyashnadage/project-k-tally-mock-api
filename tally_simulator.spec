# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Tally Data Simulator.
Run from the project root:
  .venv\Scripts\pyinstaller tally_simulator.spec
"""

import os
from pathlib import Path

ROOT = Path(SPECPATH)

block_cipher = None

a = Analysis(
    [str(ROOT / "backend" / "__main__.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # React build (served as static files by FastAPI)
        (str(ROOT / "frontend" / "dist"), "frontend/dist"),
        # Faker locale data (pure-Python but has JSON/txt data files)
        (str(ROOT / ".venv/Lib/site-packages/faker"), "faker"),
    ],
    hiddenimports=[
        # uvicorn dynamic imports
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.loops.asyncio",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        # SQLAlchemy SQLite dialect
        "sqlalchemy.dialects.sqlite",
        "sqlalchemy.dialects.sqlite.pysqlite",
        # FastAPI / starlette internals
        "starlette.routing",
        "starlette.middleware",
        "starlette.staticfiles",
        "anyio",
        "anyio.from_thread",
        # All backend modules
        "backend",
        "backend.main",
        "backend.config",
        "backend.database",
        "backend.models",
        "backend.models.company",
        "backend.models.ledger",
        "backend.models.voucher",
        "backend.models.stock",
        "backend.models.simulation",
        "backend.models.cost_center",
        "backend.models.sync_state",
        "backend.api",
        "backend.api.simulation_routes",
        "backend.api.data_routes",
        "backend.api.health_routes",
        "backend.api.tdml_routes",
        "backend.api.emulator_routes",
        "backend.simulator",
        "backend.simulator.engine",
        "backend.simulator.ledger_gen",
        "backend.simulator.voucher_gen",
        "backend.simulator.stock_gen",
        "backend.simulator.company_gen",
        "backend.simulator.guid_factory",
        "backend.simulator.schemas",
        "backend.simulator.seasonality",
        "backend.simulator.sector_templates",
        "backend.tdml",
        "backend.tdml.request_parser",
        "backend.tdml.response_builder",
        "backend.tdml.encoding",
        "backend.tdml.exporters",
        "backend.tdml.exporters.company_export",
        "backend.tdml.exporters.ledger_export",
        "backend.tdml.exporters.stock_export",
        "backend.tdml.exporters.voucher_export",
        "backend.emulator",
        "backend.emulator.app",
        "backend.emulator.state",
        "backend.emulator.json_handler",
        "backend.emulator.xml_handler",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "PIL", "pytest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TallySimulator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console so user can see logs and Ctrl+C to stop
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add ICO path here if you have one: icon="installer/icon.ico"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TallySimulator",
)
