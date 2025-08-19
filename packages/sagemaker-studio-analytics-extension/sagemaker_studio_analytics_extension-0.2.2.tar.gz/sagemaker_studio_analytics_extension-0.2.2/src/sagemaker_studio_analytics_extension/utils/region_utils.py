from botocore.session import Session
from sagemaker_studio_analytics_extension.utils.constants import USE_DUALSTACK_ENDPOINT


def get_regional_dns_suffix(botocore_session: Session, region_name: str) -> str:
    endpoint_resolver = botocore_session.get_component("endpoint_resolver")
    partition = endpoint_resolver.get_partition_for_region(region_name)
    return endpoint_resolver.get_partition_dns_suffix(partition)


def get_regional_service_endpoint_url(
    botocore_session: Session, service_name: str, region_name: str
) -> str:
    endpoint_resolver = botocore_session.get_component("endpoint_resolver")
    partition_name = endpoint_resolver.get_partition_for_region(region_name)
    endpoint_data = endpoint_resolver.construct_endpoint(
        service_name=service_name,
        region_name=region_name,
        partition_name=partition_name,
        use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT,
    )
    if endpoint_data and "hostname" in endpoint_data:
        resolved_url = endpoint_data["hostname"]
        if not resolved_url.startswith("https://"):
            resolved_url = "https://" + resolved_url
        return resolved_url
    else:
        dns_suffix = endpoint_resolver.get_partition_dns_suffix(partition_name)
        return f"https://{service_name}.{region_name}.{dns_suffix}"
