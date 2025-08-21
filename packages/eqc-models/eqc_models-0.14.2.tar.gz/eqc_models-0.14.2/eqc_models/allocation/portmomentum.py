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

from .portbase import PortBase


class PortMomentum(PortBase):
    def __init__(
        self,
        stocks: list,
        stock_data_dir: str,
        adj_date: str,
        lookback_days: int = 60,
        window_days: int = 30,
        window_overlap_days: int = 15,
        weight_upper_limit: float = 0.08,
        r_base: float = 0.05 / 365,
        alpha: float = 5.0,
        beta: float = 1.0,
        xi: float = 1.0,
    ):
        self.stocks = stocks
        self.data_dir = stock_data_dir
        self.adj_date = adj_date
        self.lookback_days = lookback_days

        self.window_days = window_days
        self.window_overlap_days = window_overlap_days
        self.weight_upper_limit = weight_upper_limit
        self.r_base = r_base
        self.alpha = alpha
        self.beta = beta
        self.xi = xi

        self._H = self.build()

    def get_hamiltonian(
        self,
        return_df,
        min_date,
        max_date,
    ):
        stocks = self.stocks
        xi = self.xi
        window_days = self.window_days
        window_overlap_days = self.window_overlap_days
        weight_upper_limit = self.weight_upper_limit

        # Set some params
        K = len(stocks)

        # Calculate Q and p_vec
        Q = np.zeros(shape=(K, K), dtype=np.float32)
        p_vec = np.zeros(shape=(K), dtype=np.float32)

        m = 0
        min_date = pd.to_datetime(min_date)
        max_date = pd.to_datetime(max_date)
        tmp_date = min_date
        while tmp_date <= max_date:
            tmp_min_date = tmp_date
            tmp_max_date = tmp_date + datetime.timedelta(days=window_days)
            tmp_df = return_df[
                (return_df["Date"] >= tmp_min_date)
                & (return_df["Date"] <= tmp_max_date)
            ]

            r_list = []
            for i in range(K):
                r_list.append(np.array(tmp_df[stocks[i]]))

            Q_tmp = np.cov(r_list)
            for i in range(K):
                p_vec[i] += -self.r_base * np.mean(r_list[i])
                for j in range(K):
                    Q[i][j] += Q_tmp[i][j]

            tmp_date += datetime.timedelta(
                days=window_days - window_overlap_days,
            )
            m += 1

        fct = m
        if fct > 0:
            fct = 1.0 / fct

        p_vec = fct * p_vec
        Q = fct * Q

        # Calculate the Hamiltonian
        J_no_limit = xi * Q
        C_no_limit = p_vec

        # make sure J is symmetric up to machine precision
        J_no_limit = 0.5 * (J_no_limit + J_no_limit.transpose())

        if weight_upper_limit is None:
            return J_no_limit, C_no_limit, 100.0

        W_max = 100.0 * weight_upper_limit

        J = np.zeros(shape=(2 * K, 2 * K), dtype=np.float32)
        C = np.zeros(shape=(2 * K), dtype=np.float32)

        for i in range(K):
            for j in range(K):
                J[i][j] = J_no_limit[i][j] + self.alpha

            J[i][i] += self.beta
            J[i][i + K] += self.beta
            J[i + K][i] += self.beta
            J[i + K][i + K] += self.beta
            C[i] = (
                C_no_limit[i] - 200.0 * self.alpha - 2 * self.beta * W_max
            )
            C[i + K] = -2 * self.beta * W_max

        C = C.reshape((C.shape[0], 1))

        # Check hamiltonian dims
        stocks = self.stocks
        K = len(stocks)

        assert J.shape[0] == K or J.shape[0] == 2 * K
        assert J.shape[1] == K or J.shape[0] == 2 * K
        assert C.shape[0] == K or C.shape[0] == 2 * K

        return J, C, K * W_max
