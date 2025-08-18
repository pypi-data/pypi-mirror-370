from __future__ import annotations
import argparse, json, importlib, importlib.util, os, sys, inspect

from ..config import Experiment, Algorithm, Evaluation
from ..api import simulate, optimize, evaluate

def _import_object(path: str):
    """
    Accepts:
      - 'package.module:attr'
      - '/abs/or/rel/path/to/file.py:attr'
    """
    if ":" not in path:
        raise ValueError("Use 'module:object' or 'path/to/file.py:object'")
    mod_part, attr = path.split(":", 1)

    if mod_part.endswith(".py") or os.path.sep in mod_part or mod_part.startswith("."):
        file_path = os.path.abspath(mod_part)
        spec = importlib.util.spec_from_file_location("heas_user_module", file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules["heas_user_module"] = module
        spec.loader.exec_module(module)
        return getattr(module, attr)
    else:
        mod = importlib.import_module(mod_part)
        return getattr(mod, attr)

def main(argv=None):
    parser = argparse.ArgumentParser(prog="heas", description="Hierarchical Evolutionary Agent Simulation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("run", help="Run simulation episodes with a model factory")
    p_sim.add_argument("--factory", required=True, help="module:obj or path/to/file.py:obj")
    p_sim.add_argument("--steps", type=int, default=100)
    p_sim.add_argument("--episodes", type=int, default=10)
    p_sim.add_argument("--seed", type=int, default=42)

    p_graph = sub.add_parser("run-graph", help="Run a hierarchical graph (spec or CompositeHeasModel)")
    p_graph.add_argument("--graph", required=True, help="module:obj or path/to/file.py:obj (Graph/Spec/CompositeHeasModel)")
    p_graph.add_argument("--steps", type=int, default=100)
    p_graph.add_argument("--episodes", type=int, default=10)
    p_graph.add_argument("--seed", type=int, default=42)

    p_opt = sub.add_parser("tune", help="Run DEAP-based evolutionary optimization")
    p_opt.add_argument("--objective", required=True, help="module:obj or path/to/file.py:obj")
    p_opt.add_argument("--schema", required=True, help="module:obj or path/to/file.py:obj")
    p_opt.add_argument("--pop", type=int, default=50)
    p_opt.add_argument("--ngen", type=int, default=10)
    p_opt.add_argument("--strategy", default="nsga2", choices=["simple","nsga2","mu_plus_lambda"])
    p_opt.add_argument("--out", default="runs/heas")

    p_eval = sub.add_parser("eval", help="Evaluate saved genotypes with an objective")
    p_eval.add_argument("--objective", required=True, help="module:obj or path/to/file.py:obj")
    p_eval.add_argument("--genotypes", required=True, help="JSON list path of genotypes")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        factory = _import_object(args.factory)
        exp = Experiment(model_factory=factory, steps=args.steps, episodes=args.episodes, seed=args.seed)
        res = simulate(exp)
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "run-graph":
        obj = _import_object(args.graph)
        model_factory = _coerce_model_factory_from_obj(obj, args.seed)

        exp = Experiment(model_factory=model_factory, steps=args.steps, episodes=args.episodes, seed=args.seed)
        res = simulate(exp)
        print(json.dumps(res, indent=2))
        return 0

    if args.cmd == "tune":
        objective = _import_object(args.objective)
        schema = _import_object(args.schema)
        exp = Experiment(model_factory=lambda kw: None)
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

def _coerce_model_factory_from_obj(obj, default_seed):
    """Return a model_factory(kwargs) from many accepted inputs."""
    from ..hierarchy import CompositeHeasModel, Graph, make_model_from_spec

    # 1) Already a CompositeHeasModel instance
    if isinstance(obj, CompositeHeasModel):
        return lambda kw: obj

    # 2) A Graph instance -> wrap
    if isinstance(obj, Graph):
        return lambda kw: CompositeHeasModel(obj, seed=kw.get("seed", default_seed))

    # 3) A Spec (list[LayerSpec]) -> build via make_model_from_spec
    if isinstance(obj, list) and all(hasattr(x, "streams") for x in obj):
        def _mf(kw):
            return make_model_from_spec(obj, seed=kw.get("seed", default_seed))({})
        return _mf

    # 4) Callable cases:
    if callable(obj):
        try:
            sig = inspect.signature(obj)
            # 4a) Zero-arg callable -> call it, then recurse on the returned object
            if len(sig.parameters) == 0:
                returned = obj()
                return _coerce_model_factory_from_obj(returned, default_seed)
            # 4b) Callable expecting kwargs -> assume it's a HEAS model_factory(kwargs)
            else:
                return obj
        except Exception:
            # Be conservative: treat as model_factory
            return obj

    raise TypeError("Unsupported --graph object. Provide CompositeHeasModel, Graph, a list[LayerSpec], or a model_factory(kwargs).")

if __name__ == "__main__":
    sys.exit(main())