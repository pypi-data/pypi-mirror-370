
"""
Command-line interface for Robin Logistics Environment.
Supports both headless execution and dashboard modes.
"""

import argparse
import importlib.util
import sys
import os
from typing import Callable, Optional
from .headless import HeadlessRunner

def load_solver_from_file(file_path: str, function_name: str = "my_solver") -> Callable:
    """
    Load a solver function from a Python file.

    Args:
        file_path: Path to Python file containing solver
        function_name: Name of the solver function (default: "my_solver")

    Returns:
        Solver function
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Solver file not found: {file_path}")

    spec = importlib.util.spec_from_file_location("solver_module", file_path)
    solver_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver_module)

    if not hasattr(solver_module, function_name):
        raise AttributeError(f"Function '{function_name}' not found in {file_path}")

    return getattr(solver_module, function_name)

def run_headless_mode(args):
    """Run solver in headless mode."""
    print("Robin Logistics - Headless Mode")

    if args.solver_file:
        solver_function = load_solver_from_file(args.solver_file, args.solver_function)
        solver_name = os.path.splitext(os.path.basename(args.solver_file))[0]
    else:
        from .solvers import test_solver
        solver_function = test_solver
        solver_name = "demo_solver"

    config = None
    if args.config_file:
        import json
        with open(args.config_file, 'r') as f:
            config = json.load(f)

    runner = HeadlessRunner(config, args.output_dir)

    results = runner.run_solver(
        solver_function,
        solver_name,
        args.run_id
    )

    return results

def run_dashboard_mode(args):
    """Run dashboard mode."""
    print("Robin Logistics - Dashboard Mode")

    solver_function = None
    if args.solver_file:
        solver_function = load_solver_from_file(args.solver_file, args.solver_function)

    from .dashboard import run_dashboard
    from .environment import LogisticsEnvironment

    env = LogisticsEnvironment()
    run_dashboard(env, solver_function)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Robin Logistics Environment - Multi-depot vehicle routing problem solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m robin_logistics.cli --headless

  python -m robin_logistics.cli --headless --solver my_solver.py

  python -m robin_logistics.cli --headless --solver my_solver.py --config config.json

  python -m robin_logistics.cli --dashboard --solver my_solver.py

  python -m robin_logistics.cli
        """
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no GUI, save results to files)'
    )
    mode_group.add_argument(
        '--dashboard',
        action='store_true',
        help='Run dashboard mode (default)'
    )

    parser.add_argument(
        '--solver',
        dest='solver_file',
        help='Path to Python file containing solver function'
    )
    parser.add_argument(
        '--solver-function',
        default='my_solver',
        help='Name of solver function in file (default: my_solver)'
    )

    parser.add_argument(
        '--output',
        dest='output_dir',
        default='results',
        help='Output directory for headless mode (default: results)'
    )
    parser.add_argument(
        '--run-id',
        help='Custom run identifier for result files'
    )
    parser.add_argument(
        '--config',
        dest='config_file',
        help='JSON configuration file for environment setup'
    )

    args = parser.parse_args()

    if not args.headless and not args.dashboard:
        args.dashboard = True

    try:
        if args.headless:
            return run_headless_mode(args)
        else:
            return run_dashboard_mode(args)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
