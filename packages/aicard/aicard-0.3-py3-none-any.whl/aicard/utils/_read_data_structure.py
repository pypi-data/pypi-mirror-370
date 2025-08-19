import os
import pandas as pd
import shutil
import yaml
from typing import Union, Tuple
import sys
import csv
from PIL import Image


def is_file(path):
    if os.path.isfile(path):
        return True
    elif os.path.isdir(path):
        return False
    else:
        raise ValueError(f"The path '{path}' does not exist or is invalid.")


def determine_type(path):
    _, extension = os.path.splitext(path)
    return extension


def get_supported_types():
    return [
        ".csv",
        ".tsv",
        ".json",
        ".jsonl",
        ".xml",
        ".yml",
        ".yaml",
        ".parquet",
        ".feather",
        ".pickle",
        ".html",
    ]


def get_supported_images():
    ext = Image.registered_extensions()
    return [ex for ex, f in ext.items() if f in Image.OPEN]


"""
def make_split(data, split):
    output_dir = os.path.expanduser('~/.transparency_service/data/splits')
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Write splits to disk
    for s in split:
        for key, group in data.groupby(s):
            filename = f"{s}_{key}.parquet"
            filepath = os.path.join(output_dir, filename)
            group.to_csv(filepath)  # Save each group to a file

    # Step 2: Delete the original data to free up memory
    del data

    # Step 3: Reload splits from disk into memory
    data_splits_dict = {}
    for s in split:
        for filename in os.listdir(output_dir):
            if filename.startswith(s):
                key = filename.replace(f"{s}_", "").replace(".csv", "")
                filepath = os.path.join(output_dir, filename)
                data_splits_dict[f"{s}: {key}"] = pd.read_csv(filepath)

    # Step 4: Clean up
    shutil.rmtree(output_dir)

    return data_splits_dict
"""
"""
def ram_efficient_read_csv(file_path, chunk_size = 1000000, split: 'str | List[str]' = None):
    import sys
    import csv

    # for large lines
    csv.field_size_limit(sys.maxsize)

    name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = os.path.expanduser(f'~/.transparency_service/data/cache/{name}')
    if os.path.exists(output_dir):
        return get_data(output_dir, split=split)
    os.makedirs(output_dir, exist_ok=True)

    # Load the .csv in chunks
    data = pd.read_csv(file_path, chunksize=chunk_size, engine="python")

    # save each chunk to a separate file
    for i, chunk in enumerate(data):
        print(f'chunk {i}')
        output_file = f'{output_dir}/{name}_{i}.csv'
        chunk.to_csv(output_file, index=False)

    return get_data(output_dir, split=split)

"""


class LazySplitter:
    def __init__(self, data, split):
        self.data = data
        self.split = split
        self.total_length = 0  # only calculates correctly after the __iter__ pass

    def __iter__(self):
        for chunk in self.data:
            self.total_length += len(chunk)
            yield self._make_split(chunk, self.split)

    def _make_split(self, data, split):
        data_splits_dict = {}
        # Perform the splits
        for s in split:
            for key, group in data.groupby(s):
                data_splits_dict[f"{s}: {key}"] = group
        # Return the dictionary with splits
        return data_splits_dict

    def get_len(self):
        return self.total_length


class LazyReader:
    def __init__(self, data):
        self.data = data
        self.total_length = 0  # only calculates correctly after the __iter__ pass

    def __iter__(self):
        for chunk in self.data:
            self.total_length += len(chunk)
            yield chunk

    def get_len(self):
        return self.total_length


def read_file(
    path, delimiter, supported_types, t, names, split
) -> "pd.DataFrame | Dict[str, pd.DataFrame]":
    chunksize = 1000000
    if t == supported_types[0]:  # .csv
        csv.field_size_limit(sys.maxsize)
        data = (
            pd.read_csv(path, chunksize=chunksize, names=names, engine="python")
            if delimiter is None
            else pd.read_csv(
                path,
                chunksize=1000000,
                delimiter=delimiter,
                names=names,
                engine="python",
            )
        )
    elif t == supported_types[1]:  # .tsb
        csv.field_size_limit(sys.maxsize)
        data = pd.read_csv(
            path, chunksize=chunksize, delimiter=delimiter, names=names, engine="python"
        )
    elif t == supported_types[2]:  # .json
        data = pd.read_json(path)
    elif t == supported_types[3]:  # .jsonl
        data = pd.read_json(path, lines=True)
    elif t == supported_types[4]:  # .xml
        data = pd.read_xml(path)
    elif t == supported_types[5] or t == supported_types[6]:  # .yml .yaml
        with open(path, "r") as file:
            yaml_data = yaml.safe_load(file)
        data = pd.DataFrame(yaml_data)
    elif t == supported_types[7]:  # .parquet
        data = pd.read_parquet(path)
    elif t == supported_types[8]:  # .feather
        data = pd.read_feather(path)
    elif t == supported_types[9]:  # .pickle
        data = pd.read_pickle(path)
    elif t == supported_types[10]:  # .html
        data = pd.read_html(path)[0]
    else:  # not supported file types
        raise ValueError(f"read_data_structure: Type of {t} is not supported")
    if not isinstance(data, pd.io.parsers.TextFileReader):
        data = [data]
    if split is not None:
        data = LazySplitter(data, split)
    else:
        data = LazyReader(data)
    return data, data.get_len


def count_items(path):
    items = os.listdir(path)
    files = [item for item in items if os.path.isfile(os.path.join(path, item))]
    folders = [item for item in items if os.path.isdir(os.path.join(path, item))]
    others = [
        item
        for item in items
        if not os.path.isfile(os.path.join(path, item))
        and not os.path.isdir(os.path.join(path, item))
    ]
    return [items, files, folders, others]


def get_list_of_items(path, items, files, folders, others):
    if not items:  # empty folder
        print("The folder is empty.")
    elif others:  # unexpected content
        raise ValueError(
            f"The folder contains unexpected elements: {len(others)} item(s)."
        )
    elif files and folders:  # files and folders
        raise ValueError(
            f"{len(files)} file(s) and {len(folders)} folder(s): Can't handle both files and folders in the same path"
        )
    elif files:  # files
        return {"Files": [os.path.join(path, f) for f in files]}, -1
    elif folders:  # folders i.e. classification
        dic = {}
        for f in folders:
            items, files, folders, others = count_items(os.path.join(path, f))
            if (
                folders
            ):  # folder->folder->folder->... format is not supported stop the madness
                raise ValueError(f"Unexpected folder(s) inside {os.path.join(path, f)}")
            elif others:
                raise ValueError(f"Unexpected item(s) inside {os.path.join(path, f)}")
            else:
                files = {
                    "Files": [os.path.join(os.path.join(path, f), ff) for ff in files]
                }
                dic[f] = files
        return dic, -1


def get_data(
    path: str,
    delimiter=None,
    names=None,
    split: "str | List[str]" = None,
) -> Union[Tuple[dict, bool, int], Tuple[None, None, None]]:
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        print(f"The specified path {path} does not exist.")
        return None, None, None
    if is_file(path):  # file
        supported_types = get_supported_types()
        t = determine_type(path)
        data, total_len = read_file(
            path, delimiter, supported_types, t, names=names, split=split
        )
        return data, True, total_len  # dic, it is a file, total_len
    else:  # folder
        items, files, folders, others = count_items(path)
        dic, total_len = get_list_of_items(path, items, files, folders, others)
        return [dic], False, total_len  # dic, it is NOT file, total_len
