
# HEAS — Hierarchical Evolutionary Agent Simulation


```bash
pip install heas 
```

## One-stop API

```python
from heas import optimize, simulate, evaluate
```

- `simulate()` — run Mesa episodes with rollouts, collect metrics
- `optimize()` — evolve genotypes via DEAP against your Mesa/PyTorch eval
- `evaluate()` — batch score saved genotypes/policies and summarize metrics

See `examples/` for a runnable toy model.
