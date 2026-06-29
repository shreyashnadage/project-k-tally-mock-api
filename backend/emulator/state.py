from threading import Lock

_lock = Lock()
_active_simulation_id: int | None = None


def get_active_simulation_id() -> int | None:
    with _lock:
        return _active_simulation_id


def set_active_simulation_id(sim_id: int | None) -> None:
    global _active_simulation_id
    with _lock:
        _active_simulation_id = sim_id
