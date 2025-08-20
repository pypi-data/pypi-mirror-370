import os, pandas as pd

from catrxneng import confs
from catrxneng.utils import Influx


class Expt:

    def __init__(self, reactor_class, rate_model, step_class, mcat):
        self.reactor_class = reactor_class
        self.rate_model = rate_model
        self.step_class = step_class
        self.mcat = mcat
        self.steps = []

    def add_step(self, step_name, start, end, T, p0, ghsv):
        step = self.step_class(step_name, len(self.steps) + 1, start, end)
        step.attach_reactor(self.reactor_class, self.rate_model, T, p0, ghsv, self.mcat)
        self.steps.append(step)

    def simulate(self, dt_sec, std_dev):
        for step in self.steps:
            step.simulate(dt_sec, std_dev)
        dframes = [step.time_series_data for step in self.steps]
        self.time_series_data = pd.concat(dframes, ignore_index=True)

    def upload_data(self, bucket, measurement):
        influx = Influx(
            url=os.getenv("INFLUXDB_URL"),
            org=os.getenv("INFLUXDB_ORG"),
            bucket=bucket,
            measurement=measurement,
        )
        tags = [
            confs.FR100.tags[data_id]
            for data_id in self.time_series_data.columns
            if data_id in self.time_series_data.columns
        ]
        influx.upload_dataframe(dataframe=self.time_series_data, tags=tags)
