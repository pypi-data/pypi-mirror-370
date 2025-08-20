import numpy as np
import torch
from aicard.evaluation import params
from aicard.evaluation import metrics
from aicard.evaluation.task import Task, targets

question_answering = Task(
    "Question Answering",
    targets=targets.text,
    metrics=[metrics.f1_macro, metrics.f1_micro],  # TODO: Exact Match (EM)
    parameters=params.unknown,  # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)

translation = Task(
    "Translation",
    targets=targets.text,
    metrics=[],  # TODO: blue, meteor, rouge, chrF++
    parameters=params.unknown,   # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)

summarization = Task(
    "Summarization",
    targets=targets.text,
    metrics=[],  # TODO: blue, meteor, rouge, BERTScore
    parameters=params.unknown,   # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)

feature_extraction = Task(
    "Translation",
    targets=targets.featextr,
    metrics=[],  # TODO: Cosine Similarity,Euclidean Distance,Pearson Correlation
    parameters=params.unknown,   # TODO: WAS NOT CLEAR
    toinstance=([np.ndarray], lambda x: isinstance(x, np.ndarray)),
)

text_generation = Task(
    "Text Generation",
    targets=targets.text,
    metrics=[],  # TODO: blue, meteor, rouge, BERTScore, Perplexity
    parameters=params.unknown,   # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)

text_to_text_generation = Task(
    "Text to Text Generation",
    targets=targets.text,
    metrics=[],  # TODO: blue, meteor, rouge, BERTScore, chrF++"
    parameters=params.unknown,   # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)

text_classification = Task(
    "Text Classification",
    targets=targets.classes,
    metrics=[metrics.precision_macro, metrics.precision_micro, metrics.recall_macro, metrics.recall_micro,
             metrics.f1_macro, metrics.f1_micro, metrics.auc_roc_macro, metrics.auc_roc_macro],  # TODO: acc
    parameters=params.classification,
    toinstance=(
        [torch.Tensor, int, float, list[float], str, dict[str, float]],
        lambda x: (
            isinstance(x, (torch.Tensor, int, float, str))
            or (isinstance(x, list) and all(isinstance(i, float) for i in x))
            or (
                isinstance(x, dict)
                and all(
                    isinstance(k, str) and isinstance(v, float)
                    for k, v in x.items()
                )
            )
        ),
    ),
)