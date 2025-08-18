
from __future__ import annotations
from typing import Any, Dict, Optional

try:
    from mesa import Agent as MesaAgent, Model as MesaModel
except Exception:  # pragma: no cover
    # Soft fallback so the package imports without Mesa installed.
    class MesaAgent:  # type: ignore
        def __init__(self, unique_id: int, model: Any): 
            self.unique_id = unique_id
            self.model = model
        def step(self): pass

    class MesaModel:  # type: ignore
        def __init__(self): pass
        def step(self): pass

class HeasAgent(MesaAgent):
    """Mixin base for HEAS agents. Override `step()`.

    Provides a tiny metrics dict you can populate.
    """
    def __init__(self, unique_id: int, model: 'HeasModel'):
        super().__init__(unique_id, model)
        self.metrics: Dict[str, Any] = {}

class HeasModel(MesaModel):
    """Mixin base for HEAS models.

    Expose `metrics_step()` and `metrics_episode()` hooks for logging.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.heas_cfg = kwargs
        self._step_idx = 0
        self.metrics_last_step: Dict[str, Any] = {}
        self.metrics_last_episode: Dict[str, Any] = {}

    def step(self):  # to be implemented by subclass
        self._step_idx += 1

    # --- Hooks ---
    def metrics_step(self) -> Dict[str, Any]:
        """Return metrics for the current step (override in your model)."""
        return {}

    def metrics_episode(self) -> Dict[str, Any]:
        """Return end-of-episode metrics (override in your model)."""
        return {}
