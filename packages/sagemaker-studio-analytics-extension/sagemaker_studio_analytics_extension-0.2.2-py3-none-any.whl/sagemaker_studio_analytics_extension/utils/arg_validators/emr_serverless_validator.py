from sagemaker_studio_analytics_extension.utils.arn_util import RoleArnValidator
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    IPYTHON_KERNEL,
    LANGUAGES_SUPPORTED,
)
from sagemaker_studio_analytics_extension.utils.exceptions import (
    MissingParametersError,
    InvalidParameterError,
)


class EMRServerlessValidator:
    REQUIRED_ARGS = ["application_id", "emr_execution_role_arn"]

    @staticmethod
    def validate_args_for_emr_serverless(args, usage, kernel_name):
        for arg in EMRServerlessValidator.REQUIRED_ARGS:
            if getattr(args, arg) is None:
                raise MissingParametersError(
                    "Missing required argument '--{}'. {}".format(
                        arg.replace("_", "-"), usage
                    )
                )

        RoleArnValidator.validate(args.emr_execution_role_arn)
        if args.assumable_role_arn:
            RoleArnValidator.validate(args.assumable_role_arn)

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
        if (
            args.auth_type is not None
            or args.secret is not None
            or args.verify_certificate is True
            or args.cluster_id is not None
        ):
            raise InvalidParameterError(
                "--cluster-id, --auth-type, --secret and --verify-certificate are not supported when connecting to "
                "EMR Serverless Applications"
            )
