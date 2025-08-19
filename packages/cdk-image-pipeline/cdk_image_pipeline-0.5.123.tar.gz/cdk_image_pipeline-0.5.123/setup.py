import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-image-pipeline",
    "version": "0.5.123",
    "description": "Quickly deploy a complete EC2 Image Builder Image Pipeline using CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/aws-samples/cdk-image-pipeline.git",
    "long_description_content_type": "text/markdown",
    "author": "Cameron Magee<magcamer@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/cdk-image-pipeline.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_image_pipeline",
        "cdk_image_pipeline._jsii"
    ],
    "package_data": {
        "cdk_image_pipeline._jsii": [
            "cdk-image-pipeline@0.5.123.jsii.tgz"
        ],
        "cdk_image_pipeline": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.189.1, <3.0.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.113.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
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
