# (C) Quantum Computing Inc., 2024.
from typing import Dict, List, Tuple
import logging
import datetime
import numpy as np
from qci_client import QciClient
from eqc_models.base.base import ModelSolver, EqcModel
from eqc_models.base.operators import OperatorNotAvailableError
from eqc_models.base.results import SolutionResults

log = logging.getLogger(name=__name__)

class QciClientMixin:
    """
    This class provides an instance method and property that manage the connection to
    the REST API.

    Methods
    -------

    connect

    Properties
    ----------

    client : QciClient

    """

    url = None
    api_token = None

    def connect(self, url: str = None, api_token: str = None):
        """
        Use this method to define connection parameters manually. Returns the string "SUCCESS"
        on a successful connection, raises an a RuntimeError on failure.

        Parameters
        --------------

        url: The URL used to connect to the Dirac machine.
        
        api_token: Authentication token.
        
        """
        self.url = url
        self.api_token = api_token
        client = self.client
        if client is None:
            raise RuntimeError("Failed to connect to Qatalyst service")
        return "SUCCESS"

    @property
    def client(self) -> QciClient:
        """
        Returns a new client object every time. If the connection was not
        configured in code, then QciClient attempts to use environment variables
        to connect to the service

        """
        # pull from environment variables if the class variables are not set
        if self.url is None and self.api_token is None:
            log.debug(
                "Getting QciClient connection using environment variables"
            )
            client = QciClient()
        else:
            log.debug("Getting QciClient connection using class variables")
            client = QciClient(url=self.url, api_token=self.api_token)
        return client

    def getMetrics(self, job_id : str) -> Dict:
        """
        Returns a dictionary containing the job metrics.

        """
        client = self.client
        metrics = client.get_job_metrics(job_id=job_id)
        return metrics

    def makeResults(self, model : EqcModel, response : Dict) -> SolutionResults:
        """ Build the results object """

        return SolutionResults.from_cloud_response(model, response, self)

class Dirac1Mixin:
    sampler_type = "dirac-1"
    requires_operator = "qubo"
    max_upper_bound = 205 # log encoding beyond this level has inherent issues
    job_params_names = ["num_samples", "alpha", "atol"]

class QuboSolverMixin:
    job_type = "qubo"

    def uploadJobFiles(self, client:QciClient, model:EqcModel):
        """ 
        This method retrieves a QUBO representation from the model's 
        :code:`qubo` property and uploads it, returning :code:`qubo_file_id`
        for submission with a job request.

        Parameters
        --------------

        client: The QciClient instance.

        model: The EqcModel instance.
        
        """

        # C, J = model.H
        # Q = J + np.diag(C)
        Q = model.qubo.Q
        qubo_file = {
            "file_name": f"{model.__class__.__name__}-qubo",
            "file_config": {
                "qubo": {"data": Q, "num_variables": Q.shape[0]}
            },
        }
        qubo_file_id = client.upload_file(file=qubo_file)["file_id"]
        return {"qubo_file_id": qubo_file_id}

class Dirac3Mixin:
    """
    Defines the specifics required for using Dirac-3 as the sampler 

    """

    sampler_type = "dirac-3"
    requires_operator = "polynomial"
    # this restriction is based on the physical limit of Dirac-3 S1
    max_upper_bound = 10000
    job_params_names = [
        "num_samples",
        "relaxation_schedule",
        "mean_photon_number",
        "quantum_fluctuation_coefficient",
    ]

    def uploadJobFiles(self, client: QciClient, model: EqcModel):
        """
        Upload a Hamiltonian in polynomial format.

        Parameters
        --------------

        client: The QciClient instance.

        model: The EqcModel instance.

        """

        # poly_coeffs, poly_indices = model.sparse
        polynomial = model.polynomial
        poly_coeffs = polynomial.coefficients
        poly_indices = polynomial.indices
        data = []
        # must find these attributes of the polynomial before uploading
        max_degree = 2
        min_degree = len(poly_indices[-1])
        num_variables = 0
        for i in range(len(poly_coeffs)):
            idx = 0
            if num_variables < max(poly_indices[i]):
                num_variables = max(poly_indices[i])
            while max_degree < len(poly_indices[i]) and idx < len(
                poly_indices[i]
            ):
                if (
                    poly_indices[i][idx] > 0
                    and max_degree < len(poly_indices[i]) - idx
                ):
                    max_degree = len(poly_indices[i]) - idx
                    idx += len(poly_indices[i])
                else:
                    idx += 1
            idx = len(poly_indices[i]) - 1
            while min_degree > 1 and idx > 0:
                if (
                    poly_indices[i][idx] > 0
                    and min_degree > len(poly_indices[i]) - idx
                ):
                    min_degree = len(poly_indices[i]) - idx
                    idx = 0
                else:
                    idx -= 1
            data.append(
                {
                    "idx": poly_indices[i],
                    "val": float(poly_coeffs[i]),
                }
            )
        log.debug("Min degree of polynomial %d", min_degree)
        log.debug("Max degree of polynomial %d", max_degree)
        log.debug("Number of polynomial elements %d", len(poly_coeffs))
        polynomial = {
            "file_name": f"{model.__class__.__name__}",
            "file_config": {
                "polynomial": {
                    "num_variables": int(num_variables)
                    + model.machine_slacks,
                    "max_degree": max_degree,
                    "min_degree": min_degree,
                    "data": data,
                }
            },
        }
        log.debug(polynomial)
        file_id = client.upload_file(file=polynomial)["file_id"]
        log.debug("Upload polynomial file produced file id %s", file_id)
        return {"polynomial_file_id": file_id}

class QciClientSolver(QciClientMixin, ModelSolver):
    """
    Parameters 
    -----------

    url : string
        optional value specifying the QCi API URL
    api_token : string
        optional value specifying the authentication token for the QCi API

    QCi API client wrapper for solving an EQC model. This class provides the 
    common method for uploading a file to the API for solving. Since the file
    types change for the job types, the specific files required for the job are
    specified in subclasses within the `uploadFiles` method.

    """

    def __init__(self, url=None, api_token=None):
        self.url = url
        self.api_token = api_token

    @staticmethod
    def uploadFile(
        file_data: np.ndarray,
        file_name: str = None,
        file_type: str = None,
        client: QciClient = None,
    ) -> str:
        """
        Upload the operator file, return the file ID.

        Parameters
        --------------

        file_data: numpy array, dictionary or list 
            contains file data to be uploaded

        file_name: str
            Name of the file to be uploaded.

        file_type: str
            Type of the file to be uploaded.

        client: QciClient
            QciClient instance

        """

        n = file_data.shape[0]
        log.debug("Uploading %s file of %d variables", file_type, n)
        if client is None:
            log.debug("Retrieving instance client")
            client = self.client
        file_obj = {"file_config": {file_type: {"data": file_data}}}
        if file_type in (
            "constraints",
            "hamiltonian",
            "qubo",
            "objective",
        ):
            file_obj["file_config"][file_type]["num_variables"] = n
        # print(ham_file)
        if file_name is None:
            ts = datetime.datetime.now().timestamp()
            file_name = f"{file_type}{n}-{ts}"
        log.debug("Using file name %s", file_name)
        file_obj["file_name"] = file_name
        file_id = client.upload_file(file=file_obj)["file_id"]
        return file_id

    def uploadJobFiles(self, client: QciClient, model: EqcModel):
        raise NotImplementedError("Subclass must override uploadJobFiles")

    def checkModel(self, model):
        """
        Parameters
        -------------

        model: EqcModel
            Instance of a model to validate against the solver requirements

        This method raises an exception if the model supplied does not meet the requirements for the solver.
        One of the validations is that the model supplies the operator that the solver uses. This is the
        `qubo` operator for Dirac-1 and `polynomial` operator for Dirac-3. If the model does not supply 
        the operator, then the solver cannot accept it and the method will fail with an explanation. 
        Another validation is for the allowed upper bound of a model. For instance, solvers which only 
        handle binary variables can only accept models with variabes having an upper bound of 1.

        """
        try:
            hasattr(model, self.requires_operator)
        except OperatorNotAvailableError:
            msg = (f"Class {model.__class__.__name__} does not provide a " 
                   f"{self.requires_operator} operator")
            raise ValueError(msg)
        if np.max(model.upper_bound) > self.max_upper_bound:
            msg = (f"Instance of {model.__class__.__name__} has greater "
                   f"upper bound on variables than {self.__class__.__name__} "
                   "supports")
            raise ValueError(msg)

    def solve(
        self,
        model: EqcModel,
        name: str = None,
        tags: List = None,
        num_samples: int = 1,
        wait=True,
        job_type=None,
        **job_kwargs,
    ) -> Dict:
        """
        Parameters
        --------------

        model: EqcModel 
            Instance of a model for solving.
        
        name: str
            Name of the job; default is None.
        
        tags: list
            A list of job tags; default is None.
        
        num_samples: int
            Number of samples used; default is 1.
        
        wait: bool
            The wait flag indicating whether to wait for the job to complete
            before returning the complete job data otherwise return a job ID 
            as soon as a job is submitted; default is True.
        
        job_type: str
            Type of the job; default is None. When None, it is constructed 
            from the instance `job_type` property.

        Returns
        ----------
        job response dictionary
        
        This method takes the particulars of the instance model and handles
        the QciClient.solve call.
 
        """

        self.checkModel(model)
        job_config = {}
        job_config.update(
            {"num_samples": num_samples, "device_type": self.sampler_type}
        )
        # set the job parameters
        for name in self.job_params_names:
            if name in job_kwargs:
                job_config[name] = job_kwargs.pop(name)
            elif hasattr(model, name):
                job_config[name] = getattr(model, name)
        leftovers = ",".join(job_kwargs.keys())
        if leftovers:
            raise ValueError(
                f"Unused job parameters given to solve method: {leftovers}"
            )
        # prep files in the API
        client = self.client
        job_files = self.uploadJobFiles(client, model)
        log.debug(f"Building job body: {job_config}")
        if job_type is None:
            job_type = f"sample-{self.job_type}"
        job_body = client.build_job_body(
            job_type=job_type,
            job_params=job_config,
            job_tags=tags,
            **job_files,
        )
        response = client.process_job(job_body=job_body, wait=wait)
        return response

    def getResults(self, response: Dict) -> Dict[str, List]:
        """
        Extract the results from response.

        Parameters
        --------------
        response: The responce from QciClient.

        Returns
        --------------
        The results json object.
        
        """

        results = response["results"]
        log.debug("Got results object: %s", results)
        return results

# Some example usage
class Dirac1CloudSolver(Dirac1Mixin, QuboSolverMixin, QciClientSolver):
    """
    Overview
    ---------
    Dirac1CloudSolver is a class that encapsulates the different calls to Qatalyst
    for Dirac-1 jobs, which are quadratic binary optimization problems.

    Examples
    -------------------

    >>> C = np.array([[-1], [-1]])
    >>> J = np.array([[0, 1.0], [1.0, 0]])
    >>> from eqc_models.base.quadratic import QuadraticModel
    >>> model = QuadraticModel(C, J)
    >>> model.upper_bound = np.array([1, 1]) # set the domain maximum per variable
    >>> solver = Dirac1CloudSolver()
    >>> response = solver.solve(model, num_samples=5) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    2... submitted... COMPLETED...
    >>> response["results"]["energies"][0] <= 1.0
    True
    """

class Dirac3CloudSolver(Dirac3Mixin, QciClientSolver):
    """
    
    Dirac3CloudSolver is a class that encapsulates the different calls to Qatalyst
    for Dirac-3 jobs. Currently, there are two different jobs, one for integer and
    another for continuous solutions. Calling the solve method with different arguments
    controls which job is submitted. The continuous job requires :code:`sum_constraint`.
    The integer job does not accept this parameter, so specifying a sum constraint forces
    the job type to be continuous, and not specifying it results in the integer job being
    called.

    Continuous Solver
    -------------------

    Utilizing Dirac-3 as a continuous solver involves encoding the variables in single time bins
    with the values of each determined by a normalized photon count value.

    Integer Solver
    -------------------

    Utilizing Dirac-3 as an integer solver involves encoding the variables in multiple time bins,
    each representing a certain value for that variable, or "qudit".

    Examples
    -------------------

    >>> C = np.array([[1], [1]])
    >>> J = np.array([[-1.0, 0], [0, -1.0]])
    >>> from eqc_models.base.quadratic import QuadraticModel
    >>> model = QuadraticModel(C, J)
    >>> model.upper_bound = np.array([1, 1]) # set the domain maximum per variable
    >>> solver = Dirac3CloudSolver()
    >>> response = solver.solve(model, sum_constraint=1, relaxation_schedule=1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    2... submitted... COMPLETED...
    >>> response["results"]["energies"][0] <= 1.0
    True
    >>> C = np.array([-1, -1], dtype=np.float32)
    >>> J = np.array([[0, 1], [1, 0]], dtype=np.float32)
    >>> model = QuadraticModel(C, J)
    >>> model.upper_bound = np.array([1, 1]) # set the domain maximum per variable
    >>> response = solver.solve(model, relaxation_schedule=1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    2... submitted... COMPLETED...
    >>> response["results"]["energies"][0] == -1.0
    True
    """

    job_type = "hamiltonian"
    job_params_names = Dirac3Mixin.job_params_names + ["num_levels", "sum_constraint"]

    def solve(
        self,
        model: EqcModel,
        name: str = None,
        tags: List = None,
        sum_constraint: float = None,
        relaxation_schedule: int = None,
        num_samples: int = 1,
        wait: bool = True,
        mean_photon_number: float = None,
        quantum_fluctuation_coefficient: int = None,
        **job_kwargs,
    ):
        """
        Parameters
        --------------

        model: EqcModel 
            a model object which supplies a hamiltonian operator for the 
            device to sample. Must support the polynomial operator property.
        tags: List 
            a list of strings to save with the job
        sum_constraint : float 
            a value which applies a constraint to the solution, forcing
            all variables to sum to this value, changes method to continuous
            solver
        relaxation_schedule : int 
            a predefined schedule indicator which sets parameters
            on the device to control the sampling through photon 
            measurement
        num_samples : int 
            the number of samples to take, defaults to 1
        wait : bool 
            a flag for waiting for the response or letting it run asynchronously.
            Asynchronous runs must retrieve results directly using qci-client and
            the job_id.
        mean_photon_number : float 
            an optional decimal value which sets the average number 
            of photons that are present in a given quantum state.
            Modify this value to control the relaxation schedule more
            precisely than the four presets given in schedules 1
            through 4. Allowed values are decimals between 0.000133333333333 and 
            0.001.
        quantum_fluctuation_coefficient: int 
            an integer value which Sets the amount of loss introduced
            into the system for each loop during the measurement process.
            Modify this value to control the relaxation schedule more
            precisely than the four presets given in schedules 1
            through 4. Allowed values range from 1 to 50.

        """
        # choose integer or continuous solver
        continuous = sum_constraint is not None
        if continuous:
            job_kwargs["sum_constraint"] = sum_constraint
            if relaxation_schedule not in (1, 2, 3, 4):
                raise ValueError(
                    "relaxation_schedule must be one of 1, 2, 3 or 4"
                )
            job_kwargs["relaxation_schedule"] = relaxation_schedule
            job_kwargs["mean_photon_number"] = mean_photon_number
            job_kwargs["quantum_fluctuation_coefficient"] = quantum_fluctuation_coefficient
            job_type = "sample-" + self.job_type
            return super().solve(
                model,
                name,
                tags=tags,
                num_samples=num_samples,
                wait=wait,
                job_type=job_type,
                **job_kwargs,
            )

        else:
            job_kwargs["mean_photon_number"] = mean_photon_number
            job_kwargs["quantum_fluctuation_coefficient"] = quantum_fluctuation_coefficient
            job_kwargs["relaxation_schedule"] = relaxation_schedule
            job_kwargs["num_levels"] = ub = [val + 1 for val in model.upper_bound.tolist()]
            job_type = "sample-" + self.job_type + "-integer"
            return super().solve(
                model,
                name,
                tags=tags,
                num_samples=num_samples,
                wait=wait,
                job_type=job_type,
                **job_kwargs,
            )

class Dirac3IntegerCloudSolver(Dirac3Mixin, QciClientSolver):
    """
    
    >>> C = np.array([-1, -1], dtype=np.float32)
    >>> J = np.array([[0, 1], [1, 0]], dtype=np.float32)
    >>> from eqc_models.base.quadratic import QuadraticModel
    >>> model = QuadraticModel(C, J)
    >>> model.upper_bound = np.array([1, 1]) # set the domain maximum per variable
    >>> solver = Dirac3IntegerCloudSolver()
    >>> model = QuadraticModel(C, J)
    >>> model.upper_bound = np.array([1, 1]) # set the domain maximum per variable
    >>> response = solver.solve(model, relaxation_schedule=1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    2... submitted... COMPLETED...
    >>> response["results"]["energies"][0] == -1.0
    True

    """
    job_type = "hamiltonian-integer"
    job_params_names = Dirac3Mixin.job_params_names + ["num_levels"]

    def solve(self, 
              model : EqcModel,     
              name: str = None,
              tags: List = None,
              relaxation_schedule: int = None,
              num_samples: int = 1,
              wait: bool = True,
              mean_photon_number: float = None,
              quantum_fluctuation_coefficient: int = None,
              **job_kwargs,
              ):
        """
        Parameters
        --------------

        model: EqcModel 
            a model object which supplies a hamiltonian operator for the 
            device to sample. Must support the polynomial operator property.
        tags: List 
            a list of strings to save with the job
        relaxation_schedule : int 
            a predefined schedule indicator which sets parameters
            on the device to control the sampling through photon 
            measurement
        num_samples : int 
            the number of samples to take, defaults to 1
        wait : bool 
            a flag for waiting for the response or letting it run asynchronously.
            Asynchronous runs must retrieve results directly using qci-client and
            the job_id.
        mean_photon_number : float 
            an optional decimal value which sets the average number 
            of photons that are present in a given quantum state.
            Modify this value to control the relaxation schedule more
            precisely than the four presets given in schedules 1
            through 4. Allowed values are decimals between 0.000133333333333 
            and 0.001.
        quantum_fluctuation_coefficient: int 
            an integer value which Sets the amount of loss introduced
            into the system for each loop during the measurement process.
            Modify this value to control the relaxation schedule more
            precisely than the four presets given in schedules 1
            through 4. Allowed values range from 1 to 50.


        Dirac3IntegerCloudSolver is a class that encapsulates the different calls to 
        Qatalyst for Dirac-3 jobs. Utilizing Dirac-3 as an integer solver involves 
        encoding the variables in multiple time bins, each representing a certain 
        value for that variable, or "qudit".


        """
        return super().solve(
            model,
            name,
            tags=tags,
            num_samples=num_samples,
            wait=wait,
            mean_photon_number=mean_photon_number,
            quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
            relaxation_schedule=relaxation_schedule,
            num_levels=[val + 1 for val in model.upper_bound.tolist()],
            **job_kwargs,
        )


class Dirac3ContinuousCloudSolver(Dirac3Mixin, QciClientSolver):
    """

    >>> C = np.array([[1], [1]])
    >>> J = np.array([[-1.0, 0], [0, -1.0]])
    >>> from eqc_models.base.quadratic import QuadraticModel
    >>> model = QuadraticModel(C, J)
    >>> model.upper_bound = np.array([1, 1]) # set the domain maximum per variable
    >>> solver = Dirac3ContinuousCloudSolver()
    >>> response = solver.solve(model, sum_constraint=1, relaxation_schedule=1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    2... submitted... COMPLETED...
    >>> response["results"]["energies"][0] <= 1.0
    True

    """
    job_type = "hamiltonian"
    job_params_names = Dirac3Mixin.job_params_names + ["sum_constraint"]

    def solve(
        self,
        model: EqcModel,
        name: str = None,
        tags: List = None,
        sum_constraint: float = None,
        relaxation_schedule: int = None,
        num_samples: int = 1,
        wait: bool = True,
        mean_photon_number: float = None,
        quantum_fluctuation_coefficient: int = None,
        **job_kwargs,
        ):
        """
        Parameters
        --------------

        model: EqcModel 
            a model object which supplies a hamiltonian operator for the 
            device to sample. Must support the polynomial operator property.
        tags: List 
            a list of strings to save with the job
        sum_constraint : float 
            a value which applies a constraint to the solution, forcing
            all variables to sum to this value
        relaxation_schedule : int 
            a predefined schedule indicator which sets parameters
            on the device to control the sampling through photon 
            measurement
        num_samples : int 
            the number of samples to take, defaults to 1
        wait : bool 
            a flag for waiting for the response or letting it run asynchronously.
            Asynchronous runs must retrieve results directly using qci-client and
            the job_id.
        mean_photon_number : float 
            an optional decimal value which sets the average number 
            of photons that are present in a given quantum state.
            Modify this value to control the relaxation schedule more
            precisely than the four presets given in schedules 1
            through 4. Allowed values are decimals between 0.000133333333333 
            and 0.001.
        quantum_fluctuation_coefficient: int 
            an integer value which Sets the amount of loss introduced
            into the system for each loop during the measurement process.
            Modify this value to control the relaxation schedule more
            precisely than the four presets given in schedules 1
            through 4. Allowed values range from 1 to 50.

        """
        if sum_constraint is None:
            raise ValueError(
                "sum_constraint must be specified as a positive number"
            )
        if relaxation_schedule not in (1, 2, 3, 4):
            raise ValueError(
                "relaxation_schedule must be one of 1, 2, 3 or 4"
            )
        job_type = "sample-" + self.job_type
        return super().solve(
            model,
            name,
            tags=tags,
            num_samples=num_samples,
            wait=wait,
            job_type=job_type,
            sum_constraint=sum_constraint,
            relaxation_schedule=relaxation_schedule,
            mean_photon_number=mean_photon_number,
            quantum_fluctuation_coefficient=quantum_fluctuation_coefficient,
            **job_kwargs,
        )

