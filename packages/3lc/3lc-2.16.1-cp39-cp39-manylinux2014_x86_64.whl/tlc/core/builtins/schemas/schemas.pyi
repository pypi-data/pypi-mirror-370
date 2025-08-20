from _typeshed import Incomplete
from tlc.core.builtins.constants.column_names import EXAMPLE_ID as EXAMPLE_ID
from tlc.core.builtins.constants.display_importances import DISPLAY_IMPORTANCE_EPOCH as DISPLAY_IMPORTANCE_EPOCH, DISPLAY_IMPORTANCE_INPUT_TABLE_ID as DISPLAY_IMPORTANCE_INPUT_TABLE_ID, DISPLAY_IMPORTANCE_ITERATION as DISPLAY_IMPORTANCE_ITERATION
from tlc.core.builtins.constants.number_roles import NUMBER_ROLE_FOREIGN_KEY as NUMBER_ROLE_FOREIGN_KEY, NUMBER_ROLE_LABEL as NUMBER_ROLE_LABEL, NUMBER_ROLE_SAMPLE_WEIGHT as NUMBER_ROLE_SAMPLE_WEIGHT, NUMBER_ROLE_TEMPORAL_INDEX as NUMBER_ROLE_TEMPORAL_INDEX, NUMBER_ROLE_XYZ_COMPONENT as NUMBER_ROLE_XYZ_COMPONENT, NUMBER_ROLE_XY_COMPONENT as NUMBER_ROLE_XY_COMPONENT
from tlc.core.schema import DimensionNumericValue as DimensionNumericValue, Float32Value as Float32Value, Int32Value as Int32Value, MapElement as MapElement, NumericValue as NumericValue, Schema as Schema
from typing import Literal

class XyzSchema(Schema):
    """A Schema defining an (x, y, z) value"""
    composite_role: Incomplete
    def __init__(self, display_name: str = '', description: str = '', writable: bool = True, display_importance: float = 0, value_type: str = ...) -> None: ...

class COCOLabelSchema(Schema):
    """
    A Schema defining COCO label
    """
    value: Incomplete
    def __init__(self, display_name: str = 'label', description: str = 'COCO Label', writable: bool = False, display_importance: float = 0) -> None: ...

class CIFAR10LabelSchema(Schema):
    """
    A Schema defining CIFAR10 label
    """
    value: Incomplete
    def __init__(self, display_name: str = 'label', description: str = 'CIFAR-10 Label', writable: bool = False, display_importance: float = 0, value_type: str = ...) -> None: ...

class CategoricalLabelSchema(Schema):
    """A schema for a categorical label"""
    value: Incomplete
    def __init__(self, class_names: list[str], display_name: str = 'label', description: str = '', writable: bool = False, display_colors: list[str] | None = None, display_importance: float = 0) -> None: ...

class FloatVector2Schema(Schema):
    """A schema for a 2D vector"""
    value: Incomplete
    size0: Incomplete
    def __init__(self, display_name: str = '2D Embedding', description: str = '', writable: bool = False, display_importance: float = 0, number_role: str = ..., mode: Literal['numpy', 'python'] = 'python') -> None: ...

class FloatVector3Schema(Schema):
    """A schema for a 3D vector"""
    value: Incomplete
    size0: Incomplete
    def __init__(self, display_name: str = '3D Embedding', description: str = '', writable: bool = False, display_importance: float = 0, number_role: str = ..., mode: Literal['numpy', 'python'] = 'python') -> None: ...

class ExampleIdSchema(Schema):
    """A schema for example ID values

    Example ID is a unique identifier for an example. It is used to identify
    examples across different tables.
    """
    value: Incomplete
    def __init__(self, display_name: str = 'Example ID', description: str = '', writable: bool = False, computable: bool = False) -> None: ...

class EpochSchema(Schema):
    """A schema for epoch values"""
    def __init__(self, display_name: str = 'Epoch', description: str = 'Epoch of training', display_importance: float | None = None) -> None: ...

class IterationSchema(Schema):
    """A schema for iteration values"""
    def __init__(self, display_name: str = 'Iteration', description: str = 'The current iteration of the training process.', display_importance: float | None = None) -> None: ...

class ForeignTableIdSchema(Schema):
    """A schema describing a value that identifies a foreign table"""
    def __init__(self, foreign_table_url: str, display_name: str = '') -> None: ...

class SampleWeightSchema(Schema):
    """A schema for sample weight values"""
    def __init__(self, display_name: str = 'Weight', description: str = 'The weights of the samples in this table.', sample_type: str = 'hidden', default_value: float = 1.0) -> None:
        """Initialize the SampleWeightSchema

        :param display_name: The display name of the schema
        :param description: The description of the schema
        :param sample_type: The sample type of the schema
        :param default_value: The default value of the schema
        """
