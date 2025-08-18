
from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple, Callable
import os, json

try:
    from deap import algorithms, tools
except Exception as e:  # pragma: no cover
    raise ImportError("DEAP not installed. Install with `pip install heas[deap]`.") from e

from .toolbox import build_toolbox
from ..utils.io import ensure_dir, save_json
from ..utils.metrics import running_best

def _eval_factory(objective_fn: Callable[[Any], tuple]):
    def _evaluate(individual):
        # Wrap list genotype directly to objective
        return tuple(objective_fn(individual))
    return _evaluate

def run_ea(exp, algo) -> Dict[str, Any]:
    schema = algo.genes_schema
    if not schema:
        raise ValueError("Algorithm.genes_schema is required for optimization.")

    weights = getattr(algo, "fitness_weights", (-1.0,))
    toolbox = build_toolbox(schema, fitness_weights=weights)
    toolbox.register("evaluate", _eval_factory(algo.objective_fn))
    if algo.tournament_k:
        toolbox.register("select", tools.selTournament, tournsize=algo.tournament_k)

    pop = toolbox.population(n=algo.pop_size)
    hof = tools.HallOfFame(5)  # keep top 5

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda fits: sum(fits)/len(fits))
    stats.register("min", min)
    stats.register("max", max)

    log = None
    if algo.strategy == "simple":
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=algo.cx_prob, mutpb=algo.mut_prob, ngen=algo.ngen, stats=stats, halloffame=hof, verbose=True)
    elif algo.strategy == "nsga2":
        pop, log = algorithms.eaMuPlusLambda(pop, toolbox, mu=algo.pop_size, lambda_=algo.pop_size, cxpb=algo.cx_prob, mutpb=algo.mut_prob, ngen=algo.ngen, stats=stats, halloffame=hof, verbose=True)
    elif algo.strategy == "mu_plus_lambda":
        mu = algo.mu or algo.pop_size//2
        lambd = algo.lambd or algo.pop_size
        pop, log = algorithms.eaMuPlusLambda(pop, toolbox, mu=mu, lambda_=lambd, cxpb=algo.cx_prob, mutpb=algo.mut_prob, ngen=algo.ngen, stats=stats, halloffame=hof, verbose=True)
    else:
        raise ValueError(f"Unknown strategy: {algo.strategy}")

    # Serialize results
    ensure_dir(algo.out_dir)
    best = [list(ind) for ind in hof.items]
    out = {
        "best": best,
        "hall_of_fame": best,
        "logbook": [dict(record) for record in (log or [])],
    }
    save_json(os.path.join(algo.out_dir, "result.json"), out)
    return out
