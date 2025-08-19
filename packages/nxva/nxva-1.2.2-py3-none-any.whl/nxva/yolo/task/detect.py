import numpy as np
import torch

from .base_predictor import BasePredictor
from ..utils import ops


class DetectionPredictor(BasePredictor):
    def __init__(self, config: dict):
        super().__init__(config)
                
    def postprocess(self, pred, pre_imgs, imgs):
        """Post-processes predictions for an image and returns them.""" 
        if isinstance(pred, list):
            pred = pred[0] if pred[0].ndim == 3 else pred[-1]
        pred = torch.from_numpy(pred) if isinstance(pred, np.ndarray) else pred

        pred = ops.non_max_suppression(
            pred,
            conf_threshold=self.conf,
            iou_threshold=self.iou,
            nc=self.nc,
            classes=self.classes,
            agnostic=self.agnostic,
            device=self.device,
            version=self.version,
        )
        results = []
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = ops.scale_boxes(pre_imgs.shape[2:], det[:, :4], imgs[i].shape).round()
                det = det.cpu().numpy()
                det = det[np.argsort(det[:, 0])]      # sort by horizontal axis
                boxes = det[:, :4]
                confs = det[:, 4:5]
                class_ids = det[:, 5:6]
            else:
                boxes = np.zeros((0, 4))
                confs = np.zeros((0, 1))
                class_ids = np.zeros((0, 1))
            results.append([boxes, confs, class_ids])
        return results