import abc
from _typeshed import Incomplete
from pyarrow.lib import Array as Array
from tlc.client.data_format import SegmentationPolygonsDict as SegmentationPolygonsDict
from tlc.client.sample_type import CategoricalLabel as CategoricalLabel, InstanceSegmentationPolygons as InstanceSegmentationPolygons
from tlc.core.builtins.constants.column_names import BOUNDING_BOXES as BOUNDING_BOXES, BOUNDING_BOX_LIST as BOUNDING_BOX_LIST, HEIGHT as HEIGHT, IMAGE as IMAGE, IMAGE_HEIGHT as IMAGE_HEIGHT, IMAGE_WIDTH as IMAGE_WIDTH, LABEL as LABEL, SEGMENTATIONS as SEGMENTATIONS, WIDTH as WIDTH, X0 as X0, X1 as X1, Y0 as Y0, Y1 as Y1
from tlc.core.builtins.constants.number_roles import NUMBER_ROLE_BB_CENTER_X as NUMBER_ROLE_BB_CENTER_X, NUMBER_ROLE_BB_CENTER_Y as NUMBER_ROLE_BB_CENTER_Y, NUMBER_ROLE_BB_SIZE_X as NUMBER_ROLE_BB_SIZE_X, NUMBER_ROLE_BB_SIZE_Y as NUMBER_ROLE_BB_SIZE_Y
from tlc.core.builtins.constants.string_roles import STRING_ROLE_URL as STRING_ROLE_URL
from tlc.core.builtins.constants.units import UNIT_RELATIVE as UNIT_RELATIVE
from tlc.core.builtins.schemas import BoundingBoxListSchema as BoundingBoxListSchema
from tlc.core.object_type_registry import ObjectTypeRegistry as ObjectTypeRegistry
from tlc.core.objects.table import TableRow as TableRow
from tlc.core.objects.tables.in_memory_columns_table import _InMemoryColumnsTable
from tlc.core.schema import DimensionNumericValue as DimensionNumericValue, ImageUrlStringValue as ImageUrlStringValue, Int32Value as Int32Value, MapElement as MapElement, Schema as Schema, StringValue as StringValue
from tlc.core.url import Url as Url
from tlc.core.utils.progress import track as track
from tlc.utils.decorators import disallow_positional_arguments as disallow_positional_arguments
from typing import Any

logger: Incomplete

class _SkipInstance(Exception): ...

class _TableFromYolo(_InMemoryColumnsTable, abc.ABC, metaclass=abc.ABCMeta):
    '''A table populated from a YOLO dataset, defined by a YAML file and a split.

    The `TableFromYolo` class is an interface between 3LC and the YOLO data format. The YAML file must contain the
    keys `path`, `names` and the provided `split`. If the path in the YAML file is relative, a set of alternatives are
    tried: The directory with the YAML file, the parent of this directory and the
    current working directory.

    :Example:
    ```python
    table = TableFromYolo(
        input_url="path/to/yaml/file.yaml",
        split="train",
    )
    print(table.table_rows[0])
    ```

    :param input_url: The Url to the YOLO YAML file to parse.
    :param split: The split of the dataset to use. Default is "val".
    :param datasets_dir_url: The Url to prepend to the \'path\' in the YAML file if it is relative. If not provided, the
        directory where the YAML sits is used.
    :param override_split_path: A list of paths to override the paths in the YAML file. If provided, the \'path\' and
        \'<split>\' in the YAML file are ignored.
    '''
    input_url: Url
    split: Incomplete
    datasets_dir: Url | None
    override_split_path: list[str] | None
    def __init__(self, *, url: Url | None = None, created: str | None = None, description: str | None = None, row_cache_url: Url | None = None, row_cache_populated: bool | None = None, override_table_rows_schema: Any = None, input_url: str | Url | None = None, split: str | None = None, datasets_dir: Url | None = None, override_split_path: list[str] | None = None, init_parameters: Any = None, input_tables: list[Url] | None = None) -> None: ...

class TableFromYoloDetection(_TableFromYolo): ...
class TableFromYoloSegmentation(_TableFromYolo): ...
class TableFromYolo(TableFromYoloDetection): ...
