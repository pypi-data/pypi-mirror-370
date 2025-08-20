import shap
from typing import Callable, Union


def explainer(
    model: Union[object, Callable],
    images,
    output_names=None,
    n_evals=100,
    batch_size=50,
    topk=4,
    mask_value="inpaint_telea",
    normalize=255,
):
    # define a masker that is used to mask out partitions of the input image.
    masker = shap.maskers.Image(mask_value, images[0].shape)
    # create an explainer with model and image masker
    e = shap.Explainer(model, masker, output_names=output_names)
    # here we explain _ images using _ evaluations of the underlying model to estimate the SHAP values
    shap_values = e(
        images,
        max_evals=n_evals,
        batch_size=batch_size,
        outputs=shap.Explanation.argsort.flip[:topk],
    )
    print(images)
    shap.image_plot(shap_values, images / normalize)
