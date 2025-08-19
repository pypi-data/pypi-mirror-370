import torch
import numpy as np

from .detect import DetectionPredictor
from ..utils import ops


class PosePredictor(DetectionPredictor):
    def __init__(self, config: dict):
        super().__init__(config)

    def postprocess(self, preds, img, orig_imgs):
        print(type(preds))
        print(preds[0].shape, 'preds[0].shape')
        print(preds[1].shape, 'preds[1].shape')
        if self.config['version'] in ['yolov8', 'yolo11']:
            weight_type = self.config['weights'].split('.')[-1]
            if weight_type == 'engine':
                preds[0], preds[1] = preds[1], preds[0]

        if isinstance(preds, list):
            preds = preds[0] if preds[0].ndim == 3 else preds[-1]

        preds = torch.from_numpy(preds) if isinstance(preds, np.ndarray) else preds

        preds = ops.non_max_suppression(
            preds,
            conf_threshold=self.conf,
            iou_threshold=self.iou,
            nc=self.nc,
            classes=self.classes,
            agnostic=self.agnostic,
            device=self.device,
            version=self.version,
            task=self.task,
        )

        results = []
        for pred, orig_img in zip(preds, orig_imgs):
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], orig_img.shape).round()
            boxes = pred[:, :6]
            kpts = pred[:, 6:].view(len(pred), *self.kpt_shape) if len(pred) else pred[:, 6:]
            kpts = ops.scale_coords(img.shape[2:], kpts, orig_img.shape)
            results.append([boxes, kpts])
        return results