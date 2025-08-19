import base64
import gzip
import io
from typing import Any

import numpy as np
import torch
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
from pydantic_core.core_schema import SerializationInfo


class Tensor(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    data: np.ndarray | torch.Tensor

    def to_numpy(self) -> None:
        self.data = self.data.cpu().numpy() if isinstance(self.data, torch.Tensor) else self.data

    def to_tensor(self) -> None:
        self.data = torch.from_numpy(self.data) if isinstance(self.data, np.ndarray) else self.data

    @classmethod
    def _base64_to_tensor(
        cls, encoded_str: str, to_torch_tensor: bool = False, compressed: bool = False
    ) -> np.ndarray | torch.Tensor:
        try:
            tags, encoded_str = encoded_str.split(":/", 1)
            tags = tags.lower().split("-")
            if len(tags) == 2:
                if tags[1] == "compressed":
                    compressed = True
                elif tags[1] == "tensor":
                    to_torch_tensor = True
            if len(tags) == 3:
                if tags[1] == "tensor" and tags[2] == "compressed":
                    compressed = True
                    to_torch_tensor = True
            decoded = base64.b64decode(encoded_str)
            buffer = io.BytesIO(decoded)
            if compressed:
                with gzip.GzipFile(fileobj=buffer, mode="rb") as f:
                    array = np.load(f)
            else:
                array = np.load(buffer)
            if to_torch_tensor:
                array = torch.from_numpy(array)
            return array
        except Exception as e:
            raise e

    @field_validator("data", mode="before")
    @classmethod
    def _prevalidate_data_input_value(cls, value: Any) -> np.ndarray:
        if value is None or (isinstance(value, str) and not value):
            # None or empty values
            return np.array([])
        if isinstance(value, str):
            # try to decode the string (assuming its base64 encoded)
            return cls._base64_to_tensor(value)
        if isinstance(value, list):
            # Convert lists to NumPy array
            try:
                return np.array(value)
            except Exception:
                raise ValueError("Error converting list to numpy array")
        else:
            # Everything else should be passed to the validators to check
            return value

    @field_validator("data", mode="after")
    @classmethod
    def _validate_data_input_value(cls, value: Any) -> np.ndarray:
        if not isinstance(value, torch.Tensor) and not isinstance(value, np.ndarray):
            raise TypeError("Invalid input type, must be a numpy array")

        return value

    @field_serializer("data")
    def _serialize_tensor(
        self, data: np.ndarray | torch.Tensor, info: SerializationInfo
    ) -> str | list[float] | list[int]:
        context = info.context
        to_base64 = context.get("to_base64", False) if context and isinstance(context, dict) else False
        if to_base64:
            # Encoding the Tensor to a Base64 encoded string. (Compression is optional)
            try:
                tag = "base64"
                compress = context.get("compress", False) if context and isinstance(context, dict) else False
                if isinstance(data, torch.Tensor):
                    tag += "-tensor"
                    tensor = data.cpu().numpy()
                buffer = io.BytesIO()
                if compress:
                    with gzip.GzipFile(fileobj=buffer, mode="wb") as f:
                        np.save(f, data)
                    tag += "-compressed"
                else:
                    np.save(buffer, data)
                return tag + ":/" + base64.b64encode(buffer.getvalue()).decode("utf-8")
            except Exception as e:
                raise e
        else:
            # Dumping as a list
            return data.tolist()