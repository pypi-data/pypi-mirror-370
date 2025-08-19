import base64
import io
from typing import Any, Optional

import httpx
import numpy as np
import torch
from PIL import Image as PILImage
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from torchvision.transforms import PILToTensor, ToPILImage
from torch import Tensor


class Image(BaseModel):
    """A versatile image handling class that supports multiple input formats and conversions.

    This class can handle images from various sources including URLs, file paths, base64 strings,
    NumPy arrays, PyTorch tensors, and PIL Images. It provides methods for converting between
    different image formats and serialization capabilities.

    Attributes:
        data (PIL.Image.Image): The internal PIL Image representation of the image data.

    Examples:
        >>> # From URL
        >>> img = Image(data="http://example.com/image.jpg")
        >>>
        >>> # From file
        >>> img = Image(data="file:/path/to/data.png")
        >>>
        >>> # From base64
        >>> img = Image(data="base64_encoded_string")
        >>>
        >>> # From numpy array
        >>> img = Image(data=numpy_array)
        >>>
        >>> # From PyTorch tensor
        >>> img = Image(data=torch_tensor)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: PILImage.Image | None = None
    """The internal PIL Image representation of the data data."""

    def to_numpy(self) -> np.ndarray:
        """Converts the internal PIL Image to a NumPy array.

        Returns:
            np.ndarray: A NumPy array containing the data data with shape (H, W, C) for RGB
            images or (H, W) for grayscale images.
        """
        return np.asarray(self.data)

    def to_tensor(self) -> torch.Tensor:
        """Convert the data to a PyTorch tensor.

        Returns:
            torch.Tensor: The data data as a PyTorch tensor.
        """
        return PILToTensor()(self.data)

    @classmethod
    def __build_from_base64(cls, value: str) -> PILImage.Image:
        """Create a PIL Image from a base64 encoded string.

        Args:
            value (str): The base64 encoded data string.

        Returns:
            PIL.Image.Image: The decoded data.

        Raises:
            ValueError: If the base64 string cannot be decoded to an data.
        """
        try:
            buffer = io.BytesIO(base64.b64decode(value))
            image = PILImage.open(buffer)
            return image
        except Exception:
            raise ValueError("Invalid value string format.")

    @classmethod
    def __build_from_url(cls, url: str) -> PILImage.Image:
        """Creates a PIL Image by downloading from a URL.

        Args:
            url (str): The URL of the data to download. Must be a valid HTTP(S) URL
            pointing to an data file.

        Returns:
            PIL.Image.Image: The downloaded and decoded data.

        Raises:
            Exception: If the data cannot be downloaded or processed, including:
            - Network connectivity issues
            - Invalid URL
            - Non-data content
            - Server errors
        """
        try:
            response = httpx.get(url)
            response.raise_for_status()
            buffer = response.content
            return PILImage.open(io.BytesIO(buffer))
        except Exception as e:
            raise e

    @classmethod
    def __build_from_file(cls, path: str) -> PILImage.Image:
        """Create a PIL Image from a file path.

        Args:
            path (str): The path to the data file (can include 'file:/' prefix).

        Returns:
            PIL.Image.Image: The loaded data.

        Raises:
            Exception: If the file cannot be opened or processed.
        """
        try:
            path = path.replace("file:/", "")
            image = PILImage.open(path)
            return image
        except Exception as e:
            raise e

    @classmethod
    def __build_from_numpy(cls, value: np.ndarray) -> PILImage.Image:
        """Create a PIL Image from a NumPy array.

        Args:
            value (np.ndarray): The NumPy array containing data data.

        Returns:
            PIL.Image.Image: The converted data.

        Raises:
            ValueError: If the NumPy array cannot be converted to an data.
        """
        try:
            return ToPILImage()(value)
        except Exception:
            raise ValueError("Invalid NumPy array format")

    @classmethod
    def __build_from_tensor(cls, value: torch.Tensor) -> PILImage.Image:
        """Create a PIL Image from a PyTorch tensor.

        Args:
            value (torch.Tensor): The PyTorch tensor containing data data.

        Returns:
            PIL.Image.Image: The converted data.

        Raises:
            ValueError: If the tensor cannot be converted to an data.
        """
        try:
            return ToPILImage()(value)
        except Exception:
            raise ValueError("Invalid tensor format")

    @field_validator("data", mode="before")
    @classmethod
    def _validate_input_value(cls, value: Any) -> Optional[PILImage.Image]:
        """Validates and converts input value to PIL Image.

        Returns:
            Optional[PIL.Image.Image]: The validated and converted PIL Image instance or None.
        """
        # Handle None and empty string cases
        if value is None or (isinstance(value, str) and not value):
            return None

        if isinstance(value, str):
            # Handle other string cases
            if value.startswith("http"):
                return cls.__build_from_url(value)
            elif value.startswith("file"):
                return cls.__build_from_file(value)
            else:
                # Should be a base64 encoded string
                return cls.__build_from_base64(value)
        elif isinstance(value, PILImage.Image):
            return value
        elif isinstance(value, np.ndarray):
            if value.size == 0:
                raise ValueError("Empty array is not allowed")
            if np.any(np.equal(value, None)):
                raise ValueError("Array containing None values is not allowed")
            try:
                return cls.__build_from_numpy(value)
            except Exception:
                raise ValueError("Invalid NumPy array format")
        elif isinstance(value, Tensor):
            if value.numel() == 0:
                raise ValueError("Empty tensor is not allowed")
            if torch.isnan(value).any():
                raise ValueError("Tensor containing NaN values is not allowed")
            try:
                return cls.__build_from_tensor(value)
            except Exception:
                raise ValueError("Invalid tensor format")
        else:
            raise ValueError("Invalid value format")

    @field_serializer("data")
    def _serialize_image(self, image: PILImage.Image | None) -> str:
        """Serialize the PIL Image to a base64 encoded string.

        Args:
            image (PIL.Image.Image): The data to serialize.

        Returns:
            str: The base64 encoded string representation of the data.
        """
        if image is None:
            return ""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
