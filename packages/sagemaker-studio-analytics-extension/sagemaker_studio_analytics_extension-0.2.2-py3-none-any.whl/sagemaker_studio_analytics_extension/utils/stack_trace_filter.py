import re

from .constants import (
    email_regex,
    phone_number_regex,
    password_regex,
    api_key_regex,
    aws_secretkey_regex,
)


class StackTraceFilter:
    def __init__(self):
        # Define patterns for potentially sensitive data
        self.patterns = [
            (re.compile(email_regex), "<EMAIL>"),
            (re.compile(phone_number_regex), "<PHONE>"),
            (re.compile(password_regex), "<SECRET>"),
            (re.compile(api_key_regex), "<SECRET>"),
            (re.compile(aws_secretkey_regex), "<AWS_SECRET>"),
        ]

    def filter(self, stack_trace: str) -> str:
        """Filter sensitive data from the given stack trace."""
        for pattern, replacement in self.patterns:
            stack_trace = re.sub(pattern, replacement, stack_trace)
        return stack_trace
