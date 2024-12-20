"""The models to represent a WorkflowSchema"""

from typing import Literal, Any

from pydantic import BaseModel, Field


class CsvData(BaseModel):
    """The Data in a CSV file"""

    column_names: list[str]
    data: list[dict[str, Any]]


class ParamReference(BaseModel):
    """A simple object that references a param name"""

    param_name: str = Field(alias="paramId")


class BaseOperation(BaseModel):
    title: str
    description: str | None


class FieldsetSchemaValidation(BaseOperation):
    """A validation operation to validate the dataset columns and their values"""

    type: Literal["fieldsetSchemaValidation"]
    fieldset_schema: str | ParamReference = Field(alias="fieldsetSchema")


class FileTypeValidation(BaseOperation):
    """A validation operation to check file type"""

    type: Literal["fileTypeValidation"]
    expected_file_type: str = Field(alias="expectedFileType")


class RowCountValidation(BaseOperation):
    """A validation operation to check row counts"""

    type: Literal["rowCountValidation"]
    min_row_count: int | None = Field(alias="minRowCount")
    max_row_count: int | None = Field(alias="maxRowCount")


WorkflowOperation = FieldsetSchemaValidation | FileTypeValidation | RowCountValidation


class TimestampDataTypeSchema(BaseModel):
    """Represents a Timestamp data type. It requires a `date_time_format` to
    represent how a timestamp should be represented."""

    data_type: Literal["timestamp"] = Field(alias="dataType")
    date_time_format: str = Field(alias="dateTimeFormat")


class BasicFieldDataTypeSchema(BaseModel):
    """Represents a data type with no additional configuration other
    than its literal type"""

    data_type: Literal["any", "string", "number"] = Field(alias="dataType")


class FieldSchema(BaseModel):
    """The validation schema for a dataset column"""

    name: str
    case_sensitive: bool = Field(alias="caseSensitive")
    required: bool
    data_type_validation: BasicFieldDataTypeSchema | TimestampDataTypeSchema = Field(
        alias="dataTypeValidation"
    )
    allow_empty_values: bool = Field(alias="allowEmptyValues")
    allowed_values: list[str] | ParamReference | None = Field(alias="allowedValues")


class FieldsetSchema(BaseModel):
    """The validation schema for a dataset's fieldset. Or, in other words,
    the column schemas. E.g. the column names, order, data types, allowable values.
    """

    name: str  # name of this fieldset, e.g. "demographic data columns"
    order_matters: bool = Field(alias="orderMatters")  # enforces column order
    fields: list[FieldSchema]
    allow_extra_columns: Literal["no", "anywhere", "onlyAfterSchemaFields"] = Field(
        alias="allowExtraColumns"
    )


class WorkflowParam(BaseModel):
    """The schema representing an argument (an input) for the Workflow that
    is passed in when a Workflow is kicked off.

    Args:
    - name: str - auto-generated name from the `display_name` to be used as the variable name for this param.
    - display_name: str - user-editable display name of this param
    - description: str
    - required: bool
    """

    name: str
    display_name: str = Field(alias="displayName")
    description: str
    required: bool


class WorkflowSchema(BaseModel):
    """A schema represents the sequence of operations a Workflow should apply."""


    # the list of operations that this Workflow executes
    operations: list[WorkflowOperation]

    # the list of fieldsetSchemas that this Workflow can support
    fieldset_schemas: list[FieldsetSchema] = Field(alias="fieldsetSchemas")

    # the list of params that are input at time a Workflow is executed
    params: list[WorkflowParam] = Field()


def create_empty_workflow_schema() -> WorkflowSchema:
    """Create an empty Workflow Schema"""
    return WorkflowSchema(version="0.1", operations=[], fieldsetSchemas=[], params=[])

class ValidationFailure(BaseModel):
    """
    A validation failure with a message.

    Arguments:
    - message (str) -- The error message
    - row_number (int | None) -- The row number of the error. Or None if there
        is no row number (e.g. if this is a file type error).
    """
    message: str
    row_number: int | None = Field(default=None, serialization_alias="rowNumber")