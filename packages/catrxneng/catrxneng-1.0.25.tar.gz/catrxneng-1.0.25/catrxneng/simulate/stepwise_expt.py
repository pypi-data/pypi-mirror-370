import os, json, time, sys, pandas as pd, numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

import catrxneng as cat
from catrxneng.quantities import *


class StepwiseExpt:
    def __init__(self, reactor):
        pass
    
    def generate_single_data_points(self):
        rate_model = cat.kinetic_models.brubach2022.Brubach2022()
        cond = {
            "T": Temperature(C=300),
            "p0": Pressure([4,12,0,0,4]),
            "ghsv": GHSV(smLhgcat=170000),
            "mcat": Mass(g=0.25)
        }
        pfr = cat.reactors.PFR(cond, rate_model)
        pfr.solve()
        self.single_data_points = {
            "bed_temp": cond["T"].C,
            "pressure": np.sum(cond["p0"]).bar,
            "co2_mfc": (pfr.Ft0 * pfr.y0[0]).smLmin,
            "h2_mfc": (pfr.Ft0 * pfr.y0[1]).smLmin,
            "n2_mfc": (pfr.Ft0 * pfr.y0[4]).smLmin,
            ""
        }

    def generate_simulated_data(self, value, err, start, end, dt="3T"):
        timestamps = pd.date_range(start=start, end=end, freq=dt)
        simulated_values = value + err * np.random.randn(len(timestamps))
        data = pd.DataFrame({"timestamp": timestamps, "value": simulated_values})
        return data

    def write_data(self, df, bucket, measurement):
        client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        records = [
            {
                "measurement": measurement,
                "time": row["timestamp"],
                "fields": {col: row[col] for col in df.columns if col != "timestamp"}
            }
            for _, row in df.iterrows()
        ]
        write_api.write(bucket=bucket, record=records)
        write_api.close()
        client.close()
