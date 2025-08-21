from eqc_models.process.base import ProcessModel

class ModelPredictiveControl(ProcessModel):
    """ Base class for implementing MPC optimization problems """

    def __init__(self, G : nx.Graph, V : int=1, V_T:float=0.0):
        self.processArgs(*args, **kwargs)
        self.T = T
        self.V_T = V_T
        super(ModelPredictiveControl, self).__init__(G)
        
    def processArgs(self, *args, **kwargs):
        """ Provide a method to capture arguments necessary for configuring an instance """
        raise NotImplementedError("subclass must implement processArgs")

    def constraints(self) -> Tuple[np.ndarray]:
        pass
