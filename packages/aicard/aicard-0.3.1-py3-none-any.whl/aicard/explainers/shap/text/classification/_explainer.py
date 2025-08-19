import shap


def explainer(model, data):
    e = shap.Explainer(model)
    shap_values = e(data)
    shap.plots.text(shap_values)
