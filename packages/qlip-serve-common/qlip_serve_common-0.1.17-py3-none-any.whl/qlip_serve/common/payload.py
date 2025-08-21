import abc
import io
from abc import ABC
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

from .model_config.utils import TRITON_NUMERAL_NP_TYPES
from .signature import (
    BaseSignature,
    TensorSignature,
)
from .utils import convert_image_dtype, load_sample, repair_webp

__all__ = ["ImagePayload", "TextPayload", "TensorPayload", "FilePayload"]


# TODO: use as a reference for the future
# https://github.com/bentoml/BentoML/blob/1b377af15b89cc97a037a2c3d26da79a7a71aa76/src/bentoml/io.py#L24

# __all__ = [
#     "File",
#     "Image",
#     "IODescriptor",
#     "JSON",
#     "Multipart",
#     "NumpyNdarray",
#     "PandasDataFrame",
#     "PandasSeries",
#     "Text",
#     "from_spec",
#     "SSE",
# ]


def shapes_equal(shape_one: Union[List, Tuple], shape_two: Union[List, Tuple]) -> bool:
    if len(shape_one) != len(shape_two):
        return False

    for i in range(len(shape_one)):
        if shape_one[i] != shape_two[i] and shape_one[i] != -1 and shape_two[i] != -1:
            return False

    return True


class BasePayload(ABC):
    def __init__(
        self,
        signature: Union[BaseSignature],
        model_metadata: Dict[str, Any],
    ):
        # TODO: get rid of signature and model_metadata
        self.signature = signature
        self.model_metadata = model_metadata
        # TODO: setter/getter for data
        self.data: Optional[Union[np.ndarray, bytes]] = None
        # TODO: add ability to customize pre-process and post-process with functions arrays

    def preprocess(self, tensor: np.ndarray):
        if not shapes_equal(tensor.shape, self.signature.shape):
            raise ValueError(
                f"Input shape mismatch: {tensor.shape} != {self.signature.shape}"
            )

        batch = self.model_metadata["batch"]["enabled"]
        if batch:
            tensor = tensor[np.newaxis, ...]

        return tensor

    def postprocess(self, tensor: np.ndarray):
        # TODO: add meta to returned tensors?
        # TODO: refactor metadata to remove batch when not needed?
        batch = self.model_metadata["batch"]["enabled"]
        if batch:
            tensor = tensor[0]

        # TODO: investigate when its happens
        if not hasattr(tensor, "shape"):
            tensor_shape = (1,)
        else:
            tensor_shape = tensor.shape

        if not shapes_equal(tensor_shape, self.signature.shape):
            raise ValueError(
                f"Output shape mismatch: {tensor_shape} != {self.signature.shape}"
            )

        return tensor

    @abc.abstractmethod
    def load(self, tensor: Union[List, Any]):
        ...

    # TODO: mage generic _repr_ or whatever for debug/logging purposes
    # def request_body(self):
    #     # TODO: change from json to binary
    #     return {
    #         "name": self.signature.tensor.name,
    #         "shape": list(self.data.shape),
    #         "datatype": np_to_triton_dtype(self.signature.tensor.dtype),
    #         "data": self.data.tolist(),
    #     }

    # TODO: Loading from the binary string
    # def load_from_json(self, output: Dict[str, Any]):
    #     if self.signature.tensor.dtype not in TRITON_NUMERAL_NP_TYPES:
    #         raise ValueError(
    #             f"Unsupported dtype for the image signature: {self.signature.tensor.dtype}"
    #         )
    #
    #     # TODO: check output type and shape with signature
    #     # print(output.keys())
    #     # print(output["datatype"])
    #     # print(output["shape"])
    #     output_data = np.array(
    #         output["data"], dtype=triton_to_np_dtype(output["datatype"])
    #     ).reshape(output["shape"])
    #     self.data = output_data


class ImagePayload(BasePayload):
    #  TODO: add support for the non 3 channel images
    #  TODO: add support for custom pre/post image processing (or custom Payload classes with examples in doc?)
    def preprocess(self, img_bytes: bytes):
        img_pil = Image.open(io.BytesIO(img_bytes))
        img = np.array(img_pil)
        if self.signature.dtype in [np.bytes_, np.object_]:
            img_processed_bytes = io.BytesIO()
            img_processed_pil = Image.fromarray(img)
            # TODO: add ability to customize formats
            img_processed_pil.save(img_processed_bytes, format="PNG")
            data = np.array([img_processed_bytes.getvalue()])
        elif self.signature.dtype in TRITON_NUMERAL_NP_TYPES:
            img = convert_image_dtype(img, self.signature.dtype)

            # HWC -> CHW (auto-detect channel order of input tensor)
            if not shapes_equal(img.shape, self.signature.shape):
                if img.shape[-1] == 3 and self.signature.shape[0] == 3:
                    img = np.transpose(img, (2, 0, 1))
                else:
                    raise ValueError(
                        "Unable to autodetect channel order. Expected 3 channels."
                    )
            data = img
        else:
            raise ValueError("Unsupported dtype for the image signature")

        data = super().preprocess(data)

        return data

    def postprocess(self, data: np.ndarray):
        postprocessed_data = super().postprocess(data)

        if self.signature.dtype in [np.bytes_, np.object_]:
            # TODO: decompose checking image format/repairing
            # Warning! We intentionally use entire array instead of the first element
            # Because of problem with fixed strings
            # https://github.com/numpy/numpy/issues/26275#issuecomment-2053628627
            img_pil = Image.open(io.BytesIO(repair_webp(postprocessed_data)))
            img = np.array(img_pil)
        elif self.signature.dtype in TRITON_NUMERAL_NP_TYPES:
            # Convert to the PIL array format to be able save image
            img = convert_image_dtype(postprocessed_data, np.uint8)

            # CHW -> HWC (hardcode conversion for PIL)
            if not shapes_equal(img.shape, (-1, -1, 3)):
                if img.shape[0] == 3:
                    img = np.transpose(img, (1, 2, 0))
                else:
                    raise ValueError(
                        "Unable to autodetect channel order. Expected 3 channels."
                    )
        else:
            raise ValueError("Unsupported dtype for the image signature")

        return img

    def load(self, sample: Union[str, bytes]):
        img_bytes = load_sample(sample)
        self.data = self.preprocess(img_bytes)

    def save(self, path: str):
        # TODO: add ability to get PIL image without saving
        img = self.postprocess(self.data)
        # TODO: add debug prints
        # print(self.data.shape)
        # print(img.shape)
        im = Image.fromarray(img)
        im.save(path)


class TextPayload(BasePayload):
    def load(self, raw_text: str):
        # TODO: np.object_ support figure out usecases
        # if self.signature.tensor.dtype not in [np.bytes_]:
        #     raise ValueError(
        #         f"Unsupported dtype for the text signature: {self.signature.tensor.dtype}"
        #     )

        # TODO: Array of texts?
        text = np.array(raw_text, dtype=np.bytes_)
        text = self.preprocess(text)
        self.data = text


class TensorPayload:
    def __init__(self, signature: TensorSignature, model_metadata: Dict[str, Any]):
        self.signature = signature
        self.model_metadata = model_metadata
        self.data: Optional[np.ndarray] = None

    def preprocess(self, tensor: np.ndarray):
        batch = self.model_metadata["batch"]["enabled"]
        if batch:
            tensor = tensor[np.newaxis, ...]

        return tensor

    def postprocess(self, tensor: np.ndarray):
        # TODO: add meta to returned tensors?
        if self.model_metadata["batch"]["enabled"]:
            tensor = tensor[0]

        return tensor

    # TODO: add tensor loading from file?
    def load(self, tensor: Union[List, Any]):
        # TODO: what to check here?
        # if self.signature.tensor.dtype not in [np.object_]:
        #     raise ValueError(
        #         f"Unsupported dtype for the tensor signature: {self.signature.tensor.dtype}"
        #     )

        # TODO: Array of texts?
        text = np.array(tensor, dtype=self.signature.dtype)

        text = self.preprocess(text)
        self.data = text


class FilePayload(BasePayload):
    def load(self, path: str):
        file_bytes = load_sample(path)
        file_bytes = self.preprocess(np.array([file_bytes], dtype=np.bytes_))
        self.data = file_bytes

    def save(self, path: str):
        data = self.postprocess(self.data)
        with open(path, "wb") as f:
            f.write(data[0])
