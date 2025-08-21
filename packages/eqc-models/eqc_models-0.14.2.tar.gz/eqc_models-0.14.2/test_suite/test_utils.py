import numpy as np
import pandas as pd


def get_dirac3_energy(response):
    try:
        if "results" in response and "energies" in response["results"]:
            min_id = np.argmin(response["results"]["energies"])
            energy = response["results"]["energies"][min_id]
        elif "energy" in response:
            min_id = np.argmin(response["energy"])
            energy = response["energy"][min_id]
    except Exception as exc:
        print(exc)
        energy = None

    return energy


def get_dirac3_runtime(response):
    try:
        if "job_info" in response:
            job_resp = response["job_info"]["job_status"]
            running_time = None
            completion_time = None
            runtime = None
            for item in job_resp.keys():
                if "running_at" in item:
                    running_time = pd.to_datetime(job_resp[item])
                elif "completed_at" in item:
                    completion_time = pd.to_datetime(job_resp[item])

            if running_time is not None and completion_time is not None:
                runtime = (completion_time - running_time).total_seconds()

        elif (
            "runtime" in response
            and "preprocessing_time" in response
            and "postprocessing_time" in response
        ):
            runtime = (
                sum(response["runtime"])
                + response["preprocessing_time"]
                + sum(response["postprocessing_time"])
            )
    except Exception as exc:
        print(exc)
        runtime = None

    return runtime
