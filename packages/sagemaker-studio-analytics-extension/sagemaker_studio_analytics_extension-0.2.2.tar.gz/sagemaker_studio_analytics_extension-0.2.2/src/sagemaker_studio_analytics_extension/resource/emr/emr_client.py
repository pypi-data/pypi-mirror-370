import warnings

from sagemaker_studio_sparkmagic_lib.emr import utils


def get_emr_client(boto_session):
    """
    https://github.com/boto/botocore/issues/2705

    We are already overriding emr client with correct endpoint overrides
    following the pattern {service}.{region}.{dnsSuffix}
    """
    warnings.filterwarnings("ignore", category=FutureWarning, module="botocore.client")

    # We need to make an EMR list instance groups call, which the sagemaker-studio-sparkmagic-lib instantiated EMR
    # client doesn't do. Also, the EMRCluster object does not provide a getter to reuse the EMR client instantiated
    # through that class. Hence we need a new client, till we can refactor both libraries. This should be fixed
    # during combined refactoring of sagemaker-studio-sparkmagic-lib and sagemaker-analytics library.
    """
    boto3 url for EMR is not constructed correctly in some regions See https://github.com/boto/botocore/issues/2376
        @TODO: Deprecate after  https://github.com/boto/botocore/issues/2376 is fixed

        This causes issues when customer use Private Link for EMR without internet connections

        As per recommendation we construct EMR endpoints to match https://docs.aws.amazon.com/general/latest/gr/emr.html
    """
    return boto_session.client("emr", endpoint_url=get_emr_endpoint_url(boto_session))


def get_emr_endpoint_url(boto_session):
    return utils.get_emr_endpoint_url(boto_session.region_name)
