from typing import List, Literal, TypedDict, Union


class _FilterRequired(TypedDict):
    attribute: str


class _FilterOptional(TypedDict, total=False):
    values: List[str]


class Filter(_FilterRequired, _FilterOptional):
    pass


class Interval(TypedDict):
    end: str
    start: str


class Preset(TypedDict):
    value: Literal[
        "PreviousQuarter",
        "ThisWeek",
        "PreviousWeek",
        "Yesterday",
        "Today",
        "ThisMonth",
        "PreviousMonth",
        "ThisQuarter",
        "ThisYear",
    ]


class _FilterValueRequired(TypedDict):
    value: str


class _FilterValueOptional(TypedDict, total=False):
    label: str


class FilterValue(_FilterValueRequired, _FilterValueOptional):
    pass


Measure = Literal["Min", "Max", "Sum", "Percentage", "StdDev", "Average", "Count"]

DoubleMeasure = Literal["Min", "Max", "Sum", "Percentage", "StdDev", "Average"]

LongMeasure = Literal["Count"]


class LongAggregateValue(TypedDict, total=False):
    measure: LongMeasure
    value: int


class DoubleAggregateValue(TypedDict, total=False):
    measure: DoubleMeasure
    value: float


class _MetricDataRequired(TypedDict):
    aggregates: List[Union[DoubleAggregateValue, LongAggregateValue]]


class _MetricDataOptional(TypedDict, total=False):
    id: str


class MetricData(_MetricDataRequired, _MetricDataOptional):
    pass


class BooleanField(TypedDict):
    value: bool


class DoubleField(TypedDict):
    value: float


class InstantField(TypedDict):
    value: str


class IntField(TypedDict):
    value: int


class LongField(TypedDict):
    value: int


class StringField(TypedDict):
    value: str


class TimestampField(TypedDict):
    value: str


class UUIDField(TypedDict):
    value: str


class ListField(TypedDict):
    value: List[
        Union[
            BooleanField,
            DoubleField,
            InstantField,
            IntField,
            LongField,
            StringField,
            TimestampField,
            UUIDField,
        ]
    ]


MetricRecordValue = Union[
    BooleanField,
    DoubleField,
    InstantField,
    IntField,
    ListField,
    LongField,
    StringField,
    TimestampField,
    UUIDField,
]


class _FieldRequired(TypedDict):
    name: str


class _FieldOptional(TypedDict, total=False):
    field: MetricRecordValue


class Field(_FieldRequired, _FieldOptional):
    pass


class MetricRecord(TypedDict, total=False):
    fields: List[Field]
    primaryTimestampField: TimestampField
    value: MetricRecordValue


class _AggregateMetadataRequired(TypedDict):
    measure: Measure


class _AggregateMetadataOptional(TypedDict, total=False):
    description: str


class AggregateMetadata(_AggregateMetadataRequired, _AggregateMetadataOptional):
    pass


class _FilterMetadataRequired(TypedDict):
    filterAttribute: str


class _FilterMetadataOptional(TypedDict, total=False):
    description: str


class FilterMetadata(_FilterMetadataRequired, _FilterMetadataOptional):
    pass


class _MetricMetadataRequired(TypedDict):
    id: str


class _MetricMetadataOptional(TypedDict, total=False):
    aggregations: List[AggregateMetadata]
    description: str
    filters: List[FilterMetadata]
    relatedREcordIds: List[str]


class MetricMetadata(_MetricMetadataRequired, _MetricMetadataOptional):
    pass


class FieldMetadata(TypedDict):
    description: str
    name: str
    nullable: bool


class _MetricRecordMetadataRequired(TypedDict):
    description: str
    id: str


class _MetricRecordMetadataOptional(TypedDict, total=False):
    fieldsMetadata: List[FieldMetadata]
    filters: List[FilterMetadata]
    relatedMetricIds: List[str]


class MetricRecordMetadata(
    _MetricRecordMetadataRequired, _MetricRecordMetadataOptional
):
    pass
