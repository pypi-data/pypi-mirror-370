import dataclasses
from typing import Any, Dict

import numpy as np

from .model_config import Tensor
from .model_config.utils import TRITON_NUMERAL_NP_TYPES, np_to_triton_dtype

# TODO: use as a reference for the future (when front-end server will be implemented)
# https://github.com/bentoml/BentoML/blob/1b377af15b89cc97a037a2c3d26da79a7a71aa76/src/_bentoml_sdk/io_models.py#L103

# def mime_type(cls) -> str:
#     if cls.media_type is not None:
#         return cls.media_type
#     if not issubclass(cls, RootModel):
#         if cls.multipart_fields:
#             return "multipart/form-data"
#         return "application/json"
#     json_schema = cls.model_json_schema()
#     if json_schema.get("type") == "string":
#         return DEFAULT_TEXT_MEDIA_TYPE
#     elif json_schema.get("type") == "file":
#         if "content_type" in json_schema:
#             return json_schema["content_type"]
#         if (format := json_schema.get("format")) == "image":
#             return "image/*"
#         elif format == "audio":
#             return "audio/*"
#         elif format == "video":
#             return "video/*"
#         return "application/octet-stream"
#     return "application/json"

__all__ = [
    "BaseSignature",
    "ImageSignature",
    "TextSignature",
    "TensorSignature",
    "FileSignature",
]


@dataclasses.dataclass(frozen=False)
class BaseSignature(Tensor):
    signature_type: str = None
    external: bool = None

    def __post_init__(self):
        if self.signature_type is None and not hasattr(self, "signature_type"):
            raise ValueError("signature_type should be provided")
        if self.external is None and not hasattr(self, "external"):
            raise ValueError("external should be provided")

    def get_dict(self) -> Dict[str, Any]:
        return {
            # TODO: Could other signatures have dimensions other than (-1,)?
            "shape": self.shape,
            "dtype": np_to_triton_dtype(self.dtype),
            "name": self.name,
            "optional": self.optional,
            "allow_ragged_batch": self.allow_ragged_batch,
            "signature_type": self.signature_type,
        }

    def __eq__(self, other: "BaseSignature") -> bool:
        return (
            self.shape == other.shape
            and self.dtype == other.dtype
            and self.name == other.name
            and self.optional == other.optional
            and self.allow_ragged_batch == other.allow_ragged_batch
            and self.signature_type == other.signature_type
        )

    # TODO: we could implement it when we'll have separate front-end server
    # @abstractmethod
    # def decode(self):
    #     ...

    # @abstractmethod
    # def encode(self, value):
    #     ...


@dataclasses.dataclass(frozen=False)
class ImageSignature(BaseSignature):
    def __post_init__(self):
        self.signature_type = "image"
        super().__post_init__()
        if self.dtype in [np.bytes_, np.object_]:
            pass
        elif self.dtype not in TRITON_NUMERAL_NP_TYPES:
            raise ValueError(
                f"Unsupported Tensor's dtype: {self.dtype} for ImageSignature."
            )


@dataclasses.dataclass(frozen=False)
class TextSignature(BaseSignature):
    def __post_init__(self):
        self.signature_type = "text"
        super().__post_init__()
        # TODO: figure out when to use object (bytes_?)
        if self.dtype not in [np.object_, np.bytes_]:
            raise ValueError(
                f"Unsupported Tensor's dtype: {self.dtype} for TextSignature."
            )


@dataclasses.dataclass(frozen=False)
class TensorSignature(BaseSignature):
    def __post_init__(self):
        self.signature_type = "tensor"
        super().__post_init__()


@dataclasses.dataclass(frozen=False)
class FileSignature(BaseSignature):
    def __post_init__(self):
        self.signature_type = "file"
        super().__post_init__()
        if self.dtype not in [np.object_, np.bytes_]:
            raise ValueError(
                f"Unsupported Tensor's dtype: {self.dtype} for FileSignature."
            )
