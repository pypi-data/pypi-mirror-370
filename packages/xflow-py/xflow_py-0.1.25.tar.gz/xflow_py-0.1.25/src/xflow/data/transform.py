"""Pipeline transformation utilities for data preprocessing."""

import itertools
import logging
import random
from functools import partial
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
)

import numpy as np
from PIL import Image

from ..utils.decorator import with_progress
from ..utils.typing import ImageLike, PathLikeStr, TensorLike
from .pipeline import BasePipeline

# Only for type checkers; won't import torch at runtime
if TYPE_CHECKING:
    from torch.utils.data import Dataset as TorchDataset  # noqa: F401

# Runtime-safe base: real Dataset if available, else a stub so this module imports fine
try:
    from torch.utils.data import Dataset as _TorchDataset  # type: ignore
except Exception:

    class _TorchDataset:  # minimal stub
        pass


def _copy_pipeline_attributes(target: "BasePipeline", source: BasePipeline) -> None:
    """Helper function to copy essential attributes from source to target pipeline.

    This ensures all pipeline wrappers maintain the same interface as BasePipeline.
    """
    target.data_provider = source.data_provider
    target.transforms = source.transforms
    target.logger = source.logger
    target.skip_errors = source.skip_errors
    target.error_count = source.error_count


@with_progress
def apply_transforms_to_dataset(
    data: Iterable[Any],
    transforms: List[Callable],
    *,
    logger: Optional[logging.Logger] = None,
    skip_errors: bool = True,
) -> Tuple[List[Any], int]:
    """Apply sequential transforms to dataset items."""
    logger = logger or logging.getLogger(__name__)
    processed_items = []
    error_count = 0

    for item in data:
        try:
            for transform in transforms:
                item = transform(item)
            processed_items.append(item)
        except Exception as e:
            error_count += 1
            logger.warning(f"Failed to process item: {e}")
            if not skip_errors:
                raise

    return processed_items, error_count


class ShufflePipeline(BasePipeline):
    """Memory-efficient shuffle using reservoir sampling."""

    def __init__(self, base: BasePipeline, buffer_size: int) -> None:
        _copy_pipeline_attributes(self, base)
        self.base = base
        self.buffer_size = buffer_size

    def __iter__(self) -> Iterator[Any]:
        it = self.base.__iter__()
        buf = list(itertools.islice(it, self.buffer_size))
        random.shuffle(buf)

        for x in buf:
            yield x

        for x in it:
            buf[random.randrange(self.buffer_size)] = x
            random.shuffle(buf)
            yield buf.pop()

    def __len__(self) -> int:
        return len(self.base)

    def sample(self, n: int = 5) -> List[Any]:
        """Return up to n preprocessed items for inspection."""
        return list(itertools.islice(self.__iter__(), n))

    def reset_error_count(self) -> None:
        """Reset the error count to zero."""
        self.error_count = 0
        self.base.reset_error_count()

    def to_framework_dataset(self) -> Any:
        return self.base.to_framework_dataset().shuffle(self.buffer_size)


class BatchPipeline(BasePipeline):
    """Groups items into fixed-size batches."""

    def __init__(self, base: BasePipeline, batch_size: int) -> None:
        _copy_pipeline_attributes(self, base)
        self.base = base
        self.batch_size = batch_size

    def __iter__(self) -> Iterator[List[Any]]:
        it = self.base.__iter__()
        while True:
            batch = list(itertools.islice(it, self.batch_size))
            if not batch:
                break
            yield batch

    def __len__(self) -> int:
        return (len(self.base) + self.batch_size - 1) // self.batch_size

    def sample(self, n: int = 5) -> List[Any]:
        """Return up to n preprocessed items for inspection."""
        return list(itertools.islice(self.__iter__(), n))

    def reset_error_count(self) -> None:
        """Reset the error count to zero."""
        self.error_count = 0
        self.base.reset_error_count()

    def unbatch(self) -> BasePipeline:
        """Return the underlying pipeline yielding individual items (no batch dimension)."""
        return self.base

    def batch(self, batch_size: int) -> "BatchPipeline":
        """Return a new BatchPipeline with the specified batch size."""
        return BatchPipeline(self, batch_size)

    def to_framework_dataset(self) -> Any:
        return self.base.to_framework_dataset().batch(self.batch_size)


class TransformRegistry:
    """Registry for all available transforms."""

    _transforms: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(func):
            cls._transforms[name] = func
            return func

        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._transforms:
            raise ValueError(
                f"Transform '{name}' not found. Available: {list(cls._transforms.keys())}"
            )
        return cls._transforms[name]

    @classmethod
    def list_transforms(cls) -> List[str]:
        return list(cls._transforms.keys())


# Core transforms
@TransformRegistry.register("load_image")
def load_image(path: PathLikeStr) -> Image.Image:
    """Load image from file path."""
    return Image.open(Path(path))


@TransformRegistry.register("to_narray")
def to_numpy_array(image: ImageLike) -> np.ndarray:
    """Convert image to numpy array."""
    if hasattr(image, "numpy"):  # TensorFlow tensor
        return image.numpy()
    elif isinstance(image, Image.Image):  # PIL Image
        return np.array(image)
    elif hasattr(image, "__array__"):  # Array-like objects
        return np.asarray(image)
    else:
        raise ValueError(f"Cannot convert {type(image)} to numpy array")


@TransformRegistry.register("to_grayscale")
def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert image to grayscale using channel averaging."""
    if len(image.shape) == 2:
        return image
    elif len(image.shape) == 3:
        return np.mean(image, axis=2).astype(image.dtype)
    elif len(image.shape) == 4:
        if image.shape[2] == 4:  # RGBA format (H, W, 4)
            return np.mean(image[:, :, :3], axis=2).astype(image.dtype)
        elif image.shape[3] == 4:  # RGBA format (H, W, 1, 4)
            return np.mean(image[:, :, 0, :3], axis=2).astype(image.dtype)
        else:
            return np.mean(image.reshape(image.shape[:2] + (-1,)), axis=2).astype(
                image.dtype
            )
    else:
        spatial_dims = image.shape[:2]
        flattened = image.reshape(spatial_dims + (-1,))
        return np.mean(flattened, axis=2).astype(image.dtype)


@TransformRegistry.register("remap_range")
def remap_range(
    image: np.ndarray,
    current_min: float = 0.0,
    current_max: float = 255.0,
    target_min: float = 0.0,
    target_max: float = 1.0,
) -> np.ndarray:
    """Remap pixel values from [current_min, current_max] to [target_min, target_max]."""
    image = image.astype(np.float32)
    denominator = current_max - current_min
    if denominator == 0:
        return np.full_like(image, target_min, dtype=np.float32)
    normalized = (image - current_min) / denominator
    remapped = normalized * (target_max - target_min) + target_min
    return remapped.astype(np.float32)


@TransformRegistry.register("resize")
def resize(
    image: np.ndarray, size: Tuple[int, int], interpolation: str = "lanczos"
) -> np.ndarray:
    """Resize image using OpenCV."""
    import cv2

    target_height, target_width = size

    interp_map = {
        "lanczos": cv2.INTER_LANCZOS4,
        "cubic": cv2.INTER_CUBIC,
        "area": cv2.INTER_AREA,
        "linear": cv2.INTER_LINEAR,
        "nearest": cv2.INTER_NEAREST,
    }

    cv_interpolation = interp_map.get(interpolation, cv2.INTER_LANCZOS4)
    return cv2.resize(
        image, (target_width, target_height), interpolation=cv_interpolation
    )


@TransformRegistry.register("expand_dims")
def expand_dims(image: np.ndarray, axis: int = -1) -> np.ndarray:
    """Add a dimension of size 1 at the specified axis."""
    return np.expand_dims(image, axis=axis)


@TransformRegistry.register("squeeze")
def squeeze(image: np.ndarray, axis: Optional[Tuple[int, ...]] = None) -> np.ndarray:
    """Remove dimensions of size 1 from the array."""
    return np.squeeze(image, axis=axis)


@TransformRegistry.register("split_width")
def split_width(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Split image at width midpoint."""
    height, width = image.shape[:2]
    mid_point = width // 2
    return image[:, :mid_point], image[:, mid_point:]


# TensorFlow transforms
@TransformRegistry.register("tf_read_file")
def tf_read_file(file_path: str) -> TensorLike:
    """Read file contents as bytes using TensorFlow. tf only supports string paths."""
    import tensorflow as tf

    return tf.io.read_file(file_path)


@TransformRegistry.register("tf_decode_image")
def tf_decode_image(
    image_bytes: TensorLike, channels: int = 1, expand_animations: bool = False
) -> TensorLike:
    """Decode image bytes to tensor with specified channels."""
    import tensorflow as tf

    return tf.image.decode_image(
        image_bytes, channels=channels, expand_animations=expand_animations
    )


@TransformRegistry.register("tf_convert_image_dtype")
def tf_convert_image_dtype(image: TensorLike, dtype=None) -> TensorLike:
    """Convert image to specified dtype. and normalize to [0, 1] range."""
    import tensorflow as tf

    return tf.image.convert_image_dtype(image, tf.float32 if not dtype else dtype)


@TransformRegistry.register("tf_remap_range")
def tf_remap_range(
    image: TensorLike,
    current_min: float = 0.0,
    current_max: float = 255.0,
    target_min: float = 0.0,
    target_max: float = 1.0,
) -> TensorLike:
    """Remap pixel values from [current_min, current_max] to [target_min, target_max] using TensorFlow."""
    import tensorflow as tf

    image = tf.cast(image, tf.float32)
    # Avoid division by zero
    denominator = tf.where(
        tf.equal(current_max, current_min),
        tf.ones_like(current_max),
        current_max - current_min,
    )
    normalized = (image - current_min) / denominator
    remapped = normalized * (target_max - target_min) + target_min
    return remapped


@TransformRegistry.register("tf_resize")
def tf_resize(image: TensorLike, size: List[int]) -> TensorLike:
    """Resize image using TensorFlow."""
    import tensorflow as tf

    return tf.image.resize(image, size)


@TransformRegistry.register("tf_to_grayscale")
def tf_to_grayscale(image: TensorLike) -> TensorLike:
    """Convert image to grayscale, handling RGB, RGBA, and single-channel images."""
    import tensorflow as tf

    # Handle dynamic shapes properly
    rank = tf.rank(image)
    image = tf.cond(tf.equal(rank, 2), lambda: tf.expand_dims(image, -1), lambda: image)
    ch = tf.shape(image)[-1]

    def rgb_branch():
        rgb = image[..., :3]
        return tf.image.rgb_to_grayscale(rgb)

    def gray_branch():
        return image

    return tf.cond(tf.equal(ch, 1), gray_branch, rgb_branch)


@TransformRegistry.register("tf_split_width")
def tf_split_width(
    image: TensorLike, swap: bool = False
) -> Tuple[TensorLike, TensorLike]:
    """Split image at width midpoint using TensorFlow."""
    import tensorflow as tf

    width = tf.shape(image)[1]
    mid_point = width // 2
    left_half = image[:, :mid_point]
    right_half = image[:, mid_point:]

    if swap:
        return right_half, left_half
    return left_half, right_half


@TransformRegistry.register("tf_expand_dims")
def tf_expand_dims(image: TensorLike, axis: int = -1) -> TensorLike:
    """Add dimension to tensor."""
    import tensorflow as tf

    return tf.expand_dims(image, axis)


@TransformRegistry.register("tf_squeeze")
def tf_squeeze(image: TensorLike, axis: List[int] = None) -> TensorLike:
    """Remove dimensions of size 1."""
    import tensorflow as tf

    return tf.squeeze(image, axis)


def build_transforms_from_config(
    config: List[Dict[str, Any]], name_key: str = "name", params_key: str = "params"
) -> List[Callable]:
    """Build transform pipeline from configuration."""
    transforms = []
    for transform_config in config:
        if name_key not in transform_config:
            raise ValueError(
                f"Transform config missing '{name_key}' key: {transform_config}"
            )
        name = transform_config[name_key]
        params = transform_config.get(params_key, {})
        
        # Check if params has 'transforms' list (multi-branch pattern)
        if "transforms" in params and isinstance(params["transforms"], list):
            processed_params = params.copy()
            nested_transforms = []
            
            for nested_config in params["transforms"]:
                if nested_config is None:
                    nested_transforms.append(None)
                else:
                    nested_transforms.append(build_transform_closure(nested_config, name_key, params_key))
            
            processed_params["transforms"] = nested_transforms
            transform_fn = partial(TransformRegistry.get(name), **processed_params)
        else:
            # Regular transform - original behavior preserved
            transform_fn = TransformRegistry.get(name)
            if params:
                transform_fn = partial(transform_fn, **params)
        
        transforms.append(transform_fn)
    return transforms


class DatasetOperationRegistry:
    """Registry for dataset-level operations."""

    _operations: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(fn):
            cls._operations[name] = fn
            return fn

        return decorator

    @classmethod
    def get(cls, name: str):
        if name not in cls._operations:
            raise ValueError(f"Unknown dataset operation: {name}")
        return cls._operations[name]

    @classmethod
    def list_operations(cls):
        return list(cls._operations.keys())


# Dataset operations (applied to entire dataset)
@DatasetOperationRegistry.register("tf_batch")
def tf_batch(dataset, batch_size: int, drop_remainder: bool = False):
    """Group dataset elements into batches."""
    return dataset.batch(batch_size, drop_remainder=drop_remainder)


@DatasetOperationRegistry.register("tf_prefetch")
def tf_prefetch(dataset, buffer_size: int = None):
    """Prefetch data for better performance."""
    import tensorflow as tf

    if buffer_size is None:
        buffer_size = tf.data.AUTOTUNE
    return dataset.prefetch(buffer_size)


@DatasetOperationRegistry.register("tf_shuffle")
def tf_shuffle(dataset, buffer_size: int, seed: int = 42):
    """Randomly shuffle dataset elements."""
    return dataset.shuffle(buffer_size, seed=seed)


@DatasetOperationRegistry.register("tf_repeat")
def tf_repeat(dataset, count: int = None):
    """Repeat dataset for multiple epochs."""
    return dataset.repeat(count)


@DatasetOperationRegistry.register("tf_cache")
def tf_cache(dataset, filename: str = ""):
    """Cache dataset in memory or disk."""
    return dataset.cache(filename)


@DatasetOperationRegistry.register("tf_take")
def tf_take(dataset, count: int):
    """Take first count elements from dataset."""
    return dataset.take(count)


@DatasetOperationRegistry.register("tf_skip")
def tf_skip(dataset, count: int):
    """Skip first count elements from dataset."""
    return dataset.skip(count)


def apply_dataset_operations_from_config(
    dataset: Any,
    operations_config: List[Dict[str, Any]],
    name_key: str = "name",
    params_key: str = "params",
) -> Any:
    """Apply dataset operations from configuration."""
    for op_config in operations_config:
        if name_key not in op_config:
            raise ValueError(f"Operation config missing '{name_key}' key: {op_config}")
        name = op_config[name_key]
        params = op_config.get(params_key, {})
        operation = DatasetOperationRegistry.get(name)
        dataset = operation(dataset, **params)
    return dataset


# Text processing transforms
@TransformRegistry.register("add_prefix")
def add_prefix(text: str, prefix: str, separator: str = "") -> str:
    """Add prefix to text with optional separator."""
    return prefix + separator + text


@TransformRegistry.register("add_suffix")
def add_suffix(text: str, suffix: str, separator: str = "") -> str:
    """Add suffix to text with optional separator."""
    return text + separator + suffix


@TransformRegistry.register("to_uppercase")
def to_uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


@TransformRegistry.register("to_lowercase")
def to_lowercase(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()


@TransformRegistry.register("strip_whitespace")
def strip_whitespace(text: str, chars: str = None) -> str:
    """Strip whitespace or specified characters from both ends."""
    return text.strip(chars)


@TransformRegistry.register("replace_text")
def replace_text(text: str, old: str, new: str, count: int = -1) -> str:
    """Replace occurrences of old substring with new substring."""
    return text.replace(old, new, count)


@TransformRegistry.register("split_text")
def split_text(text: str, separator: str = None, maxsplit: int = -1) -> List[str]:
    """Split text into list of strings."""
    return text.split(separator, maxsplit)


@TransformRegistry.register("join_text")
def join_text(text_list: List[str], separator: str = "") -> str:
    """Join list of strings into single string."""
    return separator.join(text_list)


# TensorFlow native text transforms
@TransformRegistry.register("tf_add_prefix")
def tf_add_prefix(text: TensorLike, prefix: str, separator: str = "") -> TensorLike:
    """Add prefix to text tensor using TensorFlow."""
    import tensorflow as tf

    prefix_tensor = tf.constant(prefix + separator)
    return tf.strings.join([prefix_tensor, text])


@TransformRegistry.register("tf_add_suffix")
def tf_add_suffix(text: TensorLike, suffix: str, separator: str = "") -> TensorLike:
    """Add suffix to text tensor using TensorFlow."""
    import tensorflow as tf

    suffix_tensor = tf.constant(separator + suffix)
    return tf.strings.join([text, suffix_tensor])


@TransformRegistry.register("tf_to_uppercase")
def tf_to_uppercase(text: TensorLike) -> TensorLike:
    """Convert text tensor to uppercase using TensorFlow."""
    import tensorflow as tf

    return tf.strings.upper(text)


@TransformRegistry.register("tf_to_lowercase")
def tf_to_lowercase(text: TensorLike) -> TensorLike:
    """Convert text tensor to lowercase using TensorFlow."""
    import tensorflow as tf

    return tf.strings.lower(text)


@TransformRegistry.register("tf_strip_whitespace")
def tf_strip_whitespace(text: TensorLike) -> TensorLike:
    """Strip whitespace from text tensor using TensorFlow."""
    import tensorflow as tf

    return tf.strings.strip(text)


@TransformRegistry.register("tf_replace_text")
def tf_replace_text(text: TensorLike, old: str, new: str) -> TensorLike:
    """Replace substring in text tensor using TensorFlow."""
    import tensorflow as tf

    return tf.strings.regex_replace(text, old, new)


@TransformRegistry.register("tf_split_text")
def tf_split_text(text: TensorLike, separator: str = " ") -> TensorLike:
    """Split text tensor into tokens using TensorFlow."""
    import tensorflow as tf

    return tf.strings.split(text, separator)


@TransformRegistry.register("tf_join_text")
def tf_join_text(text_tokens: TensorLike, separator: str = "") -> TensorLike:
    """Join text tokens into single string using TensorFlow."""
    import tensorflow as tf

    return tf.strings.reduce_join(text_tokens, separator=separator)


@TransformRegistry.register("tf_string_length")
def tf_string_length(text: TensorLike) -> TensorLike:
    """Get length of text tensor using TensorFlow."""
    import tensorflow as tf

    return tf.strings.length(text)


@TransformRegistry.register("tf_substring")
def tf_substring(text: TensorLike, start: int, length: int) -> TensorLike:
    """Extract substring from text tensor using TensorFlow."""
    import tensorflow as tf

    return tf.strings.substr(text, start, length)


# PyTorch/torchvision transforms
@TransformRegistry.register("torch_load_image")
def torch_load_image(path: PathLikeStr) -> TensorLike:
    """Load image from file path using torchvision."""
    try:
        import torchvision.io

        return torchvision.io.read_image(str(path))
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_to_tensor")
def torch_to_tensor(image: ImageLike) -> TensorLike:
    """Convert image to PyTorch tensor."""
    try:
        import torch
        import torchvision.transforms.functional as F
        from PIL import Image

        if isinstance(image, Image.Image):
            return F.to_tensor(image)
        elif isinstance(image, np.ndarray):
            return torch.from_numpy(image).float()
        elif hasattr(image, "__array__"):
            return torch.from_numpy(np.asarray(image)).float()
        else:
            raise ValueError(f"Cannot convert {type(image)} to PyTorch tensor")
    except ImportError:
        raise RuntimeError("PyTorch not available")


@TransformRegistry.register("torch_to_pil")
def torch_to_pil(tensor: TensorLike) -> Image.Image:
    """Convert PyTorch tensor to PIL Image."""
    try:
        import torchvision.transforms.functional as F

        return F.to_pil_image(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_flatten")
def torch_flatten(
    tensor: TensorLike, 
    start_dim: int = 1, 
    end_dim: int = -1,
    make_contiguous: bool = True
) -> TensorLike:
    """Flatten tensor dimensions for vectorization (e.g., image serialization).
    
    This is the standard PyTorch approach for converting multi-dimensional tensors
    into vectors while preserving batch dimensions or other specified dimensions.
    Commonly used for:
    - Image vectorization: (B, C, H, W) -> (B, C*H*W)
    - Feature flattening: (B, H, W, C) -> (B, H*W*C) 
    - Complete flattening: (H, W, C) -> (H*W*C,)
    
    Args:
        tensor: Input PyTorch tensor to flatten
        start_dim: First dimension to flatten (inclusive). Default: 1 (preserve batch)
        end_dim: Last dimension to flatten (inclusive). Default: -1 (last dimension)
        make_contiguous: Whether to ensure output is contiguous in memory for better performance
    
    Returns:
        Flattened tensor with dimensions from start_dim to end_dim collapsed into a single dimension
    
    Examples:
        >>> # Image vectorization preserving batch: (32, 3, 224, 224) -> (32, 150528)
        >>> images = torch.randn(32, 3, 224, 224)
        >>> flattened = torch_flatten(images)  # start_dim=1 by default
        
        >>> # Complete flattening: (3, 224, 224) -> (150528,)
        >>> image = torch.randn(3, 224, 224) 
        >>> vector = torch_flatten(image, start_dim=0)
        
        >>> # Flatten spatial dimensions only: (32, 256, 7, 7) -> (32, 256, 49)
        >>> features = torch.randn(32, 256, 7, 7)
        >>> spatial_flat = torch_flatten(features, start_dim=2)
        
        >>> # Flatten everything except last dim: (32, 256, 7, 7) -> (114688, 7)
        >>> flattened = torch_flatten(features, start_dim=0, end_dim=2)
    """
    try:
        import torch
        
        # Use torch.flatten which is the standard and most efficient approach
        flattened = torch.flatten(tensor, start_dim=start_dim, end_dim=end_dim)
        
        # Ensure contiguous memory layout for better performance if requested
        if make_contiguous and not flattened.is_contiguous():
            flattened = flattened.contiguous()
            
        return flattened
        
    except ImportError:
        raise RuntimeError("PyTorch not available")


@TransformRegistry.register("torch_remap_range")
def torch_remap_range(
    tensor: TensorLike,
    current_min: float = 0.0,
    current_max: float = 255.0,
    target_min: float = 0.0,
    target_max: float = 1.0,
) -> TensorLike:
    """Remap tensor values from [current_min, current_max] to [target_min, target_max] using PyTorch."""
    try:
        import torch

        tensor = tensor.float()
        denominator = current_max - current_min
        if denominator == 0:
            return torch.full_like(tensor, target_min, dtype=torch.float32)
        normalized = (tensor - current_min) / denominator
        remapped = normalized * (target_max - target_min) + target_min
        return remapped
    except ImportError:
        raise RuntimeError("PyTorch not available")


@TransformRegistry.register("torch_resize")
def torch_resize(
    tensor: TensorLike, size: List[int], interpolation: str = "bilinear"
) -> TensorLike:
    """Resize tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F
        from torchvision.transforms import InterpolationMode

        interp_map = {
            "nearest": InterpolationMode.NEAREST,
            "bilinear": InterpolationMode.BILINEAR,
            "bicubic": InterpolationMode.BICUBIC,
            "lanczos": InterpolationMode.LANCZOS,
        }

        interp_mode = interp_map.get(interpolation, InterpolationMode.BILINEAR)
        return F.resize(tensor, size, interpolation=interp_mode)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_center_crop")
def torch_center_crop(tensor: TensorLike, size: List[int]) -> TensorLike:
    """Center crop tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.center_crop(tensor, size)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_random_crop")
def torch_random_crop(tensor: TensorLike, size: List[int]) -> TensorLike:
    """Random crop tensor using torchvision."""
    try:
        import torchvision.transforms as T

        transform = T.RandomCrop(size)
        return transform(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_horizontal_flip")
def torch_horizontal_flip(tensor: TensorLike) -> TensorLike:
    """Horizontally flip tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.hflip(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_vertical_flip")
def torch_vertical_flip(tensor: TensorLike) -> TensorLike:
    """Vertically flip tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.vflip(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_random_horizontal_flip")
def torch_random_horizontal_flip(tensor: TensorLike, p: float = 0.5) -> TensorLike:
    """Randomly horizontally flip tensor using torchvision."""
    try:
        import torchvision.transforms as T

        transform = T.RandomHorizontalFlip(p=p)
        return transform(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_random_vertical_flip")
def torch_random_vertical_flip(tensor: TensorLike, p: float = 0.5) -> TensorLike:
    """Randomly vertically flip tensor using torchvision."""
    try:
        import torchvision.transforms as T

        transform = T.RandomVerticalFlip(p=p)
        return transform(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_rotation")
def torch_rotation(
    tensor: TensorLike, angle: float, interpolation: str = "bilinear"
) -> TensorLike:
    """Rotate tensor by angle using torchvision."""
    try:
        import torchvision.transforms.functional as F
        from torchvision.transforms import InterpolationMode

        interp_map = {
            "nearest": InterpolationMode.NEAREST,
            "bilinear": InterpolationMode.BILINEAR,
            "bicubic": InterpolationMode.BICUBIC,
        }

        interp_mode = interp_map.get(interpolation, InterpolationMode.BILINEAR)
        return F.rotate(tensor, angle, interpolation=interp_mode)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_random_rotation")
def torch_random_rotation(tensor: TensorLike, degrees: List[float]) -> TensorLike:
    """Randomly rotate tensor using torchvision."""
    try:
        import torchvision.transforms as T

        transform = T.RandomRotation(degrees)
        return transform(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_to_grayscale")
def torch_to_grayscale(tensor: TensorLike, num_output_channels: int = 1) -> TensorLike:
    """Convert tensor to grayscale, handling tensors shaped (..., C, H, W) or (H, W). Supports 1/3/4 channels."""
    import torch
    import torchvision.transforms.functional as F

    if num_output_channels not in (1, 3):
        raise ValueError("num_output_channels must be 1 or 3.")

    # Normalize to have a channel dim
    if tensor.dim() == 2:  # (H, W)
        tensor = tensor.unsqueeze(0)  # (1, H, W)

    if tensor.dim() < 3:
        raise ValueError("Expected at least 3D tensor with channel dimension.")

    C = tensor.shape[-3]

    if C == 1:
        y = tensor
    elif C == 3:
        y = F.rgb_to_grayscale(tensor, num_output_channels=1)
    elif C == 4:
        y = F.rgb_to_grayscale(tensor[..., :3, :, :], num_output_channels=1)
    else:
        # Fallback: simple mean across channels
        y = (
            tensor.float().mean(dim=-3, keepdim=True).to(tensor.dtype)
            if tensor.is_floating_point()
            else tensor.mean(dim=-3, keepdim=True)
        )

    if num_output_channels == 3:
        y = y.repeat_interleave(3, dim=-3)

    return y


@TransformRegistry.register("torch_split_width")
def torch_split_width(
    tensor: TensorLike, swap: bool = False, width_dim: int = -1
) -> Tuple[TensorLike, TensorLike]:
    """Split tensor at width midpoint along specified dimension.

    Args:
        tensor: Input tensor to split
        swap: If True, return (right_half, left_half) instead of (left_half, right_half)
        width_dim: Dimension to split along (0, 1, 2, 3, etc. or -1 for last)

    Returns:
        Tuple of (left_half, right_half) or (right_half, left_half) if swap=True
    """
    try:
        import torch

        width = tensor.shape[width_dim]
        mid_point = width // 2

        left_half = torch.split(tensor, mid_point, dim=width_dim)[0]
        right_half = torch.split(tensor, mid_point, dim=width_dim)[1]

        if swap:
            return right_half, left_half
        return left_half, right_half
    except ImportError:
        raise RuntimeError("PyTorch not available")


@TransformRegistry.register("torch_adjust_brightness")
def torch_adjust_brightness(tensor: TensorLike, brightness_factor: float) -> TensorLike:
    """Adjust brightness of tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.adjust_brightness(tensor, brightness_factor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_adjust_contrast")
def torch_adjust_contrast(tensor: TensorLike, contrast_factor: float) -> TensorLike:
    """Adjust contrast of tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.adjust_contrast(tensor, contrast_factor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_adjust_saturation")
def torch_adjust_saturation(tensor: TensorLike, saturation_factor: float) -> TensorLike:
    """Adjust saturation of tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.adjust_saturation(tensor, saturation_factor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_adjust_hue")
def torch_adjust_hue(tensor: TensorLike, hue_factor: float) -> TensorLike:
    """Adjust hue of tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.adjust_hue(tensor, hue_factor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_gaussian_blur")
def torch_gaussian_blur(
    tensor: TensorLike, kernel_size: List[int], sigma: List[float] = None
) -> TensorLike:
    """Apply Gaussian blur to tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.gaussian_blur(tensor, kernel_size, sigma)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_pad")
def torch_pad(
    tensor: TensorLike,
    padding: List[int],
    fill: float = 0,
    padding_mode: str = "constant",
) -> TensorLike:
    """Pad tensor using torchvision."""
    try:
        import torchvision.transforms.functional as F

        return F.pad(tensor, padding, fill=fill, padding_mode=padding_mode)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_random_crop_resize")
def torch_random_crop_resize(
    tensor: TensorLike,
    size: List[int],
    scale: List[float] = (0.8, 1.0),
    ratio: List[float] = (0.75, 1.33),
) -> TensorLike:
    """Random crop and resize tensor using torchvision."""
    try:
        import torchvision.transforms as T

        transform = T.RandomResizedCrop(size, scale=scale, ratio=ratio)
        return transform(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_color_jitter")
def torch_color_jitter(
    tensor: TensorLike,
    brightness: float = 0,
    contrast: float = 0,
    saturation: float = 0,
    hue: float = 0,
) -> TensorLike:
    """Apply color jitter to tensor using torchvision."""
    try:
        import torchvision.transforms as T

        transform = T.ColorJitter(
            brightness=brightness, contrast=contrast, saturation=saturation, hue=hue
        )
        return transform(tensor)
    except ImportError:
        raise RuntimeError("torchvision not available")


@TransformRegistry.register("torch_permute")
def torch_permute(
    tensor, dims=None, format_from="BHWC", format_to="BCHW", make_contiguous=False
):
    """
    Permute tensor dims either explicitly (dims) or via format strings.
    Examples:
      torch_permute(x, dims=[0,3,1,2])           # BHWC -> BCHW
      torch_permute(x, format_from="BHWC", format_to="BCHW")
      torch_permute(x, format_from="HWC",  format_to="CHW")
    """
    import torch

    rank = tensor.dim()

    if dims is not None:
        if len(dims) != rank:
            raise ValueError(f"dims length {len(dims)} != tensor rank {rank}")
        if sorted(dims) != list(range(rank)):
            raise ValueError(f"dims must be a permutation of 0..{rank-1}, got {dims}")
        out = tensor.permute(*dims)
        return out.contiguous() if make_contiguous else out

    # Normalize format strings
    fr = "".join(format_from.split()).upper()
    to = "".join(format_to.split()).upper()

    if len(fr) != len(to):
        raise ValueError(f"format lengths differ: {fr} vs {to}")
    if len(fr) != rank:
        raise ValueError(f"format length {len(fr)} != tensor rank {rank}")
    if len(set(fr)) != len(fr) or len(set(to)) != len(to):
        raise ValueError("format chars must be unique (e.g., no repeated 'H')")
    if set(fr) != set(to):
        raise ValueError(f"formats must contain same symbols: {fr} vs {to}")

    # Build permutation: for each target char, find its index in source
    idx = [fr.index(ch) for ch in to]
    out = tensor.permute(*idx)
    return out.contiguous() if make_contiguous else out


@TransformRegistry.register("torch_squeeze")
def torch_squeeze(tensor: TensorLike, dim: Optional[int] = None) -> TensorLike:
    """Remove dimensions of size 1 from PyTorch tensor.
    
    This is the PyTorch equivalent of the numpy squeeze function, designed to 
    handle image channel squeezing operations like:
    - (256, 256, 1) -> (256, 256)  # Remove trailing single channel
    - (1, 256, 256) -> (256, 256)  # Remove leading single channel
    - (1, 1, 256, 256) -> (256, 256)  # Remove multiple single dimensions
    
    Args:
        tensor: Input PyTorch tensor
        dim: If given, only removes dimensions of size 1 at the specified dimension.
             If None, removes all dimensions of size 1.
    
    Returns:
        Squeezed tensor with single-size dimensions removed
    
    Examples:
        >>> # Remove trailing channel dimension: (H, W, 1) -> (H, W)
        >>> tensor = torch.randn(256, 256, 1)
        >>> squeezed = torch_squeeze(tensor, dim=2)  # or dim=-1
        
        >>> # Remove leading batch/channel dimension: (1, H, W) -> (H, W)
        >>> tensor = torch.randn(1, 256, 256)
        >>> squeezed = torch_squeeze(tensor, dim=0)
        
        >>> # Remove all single dimensions automatically
        >>> tensor = torch.randn(1, 256, 256, 1)
        >>> squeezed = torch_squeeze(tensor)  # -> (256, 256)
    """
    try:
        import torch
        
        if dim is not None:
            # Only squeeze the specified dimension if it has size 1
            if tensor.size(dim) == 1:
                return torch.squeeze(tensor, dim=dim)
            else:
                return tensor  # Return unchanged if dimension is not size 1
        else:
            # Squeeze all dimensions of size 1
            return torch.squeeze(tensor)
    except ImportError:
        raise RuntimeError("PyTorch not available")


@TransformRegistry.register("torch_unsqueeze")
def torch_unsqueeze(tensor: TensorLike, dim: int) -> TensorLike:
    """Add dimension to PyTorch tensor at specified position.
    
    This is the PyTorch equivalent of numpy's expand_dims function, useful for:
    - Adding batch dimension: (H, W, C) -> (1, H, W, C)
    - Adding channel dimension: (H, W) -> (H, W, 1)
    - Preparing tensors for operations that require specific dimensionality
    
    Args:
        tensor: Input PyTorch tensor
        dim: Position where the new axis is placed
    
    Returns:
        Tensor with an additional dimension of size 1 inserted at the specified position
    
    Examples:
        >>> # Add batch dimension at the beginning: (H, W, C) -> (1, H, W, C)
        >>> tensor = torch.randn(256, 256, 3)
        >>> batched = torch_unsqueeze(tensor, dim=0)
        
        >>> # Add channel dimension at the end: (H, W) -> (H, W, 1)
        >>> tensor = torch.randn(256, 256)
        >>> with_channel = torch_unsqueeze(tensor, dim=-1)
        
        >>> # Add dimension for broadcasting: (N,) -> (N, 1)
        >>> tensor = torch.randn(256, 256)
        >>> batched = torch_unsqueeze(tensor, dim=0)
    """
    try:
        import torch
        
        return torch.unsqueeze(tensor, dim=dim)
    except ImportError:
        raise RuntimeError("PyTorch not available")


@TransformRegistry.register("torch_debug_shape")
def torch_debug_shape(
    tensor: TensorLike, 
    label: str = "tensor", 
    show_stats: bool = False,
    blocking: bool = False
) -> TensorLike:
    """Debug utility that prints tensor shape and passes data through unchanged.
    
    Useful for inspecting data flow in transform pipelines without modifying the data.
    Can be inserted anywhere in a pipeline to understand tensor dimensions.
    
    Args:
        tensor: Input PyTorch tensor (passed through unchanged)
        label: Descriptive label for the tensor (default: "tensor")
        show_stats: Whether to show additional statistics (mean, std, min, max)
        blocking: If True, waits for user input before continuing (useful for step-by-step debugging)
    
    Returns:
        The input tensor unchanged
    
    Examples:
        >>> # Basic shape debugging
        >>> x = torch.randn(32, 3, 224, 224)
        >>> x = torch_debug_shape(x, "after_loading")
        # Prints: "[DEBUG] after_loading: torch.Size([32, 3, 224, 224]) | dtype: float32"
        
        >>> # With statistics and blocking
        >>> x = torch_debug_shape(x, "normalized", show_stats=True, blocking=True)
        # Prints: "[DEBUG] normalized: torch.Size([32, 3, 224, 224]) | dtype: float32 | μ=0.02 σ=1.0 [min=-2.1, max=2.3]"
        # Waits: "Press Enter to continue..."
        
        >>> # Step-by-step pipeline debugging
        >>> x = torch_debug_shape(x, "critical_point", blocking=True)
        # Pauses execution to examine this specific step
    """
    try:
        import torch
        
        # Basic info
        shape_str = f"[DEBUG] {label}: {tensor.shape} | dtype: {tensor.dtype}"
        
        if show_stats and tensor.numel() > 0:
            if tensor.is_floating_point():
                mean_val = tensor.mean().item()
                std_val = tensor.std().item() if tensor.numel() > 1 else 0.0
                min_val = tensor.min().item()
                max_val = tensor.max().item()
                shape_str += f" | μ={mean_val:.2f} σ={std_val:.2f} [min={min_val:.1f}, max={max_val:.1f}]"
            else:
                min_val = tensor.min().item()
                max_val = tensor.max().item()
                shape_str += f" | range=[{min_val}, {max_val}]"
        
        print(shape_str)
        
        if blocking:
            input("Press Enter to continue...")
        
        return tensor
        
    except ImportError:
        print(f"[DEBUG] {label}: <torch not available>")
        if blocking:
            input("Press Enter to continue...")
        return tensor


@TransformRegistry.register("torch_shape")
def torch_shape(tensor: TensorLike, label: str = "") -> TensorLike:
    """Minimal shape debug utility - just prints shape and passes through.
    
    Ultra-simple version for quick debugging. Just prints the shape with 
    optional label and returns the tensor unchanged.
    
    Args:
        tensor: Input tensor (unchanged)
        label: Optional prefix label
    
    Returns:
        Input tensor unchanged
        
    Examples:
        >>> x = torch_shape(torch.randn(3, 224, 224), "input")
        # Prints: "input: (3, 224, 224)"
        
        >>> x = torch_shape(x)  # No label
        # Prints: "(3, 224, 224)"
    """
    try:
        import torch
        if label:
            print(f"{label}: {tuple(tensor.shape)}")
        else:
            print(f"{tuple(tensor.shape)}")
        return tensor
    except ImportError:
        print(f"{label}: <torch unavailable>" if label else "<torch unavailable>")
        return tensor


# PyTorch dataset operations
@DatasetOperationRegistry.register("torch_batch")
def torch_batch(
    dataset: "_TorchDataset",
    batch_size: int,
    drop_last: bool = False,
    shuffle: bool = False,
    num_workers: int = 0,
    pin_memory: bool = False,
    collate_fn: Optional[Any] = None,
    pin_memory_device: str = "",
    worker_init_fn=None,
    prefetch_factor: Optional[int] = None,
    seed: Optional[int] = None,   # <--- new
):
    """Wrap a dataset in a PyTorch DataLoader for batching with optional seed."""
    from torch.utils.data import DataLoader
    import torch

    generator = None
    if seed is not None:
        generator = torch.Generator()
        generator.manual_seed(int(seed))

        if worker_init_fn is None and num_workers > 0:
            def seed_worker(worker_id):
                worker_seed = torch.initial_seed() % 2**32
                np.random.seed(worker_seed)
                random.seed(worker_seed)
            worker_init_fn = seed_worker

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=drop_last,
        num_workers=num_workers,
        pin_memory=pin_memory,
        pin_memory_device=pin_memory_device,
        persistent_workers=(num_workers > 0),
        collate_fn=collate_fn,
        worker_init_fn=worker_init_fn,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
        generator=generator,   # <--- key for deterministic shuffle
    )


@DatasetOperationRegistry.register("torch_subset")
def torch_subset(dataset: "_TorchDataset", indices: List[int]):
    """Create a subset of a dataset using specified indices."""
    try:
        from torch.utils.data import Subset  # lazy import
    except Exception:
        raise RuntimeError("PyTorch not available")
    return Subset(dataset, indices)


@DatasetOperationRegistry.register("torch_concat")
def torch_concat(datasets: List["_TorchDataset"]):
    """Concatenate multiple datasets into one."""
    try:
        from torch.utils.data import ConcatDataset  # lazy import
    except Exception:
        raise RuntimeError("PyTorch not available")
    return ConcatDataset(datasets)


@DatasetOperationRegistry.register("torch_random_split")
def torch_random_split(
    dataset: "_TorchDataset", lengths: Sequence[int], generator=None
):
    """Randomly split a dataset into non-overlapping subsets."""
    try:
        from torch.utils.data import random_split  # lazy import
    except Exception:
        raise RuntimeError("PyTorch not available")
    return random_split(dataset, lengths, generator=generator)


@TransformRegistry.register("multi_transform")
def multi_transform(inputs, transforms):
    """Apply different transforms to multiple inputs.
    
    Args:
        inputs: tuple/list of inputs (e.g., from split operations)
        transforms: list of transform functions, one per input
        
    Returns:
        tuple of transformed outputs
    """
    if not isinstance(inputs, (tuple, list)):
        raise ValueError("inputs must be tuple or list")
    
    if len(inputs) != len(transforms):
        raise ValueError(f"Number of inputs ({len(inputs)}) must match transforms ({len(transforms)})")
    
    results = []
    for inp, transform in zip(inputs, transforms):
        if transform is not None:  # Allow None to mean "no transform"
            results.append(transform(inp))
        else:
            results.append(inp)
    
    return tuple(results)

def build_transform_closure(transform_config, name_key="name", params_key="params"):
    """Build a single transform function with preset parameters.
    
    Args:
        transform_config: dict with transform name and params
        
    Returns:
        Callable transform function with parameters bound
    """
    if isinstance(transform_config, str):
        # Simple case: just transform name, no params
        return TransformRegistry.get(transform_config)
    
    if name_key not in transform_config:
        raise ValueError(f"Transform config missing '{name_key}' key: {transform_config}")
    
    name = transform_config[name_key]
    params = transform_config.get(params_key, {})
    transform_fn = TransformRegistry.get(name)
    
    if params:
        return partial(transform_fn, **params)
    return transform_fn

@TransformRegistry.register("tuple_select")
def tuple_select(inputs, index=0):
    """Select specific item from tuple/list (useful after multi_transform)."""
    return inputs[index]

class TorchDataset(_TorchDataset):
    """Map-style Dataset wrapper for an indexable pipeline."""

    def __init__(self, pipeline):
        self.pipeline = pipeline  # expects __len__ and __getitem__

    def __len__(self):
        """Return number of samples in the pipeline."""
        return len(self.pipeline)

    def __getitem__(self, idx):
        """Return a single sample by index."""
        return self.pipeline[idx]
