import { useQuery } from '@tanstack/react-query';
import { getHealth } from '../api/client';

export function StatusPanel() {
  const { data } = useQuery({ queryKey: ['health'], queryFn: getHealth, refetchInterval: 10000 });

  return (
    <div className="status-panel">
      <h3>Server Status</h3>
      <div className="status-item">
        <span><span className={`status-dot ${data ? 'online' : ''}`} />TDML Server</span>
        <span>{data ? 'Online' : '...'}</span>
      </div>
      <div className="status-item">
        <span>Port</span>
        <span>9001</span>
      </div>
      <div className="status-item">
        <span>Simulations</span>
        <span>{data?.simulations_count ?? 0}</span>
      </div>
      <div className="connection-info">
        TALLY_URL=http://localhost:9001
      </div>
    </div>
  );
}
