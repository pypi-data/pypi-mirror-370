from _typeshed import Incomplete
from tlc.core.builtins.constants.column_names import BOUNDING_BOXES as BOUNDING_BOXES, BOUNDING_BOX_LIST as BOUNDING_BOX_LIST, HEIGHT as HEIGHT, IMAGE as IMAGE, IMAGE_HEIGHT as IMAGE_HEIGHT, IMAGE_WIDTH as IMAGE_WIDTH, IS_CROWD as IS_CROWD, WIDTH as WIDTH
from tlc.core.builtins.types.bounding_box import BoundingBox as BoundingBox, SegmentationBoundingBox as SegmentationBoundingBox
from tlc.core.export.exporter import Exporter as Exporter, register_exporter as register_exporter
from tlc.core.objects.table import Table as Table
from tlc.core.schema import StringValue as StringValue
from tlc.core.url import Url as Url
from tlc.core.utils.progress import track as track
from typing import Any

logger: Incomplete

def parse_include_segmentation_arg(include_segmentation: bool | str | None) -> bool | None: ...

class COCOExporter(Exporter):
    """Exporter for the COCO format.

    Tables which are originally instances of the TableFromCoco class will be compatible with this exporter.
    """
    supported_format: str
    priority: int
    @classmethod
    def can_export(cls, table: Table, output_url: Url) -> bool: ...
    @classmethod
    def serialize(cls, table: Table, output_url: Url, weight_threshold: float = 0.0, image_folder: Url | str = '', absolute_image_paths: bool = False, include_segmentation: bool | None = None, indent: int = 4, **kwargs: Any) -> str:
        """Serialize a table to the COCO format.

        Default behavior is to write a COCO file with image paths relative to the (output) annotations file. Written
        paths can be further configured with the `absolute_image_paths` and `image_folder` argument.

        Note that for a coco file to be valid, the image paths should be absolute or relative w.r.t. the annotations
        file itself.

        :param table: The table to serialize
        :param output_url: The output URL
        :param weight_threshold: The weight threshold
        :param image_folder: Make image paths relative to a specific folder. Note that this may produce an annotations
            file that needs special handling. This option is mutually exclusive with `absolute_image_paths`.
        :param absolute_image_paths: Make image paths absolute. If this is set to True, the `image_folder` cannot be
            set.
        :param include_segmentation: Whether to include segmentation in the exported COCO file. If this flag is True,
            segmentation poly-lines will be generated directly from the bounding box annotations. If this flag is False,
            no segmentations are written. If this flag is None, segmentation info will be copied directly from the input
            Table.
        :param indent: The number of spaces to use for indentation in the output.
        :param kwargs: Any additional arguments
        :return: The serialized table
        """
