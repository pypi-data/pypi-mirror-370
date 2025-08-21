from typing import List, Optional, TypedDict, Union

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.analytics import (
    Filter,
    FilterValue,
    Interval,
    MetricData,
    MetricMetadata,
    MetricRecord,
    MetricRecordMetadata,
    Preset,
)


class AnalyticsGetMetricDataBody(TypedDict):
    aggregations: List[str]
    filters: Optional[List[Filter]]
    id: str
    periodFilter: Union[Interval, Preset]
    timezone: str


class AnalyticsGetMetricRecordsDataBody(TypedDict):
    filters: Optional[List[Filter]]
    id: str
    periodFilter: Union[Interval, Preset]
    timezone: str


class AnalyticsResource(DixaResource):
    """
    https://developer.rechargepayments.com/2021-01/addresses
    """

    resource = "analytics"
    dixa_version: DixaVersion = "v1"

    def filter(self, filter_attribute: str) -> List[FilterValue]:
        """Filter values.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/getAnalyticsFilterFilterattribute
        """
        return self.client.paginate(f"{self._url}/filter/{filter_attribute}")

    def get_metric_data(self, body: AnalyticsGetMetricDataBody) -> MetricData:
        """Get metric data.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/postAnalyticsMetrics
        """
        data = self.client.post(f"{self._url}/metrics", body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return MetricData(**data)

    def get_metric_records_data(
        self, body: AnalyticsGetMetricRecordsDataBody
    ) -> List[MetricRecord]:
        """Get metric records data.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/postAnalyticsRecords
        """
        data = self.client.post(f"{self._url}/records", body, list)
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        return [MetricRecord(**elem) for elem in data]

    def get_metric_description(self, metric_id: str) -> MetricMetadata:
        """Get metric description.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/getAnalyticsMetricsMetricid
        """
        data = self.client.get(f"{self._url}/metrics/{metric_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return MetricMetadata(**data)

    def get_metric_record_description(self, record_id: str) -> MetricRecordMetadata:
        """Get metric record description.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/getAnalyticsRecordsRecordid
        """
        data = self.client.get(f"{self._url}/records/{record_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return MetricRecordMetadata(**data)

    def get_metric_records_catalogue(
        self, query: Union[dict, None] = None
    ) -> List[MetricRecordMetadata]:
        """Get metric record description.

        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/getAnalyticsRecordsRecordid
        """
        return self.client.paginate(f"{self._url}/records", query)

    def get_metrics_catalogue(
        self, query: Union[dict, None] = None
    ) -> List[MetricMetadata]:
        """Get metrics catalogue.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Analytics/#tag/Analytics/operation/getAnalyticsMetrics
        """
        return self.client.paginate(f"{self._url}/metrics", query)
