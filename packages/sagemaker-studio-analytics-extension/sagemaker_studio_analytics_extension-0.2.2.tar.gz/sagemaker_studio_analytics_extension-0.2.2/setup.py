import os
import setuptools
import sysconfig
from setuptools.command.install import install

NAME = "sagemaker-studio-analytics-extension"
AUTHOR = "Amazon Web Services"
DESCRIPTION = "SageMaker Studio Analytics Extension"
LICENSE = "Apache 2.0"
URL = "https://aws.amazon.com/sagemaker"
README = "README.md"
VERSION = "0.2.2"
CLASSIFIERS = [
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.10",
]

INSTALL_REQUIRES = [
    "boto3>=1.26.49, < 2.0",
    "sparkmagic==0.22.0",
    "sagemaker_studio_sparkmagic_lib>=0.1.1",
    "sagemaker-jupyterlab-extension-common>=0.2.2, <1.0",
    "filelock>=3.0.12",
]
ENTRY_POINTS = {
    "console_scripts": [
        "sm_analytics_runtime_check=sagemaker_studio_analytics_extension.utils.runtime_check:main"
    ]
}

HERE = os.path.dirname(__file__)


def read(file):
    with open(os.path.join(HERE, file), "r") as fh:
        return fh.read()


LONG_DESCRIPTION = read(README)


class PostInstallCommand(install):
    """
    Post-installation method which runs after package installation
    See https://stackoverflow.com/questions/20288711
    """

    def run(self):
        install.run(self)

        source_dir = os.path.join(
            HERE, "src", "sagemaker_studio_analytics_extension", "patches"
        )
        # https://stackoverflow.com/questions/122327
        destination_dir = os.path.join(sysconfig.get_paths()["purelib"], "sparkmagic")

        if os.path.exists(destination_dir):
            os.system(
                f"cp -R {source_dir}/configuration.py {destination_dir}/utils/configuration.py"
            )
            os.system(
                f"cp -R {source_dir}/reliablehttpclient.py {destination_dir}/livyclientlib/reliablehttpclient.py"
            )


if __name__ == "__main__":
    setuptools.setup(
        name=NAME,
        version=VERSION,
        package_dir={"": "src"},
        packages=[
            "sagemaker_studio_analytics_extension",
            "sagemaker_studio_analytics_extension/utils",
            "sagemaker_studio_analytics_extension/magics",
            "sagemaker_studio_analytics_extension/resource/",
            "sagemaker_studio_analytics_extension/resource/emr/",
            "sagemaker_studio_analytics_extension/utils/arg_validators/",
            "sagemaker_studio_analytics_extension/external_dependencies/",
            "sagemaker_studio_analytics_extension/resource/emr_serverless/",
        ],
        data_files=[
            (
                "patches",
                [
                    "src/sagemaker_studio_analytics_extension/patches/configuration.py",
                    "src/sagemaker_studio_analytics_extension/patches/reliablehttpclient.py",
                ],
            ),
        ],
        author=AUTHOR,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        license=LICENSE,
        url=URL,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        include_package_data=True,
        cmdclass={
            "install": PostInstallCommand,
        },
    )
