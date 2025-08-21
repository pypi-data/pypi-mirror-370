r'''
Constructs for the AWS EC2 service

# EC2 Instance Connect Endpoint CDK Construct

## Overview

The `InstanceConnectEndpoint` construct facilitates the creation and management of [EC2 Instance Connect endpoints](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-with-ec2-instance-connect-endpoint.html)
within AWS CDK applications.

## Usage

Import the necessary classes from AWS CDK and this construct and create a VPC for the endpoint:

```python
import { App, Stack } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { InstanceConnectEndpoint } from '@open-constructs/aws-cdk/aws-ec2';

const app = new App();
const stack = new Stack(app, 'InstanceConnectEndpointStack');
const vpc = new ec2.Vpc(stack, 'MyVpc');
```

### Basic Example

Here's how you can create an EC2 Instance Connect endpoint and allow connections to an EC2 instance:

```python
const instance = new ec2.Instance(this, 'Instance', {
  vpc,
  instanceType: ec2.InstanceType.of(
    ec2.InstanceClass.C5,
    ec2.InstanceSize.LARGE,
  ),
  machineImage: new ec2.AmazonLinuxImage({
    generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023,
  }),
});

const endpoint = new InstanceConnectEndpoint(stack, 'MyEndpoint', {
  vpc,
});

// Allow SSH connections to the instance
// You can also use the port 3389 for RDP connections
endpoint.connections.allowTo(instance, ec2.Port.tcp(22));
```

### Advanced Example

Creating an endpoint with a custom settings:

```python
declare const endpointSecurityGroup: ec2.ISecurityGroup;

const endpoint = new InstanceConnectEndpoint(stack, 'MyCustomEndpoint', {
  vpc,
  securityGroups: [endpointSecurityGroup], // Specify user-defined security groups
  preserveClientIp: true, // Whether your client's IP address is preserved as the source
  clientToken: 'my-client-token', // Specify client token to ensure the idempotency of the request.
});
```

Import an existing endpoint:

```python
declare const existingEndpoint: ec2.IInstanceConnectEndpoint;
declare const securityGroups: ec2.ISecurityGroup[];

const existingEndpoint = InstanceConnectEndpoint.fromInstanceConnectEndpointAttributes(
  stack,
  'MyExistingEndpoint',
  {
    instanceConnectEndpointId: existingEndpoint.instanceConnectEndpointId,
    securityGroups,
  },
);
```
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

from .._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_ec2.IInstanceConnectEndpoint")
class IInstanceConnectEndpoint(
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    _aws_cdk_ceddda9d.IResource,
    typing_extensions.Protocol,
):
    '''An EC2 Instance Connect Endpoint.'''

    @builtins.property
    @jsii.member(jsii_name="instanceConnectEndpointId")
    def instance_connect_endpoint_id(self) -> builtins.str:
        '''The ID of the EC2 Instance Connect Endpoint.

        :attribute: true
        '''
        ...


class _IInstanceConnectEndpointProxy(
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''An EC2 Instance Connect Endpoint.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_ec2.IInstanceConnectEndpoint"

    @builtins.property
    @jsii.member(jsii_name="instanceConnectEndpointId")
    def instance_connect_endpoint_id(self) -> builtins.str:
        '''The ID of the EC2 Instance Connect Endpoint.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceConnectEndpointId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInstanceConnectEndpoint).__jsii_proxy_class__ = lambda : _IInstanceConnectEndpointProxy


@jsii.implements(IInstanceConnectEndpoint)
class InstanceConnectEndpoint(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_ec2.InstanceConnectEndpoint",
):
    '''Represents an EC2 Instance Connect Endpoint construct in AWS CDK.

    Example::

        declare const securityGroups: aws_ec2.ISecurityGroup[];
        declare const vpc: aws_ec2.IVpc;
        
        const instanceConnectEndpoint = new InstanceConnectEndpoint(
          stack,
          'InstanceConnectEndpoint',
          {
            clientToken: 'my-client-token',
            preserveClientIp: true,
            securityGroups,
            vpc,
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        client_token: typing.Optional[builtins.str] = None,
        preserve_client_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC in which the EC2 Instance Connect Endpoint is created.
        :param client_token: Unique, case-sensitive identifier that you provide to ensure the idempotency of the request.
        :param preserve_client_ip: Indicates whether your client's IP address is preserved as the source. Default: true
        :param security_groups: The security groups to associate with the EC2 Instance Connect Endpoint. Default: - a new security group is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c085e93fb4ae37c193f39d03f556b10e463bac0491bbcbff5f00a9d6531b249e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InstanceConnectEndpointProps(
            vpc=vpc,
            client_token=client_token,
            preserve_client_ip=preserve_client_ip,
            security_groups=security_groups,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromInstanceConnectEndpointAttributes")
    @builtins.classmethod
    def from_instance_connect_endpoint_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_connect_endpoint_id: builtins.str,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> IInstanceConnectEndpoint:
        '''Import an existing endpoint to the stack from its attributes.

        :param scope: -
        :param id: -
        :param instance_connect_endpoint_id: The ID of the EC2 Instance Connect Endpoint.
        :param security_groups: The security groups associated with the EC2 Instance Connect Endpoint.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__282741fcc72d88c4d64fad9c94629129cfdafc2dbe87dca3b18c7547f938ac14)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = InstanceConnectEndpointAttributes(
            instance_connect_endpoint_id=instance_connect_endpoint_id,
            security_groups=security_groups,
        )

        return typing.cast(IInstanceConnectEndpoint, jsii.sinvoke(cls, "fromInstanceConnectEndpointAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="createInstanceConnectEndpoint")
    def _create_instance_connect_endpoint(
        self,
    ) -> _aws_cdk_aws_ec2_ceddda9d.CfnInstanceConnectEndpoint:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.CfnInstanceConnectEndpoint, jsii.invoke(self, "createInstanceConnectEndpoint", []))

    @jsii.member(jsii_name="createSecurityGroup")
    def _create_security_group(self) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.invoke(self, "createSecurityGroup", []))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The connection object associated with the EC2 Instance Connect Endpoint.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="instanceConnectEndpointId")
    def instance_connect_endpoint_id(self) -> builtins.str:
        '''The ID of the EC2 Instance Connect Endpoint.'''
        return typing.cast(builtins.str, jsii.get(self, "instanceConnectEndpointId"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_ec2.InstanceConnectEndpointAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "instance_connect_endpoint_id": "instanceConnectEndpointId",
        "security_groups": "securityGroups",
    },
)
class InstanceConnectEndpointAttributes:
    def __init__(
        self,
        *,
        instance_connect_endpoint_id: builtins.str,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    ) -> None:
        '''Attributes for importing an EC2 Instance Connect Endpoint.

        :param instance_connect_endpoint_id: The ID of the EC2 Instance Connect Endpoint.
        :param security_groups: The security groups associated with the EC2 Instance Connect Endpoint.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2d271b449b4175f0791dec29a1003e8a427277a621f0b471d7818817e158939)
            check_type(argname="argument instance_connect_endpoint_id", value=instance_connect_endpoint_id, expected_type=type_hints["instance_connect_endpoint_id"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_connect_endpoint_id": instance_connect_endpoint_id,
            "security_groups": security_groups,
        }

    @builtins.property
    def instance_connect_endpoint_id(self) -> builtins.str:
        '''The ID of the EC2 Instance Connect Endpoint.'''
        result = self._values.get("instance_connect_endpoint_id")
        assert result is not None, "Required property 'instance_connect_endpoint_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security groups associated with the EC2 Instance Connect Endpoint.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceConnectEndpointAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_ec2.InstanceConnectEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "client_token": "clientToken",
        "preserve_client_ip": "preserveClientIp",
        "security_groups": "securityGroups",
    },
)
class InstanceConnectEndpointProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        client_token: typing.Optional[builtins.str] = None,
        preserve_client_ip: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> None:
        '''Properties for defining an EC2 Instance Connect Endpoint.

        :param vpc: The VPC in which the EC2 Instance Connect Endpoint is created.
        :param client_token: Unique, case-sensitive identifier that you provide to ensure the idempotency of the request.
        :param preserve_client_ip: Indicates whether your client's IP address is preserved as the source. Default: true
        :param security_groups: The security groups to associate with the EC2 Instance Connect Endpoint. Default: - a new security group is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0557891e521051ecb24792dd1f44fbdfa0743315e751dc586b1c39aded8a238d)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument client_token", value=client_token, expected_type=type_hints["client_token"])
            check_type(argname="argument preserve_client_ip", value=preserve_client_ip, expected_type=type_hints["preserve_client_ip"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if client_token is not None:
            self._values["client_token"] = client_token
        if preserve_client_ip is not None:
            self._values["preserve_client_ip"] = preserve_client_ip
        if security_groups is not None:
            self._values["security_groups"] = security_groups

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC in which the EC2 Instance Connect Endpoint is created.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def client_token(self) -> typing.Optional[builtins.str]:
        '''Unique, case-sensitive identifier that you provide to ensure the idempotency of the request.

        :see: https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-instanceconnectendpoint.html#cfn-ec2-instanceconnectendpoint-clienttoken
        '''
        result = self._values.get("client_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def preserve_client_ip(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether your client's IP address is preserved as the source.

        :default: true

        :see: https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-instanceconnectendpoint.html#cfn-ec2-instanceconnectendpoint-preserveclientip
        '''
        result = self._values.get("preserve_client_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the EC2 Instance Connect Endpoint.

        :default: - a new security group is created
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InstanceConnectEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IInstanceConnectEndpoint",
    "InstanceConnectEndpoint",
    "InstanceConnectEndpointAttributes",
    "InstanceConnectEndpointProps",
]

publication.publish()

def _typecheckingstub__c085e93fb4ae37c193f39d03f556b10e463bac0491bbcbff5f00a9d6531b249e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    client_token: typing.Optional[builtins.str] = None,
    preserve_client_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__282741fcc72d88c4d64fad9c94629129cfdafc2dbe87dca3b18c7547f938ac14(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_connect_endpoint_id: builtins.str,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d271b449b4175f0791dec29a1003e8a427277a621f0b471d7818817e158939(
    *,
    instance_connect_endpoint_id: builtins.str,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0557891e521051ecb24792dd1f44fbdfa0743315e751dc586b1c39aded8a238d(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    client_token: typing.Optional[builtins.str] = None,
    preserve_client_ip: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass
