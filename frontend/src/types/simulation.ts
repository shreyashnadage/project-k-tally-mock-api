export interface SimulationParams {
  name: string;
  company_name: string;
  sector: 'retail' | 'manufacturing' | 'trading' | 'services' | 'pharma' | 'fmcg';
  business_size: 'micro' | 'small' | 'medium';
  date_from: string;
  date_to: string;
  enable_seasonality: boolean;
  monthly_revenue_min: number;
  monthly_revenue_max: number;
  customer_count: number;
  vendor_count: number;
  product_count: number;
  payment_terms_days: number;
  bad_debt_pct: number;
  cash_sale_pct: number;
  gst_rate: number;
  gross_margin_pct: number;
  growth_trend: 'flat' | 'growing' | 'declining';
  growth_rate_pct: number;
  state: string;
  seed?: number;
}

export interface SimulationResult {
  simulation_id: number;
  company_name: string;
  companies: number;
  ledger_groups: number;
  ledgers: number;
  stock_groups: number;
  stock_items: number;
  vouchers: number;
  total_sales: number;
  total_purchases: number;
  total_receipts: number;
  total_payments: number;
}

export interface SimulationSummary {
  id: number;
  name: string;
  status: string;
  company_name: string | null;
  created_at: string;
  completed_at: string | null;
  params: SimulationParams | null;
}

export interface MonthlySummary {
  month: string;
  sales: number;
  purchases: number;
  receipts: number;
  payments: number;
}

export interface LedgerOut {
  id: number;
  name: string;
  group_name: string;
  opening_balance: number;
  closing_balance: number;
  state: string;
  gst_number: string;
  credit_period: number;
}

export interface VoucherOut {
  id: number;
  voucher_type: string;
  voucher_number: string;
  date: string;
  party_ledger_name: string;
  amount: number;
  narration: string;
  is_cancelled: boolean;
}

export interface StockItemOut {
  id: number;
  name: string;
  group_name: string;
  unit: string;
  opening_quantity: number;
  opening_rate: number;
  opening_value: number;
  gst_rate: number;
  hsn_code: string;
}

export const DEFAULT_PARAMS: SimulationParams = {
  name: 'New Simulation',
  company_name: 'Sharma Traders Pvt Ltd',
  sector: 'trading',
  business_size: 'small',
  date_from: '2024-04-01',
  date_to: '2025-03-31',
  enable_seasonality: true,
  monthly_revenue_min: 500000,
  monthly_revenue_max: 2000000,
  customer_count: 20,
  vendor_count: 10,
  product_count: 15,
  payment_terms_days: 30,
  bad_debt_pct: 5,
  cash_sale_pct: 20,
  gst_rate: 18,
  gross_margin_pct: 25,
  growth_trend: 'flat',
  growth_rate_pct: 10,
  state: 'Maharashtra',
};
