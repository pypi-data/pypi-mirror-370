import json
import os
import posixpath
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ArtifactType,
)
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.log_types.artifacts.artifact import (
    ArtifactVersionInternalMetadata,
    _log_artifact_version_helper,
)
from truefoundry.ml.log_types.artifacts.constants import (
    FILES_DIR,
    INTERNAL_METADATA_PATH,
)
from truefoundry.ml.log_types.artifacts.utils import _make_dest_to_src_map_from_dir
from truefoundry.ml.log_types.image.constants import (
    DEFAULT_IMAGE_FORMAT,
    IMAGE_KEY_REGEX,
    IMAGE_METADATA_FILE_NAME,
    MISSING_PILLOW_PACKAGE_MESSAGE,
)
from truefoundry.ml.log_types.image.image_normalizer import normalize_image
from truefoundry.ml.log_types.image.types import BoundingBoxGroups, ClassGroups
from truefoundry.ml.log_types.pydantic_base import PydanticBase
from truefoundry.ml.run_utils import get_module

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    import numpy  # noqa: F401
    import PIL.Image
    from numpy.typing import NDArray  # noqa: F401

    from truefoundry.ml.mlfoundry_run import MlFoundryRun

ImageLikeNDArray = Union[
    "NDArray[numpy.int8]",
    "NDArray[numpy.uint8]",
    "NDArray[numpy.float32]",
    "NDArray[numpy.float64]",
    "NDArray[numpy.bool_]",
]
DataOrPathType = Union[str, Path, ImageLikeNDArray, "PIL.Image.Image"]
ClassGroupsType = Dict[str, Union[str, List[str]]]
BBoxGrouptype = Dict[str, List[Dict[str, Any]]]


def validate_key_name(key: str):
    if not key or not IMAGE_KEY_REGEX.match(key):
        raise MlFoundryException(
            f"Invalid run image key: {key} should only contain alphanumeric, hyphen or underscore"
        )


class ImageVersionInternalMetadata(ArtifactVersionInternalMetadata):
    image_file: str
    image_metadata_file: str


class Image:
    def __init__(
        self,
        data_or_path: DataOrPathType,
        caption: Optional[str] = None,
        class_groups: Optional[ClassGroupsType] = None,
        bbox_groups: Optional[BBoxGrouptype] = None,
    ):
        """Represent and log image using this class in `mlfoundry`.

        You can initialize `truefoundry.ml.Image` by either by using a local path
        or you can use a numpy array / PIL.Image object.

        If you are using numpy array, we only support the following data types,
        - bool
        - integer [0 - 255]
        - unsigned integer [0 - 255]
        - float [0.0 - 1.0]

        Any out of range value will be clipped.

        As for array shape/dim, we follow the following structures,
        - H x W (Grayscale)
        - H x W x 1 (Grayscale)
        - H x W x 3 (an RGB channel order is assumed)
        - H x W x 4 (an RGBA channel order is assumed)

        `PIL` package is required to log images. To install the `PIL` package,
        run `pip install pillow`.

        We can also log class names and bounding boxes associated with the image.
        Class names and bounding boxes should be always grouped under `actuals` or
        `predictions`. For example, if we have an image where the ground truth class
        is "cat" and predicted class is "dog", we can represent it like,

        ```python
        from truefoundry.ml import Image

        Image(
            data_or_path=imarray,
            class_groups={"actuals": "dog", "predictions": "cat"}
        )
        ```

        You can define a bounding box using the following dictionary structure,
        ```python
        {
            "position": {"min_x": 15, "min_y": 5, "max_x": 20, "max_y": 30}, # required, defines the position of the bounding box
                                                                             # (min_x, min_y) defines the top left and
                                                                             # (max_x, max_y) defines the bottom right corner of the box.
            "class_name": "dog", # required, the class name of the bounding box
            "caption": "dog", # optional, the caption of the bounding box.
                              # If not passed, the class name is set as caption.
        }
        ```

        Args:
            data_or_path (Union[str, Path, "numpy.ndarray", "PIL.Image.Image"]):
                Either the local path or the image object (Numpy array or PIL Image).
            caption (Optional[str], optional): A string caption or label for the image.
            class_groups (Optional[Dict[str, Union[str, List[str]]]], optional):
                Class names associated with the image. Expects class name(s) grouped by
                `predictions` or `actuals`.
            bbox_groups (Optional[Dict[str, List[Dict]]], optional): Bounding boxes
                associated with the image. Expects bounding boxes grouped by `predictions`
                or `actuals`.

        Examples:
        ### Logging images with caption and class names

        ```python
        from truefoundry.ml import get_client, Image
        import numpy as np

        client = get_client()
        run = client.create_run(
            ml_repo="my-classification-project",
        )

        imarray = np.random.randint(low=0, high=256, size=(100, 100, 3))

        images_to_log = {
            "logged-image-array": Image(
                data_or_path=imarray,
                caption="testing image logging",
                class_groups={"actuals": "dog", "predictions": "cat"},
            ),
        }
        run.log_images(images_to_log, step=1)

        run.end()
        ```

        ### Logging images for a multi-label classification problem

        ```python
        from truefoundry.ml import Image

        images_to_log = {
            "logged-image-array": Image(
                data_or_path=imarray,
                caption="testing image logging",
                class_groups={"actuals": ["dog", "human"], "predictions": ["cat", "human"]},
            ),
        }

        run.log_images(images_to_log, step=1)
        ```

        ### Logging images with bounding boxes

        ```python
        from truefoundry.ml import Image

        images_to_log = {
            "logged-image-array": Image(
                data_or_path=imarray,
                caption="testing image logging",
                bbox_groups={
                    "predictions": [
                        {
                            "position": {"min_x": 5, "min_y": 5, "max_x": 20, "max_y": 30},
                            "class_name": "cat",
                        }
                    ],
                    "actuals": [
                        {
                            "position": {"min_x": 15, "min_y": 5, "max_x": 20, "max_y": 30},
                            "class_name": "dog",
                            "caption": "dog",
                        }
                    ],
                },
            ),
        }

        run.log_images(images_to_log, step=1)
        ```
        """

        self._caption: Optional[str] = None
        self._class_groups: Optional[ClassGroups] = None
        self._bbox_groups: Optional[BoundingBoxGroups] = None

        self._image: Optional["PIL.Image.Image"] = None
        self._image_artifact_path = None
        self._local_image_path: Optional[str] = None

        self._init_image(data_or_path)
        self._init_metadata(
            caption=caption, class_groups=class_groups, bbox_groups=bbox_groups
        )

    @property
    def image(self) -> "PIL.Image.Image":
        if self._image is None:
            raise MlFoundryException("Image is not initialized")
        return self._image

    @property
    def caption(self) -> Optional[str]:
        return self._caption

    @property
    def class_groups(self) -> Optional[ClassGroups]:
        return self._class_groups

    @property
    def bbox_groups(self) -> Optional[BoundingBoxGroups]:
        return self._bbox_groups

    def save_image_to_local_dir(self, local_dir) -> str:
        if self._local_image_path is None:
            image_file_name = self._serialize_and_save_image_as_artifact(local_dir)
        else:
            image_file_name = self._copy_local_image_as_artifact(local_dir)

        return image_file_name

    def _serialize_and_save_image_as_artifact(self, local_dir: str) -> str:
        file_name = f"image.{DEFAULT_IMAGE_FORMAT}"
        local_path = os.path.join(local_dir, file_name)
        self.image.save(local_path)

        return file_name

    def _copy_local_image_as_artifact(self, local_dir: str) -> str:
        assert self._local_image_path is not None
        file_name = os.path.basename(self._local_image_path)
        new_local_image_path = os.path.join(local_dir, file_name)
        shutil.copy2(self._local_image_path, new_local_image_path)
        return file_name

    def _init_image(self, data_or_path: DataOrPathType):
        pil_image_module = get_module(
            module_name="PIL.Image",
            required=True,
            error_message=MISSING_PILLOW_PACKAGE_MESSAGE,
        )
        if isinstance(data_or_path, (str, Path)):
            self._local_image_path = os.path.abspath(data_or_path)
            with pil_image_module.open(data_or_path) as image:
                image.load()
                self._image = image
        else:
            self._image = normalize_image(data_or_path)

    def _init_metadata(
        self,
        caption: Optional[str],
        class_groups: Optional[ClassGroupsType],
        bbox_groups: Optional[Dict[str, Any]],
    ):
        if caption is not None:
            self._caption = str(caption)

        if class_groups:
            self._class_groups = ClassGroups.parse_obj(class_groups)

        if bbox_groups:
            self._bbox_groups = BoundingBoxGroups.parse_obj(bbox_groups)

    def _to_dict(self) -> Dict[str, Any]:
        dict_ = {}
        dict_["caption"] = self._caption
        dict_["class_groups"] = (
            self.class_groups.to_dict() if self.class_groups is not None else None
        )
        dict_["bbox_groups"] = (
            self.bbox_groups.to_dict() if self.bbox_groups is not None else None
        )

        return dict_

    def save(
        self,
        run: "MlFoundryRun",
        key: str,
        step: int = 0,
    ):
        validate_key_name(key)

        # creating temp dir, files directory, .truefoundry directory
        temp_dir = tempfile.TemporaryDirectory(prefix="truefoundry-")

        local_internal_metadata_path = os.path.join(
            temp_dir.name, INTERNAL_METADATA_PATH
        )
        os.makedirs(os.path.dirname(local_internal_metadata_path), exist_ok=True)

        local_files_dir = os.path.join(temp_dir.name, FILES_DIR)
        os.makedirs(local_files_dir, exist_ok=True)

        try:
            # saving the image file
            image_file_name = self.save_image_to_local_dir(local_files_dir)

            # saving the image_metadata
            local_image_metadata_file_path = os.path.join(
                local_files_dir, IMAGE_METADATA_FILE_NAME
            )
            with open(local_image_metadata_file_path, "w") as fp:
                fp.write(ImageRunLogType(value=self._to_dict()).json())

            # creating and saving the internal_metadata file
            internal_metadata = ImageVersionInternalMetadata(
                files_dir=FILES_DIR,
                # joining with posixpath for avoiding backslash in case logged from windows machine
                image_file=posixpath.join(FILES_DIR, image_file_name),
                image_metadata_file=posixpath.join(FILES_DIR, IMAGE_METADATA_FILE_NAME),
            )
            with open(local_internal_metadata_path, "w") as f:
                json.dump(internal_metadata.dict(), f)

        except Exception as e:
            temp_dir.cleanup()
            raise MlFoundryException("Failed to log Image") from e

        _log_artifact_version_helper(
            run=run,
            name=key,
            artifact_type=ArtifactType.IMAGE,
            artifact_dir=temp_dir,
            dest_to_src_map=_make_dest_to_src_map_from_dir(root_dir=temp_dir.name),
            internal_metadata=internal_metadata,
            step=step,
        )


class ImageRunLogType(PydanticBase):
    value: Dict[str, Any]

    @staticmethod
    def get_log_type() -> str:
        return "image"
