import torch.nn as nn
import torch
import numpy as np
import torchvision.transforms as T
from .models import build_model
from .reid_model_factory import load_pretrained_weights

class ReIDDetectMultiBackend(nn.Module):
    # ReID models MultiBackend class for python inference on various backends
    def __init__(self, weights='osnet_x0_25_msmt17.pt', device=torch.device('cpu'), fp16=False, pretrained=True):
        super().__init__()
        model_name = (weights.split('/')[-1]).split('.')[0]
        model_type = (weights.split('/')[-1]).split('.')[-1]

        self.pt = False
        self.jit = False
        self.onnx = False
        self.xml = False
        self.engine = False
        self.tflite = False
        # 根據model_type
        if model_type == 'pt':
            self.pt = True
        elif model_type == 'jit':
            self.jit = True
        elif model_type == 'onnx':
            self.onnx = True
        elif model_type == 'xml':
            self.xml = True
        elif model_type == 'engine':
            self.engine = True
        elif model_type == 'tflite':
            self.tflite = True
        else:
            pass
        # a = basename(w) #擷取weights 名稱
        self.fp16 = fp16

        # Build transform functions
        self.device = torch.device(device)
        self.image_size=(256, 128)
        self.pixel_mean=[0.485, 0.456, 0.406]
        self.pixel_std=[0.229, 0.224, 0.225]
        self.transforms = []
        self.transforms += [T.Resize(self.image_size)]
        self.transforms += [T.ToTensor()]
        self.transforms += [T.Normalize(mean=self.pixel_mean, std=self.pixel_std)]
        self.preprocess = T.Compose(self.transforms)
        self.to_pil = T.ToPILImage()

        # Build model
        self.model = build_model(
            model_name,
            num_classes=1,
            # pretrained=not (w and w.is_file()),
            pretrained=not(weights),
            use_gpu=device
        )
        if weights:
            load_pretrained_weights(self.model,weights)
        self.model.to(device).eval()
        self.model.half() if self.fp16 else  self.model.float()

    def _preprocess(self, im_batch):
        images = []
        for element in im_batch:
            image = self.to_pil(element)
            image = self.preprocess(image)
            images.append(image)

        images = torch.stack(images, dim=0)
        images = images.to(self.device)

        return images
    
    def forward(self, im_batch):
        # preprocess batch
        im_batch = self._preprocess(im_batch)

        # batch to half
        if self.fp16 and im_batch.dtype != torch.float16:
           im_batch = im_batch.half()

        # batch processing
        features = []
        if self.pt:
            features = self.model(im_batch)
        elif self.jit:  # TorchScript
            features = self.model(im_batch)
        elif self.onnx:  # ONNX Runtime
            im_batch = im_batch.cpu().numpy()  # torch to numpy
            features = self.session.run([self.session.get_outputs()[0].name], {self.session.get_inputs()[0].name: im_batch})[0]
        elif self.engine:  # TensorRT
            if True and im_batch.shape != self.bindings['images'].shape:
                i_in, i_out = (self.model_.get_binding_index(x) for x in ('images', 'output'))
                self.context.set_binding_shape(i_in, im_batch.shape)  # reshape if dynamic
                self.bindings['images'] = self.bindings['images']._replace(shape=im_batch.shape)
                self.bindings['output'].data.resize_(tuple(self.context.get_binding_shape(i_out)))
            s = self.bindings['images'].shape
            assert im_batch.shape == s, f"input size {im_batch.shape} {'>' if self.dynamic else 'not equal to'} max model size {s}"
            self.binding_addrs['images'] = int(im_batch.data_ptr())
            self.context.execute_v2(list(self.binding_addrs.values()))
            features = self.bindings['output'].data
        elif self.xml:  # OpenVINO
            im_batch = im_batch.cpu().numpy()  # FP32
            features = self.executable_network([im_batch])[self.output_layer]
        else:
            print('Framework not supported at the moment, we are working on it...')
            exit()

        if isinstance(features, (list, tuple)):
            return self.from_numpy(features[0]) if len(features) == 1 else [self.from_numpy(x) for x in features]
        else:
            return self.from_numpy(features)

    def from_numpy(self, x):
        return torch.from_numpy(x).to(self.device) if isinstance(x, np.ndarray) else x

    def warmup(self, imgsz=[(256, 128, 3)]):
        # Warmup model by running inference once
        warmup_types = self.pt, self.jit, self.onnx, self.engine, self.tflite
        if any(warmup_types) and self.device.type != 'cpu':
            im = [np.empty(*imgsz).astype(np.uint8)]  # input
            for _ in range(2 if self.jit else 1):  #
                self.forward(im)  # warmup