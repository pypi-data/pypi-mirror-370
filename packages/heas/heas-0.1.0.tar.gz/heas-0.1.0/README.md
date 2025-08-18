
# HEAS — Hierarchical Evolutionary Agent Simulation

**Version:** 0.1.0 • **Built:** 2025-08-18T05:54:38.112635 UTC

HEAS stitches together **Mesa** (agent-based sims), **DEAP** (evolutionary algorithms),
and **PyTorch** (policies / differentiable bits) through a consistent, typed API.

```bash
pip install .[mesa,deap]
# or: pip install heas  # (after you publish)
```

## One-stop API

```python
from heas import optimize, simulate, evaluate
```

- `simulate()` — run Mesa episodes with rollouts, collect metrics
- `optimize()` — evolve genotypes via DEAP against your Mesa/PyTorch eval
- `evaluate()` — batch score saved genotypes/policies and summarize metrics

See `examples/` for a runnable toy model.
