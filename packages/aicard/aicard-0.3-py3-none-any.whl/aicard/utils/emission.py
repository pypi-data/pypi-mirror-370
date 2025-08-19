import eco2ai
import os
from ..evaluation._evaluate import read_data


class Emission:
    def __init__(
        self, mc: "Model Card" = None, project_name="", experiment_description=""
    ):
        self.mc = mc
        self.file_name = "emission.csv"
        self.tracker = eco2ai.Tracker(
            project_name=project_name,
            experiment_description=experiment_description,
            file_name=self.file_name,
        )

    def start(self):
        self.tracker.start()

    def stop(self):
        self.tracker.stop()
        if self.mc is not None:
            with open(self.file_name, "r") as f:
                data = read_data(self.file_name)
            self.mc.emission = data
            os.remove(self.file_name)
