import numpy as np
import torch
from typing import Tuple
from aicard.evaluation import params
from aicard.evaluation import metrics
from aicard.evaluation.task import Task, targets

depth_estimation = Task(
    "Depth Estimation",
    targets=targets.depth,
    metrics=[metrics.mae, metrics.rmse, metrics.ssim, metrics],  # TODO: sirmse (Scale-Invariant rmse)
    parameters=params.classification,                            # TODO: WAS NOT CLEAR
    toinstance=([np.ndarray], lambda x: isinstance(x, np.ndarray)),
)

image_segmentation = Task(
    "Image Segmentation",
    targets=targets.segmentation, # special value
    metrics=[metrics.IoU,metrics.dice_macro, metrics.dice_micro], # TODO: pixel acc, metrics.map
    parameters=params.image_segmentation,
    toinstance=([np.ndarray], lambda x: isinstance(x, np.ndarray)),
)

object_detection = Task(
    "Object Detection",
    targets=targets.objdetect, # special value
    metrics=[metrics.precision_macro, metrics.precision_micro, metrics.f1_macro, metrics.f1_micro], # TODO: metrics.map, metrics.IoU
    parameters=params.object_detection,
    toinstance=(
            [dict[str, torch.Tensor], Tuple[list[list[int]], list[int], list[float]], list[int], list[float]],
            lambda x: (
                isinstance(x, list)
                and len(x) == 3
                and isinstance(x[0], list)
                and all(
                    isinstance(sublist, list)
                    and len(sublist) == 4
                    and all(isinstance(i, int) for i in sublist)
                    for sublist in x[0]
                )
                and isinstance(x[1], list)
                and all(isinstance(i, int) for i in x[1])
                and isinstance(x[2], list)
                and all(isinstance(f, float) for f in x[2])
            ) # box, cat_id, score,
            or (
                isinstance(x, dict)
                and len(x)==3
                and "scores" in x
                and isinstance(x["scores"], torch.Tensor)
                and "labels" in x
                and isinstance(x["labels"], torch.Tensor)
                and "boxes" in x
                and isinstance(x["boxes"], torch.Tensor)
            ),
        ),
)

image_classification = Task(
    "Image Classification",
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

text_to_image = Task(
    "Text to Image",
    targets=targets.image,
    metrics=[metrics.ssim], # TODO: Inception Score (IS), Fréchet Inception Distance (fid), CLIPScore
    parameters=params.image_segmentation,  # TODO: WAS NOT CLEAR - I PUT ONE AT RANDOM (Manios)
    toinstance= ([np.ndarray], lambda x: isinstance(x, np.ndarray)),
)

image_to_text = Task(
    "Image to Text",
    targets=targets.text,
    metrics=[],  # TODO: blue, rouge, meteor, CIDEr, spice
    parameters=params.classification,  # TODO: WAS NOT CLEAR
    toinstance=([str], lambda x: isinstance(x, str)),
)

image_to_image = Task(
    "Image to Image",
    targets=targets.image,
    metrics=[metrics.ssim, metrics.psnr],  # TODO: lpips (Perceptual Loss)
    parameters=params.image_segmentation,  # TODO: WAS NOT CLEAR - I PUT ONE AT RANDOM (Manios)
    toinstance=([np.ndarray], lambda x: isinstance(x, np.ndarray))
)

image_to_video = Task(
    "Image to Video",
    targets=targets.video,
    metrics=[metrics.ssim, metrics.psnr],  # TODO: FVD (Fréchet Video Distance)
    parameters=params.unknown,             # TODO: WAS NOT CLEAR AT ALL
    toinstance=(list[np.ndarray],lambda x: isinstance(x, list) and all(isinstance(t, np.ndarray) for t in x),),
)

video_classification = Task(
    "Video Classification",
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

text_to_video = Task(
    "Text to Video",
    targets=targets.video,
    metrics=[metrics.ssim],     # TODO: FVD, IS, Fid
    parameters=params.unknown,  # TODO: WAS NOT CLEAR
    toinstance=(list[np.ndarray],lambda x: isinstance(x, list) and all(isinstance(t, np.ndarray) for t in x),),
)

mask_generation = Task(
    "Text to Video",
    targets=targets.mask,
    metrics=[metrics.IoU, metrics.dice_macro, metrics.dice_micro], # TODO: Pixel Accuracy
    parameters=params.unknown,  # TODO: WAS NOT CLEAR
    toinstance=([np.ndarray], lambda x: isinstance(x, np.ndarray)),
)

image_feature_extraction = Task(
    "Image Feature Extraction",
    targets=targets.imgfeatextr,
    metrics=[], # TODO: Cosine Similarity,Euclidean Distance,lpips
    parameters=params.unknown,  # TODO: WAS NOT CLEAR
    toinstance=([np.ndarray], lambda x: isinstance(x, np.ndarray)),
)

keypoint_detection = Task(
    "Keypoint Detection",
    targets=targets.keypoint,
    metrics=[metrics.rmse],     # TODO: Percentage of Correct Keypoints (PCK), Normalized Mean Error (NME), Mean Squared Error (MSE)
    parameters=params.unknown,  # TODO: WAS NOT CLEAR
    toinstance=(
        list[Tuple[int, int]],
        lambda x: isinstance(x, list)
        and all(
            isinstance(t, tuple)
            and len(t) == 2
            and isinstance(t[0], int)
            and isinstance(t[1], int)
            for t in x
        ),
    ),
)

