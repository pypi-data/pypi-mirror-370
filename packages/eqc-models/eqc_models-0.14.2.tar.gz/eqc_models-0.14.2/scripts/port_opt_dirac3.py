# (C) Quantum Computing Inc., 2024.
import sys
import pandas as pd

from eqc_models.allocation import PortMomentum
from eqc_models.solvers import Dirac3CloudSolver
from utils import (
    STOCK_DATA_DIR,
    get_nasdaq100_constituents,
    get_port_stats,
)

# Set parameters
ADJ_DATE = "2022-01-01"
LOOKBACK_DAYS = 60
LOOKFORWARD_DAYS = 30

# Get stock list
stocks = get_nasdaq100_constituents(
    ADJ_DATE, LOOKBACK_DAYS, LOOKFORWARD_DAYS,
)

# Get portfolio model
model = PortMomentum(
    stocks=stocks,
    adj_date=ADJ_DATE,
    stock_data_dir=STOCK_DATA_DIR,
    lookback_days=LOOKBACK_DAYS,
    window_days=30,                                                                
    window_overlap_days=15,                                                        
    weight_upper_limit=0.08,                                                     
    r_base=0.05 / 365,                                                           
    alpha=5.0,                                                                   
    beta=1.0,  
    xi=1.0,
)

# Solve on Dirac-3
solver = Dirac3CloudSolver()
response = solver.solve(
    model,
    relaxation_schedule=2,
    num_samples=1,
)
sol = response["results"]["solutions"][0][:len(stocks)]

print(response)

weight_hash = {}
for i in range(len(stocks)):
    weight_hash[stocks[i]] = sol[i] / 100.0

tot_weight = sum(weight_hash.values())

if tot_weight != 1.0:
    for stock in stocks:
        weight_hash[stock] = weight_hash[stock] / tot_weight

weight_df = pd.DataFrame(
    {
        "Stock": [item for item in weight_hash.keys()],
        "Allocation": [
            weight_hash[item] for item in weight_hash.keys()
        ],
    }
)
weight_df["Date"] = ADJ_DATE
weight_df = weight_df[weight_df["Allocation"] > 0]

ret_df = get_port_stats(weight_df, 30)

print(ret_df)
