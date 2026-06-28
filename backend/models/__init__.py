from backend.models.company import Company
from backend.models.ledger import Ledger, LedgerGroup
from backend.models.stock import StockGroup, StockItem
from backend.models.voucher import Voucher, VoucherInventoryItem, VoucherLineItem
from backend.models.cost_center import CostCenter
from backend.models.simulation import Simulation
from backend.models.sync_state import AlterIdTracker

__all__ = [
    "Company",
    "LedgerGroup",
    "Ledger",
    "StockGroup",
    "StockItem",
    "Voucher",
    "VoucherLineItem",
    "VoucherInventoryItem",
    "CostCenter",
    "Simulation",
    "AlterIdTracker",
]


def _register_all():
    """Import side-effect: ensures all models are registered with Base.metadata."""
    pass
