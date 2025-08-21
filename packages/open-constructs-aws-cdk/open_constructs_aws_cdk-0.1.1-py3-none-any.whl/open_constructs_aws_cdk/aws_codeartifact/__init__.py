r'''
Constructs for the AWS CodeArtifact service

# CDK Constructs for CodeArtifact Service

## Overview

The `Domain` and `Repository` constructs simplify the creation and management of AWS CodeArtifact domains and repositories within AWS CDK
applications. These constructs allow users to manage private repositories for software packages and define domains to group repositories,
facilitating secure sharing and version control across teams.

## Usage

Import the `Domain` and `Repository` constructs and create a new CodeArtifact domain & repository within your AWS CDK stack.

```python
import { App, Stack } from 'aws-cdk-lib';
import { Domain, Repository } from '@open-constructs/aws-cdk/aws-codeartifact';

const app = new App();
const stack = new Stack(app, 'CodeArtifactDomainStack');

const domain = new Domain(stack, 'MyDomain', {
  domainName: 'my-domain',
});

const repository = new Repository(this, 'MyRepo', {
  domain: domain,
  repositoryName: 'my-repo',
});
```

### Importing existing resources

If you need to manage an existing CodeArtifact repository, you can import it into your CDK stack. Since the domain is implicit in the ARN of the repository it will be automatically imported as well.

```python
import { Repository } from '@open-constructs/aws-cdk/aws-codeartifact';

const existingRepo = Repository.fromRepositoryArn(stack, 'ImportedRepo', 'arn:aws:codeartifact:us-east-1:123456789012:repository/my-domain/my-repo');
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
import aws_cdk.aws_codeartifact as _aws_cdk_aws_codeartifact_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_codeartifact.DomainAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "domain_arn": "domainArn",
        "domain_name": "domainName",
        "domain_owner": "domainOwner",
        "encryption_key": "encryptionKey",
    },
)
class DomainAttributes:
    def __init__(
        self,
        *,
        domain_arn: builtins.str,
        domain_name: builtins.str,
        domain_owner: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''Interface representing the attributes of a CodeArtifact domain.

        :param domain_arn: The ARN (Amazon Resource Name) of the CodeArtifact domain.
        :param domain_name: The name of the CodeArtifact domain.
        :param domain_owner: The AWS account ID that owns the domain.
        :param encryption_key: The AWS KMS encryption key associated with the domain, if any.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c109231d3736b50dc896dabd1e50ca5b62f1cfdda7494d6d022a07f7f3605d7f)
            check_type(argname="argument domain_arn", value=domain_arn, expected_type=type_hints["domain_arn"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument domain_owner", value=domain_owner, expected_type=type_hints["domain_owner"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_arn": domain_arn,
            "domain_name": domain_name,
            "domain_owner": domain_owner,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key

    @builtins.property
    def domain_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the CodeArtifact domain.'''
        result = self._values.get("domain_arn")
        assert result is not None, "Required property 'domain_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The name of the CodeArtifact domain.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_owner(self) -> builtins.str:
        '''The AWS account ID that owns the domain.'''
        result = self._values.get("domain_owner")
        assert result is not None, "Required property 'domain_owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS encryption key associated with the domain, if any.'''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_codeartifact.DomainProps",
    jsii_struct_bases=[],
    name_mapping={"domain_name": "domainName", "encryption_key": "encryptionKey"},
)
class DomainProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''Construction properties for ``Domain``.

        :param domain_name: The name of the Domain.
        :param encryption_key: The key used to encrypt the Domain. Default: - An AWS managed KMS key is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bda309421b7559277b11225ab420a35b5369e809799ac8153e9fa3c0862b509f)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The name of the Domain.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The key used to encrypt the Domain.

        :default: - An AWS managed KMS key is used
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_codeartifact.IDomain")
class IDomain(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''Represents a CodeArtifact Domain.'''

    @builtins.property
    @jsii.member(jsii_name="domainArn")
    def domain_arn(self) -> builtins.str:
        '''The ARN of the Domain.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''The name of the Domain.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        '''12-digit account number of the AWS account that owns the domain that contains the Domain.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainEncryptionKey")
    def domain_encryption_key(self) -> typing.Optional[builtins.str]:
        '''The ARN of the key used to encrypt the Domain.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used to encrypt the Domain.'''
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''Adds a statement to the Codeartifact domain resource policy.

        :param statement: The policy statement to add.
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permissions to the specified grantee on this CodeArtifact domain.

        It handles both same-environment and cross-environment scenarios:

        - For same-environment grants, it adds the permissions to the principal or resource.
        - For cross-environment grants, it adds the permissions to both the principal and the resource.

        :param grantee: - The principal to grant permissions to.
        :param actions: - The actions to grant. These should be valid CodeArtifact actions.
        '''
        ...

    @jsii.member(jsii_name="grantContribute")
    def grant_contribute(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants contribute permissions to the specified grantee on this CodeArtifact domain.

        :param grantee: - The principal to grant contribute permissions to.
        '''
        ...


class _IDomainProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''Represents a CodeArtifact Domain.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_codeartifact.IDomain"

    @builtins.property
    @jsii.member(jsii_name="domainArn")
    def domain_arn(self) -> builtins.str:
        '''The ARN of the Domain.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainArn"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''The name of the Domain.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        '''12-digit account number of the AWS account that owns the domain that contains the Domain.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @builtins.property
    @jsii.member(jsii_name="domainEncryptionKey")
    def domain_encryption_key(self) -> typing.Optional[builtins.str]:
        '''The ARN of the key used to encrypt the Domain.

        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainEncryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used to encrypt the Domain.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "encryptionKey"))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''Adds a statement to the Codeartifact domain resource policy.

        :param statement: The policy statement to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c8236f4c606fe58dced0b657e9f6a829ceb6bfe15fb58389cee4e062b060584)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permissions to the specified grantee on this CodeArtifact domain.

        It handles both same-environment and cross-environment scenarios:

        - For same-environment grants, it adds the permissions to the principal or resource.
        - For cross-environment grants, it adds the permissions to both the principal and the resource.

        :param grantee: - The principal to grant permissions to.
        :param actions: - The actions to grant. These should be valid CodeArtifact actions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8aac46825d08b3bbb12ae75e9fb511f75f6e7317d79a23ebeccd382bd433839)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantContribute")
    def grant_contribute(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants contribute permissions to the specified grantee on this CodeArtifact domain.

        :param grantee: - The principal to grant contribute permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d31471ca17498c50cc76e566639d2402aff6930001fc90790f6f327e416fd3e)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantContribute", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomain).__jsii_proxy_class__ = lambda : _IDomainProxy


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_codeartifact.IRepository")
class IRepository(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''Represents an CodeArtifact Repository.'''

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> IDomain:
        '''The domain that contains the repository.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> builtins.str:
        '''The ARN of the repository.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryDomainName")
    def repository_domain_name(self) -> builtins.str:
        '''The domain that contains the repository.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryDomainOwner")
    def repository_domain_owner(self) -> builtins.str:
        '''The domain owner of the repository.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The name of the repository.

        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''Adds a statement to the CodeArtifact repository resource policy.

        :param statement: The policy statement to add.
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants the given principal identity permissions to perform the actions on the repository.

        :param grantee: The principal to grant permissions to.
        :param actions: The actions to grant.
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants the given principal identity permissions to perform the actions on the repository.

        :param grantee: The principal to grant permissions to.
        '''
        ...

    @jsii.member(jsii_name="grantReadAndPublish")
    def grant_read_and_publish(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants the given principal identity permissions to perform the actions on the repository.

        :param grantee: The principal to grant permissions to.
        '''
        ...


class _IRepositoryProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''Represents an CodeArtifact Repository.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_codeartifact.IRepository"

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> IDomain:
        '''The domain that contains the repository.'''
        return typing.cast(IDomain, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> builtins.str:
        '''The ARN of the repository.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryArn"))

    @builtins.property
    @jsii.member(jsii_name="repositoryDomainName")
    def repository_domain_name(self) -> builtins.str:
        '''The domain that contains the repository.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryDomainName"))

    @builtins.property
    @jsii.member(jsii_name="repositoryDomainOwner")
    def repository_domain_owner(self) -> builtins.str:
        '''The domain owner of the repository.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryDomainOwner"))

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The name of the repository.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''Adds a statement to the CodeArtifact repository resource policy.

        :param statement: The policy statement to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0959504b2f1d7a0b506f9b545ad9b2f131a04154f7af8d55987c54b5cd08938c)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants the given principal identity permissions to perform the actions on the repository.

        :param grantee: The principal to grant permissions to.
        :param actions: The actions to grant.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b9d42dc0cdd6b42ea423070fcb7b4481d2baac142fe936d5211dda62eca9d2)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants the given principal identity permissions to perform the actions on the repository.

        :param grantee: The principal to grant permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3788fd271973de8dd7177bc1dc7491c0cb1da348880d167c6dddb7dcbab1e4d8)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantReadAndPublish")
    def grant_read_and_publish(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants the given principal identity permissions to perform the actions on the repository.

        :param grantee: The principal to grant permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__619867cf123aff4b515ffc9fab13c3b1059bb1a47f39710fc50389c615f88928)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadAndPublish", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRepository).__jsii_proxy_class__ = lambda : _IRepositoryProxy


@jsii.implements(IRepository)
class Repository(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_codeartifact.Repository",
):
    '''Deploys a CodeArtifact repository.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: IDomain,
        description: typing.Optional[builtins.str] = None,
        external_connection: typing.Optional["RepositoryConnection"] = None,
        repository_name: typing.Optional[builtins.str] = None,
        upstreams: typing.Optional[typing.Sequence[IRepository]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain: The domain that contains the repository.
        :param description: The description of the repository. Default: - No description
        :param external_connection: The connections to external repositories (like npmjs, pypi, etc.). You can use the AWS CLI to connect your CodeArtifact repository to an external repository by adding an external connection directly to the repository. This will allow users connected to the CodeArtifact repository, or any of its downstream repositories, to fetch packages from the configured external repository. Each CodeArtifact repository can only have one external connection. Default: - No external connections
        :param repository_name: The name of the repository. Default: - A name is automatically generated
        :param upstreams: A list of upstream Codeartifact repositories to associate with the repository. The order of the upstream repositories in the list determines their priority order when CodeArtifact looks for a requested package version. see https://docs.aws.amazon.com/codeartifact/latest/ug/repo-upstream-behavior.html#package-retention-intermediate-repositories Default: - No upstream repositories
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ee4cfdb03a9ecad3c576bc4f75ca47c716f6087dee5bbfb4db2ec07edf8f1a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RepositoryProps(
            domain=domain,
            description=description,
            external_connection=external_connection,
            repository_name=repository_name,
            upstreams=upstreams,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromRepositoryArn")
    @builtins.classmethod
    def from_repository_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        repository_arn: builtins.str,
    ) -> IRepository:
        '''Creates an IRepository object from an existing repository ARN.

        :param scope: - The parent construct in which to create this repository reference.
        :param id: - The identifier of the construct.
        :param repository_arn: - The ARN of the repository to import.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e0cb00ec061b4f5cdfb330bdf8765bb028fa44496b4ade946e47f01d444a6ed)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument repository_arn", value=repository_arn, expected_type=type_hints["repository_arn"])
        return typing.cast(IRepository, jsii.sinvoke(cls, "fromRepositoryArn", [scope, id, repository_arn]))

    @jsii.member(jsii_name="fromRepositoryAttributes")
    @builtins.classmethod
    def from_repository_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain: IDomain,
        repository_arn: builtins.str,
        repository_name: builtins.str,
    ) -> IRepository:
        '''Creates an IRepository object from existing repository attributes.

        :param scope: - The parent construct in which to create this repository reference.
        :param id: - The identifier of the construct.
        :param domain: The CodeArtifact domain associated with this repository.
        :param repository_arn: The ARN (Amazon Resource Name) of the CodeArtifact repository.
        :param repository_name: The name of the CodeArtifact repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07c900597c65b47b66a930a11b0d02eb5a67a1bfc203b233552019a3cb465d53)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = RepositoryAttributes(
            domain=domain,
            repository_arn=repository_arn,
            repository_name=repository_name,
        )

        return typing.cast(IRepository, jsii.sinvoke(cls, "fromRepositoryAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''Adds a statement to the CodeArtifact repository resource policy.

        :param statement: The policy statement to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7372a5c81257e393bd4095d93b4cd1599ea053bc7c45d70e1bbc0a40de8a924d)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnRepository:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0b1e059e2b7a259104ec846bbdaf88a25ae770561f3160c29df23fb58e2e1b8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnRepository, jsii.invoke(self, "createResource", [scope, id]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permissions to the specified grantee on this CodeArtifact repository.

        :param grantee: The principal to grant permissions to.
        :param actions: The actions to grant.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4768886209cd4bcd32623ea9c3c1542fd381e7e12fe31696bca2d55b9ac9cd43)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants read permissions to the specified grantee on this CodeArtifact repository.

        :param grantee: The principal to grant read permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd76e179744fe1f3eb436a2aa95606a6a9cb3afb702159163145a5f7ddf84bf0)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantReadAndPublish")
    def grant_read_and_publish(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants read and publish permissions to the specified grantee on this CodeArtifact repository.

        :param grantee: The principal to grant read and publish permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a91d63c253e196851c004d1cc9d27c5eeb157937404899ca2e41c2e9250c95)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadAndPublish", [grantee]))

    @jsii.member(jsii_name="renderUpstreams")
    def _render_upstreams(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "renderUpstreams", []))

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> IDomain:
        '''The domain that contains this repository.'''
        return typing.cast(IDomain, jsii.get(self, "domain"))

    @builtins.property
    @jsii.member(jsii_name="repositoryArn")
    def repository_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of this CodeArtifact repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryArn"))

    @builtins.property
    @jsii.member(jsii_name="repositoryDomainName")
    def repository_domain_name(self) -> builtins.str:
        '''The domain that contains this repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryDomainName"))

    @builtins.property
    @jsii.member(jsii_name="repositoryDomainOwner")
    def repository_domain_owner(self) -> builtins.str:
        '''The domain owner of this repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryDomainOwner"))

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The name of this CodeArtifact repository.'''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @builtins.property
    @jsii.member(jsii_name="upstreams")
    def _upstreams(self) -> typing.List[IRepository]:
        return typing.cast(typing.List[IRepository], jsii.get(self, "upstreams"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def _policy(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], jsii.get(self, "policy"))

    @builtins.property
    @jsii.member(jsii_name="cfnResource")
    def _cfn_resource(self) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnRepository:
        '''(internal) The CloudFormation resource representing this CodeArtifact repository.'''
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnRepository, jsii.get(self, "cfnResource"))

    @_cfn_resource.setter
    def _cfn_resource(
        self,
        value: _aws_cdk_aws_codeartifact_ceddda9d.CfnRepository,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53c035aa2d7d564b157ad96217f36a749894de3416a37c696098d62c13657418)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cfnResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cfnResourceProps")
    def _cfn_resource_props(
        self,
    ) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnRepositoryProps:
        '''The properties used to create the CloudFormation resource for this repository.'''
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnRepositoryProps, jsii.get(self, "cfnResourceProps"))

    @_cfn_resource_props.setter
    def _cfn_resource_props(
        self,
        value: _aws_cdk_aws_codeartifact_ceddda9d.CfnRepositoryProps,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__709f8c12811401f86b43b15e801e92f62f81109f2a53c56c96db1e63bb0e258d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cfnResourceProps", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_codeartifact.RepositoryAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "repository_arn": "repositoryArn",
        "repository_name": "repositoryName",
    },
)
class RepositoryAttributes:
    def __init__(
        self,
        *,
        domain: IDomain,
        repository_arn: builtins.str,
        repository_name: builtins.str,
    ) -> None:
        '''Represents the attributes of an existing CodeArtifact repository.

        :param domain: The CodeArtifact domain associated with this repository.
        :param repository_arn: The ARN (Amazon Resource Name) of the CodeArtifact repository.
        :param repository_name: The name of the CodeArtifact repository.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93cc9f195167e10e5e90b4b76b6fbaad16c1540b02a50d70560fab445cd696be)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument repository_arn", value=repository_arn, expected_type=type_hints["repository_arn"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "repository_arn": repository_arn,
            "repository_name": repository_name,
        }

    @builtins.property
    def domain(self) -> IDomain:
        '''The CodeArtifact domain associated with this repository.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(IDomain, result)

    @builtins.property
    def repository_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of the CodeArtifact repository.'''
        result = self._values.get("repository_arn")
        assert result is not None, "Required property 'repository_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''The name of the CodeArtifact repository.'''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@open-constructs/aws-cdk.aws_codeartifact.RepositoryConnection")
class RepositoryConnection(enum.Enum):
    '''Represents the supported external connections for CodeArtifact repositories.'''

    PYTHON = "PYTHON"
    '''Python Package Index (PyPI).'''
    NPM = "NPM"
    '''Node Package Manager (npm).'''
    NUGET = "NUGET"
    '''NuGet Gallery.'''
    RUBY = "RUBY"
    '''RubyGems.'''
    RUST = "RUST"
    '''Crates.io (Rust).'''
    MAVEN_CENTRAL = "MAVEN_CENTRAL"
    '''Maven Central Repository.'''
    GRADLE_PLUGINS = "GRADLE_PLUGINS"
    '''Gradle Plugins.'''
    MAVEN_GOOGLE = "MAVEN_GOOGLE"
    '''Maven Google.'''
    MAVEN_APACHE = "MAVEN_APACHE"
    '''Maven Apache.'''
    MAVEN_ATLASSIAN = "MAVEN_ATLASSIAN"
    '''Maven Atlassian.'''
    MAVEN_ECLIPSE = "MAVEN_ECLIPSE"
    '''Maven Eclipse.'''
    MAVEN_JBOSS = "MAVEN_JBOSS"
    '''Maven JBoss.'''
    MAVEN_SPRING = "MAVEN_SPRING"
    '''Maven Spring.'''
    MAVEN_SPRING_PLUGINS = "MAVEN_SPRING_PLUGINS"
    '''Maven Spring Plugins.'''


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_codeartifact.RepositoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain": "domain",
        "description": "description",
        "external_connection": "externalConnection",
        "repository_name": "repositoryName",
        "upstreams": "upstreams",
    },
)
class RepositoryProps:
    def __init__(
        self,
        *,
        domain: IDomain,
        description: typing.Optional[builtins.str] = None,
        external_connection: typing.Optional[RepositoryConnection] = None,
        repository_name: typing.Optional[builtins.str] = None,
        upstreams: typing.Optional[typing.Sequence[IRepository]] = None,
    ) -> None:
        '''Properties for creating a new CodeArtifact repository.

        :param domain: The domain that contains the repository.
        :param description: The description of the repository. Default: - No description
        :param external_connection: The connections to external repositories (like npmjs, pypi, etc.). You can use the AWS CLI to connect your CodeArtifact repository to an external repository by adding an external connection directly to the repository. This will allow users connected to the CodeArtifact repository, or any of its downstream repositories, to fetch packages from the configured external repository. Each CodeArtifact repository can only have one external connection. Default: - No external connections
        :param repository_name: The name of the repository. Default: - A name is automatically generated
        :param upstreams: A list of upstream Codeartifact repositories to associate with the repository. The order of the upstream repositories in the list determines their priority order when CodeArtifact looks for a requested package version. see https://docs.aws.amazon.com/codeartifact/latest/ug/repo-upstream-behavior.html#package-retention-intermediate-repositories Default: - No upstream repositories
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74b744238221843925e3caa2c8c70c1d0da2ff06fbe89ceda90277d5beb3d578)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument external_connection", value=external_connection, expected_type=type_hints["external_connection"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument upstreams", value=upstreams, expected_type=type_hints["upstreams"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
        }
        if description is not None:
            self._values["description"] = description
        if external_connection is not None:
            self._values["external_connection"] = external_connection
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if upstreams is not None:
            self._values["upstreams"] = upstreams

    @builtins.property
    def domain(self) -> IDomain:
        '''The domain that contains the repository.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(IDomain, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the repository.

        :default: - No description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_connection(self) -> typing.Optional[RepositoryConnection]:
        '''The connections to external repositories (like npmjs, pypi, etc.).

        You can use the AWS CLI to connect your CodeArtifact repository to an external repository by adding an external connection directly to the repository.
        This will allow users connected to the CodeArtifact repository, or any of its downstream repositories, to fetch packages from the configured external repository.
        Each CodeArtifact repository can only have one external connection.

        :default: - No external connections
        '''
        result = self._values.get("external_connection")
        return typing.cast(typing.Optional[RepositoryConnection], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''The name of the repository.

        :default: - A name is automatically generated
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upstreams(self) -> typing.Optional[typing.List[IRepository]]:
        '''A list of upstream Codeartifact repositories to associate with the repository.

        The order of the upstream repositories in the list determines their priority order when CodeArtifact looks for a requested package version.
        see https://docs.aws.amazon.com/codeartifact/latest/ug/repo-upstream-behavior.html#package-retention-intermediate-repositories

        :default: - No upstream repositories
        '''
        result = self._values.get("upstreams")
        return typing.cast(typing.Optional[typing.List[IRepository]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IDomain)
class Domain(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_codeartifact.Domain",
):
    '''Deploys a CodeArtifact domain.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: The name of the Domain.
        :param encryption_key: The key used to encrypt the Domain. Default: - An AWS managed KMS key is used
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9dcd366bf741719faf5ea62756b42382e945b15cd24906a510ce03283b73560)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DomainProps(domain_name=domain_name, encryption_key=encryption_key)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDomainArn")
    @builtins.classmethod
    def from_domain_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        domain_arn: builtins.str,
    ) -> IDomain:
        '''Creates an IDomain object from an existing CodeArtifact domain ARN.

        :param scope: The parent construct.
        :param id: The construct id.
        :param domain_arn: - The ARN (Amazon Resource Name) of the existing CodeArtifact domain.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09f46d8051e554ed384ccac3d5877a883732c2824a3ef6e4406f097bd48e33fc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument domain_arn", value=domain_arn, expected_type=type_hints["domain_arn"])
        return typing.cast(IDomain, jsii.sinvoke(cls, "fromDomainArn", [scope, id, domain_arn]))

    @jsii.member(jsii_name="fromDomainAttributes")
    @builtins.classmethod
    def from_domain_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_arn: builtins.str,
        domain_name: builtins.str,
        domain_owner: builtins.str,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    ) -> IDomain:
        '''Creates a Domain object from existing domain attributes.

        :param scope: The parent construct.
        :param id: The construct id.
        :param domain_arn: The ARN (Amazon Resource Name) of the CodeArtifact domain.
        :param domain_name: The name of the CodeArtifact domain.
        :param domain_owner: The AWS account ID that owns the domain.
        :param encryption_key: The AWS KMS encryption key associated with the domain, if any.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc7d8a459f12f3b348d15176032439ef30dcd2f1d274a4dedd94feb4cc578fe3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = DomainAttributes(
            domain_arn=domain_arn,
            domain_name=domain_name,
            domain_owner=domain_owner,
            encryption_key=encryption_key,
        )

        return typing.cast(IDomain, jsii.sinvoke(cls, "fromDomainAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''Adds a statement to the Codeartifact domain resource policy.

        :param statement: The policy statement to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5abc8f8a30217cb0b835e8db9783f4f11f9a4013a4a2f183a538c9b5c56cd60)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnDomain:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c17115e375263a42744d2e6b56a4423a44e9fc529e8e1aeca254d9a38614ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnDomain, jsii.invoke(self, "createResource", [scope, id]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants permissions to the specified grantee on this CodeArtifact domain.

        It handles both same-environment and cross-environment scenarios:

        - For same-environment grants, it adds the permissions to the principal or resource.
        - For cross-environment grants, it adds the permissions to both the principal and the resource.

        :param grantee: - The principal to grant permissions to.
        :param actions: - The actions to grant. These should be valid CodeArtifact actions.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6401d3f915f3f485b50bbef13d4e273d43b3632d840790f21a7e12afd2a6c44)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantContribute")
    def grant_contribute(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grants contribute permissions to the specified grantee on this CodeArtifact domain.

        :param grantee: - The principal to grant contribute permissions to.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59bb130822501345d67f2962b45e25b34105d38125531c0e6503c19e04690fb)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantContribute", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="domainArn")
    def domain_arn(self) -> builtins.str:
        '''The ARN (Amazon Resource Name) of this CodeArtifact domain.'''
        return typing.cast(builtins.str, jsii.get(self, "domainArn"))

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''The name of this CodeArtifact domain.'''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> builtins.str:
        '''The AWS account ID that owns this domain.'''
        return typing.cast(builtins.str, jsii.get(self, "domainOwner"))

    @builtins.property
    @jsii.member(jsii_name="domainEncryptionKey")
    def domain_encryption_key(self) -> typing.Optional[builtins.str]:
        '''The ARN of the key used to encrypt the Domain.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainEncryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The AWS KMS encryption key associated with this domain, if any.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="cfnResource")
    def _cfn_resource(self) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnDomain:
        '''(internal) The CloudFormation resource representing this CodeArtifact domain.'''
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnDomain, jsii.get(self, "cfnResource"))

    @_cfn_resource.setter
    def _cfn_resource(
        self,
        value: _aws_cdk_aws_codeartifact_ceddda9d.CfnDomain,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3400194a84478bbaf6d2b8840bdd827a53ac6c56cbd08ae70b1176c330a49b3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cfnResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policy")
    def _policy(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], jsii.get(self, "policy"))

    @_policy.setter
    def _policy(
        self,
        value: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cb66b2e3da0f56ac62d2aba216cdb0d17f813cc4f284d49a43bc6dea7926d39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policy", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Domain",
    "DomainAttributes",
    "DomainProps",
    "IDomain",
    "IRepository",
    "Repository",
    "RepositoryAttributes",
    "RepositoryConnection",
    "RepositoryProps",
]

publication.publish()

def _typecheckingstub__c109231d3736b50dc896dabd1e50ca5b62f1cfdda7494d6d022a07f7f3605d7f(
    *,
    domain_arn: builtins.str,
    domain_name: builtins.str,
    domain_owner: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bda309421b7559277b11225ab420a35b5369e809799ac8153e9fa3c0862b509f(
    *,
    domain_name: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c8236f4c606fe58dced0b657e9f6a829ceb6bfe15fb58389cee4e062b060584(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8aac46825d08b3bbb12ae75e9fb511f75f6e7317d79a23ebeccd382bd433839(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d31471ca17498c50cc76e566639d2402aff6930001fc90790f6f327e416fd3e(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0959504b2f1d7a0b506f9b545ad9b2f131a04154f7af8d55987c54b5cd08938c(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b9d42dc0cdd6b42ea423070fcb7b4481d2baac142fe936d5211dda62eca9d2(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3788fd271973de8dd7177bc1dc7491c0cb1da348880d167c6dddb7dcbab1e4d8(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__619867cf123aff4b515ffc9fab13c3b1059bb1a47f39710fc50389c615f88928(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ee4cfdb03a9ecad3c576bc4f75ca47c716f6087dee5bbfb4db2ec07edf8f1a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: IDomain,
    description: typing.Optional[builtins.str] = None,
    external_connection: typing.Optional[RepositoryConnection] = None,
    repository_name: typing.Optional[builtins.str] = None,
    upstreams: typing.Optional[typing.Sequence[IRepository]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e0cb00ec061b4f5cdfb330bdf8765bb028fa44496b4ade946e47f01d444a6ed(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    repository_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07c900597c65b47b66a930a11b0d02eb5a67a1bfc203b233552019a3cb465d53(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain: IDomain,
    repository_arn: builtins.str,
    repository_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7372a5c81257e393bd4095d93b4cd1599ea053bc7c45d70e1bbc0a40de8a924d(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0b1e059e2b7a259104ec846bbdaf88a25ae770561f3160c29df23fb58e2e1b8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4768886209cd4bcd32623ea9c3c1542fd381e7e12fe31696bca2d55b9ac9cd43(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd76e179744fe1f3eb436a2aa95606a6a9cb3afb702159163145a5f7ddf84bf0(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a91d63c253e196851c004d1cc9d27c5eeb157937404899ca2e41c2e9250c95(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53c035aa2d7d564b157ad96217f36a749894de3416a37c696098d62c13657418(
    value: _aws_cdk_aws_codeartifact_ceddda9d.CfnRepository,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__709f8c12811401f86b43b15e801e92f62f81109f2a53c56c96db1e63bb0e258d(
    value: _aws_cdk_aws_codeartifact_ceddda9d.CfnRepositoryProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93cc9f195167e10e5e90b4b76b6fbaad16c1540b02a50d70560fab445cd696be(
    *,
    domain: IDomain,
    repository_arn: builtins.str,
    repository_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b744238221843925e3caa2c8c70c1d0da2ff06fbe89ceda90277d5beb3d578(
    *,
    domain: IDomain,
    description: typing.Optional[builtins.str] = None,
    external_connection: typing.Optional[RepositoryConnection] = None,
    repository_name: typing.Optional[builtins.str] = None,
    upstreams: typing.Optional[typing.Sequence[IRepository]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9dcd366bf741719faf5ea62756b42382e945b15cd24906a510ce03283b73560(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09f46d8051e554ed384ccac3d5877a883732c2824a3ef6e4406f097bd48e33fc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    domain_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc7d8a459f12f3b348d15176032439ef30dcd2f1d274a4dedd94feb4cc578fe3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_arn: builtins.str,
    domain_name: builtins.str,
    domain_owner: builtins.str,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5abc8f8a30217cb0b835e8db9783f4f11f9a4013a4a2f183a538c9b5c56cd60(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c17115e375263a42744d2e6b56a4423a44e9fc529e8e1aeca254d9a38614ef(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6401d3f915f3f485b50bbef13d4e273d43b3632d840790f21a7e12afd2a6c44(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59bb130822501345d67f2962b45e25b34105d38125531c0e6503c19e04690fb(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3400194a84478bbaf6d2b8840bdd827a53ac6c56cbd08ae70b1176c330a49b3f(
    value: _aws_cdk_aws_codeartifact_ceddda9d.CfnDomain,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cb66b2e3da0f56ac62d2aba216cdb0d17f813cc4f284d49a43bc6dea7926d39(
    value: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument],
) -> None:
    """Type checking stubs"""
    pass
