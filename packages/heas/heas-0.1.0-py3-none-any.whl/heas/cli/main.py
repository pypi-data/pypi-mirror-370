
from __future__ import annotations
import argparse, json, importlib, sys
from ..config import Experiment, Algorithm, Evaluation
from ..api import simulate, optimize, evaluate
from ..schemas.genes import Real, Int, Cat, Bool

def _import_object(path: str):
    mod_name, attr = path.split(":")
    mod = importlib.import_module(mod_name)
    return getattr(mod, attr)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="heas", description="Hierarchical Evolutionary Agent Simulation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("run", help="Run Mesa simulation episodes")
    p_sim.add_argument("--factory", required=True, help="Python path to model factory, e.g. examples.simple_model:make_model")
    p_sim.add_argument("--steps", type=int, default=100)
    p_sim.add_argument("--episodes", type=int, default=10)
    p_sim.add_argument("--seed", type=int, default=42)

    p_opt = sub.add_parser("tune", help="Run DEAP-based evolutionary optimization")
    p_opt.add_argument("--objective", required=True, help="Python path to objective(genome)->fitness tuple")
    p_opt.add_argument("--schema", required=True, help="Python path to schema iterable, e.g. examples.simple_model:SCHEMA")
    p_opt.add_argument("--pop", type=int, default=50)
    p_opt.add_argument("--ngen", type=int, default=10)
    p_opt.add_argument("--strategy", default="nsga2", choices=["simple","nsga2","mu_plus_lambda"])
    p_opt.add_argument("--out", default="runs/heas")

    p_eval = sub.add_parser("eval", help="Evaluate saved genotypes with an objective")
    p_eval.add_argument("--objective", required=True)
    p_eval.add_argument("--genotypes", required=True, help="JSON list path of genotypes")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        factory = _import_object(args.factory)
        exp = Experiment(model_factory=factory, steps=args.steps, episodes=args.episodes, seed=args.seed)
        res = simulate(exp)
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "tune":
        objective = _import_object(args.objective)
        schema = _import_object(args.schema)
        exp = Experiment(model_factory=lambda kw: None)  # not used by optimizer directly
        algo = Algorithm(objective_fn=objective, genes_schema=schema, pop_size=args.pop, ngen=args.ngen, out_dir=args.out, strategy=args.strategy)
        res = optimize(exp, algo)
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "eval":
        objective = _import_object(args.objective)
        with open(args.genotypes) as f:
            genos = json.load(f)
        exp = Experiment(model_factory=lambda kw: None)
        eva = Evaluation(genotypes=genos, objective_fn=objective)
        res = evaluate(exp, eva)
        print(json.dumps(res, indent=2))
        return 0

if __name__ == "__main__":
    sys.exit(main())
