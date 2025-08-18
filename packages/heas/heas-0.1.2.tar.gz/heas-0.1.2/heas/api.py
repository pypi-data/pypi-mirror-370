
from __future__ import annotations
from dataclasses import asdict
from typing import Any, Callable, Dict, Iterable, Optional, Tuple

from .config import Experiment, Algorithm, Evaluation
from .utils.rng import seed_everything
from .utils.io import ensure_dir
from .utils.metrics import summarize_metrics

# Lazy imports inside functions to keep optional deps optional
# Mesa integration
# DEAP integration
# Torch integration

def simulate(exp: Experiment) -> Dict[str, Any]:
    """Run one or many Mesa episodes and collect metrics.

    Parameters
    ----------
    exp : Experiment
        Experiment configuration holding the model factory, steps, repeats, etc.
    """
    seed_everything(exp.seed)
    try:
        from .mesa_integration.runner import run_many
    except Exception as e:
        raise RuntimeError("Mesa integration not available. Install extras: heas[mesa].") from e

    results = run_many(
        model_factory=exp.model_factory,
        steps=exp.steps,
        episodes=exp.episodes,
        seed=exp.seed,
        per_step_metrics=exp.per_step_metrics,
        per_episode_metrics=exp.per_episode_metrics,
    )
    return results


def optimize(exp: Experiment, algo: Algorithm) -> Dict[str, Any]:
    """Evolve genotypes using DEAP and your objective function.

    The `algo.objective_fn` should accept a genotype (dict/list/array) and return a tuple
    of fitness values (supporting single/multi-objective)."""
    seed_everything(exp.seed)
    ensure_dir(algo.out_dir)

    try:
        from .deap_integration.algorithms import run_ea
    except Exception as e:
        raise RuntimeError("DEAP integration not available. Install extras: heas[deap].") from e

    return run_ea(exp=exp, algo=algo)


def evaluate(exp: Experiment, eval_cfg: Evaluation) -> Dict[str, Any]:
    """Evaluate a set of genotypes/policies and return summary statistics."""
    seed_everything(exp.seed)
    scores = []
    for g in eval_cfg.genotypes:
        score = eval_cfg.objective_fn(g)
        scores.append(score)
    summary = summarize_metrics(scores)
    return {
        "n": len(scores),
        "summary": summary,
        "raw": scores,
        "config": {
            "experiment": asdict(exp),
            "evaluation": asdict(eval_cfg)
        }
    }
