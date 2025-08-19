class AnalyticsLibError(Exception):
    pass


class AnalyticsLibFault(Exception):
    pass


class InvalidArnException(AnalyticsLibError):
    pass


class LivyConnectionError(AnalyticsLibError):
    pass


class MissingParametersError(AnalyticsLibError):
    pass


class InvalidParameterError(AnalyticsLibError):
    pass


class InvalidConfigError(AnalyticsLibError):
    pass


class InvalidEMRServerlessApplicationStateError(AnalyticsLibError):
    pass


class EMRServerlessApplicationStartTimeoutFault(AnalyticsLibFault):
    pass


class EMRServerlessFault(AnalyticsLibFault):
    pass


class EMRServerlessError(AnalyticsLibError):
    pass


class SparkSessionStartFailedFault(AnalyticsLibFault):
    pass


class SparkSessionStartFailedError(AnalyticsLibError):
    pass
