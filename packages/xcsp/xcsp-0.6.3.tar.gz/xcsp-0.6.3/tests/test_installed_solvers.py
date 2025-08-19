import json
import os
import sys
import pytest

from xcsp.solver.solver import Solver, ResultStatusEnum

solvers = list([k for k in Solver.available_solvers().keys() if "picat" not in k.lower()])

# Get all instance files
instances_sat = [
    os.path.join("tests/xcsp3/cop/SAT", instance)
    for instance in os.listdir("tests/xcsp3/cop/SAT")
    if instance.endswith(".xml")
]

instances_unsat = [
    os.path.join("tests/xcsp3/cop/UNSAT", instance)
    for instance in os.listdir("tests/xcsp3/cop/UNSAT")
    if instance.endswith(".xml")
]

instances_unknown = [
    os.path.join("tests/xcsp3/cop/UNKNOWN", instance)
    for instance in os.listdir("tests/xcsp3/cop/UNKNOWN")
    if instance.endswith(".xml")
]


class TestSolver:
    @pytest.mark.parametrize("solver, instance", [
        (solver, instance) for solver in solvers for instance in instances_sat
    ])
    def test_with_xcsp_file_sat(self, solver, instance):

        with open("tests/xcsp3/cop/SAT/solutions.json") as f:
            solutions = json.load(f)
            if solver not in solutions:
                print(f"{solver} is not present in solutions.json file. We skip test.",file=sys.stderr)
                return
            solution_for_current_instance = solutions[solver][instance.split("/")[-1]]
            print(f"Test of ace with input {instance}", file=sys.stderr)
            for index, o in enumerate(solution_for_current_instance["solutions"]):
                solver = Solver.lookup("ace")
                solver.set_limit_number_of_solutions(index + 1)
                solver.solve(instance)
                assert solver.objective_value() is not None
                assert solver.objective_value() == o
                assert solver.status() == ResultStatusEnum.SATISFIABLE
            if solution_for_current_instance["last_is_optimum"]:
                solver = Solver.lookup("ace")
                solver.all_solutions(True)
                solver.solve(instance)
                assert solver.objective_value() is not None
                assert solver.objective_value() == o
                assert solver.status() == ResultStatusEnum.OPTIMUM

    @pytest.mark.parametrize("solver, instance", [
        (solver, instance) for solver in solvers for instance in instances_unsat
    ])
    def test_with_xcsp_file_unsat(self, solver, instance):
        print(f"Test of ace with input {instance}", file=sys.stderr)
        solver = Solver.lookup(solver)
        solver.solve(instance)
        assert solver.objective_value() is None
        assert solver.status() == ResultStatusEnum.UNSATISFIABLE

    @pytest.mark.parametrize("solver, instance", [
        (solver, instance) for solver in solvers for instance in instances_unknown
    ])
    def test_with_xcsp_file_unknown(self, solver, instance):
        print(f"Test of ace with input {instance}", file=sys.stderr)
        solver = Solver.lookup(solver)
        solver.set_time_limit(10)
        solver.solve(instance)
        assert solver.status() == ResultStatusEnum.UNKNOWN
