from sklearn.metrics import average_precision_score, accuracy_score, f1_score
from typing import List, Union, Optional
import numpy as np
import pandas


class Metrics:
    def generate_ap_data(
        self,
        y_true: Union[List[int], np.ndarray],
        y_pred: Union[List[float], np.ndarray],
        label: str,
    ):
        ap = average_precision_score(y_true, y_pred)
        self._add_to_data(label, ap=ap * 100)

    def generate_acc_data(
        self,
        y_true: Union[List[int], np.ndarray],
        y_pred: Union[List[int], np.ndarray],
        label: str,
    ):
        acc = accuracy_score(y_true, y_pred)
        self._add_to_data(label, acc=acc * 100)

    def generate_f1_data(
        self,
        y_true: Union[List[int], np.ndarray],
        y_pred: Union[List[int], np.ndarray],
        label: str,
    ):  # TODO: test it
        f1 = f1_score(y_true, y_pred)
        self._add_to_data(label, f1=f1 * 100)

    # Helper function to add data to
    def _add_to_data(
        self,
        label: str,
        acc: Optional[float] = None,
        ap: Optional[float] = None,
        f1: Optional[float] = None,
    ):
        # Check if the label already exists
        if label in self.data["label"].values:
            self.data.loc[self.data["label"] == label, "acc"] = (
                acc
                if acc is not None
                else self.data.loc[self.data["label"] == label, "acc"].values[0]
            )
            self.data.loc[self.data["label"] == label, "ap"] = (
                ap
                if ap is not None
                else self.data.loc[self.data["label"] == label, "ap"].values[0]
            )
            self.data.loc[self.data["label"] == label, "f1"] = (
                f1
                if f1 is not None
                else self.data.loc[self.data["label"] == label, "f1"].values[0]
            )
        else:
            # Append a new row if the label doesn't exist
            new_row = {"label": label, "acc": acc, "ap": ap, "f1": f1}
            new_row = pandas.DataFrame(new_row, index=[0])
            self.data = pandas.concat([self.data, new_row], ignore_index=True)
