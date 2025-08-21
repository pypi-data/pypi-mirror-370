import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "open-constructs-aws-cdk",
    "version": "0.1.1",
    "description": "@open-constructs/aws-cdk",
    "license": "Apache-2.0",
    "url": "https://github.com/open-constructs/aws-cdk-library.git",
    "long_description_content_type": "text/markdown",
    "author": "Open Construct Foundation<thorsten.hoeger@taimos.de>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/open-constructs/aws-cdk-library.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "open_constructs_aws_cdk",
        "open_constructs_aws_cdk._jsii",
        "open_constructs_aws_cdk.aws_codeartifact",
        "open_constructs_aws_cdk.aws_cur",
        "open_constructs_aws_cdk.aws_ec2",
        "open_constructs_aws_cdk.aws_elasticache",
        "open_constructs_aws_cdk.aws_fsx",
        "open_constructs_aws_cdk.aws_redshiftserverless"
    ],
    "package_data": {
        "open_constructs_aws_cdk._jsii": [
            "aws-cdk@0.1.1.jsii.tgz"
        ],
        "open_constructs_aws_cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.168.0, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.106.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
