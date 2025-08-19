import torch
import datasets
import inspect
from aicard.evaluation.task import Task
from aicard.evaluation import tasks
from aicard.evaluation import loaders

def handle_object_special_case(data, task: Task):
    t2t = task.targets
    targets_found = []
    for candidate_object in t2t["obj"]:
        for key in data:
            if candidate_object.lower() in key.lower():  # we have an object
                if isinstance(data[key], dict):
                    for candidate_target in t2t["target"]:
                        t = []
                        t_found = 0
                        l_found = 0
                        for k in data[key]:
                            if candidate_target.lower() in k.lower():
                                t.append(k)
                                t_found += 1
                            for candidate_label in t2t["label"]:
                                if candidate_label.lower() in k.lower():
                                    t.append(k)
                                    l_found += 1
                        if t_found == 1 and l_found == 1:
                            return [key, t[0], t[1]]  # object, target, label
                elif isinstance(data[key], list):
                    for candidate_target in t2t["target"]:
                        t = []
                        t_found = 0
                        l_found = 0
                        for k in data[key][0]:
                            if candidate_target.lower() in k.lower():
                                t.append(k)
                                t_found += 1
                            for candidate_label in t2t["label"]:
                                if candidate_label.lower() in k.lower():
                                    t.append(k)
                                    l_found += 1
                        if t_found == 1 and l_found == 1:
                            return [key, t[0], t[1]]  # object, target, label
    # if we don't have an object
    for candidate_target in t2t["target"]:
        t = []
        t_found = 0
        l_found = 0
        for k in data:
            if candidate_target.lower() in k.lower():
                t.append(k)
                t_found += 1
            for candidate_label in t2t["label"]:
                if candidate_label.lower() in k.lower():
                    t.append(k)
                    l_found += 1
        if t_found == 1 and l_found == 1:
            return [t[0], t[1]]  # target, category

def check_validity_of_target(data, task: Task, target_column: str|None=None):
    if task==tasks.vision.image_segmentation or task == tasks.vision.object_detection:
        target_column = handle_object_special_case(data, task)
        return target_column
    if target_column is not None:
        for key in data:
            if target_column in key:
                return target_column
    t2t = task.targets
    targets_found = []
    for candidate in t2t:
        for key in data:
            if candidate.lower() in key.lower():  # cases insensitive match
                targets_found.append(key)
    assert len(targets_found), f"""Expected one of {', '.join('"'+i+'"' for i in t2t)}, but got {', '.join('"'+key+'"' for key in data)}"""
    assert len(targets_found) == 1, f"""Found more that one match to target: {', '.join('"'+i+'"' for i in targets_found)}. Use the option "target" to choose which one you want"""
    return targets_found[0]

def convert_to_datasets(data):
    if isinstance(data, datasets.Dataset): return data
    if isinstance(data, dict): return datasets.Dataset.from_dict(data)
    if isinstance(data, list): return datasets.Dataset.from_list(data)
    raise AssertionError(f"Dataset of type {type(data)} is not supported")

def anns_to_datasets(anns):
    # assuming anns is a list
    if isinstance(anns[0], dict): return datasets.Dataset.from_list(anns)
    anns = [datasets.Dataset.from_list(ann) for ann in anns]
    anns = [datasets.Dataset.to_dict(ann) for ann in anns]
    return datasets.Dataset.from_list(anns)

def autocall(metric, **kwargs):
    args = set(inspect.signature(metric).parameters.keys())
    kwargs = {k: v for k, v in kwargs.items() if k in args}
    try: return metric(**kwargs)
    except TypeError as e:
        print(e)
        return None

def evaluate(
    data: "path or data",
    pipeline: callable,
    task: Task,
    target_column:str|None=None,
    num_classes:int|None=None,  # in case the preds have more classes than target
    batch_size:int=1,
    anns: list[list[dict]]|list[dict]|None=None,
):
    if anns is None:
        anns = [None]
    if loaders.is_path(data):
        data = loaders.read_data(data)
    data = convert_to_datasets(data)
    data = data.batch(batch_size)
    anns = anns_to_datasets(anns)
    anns = anns.batch(batch_size)

    out_sample = pipeline(data[0])
    task.assert_output_type(out_sample[0])
    target_column = check_validity_of_target(anns[0] if len(anns.features) else data[0], task, target_column)

    preds = []
    for batch in data:
        preds.extend(pipeline(batch))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    kwargs = task.parameters(
        data=data,
        preds=preds,
        target_column=target_column,
        num_classes=num_classes,
        anns=anns,
        device=device
    )
    ret = {metric.__name__: autocall(metric, **kwargs, device=device) for metric in task.metrics}
    return {k: float(v) for k,v in ret.items() if v is not None}


# run({'label': [1, 0, 1,0,1,0,1]}, [0.2,0.8,0.8,0.1,0.8,0.3,0.6], 'label', 'Image Classification')
# run(data={"boxes": [[[300.00, 100.00, 315.00, 150.00],[300.00, 100.00, 315.00, 150.00]]], "labels": [[4,5]]}, preds=[([
#              [296.55, 93.96, 314.97, 152.79],
#              [298.55, 98.96, 314.97, 151.79]], [4, 5], [0.9, 0.8])], task='Object Detection',
#              target=['boxes', "labels"], num_classes_model=None)
