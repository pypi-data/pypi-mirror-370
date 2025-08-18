
from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple, Callable
import random

try:
    from deap import base, creator, tools
except Exception as e:  # pragma: no cover
    raise ImportError("DEAP not installed. Install with `pip install heas[deap]`.") from e

from ..schemas.genes import Real, Int, Cat, Bool

def _make_individual_from_schema(schema: Sequence[Any]) -> Callable[[], list]:
    # Returns a factory that samples one genotype as a list
    def factory():
        geno = []
        for gene in schema:
            if isinstance(gene, Real):
                lo, hi = gene.low, gene.high
                geno.append(random.uniform(lo, hi))
            elif isinstance(gene, Int):
                geno.append(random.randint(gene.low, gene.high))
            elif isinstance(gene, Cat):
                geno.append(random.choice(gene.choices))
            elif isinstance(gene, Bool):
                geno.append(bool(random.getrandbits(1)))
            else:
                raise TypeError(f"Unsupported gene type: {type(gene)}")
        return geno
    return factory

def build_toolbox(schema: Sequence[Any], fitness_weights: Tuple[float, ...] = (-1.0,)) -> 'base.Toolbox':
    """Create a DEAP toolbox from a HEAS genes schema.

    `fitness_weights` follows DEAP semantics: positive = maximize, negative = minimize
    """
    # Create Fitness/Individual classes (idempotent-ish by name guarding)
    fit_name = "FitnessHEAS"
    ind_name = "IndividualHEAS"
    if not hasattr(creator, fit_name):
        creator.create(fit_name, base.Fitness, weights=fitness_weights)
    if not hasattr(creator, ind_name):
        creator.create(ind_name, list, fitness=getattr(creator, fit_name))

    toolbox = base.Toolbox()
    toolbox.register("individual", tools.initIterate, getattr(creator, ind_name), _make_individual_from_schema(schema))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Variation operators
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.1, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    return toolbox
