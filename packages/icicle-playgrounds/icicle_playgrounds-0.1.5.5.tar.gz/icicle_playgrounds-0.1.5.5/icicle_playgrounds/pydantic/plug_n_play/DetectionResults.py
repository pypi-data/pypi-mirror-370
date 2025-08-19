from enum import Enum, auto
from pydantic import BaseModel, ConfigDict

from icicle_playgrounds.pydantic.plug_n_play.Tensor import Tensor
class BoundingBoxFormat(Enum):
    XYXY = auto()
    XYWH = auto()
    XYXYN = auto()
    XYWHN = auto()

class DetectionResults(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    boxes: Tensor
    labels: list[str] = []
    scores: Tensor

    box_format: BoundingBoxFormat = BoundingBoxFormat.XYXY