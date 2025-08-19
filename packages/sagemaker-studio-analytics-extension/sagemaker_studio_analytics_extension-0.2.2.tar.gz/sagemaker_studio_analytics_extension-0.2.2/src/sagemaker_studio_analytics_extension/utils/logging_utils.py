import logging
import os
import sys
from uuid import uuid4


class ServiceFileLogger:
    """
    Logs service logs to a given file.
    """

    def __init__(
        self,
        log_file_name,
        log_base_directory,
        context_logger=None,
        also_write_to_stdout=False,
    ):
        """
        :param log_file_name:           File name to publish logs to
        :param log_base_directory:      log_base_directory : Creates directory structure if one does not exist.
        :param context_logger:          Loggers passed from caller's context.
                                        Errors while creating logger / logging are sent to this logger.
        :param also_write_to_stdout:    also_write_to_stdout
        """

        try:
            os.makedirs(log_base_directory, exist_ok=True)

            self.context_logger = context_logger

            self.file_logger = logging.getLogger(uuid4().hex)
            self.file_logger.handlers.clear()
            self.file_logger.setLevel(logging.INFO)

            file_path = os.path.join(log_base_directory, log_file_name)
            self.file_logger.addHandler(logging.FileHandler(file_path))

            if also_write_to_stdout:
                stream_handler = logging.StreamHandler(stream=sys.stdout)
                self.file_logger.addHandler(stream_handler)

        except Exception as e:
            self.file_logger = None
            if context_logger is not None:
                context_logger.error(f"Failed to initialize ServiceFileLogger: {e}")

    def log(self, payload):
        try:
            self.file_logger.info(payload)
        except Exception as e:
            if self.context_logger is not None:
                self.context_logger.error(f"Failed to log service payload: {e}")
