import os, pandas as pd, numpy as np

from .step import Step
from catrxneng.utils.influx import Influx
from catrxneng import confs


class Co2FtsStep(Step):

    def __init__(self, step_name, step_num, start, end):
        super().__init__(step_name, step_num, start, end)

    def attach_reactor(self, reactor_class, rate_model, T, p0, ghsv, mcat):
        self.reactor = reactor_class(rate_model, T, p0, ghsv, mcat, "co2")

    def simulate(self, dt_sec, std_dev):
        df = pd.DataFrame()
        df["timestamp"] = np.arange(self.start.UET, self.end.UET + dt_sec, dt_sec)
        num_points = df["timestamp"].size
        df["step_name"] = self.step_name
        df["step_num"] = self.step_num
        self.reactor.solve()
        df["bed_temp"] = self.reactor.T.C * np.random.normal(
            loc=1, scale=std_dev, size=num_points
        )
        df["pressure"] = self.reactor.P.bar * np.random.normal(
            loc=1, scale=std_dev, size=num_points
        )
        df["n2_mfc"] = self.reactor.F0["inert"].smLmin * np.random.normal(

            loc=1, scale=std_dev, size=num_points
        )
        df["co2_mfc"] = self.reactor.F0["co2"].smLmin * np.random.normal(
            loc=1, scale=std_dev, size=num_points
        )
        df["h2_mfc"] = self.reactor.F0["h2"].smLmin * np.random.normal(
            loc=1, scale=std_dev, size=num_points
        )

        ch4_sel = 0.3
        olefins_sel = 0.4
        paraffins_sel = 1 - ch4_sel - olefins_sel
        F_hydrocarbons = (
            self.reactor.F0["co2"] - self.reactor.F["co2"][-1] - self.reactor.F["co"][-1]
        )

        self.reactor.F["ch4"] = F_hydrocarbons * ch4_sel
        self.reactor.F["c2h4"] = F_hydrocarbons * olefins_sel / 4 / 2
        self.reactor.F["c3h6"] = F_hydrocarbons * olefins_sel / 4 / 3
        self.reactor.F["c4h8"] = F_hydrocarbons * olefins_sel / 4 / 4
        self.reactor.F["c5h10"] = F_hydrocarbons * olefins_sel / 4 / 5
        self.reactor.F["c2h6"] = F_hydrocarbons * paraffins_sel / 4 / 2
        self.reactor.F["c3h8"] = F_hydrocarbons * paraffins_sel / 4 / 3
        self.reactor.F["c4h10"] = F_hydrocarbons * paraffins_sel / 4 / 4
        self.reactor.F["c5h12"] = F_hydrocarbons * paraffins_sel / 4 / 5

        self.reactor.y = self.reactor.F / self.reactor.Ft

        for component in self.reactor.y.keys:
            df[f"{component}_gc_conc"] = self.reactor.y[
                component
            ].pct * np.random.normal(loc=1, scale=std_dev, size=num_points)

        self.time_series_data = df

    # def upload_data(self, bucket, measurement):
    #     influx = Influx(
    #         url=os.getenv("INFLUXDB_URL"),
    #         org=os.getenv("INFLUXDB_ORG"),
    #         bucket=bucket,
    #         measurement=measurement,
    #     )
    #     tags = [
    #         confs.FR100.tags[data_id]
    #         for data_id in self.time_series_data.columns
    #         if data_id in self.time_series_data.columns
    #     ]
    #     influx.upload_dataframe(dataframe=self.time_series_data, tags=tags)
