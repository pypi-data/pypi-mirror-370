from dataclasses import dataclass


@dataclass
class MagicExecutionContext:
    """
    Object to track context about a magic execution. Can be used for:
    * Passing data around different methods
    * Passing data to query logger
    """

    connection_protocol: str = None
