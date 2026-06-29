import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { SimulationForm } from './components/SimulationForm';
import { DataPreview } from './components/DataPreview';
import { SimulationList } from './components/SimulationList';
import { StatusPanel } from './components/StatusPanel';
import type { SimulationResult } from './types/simulation';
import './App.css';

const queryClient = new QueryClient();

function AppContent() {
  const [activeSimId, setActiveSimId] = useState<number | null>(null);
  const [lastResult, setLastResult] = useState<SimulationResult | null>(null);

  const handleSimulationCreated = (result: SimulationResult) => {
    setLastResult(result);
    setActiveSimId(result.simulation_id);
    queryClient.invalidateQueries({ queryKey: ['simulations'] });
    queryClient.invalidateQueries({ queryKey: ['health'] });
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Tally Data Simulator</h1>
        <p className="subtitle">Generate realistic MSME financial data for development & testing</p>
      </header>

      <div className="app-layout">
        <aside className="sidebar">
          <StatusPanel />
          <SimulationList
            activeId={activeSimId}
            onSelect={(id) => { setActiveSimId(id); setLastResult(null); }}
          />
        </aside>

        <main className="main-content">
          <SimulationForm onCreated={handleSimulationCreated} />

          {lastResult && (
            <div className="result-banner">
              <h3>Simulation Complete</h3>
              <div className="result-stats">
                <span>{lastResult.ledgers} ledgers</span>
                <span>{lastResult.stock_items} stock items</span>
                <span>{lastResult.vouchers} vouchers</span>
                <span>Sales: &#8377;{lastResult.total_sales.toLocaleString('en-IN')}</span>
                <span>Purchases: &#8377;{lastResult.total_purchases.toLocaleString('en-IN')}</span>
              </div>
            </div>
          )}

          {activeSimId && <DataPreview simId={activeSimId} />}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
