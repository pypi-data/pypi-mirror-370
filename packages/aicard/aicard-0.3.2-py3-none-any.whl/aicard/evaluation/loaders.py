import os
import csv
import sys
import yaml
import datasets
import pandas as pd

def is_path(s):
    return isinstance(s, str) and os.path.exists(os.path.expanduser(s))

def get_supported_types():
    return [".csv",".tsv",".json",".jsonl",".xml",".yml",".yaml",".parquet",".feather",".pickle"".html"]

def get_supported_image_types():
    return [".jpg",".jpeg",".png",".gif",".bmp",".tiff",".tif"]

def determine_type(path):
    _, extension = os.path.splitext(path)
    return extension

def read_pd(path, delimiter=None, names=None, split=None):
    # TODO: split is unused
    supported_types = get_supported_types()
    t = determine_type(path)
    if t == supported_types[0]:  # .csv
        csv.field_size_limit(sys.maxsize)
        return (
            pd.read_csv(path, names=names, engine="python")
            if delimiter is None
            else pd.read_csv(path, delimiter=delimiter, names=names, engine="python")
        )
    if t == supported_types[1]:  # .tsb
        csv.field_size_limit(sys.maxsize)
        return pd.read_csv(path, delimiter=delimiter, names=names, engine="python")
    if t == supported_types[2]: return pd.read_json(path)
    if t == supported_types[3]: return pd.read_json(path, lines=True)
    if t == supported_types[4]: return pd.read_xml(path)
    if t == supported_types[5] or t == supported_types[6]:  # .yml .yaml
        with open(path, "r") as file:
            yaml_data = yaml.safe_load(file)
        return pd.DataFrame(yaml_data)
    if t == supported_types[7]: return pd.read_parquet(path)
    if t == supported_types[8]: return pd.read_feather(path)
    if t == supported_types[9]: return pd.read_pickle(path)
    if t == supported_types[10]:  return pd.read_html(path)[0]
    raise AssertionError(f"read_data_structure: Type of {t} is not one of: {', '.join(get_supported_types())}")

def read_data(path, delimiter=None, names=None, split=None):
    return datasets.Dataset.from_pandas(read_pd(path, delimiter=delimiter, names=names, split=split))

class BoxFormatHelpers:
    @staticmethod
    def xyxy2xywh(xyxy):
        x_min, y_min, x_max, y_max = xyxy
        w = x_max - x_min
        h = y_max - y_min
        return x_min, y_min, w, h

    @staticmethod
    def xywh2xyxy(xywh):
        x_min, y_min, w, h = xywh
        x_max = x_min + w
        y_max = y_min + h
        return x_min, y_min, x_max, y_max

    @staticmethod
    def determine_xyxy_or_xywh(bbox, img_w, img_h):
        x_min, y_min, curious1, curious2 = BoxFormatHelpers.xyxy2xywh(bbox)
        if curious1 < 0 or curious2 < 0:
            return "xywh"
        x_min, y_min, curious1, curious2 = BoxFormatHelpers.xywh2xyxy(bbox)
        if curious1 > img_w or curious2 > img_h:
            return "xyxy"
        # warnings.warn("Warning: Can't determine bbox format. Assuming xyxy. Consider using the box_format option")
        return None
