from sagemaker_studio_analytics_extension.utils.arn_util import RoleArnValidator
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    IPYTHON_KERNEL,
    LANGUAGES_SUPPORTED,
    AUTH_TYPE_SET,
)
from sagemaker_studio_analytics_extension.utils.exceptions import (
    MissingParametersError,
    InvalidParameterError,
)


class EMRValidator:
    REQUIRED_ARGS = ["cluster_id", "auth_type"]

    @staticmethod
    def validate_emr_args(args, usage, kernel_name):
        for arg in EMRValidator.REQUIRED_ARGS:
            if getattr(args, arg) is None:
                raise MissingParametersError(
                    "Missing required argument '--{}'. {}".format(
                        arg.replace("_", "-"), usage
                    )
                )

        if args.auth_type not in AUTH_TYPE_SET:
            raise MissingParametersError(
                "Invalid auth type, supported auth types are '{}'. {}".format(
                    AUTH_TYPE_SET, usage
                )
            )

        if args.assumable_role_arn:
            RoleArnValidator.validate(args.assumable_role_arn)

        if args.emr_execution_role_arn:
            RoleArnValidator.validate(args.emr_execution_role_arn)

        # Only IPython kernel needs language option support
        if kernel_name == IPYTHON_KERNEL:
            if args.language is None:
                raise MissingParametersError(
                    "Missing required argument '{}' for IPython kernel. {}".format(
                        "--language", usage
                    )
                )
            elif args.language not in LANGUAGES_SUPPORTED:
                raise InvalidParameterError(
                    "Invalid language, supported languages are '{}'. {}".format(
                        LANGUAGES_SUPPORTED, usage
                    )
                )
