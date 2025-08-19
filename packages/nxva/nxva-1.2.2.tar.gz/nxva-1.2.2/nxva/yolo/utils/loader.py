#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom PyTorch Model Serialization/Deserialization Tool

This module provides a custom model loading function that can work with custom pickle modules,
used for loading YOLOv5 and YOLOv11 models, and supports module path mapping.

Main Features:
- Support for custom pickle modules
- Automatic module path mapping handling
- Compatible with YOLOv5 and YOLOv11
- Provides detailed debug information

Usage Example:
    from serialization import custom_load, create_custom_pickle_module
    
    pickle_module = create_custom_pickle_module({"DetectV5": "Detect"})
    model = custom_load('model.pt', pickle_module=pickle_module)
"""

import io, os, glob, cv2, numpy as np, torch, pickle, inspect, importlib, yaml
from pathlib import Path
import logging
from typing import Any, Dict, Optional, Union, IO, Callable

# ==================== Type Definitions ====================
from torch.storage import _get_dtype_from_pickle_storage_type
from torch.types import Storage

# Custom type aliases
FILE_LIKE = Union[str, os.PathLike, IO[bytes]]
MAP_LOCATION = Optional[Union[Callable, torch.device, str, Dict[str, str]]]

logger = logging.getLogger(__name__)

# ==================== Custom Pickle Module ====================
def create_custom_pickle_module(replace):
    """
    Create custom pickle module
    
    Args:
        replace: Class name replacement dictionary, e.g. {"DetectV5": "Detect"}
    
    Returns:
        Custom pickle module
    
    Example:
        pickle_module = create_custom_pickle_module({"DetectV5": "Detect"})
        model = custom_load('model.pt', pickle_module=pickle_module)
    """
    class CustomUnpicklerWrapper(pickle.Unpickler):
        def __init__(self, file, **kwargs):
            super().__init__(file, **kwargs)  # Initialize parent class, necessary!
            self.get_target_modules_path(replace)

        def get_all_classes_from_init(self, module_path): 
            """Get all classes from __all__ in specified module"""
            try:
                mod = importlib.import_module(module_path)
                classes = []
                for name in getattr(mod, '__all__', []):
                    attr = getattr(mod, name, None)
                    if inspect.isclass(attr):
                        classes.append(f"{attr.__module__}.{attr.__qualname__}")
                return classes
            except ImportError:
                print(f"Warning: Cannot import module {module_path}")

                return []

        def to_suffix_dict(self, lst):
            """Convert list to dictionary with last part as key"""
            return {item.split('.')[-1]: item for item in lst}

        def get_target_modules_path(self, replace: dict):
            """Get target module paths"""
            # Get classes from custom modules
            # path = self.get_all_classes_from_init("yolo.nn.modules") + self.get_all_classes_from_init("yolo.nn.models")
            path = self.get_all_classes_from_init("nxva.yolo.nn.modules") + self.get_all_classes_from_init("nxva.yolo.nn.models")
            self.modules_dict = self.to_suffix_dict(path)

            # Add mappings instead of replacing
            # replace format: {'Detect': 'DetectV5', 'Model': 'DetectionModel'}
            # meaning: add Detect -> modules_dict['DetectV5'] mapping
            for source_key, target_key in replace.items():
                if target_key in self.modules_dict:
                    # Add new mapping: source_key -> target_key corresponding module path
                    self.modules_dict[source_key] = self.modules_dict[target_key]
                    print(f"Added mapping: {source_key} -> {self.modules_dict[target_key]}")
                else:
                    print(f"Warning: Target key {target_key} not found, skipping {source_key} mapping")            

        def find_class(self, mod_name, name):
            """Core method for finding classes"""
            print(f'Looking for class: {mod_name}.{name}')
            # Handle Storage types
            if type(name) is str and 'Storage' in name:
                try:
                    # Let parent handle Storage types
                    pass
                except KeyError:
                    pass
            
            # Extract last part of class name for comparison
            # Example: ultralytics.nn.modules.conv.Conv => Conv
            class_name = name.split('.')[-1] if '.' in name else name
            print(class_name, 'class_name')

            # Check if in our custom module dictionary
            if class_name in self.modules_dict:
                target_path = self.modules_dict[class_name]
                target_mod_name = '.'.join(target_path.split('.')[:-1])
                target_class_name = target_path.split('.')[-1]
                
                print(f'Mapping: {mod_name}.{name} -> {target_mod_name}.{target_class_name}')
                try:
                    return super().find_class(target_mod_name, target_class_name)
                except (ImportError, AttributeError) as e:
                    print(f'Mapping failed: {e}, using original path')
            
            # If no mapping found, use original module and class name
            return super().find_class(mod_name, name)

    class CustomModule:
        Unpickler = CustomUnpicklerWrapper  

    return CustomModule


# ==================== Utility Functions ====================
class SerializationUtils:
    """Serialization utility class"""
    
    @staticmethod
    def decode_ascii(bytes_str: Union[bytes, str]) -> str:
        """
        Decode bytes string to ascii format
        
        Args:
            bytes_str: String or bytes to decode
            
        Returns:
            Decoded string
        """
        if isinstance(bytes_str, bytes):
            return bytes_str.decode('ascii')
        return bytes_str
    
    @staticmethod
    def default_restore_location(storage, location: str):
        """
        Default storage location restoration function
        
        Args:
            storage: Storage object
            location: Location label
            
        Returns:
            Restored storage object
        """
        if location == 'cpu':
            return storage
        
        # Try to move to CPU
        try:
            if hasattr(storage, 'cpu'):
                return storage.cpu()
        except Exception:
            pass
        
        return storage
    
    @staticmethod
    def get_restore_location(map_location: MAP_LOCATION) -> Callable:
        """
        Get storage location restoration function
        
        Args:
            map_location: Map location parameter
            
        Returns:
            Location restoration function
        """
        if map_location is None:
            return SerializationUtils.default_restore_location
        
        if isinstance(map_location, dict):
            def restore_location(storage, location):
                location = map_location.get(location, location)
                return SerializationUtils.default_restore_location(storage, location)
            return restore_location
        
        if isinstance(map_location, str):
            def restore_location(storage, location):
                return SerializationUtils.default_restore_location(storage, map_location)
            return restore_location
        
        if isinstance(map_location, torch.device):
            def restore_location(storage, location):
                return SerializationUtils.default_restore_location(storage, str(map_location))
            return restore_location
        
        # Custom mapping function
        def restore_location(storage, location):
            result = map_location(storage, location)
            if result is None:
                result = SerializationUtils.default_restore_location(storage, location)
            return result
        
        return restore_location


# ==================== Storage Type Handling ====================
class StorageType:
    """
    Storage type handling class
    
    Used for handling different types of storage objects
    """
    
    def __init__(self, name: str):
        """
        Initialize storage type
        
        Args:
            name: Storage type name
        """
        self.dtype = _get_dtype_from_pickle_storage_type(name)
    
    def __str__(self) -> str:
        return f'StorageType(dtype={self.dtype})'
    
    def __repr__(self) -> str:
        return self.__str__()


# ==================== Core Loading Functionality ====================
class ModelLoader:
    """Model loader class"""
    
    def __init__(self, zip_file, map_location: MAP_LOCATION, pickle_module: Any):
        """
        Initialize model loader
        
        Args:
            zip_file: Zip file object
            map_location: Device mapping location
            pickle_module: Pickle module for deserialization
        """
        self.zip_file = zip_file
        self.map_location = map_location
        self.pickle_module = pickle_module
        self.restore_location = SerializationUtils.get_restore_location(map_location)
        self.loaded_storages = {}
        
        # Module mapping configuration
        self.module_mappings = {
            'torch.tensor': 'torch._tensor'
        }
    
    def load_tensor(self, dtype: torch.dtype, numel: int, key: str, location: str) -> None:
        """
        Load tensor data
        
        Args:
            dtype: Data type
            numel: Number of elements
            key: Storage key
            location: Storage location
        """
        name = f'data/{key}'
        storage = self.zip_file.get_storage_from_record(name, numel, torch.UntypedStorage).storage().untyped()
        self.loaded_storages[key] = torch.storage.TypedStorage(
            wrap_storage=self.restore_location(storage, location),
            dtype=dtype
        )
    
    def persistent_load(self, saved_id: tuple) -> Any:
        """
        Persistent load function
        
        Args:
            saved_id: Saved ID tuple
            
        Returns:
            Loaded storage object
        """
        if not isinstance(saved_id, tuple):
            raise ValueError(f"Expected tuple, got {type(saved_id)}")
        
        typename = SerializationUtils.decode_ascii(saved_id[0])
        data = saved_id[1:]
        
        if typename != 'storage':
            raise ValueError(f"Unknown typename for persistent_load: '{typename}', expected 'storage'")
        
        storage_type, key, location, numel = data
        
        # Determine data type
        if storage_type is torch.UntypedStorage:
            dtype = torch.uint8
        else:
            dtype = storage_type.dtype
        
        # Load storage if not already loaded
        if key not in self.loaded_storages:
            nbytes = numel * torch._utils._element_size(dtype)
            self.load_tensor(dtype, nbytes, key, SerializationUtils.decode_ascii(location))
        
        return self.loaded_storages[key]
    
    def create_unpickler(self, data_file: IO[bytes], **pickle_load_args) -> Any:
        """
        Create custom Unpickler
        
        Args:
            data_file: Data file object
            **pickle_load_args: Pickle load arguments
            
        Returns:
            Configured Unpickler instance
        """
        class CustomUnpicklerWrapper(self.pickle_module.Unpickler):
            def __init__(self, file, **kwargs):
                super().__init__(file, **kwargs)
                self.loader = None  # Will be set externally
            
            def find_class(self, mod_name: str, name: str) -> Any:
                """
                Find class method - calls custom pickle module logic
                
                Args:
                    mod_name: Module name
                    name: Class name
                    
                Returns:
                    Found class object
                """
                # Handle Storage types
                if isinstance(name, str) and 'Storage' in name:
                    try:
                        return StorageType(name)
                    except KeyError:
                        pass
                
                # Apply module mapping 
                mapped_mod_name = self.loader.module_mappings.get(mod_name, mod_name)
                
                # Call parent method
                return super().find_class(mapped_mod_name, name)
        
        unpickler = CustomUnpicklerWrapper(data_file, **pickle_load_args)
        unpickler.loader = self
        unpickler.persistent_load = self.persistent_load
        
        return unpickler
    
    def load(self, pickle_file: str = 'data.pkl', **pickle_load_args) -> Any:
        """
        Execute actual model loading
        
        Args:
            pickle_file: Pickle file name
            **pickle_load_args: Pickle load arguments
            
        Returns:
            Loaded model object
        """
        # Prepare data file
        data_file = io.BytesIO(self.zip_file.get_record(pickle_file))
        
        # Create and configure unpickler
        unpickler = self.create_unpickler(data_file, **pickle_load_args)
        
        # Load model
        result = unpickler.load()
        
        # Validate sparse tensors (if available)
        if hasattr(torch._utils, '_validate_loaded_sparse_tensors'):
            torch._utils._validate_loaded_sparse_tensors()
        
        return result


# ==================== Main API Function ====================
def custom_load(
    f: FILE_LIKE,
    map_location: MAP_LOCATION = None,
    pickle_module: Any = None,
    **pickle_load_args: Any,
) -> Any:
    """
    Custom model loading function
    
    This function provides an alternative to torch.load, supporting custom pickle modules,
    especially suitable for scenarios requiring module path mapping, such as YOLOv5 and YOLOv11 models.
    
    Args:
        f: File path or file object
        map_location: Device mapping location, can be:
            - None: Use default location
            - str: Device string (e.g. 'cpu', 'cuda:0')
            - torch.device: Device object
            - dict: Location mapping dictionary
            - callable: Custom mapping function
        pickle_module: Custom pickle module, usually created by create_custom_pickle_module
        **pickle_load_args: Additional arguments passed to pickle.load
        
    Returns:
        Loaded model object
        
    Raises:
        FileNotFoundError: File does not exist
        RuntimeError: Error occurred during loading
        
    Example:
        >>> pickle_module = create_custom_pickle_module({"DetectV5": "Detect"})
        >>> model = custom_load('model.pt', pickle_module=pickle_module)
    """
    # Set default parameters
    if pickle_module is None:
        pickle_module = pickle
    
    if 'encoding' not in pickle_load_args:
        pickle_load_args['encoding'] = 'utf-8'
    
    # Validate file exists
    if isinstance(f, (str, os.PathLike)) and not os.path.exists(f):
        raise FileNotFoundError(f"Model file not found: {f}")
    
    # Create PyTorchFileReader and load
    zip_file = None
    try:
        zip_file = torch._C.PyTorchFileReader(f)
        loader = ModelLoader(zip_file, map_location, pickle_module)
        return loader.load(**pickle_load_args)
    
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}") from e
    
    finally:
        # Clean up resources
        if zip_file is not None and hasattr(zip_file, 'close'):
            zip_file.close()

IMG_FORMATS = "bmp", "dng", "jpeg", "jpg", "mpo", "png", "tif", "tiff", "webp", "pfm"  # include image suffixes
VID_FORMATS = "asf", "avi", "gif", "m4v", "mkv", "mov", "mp4", "mpeg", "mpg", "ts", "wmv"  # include video suffixes
class LoadImages:
    """YOLOv5 image/video dataloader, i.e. `python detect.py --source image.jpg/vid.mp4`."""

    def __init__(self, path, vid_stride=1):
        """Initializes YOLOv5 loader for images/videos, supporting glob patterns, directories, and lists of paths."""
        
        # Handle different types of input
        self.input_type = None
        self.numpy_images = None
        
        # Check if input is a .txt file
        if isinstance(path, str) and Path(path).suffix == ".txt":
            if not os.path.isfile(path):
                raise FileNotFoundError(f"File not found: {path}")
            
            # Read .txt file and parse paths
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Clean and filter empty lines
                paths = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comment lines
                        paths.append(line)
                
                if not paths:
                    raise ValueError(f"No valid paths found in txt file {path}")
                
                print(f"Read {len(paths)} paths from {path}")
                
                # Set path list as string list input
                self.input_type = "string_list"
                self.string_paths = paths
                self.files = paths
                self.nf = len(paths)
                self.video_flag = []
                self.mode = "image"
                self.vid_stride = vid_stride
                self.cap = None
                
                # Check if each path is a video
                for p in paths:
                    if p.split(".")[-1].lower() in VID_FORMATS:
                        self.video_flag.append(True)
                    else:
                        self.video_flag.append(False)
                
                # If there are videos, initialize the first video
                video_paths = [p for i, p in enumerate(paths) if self.video_flag[i]]
                if video_paths:
                    self._new_video(video_paths[0])
                
                return
                
            except Exception as e:
                raise ValueError(f"Error reading .txt file: {str(e)}")
        
        # Check if input is a list
        if isinstance(path, list):
            if len(path) == 0:
                raise ValueError("Input list cannot be empty")
            
            # Check type of first element
            first_element = path[0]
            
            if isinstance(first_element, str):
                # String list - process all paths
                self.input_type = "string_list"
                self.string_paths = path  # Save all paths
                print(f"Detected string list with {len(path)} paths")
                # Set basic attributes
                self.files = path
                self.nf = len(path)
                self.video_flag = []
                self.mode = "image"
                self.vid_stride = vid_stride
                self.cap = None
                
                # Check if each path is a video
                for p in path:
                    if p.split(".")[-1].lower() in VID_FORMATS:
                        self.video_flag.append(True)
                    else:
                        self.video_flag.append(False)
                
                # If there are videos, initialize the first video
                video_paths = [p for i, p in enumerate(path) if self.video_flag[i]]
                if video_paths:
                    self._new_video(video_paths[0])
                
                return
            elif isinstance(first_element, np.ndarray):
                # Numpy array list - return the entire list directly
                self.input_type = "numpy_list"
                self.numpy_images = path  # Save the entire numpy list
                print(f"Detected numpy array list with {len(path)} arrays")
                # Set basic attributes
                self.files = [f"numpy_array_{i}" for i in range(len(path))]
                self.nf = len(path)
                self.video_flag = [False] * len(path)
                self.mode = "image"
                self.vid_stride = vid_stride
                self.cap = None
                return
            else:
                raise ValueError(f"Unsupported list element type: {type(first_element)}")
        
        # Original file path processing logic
        files = []
        for p in sorted(path) if isinstance(path, (list, tuple)) else [path]:
            p = str(Path(p).resolve())
            if "*" in p:
                files.extend(sorted(glob.glob(p, recursive=True)))  # glob
            elif os.path.isdir(p):
                files.extend(sorted(glob.glob(os.path.join(p, "*.*"))))  # dir
            elif os.path.isfile(p):
                files.append(p)  # files
            else:
                raise FileNotFoundError(f"{p} does not exist")

        images = [x for x in files if x.split(".")[-1].lower() in IMG_FORMATS]
        videos = [x for x in files if x.split(".")[-1].lower() in VID_FORMATS]
        ni, nv = len(images), len(videos)
        self.files = images + videos
        self.nf = ni + nv  # number of files
        self.video_flag = [False] * ni + [True] * nv
        self.mode = "image"
        self.vid_stride = vid_stride  # video frame-rate stride
        if any(videos):
            self._new_video(videos[0])  # new video
        else:
            self.cap = None
        assert self.nf > 0, (
            f"No images or videos found in {p}. Supported formats are:\nimages: {IMG_FORMATS}\nvideos: {VID_FORMATS}"
        )

    def __iter__(self):
        """Initializes iterator by resetting count and returns the iterator object itself."""
        self.count = 0
        return self

    def __next__(self):
        """Advances to the next file in the dataset, raising StopIteration if at the end."""
        if self.count == self.nf:
            raise StopIteration
        
        # Handle numpy array input
        if self.input_type == "numpy_list":
            if self.count >= len(self.numpy_images):
                raise StopIteration
            im0 = self.numpy_images[self.count]
            self.count += 1
            return im0
        
        # Handle string list input
        if self.input_type == "string_list":
            if self.count >= len(self.string_paths):
                raise StopIteration
            
            path = self.string_paths[self.count]
            
            if self.video_flag[self.count]:
                # Handle video file (this logic may need more complex state management)
                # Simplified handling: directly read first frame
                cap = cv2.VideoCapture(path)
                ret, im0 = cap.read()
                cap.release()
                if not ret:
                    raise ValueError(f"Cannot read video: {path}")
                self.count += 1
                return im0
            else:
                # Handle image file
                im0 = cv2.imread(path)
                if im0 is None:
                    raise ValueError(f"Cannot read image: {path}")
                self.count += 1
                return im0
        
        # Original file processing logic
        path = self.files[self.count]

        if self.video_flag[self.count]:
            # Read video
            self.mode = "video"
            for _ in range(self.vid_stride):
                self.cap.grab()
            ret_val, im0 = self.cap.retrieve()
            while not ret_val:
                self.count += 1
                self.cap.release()
                if self.count == self.nf:  # last video
                    raise StopIteration
                path = self.files[self.count]
                self._new_video(path)
                ret_val, im0 = self.cap.read()

            self.frame += 1
            # im0 = self._cv2_rotate(im0)  # for use if cv2 autorotation is False
            s = f"video {self.count + 1}/{self.nf} ({self.frame}/{self.frames}) {path}: "

        else:
            # Read image
            self.count += 1
            im0 = cv2.imread(path)  # BGR
            assert im0 is not None, f"Image Not Found {path}"
            s = f"image {self.count}/{self.nf} {path}: "

        # return path, im0, self.cap, s
        return im0


    def _new_video(self, path):
        """Initializes a new video capture object with path, frame count adjusted by stride, and orientation
        metadata.
        """
        self.frame = 0
        self.cap = cv2.VideoCapture(path)
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.vid_stride)
        self.orientation = int(self.cap.get(cv2.CAP_PROP_ORIENTATION_META))  # rotation degrees
        # self.cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 0)  # disable https://github.com/ultralytics/yolov5/issues/8493

    def _cv2_rotate(self, im):
        """Rotates a cv2 image based on its orientation; supports 0, 90, and 180 degrees rotations."""
        if self.orientation == 0:
            return cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
        elif self.orientation == 180:
            return cv2.rotate(im, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.orientation == 90:
            return cv2.rotate(im, cv2.ROTATE_180)
        return im

    def get_all_images(self):
        """Returns a list of all images, including all frames from image files and video files.
        
        Returns:
            List[np.ndarray]: List containing all image frames, each element is a numpy array
        """
        # If input is numpy array list, return directly
        if self.input_type == "numpy_list":
            print(f"Returning numpy array list with {len(self.numpy_images)} arrays")
            return self.numpy_images
        
        # If input is string list, process all paths directly
        if self.input_type == "string_list":
            all_images = []
            for i, image_path in enumerate(self.string_paths):
                if self.video_flag[i]:
                    # Handle video file - read all frames
                    cap = cv2.VideoCapture(image_path)
                    
                    frame_count = 0
                    while True:
                        # Skip frames according to vid_stride
                        for _ in range(self.vid_stride):
                            ret = cap.grab()
                            if not ret:
                                break
                        
                        ret, frame = cap.retrieve()
                        if not ret:
                            break
                        
                        all_images.append(frame)
                        frame_count += 1
                    
                    cap.release()
                    print(f"Extracted {frame_count} frames from video {image_path}")
                else:
                    # Handle image file
                    img = cv2.imread(image_path)
                    if img is not None:
                        all_images.append(img)
                    else:
                        print(f"Warning: Cannot read image {image_path}")
            
            print(f"Total loaded {len(all_images)} images")
            return all_images
        
        # Original file processing logic
        all_images = []
        
        for i in range(self.nf):
            if self.video_flag[i]:
                # Handle video file - read all frames
                video_path = self.files[i]
                cap = cv2.VideoCapture(video_path)
                
                frame_count = 0
                while True:
                    # Skip frames according to vid_stride
                    for _ in range(self.vid_stride):
                        ret = cap.grab()
                        if not ret:
                            break
                    
                    ret, frame = cap.retrieve()
                    if not ret:
                        break
                    
                    all_images.append(frame)
                    frame_count += 1
                
                cap.release()
                print(f"Extracted {frame_count} frames from video {video_path}")
                
            else:
                # Handle image file
                image_path = self.files[i]
                img = cv2.imread(image_path)
                if img is not None:
                    all_images.append(img)
                else:
                    print(f"Warning: Cannot read image {image_path}")
        
        print(f"Total loaded {len(all_images)} images")
        return all_images

    def __len__(self):
        """Returns the number of files in the dataset."""
        return self.nf  # number of files

def load_config(config: Union[str]) -> dict:
    """載入配置"""
    if isinstance(config, str) and config.endswith(('yaml', 'yml')):
        try:
            with open(config, 'r') as f:
                setting = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Error loading config: {e}")
    
    # 特殊處理：將 kpt_shape 從列表轉換為 tuple
    if 'kpt_shape' in setting and isinstance(setting['kpt_shape'], list):
        setting['kpt_shape'] = tuple(setting['kpt_shape'])
    return setting

# def load_images(path: str, vid_stride: int = 1):
#     from .utils import LoadImages
    
#     loader = LoadImages(path=path, vid_stride=vid_stride)
#     # 獲取所有圖像
#     all_images = loader.get_all_images()  # 返回 [img1, img2, img3, ...]
#     return all_images