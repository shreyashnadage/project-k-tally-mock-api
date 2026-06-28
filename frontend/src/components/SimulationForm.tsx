import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import { createSimulation } from '../api/client';
import { DEFAULT_PARAMS, type SimulationParams, type SimulationResult } from '../types/simulation';

interface Props {
  onCreated: (result: SimulationResult) => void;
}

const SECTORS = [
  { value: 'retail', label: 'Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'trading', label: 'Trading' },
  { value: 'services', label: 'IT Services' },
  { value: 'pharma', label: 'Pharma' },
  { value: 'fmcg', label: 'FMCG' },
];

const STATES = [
  'Maharashtra', 'Gujarat', 'Karnataka', 'Tamil Nadu', 'Delhi',
  'Uttar Pradesh', 'Rajasthan', 'West Bengal', 'Telangana', 'Kerala',
];

export function SimulationForm({ onCreated }: Props) {
  const [params, setParams] = useState<SimulationParams>({ ...DEFAULT_PARAMS });
  const [collapsed, setCollapsed] = useState(false);

  const mutation = useMutation({
    mutationFn: createSimulation,
    onSuccess: onCreated,
  });

  const set = <K extends keyof SimulationParams>(key: K, value: SimulationParams[K]) =>
    setParams((p) => ({ ...p, [key]: value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(params);
  };

  return (
    <form className="sim-form" onSubmit={handleSubmit}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: collapsed ? 0 : 20 }}>
        <h2>Configure Simulation</h2>
        <button type="button" className="btn" style={{ padding: '4px 12px', fontSize: '0.75rem' }}
          onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? 'Expand' : 'Collapse'}
        </button>
      </div>

      {!collapsed && (
        <>
          <div className="form-grid">
            <div className="form-group">
              <label>Simulation Name</label>
              <input value={params.name} onChange={(e) => set('name', e.target.value)} />
            </div>

            <div className="form-group">
              <label>Company Name</label>
              <input value={params.company_name} onChange={(e) => set('company_name', e.target.value)} />
            </div>

            <div className="form-group">
              <label>Sector / Industry</label>
              <select value={params.sector} onChange={(e) => set('sector', e.target.value as SimulationParams['sector'])}>
                {SECTORS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Business Size</label>
              <select value={params.business_size} onChange={(e) => set('business_size', e.target.value as SimulationParams['business_size'])}>
                <option value="micro">Micro</option>
                <option value="small">Small</option>
                <option value="medium">Medium</option>
              </select>
            </div>

            <div className="form-group">
              <label>Financial Year Start</label>
              <input type="date" value={params.date_from} onChange={(e) => set('date_from', e.target.value)} />
            </div>

            <div className="form-group">
              <label>Financial Year End</label>
              <input type="date" value={params.date_to} onChange={(e) => set('date_to', e.target.value)} />
            </div>

            <div className="form-group">
              <label>Monthly Revenue Min ({'₹'})</label>
              <input type="number" value={params.monthly_revenue_min}
                onChange={(e) => set('monthly_revenue_min', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Monthly Revenue Max ({'₹'})</label>
              <input type="number" value={params.monthly_revenue_max}
                onChange={(e) => set('monthly_revenue_max', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Customers: {params.customer_count}</label>
              <input type="range" min={1} max={30} value={params.customer_count}
                onChange={(e) => set('customer_count', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Vendors: {params.vendor_count}</label>
              <input type="range" min={1} max={15} value={params.vendor_count}
                onChange={(e) => set('vendor_count', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Products: {params.product_count}</label>
              <input type="range" min={1} max={15} value={params.product_count}
                onChange={(e) => set('product_count', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Payment Terms (days): {params.payment_terms_days}</label>
              <input type="range" min={7} max={120} value={params.payment_terms_days}
                onChange={(e) => set('payment_terms_days', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Bad Debt %: {params.bad_debt_pct}%</label>
              <input type="range" min={0} max={30} step={1} value={params.bad_debt_pct}
                onChange={(e) => set('bad_debt_pct', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Cash Sale %: {params.cash_sale_pct}%</label>
              <input type="range" min={0} max={100} step={5} value={params.cash_sale_pct}
                onChange={(e) => set('cash_sale_pct', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>GST Rate</label>
              <select value={params.gst_rate} onChange={(e) => set('gst_rate', Number(e.target.value))}>
                <option value={0}>0%</option>
                <option value={5}>5%</option>
                <option value={12}>12%</option>
                <option value={18}>18%</option>
                <option value={28}>28%</option>
              </select>
            </div>

            <div className="form-group">
              <label>Gross Margin %: {params.gross_margin_pct}%</label>
              <input type="range" min={5} max={60} step={1} value={params.gross_margin_pct}
                onChange={(e) => set('gross_margin_pct', Number(e.target.value))} />
            </div>

            <div className="form-group">
              <label>Growth Trend</label>
              <select value={params.growth_trend}
                onChange={(e) => set('growth_trend', e.target.value as SimulationParams['growth_trend'])}>
                <option value="flat">Flat</option>
                <option value="growing">Growing</option>
                <option value="declining">Declining</option>
              </select>
            </div>

            {params.growth_trend !== 'flat' && (
              <div className="form-group">
                <label>Growth Rate %: {params.growth_rate_pct}%</label>
                <input type="range" min={1} max={50} value={params.growth_rate_pct}
                  onChange={(e) => set('growth_rate_pct', Number(e.target.value))} />
              </div>
            )}

            <div className="form-group">
              <label>State</label>
              <select value={params.state} onChange={(e) => set('state', e.target.value)}>
                {STATES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div className="form-group checkbox-group">
              <input type="checkbox" checked={params.enable_seasonality}
                onChange={(e) => set('enable_seasonality', e.target.checked)} />
              <label style={{ textTransform: 'none', fontSize: '0.85rem' }}>Enable Seasonality</label>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={mutation.isPending}>
              {mutation.isPending ? 'Generating...' : 'Generate Data'}
            </button>
          </div>

          {mutation.isError && (
            <p style={{ color: 'var(--danger)', marginTop: 12, fontSize: '0.85rem' }}>
              Error: {(mutation.error as Error).message}
            </p>
          )}
        </>
      )}
    </form>
  );
}
