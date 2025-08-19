import torch
import warnings
import validators
import requests
from PIL import Image
from io import BytesIO
from aicard.evaluation import loaders

def unknown(data, preds, target_column, num_classes_model, anns, device):
    raise NotImplemented("Unknown parameters for the task")

def classification(data, preds, target_column, num_classes, anns, device):
    num_classes_model = num_classes
    target = []
    for batch in data:  # flatten the batch data[target_column]
        target.extend(batch[target_column])
    if isinstance(target[0], int):
        num_classes = num_classes_model if num_classes_model is not None else len(set(target))
        assert num_classes >= 2, f"found only {num_classes} classes in the dataset. Can't calculate metrics"
        class_task = "binary" if num_classes == 2 else "multiclass"
    elif isinstance(target[0], list):
        class_task = "multilabel"
        if num_classes_model is not None:
            num_classes = num_classes_model
        else:
            classes = set()
            for sample in target: classes |= set(sample)
            num_classes = len(classes)
        for t in target:  # correct the format
            if len(t) != num_classes:
                for i in range(len(target)):
                    reconstruct = [0] * num_classes
                    for cl in target[i]: reconstruct[cl] = 1
                    target[i] = reconstruct
                break
    else:
        raise AssertionError("Could not detect classification data format")
    return {
        "preds": torch.tensor(preds).to(device),
        "target": torch.tensor(target).to(device),
        "task": class_task,
        "num_classes": num_classes
    }

def object_detection(data, preds, target_column, num_classes, anns, device):
    anns_source = data if len(anns.features) == 0 else anns
    if len(target_column) == 2:
        bbox_column, label_column = target_column
    else:
        obj_column, bbox_column, label_column = target_column
    iou_type = "bbox"
    img_column = None
    src_type = None

    for key in data.column_names:  # search for the images as path or web
        if loaders.is_path(data[key][0][0]):
            if loaders.determine_type(data[key][0][0]) in loaders.get_supported_image_types():
                img_column = key
                src_type = "path"
        elif validators.url(data[key][0][0]):
            image_formats = ["image/" + t.replace(".", "") for t in loaders.get_supported_image_types()]
            r = requests.head(data[key][0][0])
            if r.headers["content-type"] in image_formats:
                img_column = key
                src_type = "url"
    box_format = None
    if src_type == "path":  # we can found the images
        for batch in data:
            for img, bboxes in zip(batch[img_column], batch[bbox_column]):
                image = Image.open(img)
                width, height = image.size
                for bbox in bboxes:
                    box_format = loaders.BoxFormatHelpers.determine_xyxy_or_xywh(bbox, width, height)
                    if box_format is not None:
                        break
                if box_format is not None:
                    break
            if box_format is not None:
                break
    elif src_type == "url":
        for batch in zip(data, anns_source):
            for img, bboxes in zip(batch[0][img_column], batch[1][bbox_column]):
                image = Image.open(BytesIO(requests.get(img).content))
                width, height = image.size
                for bbox in bboxes:
                    box_format = loaders.BoxFormatHelpers.determine_xyxy_or_xywh(bbox, width, height)
                    if box_format is not None:
                        break
                if box_format is not None:
                    break
            if box_format is not None:
                break
    if box_format is None:
        warnings.warn("Warning: can't determine box_format. Setting box_format = 'xyxy'. Consider using the box_format option")
        box_format = "xyxy"
    preds_ready = []
    if not isinstance(preds[0], dict):
        for pred in preds:
            boxes, cat_ids, scores = pred
            preds_ready.append({
                "boxes": torch.tensor(boxes).to(device),
                "labels": torch.tensor(cat_ids).to(device),
                "scores": torch.tensor(scores).to(device),
            })
    else:
        preds_ready = preds
        for pred_ready in preds_ready:
            for key in pred_ready:
                pred_ready[key] = pred_ready[key].to(device)
    target_ready = []
    if len(target_column) == 2:
        # bbox, label = target
        # assuming batch[bbox_column] and batch[label_column] are list or tuple
        for batch in anns_source:
            for boxes_target, cat_ids_target in zip(batch[bbox_column], batch[label_column]):
                if (boxes_target is not None) and (cat_ids_target is not None):  # prevent reading None values that the convertion to datasets creates
                    target_ready.append({
                        "boxes": torch.tensor(boxes_target).to(device),
                        "labels": torch.tensor(cat_ids_target).to(device),
                    })
    else:
        # obj, bbox, label = target
        if isinstance(anns_source[0][obj_column], dict):
            for batch in anns_source:
                for boxes_target, cat_ids_target in zip(
                    batch[obj_column][bbox_column], batch[obj_column][label_column]
                ):
                    if (boxes_target is not None) and (
                        cat_ids_target is not None
                    ):  # prevent reading None values that the convertion to datasets creates
                        target_ready.append({
                            "boxes": torch.tensor(boxes_target).to(device),
                            "labels": torch.tensor(cat_ids_target).to(device),
                        })
        else:  # elif isinstance(data[obj], list)
            for batch in anns_source:
                for object in batch[obj_column]:
                    if (object[bbox_column] is not None) and (
                        object[label_column] is not None
                    ):  # prevent reading None values that the convertion to datasets creates
                        target_ready.append({
                            "boxes": torch.tensor(object[bbox_column]).to(device),
                            "labels": torch.tensor(object[label_column]).to(device),
                        })
    # TODO: (manios) I have literally no idea of what this file is supposed to do
    return {
        "iou_type": iou_type,
        "box_format": box_format,
        "task": "MULTILABEL",
        "num_classes": num_classes
    }

def image_segmentation(data, preds, target_column, num_classes_model, anns, device=None):
    return {"iou_type": "segm"}
