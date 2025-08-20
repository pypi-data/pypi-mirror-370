import os, pandas as pd
from influxdb_client import InfluxDBClient, WritePrecision

from catrxneng.utils.time import Time


class Influx:

    def __init__(self, url, org, bucket, measurement, data_conf):
        self.url = url
        self.org = org
        self.bucket = bucket
        self.measurement = measurement
        self.data_conf = data_conf

    def upload_dataframe(self, dataframe, tags=None):
        if tags is None:
            tags = dataframe.columns
            tags.remove("timestamp")
        dataframe.set_index("timestamp", inplace=True)
        with InfluxDBClient(
            url=self.url, token=os.getenv("INFLUXDB_TOKEN"), org=self.org
        ) as client:
            with client.write_api() as write_api:
                write_api.write(
                    bucket=self.bucket,
                    record=dataframe,
                    data_frame_measurement_name=self.measurement,
                    data_frame_tag_columns=tags,
                    write_precision=WritePrecision.S,
                )

    def generate_query(self, start: Time, end: Time, dt_sec, tags):
        tag_string = ""
        for tag in list(tags.values()):
            tag_string = tag_string + 'r["_field"] == "' + tag + '" or '
        tag_string = tag_string[:-4]
        tag_string = tag_string + ")"

        query_start = (
            start.UTC.strftime("%Y-%m-%d") + "T" + start.UTC.strftime("%H:%M:%S") + "Z"
        )
        query_end = (
            end.UTC.strftime("%Y-%m-%d") + "T" + end.UTC.strftime("%H:%M:%S") + "Z"
        )

        self.query = """
        from(bucket: "BUCKET")
        |> range(start: START, stop: END)
        |> filter(fn: (r) => r["_measurement"] == "MEASUREMENT")
        |> filter(fn: (r) => TAGS
        |> aggregateWindow(every: SECONDSs, fn: last, createEmpty: false)
        |> map(fn: (r) => ({ r with _time: int(v: r._time) / 1000000000}))
        |> keep(columns: ["_time", "_field", "_value"])
        |> yield(name: "last")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """

        self.query = self.query.replace("BUCKET", self.bucket)
        self.query = self.query.replace("MEASUREMENT", self.measurement)
        self.query = self.query.replace("START", query_start)
        self.query = self.query.replace("END", query_end)
        self.query = self.query.replace("TAGS", tag_string)
        self.query = self.query.replace("SECONDS", str(int(dt_sec)))

    def request_data(self):
        timeout_min = 5
        with InfluxDBClient(
            url=self.url,
            token=os.getenv("INFLUXDB_TOKEN"),
            org=self.org,
            timeout=timeout_min * 60 * 1000,
        ) as client:
            try:
                self.raw_dataframes = client.query_api().query_data_frame(
                    query=self.query
                )
            except ValueError:
                self.query = self.query.split("|> pivot")[0]
                self.raw_dataframes = client.query_api().query_data_frame(
                    query=self.query
                )

    def format_data(self):
        self.data = pd.concat(self.raw_dataframes, ignore_index=True)
        self.data = self.data[["_time", "_field", "_value"]]
        self.data.rename(
            columns={"_time": "timestamp", "_value": "value"}, inplace=True
        )
        self.data_dict = {
            key: self.data[self.data["_field"] == value][["timestamp", "value"]]
            for key, value in self.tags.items()
        }
        for key, dataset in self.data_dict.items():
            try:
                dataset.loc[:, "value"] = dataset["value"] * self.conf[key].get(
                    "multiplier", 1
                )
                dataset.loc[:, "value"] = dataset["value"] + self.conf[key].get(
                    "add", 0
                )
            except TypeError:
                pass
