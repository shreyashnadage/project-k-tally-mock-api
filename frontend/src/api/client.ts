import axios from 'axios';
import type {
  LedgerOut,
  MonthlySummary,
  SimulationParams,
  SimulationResult,
  SimulationSummary,
  StockItemOut,
  VoucherOut,
} from '../types/simulation';

const api = axios.create({ baseURL: '/api' });

export async function listSimulations(): Promise<SimulationSummary[]> {
  const { data } = await api.get('/simulations');
  return data;
}

export async function createSimulation(params: SimulationParams): Promise<SimulationResult> {
  const { data } = await api.post('/simulations', params);
  return data;
}

export async function deleteSimulation(id: number): Promise<void> {
  await api.delete(`/simulations/${id}`);
}

export async function getMonthlySummary(simId: number): Promise<MonthlySummary[]> {
  const { data } = await api.get(`/simulations/${simId}/monthly-summary`);
  return data;
}

export async function getLedgers(simId: number, group?: string): Promise<LedgerOut[]> {
  const { data } = await api.get(`/data/${simId}/ledgers`, { params: group ? { group } : {} });
  return data;
}

export async function getVouchers(simId: number, voucherType?: string, month?: string): Promise<VoucherOut[]> {
  const params: Record<string, string> = {};
  if (voucherType) params.voucher_type = voucherType;
  if (month) params.month = month;
  const { data } = await api.get(`/data/${simId}/vouchers`, { params });
  return data;
}

export async function getStockItems(simId: number): Promise<StockItemOut[]> {
  const { data } = await api.get(`/data/${simId}/stock-items`);
  return data;
}

export async function getHealth(): Promise<{ status: string; simulations_count: number }> {
  const { data } = await api.get('/health');
  return data;
}

export interface EmulatorState {
  active_simulation_id: number | null;
  company_name: string | null;
  company_guid: string | null;
  gst_number: string | null;
  financial_year_from: string | null;
  financial_year_to: string | null;
  emulator_port: number;
}

export async function getEmulatorState(): Promise<EmulatorState> {
  const { data } = await api.get('/emulator/state');
  return data;
}

export async function activateEmulator(simulationId: number | null): Promise<void> {
  await api.post('/emulator/activate', { simulation_id: simulationId });
}
