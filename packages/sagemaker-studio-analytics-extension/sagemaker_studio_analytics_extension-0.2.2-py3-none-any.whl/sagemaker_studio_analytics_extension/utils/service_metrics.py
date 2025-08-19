import traceback

import botocore
import time
import json
from enum import Enum
import functools

from sparkmagic.livyclientlib.exceptions import EXPECTED_EXCEPTIONS

from .constants import (
    OPERATION,
    SERVICE,
    AUTH_TYPE_SET_FOR_LOGGING,
    VerifyCertificateArgument,
)
from .exceptions import AnalyticsLibError
from .stack_trace_filter import StackTraceFilter

from ..resource.resource_metadata import ResourceMetadata
from ..resource.emr.auth import ClusterAuthUtils

resource_metadata = ResourceMetadata()


class MetricDimension(str, Enum):
    LibraryVersion = "LibraryVersion"
    Service = "Service"
    Operation = "Operation"
    AccountId = "AccountId"
    EventTimeStampMillis = "EventTimeStampMillis"
    Success = "Success"
    Fault = "Fault"
    Error = "Error"
    Exception = "Exception"
    ExceptionString = "ExceptionString"
    OperationStartTimeMillis = "OperationStartTimeMillis"
    OperationEndTimeMillis = "OperationEndTimeMillis"
    OperationDurationMillis = "OperationDurationMillis"
    KernelName = "KernelName"
    ClusterId = "ClusterId"
    AuthType = "AuthType"
    VerifyCertificate = "VerifyCertificate"
    ConnectionProtocol = "ConnectionProtocol"
    StackTrace = "StackTrace"
    ServerlessApplicationId = "ServerlessApplicationId"

    def __str__(self):
        return str.__str__(self)


class ServiceMetric:
    def __init__(
        self,
        resource_metadata,
        service: SERVICE,
        operation: OPERATION,
    ) -> None:
        self._data = dict()
        if resource_metadata.library_version:
            self._data[MetricDimension.LibraryVersion.value] = (
                resource_metadata.library_version
            )
        self._data[MetricDimension.Service.value] = service.value
        self._data[MetricDimension.Operation.value] = operation.value
        self._data[MetricDimension.AccountId.value] = resource_metadata.account_id
        self._data[MetricDimension.EventTimeStampMillis.value] = None
        self._data[MetricDimension.Exception.value] = None
        self._data[MetricDimension.ExceptionString.value] = None
        self._data[MetricDimension.Error.value] = 0
        self._data[MetricDimension.Fault.value] = 0
        self._data[MetricDimension.Success.value] = None
        self._data[MetricDimension.AuthType.value] = None
        self._data[MetricDimension.ConnectionProtocol.value] = None
        self._data[MetricDimension.StackTrace.value] = None
        self._stack_trace_filter = StackTraceFilter()

    def put(self, **kwargs) -> None:
        self._data.update(kwargs)

    def set_error(self, ex: Exception) -> None:
        """
        Failure due to user-error.
        :param ex: Exception
        :return: None
        """
        self._data[MetricDimension.Error.value] = 1
        self._data[MetricDimension.Exception.value] = ex.__class__.__name__
        # Safe to log AnalyticsLibError details
        if isinstance(ex, AnalyticsLibError):
            self._data[MetricDimension.ExceptionString.value] = str(ex)
        self._data[MetricDimension.StackTrace.value] = self._stack_trace_filter.filter(
            traceback.format_exc()
        )

    def set_fault(self, ex: Exception) -> None:
        """
        Failure due to system faults.
        Note that currently we're considering all failures (even user-errors) as faults, making the fault metric noisy.
        :param ex: Exception
        :return: None
        """
        self._data[MetricDimension.Fault.value] = 1
        self._data[MetricDimension.Exception.value] = ex.__class__.__name__
        self._data[MetricDimension.StackTrace.value] = self._stack_trace_filter.filter(
            traceback.format_exc()
        )

    def set_auth_type(self, auth_type) -> None:
        """
        Auth type to log.
        :param auth_type: str
        :return: None
        """
        if auth_type not in AUTH_TYPE_SET_FOR_LOGGING:
            raise ValueError(
                f"Invalid auth type for logging - '{auth_type}'. Should be one of {AUTH_TYPE_SET_FOR_LOGGING}"
            )
        self._data[MetricDimension.AuthType.value] = auth_type

    def set_connection_protocol(self, protocol: str) -> None:
        self._data[MetricDimension.ConnectionProtocol.value] = protocol

    def serialize(self) -> str:
        return json.dumps(self._data)

    def finalize_metric(self) -> None:
        self._data[MetricDimension.Success.value] = (
            0
            if (
                self._data[MetricDimension.Fault.value] == 1
                or self._data[MetricDimension.Error.value] == 1
            )
            else 1
        )
        self._data[MetricDimension.EventTimeStampMillis.value] = time.time() * 1000

    def __str__(self) -> str:
        return self.serialize()

    @staticmethod
    def responds_to(**kwargs):
        """
        Determine if this is an appropriate metric to be used for given kwargs.
        :param kwargs:
        :return:
        """
        return False


class TimedMetric:
    def __init__(self, service: SERVICE, operation: OPERATION) -> None:
        self.__operation = operation
        self.__service = service
        self._start_time = None
        self._end_time = None
        self._duration = None

    def start_timer(self) -> None:
        self._start_time = time.time() * 1000

    def stop_timer(self) -> None:
        if self.is_timer_running():
            self._end_time = time.time() * 1000
            # System clock can be set backwards. In that case, discard duration.
            self._duration = max(self._end_time - self._start_time, 0)

    def is_timer_running(self) -> bool:
        return self._start_time is not None and self._end_time is None

    def finalize_metric(self) -> None:
        self.stop_timer()


class TimedServiceMetric(ServiceMetric, TimedMetric):
    def __init__(
        self, resource_metadata, service: SERVICE, operation: OPERATION, **kwargs
    ) -> None:
        ServiceMetric.__init__(self, resource_metadata, service, operation)
        TimedMetric.__init__(self, service, operation)
        self._data[MetricDimension.OperationStartTimeMillis.value] = None
        self._data[MetricDimension.OperationEndTimeMillis.value] = None
        self._data[MetricDimension.OperationDurationMillis.value] = None

    def serialize(self) -> str:
        self._data[MetricDimension.OperationStartTimeMillis.value] = self._start_time
        self._data[MetricDimension.OperationEndTimeMillis.value] = self._end_time
        self._data[MetricDimension.OperationDurationMillis.value] = self._duration
        return super().serialize()

    def finalize_metric(self) -> None:
        TimedMetric.finalize_metric(self)
        ServiceMetric.finalize_metric(self)


class EmrConnectionServiceMetric(TimedServiceMetric):
    SERVICE = SERVICE.EMR
    OPERATION = OPERATION.CONNECT

    def __init__(self, resource_metadata, **kwargs) -> None:
        super().__init__(
            resource_metadata,
            EmrConnectionServiceMetric.SERVICE,
            EmrConnectionServiceMetric.OPERATION,
        )

        args = kwargs["args"]
        if "kernel_name" in kwargs:
            self._data[MetricDimension.KernelName] = kwargs["kernel_name"]
        self._data[MetricDimension.ClusterId.value] = args.cluster_id
        self._data[MetricDimension.VerifyCertificate.value] = (
            args.verify_certificate.type.value
        )

    @staticmethod
    def responds_to(**kwargs):
        try:
            service = kwargs["service"]
            operation = kwargs["operation"]
            return (
                service == EmrConnectionServiceMetric.SERVICE
                and operation == EmrConnectionServiceMetric.OPERATION
            )
        except KeyError:
            return False


class EmrServerlessConnectionServiceMetric(TimedServiceMetric):
    SERVICE = SERVICE.EMR_SERVERLESS
    OPERATION = OPERATION.EMRS_CONNECT

    def __init__(self, resource_metadata, **kwargs) -> None:
        super().__init__(
            resource_metadata,
            EmrServerlessConnectionServiceMetric.SERVICE,
            EmrServerlessConnectionServiceMetric.OPERATION,
        )

        args = kwargs["args"]
        if "kernel_name" in kwargs:
            self._data[MetricDimension.KernelName] = kwargs["kernel_name"]
        self._data[MetricDimension.ServerlessApplicationId.value] = args.application_id

    @staticmethod
    def responds_to(**kwargs):
        try:
            service = kwargs["service"]
            return service == EmrServerlessConnectionServiceMetric.SERVICE
        except KeyError:
            return False


class MetricFactory:
    class NoValidMetricFoundException(Exception):
        """
        Do not log kwargs passed to metric. kwargs may contain sensitive data.
        """

        pass

    SERVICE_METRIC_SUBCLASSES = None

    @staticmethod
    def create_metric(resource_metadata: ResourceMetadata, **kwargs) -> ServiceMetric:
        """
        Creates an instance of a child of ServiceMetric class which responds to the given kwargs.
        :param resource_metadata:   resource_metadata
        :param kwargs:              kwargs
        :return:                    Child of ServiceMetric
        """
        if MetricFactory.SERVICE_METRIC_SUBCLASSES is None:
            SERVICE_METRIC_SUBCLASSES = MetricFactory._all_subclasses(ServiceMetric)

        for metric_class in SERVICE_METRIC_SUBCLASSES:
            if metric_class.responds_to(**kwargs):
                return metric_class(resource_metadata, **kwargs)
        raise MetricFactory.NoValidMetricFoundException()

    @staticmethod
    def _all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in MetricFactory._all_subclasses(c)]
        )


def records_service_metrics(func):
    """
    Records a timed metric which measures latency for the provided func.
    In case of errors, fails silently, ensuring original library is not impacted for service logs.
    :param func: function for which to record a timed metric
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        :param args:        args.
        :param kwargs:      kwargs. Must contain `service_logger` key.
        :return:
        """
        service_logger = kwargs["service_logger"]
        context = kwargs["context"]

        metric = None

        try:
            metric = MetricFactory.create_metric(resource_metadata, **kwargs)
            if isinstance(metric, TimedMetric):
                metric.start_timer()
        except Exception as ex:
            service_logger.log(
                f"Failed to create metric or start_timer: {ex.__class__.__name__} : {ex}"
            )

        try:
            ret_val = func(*args, **kwargs)
        except Exception as e:
            if metric is not None:
                if is_customer_error(e):
                    metric.set_error(e)
                else:
                    metric.set_fault(e)
                metric.finalize_metric()
                service_logger.log(metric)
            raise e
        arguments = kwargs["args"]
        if "cluster_id" in arguments and arguments.cluster_id is not None:
            metric.set_auth_type(ClusterAuthUtils.get_auth_type_for_logging(**kwargs))
            metric.set_connection_protocol(context.connection_protocol)
        metric.finalize_metric()
        service_logger.log(metric)

        return ret_val

    return wrapper


def is_customer_error(e: Exception):
    is_livy_expected_exception = False
    for livy_expected_exception in tuple(EXPECTED_EXCEPTIONS):
        if isinstance(e, livy_expected_exception):
            is_livy_expected_exception = True

    return (
        isinstance(e, AnalyticsLibError)
        or isinstance(e, botocore.exceptions.ClientError)
        or is_livy_expected_exception
    )
