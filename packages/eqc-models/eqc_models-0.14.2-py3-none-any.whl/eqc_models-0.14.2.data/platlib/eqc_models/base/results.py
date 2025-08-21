import dataclasses
from typing import Dict
import warnings
import numpy as np

@dataclasses.dataclass
class SolutionResults:
    """
    The class is meant to provide a uniform interface to results, no matter
    the method of running the job. If available, the metrics are reported
    in nanoseconds.

    Properties
    ------------

    solutions : np.ndarray
        2-d array of solution vectors

    energies : np.ndarray
        1-d array of energies computed from the device for each sample

    counts : np.ndarray
        1-d array of counts the particular sample occurred during sampling

    objectives : np.ndarray
        1-d array of objective values. Is None if the model does not provide
        a separate objective function

    run_time : np.ndarray
        1-d array of runtimes reported by the device.

    preprocessing_time : int
        Single value for time spent preprocessing before sampling occurs.

    postprocessing_time : np.ndarray
        1-d array of time spent post-processing samples.

    penalties : np.ndarray
        1-d array of penalty values for each sample. Is None if the model does 
        not have constraints.

    device : str
        String that represents the device used to solve the model.

    raw_solutions : np.ndarray
        Numpy array of the solutions as returned by the solver device.

    calibration_time : float
        Total time spend during job exectution where the device performed calibration.
        The calibration is not directly affected by the job submission and the time
        is not included in run_time.

    time_units : str
        String indicator of the unit of time reported in the metrics. Only
        ns is supported at this time.

    """

    solutions : np.ndarray
    energies : np.ndarray
    counts : np.ndarray
    objectives : np.ndarray
    run_time : np.ndarray
    preprocessing_time : int
    postprocessing_time : np.ndarray
    penalties : np.ndarray = None
    device : str = None
    raw_solutions : np.ndarray = None
    time_units : str = "ns"

    @property
    def device_time(self) -> np.ndarray:
        """ 
        1-d array of device usage computed from preprocessing, runtime
        and postprocessing time.

        """
        if self.run_time:
            pre = self.preprocessing_time
            runtime = np.sum(self.run_time)
            post = np.sum(self.postprocessing_time)
            return pre + runtime + post
        else:
            return None

    @property
    def total_samples(self):
        return np.sum(self.counts)

    @property
    def best_energy(self):
        return np.min(self.energies)

    @classmethod
    def determine_device_type(cls, device_config):
        """ 
        Use the device config object from a cloud response
        to get the device info. It will have a device and job type
        identifiers in it.

        """
        devices = [k for k in device_config.keys()]
        # only one device type is supported at a time
        return devices[0]

    @classmethod
    def from_cloud_response(cls, model, response, solver):
        """ 
        Fill in the details from the cloud 

        Parameters
        ------------

        model : eqc_models.base.EqcModel
            EqcModel object describing the problem solved in response

        response : Dict
            Dictionary of the repsonse from the solver device.

        solver : eqc_models.base.ModelSolver
            ModelSolver object which is used to obtain job metrics.

        """

        solutions = np.array(response["results"]["solutions"])
        if model.machine_slacks > 0:
            solutions = solutions[:,:-model.machine_slacks]
        energies = np.array(response["results"]["energies"])
        # interrogate to determine the device type
        try:
            device_type = cls.determine_device_type(response["job_info"]["job_submission"]["device_config"])
        except KeyError:
            print(response.keys())
            raise
        if "dirac-1" in device_type:
            # decode the qubo
            new_solutions = []
            for solution in solutions:
                solution = np.array(solution)
                # build an operator to map the bit vector to scalar
                base_count = np.floor(np.log2(model.upper_bound))+1
                assert np.sum(base_count) == solution.shape[0], "Incorrect solution-upper bound match"
                m = model.upper_bound.shape[0]
                n = solution.shape[0]
                D = np.zeros((m, n), dtype=np.int32)
                j = 0
                for i in range(m):
                    k = int(base_count[i])
                    D[i, j:j+k] = 2**np.arange(k)
                    j += k
                solution = D@solution 
                new_solutions.append(solution)
            solutions = np.array(new_solutions)
        if hasattr(model, "evaluateObjective"):
            objectives = np.zeros((solutions.shape[0],), dtype=np.float32)
            try:
                objectives[:] = model.evaluateObjective(solutions)
            except NotImplementedError:
                warnings.warn(f"Cannot evaluate objective value in results for {model.__class__}. Method not implemented.")
                objectives = None
            # for i in range(solutions.shape[0]):
            #     try:
            #         objective = model.evaluateObjective(solutions[i])
            #     except NotImplementedError:
            #         warnings.warn(f"Cannot set objective value in results for {model.__class__}")
            #         objectives = None
            #         break
            #     objectives[i] = objective
        else:
            objectives = None
        if hasattr(model, "evaluatePenalties"):
            penalties = np.zeros((solutions.shape[0],), dtype=np.float32)
            for i in range(solutions.shape[0]):
                penalties[i] = model.evaluatePenalties(solutions[i]) + model.offset
        else:
            penalties = None
        counts = np.array(response["results"]["counts"])
        job_id = response["job_info"]["job_id"]
        try:
            metrics = solver.client.get_job_metrics(job_id=job_id)
            metrics = metrics["job_metrics"]
            time_ns = metrics["time_ns"]
            device = time_ns["device"][device_type]
            runtime = device["samples"]["runtime"]
            post = device["samples"].get("postprocessing_time", [0 for t in runtime])
            pre = device["samples"].get("preprocessing_time", 0)
        except KeyError:
            time_ns = []
            runtime = []
            post = []
            pre = None
        results = SolutionResults(solutions, energies, counts, objectives, 
                                  runtime, pre, post, penalties=penalties,
                                  device=device_type, time_units="ns")

        return results

    @classmethod
    def from_eqcdirect_response(cls, model, response, solver):
        """
        Fill in details from the response dictionary and possibly the solver device.

        Parameters
        ------------

        model : eqc_models.base.EqcModel
            EqcModel object describing the problem solved in response

        response : Dict
            Dictionary of the repsonse from the solver device.

        solver : eqc_models.base.ModelSolver
            ModelSolver object which is used to obtain device information. 

        """
        solutions = np.array(response["solution"])
        if model.machine_slacks > 0:
            solutions = solutions[:,:-model.machine_slacks]
        energies = np.array(response["energy"])
        # interrogate to determine the device type
        info_dict = solver.client.system_info()
        device_type = info_dict["device_type"]
        if hasattr(model, "evaluateObjective"):
            objectives = np.zeros((solutions.shape[0],), dtype=np.float32)
            try:
                objectives[:] = model.evaluateObjective(solutions)
            except NotImplementedError:
                warnings.warn(f"Cannot evaluate objective value in results for {model.__class__}. Method not implemented.")
                objectives = None
        else:
            objectives = None
        if hasattr(model, "evaluatePenalties"):
            penalties = np.zeros((solutions.shape[0],), dtype=np.float32)
            for i in range(solutions.shape[0]):
                penalties[i] = model.evaluatePenalties(solutions[i]) + model.offset
        else:
            penalties = None
        counts = np.ones(solutions.shape[0])
        runtime = response["runtime"]
        post = response["postprocessing_time"]
        pre = response["preprocessing_time"]
        results = SolutionResults(solutions, energies, counts, objectives, 
                                  runtime, pre, post, penalties=penalties,
                                  device=device_type, time_units="s")

        return results


