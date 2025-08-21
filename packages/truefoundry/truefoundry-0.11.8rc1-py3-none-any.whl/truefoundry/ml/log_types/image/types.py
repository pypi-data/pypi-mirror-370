import enum
from typing import Dict, List, Optional

from truefoundry.pydantic_v1 import BaseModel, NonEmptyStr, root_validator


class Group(enum.Enum):
    ACTUALS = "actuals"
    PREDICTIONS = "predictions"


class Position(BaseModel):
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    class Config:
        allow_mutation = False


class BoundingBox(BaseModel):
    position: Position
    class_name: NonEmptyStr
    caption: Optional[str] = None

    class Config:
        allow_mutation = False

    @root_validator(pre=True)
    def set_caption_if_not_passed(cls, values):
        if not values.get("caption"):
            values["caption"] = values.get("class_name")

        return values


class BoundingBoxGroups(BaseModel):
    __root__: Dict[Group, List[BoundingBox]]

    class Config:
        allow_mutation = False
        use_enum_values = True

    def to_dict(self):
        return self.dict()["__root__"]


class ClassGroups(BaseModel):
    __root__: Dict[Group, List[NonEmptyStr]]

    class Config:
        allow_mutation = False
        use_enum_values = True

    @root_validator(pre=True)
    def transform_class_to_classes(cls, values):
        values = values["__root__"]
        processed_values = {}
        for group, classes in values.items():
            if isinstance(classes, str):
                processed_values[group] = [classes]
            else:
                processed_values[group] = classes
        return {"__root__": processed_values}

    def to_dict(self):
        return self.dict()["__root__"]
