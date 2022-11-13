from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, Extra


class Model(BaseModel):
    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True


class UserResponse(BaseModel):
    created_at: Optional[str] = Field(None, title='Created At')
    allocated_memory: Optional[int] = Field(0, title='Allocated Memory')
    datasets_count: Optional[int] = Field(0, title='Datasets Count')
    model_type: Optional[str] = Field('user', title='Model Type')
    name: Optional[str] = Field(None, title='User Name')


class RefreshResponse(BaseModel):
    access_token: str = Field(..., title='Access Token')


class UploadParams(BaseModel):
    private_url: Optional[str] = Field(None, title='Private Url')
    data: Optional[Dict[str, Any]] = Field(None, title='Data')
    detail: Optional[List] = Field(None, title='Detail')


class DatasetExtendedCardOut(BaseModel):
    user_id: str = Field(..., title='User Id')
    name: str = Field(..., title='Name')
    id: Optional[str] = Field(None, title=' Id', alias="_id")
    dataset_id: str = Field(..., title='Dataset Id')
    rows_num: int = Field(..., title='Rows Num')
    cols_num: int = Field(..., title='Cols Num')
    missing_num: int = Field(..., title='Missing Num')
    upload_date: str = Field(..., title='Upload Date')
    allocated_memory: int = Field(..., title='Allocated Memory')
    delimiter: str = Field(..., title='Delimiter')
    deleted_at: Optional[bool] = Field(False, title='Deleted At')
    associated_scoring_template_id: Optional[str] = Field(
        '', title='Associated Scoring Template Id'
    )
    associated_scoring_template_name: Optional[str] = Field(
        '', title='Associated Scoring Template Name'
    )
    model_type: str = Field('dataset_card', title='Model Type')


class Task(BaseModel):
    id: Optional[str] = Field(None, title='Id')
    status: str = Field(..., title='Status')
    meta: Dict[str, Any] = Field(..., title='Meta')
    result: Optional[Union[DatasetExtendedCardOut, Any]] = Field(None, title='Result')


class ValidateDataset(BaseModel):
    filepath: str = Field(..., title='Filepath')


class UserFeedback(BaseModel):
    id: Optional[str] = Field(None, title='Id')
    form_name: Optional[str] = Field(None, title='Form Name')
    type_of_request: str = Field(..., title='Type Of Request')
    user_issue: str = Field(..., title='User Issue')
    email: str = Field(..., title='Email')
    screenshots: Union[List, str] = Field(..., title='Screenshot')
    user_id: str = Field(..., title='User Id')
    timestamp: str = Field(..., title='Timestamp')


class ComplexValue(BaseModel):
    order: int = Field(..., title='Order')
    value: str = Field(..., title='Value')


class DatasetColumn(BaseModel):
    id: Optional[str] = Field(None, title=' Id', alias="_id")
    name: str = Field(..., title='Name')
    values: List[ComplexValue] = Field(..., title='Values')
    visible: Optional[bool] = Field(False, title='Visible')
    pinned: Optional[bool] = Field(False, title='Pinned')
    scored: Optional[bool] = Field(False, title='Scored')
    numeric: Optional[bool] = Field(False, title='Numeric')
    max: Optional[str] = Field('', title='Max')
    min: Optional[str] = Field('', title='Min')
    color: Optional[str] = Field('', title='Color')
    model_type: Optional[str] = Field('dataset_column', title='Model Type')


class CustomDatasetColumn(BaseModel):
    id: Optional[str] = Field(None, title=' Id', alias="_id")
    name: str = Field(..., title='Name')
    values: Optional[List[ComplexValue]] = Field([], title='Values')
    visible: Optional[bool] = Field(True, title='Visible')
    pinned: Optional[bool] = Field(False, title='Pinned')
    scored: Optional[bool] = Field(False, title='Scored')
    numeric: Optional[bool] = Field(True, title='Numeric')
    max: Optional[str] = Field(None, title='Max')
    min: Optional[str] = Field(None, title='Min')
    ordinal_number: Optional[int] = Field(None, title='Ordinal Number')
    color: Optional[str] = Field('', title='Color')
    model_type: Optional[str] = Field('custom_dataset_column', title='Model Type')
    custom_formula: str = Field('', title='Custom Formula')


class DatasetPagination(BaseModel):
    user_id: str = Field(..., title='User Id')
    columns: Optional[List[Union[DatasetColumn, CustomDatasetColumn]]] = Field(
        None, title='Columns'
    )
    allocated_memory: int = Field('', title='Allocated Memory')
    associated_scored_dataset_id: Optional[str] = Field(
        '', title='Associated Scored Dataset Id'
    )
    associated_scoring_template_id: Optional[str] = Field(
        '', title='Associated Scoring Template Id'
    )
    associated_scoring_template_md5_hash: Optional[str] = Field(
        '', title='Associated Scoring Template Md5 Hash'
    )
    columns_order: List[int] = Field(..., title='Columns Order')
    delimiter: Optional[str] = Field(None, title='Delimiter')
    id: str = Field(..., title='Id')
    model_type: str = Field(..., title='Model Type')
    name: Optional[str] = Field(None, title='Name')
    rows_order: List[int] = Field(..., title='Rows Order')
    upload_date: Optional[str] = Field(None, title='Upload Date')


class ScoringResults(BaseModel):
    column_meta: List[Dict] = Field(..., title='Column Meta')
    counted_columns: List[DatasetColumn] = Field(..., title='Counted Columns')
    scored_column: List[Union[float, str]] = Field(..., title='Scored Column')


class RenderedImages(BaseModel):
    values: List[ComplexValue] = Field(..., title='Values')


class ResultModel(BaseModel):
    dataset: DatasetPagination
    radar: Optional[Dict] = Field(None, title='Radar')
    scored: Optional[ScoringResults] = Field(None, title='Scored')
    rendered_images: RenderedImages


class DesirabilityFunctionTypes(str, Enum):
    linear = 'linear'
    logarithmic = 'logarithmic'
    rectangular = 'rectangular'
    triangular = 'triangular'
    unit_step = 'unit_step'
    logistic = 'logistic'
    custom_curve = 'custom_curve'


class MissingValuesTypes(str, Enum):
    no_calculate = 'no-calculate'
    default_x = 'default-x'
    default_y = 'default-y'
    swap = 'swap'


class Point(BaseModel):
    x: Optional[float] = Field(None, title='X')
    y: Optional[float] = Field(None, title='Y')


class Threshold(BaseModel):
    min: Optional[float] = Field(None, title='Min')
    max: Optional[float] = Field(None, title='Max')


class DesirabilityFunction(BaseModel):
    id: Optional[str] = Field(None, title=' Id', alias="_id")
    name: Optional[str] = Field(None, title='Name')
    type: Optional[DesirabilityFunctionTypes] = 'linear'
    points: Optional[List[Point]] = Field([{}], title='Points')
    parameters: Optional[Dict[str, Any]] = Field(None, title='Parameters')
    model_type: Optional[str] = Field('desirability_function', title='Model Type')


class MissingValues(BaseModel):
    type: Optional[MissingValuesTypes] = 'no-calculate'
    value: Optional[float] = Field(None, title='Value')
    swap_type: Optional[MissingValuesTypes] = 'no-calculate'
    swap_column: Optional[str] = Field(None, title='Swap Column')


class TemplateProperty(BaseModel):
    id: Optional[str] = Field(None, title=' Id', alias="_id")
    column_name: str = Field(..., title='Column Name')
    enabled_for_scoring: Optional[bool] = Field(False, title='Enabled For Scoring')
    importance: Optional[int] = Field(1, title='Importance')
    missing_values: Optional[MissingValues] = None
    desirability_function: DesirabilityFunction
    threshold: Optional[Threshold] = None
    model_type: Optional[str] = Field('template_property', title='Model Type')


class PostScoringTemplate(BaseModel):
    name: Optional[str] = Field(None, title='Name')
    properties: Optional[List[TemplateProperty]] = Field([], title='Properties')
    dataset_id: str = Field(..., title='Dataset Id')
    scoring_template_id: Optional[str] = Field(None, title='Scoring Template Id')


class CreateResponse(BaseModel):
    created_id: Optional[str] = Field(None, title='Created Id')


class RequestTemplateProperty(BaseModel):
    column_name: str = Field(..., title='Column Name')
    enabled_for_scoring: Optional[bool] = Field(False, title='Enabled For Scoring')
    importance: Optional[int] = Field(1, title='Importance')
    missing_values: Optional[MissingValues] = None
    desirability_function: Optional[DesirabilityFunction]
    threshold: Optional[Threshold] = None
