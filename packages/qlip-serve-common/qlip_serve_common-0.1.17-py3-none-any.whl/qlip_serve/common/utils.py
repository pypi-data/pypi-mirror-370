import logging
import struct
from typing import Union
from urllib.parse import urlparse

import numpy as np
import requests

logger = logging.getLogger(__name__)

__all__ = ["convert_image_dtype", "load_sample"]


def convert_image_dtype(image: np.ndarray, dtype: np.dtype = np.float32) -> np.ndarray:
    # Inspired by https://github.com/pytorch/vision/blob/33e47d88265b2d57c2644aad1425be4fccd64605/torchvision/transforms/_functional_tensor.py#L66
    if image.dtype == dtype:
        return image
    if np.issubdtype(image.dtype, np.floating):
        if np.issubdtype(dtype, np.floating):
            return image.astype(dtype)
        # float to int
        if (image.dtype == np.float32 and dtype in (np.int32, np.int64)) or (
            image.dtype == np.float64 and dtype == np.int64
        ):
            msg = f"The cast from {image.dtype} to {dtype} cannot be performed safely."
            raise RuntimeError(msg)
        eps = 1e-3
        max_val = np.iinfo(dtype).max
        result = (image * (max_val + 1.0 - eps)).astype(dtype)
        return result
    else:
        input_max = np.iinfo(image.dtype).max
        # int to float
        if np.issubdtype(dtype, np.floating):
            image = image.astype(dtype)
            return image / input_max
        output_max = np.iinfo(dtype).max
        # int to int
        if input_max > output_max:
            factor = (input_max + 1) // (output_max + 1)
            image = image // factor
            return image.astype(dtype)
        else:
            factor = (output_max + 1) // (input_max + 1)
            image = image.astype(dtype)
            return image * factor


def load_sample(sample: Union[str, bytes]) -> bytes:
    """
    Loads a media sample from a URL, file path, or bytes.

    Args:
        sample (Union[str, bytes]): The media sample as a URL, file path, or bytes.

    Returns:
        bytes: The loaded media sample as bytes.

    Raises:
        ValueError: If the sample type is unsupported.
        requests.HTTPError: If the request to retrieve the sample from a URL fails.
        IOError: If reading the sample from a file fails.
    """
    if isinstance(sample, str):
        if _is_valid_uri(sample):
            sample_bytes = _get_sample_from_url(sample)
        else:
            with open(sample, "rb") as file:
                sample_bytes = file.read()
    elif isinstance(sample, bytes):
        sample_bytes = sample
    else:
        raise ValueError(f"Unsupported type for sample: {type(sample)}")

    return sample_bytes


def _get_sample_from_url(url: str, chunk_size: int = 1024) -> bytes:
    """
    Retrieves the sample data from the given URL using streaming and chunked download.

    Args:
        url (str): The URL of the sample data.
        chunk_size (int): The size of each chunk in bytes (default: 1024).

    Returns:
        bytes: The sample data as bytes.

    Raises:
        requests.HTTPError: If the request fails.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        sample_bytes = bytearray()
        for chunk in response.iter_content(chunk_size=chunk_size):
            sample_bytes.extend(chunk)

        return bytes(sample_bytes)
    except requests.HTTPError as e:
        logger.error(f"Failed to retrieve sample from URL: {url}. Error: {str(e)}")
        raise


def _is_valid_uri(uri: str) -> bool:
    """
    Checks if the given URI is valid.

    Args:
        uri (str): The URI to validate.

    Returns:
        bool: True if the URI is valid, False otherwise.
    """
    try:
        result = urlparse(uri)
        return bool(result.scheme and result.netloc)
    except Exception as e:
        logger.warning(f"Invalid URI: {uri}. Error: {str(e)}")
        return False


def repair_webp(data: bytes, keep_extra_data: bool = True) -> bytes:
    """
    Attempt to fully parse and repair a WebP file (RIFF container).
    Ensures:
      - 'RIFF' + <FileSize> + 'WEBP' header is present.
      - Each chunk's declared payload is fully available (or zero-padded if truncated).
      - A 1-byte 0x00 pad follows any chunk with an odd payload size.
      - The RIFF <FileSize> field is recalculated and updated if changed by repairs.

    Parameters:
      data             : Possibly truncated or malformed .webp file bytes
      keep_extra_data  : If True, preserve any leftover data after parsing chunks.
                         If False, discard anything beyond the final chunk/padding.

    Raises:
      WebPRepairError if the input is too short for even the basic RIFF/WEBP header,
      or if the 'RIFF'/'WEBP' signatures are missing.

    Returns:
      A new, self-consistent byte-string representing a valid (or at least
      structurally parseable) WebP/RIFF file.
    """
    # 1. Check basic RIFF/WEBP header (12 bytes total).
    if len(data) < 12:
        return data  # Not enough for any real fix. Return as is or raise an error.
        # raise WebPRepairError("Data is too short to contain a RIFF+WEBP header (12 bytes).")

    if data[0:4] != b"RIFF":
        return data  # Not a RIFF container, can't fix in a standard way.
        # raise WebPRepairError("Missing 'RIFF' signature in file header.")

    # The declared RIFF size is the number of bytes following this 8-byte sub-header
    declared_size = struct.unpack_from("<I", data, 4)[0]
    if data[8:12] != b"WEBP":
        return data  # Not a WebP fourcc.
        # raise WebPRepairError("Missing 'WEBP' signature in RIFF container.")

    # The total length the file *claims* to have is declared_size + 8
    declared_end = declared_size + 8

    # We'll work in a mutable buffer so we can append zeros for truncated chunks.
    buf = bytearray(data)

    # 2. Now parse chunks from offset=12 to the end.
    offset = 12  # skip the 12-byte RIFF header

    while True:
        # If we can't even read an 8-byte chunk header, we break out
        if offset + 8 > len(buf):
            break

        # Read FourCC (4 bytes) + chunk size (4 bytes, LE)
        fourcc = buf[offset : offset + 4]  # Not strictly validated here, but we have it
        chunk_size = struct.unpack_from("<I", buf, offset + 4)[0]
        offset += 8

        # The end offset of this chunk's payload:
        chunk_payload_end = offset + chunk_size

        # If the chunk extends beyond our current buffer, we append zeros:
        if chunk_payload_end > len(buf):
            missing = chunk_payload_end - len(buf)
            buf.extend(b"\x00" * missing)

        # Advance offset to the end of the payload
        offset = chunk_payload_end

        # 3. If chunk_size is odd, there must be a 1-byte zero pad.
        if (chunk_size & 1) == 1:
            if offset >= len(buf):
                # If missing, append it
                buf.append(0)
            else:
                # If the pad byte exists but isn't zero, fix it
                if buf[offset] != 0:
                    buf[offset] = 0
            offset += 1

        # 4. If we've reached or passed the declared_end,
        #    we normally could stop here. But if keep_extra_data=True,
        #    we keep going to preserve any additional data.
        if offset >= declared_end:
            break

    # 5. Possibly discard leftover data beyond the final offset,
    #    or keep it if keep_extra_data=True.
    if keep_extra_data:
        # If we appended zeros but are still shorter than declared_end, offset might be < declared_end.
        # We'll keep everything in buf.  (No changes here.)
        pass
    else:
        # Truncate to the final offset if there's leftover
        if offset < len(buf):
            del buf[offset:]

    # 6. Now that we've appended zeros for truncated chunks and possibly
    #    truncated leftover data, recompute the correct size for the RIFF:
    final_size = len(buf)
    new_declared_size = final_size - 8  # Because the 'size' is fileLengthMinus8

    # Overwrite the <FileSize> field in the header if it's changed
    if new_declared_size != declared_size:
        struct.pack_into("<I", buf, 4, new_declared_size)

    return bytes(buf)
