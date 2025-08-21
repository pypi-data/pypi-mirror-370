import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge

from .reservoir import QciReservoir
from .forecastbase import BaseForecastModel

class ReservoirForecastModel(BaseForecastModel, QciReservoir):
    """
    A reservoir based forecast model.

    Parameters
    ----------

    ip_addr: The IP address of the device.

    num_nodes: Number of reservoir network nodes.

    feature_scaling: The factor used to scale the reservoir output.

    num_pads: Size of the pad used in the reservoir input;
    default: 0.

    reg_coef: L2 regularization coefficient for linear regression;
    default: 0.
        
    device: The QCi reservoir device. Currently only 'EmuCore' is
    supported; default: EmuCore.


    Examples
    ---------
    
    >>> MAX_TRAIN_DAY = 800
    >>> IP_ADDR = "172.22.19.49"
    >>> FEATURE_SCALING = 0.1
    >>> NUM_NODES = 1000
    >>> NUM_PADS = 100
    >>> LAGS = 2
    >>> from contextlib import redirect_stdout
    >>> import io
    >>> f = io.StringIO()
    >>> from eqc_models.ml import ReservoirForecastModel
    >>> with redirect_stdout(f):
    ...    model = ReservoirForecastModel(
    ...        ip_addr=IP_ADDR,
    ...        num_nodes=NUM_NODES,
    ...        feature_scaling=FEATURE_SCALING,
    ...        num_pads=NUM_PADS,
    ...        device="EmuCore",
    ...    )
    ...    model.fit(
    ...        data=train_df,
    ...        feature_fields=["norm_cell_prod"],
    ...        target_fields=["norm_cell_prod"],
    ...        lags=LAGS,
    ...        horizon_size=1,
    ...    )
    ...    y_train_pred = model.predict(train_df, mode="in_sample")
    ...    y_test_pred = model.predict(test_df, mode="in_sample")
    >>> model.close()
    
    """
    
    def __init__(
        self,
        ip_addr,
        num_nodes,
        feature_scaling,
        num_pads: int = 0,
        reg_coef: float = 0.0,
        device: str = "EmuCore",
    ):
        super(ReservoirForecastModel).__init__()
        BaseForecastModel.__init__(self)
        QciReservoir.__init__(self, ip_addr, num_nodes)
        
        assert device == "EmuCore", "Unknown device!"

        self.ip_addr = ip_addr
        self.num_nodes = num_nodes
        self.feature_scaling = feature_scaling
        self.num_pads = num_pads
        self.reg_coef = reg_coef        
        self.device = device

        self.lock_id = None
        self.lin_model = None
        self.feature_fields = None
        self.target_fields = None
        self.lags = None
        self.horizon_size = None
        self.zero_pad_data = None
        self.train_pad_data = None        
        
        self.init_reservoir()

    def close(self):
        self.release_lock()

    def fit(
        self,
        data: pd.DataFrame,
        feature_fields: list,
        target_fields: list,
        lags: int = 0,
        horizon_size: int = 1,
    ):
        """A function to train a forecast model.

        Parameters
        ----------

        data: A pandas data frame that contain the time series.

        feature_fields: A list of fields in the data frame that are as
        inputs to the reservoir.

        target_fields: A list of fields in teh data frame that are to be
        forecasted.

        lags: Number of lags used; default = 0.

        horizon_size: Size of the horizon, e.g. number of forecast
        steps.

        """

        # Pad input
        num_pads = self.num_pads
        if num_pads is not None and num_pads > 0:
            self.zero_pad_data = pd.DataFrame()
            for item in data.columns:
                self.zero_pad_data[item] = np.zeros(shape=(num_pads))
                
            data = pd.concat([self.zero_pad_data, data])
        
        # Prep data
        fea_data = np.array(data[feature_fields])
        targ_data = np.array(data[target_fields])

        X_train, y_train, steps = self.prep_fea_targs(
            fea_data=fea_data,
            targ_data=targ_data,
            window_size=lags + 1,
            horizon_size=horizon_size,
        )

        # Save some parameters
        self.feature_fields = feature_fields
        self.target_fields = target_fields
        self.lags = lags
        self.horizon_size = horizon_size

        # Push to reservoir        
        X_train_resp = self.push_reservoir(X_train)

        if num_pads is not None and num_pads > 0:
            X_train_resp = X_train_resp[num_pads:]
            y_train = y_train[num_pads:]
            
        # Build linear model
        #self.lin_model = LinearRegression(fit_intercept=True)
        self.lin_model = Ridge(alpha=self.reg_coef, fit_intercept=True)
        self.lin_model.fit(X_train_resp, y_train)

        # Get predictions
        y_train_pred = self.lin_model.predict(X_train_resp)

        # Echo some stats
        train_stats = self.get_stats(y_train, y_train_pred)

        print("Training stats:", train_stats)

        if num_pads is not None and num_pads > 0:        
            self.train_pad_data = data.tail(num_pads)

        return

    def predict(
        self,
        data: pd.DataFrame,
        pad_mode: str = "zero",
        mode: str = "in_sample",
    ):
        """A function to get predictions from forecast model.

        Parameters
        ----------

        data: A pandas data frame that contain the time series.

        pad_mode: Mode of the reservoir input padding, either
        'last_train' or 'zero'; default: 'zero.
        
        mode: A value of 'out_of_sample' predicts the horizon
        following the time series. A value of 'in_sample' predicts in
        sample (used for testing); default: in_sample.

        Returns
        -------

        The predictions: numpy.array((horizon_size, num_dims)).

        """

        assert self.lin_model is not None, "Model not train yet!"
        assert mode in ["in_sample", "out_of_sample"], (
            "Unknown mode <%s>!" % mode
        )

        num_pads = self.num_pads
        if num_pads is not None and num_pads > 0:
            if pad_mode == "last_train":
                pad_data = self.train_pad_data
            else:
                pad_data = self.zero_pad_data
            
            data = pd.concat([pad_data, data])
        
        num_records = data.shape[0]
        fea_data = np.array(data[self.feature_fields])
        targ_data = np.array(data[self.target_fields])
        
        if mode == "in_sample":
            X, y, _ = self.prep_fea_targs(
                fea_data=fea_data,
                targ_data=targ_data,
                window_size=self.lags + 1,
                horizon_size=self.horizon_size,
            )
        elif mode == "out_of_sample":
            X = self.prep_out_of_sample(
                fea_data=fea_data,
                window_size=self.lags + 1,
                horizon_size=self.horizon_size,
            )
        else:
            assert False, "Unknown mode <%s>!" % mode
            
        X_resp = self.push_reservoir(X)

        if self.num_pads is not None and self.num_pads > 0:
            X_resp = X_resp[self.num_pads:]
            y = y[self.num_pads:]
            
        y_pred = self.lin_model.predict(X_resp)

        # Echo some stats
        if mode == "in_sample":
            stats = self.get_stats(y, y_pred)
            print("In-sample prediction stats:", stats)
        
        return y_pred
