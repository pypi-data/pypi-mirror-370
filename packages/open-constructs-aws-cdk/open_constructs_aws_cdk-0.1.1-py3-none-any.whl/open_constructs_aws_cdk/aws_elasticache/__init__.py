r'''
Constructs for the Amazon ElastiCache

# ElastiCache CDK Construct

This module has constructs for [Amazon ElastiCache](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html).

* The `User` and `UserGroup` constructs facilitate the creation and management of users for the cache.
* The `ServerlessCache` construct facilitates the creation and management of serverless cache.

## Basic Usage for user and user group

Setup required properties and create:

```python
const newDefaultUser = new NoPasswordRequiredUser(this, 'DefaultUser', {
  userName: 'default',
});

const userGroup = new UserGroup(this, 'UserGroup', {
  users: [defaultUser],
});
```

### RBAC

In Valkey 7.2 and onward and Redis OSS 6.0 onward you can use a feature called Role-Based Access Control (RBAC). RBAC is also the only way to control access to serverless caches.

RBAC enables you to control cache access through user groups. These user groups are designed as a way to organize access to caches.

For more information, see [Role-Based Access Control (RBAC)](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html).

To enable RBAC for ElastiCache with Valkey or Redis OSS, you take the following steps:

* Create users.
* Create a user group and add users to the user group.
* Assign the user group to a cache.

### Create users

First, you need to create users by using `IamUser`, `PasswordUser` or `NoPasswordRequiredUser` construct.

With RBAC, you create users and assign them specific permissions by using `accessString` property.

For more information, see [Specifying Permissions Using an Access String](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html#Access-string).

You can create an IAM-enabled user by using `IamUser` construct:

```python
const user = new IamUser(this, 'User', {
  // set user id
  userId: 'my-user',

  // set access string
  accessString: 'on ~* +@all',
});
```

> NOTE: You can't set username in `IamUser` construct because IAM-enabled users must have matching user id and username. For more information, see [Limitations](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth-iam.html). The construct automatically sets the username to be the same as the user id.

If you want to create a password authenticated user, use `PasswordUser` construct:

```python
const user = new PasswordUser(this, 'User', {
  // set user id
  userId: 'my-user-id',

  // set access string
  accessString: 'on ~* +@all',

  // set username
  userName: 'my-user-name',

  // set up to two passwords
  passwords: [
    cdk.SecretValue.unsafePlainText('adminUserPassword123'),
    cdk.SecretValue.unsafePlainText('anotherAdminUserPassword123'),
  ],
});
```

If the `passwords` property is not specified, a single password will be automatically generated and stored in AWS Secrets Manager.

```python
const user = new PasswordUser(this, 'User', {
  userId: 'my-user-id',
  accessString: 'on ~* +@all',
  userName: 'my-user-name',
  // `passwords` property is not specified and a single password will be generated
});

// you can access the ISecret object
user.generatedSecret
```

You can also create a no password required user by using `NoPasswordRequiredUser` construct:

```python
const user = new NoPasswordRequiredUser(this, 'User', {
  // set user id
  userId: 'my-user-id',

  // set access string
  accessString: 'on ~* +@all',

  // set username
  userName: 'my-user-name',
});
```

### Default user

ElastiCache automatically creates a default user with both a user ID and username set to `default`. This default user cannot be modified or deleted. The user is created as a no password authentication user.

This user is intended for compatibility with the default behavior of previous Redis OSS versions and has an access string that permits it to call all commands and access all keys.

To use this automatically created default user in CDK, you can import it using `NoPasswordRequiredUser.fromUserAttributes` method. For more information on import methods, see the [Import an existing user and user group](#import-an-existing-user-and-user-group) section.

To add proper access control to a cache, replace the default user with a new one that is either disabled by setting the `accessString` to `off -@all` or secured with a strong password.

To change the default user, create a new default user with the username set to `default`. You can then swap it with the original default user.

For more information, see [Applying RBAC to a Cache for ElastiCache with Valkey or Redis OSS](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html#rbac-using).

If you want to create a new default user, `userName` must be `default` and `userId` must not be `default` by using `NoPasswordRequiredUser` or `PasswordUser`:

```python
// use the original `default` user by using import method
const defaultUser = NoPasswordRequiredUser.fromUserAttributes(this, 'DefaultUser', {
  // userId and userName must be 'default'
  userId: 'default',
  userName: 'default',
});

// create a new default user
const newDefaultUser = new NoPasswordRequiredUser(this, 'NewDefaultUser', {
  // new default user id must not be 'default'
  userId: 'new-default',
  // default username must be 'default'
  userName: 'default',
});
```

> NOTE: You can't create a new default user using `IamUser` because an IAM-enabled user's username and user ID cannot be different.

### Add users to the user group

Next, use the `UserGroup` construct to create a user group and add users to it.
Ensure that you include either the original default user or a new default user:

```python
declare const newDefaultUser: User;
declare const user: User;
declare const anotherUser: User;

const userGroup = new UserGroup(this, 'UserGroup', {
  // add users including default user
  users: [newDefaultUser, user],
});

// you can also add a user by using addUser method
userGroup.addUser(anotherUser);
```

### Assign user group

Finally, assign a user group to cache:

```python
declare const vpc: ec2.Vpc;
declare const userGroup: UserGroup;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  majorEngineVersion: MajorVersion.VER_8,
  serverlessCacheName: 'my-serverless-cache',
  vpc,
  // assign User Group
  userGroup,
});
```

### Grant permissions to IAM-enabled users

If you create IAM-enabled users, `"elasticache:Connect"` action must be allowed for the users and cache.

> NOTE: You don't need grant permissions to no password required users or password authentication users.

For more information, see [Authenticating with IAM](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth-iam.html).

To grant permissions, you can use the `grantConnect` method in `IamUser` and `ServerlessCache` constructs:

```python
declare const user: IamUser;
declare const serverlessCache: ServerlessCache;
declare const role: iam.Role;

// grant "elasticache:Connect" action permissions to role
user.grantConnect(role);
serverlessCache.grantConnect(role);
```

### Import an existing user and user group

You can import an existing user and user group by using import methods:

```python
const importedIamUser = IamUser.fromUserId(this, 'ImportedIamUser', 'my-iam-user-id');

const importedPasswordUser = PasswordUser.fromUserAttributes(stack, 'ImportedPasswordUser', {
  userId: 'my-password-user-id',
  userName: 'my-password-user-name',
});

const importedNoPasswordRequiredUser = NoPasswordRequiredUser.fromUserAttributes(stack, 'ImportedNoPasswordUser', {
  userId: 'my-no-password-user-id',
  userName: 'my-no-password-user-name',
});

const importedUserGroup = UserGroup.fromUserGroupId(this, 'ImportedUserGroup', 'my-user-group-id');
```

## Basic Usage for serverless cache

Setup required properties and create:

```python
declare const vpc: ec2.Vpc;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  vpc,
  majorEngineVersion: MajorVersion.VER_8,
});
```

### Connecting to serverless cache

To control who can access the serverless cache by the security groups, use the `.connections` attribute.

The serverless cache has a default port `6379`.

This example allows an EC2 instance to connect to the serverless cache:

```python
declare const serverlessCache: ServerlessCache;
declare const instance: ec2.Instance;

// allow the EC2 instance to connect to serverless cache on default port 6379
serverlessCache.connections.allowDefaultPortFrom(instance);
```

The endpoint and the port to access your serverless cache will be available as the `.endpointAddress` and `.endpointPort` attributes:

```python
declare const serverlessCache: ServerlessCache;

const endpointAddress = serverlessCache.endpointAddress;
const endpointPort = serverlessCache.endpointPort;
```

### Cache usage limits

You can choose to configure a maximum usage on both cache data storage and ECPU/second for your cache to control cache costs.
Doing so will ensure that your cache usage never exceeds the configured maximum.

For more infomation, see [Setting scaling limits to manage costs](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Scaling.html#Pre-Scaling).

```python
declare const vpc: ec2.Vpc;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  vpc,
  cacheUsageLimits: {
    // cache data storage limits (GB)
    dataStorage: DataStorage.gb({ minimum: 1, maximum: 5000 }), // minimum: 1GB, maximum: 5000GB
    // ECPU limits (ECPU/second)
    ecpuPerSecond: ECPUPerSecond.of({ minimum: 1000, maximum: 15000000 }), // minimum: 1000, maximum: 15000000
  },
});
```

### Snapshots and restore

You can enable automatic backups for serverless cache.
When automatic backups are enabled, ElastiCache creates a backup of the cache on a daily basis.

Also you can set the backup window for any time when it's most convenient.
If you don't specify a backup window, ElastiCache assigns one automatically.

For more information, see [Scheduling automatic backups](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/backups-automatic.html).

To enable automatic backups, set the `snapshotRetentionLimit` property. You can also specify the snapshot creation time by setting `dailySnapshotTime` property:

```python
declare const vpc: ec2.Vpc;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  // enable automatic backups and set the retention period to 6 days
  snapshotRetentionLimit: 6,
  // set the backup window to 12:00 AM UTC
  dailySnapshotTime: new DailySnapshotTime({ hour: 12, minute: 0 }),
  vpc,
  majorEngineVersion: MajorVersion.VER_8,
});
```

You can create a final backup by setting `finalSnapshotName` property.

```python
declare const vpc: ec2.Vpc;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  // set the final snapshot name
  finalSnapshotName: 'my-finalsnapshot',
  vpc,
  majorEngineVersion: MajorVersion.VER_8,
});
```

You can restore from snapshots by setting snapshot ARNs to `snapshotArnsToRestore` property:

```python
declare const vpc: ec2.Vpc;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  // set the snapshot to restore
  snapshotArnsToRestore: ['arn:aws:elasticache:us-east-1:123456789012:serverlesscachesnapshot:my-final-snapshot'],
  vpc,
  majorEngineVersion: MajorVersion.VER_8,
});
```

### Customer Managed Key for encryption at rest

ElastiCache supports symmetric Customer Managed key (CMK) for encryption at rest.

For more information, see [Using customer managed keys from AWS KMS](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/at-rest-encryption.html#using-customer-managed-keys-for-elasticache-security).

To use CMK, set your CMK to the `kmsKey` property:

```python
declare const kmsKey: kms.Key;

const serverlessCache = new ServerlessCache(this, 'ServerlessCache', {
  engine: Engine.VALKEY,
  serverlessCacheName: 'my-serverless-cache',
  vpc,
  // set Customer Managed Key
  kmsKey,
  majorEngineVersion: MajorVersion.VER_8,
});
```

### Metrics

You can monitor your serverless cache using CloudWatch Metrics via the `metric` method.

For more information about serverless cache metrics, see [Serverless metrics and events for Valkey and Redis OSS](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/serverless-metrics-events-redis.html) and [Serverless metrics and events for Memcached](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/serverless-metrics-events.memcached.html).

```python
declare const serverlessCache: ServerlessCache;

// The 5 minutes average of the total number of successful read-only key lookups in the cache over 5 minutes.
const cacheHits = serverlessCache.metric('CacheHits', { statistic: 'sum' });

// The 5 minutes average of the total number of bytes used by the data stored in your cache over 5 minutes.
const bytesUsedForCache = serverlessCache.metricBytesUsedForCache();

// The 5 minutes average of the total number of ElastiCacheProcessingUnits (ECPUs) consumed by the requests executed on your cache.
const elastiCacheProcessingUnits = serverlessCache.metricElastiCacheProcessingUnits();

// Create an alarm for ECPUs.
elastiCacheProcessingUnits.createAlarm(this, 'ElastiCacheProcessingUnitsAlarm', {
  threshold: 50,
  evaluationPeriods: 1,
});
```

### Import an existing serverless cache

To import an existing ServerlessCache, use the `ServerlessCache.fromServerlessCacheAttributes` method:

```python
declare const vpc: ec2.Vpc;
declare const securityGroup: ec2.SecurityGroup;

const importedServerlessCache = ServerlessCache.fromServerlessCacheAttributes(this, 'ImportedServerlessCache', {
  serverlessCacheName: 'my-serverless-cache',
  securityGroups: [securityGroup],
  endpointAddress: 'my-serverless-cache.endpoint.com',
  endpointPort: 6379,
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
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_elasticache as _aws_cdk_aws_elasticache_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.BaseUserProps",
    jsii_struct_bases=[],
    name_mapping={"access_string": "accessString", "user_id": "userId"},
)
class BaseUserProps:
    def __init__(
        self,
        *,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for all user types.

        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95423522f78f1936df311c0dd9f42a1d89e036b84252a3acc8269168d8de63fa)
            check_type(argname="argument access_string", value=access_string, expected_type=type_hints["access_string"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_string is not None:
            self._values["access_string"] = access_string
        if user_id is not None:
            self._values["user_id"] = user_id

    @builtins.property
    def access_string(self) -> typing.Optional[builtins.str]:
        '''Access permissions string used for this user.

        :default: - 'off -@all'

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html#Access-string
        '''
        result = self._values.get("access_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the user.

        Must consist only of alphanumeric characters or hyphens, with the first character as a letter.
        Cannot end with a hyphen or contain two consecutive hyphens.

        :default: - auto generated
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.CacheUsageLimits",
    jsii_struct_bases=[],
    name_mapping={"data_storage": "dataStorage", "ecpu_per_second": "ecpuPerSecond"},
)
class CacheUsageLimits:
    def __init__(
        self,
        *,
        data_storage: typing.Optional["DataStorage"] = None,
        ecpu_per_second: typing.Optional["ECPUPerSecond"] = None,
    ) -> None:
        '''The usage limits for storage and ElastiCache Processing Units for the cache.

        :param data_storage: The data storage limit. Default: - no limits
        :param ecpu_per_second: The configuration for the number of ElastiCache Processing Units (ECPU) the cache can consume per second. Default: - no limits
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1267ddaa74bdea17859fae2f17caf548444afe350ce9bf1ea6560ec5357c018)
            check_type(argname="argument data_storage", value=data_storage, expected_type=type_hints["data_storage"])
            check_type(argname="argument ecpu_per_second", value=ecpu_per_second, expected_type=type_hints["ecpu_per_second"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if data_storage is not None:
            self._values["data_storage"] = data_storage
        if ecpu_per_second is not None:
            self._values["ecpu_per_second"] = ecpu_per_second

    @builtins.property
    def data_storage(self) -> typing.Optional["DataStorage"]:
        '''The data storage limit.

        :default: - no limits
        '''
        result = self._values.get("data_storage")
        return typing.cast(typing.Optional["DataStorage"], result)

    @builtins.property
    def ecpu_per_second(self) -> typing.Optional["ECPUPerSecond"]:
        '''The configuration for the number of ElastiCache Processing Units (ECPU) the cache can consume per second.

        :default: - no limits
        '''
        result = self._values.get("ecpu_per_second")
        return typing.cast(typing.Optional["ECPUPerSecond"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CacheUsageLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DailySnapshotTime(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.DailySnapshotTime",
):
    '''Class for scheduling a daily snapshot time.'''

    def __init__(self, *, hour: jsii.Number, minute: jsii.Number) -> None:
        '''
        :param hour: The hour of the day (from 0-23) for snapshot starts.
        :param minute: The minute of the hour (from 0-59) for snapshot starts.
        '''
        props = DailySnapshotTimeProps(hour=hour, minute=minute)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toTimestamp")
    def to_timestamp(self) -> builtins.str:
        '''Converts an hour, and minute into HH:MM string.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toTimestamp", []))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.DailySnapshotTimeProps",
    jsii_struct_bases=[],
    name_mapping={"hour": "hour", "minute": "minute"},
)
class DailySnapshotTimeProps:
    def __init__(self, *, hour: jsii.Number, minute: jsii.Number) -> None:
        '''Properties required for setting up a daily snapshot time.

        :param hour: The hour of the day (from 0-23) for snapshot starts.
        :param minute: The minute of the hour (from 0-59) for snapshot starts.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8e50e073a334e7716ce72644a1b96741989d57781f9d8a72312e3cd63db8186)
            check_type(argname="argument hour", value=hour, expected_type=type_hints["hour"])
            check_type(argname="argument minute", value=minute, expected_type=type_hints["minute"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hour": hour,
            "minute": minute,
        }

    @builtins.property
    def hour(self) -> jsii.Number:
        '''The hour of the day (from 0-23) for snapshot starts.'''
        result = self._values.get("hour")
        assert result is not None, "Required property 'hour' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def minute(self) -> jsii.Number:
        '''The minute of the hour (from 0-59) for snapshot starts.'''
        result = self._values.get("minute")
        assert result is not None, "Required property 'minute' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DailySnapshotTimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataStorage(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.DataStorage",
):
    '''The data storage limit.'''

    @jsii.member(jsii_name="gb")
    @builtins.classmethod
    def gb(
        cls,
        *,
        maximum: typing.Optional[jsii.Number] = None,
        minimum: typing.Optional[jsii.Number] = None,
    ) -> "DataStorage":
        '''Creates data storage settings with gigabytes as the unit.

        :param maximum: The upper limit for data storage the cache is set to use. Default: - no upper limit
        :param minimum: The lower limit for data storage the cache is set to use. Default: - no lower limit
        '''
        options = DataStorageOptions(maximum=maximum, minimum=minimum)

        return typing.cast("DataStorage", jsii.sinvoke(cls, "gb", [options]))

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> "StorageUnit":
        '''The unit of the storage sizes.'''
        return typing.cast("StorageUnit", jsii.get(self, "unit"))

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> typing.Optional[jsii.Number]:
        '''The upper limit for data storage the cache is set to use.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximum"))

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> typing.Optional[jsii.Number]:
        '''The lower limit for data storage the cache is set to use.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimum"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.DataStorageOptions",
    jsii_struct_bases=[],
    name_mapping={"maximum": "maximum", "minimum": "minimum"},
)
class DataStorageOptions:
    def __init__(
        self,
        *,
        maximum: typing.Optional[jsii.Number] = None,
        minimum: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Interface for configuring data storage limits.

        :param maximum: The upper limit for data storage the cache is set to use. Default: - no upper limit
        :param minimum: The lower limit for data storage the cache is set to use. Default: - no lower limit
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__158122e160f6c28621de63155cf453fa40dd0f89ee2bed84d62ccb6cf9ff37b6)
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if maximum is not None:
            self._values["maximum"] = maximum
        if minimum is not None:
            self._values["minimum"] = minimum

    @builtins.property
    def maximum(self) -> typing.Optional[jsii.Number]:
        '''The upper limit for data storage the cache is set to use.

        :default: - no upper limit
        '''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minimum(self) -> typing.Optional[jsii.Number]:
        '''The lower limit for data storage the cache is set to use.

        :default: - no lower limit
        '''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataStorageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ECPUPerSecond(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.ECPUPerSecond",
):
    '''The configuration for the number of ElastiCache Processing Units (ECPU) the cache can consume per second.'''

    @jsii.member(jsii_name="of")
    @builtins.classmethod
    def of(
        cls,
        *,
        maximum: typing.Optional[jsii.Number] = None,
        minimum: typing.Optional[jsii.Number] = None,
    ) -> "ECPUPerSecond":
        '''Creates ECPU per second settings.

        :param maximum: The configuration for the maximum number of ECPUs the cache can consume per second. Default: - no maximum configuration
        :param minimum: The configuration for the minimum number of ECPUs the cache should be able consume per second. Default: - no minimum configuration
        '''
        options = ECPUPerSecondOptions(maximum=maximum, minimum=minimum)

        return typing.cast("ECPUPerSecond", jsii.sinvoke(cls, "of", [options]))

    @builtins.property
    @jsii.member(jsii_name="maximum")
    def maximum(self) -> typing.Optional[jsii.Number]:
        '''The configuration for the maximum number of ECPUs the cache can consume per second.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maximum"))

    @builtins.property
    @jsii.member(jsii_name="minimum")
    def minimum(self) -> typing.Optional[jsii.Number]:
        '''The configuration for the minimum number of ECPUs the cache should be able consume per second.'''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minimum"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.ECPUPerSecondOptions",
    jsii_struct_bases=[],
    name_mapping={"maximum": "maximum", "minimum": "minimum"},
)
class ECPUPerSecondOptions:
    def __init__(
        self,
        *,
        maximum: typing.Optional[jsii.Number] = None,
        minimum: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Interface for configuring ECPU per second limits.

        :param maximum: The configuration for the maximum number of ECPUs the cache can consume per second. Default: - no maximum configuration
        :param minimum: The configuration for the minimum number of ECPUs the cache should be able consume per second. Default: - no minimum configuration
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7616468ed377c166fe3859c5972190b8a17b6cb5dc1e64652140217471d0a63d)
            check_type(argname="argument maximum", value=maximum, expected_type=type_hints["maximum"])
            check_type(argname="argument minimum", value=minimum, expected_type=type_hints["minimum"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if maximum is not None:
            self._values["maximum"] = maximum
        if minimum is not None:
            self._values["minimum"] = minimum

    @builtins.property
    def maximum(self) -> typing.Optional[jsii.Number]:
        '''The configuration for the maximum number of ECPUs the cache can consume per second.

        :default: - no maximum configuration
        '''
        result = self._values.get("maximum")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minimum(self) -> typing.Optional[jsii.Number]:
        '''The configuration for the minimum number of ECPUs the cache should be able consume per second.

        :default: - no minimum configuration
        '''
        result = self._values.get("minimum")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ECPUPerSecondOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@open-constructs/aws-cdk.aws_elasticache.Engine")
class Engine(enum.Enum):
    '''The engine the cache uses.'''

    REDIS = "REDIS"
    '''Redis.'''
    VALKEY = "VALKEY"
    '''Valkey.'''
    MEMCACHED = "MEMCACHED"
    '''Memcached.'''


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_elasticache.IServerlessCache")
class IServerlessCache(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''Interface for an ElastiCache Serverless Cache.'''

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        '''The DNS hostname of the cache node.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="endpointPort")
    def endpoint_port(self) -> jsii.Number:
        '''The port number that the cache engine is listening on.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverlessCacheArn")
    def serverless_cache_arn(self) -> builtins.str:
        '''The serverless cache ARN.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="serverlessCacheName")
    def serverless_cache_name(self) -> builtins.str:
        '''The serverless cache name.'''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity the specified actions.

        :param grantee: -
        :param actions: -
        '''
        ...

    @jsii.member(jsii_name="grantConnect")
    def grant_connect(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity connection access to the cache.

        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''Create a CloudWatch metric.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        ...


class _IServerlessCacheProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''Interface for an ElastiCache Serverless Cache.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_elasticache.IServerlessCache"

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        '''The DNS hostname of the cache node.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointAddress"))

    @builtins.property
    @jsii.member(jsii_name="endpointPort")
    def endpoint_port(self) -> jsii.Number:
        '''The port number that the cache engine is listening on.

        :attribute: true
        '''
        return typing.cast(jsii.Number, jsii.get(self, "endpointPort"))

    @builtins.property
    @jsii.member(jsii_name="serverlessCacheArn")
    def serverless_cache_arn(self) -> builtins.str:
        '''The serverless cache ARN.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "serverlessCacheArn"))

    @builtins.property
    @jsii.member(jsii_name="serverlessCacheName")
    def serverless_cache_name(self) -> builtins.str:
        '''The serverless cache name.'''
        return typing.cast(builtins.str, jsii.get(self, "serverlessCacheName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity the specified actions.

        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0ea0fdfd2c2dad297f64f2d4a7504070e78b74eabdf909ed119e19c03d42ba3)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantConnect")
    def grant_connect(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity connection access to the cache.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04e747b96e64b838bbc682687ed210c1907d3cd262323199d91114c7367436bf)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantConnect", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''Create a CloudWatch metric.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__044fc0ffc360c836f6123367db6907e720bf67ac5c347b762b3a6fc7fbd534f5)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IServerlessCache).__jsii_proxy_class__ = lambda : _IServerlessCacheProxy


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_elasticache.IUser")
class IUser(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''Interface for a User.'''

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''The ARN of the user.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        ...


class _IUserProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''Interface for a User.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_elasticache.IUser"

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''The ARN of the user.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUser).__jsii_proxy_class__ = lambda : _IUserProxy


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_elasticache.IUserGroup")
class IUserGroup(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''Interface for a User Group.'''

    @builtins.property
    @jsii.member(jsii_name="userGroupArn")
    def user_group_arn(self) -> builtins.str:
        '''The ARN of the user group.

        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="userGroupId")
    def user_group_id(self) -> builtins.str:
        '''The ID of the user group.'''
        ...


class _IUserGroupProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''Interface for a User Group.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_elasticache.IUserGroup"

    @builtins.property
    @jsii.member(jsii_name="userGroupArn")
    def user_group_arn(self) -> builtins.str:
        '''The ARN of the user group.

        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "userGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="userGroupId")
    def user_group_id(self) -> builtins.str:
        '''The ID of the user group.'''
        return typing.cast(builtins.str, jsii.get(self, "userGroupId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUserGroup).__jsii_proxy_class__ = lambda : _IUserGroupProxy


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.IamUserProps",
    jsii_struct_bases=[BaseUserProps],
    name_mapping={"access_string": "accessString", "user_id": "userId"},
)
class IamUserProps(BaseUserProps):
    def __init__(
        self,
        *,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for IAM-enabled users.

        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d108ca85b0b400b05a0733e0b2c23c62283eaf5b667b0c781675fdda7791b797)
            check_type(argname="argument access_string", value=access_string, expected_type=type_hints["access_string"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_string is not None:
            self._values["access_string"] = access_string
        if user_id is not None:
            self._values["user_id"] = user_id

    @builtins.property
    def access_string(self) -> typing.Optional[builtins.str]:
        '''Access permissions string used for this user.

        :default: - 'off -@all'

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html#Access-string
        '''
        result = self._values.get("access_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the user.

        Must consist only of alphanumeric characters or hyphens, with the first character as a letter.
        Cannot end with a hyphen or contain two consecutive hyphens.

        :default: - auto generated
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IamUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@open-constructs/aws-cdk.aws_elasticache.MajorVersion")
class MajorVersion(enum.Enum):
    '''The version number of the engine the serverless cache is compatible with.'''

    VER_7 = "VER_7"
    '''Version 7.'''
    VER_8 = "VER_8"
    '''Version 8.'''


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.NoPasswordRequiredUserProps",
    jsii_struct_bases=[BaseUserProps],
    name_mapping={
        "access_string": "accessString",
        "user_id": "userId",
        "user_name": "userName",
    },
)
class NoPasswordRequiredUserProps(BaseUserProps):
    def __init__(
        self,
        *,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for no password required users.

        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        :param user_name: The username of the user. Default: - same as userId
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57e652922557b68eec0c3d53257cece9168ce2cba1bb0b497833871215a1789f)
            check_type(argname="argument access_string", value=access_string, expected_type=type_hints["access_string"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_string is not None:
            self._values["access_string"] = access_string
        if user_id is not None:
            self._values["user_id"] = user_id
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def access_string(self) -> typing.Optional[builtins.str]:
        '''Access permissions string used for this user.

        :default: - 'off -@all'

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html#Access-string
        '''
        result = self._values.get("access_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the user.

        Must consist only of alphanumeric characters or hyphens, with the first character as a letter.
        Cannot end with a hyphen or contain two consecutive hyphens.

        :default: - auto generated
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''The username of the user.

        :default: - same as userId
        '''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NoPasswordRequiredUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.NoPasswordUserAttributes",
    jsii_struct_bases=[],
    name_mapping={"user_id": "userId", "user_name": "userName"},
)
class NoPasswordUserAttributes:
    def __init__(self, *, user_id: builtins.str, user_name: builtins.str) -> None:
        '''Attributes for importing a no password required user.

        :param user_id: The ID of the user.
        :param user_name: The name of the user.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8c718300c410961e5f79f5db8084f6ecbc3bf7b6dc2718807449e74ecc97d0b)
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_id": user_id,
            "user_name": user_name,
        }

    @builtins.property
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NoPasswordUserAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.PasswordUserAttributes",
    jsii_struct_bases=[],
    name_mapping={"user_id": "userId", "user_name": "userName"},
)
class PasswordUserAttributes:
    def __init__(self, *, user_id: builtins.str, user_name: builtins.str) -> None:
        '''Attributes for importing a password-authenticated user.

        :param user_id: The ID of the user.
        :param user_name: The name of the user.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab950acbb17cd7dc8c8724d4ca67d7aedc6a1d9aa495fbebd7316e25d019698b)
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_id": user_id,
            "user_name": user_name,
        }

    @builtins.property
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        result = self._values.get("user_id")
        assert result is not None, "Required property 'user_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PasswordUserAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.PasswordUserProps",
    jsii_struct_bases=[BaseUserProps],
    name_mapping={
        "access_string": "accessString",
        "user_id": "userId",
        "passwords": "passwords",
        "user_name": "userName",
    },
)
class PasswordUserProps(BaseUserProps):
    def __init__(
        self,
        *,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
        passwords: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.SecretValue]] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for password-authenticated users.

        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        :param passwords: Passwords used for this user account. You can create up to two passwords for each user. Default: - automatically generate a password for the user
        :param user_name: The username of the user. Default: - same as userId
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__548df44ef8814d223dac74d5fa90fa7c65bd5a5f8ab0108667de332ec09d4574)
            check_type(argname="argument access_string", value=access_string, expected_type=type_hints["access_string"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
            check_type(argname="argument passwords", value=passwords, expected_type=type_hints["passwords"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_string is not None:
            self._values["access_string"] = access_string
        if user_id is not None:
            self._values["user_id"] = user_id
        if passwords is not None:
            self._values["passwords"] = passwords
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def access_string(self) -> typing.Optional[builtins.str]:
        '''Access permissions string used for this user.

        :default: - 'off -@all'

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Clusters.RBAC.html#Access-string
        '''
        result = self._values.get("access_string")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the user.

        Must consist only of alphanumeric characters or hyphens, with the first character as a letter.
        Cannot end with a hyphen or contain two consecutive hyphens.

        :default: - auto generated
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passwords(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.SecretValue]]:
        '''Passwords used for this user account.

        You can create up to two passwords for each user.

        :default: - automatically generate a password for the user
        '''
        result = self._values.get("passwords")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.SecretValue]], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''The username of the user.

        :default: - same as userId
        '''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PasswordUserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IServerlessCache)
class ServerlessCache(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.ServerlessCache",
):
    '''Represents an ElastiCache Serverless Cache construct in AWS CDK.

    Example::

        declare const vpc: aws_ec2.IVpc;
        
        const serverlessCache = new ServerlessCache(
          stack,
          'ServerlessCache',
          {
            serverlessCacheName: 'my-serverlessCache',
            engine: Engine.VALKEY,
            vpc,
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: Engine,
        major_engine_version: MajorVersion,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cache_usage_limits: typing.Optional[typing.Union[CacheUsageLimits, typing.Dict[builtins.str, typing.Any]]] = None,
        daily_snapshot_time: typing.Optional[DailySnapshotTime] = None,
        description: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_cache_name: typing.Optional[builtins.str] = None,
        snapshot_arns_to_restore: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        user_group: typing.Optional[IUserGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param engine: The engine the serverless cache is compatible with.
        :param major_engine_version: The version number of the engine the serverless cache is compatible with.
        :param vpc: The VPC to place the serverless cache in.
        :param cache_usage_limits: The usage limits for storage and ElastiCache Processing Units for the cache. Default: - no limits.
        :param daily_snapshot_time: The daily time when a cache snapshot will be created. This property must be set along with ``snapshotRetentionLimit``. Default: - ElastiCache automatically assigns the backup window if `snapshotRetentionLimit` is set. Otherwise, no snapshots are taken.
        :param description: A description of the serverless cache. The description can have up to 255 characters and must not contain < and > characters. Default: - no description
        :param final_snapshot_name: The name of the final snapshot taken of a cache before the cache is deleted. Default: - no final snapshot taken
        :param kms_key: The Customer Managed Key that is used to encrypt data at rest in the serverless cache. Default: - use AWS managed key
        :param security_groups: The security groups to associate with the serverless cache. Default: - a new security group is created
        :param serverless_cache_name: The unique identifier of the serverless cache. The name can have up to 40 characters, and must not contain spaces. Default: - auto generate
        :param snapshot_arns_to_restore: The ARN of the snapshot from which to restore data into the new cache. Default: - not restored
        :param snapshot_retention_limit: The number of serverless cache snapshots the system will retain. To enable automatic backups, this property must be set. `snapshotRetentionLimit` must be between 1 and 35. Default: - no automatic backups
        :param user_group: The user group associated with the serverless cache. Available for Valkey and Redis OSS only. Default: - no user group associated
        :param vpc_subnets: Where to place the serverless cache within the VPC. Default: - private subnets
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cd7bab43e94d190eb3564349203e01d3404e888aa2ee04abd9fd4594bb8e997)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ServerlessCacheProps(
            engine=engine,
            major_engine_version=major_engine_version,
            vpc=vpc,
            cache_usage_limits=cache_usage_limits,
            daily_snapshot_time=daily_snapshot_time,
            description=description,
            final_snapshot_name=final_snapshot_name,
            kms_key=kms_key,
            security_groups=security_groups,
            serverless_cache_name=serverless_cache_name,
            snapshot_arns_to_restore=snapshot_arns_to_restore,
            snapshot_retention_limit=snapshot_retention_limit,
            user_group=user_group,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromServerlessCacheAttributes")
    @builtins.classmethod
    def from_serverless_cache_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        endpoint_address: builtins.str,
        endpoint_port: jsii.Number,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        serverless_cache_name: builtins.str,
    ) -> IServerlessCache:
        '''Imports an existing ServerlessCache from attributes.

        :param scope: -
        :param id: -
        :param endpoint_address: The DNS hostname of the cache node.
        :param endpoint_port: The port number that the cache engine is listening on.
        :param security_groups: The security groups to associate with the serverless cache.
        :param serverless_cache_name: The serverless cache name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0062cca0f4d962246da0882ccbd3c69a7ee7ea17db385df3a222f7acc9094656)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = ServerlessCacheAttributes(
            endpoint_address=endpoint_address,
            endpoint_port=endpoint_port,
            security_groups=security_groups,
            serverless_cache_name=serverless_cache_name,
        )

        return typing.cast(IServerlessCache, jsii.sinvoke(cls, "fromServerlessCacheAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        serverless_cache_name: builtins.str,
        cache_usage_limits: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache.CacheUsageLimitsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        daily_snapshot_time: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        endpoint: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache.EndpointProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key_id: typing.Optional[builtins.str] = None,
        major_engine_version: typing.Optional[builtins.str] = None,
        reader_endpoint: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache.EndpointProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns_to_restore: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        user_group_id: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache:
        '''
        :param scope: -
        :param id: -
        :param engine: The engine the serverless cache is compatible with.
        :param serverless_cache_name: The unique identifier of the serverless cache.
        :param cache_usage_limits: The cache usage limit for the serverless cache.
        :param daily_snapshot_time: The daily time that a cache snapshot will be created. Default is NULL, i.e. snapshots will not be created at a specific time on a daily basis. Available for Valkey, Redis OSS, and Serverless Memcached only.
        :param description: A description of the serverless cache.
        :param endpoint: Represents the information required for client programs to connect to a cache node. This value is read-only.
        :param final_snapshot_name: The name of the final snapshot taken of a cache before the cache is deleted.
        :param kms_key_id: The ID of the AWS Key Management Service (KMS) key that is used to encrypt data at rest in the serverless cache.
        :param major_engine_version: The version number of the engine the serverless cache is compatible with.
        :param reader_endpoint: Represents the information required for client programs to connect to a cache node. This value is read-only.
        :param security_group_ids: The IDs of the EC2 security groups associated with the serverless cache.
        :param snapshot_arns_to_restore: The ARN of the snapshot from which to restore data into the new cache.
        :param snapshot_retention_limit: The current setting for the number of serverless cache snapshots the system will retain. Available for Valkey, Redis OSS, and Serverless Memcached only.
        :param subnet_ids: If no subnet IDs are given and your VPC is in us-west-1, then ElastiCache will select 2 default subnets across AZs in your VPC. For all other Regions, if no subnet IDs are given then ElastiCache will select 3 default subnets across AZs in your default VPC.
        :param tags: A list of tags to be added to this resource.
        :param user_group_id: The identifier of the user group associated with the serverless cache. Available for Valkey and Redis OSS only. Default is NULL.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a781be3ceb64253fc0ebab200002288a985e17e5e14b1536dc960206d625e93b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCacheProps(
            engine=engine,
            serverless_cache_name=serverless_cache_name,
            cache_usage_limits=cache_usage_limits,
            daily_snapshot_time=daily_snapshot_time,
            description=description,
            endpoint=endpoint,
            final_snapshot_name=final_snapshot_name,
            kms_key_id=kms_key_id,
            major_engine_version=major_engine_version,
            reader_endpoint=reader_endpoint,
            security_group_ids=security_group_ids,
            snapshot_arns_to_restore=snapshot_arns_to_restore,
            snapshot_retention_limit=snapshot_retention_limit,
            subnet_ids=subnet_ids,
            tags=tags,
            user_group_id=user_group_id,
        )

        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache, jsii.invoke(self, "createResource", [scope, id, props]))

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
            type_hints = typing.get_type_hints(_typecheckingstub__5a33b2101d338886b43efbd5615460a5a35435d43ef9e42c7c4237f6392006c6)
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

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity the specified actions.

        :param grantee: the identity to be granted the actions.
        :param actions: the data-access actions.

        :see: https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticache.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92e8d6985d8eb526490f3620e9d23a9bac015f451f4328cb40ce72a5cf077290)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantConnect")
    def grant_connect(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Permits an IAM principal to perform connect to the serverless cache.

        Actions: Connect

        :param grantee: The principal to grant access to.

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth-iam.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b92b4f8cce12abba429cd7953d282190b4145dfd6faea452d0b1724d999e5f7)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantConnect", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''Create a CloudWatch metric for serverless cache.

        :param metric_name: name of the metric.
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/serverless-metrics-events.memcached.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f682a951d3028ca25cea497ed1ae48b69ddbd7ea809fd304b76749bc81ca9397)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBytesUsedForCache")
    def metric_bytes_used_for_cache(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''Metric for the total number of bytes used by the data stored in your cache.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricBytesUsedForCache", [props]))

    @jsii.member(jsii_name="metricElastiCacheProcessingUnits")
    def metric_elasti_cache_processing_units(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''Metric for the total number of ElastiCacheProcessingUnits (ECPUs) consumed by the requests executed on your cache.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :default: - average over 5 minutes
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricElastiCacheProcessingUnits", [props]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The connection object associated with the ElastiCache Serverless Cache.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="endpointAddress")
    def endpoint_address(self) -> builtins.str:
        '''The DNS hostname of the cache node.'''
        return typing.cast(builtins.str, jsii.get(self, "endpointAddress"))

    @builtins.property
    @jsii.member(jsii_name="endpointPort")
    def endpoint_port(self) -> jsii.Number:
        '''The port number that the cache engine is listening on.'''
        return typing.cast(jsii.Number, jsii.get(self, "endpointPort"))

    @builtins.property
    @jsii.member(jsii_name="serverlessCacheArn")
    def serverless_cache_arn(self) -> builtins.str:
        '''The serverless cache ARN.'''
        return typing.cast(builtins.str, jsii.get(self, "serverlessCacheArn"))

    @builtins.property
    @jsii.member(jsii_name="serverlessCacheName")
    def serverless_cache_name(self) -> builtins.str:
        '''The serverless cache name.'''
        return typing.cast(builtins.str, jsii.get(self, "serverlessCacheName"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.ServerlessCacheAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_address": "endpointAddress",
        "endpoint_port": "endpointPort",
        "security_groups": "securityGroups",
        "serverless_cache_name": "serverlessCacheName",
    },
)
class ServerlessCacheAttributes:
    def __init__(
        self,
        *,
        endpoint_address: builtins.str,
        endpoint_port: jsii.Number,
        security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
        serverless_cache_name: builtins.str,
    ) -> None:
        '''Attributes for importing an ElastiCache Serverless Cache.

        :param endpoint_address: The DNS hostname of the cache node.
        :param endpoint_port: The port number that the cache engine is listening on.
        :param security_groups: The security groups to associate with the serverless cache.
        :param serverless_cache_name: The serverless cache name.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__183b85098550ecaa16b726308dfe3455773324f58936c16d5a857beb932f8e10)
            check_type(argname="argument endpoint_address", value=endpoint_address, expected_type=type_hints["endpoint_address"])
            check_type(argname="argument endpoint_port", value=endpoint_port, expected_type=type_hints["endpoint_port"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument serverless_cache_name", value=serverless_cache_name, expected_type=type_hints["serverless_cache_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "endpoint_address": endpoint_address,
            "endpoint_port": endpoint_port,
            "security_groups": security_groups,
            "serverless_cache_name": serverless_cache_name,
        }

    @builtins.property
    def endpoint_address(self) -> builtins.str:
        '''The DNS hostname of the cache node.'''
        result = self._values.get("endpoint_address")
        assert result is not None, "Required property 'endpoint_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_port(self) -> jsii.Number:
        '''The port number that the cache engine is listening on.'''
        result = self._values.get("endpoint_port")
        assert result is not None, "Required property 'endpoint_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def security_groups(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''The security groups to associate with the serverless cache.'''
        result = self._values.get("security_groups")
        assert result is not None, "Required property 'security_groups' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def serverless_cache_name(self) -> builtins.str:
        '''The serverless cache name.'''
        result = self._values.get("serverless_cache_name")
        assert result is not None, "Required property 'serverless_cache_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessCacheAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.ServerlessCacheProps",
    jsii_struct_bases=[],
    name_mapping={
        "engine": "engine",
        "major_engine_version": "majorEngineVersion",
        "vpc": "vpc",
        "cache_usage_limits": "cacheUsageLimits",
        "daily_snapshot_time": "dailySnapshotTime",
        "description": "description",
        "final_snapshot_name": "finalSnapshotName",
        "kms_key": "kmsKey",
        "security_groups": "securityGroups",
        "serverless_cache_name": "serverlessCacheName",
        "snapshot_arns_to_restore": "snapshotArnsToRestore",
        "snapshot_retention_limit": "snapshotRetentionLimit",
        "user_group": "userGroup",
        "vpc_subnets": "vpcSubnets",
    },
)
class ServerlessCacheProps:
    def __init__(
        self,
        *,
        engine: Engine,
        major_engine_version: MajorVersion,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        cache_usage_limits: typing.Optional[typing.Union[CacheUsageLimits, typing.Dict[builtins.str, typing.Any]]] = None,
        daily_snapshot_time: typing.Optional[DailySnapshotTime] = None,
        description: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        serverless_cache_name: typing.Optional[builtins.str] = None,
        snapshot_arns_to_restore: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        user_group: typing.Optional[IUserGroup] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for defining an ElastiCache Serverless Cache.

        :param engine: The engine the serverless cache is compatible with.
        :param major_engine_version: The version number of the engine the serverless cache is compatible with.
        :param vpc: The VPC to place the serverless cache in.
        :param cache_usage_limits: The usage limits for storage and ElastiCache Processing Units for the cache. Default: - no limits.
        :param daily_snapshot_time: The daily time when a cache snapshot will be created. This property must be set along with ``snapshotRetentionLimit``. Default: - ElastiCache automatically assigns the backup window if `snapshotRetentionLimit` is set. Otherwise, no snapshots are taken.
        :param description: A description of the serverless cache. The description can have up to 255 characters and must not contain < and > characters. Default: - no description
        :param final_snapshot_name: The name of the final snapshot taken of a cache before the cache is deleted. Default: - no final snapshot taken
        :param kms_key: The Customer Managed Key that is used to encrypt data at rest in the serverless cache. Default: - use AWS managed key
        :param security_groups: The security groups to associate with the serverless cache. Default: - a new security group is created
        :param serverless_cache_name: The unique identifier of the serverless cache. The name can have up to 40 characters, and must not contain spaces. Default: - auto generate
        :param snapshot_arns_to_restore: The ARN of the snapshot from which to restore data into the new cache. Default: - not restored
        :param snapshot_retention_limit: The number of serverless cache snapshots the system will retain. To enable automatic backups, this property must be set. `snapshotRetentionLimit` must be between 1 and 35. Default: - no automatic backups
        :param user_group: The user group associated with the serverless cache. Available for Valkey and Redis OSS only. Default: - no user group associated
        :param vpc_subnets: Where to place the serverless cache within the VPC. Default: - private subnets
        '''
        if isinstance(cache_usage_limits, dict):
            cache_usage_limits = CacheUsageLimits(**cache_usage_limits)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13afb6e4d3b97e2636c8365f474edfda38bb05f84c3bf83e0524ee3b319847e1)
            check_type(argname="argument engine", value=engine, expected_type=type_hints["engine"])
            check_type(argname="argument major_engine_version", value=major_engine_version, expected_type=type_hints["major_engine_version"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument cache_usage_limits", value=cache_usage_limits, expected_type=type_hints["cache_usage_limits"])
            check_type(argname="argument daily_snapshot_time", value=daily_snapshot_time, expected_type=type_hints["daily_snapshot_time"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument final_snapshot_name", value=final_snapshot_name, expected_type=type_hints["final_snapshot_name"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument serverless_cache_name", value=serverless_cache_name, expected_type=type_hints["serverless_cache_name"])
            check_type(argname="argument snapshot_arns_to_restore", value=snapshot_arns_to_restore, expected_type=type_hints["snapshot_arns_to_restore"])
            check_type(argname="argument snapshot_retention_limit", value=snapshot_retention_limit, expected_type=type_hints["snapshot_retention_limit"])
            check_type(argname="argument user_group", value=user_group, expected_type=type_hints["user_group"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "engine": engine,
            "major_engine_version": major_engine_version,
            "vpc": vpc,
        }
        if cache_usage_limits is not None:
            self._values["cache_usage_limits"] = cache_usage_limits
        if daily_snapshot_time is not None:
            self._values["daily_snapshot_time"] = daily_snapshot_time
        if description is not None:
            self._values["description"] = description
        if final_snapshot_name is not None:
            self._values["final_snapshot_name"] = final_snapshot_name
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if serverless_cache_name is not None:
            self._values["serverless_cache_name"] = serverless_cache_name
        if snapshot_arns_to_restore is not None:
            self._values["snapshot_arns_to_restore"] = snapshot_arns_to_restore
        if snapshot_retention_limit is not None:
            self._values["snapshot_retention_limit"] = snapshot_retention_limit
        if user_group is not None:
            self._values["user_group"] = user_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def engine(self) -> Engine:
        '''The engine the serverless cache is compatible with.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(Engine, result)

    @builtins.property
    def major_engine_version(self) -> MajorVersion:
        '''The version number of the engine the serverless cache is compatible with.'''
        result = self._values.get("major_engine_version")
        assert result is not None, "Required property 'major_engine_version' is missing"
        return typing.cast(MajorVersion, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC to place the serverless cache in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def cache_usage_limits(self) -> typing.Optional[CacheUsageLimits]:
        '''The usage limits for storage and ElastiCache Processing Units for the cache.

        :default: - no limits.
        '''
        result = self._values.get("cache_usage_limits")
        return typing.cast(typing.Optional[CacheUsageLimits], result)

    @builtins.property
    def daily_snapshot_time(self) -> typing.Optional[DailySnapshotTime]:
        '''The daily time when a cache snapshot will be created.

        This property must be set along with ``snapshotRetentionLimit``.

        :default: - ElastiCache automatically assigns the backup window if `snapshotRetentionLimit` is set. Otherwise, no snapshots are taken.

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/backups-automatic.html
        '''
        result = self._values.get("daily_snapshot_time")
        return typing.cast(typing.Optional[DailySnapshotTime], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the serverless cache.

        The description can have up to 255 characters and must not contain < and > characters.

        :default: - no description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_name(self) -> typing.Optional[builtins.str]:
        '''The name of the final snapshot taken of a cache before the cache is deleted.

        :default: - no final snapshot taken
        '''
        result = self._values.get("final_snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The Customer Managed Key that is used to encrypt data at rest in the serverless cache.

        :default: - use AWS managed key
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The security groups to associate with the serverless cache.

        :default: - a new security group is created
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def serverless_cache_name(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of the serverless cache.

        The name can have up to 40 characters, and must not contain spaces.

        :default: - auto generate
        '''
        result = self._values.get("serverless_cache_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_arns_to_restore(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The ARN of the snapshot from which to restore data into the new cache.

        :default: - not restored
        '''
        result = self._values.get("snapshot_arns_to_restore")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        '''The number of serverless cache snapshots the system will retain. To enable automatic backups, this property must be set.

        ``snapshotRetentionLimit`` must be between 1 and 35.

        :default: - no automatic backups
        '''
        result = self._values.get("snapshot_retention_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_group(self) -> typing.Optional[IUserGroup]:
        '''The user group associated with the serverless cache.

        Available for Valkey and Redis OSS only.

        :default: - no user group associated
        '''
        result = self._values.get("user_group")
        return typing.cast(typing.Optional[IUserGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the serverless cache within the VPC.

        :default: - private subnets
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessCacheProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@open-constructs/aws-cdk.aws_elasticache.StorageUnit")
class StorageUnit(enum.Enum):
    '''Storage unit for data storage in ElastiCache Serverless.'''

    GB = "GB"
    '''Gigabytes.'''


@jsii.implements(IUserGroup)
class UserGroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.UserGroup",
):
    '''Represents a user group construct in AWS CDK.

    Example::

        declare const user: User;
        
        const userGroup = new UserGroup(
          stack,
          'UserGroup',
          {
             users: [user],
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        users: typing.Sequence[IUser],
        user_group_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param users: The list of User that belong to the user group. A user with the username ``default`` must be included in ``users``.
        :param user_group_id: The ID of the user group. `userGroupId` can have up to 40 characters. `userGroupId` must consist only of alphanumeric characters or hyphens, with the first character as a letter, and it can't end with a hyphen or contain two consecutive hyphens. Default: - auto generate
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb522721aba9db4e7665f911d7c8e85b39a141a109fdb488cd907c94c0ef3249)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UserGroupProps(users=users, user_group_id=user_group_id)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromUserGroupId")
    @builtins.classmethod
    def from_user_group_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        user_group_id: builtins.str,
    ) -> IUserGroup:
        '''Imports an existing user group from attributes.

        :param scope: -
        :param id: -
        :param user_group_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75b7171e7810d5cf3c5bfd24c34ed3de3919953402c52015e7c479344486ad02)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument user_group_id", value=user_group_id, expected_type=type_hints["user_group_id"])
        return typing.cast(IUserGroup, jsii.sinvoke(cls, "fromUserGroupId", [scope, id, user_group_id]))

    @jsii.member(jsii_name="addUser")
    def add_user(self, user: IUser) -> None:
        '''Adds a user to the user group.

        :param user: the user to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45449e93546e74d4bbd7339f16d7521b3bc6eca1ddc1f564ecbf973af2824878)
            check_type(argname="argument user", value=user, expected_type=type_hints["user"])
        return typing.cast(None, jsii.invoke(self, "addUser", [user]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        user_group_id: builtins.str,
        user_ids: typing.Sequence[builtins.str],
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_elasticache_ceddda9d.CfnUserGroup:
        '''
        :param scope: -
        :param id: -
        :param engine: The current supported values are valkey and redis.
        :param user_group_id: The ID of the user group.
        :param user_ids: The list of user IDs that belong to the user group. A user named ``default`` must be included.
        :param tags: The list of tags.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0d0676fcaac4c3a75c1fa91bea18ba669899a518df4d98fa2992a60f8544756)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_elasticache_ceddda9d.CfnUserGroupProps(
            engine=engine, user_group_id=user_group_id, user_ids=user_ids, tags=tags
        )

        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnUserGroup, jsii.invoke(self, "createResource", [scope, id, props]))

    @builtins.property
    @jsii.member(jsii_name="userGroupArn")
    def user_group_arn(self) -> builtins.str:
        '''The ARN of the user group.'''
        return typing.cast(builtins.str, jsii.get(self, "userGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="userGroupId")
    def user_group_id(self) -> builtins.str:
        '''The ID of the user group.'''
        return typing.cast(builtins.str, jsii.get(self, "userGroupId"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.UserGroupAttributes",
    jsii_struct_bases=[],
    name_mapping={"user_group_id": "userGroupId"},
)
class UserGroupAttributes:
    def __init__(self, *, user_group_id: builtins.str) -> None:
        '''Attributes for importing a User Group.

        :param user_group_id: The ID of the user group.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba15cb959ca538b1d4d1faebd265610f8d445b881a8565d0702f5209109c66ea)
            check_type(argname="argument user_group_id", value=user_group_id, expected_type=type_hints["user_group_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "user_group_id": user_group_id,
        }

    @builtins.property
    def user_group_id(self) -> builtins.str:
        '''The ID of the user group.'''
        result = self._values.get("user_group_id")
        assert result is not None, "Required property 'user_group_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserGroupAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.UserGroupProps",
    jsii_struct_bases=[],
    name_mapping={"users": "users", "user_group_id": "userGroupId"},
)
class UserGroupProps:
    def __init__(
        self,
        *,
        users: typing.Sequence[IUser],
        user_group_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a User Group.

        :param users: The list of User that belong to the user group. A user with the username ``default`` must be included in ``users``.
        :param user_group_id: The ID of the user group. `userGroupId` can have up to 40 characters. `userGroupId` must consist only of alphanumeric characters or hyphens, with the first character as a letter, and it can't end with a hyphen or contain two consecutive hyphens. Default: - auto generate
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__960e243b62c4e73ddb9ff931efe4fa149af4cc5615a4793134e3ba8f5fa591eb)
            check_type(argname="argument users", value=users, expected_type=type_hints["users"])
            check_type(argname="argument user_group_id", value=user_group_id, expected_type=type_hints["user_group_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "users": users,
        }
        if user_group_id is not None:
            self._values["user_group_id"] = user_group_id

    @builtins.property
    def users(self) -> typing.List[IUser]:
        '''The list of User that belong to the user group.

        A user with the username ``default`` must be included in ``users``.
        '''
        result = self._values.get("users")
        assert result is not None, "Required property 'users' is missing"
        return typing.cast(typing.List[IUser], result)

    @builtins.property
    def user_group_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the user group.

        ``userGroupId`` can have up to 40 characters.

        ``userGroupId`` must consist only of alphanumeric characters or hyphens,
        with the first character as a letter, and it can't end with a hyphen or contain two consecutive hyphens.

        :default: - auto generate
        '''
        result = self._values.get("user_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_elasticache.IIamUser")
class IIamUser(IUser, typing_extensions.Protocol):
    '''Interface for IAM-enabled users.'''

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant permissions to this user.

        :param grantee: -
        :param actions: -
        '''
        ...

    @jsii.member(jsii_name="grantConnect")
    def grant_connect(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant connect permissions to this user.

        :param grantee: -
        '''
        ...


class _IIamUserProxy(
    jsii.proxy_for(IUser), # type: ignore[misc]
):
    '''Interface for IAM-enabled users.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_elasticache.IIamUser"

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant permissions to this user.

        :param grantee: -
        :param actions: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f569aa9b7683dd9573ac4b42765783b61e08d7473e71da96b433d5834e839560)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantConnect")
    def grant_connect(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant connect permissions to this user.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85f743d6098104e0dd7813667770869bfeb9899ab93323db6a99fb3b37395bd8)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantConnect", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIamUser).__jsii_proxy_class__ = lambda : _IIamUserProxy


@jsii.interface(
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.INoPasswordRequiredUser"
)
class INoPasswordRequiredUser(IUser, typing_extensions.Protocol):
    '''Interface for no password required users.'''

    pass


class _INoPasswordRequiredUserProxy(
    jsii.proxy_for(IUser), # type: ignore[misc]
):
    '''Interface for no password required users.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_elasticache.INoPasswordRequiredUser"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, INoPasswordRequiredUser).__jsii_proxy_class__ = lambda : _INoPasswordRequiredUserProxy


@jsii.interface(jsii_type="@open-constructs/aws-cdk.aws_elasticache.IPasswordUser")
class IPasswordUser(IUser, typing_extensions.Protocol):
    '''Interface for password-authenticated users.'''

    pass


class _IPasswordUserProxy(
    jsii.proxy_for(IUser), # type: ignore[misc]
):
    '''Interface for password-authenticated users.'''

    __jsii_type__: typing.ClassVar[str] = "@open-constructs/aws-cdk.aws_elasticache.IPasswordUser"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPasswordUser).__jsii_proxy_class__ = lambda : _IPasswordUserProxy


@jsii.implements(IIamUser, IUser)
class IamUser(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.IamUser",
):
    '''Represents an IAM-enabled user construct in AWS CDK.

    Example::

        const user = new IamUser(
          stack,
          'User',
          {
            accessString: 'on ~* +@all',
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2ec51bfe8fb22fd5ae258412383098e9dd7c693a00c67623d0cc10dec044d79)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = IamUserProps(access_string=access_string, user_id=user_id)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromUserId")
    @builtins.classmethod
    def from_user_id(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        user_id: builtins.str,
    ) -> IIamUser:
        '''Imports an existing IAM-enabled user from userId.

        :param scope: -
        :param id: -
        :param user_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f85737bcf97a17cb13fab721df8d210b2a3a446e164a5095875eeece4834f69e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        return typing.cast(IIamUser, jsii.sinvoke(cls, "fromUserId", [scope, id, user_id]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        user_id: builtins.str,
        user_name: builtins.str,
        access_string: typing.Optional[builtins.str] = None,
        authentication_mode: typing.Any = None,
        no_password_required: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_elasticache_ceddda9d.CfnUser:
        '''
        :param scope: -
        :param id: -
        :param engine: The current supported value is redis.
        :param user_id: The ID of the user.
        :param user_name: The username of the user.
        :param access_string: Access permissions string used for this user.
        :param authentication_mode: Specifies the authentication mode to use. Below is an example of the possible JSON values:. Example:: { Passwords: ["*****", "******"] // If Type is password. }
        :param no_password_required: Indicates a password is not required for this user.
        :param passwords: Passwords used for this user. You can create up to two passwords for each user.
        :param tags: The list of tags.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e56ce19c60f7bfc0f87c26ea923e9a98f9077dbdd8494bae221ca2e08905e41)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_elasticache_ceddda9d.CfnUserProps(
            engine=engine,
            user_id=user_id,
            user_name=user_name,
            access_string=access_string,
            authentication_mode=authentication_mode,
            no_password_required=no_password_required,
            passwords=passwords,
            tags=tags,
        )

        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnUser, jsii.invoke(self, "createResource", [scope, id, props]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant the given identity the specified actions.

        :param grantee: the identity to be granted the actions.
        :param actions: the data-access actions.

        :see: https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticache.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d716fd7c24d8cc800a8de39ccfe5b41ebca5a2f1fc6ac69e329d670cbe261532)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantConnect")
    def grant_connect(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Permits an IAM principal to perform connect to the user.

        Actions: Connect

        :param grantee: The principal to grant access to.

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth-iam.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a53c3ae9265d8395642b35c9f37cbd504307b4181fd0aa67309b539702e7bfa)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantConnect", [grantee]))

    @jsii.member(jsii_name="renderAuthenticationMode")
    def _render_authentication_mode(self) -> typing.Any:
        '''Render authenticationMode property.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderAuthenticationMode", []))

    @jsii.member(jsii_name="renderUserName")
    def _render_user_name(self) -> builtins.str:
        '''For IAM-enabled ElastiCache users the username and user id properties must be identical.

        :see: https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/auth-iam.html
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderUserName", []))

    @jsii.member(jsii_name="validateUserId")
    def _validate_user_id(self, user_id: typing.Optional[builtins.str] = None) -> None:
        '''Validates user id.

        :param user_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76ee117fc3cfdef855da8452853668f6281aaecb98355b47edf5a1a4db026ef1)
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        return typing.cast(None, jsii.invoke(self, "validateUserId", [user_id]))

    @jsii.member(jsii_name="validateUserName")
    def _validate_user_name(
        self,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Validates username.

        :param user_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed28faa24c99ddb815e32ea0ef87911aab66b87a459e29bb208313f95c4ccd2)
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        return typing.cast(None, jsii.invoke(self, "validateUserName", [user_name]))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> BaseUserProps:
        return typing.cast(BaseUserProps, jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''The ARN of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userName"))


@jsii.implements(INoPasswordRequiredUser, IUser)
class NoPasswordRequiredUser(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.NoPasswordRequiredUser",
):
    '''Represents a no password required user construct in AWS CDK.

    Example::

        const user = new NoPasswordRequiredUser(
          stack,
          'User',
          {
            userName: 'my-user',
            accessString: 'on ~* +@all',
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        user_name: typing.Optional[builtins.str] = None,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user_name: The username of the user. Default: - same as userId
        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdb5d6847ff78aa5d12e269487c402508c496de9a1cfebddd8391318b0359434)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = NoPasswordRequiredUserProps(
            user_name=user_name, access_string=access_string, user_id=user_id
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromUserAttributes")
    @builtins.classmethod
    def from_user_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        user_id: builtins.str,
        user_name: builtins.str,
    ) -> INoPasswordRequiredUser:
        '''Imports an existing no password required user from attributes.

        :param scope: -
        :param id: -
        :param user_id: The ID of the user.
        :param user_name: The name of the user.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__104f06dadaf7f09806eb00fe92804b0a1f51b009b42bf6e9413a358d8d1e04ae)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = NoPasswordUserAttributes(user_id=user_id, user_name=user_name)

        return typing.cast(INoPasswordRequiredUser, jsii.sinvoke(cls, "fromUserAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        user_id: builtins.str,
        user_name: builtins.str,
        access_string: typing.Optional[builtins.str] = None,
        authentication_mode: typing.Any = None,
        no_password_required: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_elasticache_ceddda9d.CfnUser:
        '''
        :param scope: -
        :param id: -
        :param engine: The current supported value is redis.
        :param user_id: The ID of the user.
        :param user_name: The username of the user.
        :param access_string: Access permissions string used for this user.
        :param authentication_mode: Specifies the authentication mode to use. Below is an example of the possible JSON values:. Example:: { Passwords: ["*****", "******"] // If Type is password. }
        :param no_password_required: Indicates a password is not required for this user.
        :param passwords: Passwords used for this user. You can create up to two passwords for each user.
        :param tags: The list of tags.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24992cb56b8b5be69cfa4a3851c392ca1f579fc28093e757821bdaaa9f232f08)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_elasticache_ceddda9d.CfnUserProps(
            engine=engine,
            user_id=user_id,
            user_name=user_name,
            access_string=access_string,
            authentication_mode=authentication_mode,
            no_password_required=no_password_required,
            passwords=passwords,
            tags=tags,
        )

        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnUser, jsii.invoke(self, "createResource", [scope, id, props]))

    @jsii.member(jsii_name="renderAuthenticationMode")
    def _render_authentication_mode(self) -> typing.Any:
        '''Render authenticationMode property.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderAuthenticationMode", []))

    @jsii.member(jsii_name="renderUserName")
    def _render_user_name(self) -> builtins.str:
        '''Render userName property.'''
        return typing.cast(builtins.str, jsii.invoke(self, "renderUserName", []))

    @jsii.member(jsii_name="validateUserId")
    def _validate_user_id(self, user_id: typing.Optional[builtins.str] = None) -> None:
        '''Validates user id.

        :param user_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e13c82d1175dccd8b73ccc156a4c7e9a23dfa83fbea8c31fd8bfbcaf34bcc4e1)
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        return typing.cast(None, jsii.invoke(self, "validateUserId", [user_id]))

    @jsii.member(jsii_name="validateUserName")
    def _validate_user_name(
        self,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Validates username.

        :param user_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ae0b9c9e0312229b33fea03624d21fa11f91ec3369958333b7a86c7b85d9096)
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        return typing.cast(None, jsii.invoke(self, "validateUserName", [user_name]))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> BaseUserProps:
        return typing.cast(BaseUserProps, jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''The ARN of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userName"))


@jsii.implements(IPasswordUser, IUser)
class PasswordUser(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_elasticache.PasswordUser",
):
    '''Represents a password authentication user construct in AWS CDK.

    Example::

        const user = new PasswordUser(
          stack,
          'User',
          {
           passwords: [
             cdk.SecretValue.unsafePlainText('exampleUserPassword123'),
             cdk.SecretValue.unsafePlainText('anotherUserPassword123'),
           ],
          },
        );
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        passwords: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.SecretValue]] = None,
        user_name: typing.Optional[builtins.str] = None,
        access_string: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param passwords: Passwords used for this user account. You can create up to two passwords for each user. Default: - automatically generate a password for the user
        :param user_name: The username of the user. Default: - same as userId
        :param access_string: Access permissions string used for this user. Default: - 'off -@all'
        :param user_id: The ID of the user. Must consist only of alphanumeric characters or hyphens, with the first character as a letter. Cannot end with a hyphen or contain two consecutive hyphens. Default: - auto generated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d679775a8435bc9bbb7e2152dc68cbb0fe77a55a9d114fc28ca485ecebb0f23b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PasswordUserProps(
            passwords=passwords,
            user_name=user_name,
            access_string=access_string,
            user_id=user_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromUserAttributes")
    @builtins.classmethod
    def from_user_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        user_id: builtins.str,
        user_name: builtins.str,
    ) -> IPasswordUser:
        '''Imports an existing password authentication user from attributes.

        :param scope: -
        :param id: -
        :param user_id: The ID of the user.
        :param user_name: The name of the user.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfaebae61e8c9c9426cb55f9f6d1100d461f0eb64748c5a7bbe04f33b78974c4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = PasswordUserAttributes(user_id=user_id, user_name=user_name)

        return typing.cast(IPasswordUser, jsii.sinvoke(cls, "fromUserAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="createResource")
    def _create_resource(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        engine: builtins.str,
        user_id: builtins.str,
        user_name: builtins.str,
        access_string: typing.Optional[builtins.str] = None,
        authentication_mode: typing.Any = None,
        no_password_required: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
        passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_elasticache_ceddda9d.CfnUser:
        '''
        :param scope: -
        :param id: -
        :param engine: The current supported value is redis.
        :param user_id: The ID of the user.
        :param user_name: The username of the user.
        :param access_string: Access permissions string used for this user.
        :param authentication_mode: Specifies the authentication mode to use. Below is an example of the possible JSON values:. Example:: { Passwords: ["*****", "******"] // If Type is password. }
        :param no_password_required: Indicates a password is not required for this user.
        :param passwords: Passwords used for this user. You can create up to two passwords for each user.
        :param tags: The list of tags.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d41956157b26604e72eeb72000763c3989df98bc590a36876dfd6dc1e6a00666)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_elasticache_ceddda9d.CfnUserProps(
            engine=engine,
            user_id=user_id,
            user_name=user_name,
            access_string=access_string,
            authentication_mode=authentication_mode,
            no_password_required=no_password_required,
            passwords=passwords,
            tags=tags,
        )

        return typing.cast(_aws_cdk_aws_elasticache_ceddda9d.CfnUser, jsii.invoke(self, "createResource", [scope, id, props]))

    @jsii.member(jsii_name="renderAuthenticationMode")
    def _render_authentication_mode(self) -> typing.Any:
        '''Render authenticationMode property.'''
        return typing.cast(typing.Any, jsii.invoke(self, "renderAuthenticationMode", []))

    @jsii.member(jsii_name="renderUserName")
    def _render_user_name(self) -> builtins.str:
        '''Render userName property.'''
        return typing.cast(builtins.str, jsii.invoke(self, "renderUserName", []))

    @jsii.member(jsii_name="validateUserId")
    def _validate_user_id(self, user_id: typing.Optional[builtins.str] = None) -> None:
        '''Validates user id.

        :param user_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e03921dc83376ed9bdc53e7a43fb27a0e6571aaaae70da20b39a0d2d21d32c)
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        return typing.cast(None, jsii.invoke(self, "validateUserId", [user_id]))

    @jsii.member(jsii_name="validateUserName")
    def _validate_user_name(
        self,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Validates username.

        :param user_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4ec4d858a740a1725cb8f2a2dd013e734e3841e1de1db97e4c54ce27fea457)
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        return typing.cast(None, jsii.invoke(self, "validateUserName", [user_name]))

    @builtins.property
    @jsii.member(jsii_name="generatedSecret")
    def generated_secret(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''The secret containing the generated password.

        Throws an exception if ``passwords`` is provided in the props
        '''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "generatedSecret"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def _props(self) -> BaseUserProps:
        return typing.cast(BaseUserProps, jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        '''The ARN of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        '''The ID of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        '''The name of the user.'''
        return typing.cast(builtins.str, jsii.get(self, "userName"))


__all__ = [
    "BaseUserProps",
    "CacheUsageLimits",
    "DailySnapshotTime",
    "DailySnapshotTimeProps",
    "DataStorage",
    "DataStorageOptions",
    "ECPUPerSecond",
    "ECPUPerSecondOptions",
    "Engine",
    "IIamUser",
    "INoPasswordRequiredUser",
    "IPasswordUser",
    "IServerlessCache",
    "IUser",
    "IUserGroup",
    "IamUser",
    "IamUserProps",
    "MajorVersion",
    "NoPasswordRequiredUser",
    "NoPasswordRequiredUserProps",
    "NoPasswordUserAttributes",
    "PasswordUser",
    "PasswordUserAttributes",
    "PasswordUserProps",
    "ServerlessCache",
    "ServerlessCacheAttributes",
    "ServerlessCacheProps",
    "StorageUnit",
    "UserGroup",
    "UserGroupAttributes",
    "UserGroupProps",
]

publication.publish()

def _typecheckingstub__95423522f78f1936df311c0dd9f42a1d89e036b84252a3acc8269168d8de63fa(
    *,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1267ddaa74bdea17859fae2f17caf548444afe350ce9bf1ea6560ec5357c018(
    *,
    data_storage: typing.Optional[DataStorage] = None,
    ecpu_per_second: typing.Optional[ECPUPerSecond] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8e50e073a334e7716ce72644a1b96741989d57781f9d8a72312e3cd63db8186(
    *,
    hour: jsii.Number,
    minute: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__158122e160f6c28621de63155cf453fa40dd0f89ee2bed84d62ccb6cf9ff37b6(
    *,
    maximum: typing.Optional[jsii.Number] = None,
    minimum: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7616468ed377c166fe3859c5972190b8a17b6cb5dc1e64652140217471d0a63d(
    *,
    maximum: typing.Optional[jsii.Number] = None,
    minimum: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0ea0fdfd2c2dad297f64f2d4a7504070e78b74eabdf909ed119e19c03d42ba3(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04e747b96e64b838bbc682687ed210c1907d3cd262323199d91114c7367436bf(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__044fc0ffc360c836f6123367db6907e720bf67ac5c347b762b3a6fc7fbd534f5(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d108ca85b0b400b05a0733e0b2c23c62283eaf5b667b0c781675fdda7791b797(
    *,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57e652922557b68eec0c3d53257cece9168ce2cba1bb0b497833871215a1789f(
    *,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8c718300c410961e5f79f5db8084f6ecbc3bf7b6dc2718807449e74ecc97d0b(
    *,
    user_id: builtins.str,
    user_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab950acbb17cd7dc8c8724d4ca67d7aedc6a1d9aa495fbebd7316e25d019698b(
    *,
    user_id: builtins.str,
    user_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__548df44ef8814d223dac74d5fa90fa7c65bd5a5f8ab0108667de332ec09d4574(
    *,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
    passwords: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.SecretValue]] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cd7bab43e94d190eb3564349203e01d3404e888aa2ee04abd9fd4594bb8e997(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: Engine,
    major_engine_version: MajorVersion,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cache_usage_limits: typing.Optional[typing.Union[CacheUsageLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    daily_snapshot_time: typing.Optional[DailySnapshotTime] = None,
    description: typing.Optional[builtins.str] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_cache_name: typing.Optional[builtins.str] = None,
    snapshot_arns_to_restore: typing.Optional[typing.Sequence[builtins.str]] = None,
    snapshot_retention_limit: typing.Optional[jsii.Number] = None,
    user_group: typing.Optional[IUserGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0062cca0f4d962246da0882ccbd3c69a7ee7ea17db385df3a222f7acc9094656(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    endpoint_address: builtins.str,
    endpoint_port: jsii.Number,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    serverless_cache_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a781be3ceb64253fc0ebab200002288a985e17e5e14b1536dc960206d625e93b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: builtins.str,
    serverless_cache_name: builtins.str,
    cache_usage_limits: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache.CacheUsageLimitsProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    daily_snapshot_time: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    endpoint: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache.EndpointProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    kms_key_id: typing.Optional[builtins.str] = None,
    major_engine_version: typing.Optional[builtins.str] = None,
    reader_endpoint: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_elasticache_ceddda9d.CfnServerlessCache.EndpointProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    snapshot_arns_to_restore: typing.Optional[typing.Sequence[builtins.str]] = None,
    snapshot_retention_limit: typing.Optional[jsii.Number] = None,
    subnet_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    user_group_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a33b2101d338886b43efbd5615460a5a35435d43ef9e42c7c4237f6392006c6(
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

def _typecheckingstub__92e8d6985d8eb526490f3620e9d23a9bac015f451f4328cb40ce72a5cf077290(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b92b4f8cce12abba429cd7953d282190b4145dfd6faea452d0b1724d999e5f7(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f682a951d3028ca25cea497ed1ae48b69ddbd7ea809fd304b76749bc81ca9397(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__183b85098550ecaa16b726308dfe3455773324f58936c16d5a857beb932f8e10(
    *,
    endpoint_address: builtins.str,
    endpoint_port: jsii.Number,
    security_groups: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup],
    serverless_cache_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13afb6e4d3b97e2636c8365f474edfda38bb05f84c3bf83e0524ee3b319847e1(
    *,
    engine: Engine,
    major_engine_version: MajorVersion,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    cache_usage_limits: typing.Optional[typing.Union[CacheUsageLimits, typing.Dict[builtins.str, typing.Any]]] = None,
    daily_snapshot_time: typing.Optional[DailySnapshotTime] = None,
    description: typing.Optional[builtins.str] = None,
    final_snapshot_name: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    serverless_cache_name: typing.Optional[builtins.str] = None,
    snapshot_arns_to_restore: typing.Optional[typing.Sequence[builtins.str]] = None,
    snapshot_retention_limit: typing.Optional[jsii.Number] = None,
    user_group: typing.Optional[IUserGroup] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb522721aba9db4e7665f911d7c8e85b39a141a109fdb488cd907c94c0ef3249(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    users: typing.Sequence[IUser],
    user_group_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b7171e7810d5cf3c5bfd24c34ed3de3919953402c52015e7c479344486ad02(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    user_group_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45449e93546e74d4bbd7339f16d7521b3bc6eca1ddc1f564ecbf973af2824878(
    user: IUser,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0d0676fcaac4c3a75c1fa91bea18ba669899a518df4d98fa2992a60f8544756(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: builtins.str,
    user_group_id: builtins.str,
    user_ids: typing.Sequence[builtins.str],
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba15cb959ca538b1d4d1faebd265610f8d445b881a8565d0702f5209109c66ea(
    *,
    user_group_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__960e243b62c4e73ddb9ff931efe4fa149af4cc5615a4793134e3ba8f5fa591eb(
    *,
    users: typing.Sequence[IUser],
    user_group_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f569aa9b7683dd9573ac4b42765783b61e08d7473e71da96b433d5834e839560(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85f743d6098104e0dd7813667770869bfeb9899ab93323db6a99fb3b37395bd8(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2ec51bfe8fb22fd5ae258412383098e9dd7c693a00c67623d0cc10dec044d79(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f85737bcf97a17cb13fab721df8d210b2a3a446e164a5095875eeece4834f69e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    user_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e56ce19c60f7bfc0f87c26ea923e9a98f9077dbdd8494bae221ca2e08905e41(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: builtins.str,
    user_id: builtins.str,
    user_name: builtins.str,
    access_string: typing.Optional[builtins.str] = None,
    authentication_mode: typing.Any = None,
    no_password_required: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d716fd7c24d8cc800a8de39ccfe5b41ebca5a2f1fc6ac69e329d670cbe261532(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a53c3ae9265d8395642b35c9f37cbd504307b4181fd0aa67309b539702e7bfa(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76ee117fc3cfdef855da8452853668f6281aaecb98355b47edf5a1a4db026ef1(
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed28faa24c99ddb815e32ea0ef87911aab66b87a459e29bb208313f95c4ccd2(
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdb5d6847ff78aa5d12e269487c402508c496de9a1cfebddd8391318b0359434(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    user_name: typing.Optional[builtins.str] = None,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__104f06dadaf7f09806eb00fe92804b0a1f51b009b42bf6e9413a358d8d1e04ae(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    user_id: builtins.str,
    user_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24992cb56b8b5be69cfa4a3851c392ca1f579fc28093e757821bdaaa9f232f08(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: builtins.str,
    user_id: builtins.str,
    user_name: builtins.str,
    access_string: typing.Optional[builtins.str] = None,
    authentication_mode: typing.Any = None,
    no_password_required: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e13c82d1175dccd8b73ccc156a4c7e9a23dfa83fbea8c31fd8bfbcaf34bcc4e1(
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ae0b9c9e0312229b33fea03624d21fa11f91ec3369958333b7a86c7b85d9096(
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d679775a8435bc9bbb7e2152dc68cbb0fe77a55a9d114fc28ca485ecebb0f23b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    passwords: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.SecretValue]] = None,
    user_name: typing.Optional[builtins.str] = None,
    access_string: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfaebae61e8c9c9426cb55f9f6d1100d461f0eb64748c5a7bbe04f33b78974c4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    user_id: builtins.str,
    user_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d41956157b26604e72eeb72000763c3989df98bc590a36876dfd6dc1e6a00666(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    engine: builtins.str,
    user_id: builtins.str,
    user_name: builtins.str,
    access_string: typing.Optional[builtins.str] = None,
    authentication_mode: typing.Any = None,
    no_password_required: typing.Optional[typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable]] = None,
    passwords: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e03921dc83376ed9bdc53e7a43fb27a0e6571aaaae70da20b39a0d2d21d32c(
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4ec4d858a740a1725cb8f2a2dd013e734e3841e1de1db97e4c54ce27fea457(
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
