# (C) Quantum Computing Inc., 2024.
# Import libs
import os
import sys
import time
import datetime
import json
import warnings
from functools import wraps
import numpy as np
import pandas as pd

from ..base import ConstraintsMixIn
from eqc_models import QuadraticModel


class PortBase(ConstraintsMixIn, QuadraticModel):
    def __init__(
        self,
        stocks: list,
        stock_data_dir: str,
        adj_date: str,
        lookback_days: int = 60,
    ):
        self.stocks = stocks
        self.data_dir = stock_data_dir
        self.adj_date = adj_date
        self.lookback_days = lookback_days

        self._H = self.build()

    def get_stock_returns(self, min_date, max_date):
        stocks = self.stocks
        min_date = pd.to_datetime(min_date)
        max_date = pd.to_datetime(max_date)

        return_df = None
        for stock in stocks:
            stock_df = pd.read_csv(
                os.path.join(self.data_dir, "%s.csv" % stock)
            )
            stock_df["Date"] = stock_df["Date"].astype("datetime64[ns]")
            stock_df = (
                stock_df.fillna(method="ffill")
                .fillna(method="bfill")
                .fillna(0)
            )
            stock_df[stock] = stock_df[stock].pct_change()
            stock_df = stock_df.dropna()

            stock_df = stock_df[
                (stock_df["Date"] >= min_date)
                & (stock_df["Date"] <= max_date)
            ]

            if return_df is None:
                return_df = stock_df
            else:
                return_df = return_df.merge(
                    stock_df,
                    how="outer",
                    on="Date",
                )

        return_df = (
            return_df.fillna(method="ffill")
            .fillna(method="bfill")
            .fillna(0)
        )

        return return_df

    def get_hamiltonian(
        self,
        return_df,
        min_date,
        max_date,
    ):
        pass

    def build(self):
        # Get dates
        adj_date = pd.to_datetime(self.adj_date)
        min_date = adj_date - datetime.timedelta(days=self.lookback_days)
        max_date = adj_date - datetime.timedelta(days=1)

        # Get return dataframe
        return_df = self.get_stock_returns(min_date, max_date)
        return_df = return_df.sort_values("Date")
        return_df = return_df.fillna(method="ffill").fillna(0)

        # Get and set hamiltonian
        J, C, sum_constraint = self.get_hamiltonian(
            return_df,
            min_date,
            max_date,
        )
        self._C = C
        self._J = J
        self._sum_constraint = sum_constraint
        
        # Set domain
        num_variables = C.shape[0]
        self.upper_bound = sum_constraint * np.ones((num_variables,))

        return C, J

    def get_dynamic_range(self):
        C = self._C
        J = self._J

        if C is None:
            return

        if J is None:
            return

        absc = np.abs(C)
        absj = np.abs(J)
        minc = np.min(absc[absc > 0])
        maxc = np.max(absc)
        minj = np.min(absj[absj > 0])
        maxj = np.max(absj)

        minval = min(minc, minj)
        maxval = max(maxc, maxj)

        return 10 * np.log10(maxval / minval)
