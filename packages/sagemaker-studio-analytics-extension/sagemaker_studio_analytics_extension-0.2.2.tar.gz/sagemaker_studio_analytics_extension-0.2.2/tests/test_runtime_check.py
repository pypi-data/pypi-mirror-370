import io
import contextlib

from sagemaker_studio_analytics_extension.utils import runtime_check
from unittest.mock import patch


@patch("sagemaker_studio_analytics_extension.utils.runtime_check.find_spec")
def test_compatible_image(mock_find_spec):
    mock_find_spec.return_value = "found_module"
    # capture the stdout
    actual_result = io.StringIO()
    with contextlib.redirect_stdout(actual_result):
        runtime_check.main()

    assert mock_find_spec.call_count == 2
    expect_result = '{"namespace": "sagemaker-analytics", "emr": {"compatible": true}}'
    assert expect_result == actual_result.getvalue()


@patch("sagemaker_studio_analytics_extension.utils.runtime_check.find_spec")
def test_incompatible_image(mock_find_spec):
    # no module found
    mock_find_spec.return_value = None
    # capture the stdout
    actual_result = io.StringIO()
    with contextlib.redirect_stdout(actual_result):
        runtime_check.main()

    assert mock_find_spec.call_count == 1
    expect_result = '{"namespace": "sagemaker-analytics", "emr": {"compatible": false}}'
    assert expect_result == actual_result.getvalue()
