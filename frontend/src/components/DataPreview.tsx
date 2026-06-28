import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { getLedgers, getMonthlySummary, getStockItems, getVouchers } from '../api/client';

interface Props {
  simId: number;
}

type Tab = 'chart' | 'ledgers' | 'vouchers' | 'stock';

const fmt = (n: number) => new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Math.abs(n));

export function DataPreview({ simId }: Props) {
  const [tab, setTab] = useState<Tab>('chart');
  const [voucherType, setVoucherType] = useState('');
  const [ledgerGroup, setLedgerGroup] = useState('');

  return (
    <div className="data-preview">
      <div className="tabs">
        {(['chart', 'ledgers', 'vouchers', 'stock'] as Tab[]).map((t) => (
          <button key={t} className={`tab ${tab === t ? 'active' : ''}`}
            onClick={() => setTab(t)}>
            {t === 'chart' ? 'Monthly Chart' : t === 'stock' ? 'Stock Items' : t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {tab === 'chart' && <ChartTab simId={simId} />}
        {tab === 'ledgers' && <LedgersTab simId={simId} group={ledgerGroup} onGroupChange={setLedgerGroup} />}
        {tab === 'vouchers' && <VouchersTab simId={simId} voucherType={voucherType} onTypeChange={setVoucherType} />}
        {tab === 'stock' && <StockTab simId={simId} />}
      </div>
    </div>
  );
}

function ChartTab({ simId }: { simId: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['monthly', simId],
    queryFn: () => getMonthlySummary(simId),
  });

  if (isLoading) return <div className="loading">Loading chart...</div>;
  if (!data?.length) return <div className="empty">No data</div>;

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2e3a" />
          <XAxis dataKey="month" stroke="#8b8d98" fontSize={11} />
          <YAxis stroke="#8b8d98" fontSize={11} tickFormatter={(v) => `${(v / 100000).toFixed(0)}L`} />
          <Tooltip
            contentStyle={{ background: '#1a1d27', border: '1px solid #2a2e3a', borderRadius: 8, fontSize: 12 }}
            formatter={(value: number) => [`₹${fmt(value)}`, undefined]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="sales" fill="#6366f1" name="Sales" radius={[4, 4, 0, 0]} />
          <Bar dataKey="purchases" fill="#f59e0b" name="Purchases" radius={[4, 4, 0, 0]} />
          <Bar dataKey="receipts" fill="#22c55e" name="Receipts" radius={[4, 4, 0, 0]} />
          <Bar dataKey="payments" fill="#ef4444" name="Payments" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function LedgersTab({ simId, group, onGroupChange }: { simId: number; group: string; onGroupChange: (g: string) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['ledgers', simId, group],
    queryFn: () => getLedgers(simId, group || undefined),
  });

  if (isLoading) return <div className="loading">Loading...</div>;

  return (
    <>
      <div className="filter-bar">
        <select value={group} onChange={(e) => onGroupChange(e.target.value)}>
          <option value="">All Groups</option>
          <option value="Sundry Debtors">Sundry Debtors</option>
          <option value="Sundry Creditors">Sundry Creditors</option>
          <option value="Bank Accounts">Bank Accounts</option>
          <option value="Duties & Taxes">Duties & Taxes</option>
          <option value="Sales Accounts">Sales Accounts</option>
          <option value="Purchase Accounts">Purchase Accounts</option>
        </select>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th><th>Group</th><th>State</th><th>GSTIN</th>
            <th className="amount">Opening Bal</th><th>Terms</th>
          </tr>
        </thead>
        <tbody>
          {data?.map((l) => (
            <tr key={l.id}>
              <td>{l.name}</td>
              <td>{l.group_name}</td>
              <td>{l.state}</td>
              <td style={{ fontSize: '0.7rem' }}>{l.gst_number}</td>
              <td className={`amount ${l.opening_balance >= 0 ? 'positive' : 'negative'}`}>
                {fmt(l.opening_balance)}
              </td>
              <td>{l.credit_period}d</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!data?.length && <div className="empty">No ledgers found</div>}
    </>
  );
}

function VouchersTab({ simId, voucherType, onTypeChange }: { simId: number; voucherType: string; onTypeChange: (t: string) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['vouchers', simId, voucherType],
    queryFn: () => getVouchers(simId, voucherType || undefined),
  });

  if (isLoading) return <div className="loading">Loading...</div>;

  return (
    <>
      <div className="filter-bar">
        <select value={voucherType} onChange={(e) => onTypeChange(e.target.value)}>
          <option value="">All Types</option>
          <option value="Sales">Sales</option>
          <option value="Purchase">Purchase</option>
          <option value="Receipt">Receipt</option>
          <option value="Payment">Payment</option>
          <option value="Journal">Journal</option>
        </select>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Voucher #</th><th>Type</th><th>Date</th>
            <th>Party</th><th className="amount">Amount</th><th>Narration</th>
          </tr>
        </thead>
        <tbody>
          {data?.map((v) => (
            <tr key={v.id}>
              <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{v.voucher_number}</td>
              <td>{v.voucher_type}</td>
              <td>{v.date}</td>
              <td>{v.party_ledger_name}</td>
              <td className={`amount ${v.amount >= 0 ? 'positive' : 'negative'}`}>
                {fmt(v.amount)}
              </td>
              <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {v.narration}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!data?.length && <div className="empty">No vouchers found</div>}
    </>
  );
}

function StockTab({ simId }: { simId: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['stock', simId],
    queryFn: () => getStockItems(simId),
  });

  if (isLoading) return <div className="loading">Loading...</div>;

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>Name</th><th>Group</th><th>Unit</th><th>HSN</th>
          <th className="amount">Qty</th><th className="amount">Rate</th>
          <th className="amount">Value</th><th>GST %</th>
        </tr>
      </thead>
      <tbody>
        {data?.map((si) => (
          <tr key={si.id}>
            <td>{si.name}</td>
            <td>{si.group_name}</td>
            <td>{si.unit}</td>
            <td>{si.hsn_code}</td>
            <td className="amount">{si.opening_quantity}</td>
            <td className="amount">{fmt(si.opening_rate)}</td>
            <td className="amount">{fmt(si.opening_value)}</td>
            <td>{si.gst_rate}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
