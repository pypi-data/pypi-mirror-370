r'''
[![npm version](https://badge.fury.io/js/cdk-image-pipeline.svg)](https://badge.fury.io/js/cdk-image-pipeline)
[![PyPI version](https://badge.fury.io/py/cdk-image-pipeline.svg)](https://badge.fury.io/py/cdk-image-pipeline)
[![GitHub version](https://badge.fury.io/gh/aws-samples%2Fcdk-image-pipeline.svg)](https://badge.fury.io/gh/aws-samples%2Fcdk-image-pipeline)

# CDK Image Pipeline

---


L3 construct that can be used to quickly deploy a complete EC2 Image Builder Image Pipeline.

This construct creates the required infrastructure for an Image Pipeline:

* Infrastructure configuration which specifies the infrastructure within which to build and test your EC2 Image Builder image.
* An instance profile associated with the infrastructure configuration
* An EC2 Image Builder recipe defines the base image to use as your starting point to create a new image, along with the set of components that you add to customize your image and verify that everything is working as expected.
* Image Builder uses the AWS Task Orchestrator and Executor (AWSTOE) component management application to orchestrate complex workflows. AWSTOE components are based on YAML documents that define the scripts to customize or test your image. Support for multiple components.
* Image Builder image pipelines provide an automation framework for creating and maintaining custom AMIs and container images.

## Install

---


NPM install:

```sh
npm install cdk-image-pipeline
```

PyPi install:

```sh
pip install cdk-image-pipeline
```

## Usage

---


```python
import { ImagePipeline } from 'cdk-image-pipeline'
import { Construct } from 'constructs';

// ...
// Create a new image pipeline with the required properties
new ImagePipeline(this, "MyImagePipeline", {
    components: [
      {
        document: 'component_example.yml',
        name: 'Component',
        version: '0.0.1',
      },
      {
        document: 'component_example_2.yml',
        name: 'Component2',
        version: '0.1.0',
      },
    ],
    parentImage: 'ami-0e1d30f2c40c4c701',
    ebsVolumeConfigurations: [
        {
            deviceName: '/dev/xvda',
            ebs: {
                encrypted: true,
                iops: 200,
                kmsKeyId: 'alias/app1/key',
                volumeSize: 20,
                volumeType: 'gp3',
                throughput: 1000,
            },
        },
    ],
})
// ...
```

By default, the infrastructure configuration will deploy EC2 instances for the build/test phases into a default VPC using the default security group. If you want to control where the instances are launched, you can specify an existing VPC `SubnetID` and a list of `SecurityGroupIds`. In the example below, a new VPC is created and referenced in the `ImagePipeline` construct object.

```python
import { ImagePipeline } from 'cdk-image-pipeline'
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

// ...
// create a new VPC
const vpc = new ec2.Vpc(this, "Vpc", {
    cidr: "10.0.0.0/16",
    maxAzs: 2,
    subnetConfiguration: [
        {
            cidrMask: 24,
            name: 'ingress',
            subnetType: ec2.SubnetType.PUBLIC,
        },
        {
            cidrMask: 24,
            name: 'imagebuilder',
            subnetType: ec2.SubnetType.PRIVATE_WITH_NAT,
        },
    ]
});

// create a new security group within the VPC
const sg = new ec2.SecurityGroup(this, "SecurityGroup", {
    vpc:vpc,
});

// get the private subnet from the vpc
const private_subnet = vpc.privateSubnets;


new ImagePipeline(this, "MyImagePipeline", {
    components: [
      {
        document: 'component_example.yml',
        name: 'Component',
        version: '0.0.1',
      },
      {
        document: 'component_example_2.yml',
        name: 'Component2',
        version: '0.1.0',
      },
    ],
    parentImage: 'ami-0e1d30f2c40c4c701',
    securityGroups: [sg.securityGroupId],
    subnetId: private_subnet[0].subnetId,
})
// ...
```

Python usage:

```python
from cdk_image_pipeline import ImagePipeline
from constructs import Construct

# ...
image_pipeline = ImagePipeline(
    self,
    "LatestImagePipeline",
    components=[
      {
        document: 'component_example.yml',
        name: 'Component',
        version: '0.0.1',
      },
      {
        document: 'component_example_2.yml',
        name: 'Component2',
        version: '0.1.0',
      },
    ],
    parent_image="ami-0e1d30f2c40c4c701",
)
# ...
```

```python
from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct
from cdk_image_pipeline import ImagePipeline

# ...
# create a new VPC
vpc = ec2.Vpc(
    self,
    "MyVpcForImageBuilder",
    cidr="10.0.0.0/16",
    max_azs=2,
    subnet_configuration=[
        ec2.SubnetConfiguration(
            name="Ingress",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24,
        ),
        ec2.SubnetConfiguration(
            name="ImageBuilder", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT, cidr_mask=24
        ),
    ],
)

# create a new security group within the VPC
sg = ec2.SecurityGroup(self, "SG", vpc=vpc)

# get the private subnet from the vpc
priv_subnets = vpc.private_subnets


image_pipeline = ImagePipeline(
    self,
    "LatestImagePipeline",
    components=[
      {
        document: 'component_example.yml',
        name: 'Component',
        version: '0.0.1',
      },
      {
        document: 'component_example_2.yml',
        name: 'Component2',
        version: '0.1.0',
      },
    ],
    parent_image="ami-0e1d30f2c40c4c701",
    security_groups=[sg.security_group_id],
    subnet_id=priv_subnets[0].subnet_id
)
# ...
```

### Component Documents

---


Image Builder uses the AWS Task Orchestrator and Executor (AWSTOE) component management application to orchestrate complex workflows. AWSTOE components are based on YAML documents that define the scripts to customize or test your image.

You must provide a [component document](https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-components.html) in YAML to the `ImagePipeline` construct. See the example document below:

```yaml
name: MyComponentDocument
description: This is an example component document
schemaVersion: 1.0

phases:
  - name: build
    steps:
      - name: InstallUpdates
        action: UpdateOS
  - name: validate
    steps:
      - name: HelloWorldStep
        action: ExecuteBash
        inputs:
          commands:
            - echo "Hello World! Validate."
  - name: test
    steps:
      - name: HelloWorldStep
        action: ExecuteBash
        inputs:
          commands:
            - echo "Hello World! Test.
```

### Multiple Components

To specify multiple components, add additional component documents to the `componentDoucments` property. You can also add the names and versions of these components via the `componentNames` and `componentVersions` properties (*See usage examples above*). The components will be associated to the Image Recipe that gets created as part of the construct.

Be sure to update the `imageRecipeVersion` property when making updates to your components after your initial deployment.

### SNS Encryption using KMS

---


Specify a KMS Key via the `kmsKey` property which will be used to encrypt the SNS topic.

### Infrastructure Configuration Instance Types

---


[Infrastructure configuration](https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-infra-config.html) contain settings for building and testing your EC2 Image Builder image. This construct allows you to specify a list of instance types you wish to use via the `instanceTypes` property. The default is: `['t3.medium', 'm5.large', 'm5.xlarge']`.

## Additional API notes

---


[API Reference](API.md)
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_imagebuilder as _aws_cdk_aws_imagebuilder_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="cdk-image-pipeline.ComponentProps",
    jsii_struct_bases=[],
    name_mapping={"document": "document", "name": "name", "version": "version"},
)
class ComponentProps:
    def __init__(
        self,
        *,
        document: builtins.str,
        name: builtins.str,
        version: builtins.str,
    ) -> None:
        '''
        :param document: Relative path to Image Builder component document.
        :param name: Name of the Component Document.
        :param version: Version for each component document.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8f4421f08d0eeed51801e1088743e803f62672d6b4b15c72fc46f8f8a1ceffa)
            check_type(argname="argument document", value=document, expected_type=type_hints["document"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "document": document,
            "name": name,
            "version": version,
        }

    @builtins.property
    def document(self) -> builtins.str:
        '''Relative path to Image Builder component document.'''
        result = self._values.get("document")
        assert result is not None, "Required property 'document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Component Document.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Version for each component document.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ComponentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImagePipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-image-pipeline.ImagePipeline",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        components: typing.Sequence[typing.Union[builtins.str, typing.Union[ComponentProps, typing.Dict[builtins.str, typing.Any]]]],
        parent_image: builtins.str,
        additional_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
        ami_id_ssm_account_id: typing.Optional[builtins.str] = None,
        ami_id_ssm_path: typing.Optional[builtins.str] = None,
        ami_id_ssm_region: typing.Optional[builtins.str] = None,
        distribution_account_i_ds: typing.Optional[typing.Sequence[builtins.str]] = None,
        distribution_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        ebs_volume_configurations: typing.Optional[typing.Sequence[typing.Union["VolumeProps", typing.Dict[builtins.str, typing.Any]]]] = None,
        email: typing.Optional[builtins.str] = None,
        enable_cross_account_distribution: typing.Optional[builtins.bool] = None,
        enable_vuln_scans: typing.Optional[builtins.bool] = None,
        image_recipe_version: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        schedule: typing.Optional[typing.Union["ImagePipelineSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        user_data_script: typing.Optional[builtins.str] = None,
        vuln_scans_repo_name: typing.Optional[builtins.str] = None,
        vuln_scans_repo_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param components: List of component props.
        :param parent_image: The source (parent) image that the image recipe uses as its base environment. The value can be the parent image ARN or an Image Builder AMI ID
        :param additional_policies: Additional policies to add to the instance profile associated with the Instance Configurations.
        :param ami_id_ssm_account_id: Account ID for Parameter Store path above.
        :param ami_id_ssm_path: Parameter Store path to store latest AMI ID under.
        :param ami_id_ssm_region: Region for Parameter Store path above.
        :param distribution_account_i_ds: List of accounts to copy this AMI to, if the option to do so is enabled.
        :param distribution_regions: List of regions to copy this AMI to, if the option to do so is enabled.
        :param ebs_volume_configurations: Configuration for the AMI's EBS volumes.
        :param email: Email used to receive Image Builder Pipeline Notifications via SNS.
        :param enable_cross_account_distribution: Set to true if you want to copy this AMI to other accounts using a Distribution Configuration.
        :param enable_vuln_scans: Set to true if you want to enable continuous vulnerability scans through AWS Inpector.
        :param image_recipe_version: Image recipe version (Default: 0.0.1).
        :param instance_types: List of instance types used in the Instance Configuration (Default: [ 't3.medium', 'm5.large', 'm5.xlarge' ]).
        :param kms_key: KMS Key used to encrypt the SNS topic.
        :param name: Name of the Image Pipeline.
        :param platform: Platform type Linux or Windows (Default: Linux).
        :param resource_tags: The tags attached to the resource created by Image Builder.
        :param schedule: Schedule configuration for the image pipeline.
        :param security_groups: List of security group IDs for the Infrastructure Configuration.
        :param subnet_id: Subnet ID for the Infrastructure Configuration.
        :param user_data_script: UserData script that will override default one (if specified). Default: - none
        :param vuln_scans_repo_name: Store vulnerability scans through AWS Inpsector in ECR using this repo name (if option is enabled).
        :param vuln_scans_repo_tags: Store vulnerability scans through AWS Inpsector in ECR using these image tags (if option is enabled).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d6bcf5899c7945cb58b58346bf98d80366aa181448ff6906fb5571aeb5620d4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ImagePipelineProps(
            components=components,
            parent_image=parent_image,
            additional_policies=additional_policies,
            ami_id_ssm_account_id=ami_id_ssm_account_id,
            ami_id_ssm_path=ami_id_ssm_path,
            ami_id_ssm_region=ami_id_ssm_region,
            distribution_account_i_ds=distribution_account_i_ds,
            distribution_regions=distribution_regions,
            ebs_volume_configurations=ebs_volume_configurations,
            email=email,
            enable_cross_account_distribution=enable_cross_account_distribution,
            enable_vuln_scans=enable_vuln_scans,
            image_recipe_version=image_recipe_version,
            instance_types=instance_types,
            kms_key=kms_key,
            name=name,
            platform=platform,
            resource_tags=resource_tags,
            schedule=schedule,
            security_groups=security_groups,
            subnet_id=subnet_id,
            user_data_script=user_data_script,
            vuln_scans_repo_name=vuln_scans_repo_name,
            vuln_scans_repo_tags=vuln_scans_repo_tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="builderSnsTopic")
    def builder_sns_topic(self) -> _aws_cdk_aws_sns_ceddda9d.Topic:
        '''SNS Topic where the internal ImageBuilder will notify about new builds.'''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.Topic, jsii.get(self, "builderSnsTopic"))

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> _aws_cdk_aws_imagebuilder_ceddda9d.CfnImagePipeline:
        '''The internal image pipeline created by this construct.'''
        return typing.cast(_aws_cdk_aws_imagebuilder_ceddda9d.CfnImagePipeline, jsii.get(self, "pipeline"))

    @builtins.property
    @jsii.member(jsii_name="imageRecipeComponents")
    def image_recipe_components(
        self,
    ) -> typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.ComponentConfigurationProperty]:
        return typing.cast(typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.ComponentConfigurationProperty], jsii.get(self, "imageRecipeComponents"))

    @image_recipe_components.setter
    def image_recipe_components(
        self,
        value: typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.ComponentConfigurationProperty],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6030b5c4ec4934f0e7f5cd5e6d6b3950a65ad587993a25e55770d3d1d32b91e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageRecipeComponents", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="cdk-image-pipeline.ImagePipelineProps",
    jsii_struct_bases=[],
    name_mapping={
        "components": "components",
        "parent_image": "parentImage",
        "additional_policies": "additionalPolicies",
        "ami_id_ssm_account_id": "amiIdSsmAccountId",
        "ami_id_ssm_path": "amiIdSsmPath",
        "ami_id_ssm_region": "amiIdSsmRegion",
        "distribution_account_i_ds": "distributionAccountIDs",
        "distribution_regions": "distributionRegions",
        "ebs_volume_configurations": "ebsVolumeConfigurations",
        "email": "email",
        "enable_cross_account_distribution": "enableCrossAccountDistribution",
        "enable_vuln_scans": "enableVulnScans",
        "image_recipe_version": "imageRecipeVersion",
        "instance_types": "instanceTypes",
        "kms_key": "kmsKey",
        "name": "name",
        "platform": "platform",
        "resource_tags": "resourceTags",
        "schedule": "schedule",
        "security_groups": "securityGroups",
        "subnet_id": "subnetId",
        "user_data_script": "userDataScript",
        "vuln_scans_repo_name": "vulnScansRepoName",
        "vuln_scans_repo_tags": "vulnScansRepoTags",
    },
)
class ImagePipelineProps:
    def __init__(
        self,
        *,
        components: typing.Sequence[typing.Union[builtins.str, typing.Union[ComponentProps, typing.Dict[builtins.str, typing.Any]]]],
        parent_image: builtins.str,
        additional_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
        ami_id_ssm_account_id: typing.Optional[builtins.str] = None,
        ami_id_ssm_path: typing.Optional[builtins.str] = None,
        ami_id_ssm_region: typing.Optional[builtins.str] = None,
        distribution_account_i_ds: typing.Optional[typing.Sequence[builtins.str]] = None,
        distribution_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        ebs_volume_configurations: typing.Optional[typing.Sequence[typing.Union["VolumeProps", typing.Dict[builtins.str, typing.Any]]]] = None,
        email: typing.Optional[builtins.str] = None,
        enable_cross_account_distribution: typing.Optional[builtins.bool] = None,
        enable_vuln_scans: typing.Optional[builtins.bool] = None,
        image_recipe_version: typing.Optional[builtins.str] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        schedule: typing.Optional[typing.Union["ImagePipelineSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        user_data_script: typing.Optional[builtins.str] = None,
        vuln_scans_repo_name: typing.Optional[builtins.str] = None,
        vuln_scans_repo_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param components: List of component props.
        :param parent_image: The source (parent) image that the image recipe uses as its base environment. The value can be the parent image ARN or an Image Builder AMI ID
        :param additional_policies: Additional policies to add to the instance profile associated with the Instance Configurations.
        :param ami_id_ssm_account_id: Account ID for Parameter Store path above.
        :param ami_id_ssm_path: Parameter Store path to store latest AMI ID under.
        :param ami_id_ssm_region: Region for Parameter Store path above.
        :param distribution_account_i_ds: List of accounts to copy this AMI to, if the option to do so is enabled.
        :param distribution_regions: List of regions to copy this AMI to, if the option to do so is enabled.
        :param ebs_volume_configurations: Configuration for the AMI's EBS volumes.
        :param email: Email used to receive Image Builder Pipeline Notifications via SNS.
        :param enable_cross_account_distribution: Set to true if you want to copy this AMI to other accounts using a Distribution Configuration.
        :param enable_vuln_scans: Set to true if you want to enable continuous vulnerability scans through AWS Inpector.
        :param image_recipe_version: Image recipe version (Default: 0.0.1).
        :param instance_types: List of instance types used in the Instance Configuration (Default: [ 't3.medium', 'm5.large', 'm5.xlarge' ]).
        :param kms_key: KMS Key used to encrypt the SNS topic.
        :param name: Name of the Image Pipeline.
        :param platform: Platform type Linux or Windows (Default: Linux).
        :param resource_tags: The tags attached to the resource created by Image Builder.
        :param schedule: Schedule configuration for the image pipeline.
        :param security_groups: List of security group IDs for the Infrastructure Configuration.
        :param subnet_id: Subnet ID for the Infrastructure Configuration.
        :param user_data_script: UserData script that will override default one (if specified). Default: - none
        :param vuln_scans_repo_name: Store vulnerability scans through AWS Inpsector in ECR using this repo name (if option is enabled).
        :param vuln_scans_repo_tags: Store vulnerability scans through AWS Inpsector in ECR using these image tags (if option is enabled).
        '''
        if isinstance(schedule, dict):
            schedule = ImagePipelineSchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d44c3e3f51e9feef4d0a0beb4a7aeeeb7d2d753e8a9bb21f5c19a8edbdff4c88)
            check_type(argname="argument components", value=components, expected_type=type_hints["components"])
            check_type(argname="argument parent_image", value=parent_image, expected_type=type_hints["parent_image"])
            check_type(argname="argument additional_policies", value=additional_policies, expected_type=type_hints["additional_policies"])
            check_type(argname="argument ami_id_ssm_account_id", value=ami_id_ssm_account_id, expected_type=type_hints["ami_id_ssm_account_id"])
            check_type(argname="argument ami_id_ssm_path", value=ami_id_ssm_path, expected_type=type_hints["ami_id_ssm_path"])
            check_type(argname="argument ami_id_ssm_region", value=ami_id_ssm_region, expected_type=type_hints["ami_id_ssm_region"])
            check_type(argname="argument distribution_account_i_ds", value=distribution_account_i_ds, expected_type=type_hints["distribution_account_i_ds"])
            check_type(argname="argument distribution_regions", value=distribution_regions, expected_type=type_hints["distribution_regions"])
            check_type(argname="argument ebs_volume_configurations", value=ebs_volume_configurations, expected_type=type_hints["ebs_volume_configurations"])
            check_type(argname="argument email", value=email, expected_type=type_hints["email"])
            check_type(argname="argument enable_cross_account_distribution", value=enable_cross_account_distribution, expected_type=type_hints["enable_cross_account_distribution"])
            check_type(argname="argument enable_vuln_scans", value=enable_vuln_scans, expected_type=type_hints["enable_vuln_scans"])
            check_type(argname="argument image_recipe_version", value=image_recipe_version, expected_type=type_hints["image_recipe_version"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument platform", value=platform, expected_type=type_hints["platform"])
            check_type(argname="argument resource_tags", value=resource_tags, expected_type=type_hints["resource_tags"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_id", value=subnet_id, expected_type=type_hints["subnet_id"])
            check_type(argname="argument user_data_script", value=user_data_script, expected_type=type_hints["user_data_script"])
            check_type(argname="argument vuln_scans_repo_name", value=vuln_scans_repo_name, expected_type=type_hints["vuln_scans_repo_name"])
            check_type(argname="argument vuln_scans_repo_tags", value=vuln_scans_repo_tags, expected_type=type_hints["vuln_scans_repo_tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "components": components,
            "parent_image": parent_image,
        }
        if additional_policies is not None:
            self._values["additional_policies"] = additional_policies
        if ami_id_ssm_account_id is not None:
            self._values["ami_id_ssm_account_id"] = ami_id_ssm_account_id
        if ami_id_ssm_path is not None:
            self._values["ami_id_ssm_path"] = ami_id_ssm_path
        if ami_id_ssm_region is not None:
            self._values["ami_id_ssm_region"] = ami_id_ssm_region
        if distribution_account_i_ds is not None:
            self._values["distribution_account_i_ds"] = distribution_account_i_ds
        if distribution_regions is not None:
            self._values["distribution_regions"] = distribution_regions
        if ebs_volume_configurations is not None:
            self._values["ebs_volume_configurations"] = ebs_volume_configurations
        if email is not None:
            self._values["email"] = email
        if enable_cross_account_distribution is not None:
            self._values["enable_cross_account_distribution"] = enable_cross_account_distribution
        if enable_vuln_scans is not None:
            self._values["enable_vuln_scans"] = enable_vuln_scans
        if image_recipe_version is not None:
            self._values["image_recipe_version"] = image_recipe_version
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if name is not None:
            self._values["name"] = name
        if platform is not None:
            self._values["platform"] = platform
        if resource_tags is not None:
            self._values["resource_tags"] = resource_tags
        if schedule is not None:
            self._values["schedule"] = schedule
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if user_data_script is not None:
            self._values["user_data_script"] = user_data_script
        if vuln_scans_repo_name is not None:
            self._values["vuln_scans_repo_name"] = vuln_scans_repo_name
        if vuln_scans_repo_tags is not None:
            self._values["vuln_scans_repo_tags"] = vuln_scans_repo_tags

    @builtins.property
    def components(self) -> typing.List[typing.Union[builtins.str, ComponentProps]]:
        '''List of component props.'''
        result = self._values.get("components")
        assert result is not None, "Required property 'components' is missing"
        return typing.cast(typing.List[typing.Union[builtins.str, ComponentProps]], result)

    @builtins.property
    def parent_image(self) -> builtins.str:
        '''The source (parent) image that the image recipe uses as its base environment.

        The value can be the parent image ARN or an Image Builder AMI ID
        '''
        result = self._values.get("parent_image")
        assert result is not None, "Required property 'parent_image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]]:
        '''Additional policies to add to the instance profile associated with the Instance Configurations.'''
        result = self._values.get("additional_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]], result)

    @builtins.property
    def ami_id_ssm_account_id(self) -> typing.Optional[builtins.str]:
        '''Account ID for Parameter Store path above.'''
        result = self._values.get("ami_id_ssm_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ami_id_ssm_path(self) -> typing.Optional[builtins.str]:
        '''Parameter Store path to store latest AMI ID under.'''
        result = self._values.get("ami_id_ssm_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ami_id_ssm_region(self) -> typing.Optional[builtins.str]:
        '''Region for Parameter Store path above.'''
        result = self._values.get("ami_id_ssm_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def distribution_account_i_ds(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of accounts to copy this AMI to, if the option to do so is enabled.'''
        result = self._values.get("distribution_account_i_ds")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def distribution_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of regions to copy this AMI to, if the option to do so is enabled.'''
        result = self._values.get("distribution_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ebs_volume_configurations(self) -> typing.Optional[typing.List["VolumeProps"]]:
        '''Configuration for the AMI's EBS volumes.'''
        result = self._values.get("ebs_volume_configurations")
        return typing.cast(typing.Optional[typing.List["VolumeProps"]], result)

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''Email used to receive Image Builder Pipeline Notifications via SNS.'''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_cross_account_distribution(self) -> typing.Optional[builtins.bool]:
        '''Set to true if you want to copy this AMI to other accounts using a Distribution Configuration.'''
        result = self._values.get("enable_cross_account_distribution")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_vuln_scans(self) -> typing.Optional[builtins.bool]:
        '''Set to true if you want to enable continuous vulnerability scans through AWS Inpector.'''
        result = self._values.get("enable_vuln_scans")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def image_recipe_version(self) -> typing.Optional[builtins.str]:
        '''Image recipe version (Default: 0.0.1).'''
        result = self._values.get("image_recipe_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of instance types used in the Instance Configuration (Default: [ 't3.medium', 'm5.large', 'm5.xlarge' ]).'''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''KMS Key used to encrypt the SNS topic.'''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Image Pipeline.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Platform type Linux or Windows (Default: Linux).'''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tags attached to the resource created by Image Builder.'''
        result = self._values.get("resource_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def schedule(self) -> typing.Optional["ImagePipelineSchedule"]:
        '''Schedule configuration for the image pipeline.'''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["ImagePipelineSchedule"], result)

    @builtins.property
    def security_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of security group IDs for the Infrastructure Configuration.'''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''Subnet ID for the Infrastructure Configuration.'''
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_data_script(self) -> typing.Optional[builtins.str]:
        '''UserData script that will override default one (if specified).

        :default: - none
        '''
        result = self._values.get("user_data_script")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vuln_scans_repo_name(self) -> typing.Optional[builtins.str]:
        '''Store vulnerability scans through AWS Inpsector in ECR using this repo name (if option is enabled).'''
        result = self._values.get("vuln_scans_repo_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vuln_scans_repo_tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Store vulnerability scans through AWS Inpsector in ECR using these image tags (if option is enabled).'''
        result = self._values.get("vuln_scans_repo_tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagePipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-image-pipeline.ImagePipelineSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "schedule_expression": "scheduleExpression",
        "pipeline_execution_start_condition": "pipelineExecutionStartCondition",
    },
)
class ImagePipelineSchedule:
    def __init__(
        self,
        *,
        schedule_expression: builtins.str,
        pipeline_execution_start_condition: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param schedule_expression: The cron expression for the schedule.
        :param pipeline_execution_start_condition: Optional pipeline execution start condition.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82e4962501e8791035eb0f2b50b1e52ae251e99f1bf58de1cf3c5bb38469f776)
            check_type(argname="argument schedule_expression", value=schedule_expression, expected_type=type_hints["schedule_expression"])
            check_type(argname="argument pipeline_execution_start_condition", value=pipeline_execution_start_condition, expected_type=type_hints["pipeline_execution_start_condition"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "schedule_expression": schedule_expression,
        }
        if pipeline_execution_start_condition is not None:
            self._values["pipeline_execution_start_condition"] = pipeline_execution_start_condition

    @builtins.property
    def schedule_expression(self) -> builtins.str:
        '''The cron expression for the schedule.'''
        result = self._values.get("schedule_expression")
        assert result is not None, "Required property 'schedule_expression' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipeline_execution_start_condition(self) -> typing.Optional[builtins.str]:
        '''Optional pipeline execution start condition.'''
        result = self._values.get("pipeline_execution_start_condition")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImagePipelineSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-image-pipeline.VolumeProps",
    jsii_struct_bases=[],
    name_mapping={"device_name": "deviceName", "ebs": "ebs"},
)
class VolumeProps:
    def __init__(
        self,
        *,
        device_name: builtins.str,
        ebs: typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param device_name: Name of the volume.
        :param ebs: EBS Block Store Parameters.
        '''
        if isinstance(ebs, dict):
            ebs = _aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty(**ebs)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d99ccdd9ffe7d3f104ab96ddc5a36e3445f6dcf7821cf5b170233ea62545a232)
            check_type(argname="argument device_name", value=device_name, expected_type=type_hints["device_name"])
            check_type(argname="argument ebs", value=ebs, expected_type=type_hints["ebs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "device_name": device_name,
            "ebs": ebs,
        }

    @builtins.property
    def device_name(self) -> builtins.str:
        '''Name of the volume.'''
        result = self._values.get("device_name")
        assert result is not None, "Required property 'device_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ebs(
        self,
    ) -> _aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty:
        '''EBS Block Store Parameters.'''
        result = self._values.get("ebs")
        assert result is not None, "Required property 'ebs' is missing"
        return typing.cast(_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VolumeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ComponentProps",
    "ImagePipeline",
    "ImagePipelineProps",
    "ImagePipelineSchedule",
    "VolumeProps",
]

publication.publish()

def _typecheckingstub__a8f4421f08d0eeed51801e1088743e803f62672d6b4b15c72fc46f8f8a1ceffa(
    *,
    document: builtins.str,
    name: builtins.str,
    version: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d6bcf5899c7945cb58b58346bf98d80366aa181448ff6906fb5571aeb5620d4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    components: typing.Sequence[typing.Union[builtins.str, typing.Union[ComponentProps, typing.Dict[builtins.str, typing.Any]]]],
    parent_image: builtins.str,
    additional_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
    ami_id_ssm_account_id: typing.Optional[builtins.str] = None,
    ami_id_ssm_path: typing.Optional[builtins.str] = None,
    ami_id_ssm_region: typing.Optional[builtins.str] = None,
    distribution_account_i_ds: typing.Optional[typing.Sequence[builtins.str]] = None,
    distribution_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ebs_volume_configurations: typing.Optional[typing.Sequence[typing.Union[VolumeProps, typing.Dict[builtins.str, typing.Any]]]] = None,
    email: typing.Optional[builtins.str] = None,
    enable_cross_account_distribution: typing.Optional[builtins.bool] = None,
    enable_vuln_scans: typing.Optional[builtins.bool] = None,
    image_recipe_version: typing.Optional[builtins.str] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    platform: typing.Optional[builtins.str] = None,
    resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    schedule: typing.Optional[typing.Union[ImagePipelineSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_id: typing.Optional[builtins.str] = None,
    user_data_script: typing.Optional[builtins.str] = None,
    vuln_scans_repo_name: typing.Optional[builtins.str] = None,
    vuln_scans_repo_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6030b5c4ec4934f0e7f5cd5e6d6b3950a65ad587993a25e55770d3d1d32b91e(
    value: typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.ComponentConfigurationProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d44c3e3f51e9feef4d0a0beb4a7aeeeb7d2d753e8a9bb21f5c19a8edbdff4c88(
    *,
    components: typing.Sequence[typing.Union[builtins.str, typing.Union[ComponentProps, typing.Dict[builtins.str, typing.Any]]]],
    parent_image: builtins.str,
    additional_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.ManagedPolicy]] = None,
    ami_id_ssm_account_id: typing.Optional[builtins.str] = None,
    ami_id_ssm_path: typing.Optional[builtins.str] = None,
    ami_id_ssm_region: typing.Optional[builtins.str] = None,
    distribution_account_i_ds: typing.Optional[typing.Sequence[builtins.str]] = None,
    distribution_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ebs_volume_configurations: typing.Optional[typing.Sequence[typing.Union[VolumeProps, typing.Dict[builtins.str, typing.Any]]]] = None,
    email: typing.Optional[builtins.str] = None,
    enable_cross_account_distribution: typing.Optional[builtins.bool] = None,
    enable_vuln_scans: typing.Optional[builtins.bool] = None,
    image_recipe_version: typing.Optional[builtins.str] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    platform: typing.Optional[builtins.str] = None,
    resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    schedule: typing.Optional[typing.Union[ImagePipelineSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    security_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_id: typing.Optional[builtins.str] = None,
    user_data_script: typing.Optional[builtins.str] = None,
    vuln_scans_repo_name: typing.Optional[builtins.str] = None,
    vuln_scans_repo_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82e4962501e8791035eb0f2b50b1e52ae251e99f1bf58de1cf3c5bb38469f776(
    *,
    schedule_expression: builtins.str,
    pipeline_execution_start_condition: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d99ccdd9ffe7d3f104ab96ddc5a36e3445f6dcf7821cf5b170233ea62545a232(
    *,
    device_name: builtins.str,
    ebs: typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.EbsInstanceBlockDeviceSpecificationProperty, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass
