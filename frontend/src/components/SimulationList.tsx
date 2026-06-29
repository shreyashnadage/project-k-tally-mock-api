import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { deleteSimulation, listSimulations } from '../api/client';

interface Props {
  activeId: number | null;
  onSelect: (id: number) => void;
}

export function SimulationList({ activeId, onSelect }: Props) {
  const queryClient = useQueryClient();
  const { data: sims } = useQuery({ queryKey: ['simulations'], queryFn: listSimulations });

  const deleteMut = useMutation({
    mutationFn: deleteSimulation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulations'] });
      queryClient.invalidateQueries({ queryKey: ['health'] });
    },
  });

  if (!sims?.length) {
    return (
      <div className="sim-list">
        <h3>Simulations</h3>
        <p className="empty">No simulations yet</p>
      </div>
    );
  }

  return (
    <div className="sim-list">
      <h3>Simulations</h3>
      {sims.map((s) => (
        <div
          key={s.id}
          className={`sim-item ${activeId === s.id ? 'active' : ''}`}
          onClick={() => onSelect(s.id)}
        >
          <div className="sim-item-header">
            <span className="sim-name">{s.name}</span>
            <button
              className="delete-btn"
              onClick={(e) => { e.stopPropagation(); deleteMut.mutate(s.id); }}
              title="Delete"
            >
              x
            </button>
          </div>
          <div className="sim-meta">
            {s.company_name} &middot; {s.status}
          </div>
        </div>
      ))}
    </div>
  );
}
