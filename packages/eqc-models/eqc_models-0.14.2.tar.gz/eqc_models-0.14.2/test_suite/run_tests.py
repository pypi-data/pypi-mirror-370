import sys
import os
import json
import logging
import argparse
import unittest
import importlib.util
import pandas as pd

CONFIG_PATH = "test_suite_config.json"


class EqcModelsTester(unittest.TestCase):
    def __init__(
        self,
        config_path,
        problem_list=None,
        problem_type_list=None,            
        max_problem_size=None,
        max_problem_count=None,
        solver_access="cloud",
        ip_addr=None,
        port=None,
    ):
        """A suite of test cases for QCi devices.

        Parameters
        ----------
        config_path: Path to the main configuration file (JSON format).

        problem_list: List of problems to run; default:
        None (run all problems).

        problem_type_list: List of problems types to run; default:
        None (run all problem types).
        
        max_problem_size: Maximum size of the problem to run; default:
        None (run all sizes).

        max_problem_count: Maximum number of problems to run; default:
        None (run problems of all counts).

        solver_access: Solver access type: cloud or direct; default: cloud.

        ip_addr: IP address of the device when direct access is used; default: None.

        port: Port number of the device when direct access is used; default: None.
        """

        try:
            assert (
                max_problem_size is None or max_problem_size >= 1
            ), "Incorrect value!"
            assert (
                max_problem_count is None or max_problem_count >= 1
            ), "Incorrect value!"
        except AssertionError as exc:
            print(exc)
            sys.exit(1)

        self.config_path = config_path
        self.problem_list = problem_list
        self.problem_type_list = problem_type_list
        
        self.max_problem_size = max_problem_size
        if self.max_problem_size is not None:
            self.max_problem_size = int(self.max_problem_size)

        self.max_problem_count = max_problem_count
        if self.max_problem_count is not None:
            self.max_problem_count = int(self.max_problem_count)

        self.solver_access = solver_access
        self.ip_addr = ip_addr
        self.port = port
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )            
        self.logger = logging.getLogger("TestSuiteLogger")
        
    def run(self):
        problem_configs = json.load(open(self.config_path, "r"))

        problems = None
        if self.problem_list is not None:
            problems = self.problem_list.split(",")

        problem_types = None
        if self.problem_type_list is not None:
            problem_types = self.problem_type_list.split(",")            

        out_hash = {
            "problem": [],
            "problem_type": [],            
            "size": [],
            "samples": [],
            "energy": [],
            "merit": [],
            "runtime": [],
            "energy_test": [],
            "merit_test": [],
            "runtime_test": [],
            "overall_score": [],
        }
        count = 0
        for problem_config in problem_configs:
            if (
                problems is not None
                and problem_config["name"] not in problems
            ):
                continue
            if (
                problem_types is not None
                and problem_config["type"] not in problem_types
            ):
                continue            
            if (
                self.max_problem_size is not None
                and problem_config["hamiltonian_size"]
                > self.max_problem_size
            ):
                continue
            if (
                self.max_problem_count is not None
                and count >= self.max_problem_count
            ):
                self.logger.info("Reaching the maximum count of problems!")
                break

            problem_config["solver_access"] = self.solver_access
            problem_config["ip_addr"] = self.ip_addr
            problem_config["port"] = self.port
            
            (
                energy,
                merit,
                runtime,
                energy_test,
                merit_test,
                runtime_test,
            ) = self.run_test(problem_config)

            if (
                energy_test in ["PASS", "PASS+"]
                and merit_test in ["PASS", "PASS+"]
                and runtime_test in ["PASS", "PASS+"]
            ):
                overall_score = "PASS"
            else:
                overall_score = "FAIL"

            out_hash["problem"].append(problem_config["name"])
            out_hash["problem_type"].append(problem_config["type"])            
            out_hash["size"].append(problem_config["hamiltonian_size"])
            out_hash["samples"].append(problem_config["num_samples"])            
            out_hash["energy"].append(energy)
            out_hash["merit"].append(merit)
            out_hash["runtime"].append(runtime)
            out_hash["energy_test"].append(energy_test)
            out_hash["merit_test"].append(merit_test)
            out_hash["runtime_test"].append(runtime_test)
            out_hash["overall_score"].append(overall_score)

        out_df = pd.DataFrame(out_hash)

        return out_df

    def run_test(self, problem_config_dict):
        try:
            assert (
                "problem_source" in problem_config_dict.keys()
            ), "Field not found!"
            assert (
                "expected_merit" in problem_config_dict.keys()
            ), "Field not found!"
            assert (
                "merit_tolerance" in problem_config_dict.keys()
            ), "Field not found!"
            assert (
                "expected_runtime" in problem_config_dict.keys()
            ), "Field not found!"
            assert (
                "runtime_tolerance" in problem_config_dict.keys()
            ), "Field not found!"
        except AssertionError as exc:
            print(exc)
            sys.exit(1)

        self.logger.info("Running %s...", problem_config_dict["name"])

        problem_source = problem_config_dict["problem_source"]
        expected_energy = problem_config_dict["expected_energy"]
        energy_tolerance = problem_config_dict["energy_tolerance"]
        expected_merit = problem_config_dict["expected_merit"]
        merit_tolerance = problem_config_dict["merit_tolerance"]
        expected_runtime = problem_config_dict["expected_runtime"]
        runtime_tolerance = problem_config_dict["runtime_tolerance"]

        spec = importlib.util.spec_from_file_location(
            "loaded_module",
            problem_source,
        )
        loaded_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded_module)

        energy, merit, runtime = loaded_module.run_problem(
            problem_config_dict
        )

        if energy is not None and energy >= 0:
            fct = 1.0
        else:
            fct = -1.0

        if (
            energy is not None
            and energy <= (1.0 + fct * energy_tolerance) * expected_energy
            and energy >= (1.0 - fct * energy_tolerance) * expected_energy
        ):
            energy_test = "PASS"
        elif (
            energy is not None
            and energy < (1.0 - fct * energy_tolerance) * expected_energy
        ):
            energy_test = "PASS+"
        else:
            energy_test = "FAIL"

        if (
            merit is not None
            and merit >= (1.0 - merit_tolerance) * expected_merit
            and merit <= (1.0 + merit_tolerance) * expected_merit
        ):
            merit_test = "PASS"
        elif (
            merit is not None
            and merit > (1.0 + merit_tolerance) * expected_merit
        ):
            merit_test = "PASS+"
        else:
            merit_test = "FAIL"

        if (
            runtime is not None
            and runtime <= (1.0 + runtime_tolerance) * expected_runtime
            and runtime >= (1.0 - runtime_tolerance) * expected_runtime
        ):
            runtime_test = "PASS"
        elif (
            runtime is not None
            and runtime < (1.0 - runtime_tolerance) * expected_runtime
        ):
            runtime_test = "PASS+"
        else:
            runtime_test = "FAIL"

        self.logger.info("Done with %s!", problem_config_dict["name"])

        return (
            energy,
            merit,
            runtime,
            energy_test,
            merit_test,
            runtime_test,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--problem_list",
        type=str,
        required=False,
        help="List of problems to run",
    )
    parser.add_argument(
        "--problem_type_list",
        type=str,
        required=False,
        help="List of problem types to run",
    )    
    parser.add_argument(
        "--max_problem_size",
        type=int,
        required=False,
        help="Maximum size of the problem",
    )
    parser.add_argument(
        "--max_problem_count",
        type=int,
        required=False,
        help="Maximum number of problems to run",
    )
    parser.add_argument(
        "--solver_access",
        type=str,
        required=False,
        help="Solver access method; cloud or direct",
    )
    parser.add_argument(
        "--ip_addr",
        type=str,
        required=False,
        help="IP address for direct solver access",
    )
    parser.add_argument(
        "--port",
        type=str,
        required=False,
        help="Port for direct solver access",
    )
    args = parser.parse_args()

    print(f"Running tests with:")
    print(f"  List of problems: {args.problem_list}")
    print(f"  List of problem types: {args.problem_type_list}")    
    print(f"  Max problem size: {args.max_problem_size}")
    print(f"  Max problem count: {args.max_problem_count}")
    print(f"  Solver access method: {args.solver_access}")
    print(f"  IP address: {args.ip_addr}")
    print(f"  Port: {args.port}")            

    tester = EqcModelsTester(
        config_path=CONFIG_PATH,
        problem_list=args.problem_list,
        problem_type_list=args.problem_type_list,        
        max_problem_size=args.max_problem_size,
        max_problem_count=args.max_problem_count,
        solver_access=args.solver_access,
        ip_addr=args.ip_addr,
        port=args.port,     
    )
    out_df = tester.run()

    print(out_df[["problem", "problem_type", "size", "samples", "energy", "merit", "runtime"]])

    print(
        out_df[
            [
                "problem",
                "problem_type",                
                "energy_test",
                "merit_test",
                "runtime_test",
                "overall_score",
            ]
        ]
    )


if __name__ == "__main__":
    main()
