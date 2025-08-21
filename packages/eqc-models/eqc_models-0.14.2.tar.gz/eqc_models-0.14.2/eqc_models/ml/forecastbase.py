# (C) Quantum Computing Inc., 2024.
# Import libs
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_percentage_error,
)


# Define a base class for forecast models
class BaseForecastModel:
    """
    A base class for forecast models.
    """
    def __init__(self):
        pass

    def prep_fea_targs(
        self,
        fea_data: np.array,
        targ_data: np.array,
        window_size: int = 1,
        horizon_size: int = 1,
    ):
        num_records = fea_data.shape[0]

        assert (
            targ_data.shape[0] == num_records
        ), "Inconsistent dimensions!"

        step_vec = np.arange(num_records)

        num_fea_dims = fea_data.shape[1]
        num_targ_dims = targ_data.shape[1]

        X = []
        y = []
        steps = []
        for i in range(num_records - window_size - horizon_size + 1):
            fea_seq = fea_data[i : i + window_size]
            targ_seq = targ_data[
                i + window_size : i + window_size + horizon_size
            ]

            assert fea_seq.shape[0] == window_size
            assert fea_seq.shape[1] == num_fea_dims
            assert targ_seq.shape[0] == horizon_size
            assert targ_seq.shape[1] == num_targ_dims

            step_seq = step_vec[
                i + window_size : i + window_size + horizon_size
            ]

            assert step_seq.shape[0] == horizon_size

            fea_seq = fea_seq.reshape((num_fea_dims * window_size))
            targ_seq = targ_seq.reshape((num_targ_dims * horizon_size))
            step_seq = step_seq.reshape((horizon_size,))

            X.append(fea_seq)
            y.append(targ_seq)
            steps.append(step_seq)

        X = np.array(X)
        y = np.array(y)
        steps = np.array(steps)

        assert X.shape[0] == y.shape[0]
        assert len(steps) == X.shape[0]

        assert X.shape[1] == num_fea_dims * window_size
        assert y.shape[1] == num_targ_dims * horizon_size

        return X, y, steps

    def prep_out_of_sample(
        self,
        fea_data: np.array,
        window_size: int = 1,
        horizon_size: int = 1,
    ):
        num_records = fea_data.shape[0]

        num_fea_dims = fea_data.shape[1]

        fea_seq = fea_data[num_records - window_size : num_records]

        assert fea_seq.shape[0] == window_size
        assert fea_seq.shape[1] == num_fea_dims

        fea_seq = fea_seq.reshape((num_fea_dims * window_size))

        X = np.array([fea_seq])

        return X

    def generate_pred_df(
        self,
        y: np.array,
        y_pred: np.array,
        dates: np.array,
    ):
        num_records = y.shape[0]
        num_targ_dims = y.shape[1]

        assert y_pred.shape[0] == num_records
        assert y_pred.shape[1] == num_targ_dims
        assert dates.shape[0] == num_records
        assert dates.shape[1] == num_targ_dims

        tmp_size = num_records * num_targ_dims
        pred_df = pd.DataFrame(
            {
                "Date": dates.reshape((tmp_size)),
                "Actual": y.reshape((tmp_size)),
                "Predicted": y_pred.reshape((tmp_size)),
            }
        )

        pred_df = pred_df.groupby("Date", as_index=False)[
            "Actual", "Predicted"
        ].mean()

        return pred_df

    def get_stats(self, y, y_pred):
        mape = mean_absolute_percentage_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))

        stats_hash = {"MAPE": mape, "RMSE": rmse}

        return stats_hash

    def fit(self, data: pd.DataFrame):
        pass

    def predict(self, X: np.array):
        pass
