from ._read_data_structure import get_data
from ._read_data_structure import get_supported_images, determine_type
from ._read_data_structure import count_items, is_file
import os
import pandas as pd
from typing import List, Union
from ..card import ModelCard
from collections import defaultdict


def write_md(model_card, data_count, is_train_set):

    if isinstance(data_count[next(iter(data_count))], dict):  # we have a split
        data_count_pd = pd.DataFrame.from_dict(
            data_count, orient="columns"
        ).reset_index()
        data_count_pd.columns = ["split"] + list(data_count.keys())
        data_count_pd = data_count_pd.melt(
            id_vars=["split"],
            value_vars=data_count.keys(),
            var_name="set",
            value_name="count",
        )
        model_card.text["Training Set" if is_train_set else "Eval Set"][
            "Train Set plot" if is_train_set else "Eval Set plot"
        ] = model_card.bar_plot(
            pdata=data_count_pd,
            y="count",
            x="split",
            color="set",
            barmode="group",
            title="Train Set Splits" if is_train_set else "Eval Set Splits",
            yaxis_title="Number of Data",
        ).replace(
            "<div>", '<div class="plot-inline-div">'
        )
    else:
        data_count_pd = pd.DataFrame(list(data_count.items()), columns=["set", "count"])
        model_card.text["Training Set" if is_train_set else "Eval Set"][
            "Train Set plot" if is_train_set else "Eval Set plot"
        ] = model_card.bar_plot(
            pdata=data_count_pd,
            y="count",
            x="set",
            title="Train Set" if is_train_set else "Eval Set",
            yaxis_title="Number of Data",
        ).replace(
            "<div>", '<div class="plot-inline-div">'
        )


def count_data(
    path: "List[str] | str",
    split: "str | List[str]" = None,
    model_card: ModelCard = None,
    is_train_set=True,
) -> Union[dict, None]:
    if not isinstance(path, list):  # if not a list make it
        path = [path]
    if not isinstance(split, list) and split is not None:  # if not a list make it
        split = [split]
    count = {}
    for p in path:
        p = os.path.expanduser(p)
        if not is_file(p):  # folder
            data, isfile, total_len = get_data(p)
            if "Files" in data:  # folder -> files
                for file_path in data["Files"]:
                    if determine_type(file_path) in get_supported_images():  # if Images
                        c = len(data["Files"])
                        break
                    current = count_data(
                        file_path, split, model_card=None
                    )  # if not Images
                    all_keys = set(count.keys()).union(current.keys())
                    c = {}
                    for key in all_keys:
                        c[key] = count.get(key, 0) + current.get(key, 0)
                count[os.path.basename(p)] = c
            else:  # folder -> folders -> files
                c = 0
                for f in data:  # TODO: test split, implement for .csv etc.
                    for file_path in data[f]["Files"]:
                        if (
                            determine_type(file_path) in get_supported_images()
                        ):  # if Images
                            c += len(data[f]["Files"])
                            break
                count[os.path.basename(p)] = c
        else:  # file
            data, isfile, total_len = get_data(p, split=split)
            if split is not None:
                count = defaultdict(lambda: defaultdict(int))
                for chunk in data:
                    for key in chunk:
                        count[os.path.splitext(os.path.basename(p))[0]][key] += len(
                            chunk[key]
                        )
                count[os.path.splitext(os.path.basename(p))[0]]["total"] = total_len()
            else:
                for chunk in data:
                    pass
                count[os.path.splitext(os.path.basename(p))[0]] = total_len()

    # write in Training Set
    if model_card is not None:
        write_md(model_card, count, is_train_set)

    return count
