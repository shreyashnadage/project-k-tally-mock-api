import random

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.stock import StockGroup, StockItem
from backend.simulator.guid_factory import generate_guid
from backend.simulator.schemas import SimulationParams
from backend.simulator.sector_templates import SectorTemplate


def generate_stock_items(
    company: Company,
    params: SimulationParams,
    template: SectorTemplate,
    db: Session,
    rng: random.Random,
) -> list[StockItem]:
    seed = str(params.seed or params.company_name)

    groups_seen: set[str] = set()
    group_idx = 0
    for p in template.products:
        group_name = f"{params.sector.title()} Products"
        if group_name not in groups_seen:
            sg = StockGroup(
                guid=generate_guid("stock_group", group_idx, seed),
                company_id=company.id,
                name=group_name,
                alter_id=group_idx + 1,
            )
            db.add(sg)
            groups_seen.add(group_name)
            group_idx += 1

    products = list(template.products)
    rng.shuffle(products)
    items: list[StockItem] = []

    for i in range(min(params.product_count, len(products))):
        pt = products[i]
        rate = round(rng.uniform(pt.rate_min, pt.rate_max), 2)
        qty = round(rng.uniform(10, 500), 0)
        item = StockItem(
            guid=generate_guid("stock_item", i, seed),
            company_id=company.id,
            name=pt.name,
            group_name=f"{params.sector.title()} Products",
            unit=pt.unit,
            opening_quantity=qty,
            opening_rate=rate,
            opening_value=round(qty * rate, 2),
            gst_rate=pt.gst_rate,
            hsn_code=pt.hsn_code,
            alter_id=i + 1,
        )
        db.add(item)
        items.append(item)

    db.flush()
    return items
