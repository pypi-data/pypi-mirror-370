# (C) Quantum Computing Inc., 2025.
import logging

try:
    from emucore_direct.client import EmuCoreClient
except ModuleNotFoundError:
    # Only warn here to try to disrupt package behavior as least as possible.
    logging.warning("emucore-direct package not available")

    class EmuCoreClient:
        """This is a stub for unsupported EmuCoreClient."""

        def __init__(*_, **__) -> None:
            """Raise exception when client cannot be created."""
            raise ModuleNotFoundError(
                "emucore-direct package not available, likely because Python version is 3.11+"
            )

# Parameters
VBIAS = 0.31
GAIN = 0.72
FEATURE_SCALING = 0.1
DENSITY = 1

class QciReservoir:
    """
    A class designed as an interface to QCi's reservoir devices.

    Parameters
    ----------
        
    ip_addr: The IP address of the device.
        
    num_nodes: Number of reservoir network nodes.
        
    vbias: Bias of the reservoir device; default: 0.31. 
        
    gain: Gain of the reservoir device; default: 0.72.
        
    density: Density used for normalization of the reservoir
    output; default: 1 (no normalization done).
        
    feature_scaling: The factor used to scale the reservoir output; default: 0.1.
        
    device: The QCi reservoir device. Currently only 'EmuCore' is
    supported; default: EmuCore.

    """

    def __init__(
        self,
        ip_addr: str,
        num_nodes: int,
        vbias: float = VBIAS,
        gain: float = GAIN,
        density: float = DENSITY,
        feature_scaling: float = FEATURE_SCALING,
        device: str = "EmuCore",
    ):
        assert device == "EmuCore", "Unknown device!"

        self.ip_addr = ip_addr
        self.num_nodes = num_nodes
        self.vbias = vbias
        self.gain = gain
        self.density = density
        self.feature_scaling = feature_scaling
        self.device = device
        self.client = None
        self.lock_id = None
        
    def init_reservoir(self):
        self.client = EmuCoreClient(ip_addr=self.ip_addr)
        
        self.lock_id, _, _ = self.client.wait_for_lock()

        self.client.reservoir_reset(lock_id=self.lock_id)
        
        self.client.rc_config(
            lock_id=self.lock_id,
            vbias=self.vbias,
            gain=self.gain,
            num_nodes=self.num_nodes,
            num_taps=self.num_nodes,
        )

    def release_lock(self):
        self.client.release_lock(lock_id=self.lock_id)
            
    def push_reservoir(self, X):

        assert self.client is not None, "The reservoir should be initialized!"
        assert self.lock_id is not None, "The reservoir should be initialized!"
        
        X_resp, _, _ = self.client.process_all_data(
            input_data=X,
            num_nodes=self.num_nodes,
            density=self.density,
            feature_scaling=self.feature_scaling,
            lock_id=self.lock_id,
        )

        return X_resp

    def run_reservoir(self, X_train, X_test=None):

        if X_test is not None:
            assert X_train.shape[1] == X_test.shape[1]

        num_feas = X_train.shape[1]


        X_resp_train = _push_emucore(X_train, lock_id)

        X_resp_test = None
        if X_test is not None:
            X_resp_test = _push_emucore(X_test, lock_id)



        return X_resp_train, X_resp_test
