# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import setuptools

with open("README.md", "r") as readme:
    markdown_description = "".join(readme.readlines())

setuptools.setup(
    name="aioli-sdk",
    version="1.9.0",
    author="HPE AI Solutions",
    # author_email="hello@determined.ai",
    url="https://github.com/determined-ai/aioli",
    description="Aioli (AI OnLine Inference), a platform for deploying AI models at scale.",
    long_description = markdown_description,
    long_description_content_type = "text/markdown",
    license="Apache License 2.0",
    # classifiers=["License :: OSI Approved :: Apache Software License"],
    # Use find_namespace_packages because it will include data-only packages
    # (that is, directories containing only non-python files, like our gcp
    # terraform directory).
    packages=setuptools.find_namespace_packages(include=["aioli*"]),
    python_requires=">=3.8",
    include_package_data=True,
    install_requires=[
        "packaging",
        "numpy>=1.16.2",
        "psutil",
        "pyzmq>=18.1.0",
        # "yogadl==0.1.4",
        # Common:
        "certifi",
        "filelock",
        "requests",
        # "google-cloud-storage",
        "lomond>=0.3.3",
        "pathspec>=0.6.0",
        # "azure-core",
        # "azure-storage-blob",
        "termcolor>=1.1.0",
        "oschmod;platform_system=='Windows'",
        # CLI:
        "argcomplete>=1.9.4",
        "gitpython>=3.1.3",
        "pyOpenSSL>= 19.1.0",
        "python-dateutil",
        "pytz",
        "tabulate>=0.8.3",
        # det preview-search "pretty-dumps" a sub-yaml with an API added in 0.15.29
        "ruamel.yaml>=0.15.29",
        # Deploy
        "docker[ssh]>=3.7.3",
        # "google-api-python-client>=1.12.1",
        "paramiko>=2.4.2",  # explicitly pull in paramiko to prevent DistributionNotFound error
        "tqdm",
        "appdirs",
        # Telemetry
        "analytics-python",
        # OpenAPI generated code additional requirements
        "urllib3 >= 2.0.0, < 2.3.0",
        "pydantic >= 2",
        "typing-extensions >= 4.7.1",
        "pytest>=7.4.4",
        "pytest-cov>=4.1.0",
        "pexpect>=4.9.0",

    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "aioli = aioli.cli.__main__:main",
        ]
    },
)
