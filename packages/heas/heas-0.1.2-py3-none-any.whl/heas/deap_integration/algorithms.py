from __future__ import annotations
from typing import Any, Dict, Callable, Tuple
import os
import json
import numpy as np

try:
    from deap import algorithms, tools
except Exception as e:  # pragma: no cover
    raise ImportError("DEAP not installed. Install with `pip install heas[deap]`.") from e

from .toolbox import build_toolbox
from ..utils.io import ensure_dir, save_json

def _eval_factory(objective_fn: Callable[[Any], tuple]):
    def _evaluate(individual):
        # Ensure tuple return
        vals = objective_fn(individual)
        if not isinstance(vals, tuple):
            vals = tuple(vals) if hasattr(vals, "__iter__") else (vals,)
        return vals
    return _evaluate

def _make_vector_stats() -> "tools.Statistics":
    """
    Vector-aware reducers for DEAP Statistics.
    Handles 1D (single-objective) and 2D (multi-objective) fitness values.
    """
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)

    def _avg(fits):
        arr = np.array(list(fits), dtype=float)
        if arr.ndim == 1:
            return float(arr.mean())
        return tuple(arr.mean(axis=0).tolist())

    def _vmin(fits):
        arr = np.array(list(fits), dtype=float)
        if arr.ndim == 1:
            return float(arr.min())
        return tuple(arr.min(axis=0).tolist())

    def _vmax(fits):
        arr = np.array(list(fits), dtype=float)
        if arr.ndim == 1:
            return float(arr.max())
        return tuple(arr.max(axis=0).tolist())

    stats.register("avg", _avg)
    stats.register("min", _vmin)
    stats.register("max", _vmax)
    return stats

def run_ea(exp, algo) -> Dict[str, Any]:
    schema = algo.genes_schema
    if not schema:
        raise ValueError("Algorithm.genes_schema is required for optimization.")

    # Fitness weights: positive=maximize, negative=minimize
    weights: Tuple[float, ...] = getattr(algo, "fitness_weights", (-1.0,))

    toolbox = build_toolbox(schema, fitness_weights=weights)
    toolbox.register("evaluate", _eval_factory(algo.objective_fn))

    # Selection strategy
    strategy = getattr(algo, "strategy", "nsga2").lower()
    if strategy == "nsga2":
        toolbox.register("select", tools.selNSGA2)  # Pareto-based
    else:
        # keep whatever build_toolbox set (tournament) for simple / mu+lambda
        pass

    pop = toolbox.population(n=algo.pop_size)

    # Hall of Fame: ParetoFront for multi-objective, best-k for single
    if len(weights) > 1 or strategy == "nsga2":
        hof = tools.ParetoFront()
    else:
        hof = tools.HallOfFame(5)

    stats = _make_vector_stats()

    if strategy == "simple":
        pop, log = algorithms.eaSimple(
            pop, toolbox,
            cxpb=algo.cx_prob, mutpb=algo.mut_prob, ngen=algo.ngen,
            stats=stats, halloffame=hof, verbose=True
        )
    elif strategy in {"nsga2", "mu_plus_lambda"}:
        mu = algo.mu or (algo.pop_size if strategy == "nsga2" else max(2, algo.pop_size // 2))
        lambd = algo.lambd or algo.pop_size
        pop, log = algorithms.eaMuPlusLambda(
            pop, toolbox, mu=mu, lambda_=lambd,
            cxpb=algo.cx_prob, mutpb=algo.mut_prob, ngen=algo.ngen,
            stats=stats, halloffame=hof, verbose=True
        )
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Serialize results
    ensure_dir(algo.out_dir)
    best = [list(ind) for ind in getattr(hof, "items", hof)]
    out = {
        "best": best,
        "hall_of_fame": best,
        "logbook": [dict(record) for record in (log or [])],
    }
    save_json(os.path.join(algo.out_dir, "result.json"), out)
    return out