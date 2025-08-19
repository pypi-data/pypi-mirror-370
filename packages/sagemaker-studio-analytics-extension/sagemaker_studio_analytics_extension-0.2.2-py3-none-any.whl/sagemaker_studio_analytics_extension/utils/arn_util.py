from collections import namedtuple
from enum import Enum

from .exceptions import InvalidArnException

ARN = namedtuple("Arn", "prefix partition service region account_id resource")


class ArnParser:
    # Max character limit per: https://docs.aws.amazon.com/IAM/latest/APIReference/API_Policy.html
    MAX_CHARACTERS = 2048

    @staticmethod
    def parse(arn_string: str):
        """
        Parses and validates ARN.
        """
        arn_prefix = "arn"

        if not arn_string:
            raise InvalidArnException("Provided ARN is empty")

        if len(arn_string) >= ArnParser.MAX_CHARACTERS:
            raise InvalidArnException(
                f"ARN size must not exceed {ArnParser.MAX_CHARACTERS} character limit."
            )

        try:
            arn = ARN(*arn_string.split(":", 5))
        except TypeError:
            raise InvalidArnException(
                "ARNs must be of the form arn:partition:service:region:accountId:resource"
            )

        if arn.prefix != arn_prefix:
            raise InvalidArnException(f"ARNs must start with `{arn_prefix}`")

        if not arn.partition:
            raise InvalidArnException("Partition must be non-empty.")

        if arn.partition not in Partition.__members__.values():
            raise InvalidArnException(f"Invalid partition: {arn.partition}")

        if not arn.service:
            raise InvalidArnException("Service must be non-empty.")

        if not arn.resource:
            raise InvalidArnException("Resource must be non-empty.")

        return arn


class RoleArnValidator:
    IAM_SERVICE = "iam"
    ROLE_RESOURCE = "role"

    @staticmethod
    def validate(arn_string: str):
        """
        Validate that the given ARN represents an IAM role
        """
        arn = ArnParser.parse(arn_string)
        if arn.service != RoleArnValidator.IAM_SERVICE:
            raise InvalidArnException(
                f"Incorrect Role ARN. Provided service {arn.service} does not match expected "
                + f"service `{RoleArnValidator.IAM_SERVICE}`"
            )
        if not arn.resource.startswith(RoleArnValidator.ROLE_RESOURCE):
            raise InvalidArnException(
                f"Incorrect Role ARN. Provided resource {arn.resource} does not correspond to "
                + f"expected resource `{RoleArnValidator.ROLE_RESOURCE}`"
            )


class Partition(str, Enum):
    """
    Supported AWS partitions
    """

    AWS = "aws"
    AWS_CN = "aws-cn"
    AWS_GOV = "aws-us-gov"
