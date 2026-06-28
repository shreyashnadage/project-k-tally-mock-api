SEASONAL_CURVES: dict[str, dict[int, float]] = {
    "retail": {
        1: 0.85, 2: 0.80, 3: 1.15,  # Jan-Mar: year-end rush in Mar
        4: 0.90, 5: 0.85, 6: 0.80,  # Apr-Jun: slow start
        7: 0.75, 8: 0.80, 9: 0.95,  # Jul-Sep: monsoon dip, Ganesh Chaturthi
        10: 1.40, 11: 1.50, 12: 1.25,  # Oct-Dec: Diwali + year-end
    },
    "manufacturing": {
        1: 0.95, 2: 0.95, 3: 1.10,
        4: 1.00, 5: 1.00, 6: 0.95,
        7: 0.85, 8: 0.90, 9: 1.00,
        10: 1.10, 11: 1.10, 12: 1.05,
    },
    "trading": {
        1: 0.90, 2: 0.85, 3: 1.20,
        4: 0.95, 5: 0.90, 6: 0.85,
        7: 0.80, 8: 0.85, 9: 1.00,
        10: 1.30, 11: 1.35, 12: 1.10,
    },
    "services": {
        1: 0.85, 2: 0.90, 3: 1.15,
        4: 1.05, 5: 1.00, 6: 1.00,
        7: 0.95, 8: 0.95, 9: 1.05,
        10: 1.05, 11: 1.00, 12: 0.85,
    },
    "pharma": {
        1: 0.95, 2: 0.90, 3: 1.00,
        4: 1.00, 5: 1.05, 6: 1.10,
        7: 1.25, 8: 1.20, 9: 1.15,  # monsoon spike
        10: 0.95, 11: 0.90, 12: 0.95,
    },
    "fmcg": {
        1: 0.95, 2: 0.90, 3: 1.05,
        4: 1.00, 5: 1.00, 6: 1.05,
        7: 1.10, 8: 1.05, 9: 1.00,
        10: 1.20, 11: 1.25, 12: 1.05,
    },
}


def get_seasonal_multiplier(month: int, sector: str) -> float:
    curve = SEASONAL_CURVES.get(sector, SEASONAL_CURVES["trading"])
    return curve.get(month, 1.0)
