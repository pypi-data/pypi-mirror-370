r'''
Constructs for the Amazon Redshift Serverless

# Redshift Serverless CDK Construct

## Overview

The `Namespace` construct and the `Workgroup` construct facilitate the creation and management of [Redshift Serverless Workgroups and namespaces](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-workgroup-namespace.html) within AWS CDK applications.

## Usage

Import the necessary classes from AWS CDK and this construct and create a VPC for the workgroup:

```python
import { App, Stack } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Namespace, Workgroup } from '@open-constructs/aws-cdk/aws-redshiftserverless';

const app = new App();
const stack = new Stack(app, 'RedshiftServerlessStack',{
  account: '012345678901'
  region: 'us-east-1',
});
const vpc = new ec2.Vpc(stack, 'MyVpc');
```

**Note** If you want to use `Vpc` Construct to create a VPC for `Workgroup`, you must specify `account` and `region` in `Stack`.
`Workgroup` needs at least three subnets, and they must span across three Availability Zones.

The environment-agnostic stacks will be created with access to only 2 AZs (Ref: [`maxAzs` property docs](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Vpc.html#maxazs))

For more information about Redshift Serverless's limitations, see [Considerations when using Amazon Redshift Serverless](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-usage-considerations.html).

### Basic Example

Here's how you can create a namespace and a workgroup:

```python
import { SecretValue } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
declare const defaultIamRole: iam.IRole;
declare const anotherIamRole: iam.IRole;

const namespace = new redshiftserverless.Namespace(stack, 'Namespace', {
  namespaceName: 'my-namespace',
  defaultIamRole: myIamRole, // Specify a default IAM role
  iamRoles: [defaultIamRole, anotherIamRole], // Assign IAM roles list which must include default IAM Role
});

const workgroup = new redshiftserverless.Workgroup(stack, 'MyWorkgroup', {
  workgroupName: 'my-workgroup',
  namespace,
  vpc,
});
```

### Advanced Example

Creating a namespace and a workgroup with custom settings:

```python
declare const workgroupSecurityGroup: ec2.ISecurityGroup;

const namespace = new redshiftserverless.Namespace(stack, 'MyCustomNamespace', {
  namespaceName: 'my-custom-namespace',
  dbName: 'mydb', // Specify user-defined database name
  adminUsername: 'admin', // Specify user-defined admin username
  adminUserPassword: SecretValue.unsafePlainText('My-password-123!'), // Specify user-defined admin password
  logExports: [redshiftserverless.LogExport.USER_LOG], // Log export settings
});

const workgroup = new redshiftserverless.Workgroup(stack, 'MyCustomWorkgroup', {
  workgroupName: 'my-custom-workgroup',
  namespace,
  vpc,
  baseCapacity: 32, // Specify Base Capacity uses to serve queries
  securityGroups: [workgroupSecurityGroup], // Specify user-defined security groups
});
```

### Import an existing endpoint:

You can import existing namespaces and workgroups:

```python
declare const securityGroup: ec2.ISecurityGroup;

const importedNamespace = redshiftserverless.Namespace.fromNamespaceAttributes(stack, 'ImportedNamespace', {
  namespaceId: 'my-namespace-id',
  namespaceName: 'my-namespace-name',
});

const importedWorkgroup = redshiftserverless.Workgroup.fromWorkgroupAttributes(stack, 'ImportedWorkgroup', {
  workgroupName: 'my-workgroup',
  workgroupId: 'my-workgroup-id',
  endpointAddress: 'my-workgroup.endpoint.com',
  port: 5439,
  securityGroups: [securityGroup],
});
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
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_redshiftserverless as _aws_cdk_aws_redshiftserverless_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.INamespace")
class INamespace(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''A Redshift Serverless Namespace.'''

    @builtins.property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> builtins.str:
        '''The namespace ARN.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        '''The namespace id.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        '''The namespace name.

        :attribute: true
        '''
        ...


class _INamespaceProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''A Redshift Serverless Namespace.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_redshiftserverless.INamespace"

    @builtins.property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> builtins.str:
        '''The namespace ARN.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespaceArn"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        '''The namespace id.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        '''The namespace name.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespaceName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INamespace).__jsii_proxy_class__ = lambda : _INamespaceProxy


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.IWorkgroup")
class IWorkgroup(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''A Redshift Serverless Workgroup.'''

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        '''The workgroup endpoint address.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        '''The workgroup port.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="workgroupArn")
    def workgroup_arn(self) -> builtins.str:
        '''The workgroup Arn.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="workgroupId")
    def workgroup_id(self) -> builtins.str:
        '''The workgroup id.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="workgroupName")
    def workgroup_name(self) -> builtins.str:
        '''The workgroup name.

        :attribute: true
        '''
        ...


class _IWorkgroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''A Redshift Serverless Workgroup.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_redshiftserverless.IWorkgroup"

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        '''The workgroup endpoint address.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointAddress"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        '''The workgroup port.

        :attribute: true
        '''
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="workgroupArn")
    def workgroup_arn(self) -> builtins.str:
        '''The workgroup Arn.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "workgroupArn"))

    @builtins.property
    @jsii.member(jsii_name="workgroupId")
    def workgroup_id(self) -> builtins.str:
        '''The workgroup id.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "workgroupId"))

    @builtins.property
    @jsii.member(jsii_name="workgroupName")
    def workgroup_name(self) -> builtins.str:
        '''The workgroup name.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "workgroupName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWorkgroup).__jsii_proxy_class__ = lambda : _IWorkgroupProxy


@jsii.enum(jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.LogExport")
class LogExport(enum.Enum):
    '''The types of logs the namespace can export.'''

    USER_LOG = "USER_LOG"
    '''User log.'''
    CONNECTION_LOG = "CONNECTION_LOG"
    '''Connection log.'''
    USER_ACTIVITY_LOG = "USER_ACTIVITY_LOG"
    '''User activity log.'''


@jsii.implements(INamespace)
class Namespace(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.Namespace",
):
    '''Represents a Redshift Serverless Namespace construct in AWS CDK.

    Example::

        const nameSpace = new Namespace(
          stack,
          'Namespace',
          {
            namespaceName: 'my-namespace',
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        admin_username: typing.Optional[builtins.str] = None,
        admin_user_password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        db_name: typing.Optional[builtins.str] = None,
        default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        log_exports: typing.Optional[typing.Sequence[LogExport]] = None,
        namespace_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param admin_username: The username of the administrator for the primary database created in the namespace. You must specify both ``adminUsername`` and ``adminUserPassword``, or neither. Default: - no admin user
        :param admin_user_password: The password of the administrator for the primary database created in the namespace. You must specify both ``adminUsername`` and ``adminUserPassword``, or neither. Default: - no admin user
        :param db_name: The name of the primary database created in the namespace. Default: - 'dev'
        :param default_iam_role: The IAM role to set as a default in the namespace. ``defaultIamRole`` must be included in ``iamRoles``. Default: - no default IAM role
        :param final_snapshot_name: The name of the snapshot to be created before the namespace is deleted. If not specified, the final snapshot will not be taken. Default: - no final snapshot
        :param final_snapshot_retention_period: How long days to retain the final snapshot. You must set ``finalSnapshotName`` when you specify ``finalSnapshotRetentionPeriod``. Default: - Retained indefinitely if ``finalSnapshotName`` is specified, otherwise no final snapshot
        :param iam_roles: A list of IAM roles to associate with the namespace. Default: - no IAM role associated
        :param kms_key: A Customer Managed Key used to encrypt your data. Default: - use AWS managed key
        :param log_exports: The types of logs the namespace can export. Default: - no logs export
        :param namespace_name: The namespace name. Default: - auto generate
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__921d62f637992096bd1f7ee9eb0148c1e142a6006a4163815b2a16964672d7c5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NamespaceProps(
            admin_username=admin_username,
            admin_user_password=admin_user_password,
            db_name=db_name,
            default_iam_role=default_iam_role,
            final_snapshot_name=final_snapshot_name,
            final_snapshot_retention_period=final_snapshot_retention_period,
            iam_roles=iam_roles,
            kms_key=kms_key,
            log_exports=log_exports,
            namespace_name=namespace_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromNamespaceAttributes")
    @builtins.classmethod
    def from_namespace_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        namespace_id: builtins.str,
        namespace_name: builtins.str,
    ) -> INamespace:
        '''Imports an existing Namespace from attributes.

        :param scope: -
        :param id: -
        :param namespace_id: The namespace id.
        :param namespace_name: The namespace name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc9e16e26692f52767387364ffb2c67d80c7d2f62a9c982691f7b1748a67e8cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = NamespaceAttributes(
            namespace_id=namespace_id, namespace_name=namespace_name
        )

        return typing.cast(INamespace, jsii.sinvoke(cls, "fromNamespaceAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addIamRole")
    def add_iam_role(self, role: _aws_cdk_aws_iam_ceddda9d.IRole) -> None:
        '''Adds a role to the namespace.

        :param role: the role to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a66424df90aa8cdae9dadf104e864a8518eb7dd46de6abd70bb2ff17a87f77f)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast(None, jsii.invoke(self, "addIamRole", [role]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        namespace_name: builtins.str,
        admin_password_secret_kms_key_id: typing.Optional[builtins.str] = None,
        admin_username: typing.Optional[builtins.str] = None,
        admin_user_password: typing.Optional[builtins.str] = None,
        db_name: typing.Optional[builtins.str] = None,
        default_iam_role_arn: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        log_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
        manage_admin_password: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        namespace_resource_policy: typing.Any = None,
        redshift_idc_application_arn: typing.Optional[builtins.str] = None,
        snapshot_copy_configurations: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnNamespace.SnapshotCopyConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_redshiftserverless_ceddda9d.CfnNamespace:
        '''
        :param scope: -
        :param id: -
        :param namespace_name: The name of the namespace. Must be between 3-64 alphanumeric characters in lowercase, and it cannot be a reserved word. A list of reserved words can be found in `Reserved Words <https://docs.aws.amazon.com//redshift/latest/dg/r_pg_keywords.html>`_ in the Amazon Redshift Database Developer Guide.
        :param admin_password_secret_kms_key_id: The ID of the AWS Key Management Service (KMS) key used to encrypt and store the namespace's admin credentials secret. You can only use this parameter if ``ManageAdminPassword`` is ``true`` .
        :param admin_username: The username of the administrator for the primary database created in the namespace.
        :param admin_user_password: The password of the administrator for the primary database created in the namespace.
        :param db_name: The name of the primary database created in the namespace.
        :param default_iam_role_arn: The Amazon Resource Name (ARN) of the IAM role to set as a default in the namespace.
        :param final_snapshot_name: The name of the snapshot to be created before the namespace is deleted.
        :param final_snapshot_retention_period: How long to retain the final snapshot.
        :param iam_roles: A list of IAM roles to associate with the namespace.
        :param kms_key_id: The ID of the AWS Key Management Service key used to encrypt your data.
        :param log_exports: The types of logs the namespace can export. Available export types are ``userlog`` , ``connectionlog`` , and ``useractivitylog`` .
        :param manage_admin_password: If true, Amazon Redshift uses AWS Secrets Manager to manage the namespace's admin credentials. You can't use ``AdminUserPassword`` if ``ManageAdminPassword`` is true. If ``ManageAdminPassword`` is ``false`` or not set, Amazon Redshift uses ``AdminUserPassword`` for the admin user account's password.
        :param namespace_resource_policy: The resource policy that will be attached to the namespace.
        :param redshift_idc_application_arn: The ARN for the Redshift application that integrates with IAM Identity Center.
        :param snapshot_copy_configurations: The snapshot copy configurations for the namespace.
        :param tags: The map of the key-value pairs used to tag the namespace.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a181e9c3f13276a32f87ef4d665f1b55295efc4a152ae8a6d94112c92bb014b3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_redshiftserverless_ceddda9d.CfnNamespaceProps(
            namespace_name=namespace_name,
            admin_password_secret_kms_key_id=admin_password_secret_kms_key_id,
            admin_username=admin_username,
            admin_user_password=admin_user_password,
            db_name=db_name,
            default_iam_role_arn=default_iam_role_arn,
            final_snapshot_name=final_snapshot_name,
            final_snapshot_retention_period=final_snapshot_retention_period,
            iam_roles=iam_roles,
            kms_key_id=kms_key_id,
            log_exports=log_exports,
            manage_admin_password=manage_admin_password,
            namespace_resource_policy=namespace_resource_policy,
            redshift_idc_application_arn=redshift_idc_application_arn,
            snapshot_copy_configurations=snapshot_copy_configurations,
            tags=tags,
        )

        return typing.cast(_aws_cdk_aws_redshiftserverless_ceddda9d.CfnNamespace, jsii.invoke(self, "createResource", [scope, id, props]))

    @builtins.property
    @jsii.member(jsii_name="namespaceArn")
    def namespace_arn(self) -> builtins.str:
        '''The namespace Arn.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceArn"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        '''The namespace id.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="namespaceName")
    def namespace_name(self) -> builtins.str:
        '''The namespace name.'''
        return typing.cast(builtins.str, jsii.get(self, "namespaceName"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.NamespaceAttributes",
    jsii_struct_bases=[],
    name_mapping={"namespace_id": "namespaceId", "namespace_name": "namespaceName"},
)
class NamespaceAttributes:
    def __init__(
        self,
        *,
        namespace_id: builtins.str,
        namespace_name: builtins.str,
    ) -> None:
        '''Attributes for importing a Redshift Serverless Namespace.

        :param namespace_id: The namespace id.
        :param namespace_name: The namespace name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__655018c149d040f3f3a2d2303e836e46c51e0c2658ee75ad47ffb48e2a2f154c)
            check_type(argname="argument namespace_id", value=namespace_id, expected_type=type_hints["namespace_id"])
            check_type(argname="argument namespace_name", value=namespace_name, expected_type=type_hints["namespace_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "namespace_id": namespace_id,
            "namespace_name": namespace_name,
        }

    @builtins.property
    def namespace_id(self) -> builtins.str:
        '''The namespace id.'''
        result = self._values.get("namespace_id")
        assert result is not None, "Required property 'namespace_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace_name(self) -> builtins.str:
        '''The namespace name.'''
        result = self._values.get("namespace_name")
        assert result is not None, "Required property 'namespace_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NamespaceAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.NamespaceProps",
    jsii_struct_bases=[],
    name_mapping={
        "admin_username": "adminUsername",
        "admin_user_password": "adminUserPassword",
        "db_name": "dbName",
        "default_iam_role": "defaultIamRole",
        "final_snapshot_name": "finalSnapshotName",
        "final_snapshot_retention_period": "finalSnapshotRetentionPeriod",
        "iam_roles": "iamRoles",
        "kms_key": "kmsKey",
        "log_exports": "logExports",
        "namespace_name": "namespaceName",
    },
)
class NamespaceProps:
    def __init__(
        self,
        *,
        admin_username: typing.Optional[builtins.str] = None,
        admin_user_password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        db_name: typing.Optional[builtins.str] = None,
        default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
        iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        log_exports: typing.Optional[typing.Sequence[LogExport]] = None,
        namespace_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Redshift Serverless Namespace.

        :param admin_username: The username of the administrator for the primary database created in the namespace. You must specify both ``adminUsername`` and ``adminUserPassword``, or neither. Default: - no admin user
        :param admin_user_password: The password of the administrator for the primary database created in the namespace. You must specify both ``adminUsername`` and ``adminUserPassword``, or neither. Default: - no admin user
        :param db_name: The name of the primary database created in the namespace. Default: - 'dev'
        :param default_iam_role: The IAM role to set as a default in the namespace. ``defaultIamRole`` must be included in ``iamRoles``. Default: - no default IAM role
        :param final_snapshot_name: The name of the snapshot to be created before the namespace is deleted. If not specified, the final snapshot will not be taken. Default: - no final snapshot
        :param final_snapshot_retention_period: How long days to retain the final snapshot. You must set ``finalSnapshotName`` when you specify ``finalSnapshotRetentionPeriod``. Default: - Retained indefinitely if ``finalSnapshotName`` is specified, otherwise no final snapshot
        :param iam_roles: A list of IAM roles to associate with the namespace. Default: - no IAM role associated
        :param kms_key: A Customer Managed Key used to encrypt your data. Default: - use AWS managed key
        :param log_exports: The types of logs the namespace can export. Default: - no logs export
        :param namespace_name: The namespace name. Default: - auto generate
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__289e731c521ae8d21fe51049e93fc1a322d3209ca080f5179e574b58db99f05a)
            check_type(argname="argument admin_username", value=admin_username, expected_type=type_hints["admin_username"])
            check_type(argname="argument admin_user_password", value=admin_user_password, expected_type=type_hints["admin_user_password"])
            check_type(argname="argument db_name", value=db_name, expected_type=type_hints["db_name"])
            check_type(argname="argument default_iam_role", value=default_iam_role, expected_type=type_hints["default_iam_role"])
            check_type(argname="argument final_snapshot_name", value=final_snapshot_name, expected_type=type_hints["final_snapshot_name"])
            check_type(argname="argument final_snapshot_retention_period", value=final_snapshot_retention_period, expected_type=type_hints["final_snapshot_retention_period"])
            check_type(argname="argument iam_roles", value=iam_roles, expected_type=type_hints["iam_roles"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument log_exports", value=log_exports, expected_type=type_hints["log_exports"])
            check_type(argname="argument namespace_name", value=namespace_name, expected_type=type_hints["namespace_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if admin_username is not None:
            self._values["admin_username"] = admin_username
        if admin_user_password is not None:
            self._values["admin_user_password"] = admin_user_password
        if db_name is not None:
            self._values["db_name"] = db_name
        if default_iam_role is not None:
            self._values["default_iam_role"] = default_iam_role
        if final_snapshot_name is not None:
            self._values["final_snapshot_name"] = final_snapshot_name
        if final_snapshot_retention_period is not None:
            self._values["final_snapshot_retention_period"] = final_snapshot_retention_period
        if iam_roles is not None:
            self._values["iam_roles"] = iam_roles
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if log_exports is not None:
            self._values["log_exports"] = log_exports
        if namespace_name is not None:
            self._values["namespace_name"] = namespace_name

    @builtins.property
    def admin_username(self) -> typing.Optional[builtins.str]:
        '''The username of the administrator for the primary database created in the namespace.

        You must specify both ``adminUsername`` and ``adminUserPassword``, or neither.

        :default: - no admin user
        '''
        result = self._values.get("admin_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def admin_user_password(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''The password of the administrator for the primary database created in the namespace.

        You must specify both ``adminUsername`` and ``adminUserPassword``, or neither.

        :default: - no admin user
        '''
        result = self._values.get("admin_user_password")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def db_name(self) -> typing.Optional[builtins.str]:
        '''The name of the primary database created in the namespace.

        :default: - 'dev'
        '''
        result = self._values.get("db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_iam_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The IAM role to set as a default in the namespace.

        ``defaultIamRole`` must be included in ``iamRoles``.

        :default: - no default IAM role
        '''
        result = self._values.get("default_iam_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def final_snapshot_name(self) -> typing.Optional[builtins.str]:
        '''The name of the snapshot to be created before the namespace is deleted.

        If not specified, the final snapshot will not be taken.

        :default: - no final snapshot
        '''
        result = self._values.get("final_snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_retention_period(self) -> typing.Optional[jsii.Number]:
        '''How long days to retain the final snapshot.

        You must set ``finalSnapshotName`` when you specify ``finalSnapshotRetentionPeriod``.

        :default: - Retained indefinitely if ``finalSnapshotName`` is specified, otherwise no final snapshot
        '''
        result = self._values.get("final_snapshot_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def iam_roles(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]]:
        '''A list of IAM roles to associate with the namespace.

        :default: - no IAM role associated
        '''
        result = self._values.get("iam_roles")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.IRole]], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''A Customer Managed Key used to encrypt your data.

        :default: - use AWS managed key
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def log_exports(self) -> typing.Optional[typing.List[LogExport]]:
        '''The types of logs the namespace can export.

        :default: - no logs export
        '''
        result = self._values.get("log_exports")
        return typing.cast(typing.Optional[typing.List[LogExport]], result)

    @builtins.property
    def namespace_name(self) -> typing.Optional[builtins.str]:
        '''The namespace name.

        :default: - auto generate
        '''
        result = self._values.get("namespace_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NamespaceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IWorkgroup)
class Workgroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.Workgroup",
):
    '''Represents a Redshift Serverless Workgroup construct in AWS CDK.

    Example::

        declare const namespace: Namespace;
        declare const vpc: aws_ec2.IVpc;
        
        const nameSpace = new Workgroup(
          stack,
          'Workgroup',
          {
            workgroupName: 'my-workgroup',
            namespace: namespace,
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
        base_capacity: typing.Optional[jsii.Number] = None,
        config_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        enhanced_vpc_routing: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[INamespace] = None,
        port: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        workgroup_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC to place the workgroup in. ``vpc`` must have at least 3 subnets, and they must span across 3 Availability Zones.
        :param base_capacity: The base compute capacity of the workgroup in Redshift Processing Units (RPUs). You can adjust the base capacity setting from 8 RPUs to 512 RPUs in units of 8. Also you can increment or decrement RPUs in units of 32 when setting a base capacity between 512-1024. Default: 128
        :param config_parameters: A list of parameters to set for finer control over a database. Default: - no config parameters
        :param enhanced_vpc_routing: The value that specifies whether to enable enhanced virtual private cloud (VPC) routing, which forces Amazon Redshift Serverless to route traffic through your VPC. Default: false
        :param namespace: The namespace the workgroup is associated with. Default: - the workgroup is not associated with any namespace
        :param port: The custom port to use when connecting to a workgroup. Valid port ranges are 5431-5455 and 8191-8215. Default: 5439
        :param publicly_accessible: A value that specifies whether the workgroup can be accessible from a public network. Default: false
        :param security_groups: The security groups to associate with the workgroup. Default: - a new security group is created
        :param vpc_subnets: Where to place the workgroup within the VPC. Default: - private subnets
        :param workgroup_name: The workgroup name. `workgroupName` must be between 3 and 64 characters long, contain only lowercase letters, numbers, and hyphens. Default: - auto generate
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e76664aed2efcfcdfc1c6c578dc2f15c70e3741f37095ee6e524d249364346cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = WorkgroupProps(
            vpc=vpc,
            base_capacity=base_capacity,
            config_parameters=config_parameters,
            enhanced_vpc_routing=enhanced_vpc_routing,
            namespace=namespace,
            port=port,
            publicly_accessible=publicly_accessible,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
            workgroup_name=workgroup_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromWorkgroupAttributes")
    @builtins.classmethod
    def from_workgroup_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        endpoint_address: builtins.str,
        port: jsii.Number,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        workgroup_id: builtins.str,
        workgroup_name: builtins.str,
    ) -> IWorkgroup:
        '''Import an existing workgroup to the stack from its attributes.

        :param scope: -
        :param id: -
        :param endpoint_address: The workgroup endpoint address.
        :param port: The workgroup port.
        :param security_groups: The security groups associated with the Redshift Serverless Workgroup.
        :param workgroup_id: The workgroup id.
        :param workgroup_name: The workgroup name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__820dae0853f425374177c865b0bf73cf64c8a8ffd2a9372948f0ca0cdb8e63ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = WorkgroupAttributes(
            endpoint_address=endpoint_address,
            port=port,
            security_groups=security_groups,
            workgroup_id=workgroup_id,
            workgroup_name=workgroup_name,
        )

        return typing.cast(IWorkgroup, jsii.sinvoke(cls, "fromWorkgroupAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        workgroup_name: builtins.str,
        base_capacity: typing.Optional[jsii.Number] = None,
        config_parameters: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        enhanced_vpc_routing: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        max_capacity: typing.Optional[jsii.Number] = None,
        namespace_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup:
        '''
        :param scope: -
        :param id: -
        :param workgroup_name: The name of the workgroup.
        :param base_capacity: The base compute capacity of the workgroup in Redshift Processing Units (RPUs).
        :param config_parameters: A list of parameters to set for finer control over a database. Available options are ``datestyle`` , ``enable_user_activity_logging`` , ``query_group`` , ``search_path`` , ``max_query_execution_time`` , and ``require_ssl`` .
        :param enhanced_vpc_routing: The value that specifies whether to enable enhanced virtual private cloud (VPC) routing, which forces Amazon Redshift Serverless to route traffic through your VPC. Default: - false
        :param max_capacity: The maximum data-warehouse capacity Amazon Redshift Serverless uses to serve queries. The max capacity is specified in RPUs.
        :param namespace_name: The namespace the workgroup is associated with.
        :param port: The custom port to use when connecting to a workgroup. Valid port ranges are 5431-5455 and 8191-8215. The default is 5439.
        :param publicly_accessible: A value that specifies whether the workgroup can be accessible from a public network. Default: - false
        :param security_group_ids: A list of security group IDs to associate with the workgroup.
        :param subnet_ids: A list of subnet IDs the workgroup is associated with.
        :param tags: The map of the key-value pairs used to tag the workgroup.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2835da8bf532f3a607fecc872467c62f975a5589c73c2e9ef9909617b82e671d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroupProps(
            workgroup_name=workgroup_name,
            base_capacity=base_capacity,
            config_parameters=config_parameters,
            enhanced_vpc_routing=enhanced_vpc_routing,
            max_capacity=max_capacity,
            namespace_name=namespace_name,
            port=port,
            publicly_accessible=publicly_accessible,
            security_group_ids=security_group_ids,
            subnet_ids=subnet_ids,
            tags=tags,
        )

        return typing.cast(_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup, jsii.invoke(self, "createResource", [scope, id, props]))

    @jsii.member(jsii_name="createSecurityGroup")
    def _create_security_group(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        disable_inline_rules: typing.Optional[builtins.bool] = None,
        security_group_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :param scope: -
        :param id: -
        :param vpc: The VPC in which to create the security group.
        :param allow_all_ipv6_outbound: Whether to allow all outbound ipv6 traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound ipv6 traffic. If this is set to false, no outbound traffic will be allowed by default and all egress ipv6 traffic must be explicitly authorized. To allow all ipv4 traffic use allowAllOutbound Default: false
        :param allow_all_outbound: Whether to allow all outbound traffic by default. If this is set to true, there will only be a single egress rule which allows all outbound traffic. If this is set to false, no outbound traffic will be allowed by default and all egress traffic must be explicitly authorized. To allow all ipv6 traffic use allowAllIpv6Outbound Default: true
        :param description: A description of the security group. Default: The default name will be the construct's CDK path.
        :param disable_inline_rules: Whether to disable inline ingress and egress rule optimization. If this is set to true, ingress and egress rules will not be declared under the SecurityGroup in cloudformation, but will be separate elements. Inlining rules is an optimization for producing smaller stack templates. Sometimes this is not desirable, for example when security group access is managed via tags. The default value can be overriden globally by setting the context variable '@aws-cdk/aws-ec2.securityGroupDisableInlineRules'. Default: false
        :param security_group_name: The name of the security group. For valid values, see the GroupName parameter of the CreateSecurityGroup action in the Amazon EC2 API Reference. It is not recommended to use an explicit group name. Default: If you don't specify a GroupName, AWS CloudFormation generates a unique physical ID and uses that ID for the group name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad0d2cd9af4f4dbe01f768d808fb8027e3deeec919c6a27869b62d5b4d6a9dac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_ec2_ceddda9d.SecurityGroupProps(
            vpc=vpc,
            allow_all_ipv6_outbound=allow_all_ipv6_outbound,
            allow_all_outbound=allow_all_outbound,
            description=description,
            disable_inline_rules=disable_inline_rules,
            security_group_name=security_group_name,
        )

        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.invoke(self, "createSecurityGroup", [scope, id, props]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The connection object associated with the Redshift Serverless Workgroup.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        '''The workgroup endpoint address.'''
        return typing.cast(builtins.str, jsii.get(self, "endpointAddress"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        '''The workgroup port.'''
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="workgroupArn")
    def workgroup_arn(self) -> builtins.str:
        '''The workgroup Arn.'''
        return typing.cast(builtins.str, jsii.get(self, "workgroupArn"))

    @builtins.property
    @jsii.member(jsii_name="workgroupId")
    def workgroup_id(self) -> builtins.str:
        '''The workgroup id.'''
        return typing.cast(builtins.str, jsii.get(self, "workgroupId"))

    @builtins.property
    @jsii.member(jsii_name="workgroupName")
    def workgroup_name(self) -> builtins.str:
        '''The workgroup name.'''
        return typing.cast(builtins.str, jsii.get(self, "workgroupName"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.WorkgroupAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_address": "endpointAddress",
        "port": "port",
        "security_groups": "securityGroups",
        "workgroup_id": "workgroupId",
        "workgroup_name": "workgroupName",
    },
)
class WorkgroupAttributes:
    def __init__(
        self,
        *,
        endpoint_address: builtins.str,
        port: jsii.Number,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        workgroup_id: builtins.str,
        workgroup_name: builtins.str,
    ) -> None:
        '''Attributes for importing a Redshift Serverless Workgroup.

        :param endpoint_address: The workgroup endpoint address.
        :param port: The workgroup port.
        :param security_groups: The security groups associated with the Redshift Serverless Workgroup.
        :param workgroup_id: The workgroup id.
        :param workgroup_name: The workgroup name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__852b6a530d5bf5f46dd477f360916580509725e3aa78794a8990bd8d411497a8)
            check_type(argname="argument endpoint_address", value=endpoint_address, expected_type=type_hints["endpoint_address"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument workgroup_id", value=workgroup_id, expected_type=type_hints["workgroup_id"])
            check_type(argname="argument workgroup_name", value=workgroup_name, expected_type=type_hints["workgroup_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "endpoint_address": endpoint_address,
            "port": port,
            "security_groups": security_groups,
            "workgroup_id": workgroup_id,
            "workgroup_name": workgroup_name,
        }

    @builtins.property
    def endpoint_address(self) -> builtins.str:
        '''The workgroup endpoint address.'''
        result = self._values.get("endpoint_address")
        assert result is not None, "Required property 'endpoint_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''The workgroup port.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security groups associated with the Redshift Serverless Workgroup.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def workgroup_id(self) -> builtins.str:
        '''The workgroup id.'''
        result = self._values.get("workgroup_id")
        assert result is not None, "Required property 'workgroup_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workgroup_name(self) -> builtins.str:
        '''The workgroup name.'''
        result = self._values.get("workgroup_name")
        assert result is not None, "Required property 'workgroup_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkgroupAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_redshiftserverless.WorkgroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "base_capacity": "baseCapacity",
        "config_parameters": "configParameters",
        "enhanced_vpc_routing": "enhancedVpcRouting",
        "namespace": "namespace",
        "port": "port",
        "publicly_accessible": "publiclyAccessible",
        "security_groups": "securityGroups",
        "vpc_subnets": "vpcSubnets",
        "workgroup_name": "workgroupName",
    },
)
class WorkgroupProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        base_capacity: typing.Optional[jsii.Number] = None,
        config_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        enhanced_vpc_routing: typing.Optional[builtins.bool] = None,
        namespace: typing.Optional[INamespace] = None,
        port: typing.Optional[jsii.Number] = None,
        publicly_accessible: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        workgroup_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a Redshift Serverless Workgroup.

        :param vpc: The VPC to place the workgroup in. ``vpc`` must have at least 3 subnets, and they must span across 3 Availability Zones.
        :param base_capacity: The base compute capacity of the workgroup in Redshift Processing Units (RPUs). You can adjust the base capacity setting from 8 RPUs to 512 RPUs in units of 8. Also you can increment or decrement RPUs in units of 32 when setting a base capacity between 512-1024. Default: 128
        :param config_parameters: A list of parameters to set for finer control over a database. Default: - no config parameters
        :param enhanced_vpc_routing: The value that specifies whether to enable enhanced virtual private cloud (VPC) routing, which forces Amazon Redshift Serverless to route traffic through your VPC. Default: false
        :param namespace: The namespace the workgroup is associated with. Default: - the workgroup is not associated with any namespace
        :param port: The custom port to use when connecting to a workgroup. Valid port ranges are 5431-5455 and 8191-8215. Default: 5439
        :param publicly_accessible: A value that specifies whether the workgroup can be accessible from a public network. Default: false
        :param security_groups: The security groups to associate with the workgroup. Default: - a new security group is created
        :param vpc_subnets: Where to place the workgroup within the VPC. Default: - private subnets
        :param workgroup_name: The workgroup name. `workgroupName` must be between 3 and 64 characters long, contain only lowercase letters, numbers, and hyphens. Default: - auto generate
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b5e77c2487e1c0ae9154f6bc2e00d031df1399619b9ce4743a3501c79621a00)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument base_capacity", value=base_capacity, expected_type=type_hints["base_capacity"])
            check_type(argname="argument config_parameters", value=config_parameters, expected_type=type_hints["config_parameters"])
            check_type(argname="argument enhanced_vpc_routing", value=enhanced_vpc_routing, expected_type=type_hints["enhanced_vpc_routing"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument publicly_accessible", value=publicly_accessible, expected_type=type_hints["publicly_accessible"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument workgroup_name", value=workgroup_name, expected_type=type_hints["workgroup_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if base_capacity is not None:
            self._values["base_capacity"] = base_capacity
        if config_parameters is not None:
            self._values["config_parameters"] = config_parameters
        if enhanced_vpc_routing is not None:
            self._values["enhanced_vpc_routing"] = enhanced_vpc_routing
        if namespace is not None:
            self._values["namespace"] = namespace
        if port is not None:
            self._values["port"] = port
        if publicly_accessible is not None:
            self._values["publicly_accessible"] = publicly_accessible
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if workgroup_name is not None:
            self._values["workgroup_name"] = workgroup_name

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC to place the workgroup in.

        ``vpc`` must have at least 3 subnets, and they must span across 3 Availability Zones.
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def base_capacity(self) -> typing.Optional[jsii.Number]:
        '''The base compute capacity of the workgroup in Redshift Processing Units (RPUs).

        You can adjust the base capacity setting from 8 RPUs to 512 RPUs in units of 8.
        Also you can increment or decrement RPUs in units of 32 when setting a base capacity between 512-1024.

        :default: 128

        :see: https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-capacity.html
        '''
        result = self._values.get("base_capacity")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def config_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of parameters to set for finer control over a database.

        :default: - no config parameters

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshiftserverless-workgroup.html#cfn-redshiftserverless-workgroup-configparameters
        '''
        result = self._values.get("config_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def enhanced_vpc_routing(self) -> typing.Optional[builtins.bool]:
        '''The value that specifies whether to enable enhanced virtual private cloud (VPC) routing, which forces Amazon Redshift Serverless to route traffic through your VPC.

        :default: false
        '''
        result = self._values.get("enhanced_vpc_routing")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def namespace(self) -> typing.Optional[INamespace]:
        '''The namespace the workgroup is associated with.

        :default: - the workgroup is not associated with any namespace
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[INamespace], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The custom port to use when connecting to a workgroup.

        Valid port ranges are 5431-5455 and 8191-8215.

        :default: 5439
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def publicly_accessible(self) -> typing.Optional[builtins.bool]:
        '''A value that specifies whether the workgroup can be accessible from a public network.

        :default: false
        '''
        result = self._values.get("publicly_accessible")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the workgroup.

        :default: - a new security group is created
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the workgroup within the VPC.

        :default: - private subnets
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def workgroup_name(self) -> typing.Optional[builtins.str]:
        '''The workgroup name.

        ``workgroupName`` must be between 3 and 64 characters long, contain only lowercase letters, numbers, and hyphens.

        :default: - auto generate
        '''
        result = self._values.get("workgroup_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkgroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "INamespace",
    "IWorkgroup",
    "LogExport",
    "Namespace",
    "NamespaceAttributes",
    "NamespaceProps",
    "Workgroup",
    "WorkgroupAttributes",
    "WorkgroupProps",
]

publication.publish()

def _typecheckingstub__921d62f637992096bd1f7ee9eb0148c1e142a6006a4163815b2a16964672d7c5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    admin_username: typing.Optional[builtins.str] = None,
    admin_user_password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    db_name: typing.Optional[builtins.str] = None,
    default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
    iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    log_exports: typing.Optional[typing.Sequence[LogExport]] = None,
    namespace_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc9e16e26692f52767387364ffb2c67d80c7d2f62a9c982691f7b1748a67e8cd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    namespace_id: builtins.str,
    namespace_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a66424df90aa8cdae9dadf104e864a8518eb7dd46de6abd70bb2ff17a87f77f(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a181e9c3f13276a32f87ef4d665f1b55295efc4a152ae8a6d94112c92bb014b3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    namespace_name: builtins.str,
    admin_password_secret_kms_key_id: typing.Optional[builtins.str] = None,
    admin_username: typing.Optional[builtins.str] = None,
    admin_user_password: typing.Optional[builtins.str] = None,
    db_name: typing.Optional[builtins.str] = None,
    default_iam_role_arn: typing.Optional[builtins.str] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
    iam_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    kms_key_id: typing.Optional[builtins.str] = None,
    log_exports: typing.Optional[typing.Sequence[builtins.str]] = None,
    manage_admin_password: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    namespace_resource_policy: typing.Any = None,
    redshift_idc_application_arn: typing.Optional[builtins.str] = None,
    snapshot_copy_configurations: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnNamespace.SnapshotCopyConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__655018c149d040f3f3a2d2303e836e46c51e0c2658ee75ad47ffb48e2a2f154c(
    *,
    namespace_id: builtins.str,
    namespace_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__289e731c521ae8d21fe51049e93fc1a322d3209ca080f5179e574b58db99f05a(
    *,
    admin_username: typing.Optional[builtins.str] = None,
    admin_user_password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    db_name: typing.Optional[builtins.str] = None,
    default_iam_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    final_snapshot_retention_period: typing.Optional[jsii.Number] = None,
    iam_roles: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.IRole]] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    log_exports: typing.Optional[typing.Sequence[LogExport]] = None,
    namespace_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76664aed2efcfcdfc1c6c578dc2f15c70e3741f37095ee6e524d249364346cd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    base_capacity: typing.Optional[jsii.Number] = None,
    config_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    enhanced_vpc_routing: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[INamespace] = None,
    port: typing.Optional[jsii.Number] = None,
    publicly_accessible: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    workgroup_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__820dae0853f425374177c865b0bf73cf64c8a8ffd2a9372948f0ca0cdb8e63ac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    endpoint_address: builtins.str,
    port: jsii.Number,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    workgroup_id: builtins.str,
    workgroup_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2835da8bf532f3a607fecc872467c62f975a5589c73c2e9ef9909617b82e671d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    workgroup_name: builtins.str,
    base_capacity: typing.Optional[jsii.Number] = None,
    config_parameters: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_redshiftserverless_ceddda9d.CfnWorkgroup.ConfigParameterProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    enhanced_vpc_routing: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    max_capacity: typing.Optional[jsii.Number] = None,
    namespace_name: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    publicly_accessible: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad0d2cd9af4f4dbe01f768d808fb8027e3deeec919c6a27869b62d5b4d6a9dac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    disable_inline_rules: typing.Optional[builtins.bool] = None,
    security_group_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__852b6a530d5bf5f46dd477f360916580509725e3aa78794a8990bd8d411497a8(
    *,
    endpoint_address: builtins.str,
    port: jsii.Number,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    workgroup_id: builtins.str,
    workgroup_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b5e77c2487e1c0ae9154f6bc2e00d031df1399619b9ce4743a3501c79621a00(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    base_capacity: typing.Optional[jsii.Number] = None,
    config_parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    enhanced_vpc_routing: typing.Optional[builtins.bool] = None,
    namespace: typing.Optional[INamespace] = None,
    port: typing.Optional[jsii.Number] = None,
    publicly_accessible: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    workgroup_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
