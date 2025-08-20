from aicard.evaluation import params
from aicard.evaluation import metrics
from aicard.evaluation.task import Task, targets

audio_text_to_text = Task(
    "Audio-Text to Text",
    targets=targets.text,
    metrics=[metrics.wer, metrics.cer], # TODO: blue, rouge
    parameters=params.unknown,          # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)
image_text_to_text = Task(
    "Audio-Text to Text",
    targets=targets.text,
    metrics=[],                         # TODO: blue, rouge, meteor, cider, spice
    parameters=params.unknown,          # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)
visual_question_answering = Task(
    "Visual Question Answering",
    targets=targets.text,
    metrics=[metrics.f1_macro, metrics.f1_micro], # TODO: Exact Match (EM), blue, meteor, VQA Accuracy
    parameters=params.classification,             # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)
document_question_answering = Task(
    "Document Question Answering",
    targets=targets.text,
    metrics=[metrics.f1_macro, metrics.f1_micro], # TODO: Exact Match (EM), blue, meteor
    parameters=params.classification,             # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)
video_text_to_text = Task(
    "Video-Text to Text",
    targets=targets.text,
    metrics=[],                         # TODO: blue, rouge, meteor, CIDEr, spice
    parameters=params.classification,   # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)