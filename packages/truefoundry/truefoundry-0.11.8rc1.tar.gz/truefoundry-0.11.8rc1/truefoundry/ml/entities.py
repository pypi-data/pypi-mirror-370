from typing import Optional, Union

from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    FileInfoDto,
    MetricDto,
)
from truefoundry.pydantic_v1 import (
    BaseModel,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
)


class Metric(BaseModel):
    key: StrictStr = Field(...)
    value: Optional[Union[StrictFloat, StrictInt]] = None
    timestamp: Optional[StrictInt] = None
    step: Optional[StrictInt] = 0

    @classmethod
    def from_dto(cls, dto: MetricDto) -> "Metric":
        return cls(
            key=dto.key,
            value=dto.value,
            timestamp=dto.timestamp,
            step=dto.step,
        )

    def to_dto(self) -> MetricDto:
        return MetricDto(
            key=self.key,
            value=self.value,
            timestamp=self.timestamp,
            step=self.step,
        )


class FileInfo(BaseModel):
    path: StrictStr
    is_dir: StrictBool
    file_size: Optional[StrictInt] = None
    signed_url: Optional[StrictStr] = None

    @classmethod
    def from_dto(cls, dto: FileInfoDto) -> "FileInfo":
        return cls(
            path=dto.path,
            is_dir=dto.is_dir,
            file_size=dto.file_size,
            signed_url=dto.signed_url,
        )

    def to_dto(self) -> FileInfoDto:
        return FileInfoDto(
            path=self.path,
            is_dir=self.is_dir,
            file_size=self.file_size,
            signed_url=self.signed_url,
        )
