import random
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.models.company import Company
from backend.models.ledger import Ledger
from backend.models.stock import StockItem
from backend.models.voucher import Voucher, VoucherInventoryItem, VoucherLineItem
from backend.simulator.guid_factory import generate_guid
from backend.simulator.schemas import SimulationParams
from backend.simulator.seasonality import get_seasonal_multiplier


def _months_in_range(date_from: date, date_to: date) -> list[tuple[int, int]]:
    months = []
    current = date_from.replace(day=1)
    while current <= date_to:
        months.append((current.year, current.month))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


def _random_date_in_month(year: int, month: int, rng: random.Random) -> date:
    if month == 12:
        last_day = 31
    else:
        next_month = date(year, month + 1, 1)
        last_day = (next_month - timedelta(days=1)).day
    day = rng.randint(1, last_day)
    return date(year, month, day)


def _get_monthly_targets(params: SimulationParams) -> list[tuple[int, int, float]]:
    months = _months_in_range(params.date_from, params.date_to)
    targets = []
    base_revenue = (params.monthly_revenue_min + params.monthly_revenue_max) / 2

    for i, (year, month) in enumerate(months):
        revenue = base_revenue

        if params.enable_seasonality:
            revenue *= get_seasonal_multiplier(month, params.sector)

        if params.growth_trend == "growing":
            growth_factor = 1 + (params.growth_rate_pct / 100) * (i / max(len(months) - 1, 1))
            revenue *= growth_factor
        elif params.growth_trend == "declining":
            decline_factor = 1 - (params.growth_rate_pct / 100) * (i / max(len(months) - 1, 1))
            revenue *= max(decline_factor, 0.3)

        revenue = max(params.monthly_revenue_min, min(revenue, params.monthly_revenue_max))
        targets.append((year, month, round(revenue, 2)))

    return targets


def generate_vouchers(
    company: Company,
    params: SimulationParams,
    ledgers: list[Ledger],
    stock_items: list[StockItem],
    db: Session,
    rng: random.Random,
) -> dict[str, list[Voucher]]:
    seed = str(params.seed or params.company_name)
    customers = [l for l in ledgers if l.group_name == "Sundry Debtors"]
    vendors = [l for l in ledgers if l.group_name == "Sundry Creditors"]

    monthly_targets = _get_monthly_targets(params)

    all_vouchers: dict[str, list[Voucher]] = defaultdict(list)
    voucher_idx = 0
    sales_counter: dict[str, int] = defaultdict(int)
    purchase_counter: dict[str, int] = defaultdict(int)
    receipt_counter: dict[str, int] = defaultdict(int)
    payment_counter: dict[str, int] = defaultdict(int)
    journal_counter: dict[str, int] = defaultdict(int)

    pending_receivables: list[tuple[date, str, float]] = []
    pending_payables: list[tuple[date, str, float]] = []

    for year, month, target_revenue in monthly_targets:
        month_key = f"{year}{month:02d}"

        # --- SALES VOUCHERS ---
        num_sales = max(3, int(target_revenue / (params.monthly_revenue_max / 8)))
        num_credit_sales = int(num_sales * (1 - params.cash_sale_pct / 100))
        num_cash_sales = num_sales - num_credit_sales

        sale_amounts = _split_amount(target_revenue, num_sales, rng)

        for i, sale_amount in enumerate(sale_amounts):
            is_cash = i >= num_credit_sales
            sales_counter[month_key] += 1
            vch_num = f"SL/{month_key}/{sales_counter[month_key]:03d}"
            vch_date = _random_date_in_month(year, month, rng)

            if is_cash:
                party_name = "Cash"
                party_group = "Cash-in-Hand"
            else:
                customer = rng.choice(customers) if customers else None
                party_name = customer.name if customer else "Cash"
                party_group = "Sundry Debtors" if customer else "Cash-in-Hand"

            inv_entries, base_amount = _create_inventory_entries(sale_amount, stock_items, params, rng)
            gst_amount = round(base_amount * params.gst_rate / 100, 2)
            total_with_gst = round(base_amount + gst_amount, 2)

            is_intra_state = True
            if not is_cash and customers:
                cust_obj = next((c for c in customers if c.name == party_name), None)
                if cust_obj:
                    is_intra_state = cust_obj.state == params.state

            voucher = Voucher(
                guid=generate_guid("voucher", voucher_idx, seed),
                company_id=company.id,
                voucher_type="Sales",
                voucher_number=vch_num,
                date=vch_date,
                party_ledger_name=party_name,
                amount=-total_with_gst,  # credit-positive: sales total is negative
                is_invoice=True,
                narration=f"Sales invoice to {party_name}",
                place_of_supply=params.state,
                reference_number=vch_num,
                alter_id=voucher_idx + 1,
            )
            db.add(voucher)
            db.flush()

            # Party debit entry (customer owes us)
            db.add(VoucherLineItem(
                voucher_id=voucher.id,
                ledger_name=party_name,
                amount=-total_with_gst,
                is_deemed_positive=True,
            ))
            # Sales credit entry
            db.add(VoucherLineItem(
                voucher_id=voucher.id,
                ledger_name="Sales Account",
                amount=base_amount,
                is_deemed_positive=False,
            ))
            # GST entries
            if is_intra_state:
                half_gst = round(gst_amount / 2, 2)
                db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="CGST", amount=half_gst, is_deemed_positive=False))
                db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="SGST", amount=round(gst_amount - half_gst, 2), is_deemed_positive=False))
            else:
                db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="IGST", amount=gst_amount, is_deemed_positive=False))

            for ie in inv_entries:
                ie.voucher_id = voucher.id
                db.add(ie)

            all_vouchers["Sales"].append(voucher)
            voucher_idx += 1

            if not is_cash:
                pending_receivables.append((vch_date, party_name, total_with_gst))

        # --- PURCHASE VOUCHERS ---
        purchase_total = round(target_revenue * (1 - params.gross_margin_pct / 100), 2)
        num_purchases = max(2, num_sales // 2)
        purchase_amounts = _split_amount(purchase_total, num_purchases, rng)

        for purchase_amount in purchase_amounts:
            purchase_counter[month_key] += 1
            vch_num = f"PR/{month_key}/{purchase_counter[month_key]:03d}"
            vch_date = _random_date_in_month(year, month, rng)
            vendor = rng.choice(vendors) if vendors else None
            party_name = vendor.name if vendor else "Cash"

            is_intra_state = True
            if vendor:
                is_intra_state = vendor.state == params.state

            inv_entries, base_amount = _create_inventory_entries(purchase_amount, stock_items, params, rng, is_purchase=True)
            gst_amount = round(base_amount * params.gst_rate / 100, 2)
            total_with_gst = round(base_amount + gst_amount, 2)

            voucher = Voucher(
                guid=generate_guid("voucher", voucher_idx, seed),
                company_id=company.id,
                voucher_type="Purchase",
                voucher_number=vch_num,
                date=vch_date,
                party_ledger_name=party_name,
                amount=total_with_gst,
                is_invoice=True,
                narration=f"Purchase from {party_name}",
                place_of_supply=vendor.state if vendor else params.state,
                reference_number=vch_num,
                alter_id=voucher_idx + 1,
            )
            db.add(voucher)
            db.flush()

            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name=party_name, amount=total_with_gst, is_deemed_positive=False))
            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="Purchase Account", amount=-base_amount, is_deemed_positive=True))

            if is_intra_state:
                half_gst = round(gst_amount / 2, 2)
                db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="CGST", amount=-half_gst, is_deemed_positive=True))
                db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="SGST", amount=-round(gst_amount - half_gst, 2), is_deemed_positive=True))
            else:
                db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="IGST", amount=-gst_amount, is_deemed_positive=True))

            for ie in inv_entries:
                ie.voucher_id = voucher.id
                db.add(ie)

            all_vouchers["Purchase"].append(voucher)
            voucher_idx += 1

            if vendor:
                pending_payables.append((vch_date, party_name, total_with_gst))

        # --- RECEIPT VOUCHERS (collections from past sales) ---
        due_receivables = [
            (d, name, amt) for d, name, amt in pending_receivables
            if (date(year, month, 15) - d).days >= params.payment_terms_days
        ]
        for inv_date, party, amount in due_receivables:
            if rng.random() * 100 < params.bad_debt_pct:
                pending_receivables.remove((inv_date, party, amount))
                continue

            delay_days = rng.randint(-5, 15)
            receipt_date = inv_date + timedelta(days=params.payment_terms_days + delay_days)
            if receipt_date > params.date_to:
                continue
            if receipt_date.year != year or receipt_date.month != month:
                continue

            receipt_counter[month_key] += 1
            vch_num = f"RC/{month_key}/{receipt_counter[month_key]:03d}"

            voucher = Voucher(
                guid=generate_guid("voucher", voucher_idx, seed),
                company_id=company.id,
                voucher_type="Receipt",
                voucher_number=vch_num,
                date=receipt_date,
                party_ledger_name=party,
                amount=amount,
                is_invoice=False,
                narration=f"Payment received from {party}",
                alter_id=voucher_idx + 1,
            )
            db.add(voucher)
            db.flush()

            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="HDFC Bank Current A/c", amount=-amount, is_deemed_positive=True))
            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name=party, amount=amount, is_deemed_positive=False))

            all_vouchers["Receipt"].append(voucher)
            voucher_idx += 1
            pending_receivables.remove((inv_date, party, amount))

        # --- PAYMENT VOUCHERS (payments to vendors) ---
        due_payables = [
            (d, name, amt) for d, name, amt in pending_payables
            if (date(year, month, 15) - d).days >= params.payment_terms_days
        ]
        for inv_date, party, amount in due_payables:
            delay_days = rng.randint(-3, 10)
            payment_date = inv_date + timedelta(days=params.payment_terms_days + delay_days)
            if payment_date > params.date_to:
                continue
            if payment_date.year != year or payment_date.month != month:
                continue

            payment_counter[month_key] += 1
            vch_num = f"PM/{month_key}/{payment_counter[month_key]:03d}"

            voucher = Voucher(
                guid=generate_guid("voucher", voucher_idx, seed),
                company_id=company.id,
                voucher_type="Payment",
                voucher_number=vch_num,
                date=payment_date,
                party_ledger_name=party,
                amount=-amount,
                is_invoice=False,
                narration=f"Payment to {party}",
                alter_id=voucher_idx + 1,
            )
            db.add(voucher)
            db.flush()

            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name=party, amount=-amount, is_deemed_positive=True))
            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="HDFC Bank Current A/c", amount=amount, is_deemed_positive=False))

            all_vouchers["Payment"].append(voucher)
            voucher_idx += 1
            pending_payables.remove((inv_date, party, amount))

        # --- JOURNAL VOUCHERS (monthly provisions) ---
        if month in (3, 6, 9, 12):
            journal_counter[month_key] += 1
            vch_num = f"JV/{month_key}/{journal_counter[month_key]:03d}"
            provision_amount = round(target_revenue * 0.02, 2)

            voucher = Voucher(
                guid=generate_guid("voucher", voucher_idx, seed),
                company_id=company.id,
                voucher_type="Journal",
                voucher_number=vch_num,
                date=date(year, month, 28 if month != 2 else 27),
                party_ledger_name="",
                amount=provision_amount,
                is_invoice=False,
                narration="Quarterly provision for expenses",
                alter_id=voucher_idx + 1,
            )
            db.add(voucher)
            db.flush()

            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="Office Expenses", amount=-provision_amount, is_deemed_positive=True))
            db.add(VoucherLineItem(voucher_id=voucher.id, ledger_name="Salary Expense", amount=provision_amount, is_deemed_positive=False))

            all_vouchers["Journal"].append(voucher)
            voucher_idx += 1

    db.flush()
    return dict(all_vouchers)


def _split_amount(total: float, n: int, rng: random.Random) -> list[float]:
    if n <= 0:
        return []
    weights = [rng.random() + 0.3 for _ in range(n)]
    total_weight = sum(weights)
    amounts = [round(total * w / total_weight, 2) for w in weights]
    diff = round(total - sum(amounts), 2)
    amounts[0] = round(amounts[0] + diff, 2)
    return amounts


def _create_inventory_entries(
    target_amount: float,
    stock_items: list[StockItem],
    params: SimulationParams,
    rng: random.Random,
    is_purchase: bool = False,
) -> tuple[list[VoucherInventoryItem], float]:
    if not stock_items:
        return [], target_amount

    num_items = rng.randint(1, min(5, len(stock_items)))
    selected = rng.sample(stock_items, num_items)
    item_amounts = _split_amount(target_amount, num_items, rng)

    entries: list[VoucherInventoryItem] = []
    total_base = 0.0

    for item, amount in zip(selected, item_amounts):
        rate = float(item.opening_rate) * rng.uniform(0.9, 1.1)
        if rate <= 0:
            rate = 100.0
        qty = max(1, round(amount / rate))
        actual_amount = round(qty * rate, 2)
        total_base += actual_amount

        entry = VoucherInventoryItem(
            voucher_id=0,
            stock_item_name=item.name,
            quantity=qty,
            rate=round(rate, 2),
            amount=-actual_amount if not is_purchase else actual_amount,
        )
        entries.append(entry)

    return entries, round(total_base, 2)
