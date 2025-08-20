import torchmetrics

# (binary/multiclass) preds: Tensor[int/float], (multiclass) preds: Tensor[List[float]],, target: Tensor[int]
# or (multilabel) preds: Tensor[List[int/float]], target: Tensor[List[int]]

def f1(preds, target, task, num_classes, device): return f1_micro(preds, target, task, num_classes, device)
def f1_micro(preds, target, task, num_classes, device): return torchmetrics.F1Score(task=task, num_classes=num_classes, average="micro", num_labels=num_classes).to(device)(preds, target)
def f1_macro(preds, target, task, num_classes, device): return torchmetrics.F1Score(task=task, num_classes=num_classes, average="macro", num_labels=num_classes).to(device)(preds, target)
def f1_weighted(preds, target, task, num_classes, device): return torchmetrics.F1Score(task=task, num_classes=num_classes, average="weighted", num_labels=num_classes).to(device)(preds, target)
def top1_acc_micro(preds, target, task, num_classes, device): return torchmetrics.Accuracy(task=task, num_classes=num_classes, top_k=1, average="micro", num_labels=num_classes).to(device)(preds, target)
def top1_acc_macro(preds, target, task, num_classes, device): return torchmetrics.Accuracy(task=task, num_classes=num_classes, top_k=1, average="macro", num_labels=num_classes).to(device)(preds, target)
def top1_acc_weighted(preds, target, task, num_classes, device): return torchmetrics.Accuracy(task=task, num_classes=num_classes, top_k=1, average="weighted", num_labels=num_classes).to(device)(preds, target)
def top5_acc_micro(preds, target, task, num_classes, device): return torchmetrics.Accuracy(task=task, num_classes=num_classes, top_k=5, average="micro", num_labels=num_classes).to(device)(preds, target)
def top5_acc_macro(preds, target, task, num_classes, device): return torchmetrics.Accuracy(task=task, num_classes=num_classes, top_k=5, average="macro", num_labels=num_classes).to(device)(preds, target)
def top5_acc_weighted(preds, target, task, num_classes, device): return torchmetrics.Accuracy(task=task, num_classes=num_classes, top_k=5, average="weighted", num_labels=num_classes).to(device)(preds, target)
def precision_micro(preds, target, task, num_classes, device): return torchmetrics.Precision(task=task, num_classes=num_classes, average="micro", num_labels=num_classes).to(device)(preds, target)
def precision_macro(preds, target, task, num_classes, device): return torchmetrics.Precision(task=task,num_classes=num_classes,average="macro",num_labels=num_classes).to(device)(preds, target)
def precision_weighted(preds, target, task, num_classes, device): return torchmetrics.Precision(task=task,  num_classes=num_classes, average="weighted", num_labels=num_classes).to(device)(preds, target)
def recall_micro(preds, target, task, num_classes, device): return torchmetrics.Recall(task=task, num_classes=num_classes, average="micro",num_labels=num_classes).to(device)(preds, target)
def recall_macro(preds, target, task, num_classes, device): return torchmetrics.Recall(task=task, num_classes=num_classes, average="macro", num_labels=num_classes).to(device)(preds, target)
def recall_weighted(preds, target, task, num_classes, device): return torchmetrics.Recall(task=task, num_classes=num_classes, average="weighted", num_labels=num_classes,).to(device)(preds, target)
def auc_roc_macro(preds, target, task, num_classes, device): return torchmetrics.AUROC(task=task, num_classes=num_classes, average="macro", num_labels=num_classes).to(device)(preds, target)
def auc_roc_weighted(preds, target, task, num_classes, device): return torchmetrics.AUROC(task=task, num_classes=num_classes, average="weighted", num_labels=num_classes).to(device)(preds, target)
def dice_micro(preds, target, num_classes, device): return torchmetrics.classification.Dice(num_classes=num_classes, average="micro").to(device)(preds, target)
def dice_macro(preds, target, num_classes, device): return torchmetrics.classification.Dice(num_classes=num_classes, average="macro").to(device)(preds, target)
def wer(preds, target, device):
    """Word Error Rate"""
    return torchmetrics.text.WordErrorRate().to(device)(preds, target)
def cer(preds, target, device):
    """Character Error Rate"""
    return torchmetrics.text.CharErrorRate().to(device)(preds, target)
def mae(preds, target, device):
    """Mean Absolute Error"""
    return torchmetrics.regression.MeanAbsoluteError().to(device)(preds, target)
def rmse(preds, target, device):
    """Root Mean Square Error"""
    return torchmetrics.image.RootMeanSquaredErrorUsingSlidingWindow().to(device)(preds, target)
def ssim(preds, target, device):
    """Structural Similarity Index"""
    return torchmetrics.image.StructuralSimilarityIndexMeasure().to(device)(preds, target)
def psnr(preds, target, device):
    """Peak Signal-to-Noise Ratio"""
    return torchmetrics.image.PeakSignalNoiseRatio().to(device)(preds, target)
def map(preds, target, iou_type, box_format, device):
    """Mean Average precision"""
    # TODO: module 'torchmetrics.detection' has no attribute 'MeanAveragePrecision'
    return torchmetrics.detection.MeanAveragePrecision(iou_type=iou_type, box_format=box_format).to(device)(preds, target)
def IoU(preds, target, iou_type, box_format, device):
    """Intersection over Union"""
    # TODO: torch offers only iou for bboxes. what about segmenation
    # TODO: module 'torchmetrics.detection' has no attribute 'IntersectionOverUnion'
    return torchmetrics.detection.IntersectionOverUnion(box_format=box_format).to(device)(preds, target)
