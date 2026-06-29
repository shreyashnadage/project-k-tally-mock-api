import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { activateEmulator, getEmulatorState } from '../api/client';
import type { SimulationSummary } from '../types/simulation';

interface Props {
  simulations: SimulationSummary[];
}

export function EmulatorPanel({ simulations }: Props) {
  const queryClient = useQueryClient();

  const { data: state } = useQuery({
    queryKey: ['emulator'],
    queryFn: getEmulatorState,
    refetchInterval: 5000,
  });

  const activateMut = useMutation({
    mutationFn: (simId: number | null) => activateEmulator(simId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['emulator'] }),
  });

  const isActive = !!state?.active_simulation_id;
  const completedSims = simulations.filter((s) => s.status === 'completed');

  return (
    <div className={`emulator-panel ${isActive ? 'emulator-active' : ''}`}>
      <div className="emulator-header">
        <span className={`emulator-dot ${isActive ? 'dot-active' : 'dot-idle'}`} />
        <span className="emulator-title">Tally Emulator</span>
        <span className="emulator-port">:{state?.emulator_port ?? 9000}</span>
      </div>

      {isActive ? (
        <div className="emulator-body">
          <div className="emulator-company">{state!.company_name}</div>
          {state?.gst_number && (
            <div className="emulator-meta">GST: {state.gst_number}</div>
          )}
          {state?.financial_year_from && (
            <div className="emulator-meta">
              FY: {state.financial_year_from?.slice(0, 7)} → {state.financial_year_to?.slice(0, 7)}
            </div>
          )}

          <div className="emulator-env-block">
            <div className="emulator-env-label">Set in your agent .env:</div>
            <code className="emulator-env-code">TALLY_URL=http://localhost:9000</code>
          </div>

          <button
            className="emulator-deactivate-btn"
            onClick={() => activateMut.mutate(null)}
            disabled={activateMut.isPending}
          >
            Deactivate
          </button>
        </div>
      ) : (
        <div className="emulator-body">
          <div className="emulator-idle-msg">
            {completedSims.length === 0
              ? 'Generate a simulation to activate'
              : 'Select a simulation to activate:'}
          </div>
          {completedSims.length > 0 && (
            <div className="emulator-sim-list">
              {completedSims.map((s) => (
                <button
                  key={s.id}
                  className="emulator-sim-btn"
                  onClick={() => activateMut.mutate(s.id)}
                  disabled={activateMut.isPending}
                >
                  <span className="emulator-sim-name">{s.name}</span>
                  <span className="emulator-sim-company">{s.company_name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
