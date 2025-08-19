import unittest
from unittest.mock import patch, Mock
import subprocess
from sagemaker_studio_analytics_extension.utils.kerberos_reset_util import (
    _handle_kinit_reset_process,
)

DUMMY_USERNAME = "test_user"
DUMMY_PASSWORD = "old_pwd1!"
DUMMY_NEW_PASSWORD = Mock(value="new_pwd1!")
DUMMY_CONFIRM_PASSWORD = Mock(value="new_pwd1!")
DUMMY_KERBEROS_REALM = "TEST.COM"


class TestHandleKinitResetProcess(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.utils.kerberos_reset_util.subprocess.run"
    )
    def test_handle_kinit_reset_process_success(self, mock_subprocess_run):
        # Create a mock for subprocess.CompletedProcess for success
        mock_completed_process = Mock()
        mock_completed_process.args = ["kinit", DUMMY_USERNAME.encode()]
        mock_completed_process.returncode = 0
        mock_completed_process.stdout = bytes(
            f"Password for {DUMMY_USERNAME}@{DUMMY_KERBEROS_REALM}: \nPassword expired.  You must change it now.\nEnter new password: \nEnter it again: \n",
            encoding="utf-8",
        )
        mock_completed_process.stderr = b""

        # Configure the mock_subprocess_run to return the mock_completed_process
        mock_subprocess_run.return_value = mock_completed_process

        # Call the _handle_kinit_reset_process function
        result = _handle_kinit_reset_process(
            DUMMY_USERNAME, DUMMY_PASSWORD, DUMMY_NEW_PASSWORD, DUMMY_CONFIRM_PASSWORD
        )

        # Assertions for success case
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.args, ["kinit", DUMMY_USERNAME.encode()])
        self.assertEqual(
            result.stdout,
            bytes(
                f"Password for {DUMMY_USERNAME}@{DUMMY_KERBEROS_REALM}: \nPassword expired.  You must change it now.\nEnter new password: \nEnter it again: \n",
                encoding="utf-8",
            ),
        )
        self.assertEqual(result.stderr, b"")
        mock_subprocess_run.assert_called_once()

    @patch(
        "sagemaker_studio_analytics_extension.utils.kerberos_reset_util.subprocess.run"
    )
    def test_handle_kinit_reset_process_failure(self, mock_subprocess_run):
        # Create a mock for subprocess.CompletedProcess for failure
        mock_completed_process = Mock()
        mock_completed_process.args = ["kinit", DUMMY_USERNAME.encode()]
        mock_completed_process.returncode = (
            1  # Simulate a non-zero return code for failure
        )

        # Configure the mock_subprocess_run to return the mock_completed_process
        mock_subprocess_run.return_value = mock_completed_process

        # Call the _handle_kinit_reset_process function
        result = _handle_kinit_reset_process(
            DUMMY_USERNAME, DUMMY_PASSWORD, DUMMY_NEW_PASSWORD, DUMMY_CONFIRM_PASSWORD
        )

        # Assertions for failure case
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.args, ["kinit", DUMMY_USERNAME.encode()])
        mock_subprocess_run.assert_called_once()
