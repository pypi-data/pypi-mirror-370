import pandas as pd
from eqc_models.ml import ReservoirForecastModel

# Deine parameters
INP_FILE = "mackey_glass_cell_production_series.csv"

MAX_TRAIN_DAY = 800
IP_ADDR = "172.22.19.49"
FEATURE_SCALING = 0.1
NUM_NODES = 1000
NUM_PADS = 100
LAGS = 2

# Prepare input time series
df = pd.read_csv(INP_FILE)

train_df = df[df["days"] <= MAX_TRAIN_DAY]
test_df = df[df["days"] > MAX_TRAIN_DAY]

# Train a forecast model
model = ReservoirForecastModel(
    ip_addr=IP_ADDR,
    num_nodes=NUM_NODES,
    feature_scaling=FEATURE_SCALING,
    num_pads=NUM_PADS,
    device="EmuCore",
)

model.fit(
    data=train_df,
    feature_fields=["norm_cell_prod"],
    target_fields=["norm_cell_prod"],
    lags=LAGS,
    horizon_size=1,
)

y_train_pred = model.predict(train_df, mode="in_sample")

print(y_train_pred)
print(y_train_pred.shape)

y_test_pred = model.predict(test_df, mode="in_sample")

print(y_test_pred)
print(y_test_pred.shape)

model.close()
