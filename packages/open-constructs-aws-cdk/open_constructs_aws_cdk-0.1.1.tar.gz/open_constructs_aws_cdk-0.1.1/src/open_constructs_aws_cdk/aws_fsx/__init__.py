r'''
Constructs for the AWS FSx service

# Fsx for NetApp ONTAP File System CDK Construct

The `OntapFileSystem` construct facilitates the creation and management of [Amazon FSx for NetApp ONTAP](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/what-is-fsx-ontap.html) file systems within AWS CDK applications.

## Basic Usage for FSx for NetApp ONTAP

Setup required properties and create:

```python
declare const vpc: ec2.Vpc;

const fileSystem = new OntapFileSystem(this, 'FsxOntapFileSystem', {
  ontapConfiguration: {
    deploymentType: OntapDeploymentType.SINGLE_AZ_2,
  },
  storageCapacityGiB: 1200,
  vpc,
  vpcSubnet: vpc.privateSubnets,
});
```

### Connecting to FSx for NetApp ONTAP

To control who can access the file system, use the `.connections` attribute.

This example allows an EC2 instance to connect to a file system on port 2049:

```python
declare const fileSystem: OntapFileSystem;
declare const instance: ec2.Instance;

fileSystem.connections.allowFrom(instance, ec2.Port.tcp(2049));
```

### Deployment Type

The `OntapFileSystem` construct supports the following deployment types:

* `SINGLE_AZ_1`:  A file system configured for Single-AZ redundancy. This is a first-generation FSx for ONTAP file system.
* `SINGLE_AZ_2`: A file system configured with multiple high-availability (HA) pairs for Single-AZ redundancy. This is a second-generation FSx for ONTAP file system.
* `MULTI_AZ_1`:  A high availability file system configured for Multi-AZ redundancy to tolerate temporary Availability Zone (AZ) unavailability.  This is a first-generation FSx for ONTAP file system.
* `MULTI_AZ_2`: A high availability file system configured for Multi-AZ redundancy to tolerate temporary AZ unavailability. This is a second-generation FSx for ONTAP file system.

Only `SINGLE_AZ_2` allows setting HA pairs to a value other than 1.

### Backup

With FSx for ONTAP, you can protect your data by taking automatic daily backups and user-initiated backups of the volumes on your file system.
Creating regular backups for your volumes is a best practice that helps support your data retention and compliance needs.

You can restore volume backups to any existing FSx for ONTAP file system you have access to that is in the same AWS Region where the backup is stored.
Working with Amazon FSx backups makes it is easy to create, view, restore, and delete backups of your volumes.

To enable automatic backups, set the `automaticBackupRetention` property to a non-zero value in the `ontapConfiguration`:

```python
declare const vpc: ec2.Vpc;

const fileSystem = new OntapFileSystem(this, 'FsxOntapFileSystem', {
  ontapConfiguration: {
    deploymentType: OntapDeploymentType.SINGLE_AZ_2,
    // Enable automatic backups and set the retention period to 3 days
    automaticBackupRetention: cdk.Duration.days(3),
    // Set the backup window to 1:00 AM UTC
    dailyAutomaticBackupStartTime: new fsx.DailyAutomaticBackupStartTime({
      hour: 1,
      minute: 0,
    }),
  },
  storageCapacityGiB: 1200,
  vpc,
  vpcSubnet: vpc.privateSubnets,
});
```

### File system storage capacity and IOPS

When you create an FSx for ONTAP file system, you specify the storage capacity of the SSD tier.

For second-generation Single-AZ file systems,
the storage capacity that you specify is spread evenly among the storage pools of each high-availability (HA) pair;
these storage pools are called aggregates.

For each GiB of SSD storage that you provision,
Amazon FSx automatically provisions 3 SSD input/output operations per second (IOPS) for the file system,
up to a maximum of 160,000 SSD IOPS per file system.

For second-generation Single-AZ file systems, your SSD IOPS are spread evenly across each of your file system's aggregates.
You have the option to specify a level of provisioned SSD IOPS above the automatic 3 SSD IOPS per GiB.

For more information, see [File system storage capacity and IOPS](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/storage-capacity-and-IOPS.html).

To specify the storage capacity and level of provisioned SSD IOPS, set the `storageCapacityGiB` in the `OntapFileSystemProps` and `diskIops` property in the `ontapConfiguration`:

```python
declare const vpc: ec2.Vpc;

const fileSystem = new OntapFileSystem(this, 'FsxOntapFileSystem', {
  ontapConfiguration: {
    deploymentType: OntapDeploymentType.SINGLE_AZ_2,
    // Set the level of provisioned SSD IOPS to 12,288
    diskIops: 12288,
    haPairs: 2,
  },
  // Set the storage capacity to 2 TiB
  storageCapacityGiB: 2048,
  vpc,
  vpcSubnet: vpc.privateSubnets,
});
```

**Note**:

* The storage capacity has a minimum and maximum value based on the HA pairs. The minimum value is `1,024 * haPairs` GiB and the maximum value is smaller one between `524,288 * haPairs` and `1,048,576` GiB.
* The level of provisioned SSD IOPS has a minimum and maximum value based on the storage capacity. The minimum value is `3 * storageCapacityGiB * haPairs` IOPS and the maximum value is `200,000 * haPairs` IOPS.

### Multi-AZ file systems

Multi-AZ file systems support all the availability and durability features of Single-AZ file systems.
In addition, they are designed to provide continuous availability to data even when an Availability Zone is unavailable.

Multi-AZ deployments have a single HA pair of file servers,
the standby file server is deployed in a different Availability Zone from the active file server in the same AWS Region.
Any changes written to your file system are synchronously replicated across Availability Zones to the standby.

To create a Multi-AZ file system, set the `deploymentType` to `MULTI_AZ_X` and specify `endpointIpAddressRange`, `routeTables` and `preferredSubnet` in the `ontapConfiguration`:

```python
declare const vpc: ec2.Vpc;

const fileSystem = new OntapFileSystem(this, 'FsxOntapFileSystem', {
  ontapConfiguration: {
    deploymentType: OntapDeploymentType.MULTI_AZ_2,
    // The IP address range in which the endpoints to access your file system will be created.
    endpointIpAddressRange: '192.168.39.0/24',
    // The route tables in which Amazon FSx creates the rules for routing traffic to the correct file server.
    // You should specify all virtual private cloud (VPC) route tables associated with the subnets in which your clients are located.
    routeTables: [vpc.privateSubnets.routeTable],
    // The subnet in which you want the preferred file server to be located.
    preferredSubnet: vpc.privateSubnets[0],
  },
  storageCapacityGiB: 1200,
  vpc,
  vpcSubnet: vpc.privateSubnets,
});
```

**Note**:

* `preferredSubnet` must be the part of the `vpcSubnet`.
* Amazon FSx manages VPC route tables for Multi-AZ file systems using tag-based authentication. These route tables are tagged with Key: `AmazonFSx`; Value: `ManagedByAmazonFSx`.

### Throughput Capacity

FSx for ONTAP configures throughput capacity when you create the file system.
You can modify your file system's throughput capacity at any time.

Keep in mind that your file system requires a specific configuration to achieve the maximum amount of throughput capacity.

For more information, see [Managing throughput capacity](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/managing-throughput-capacity.html).

To specify the throughput capacity, set the `throughputCapacityPreHaPair` property in the `ontapConfiguration`.

This example sets the throughput capacity to 1536 MiB/s per HA pair:

```python
declare const vpc: ec2.Vpc;

const fileSystem = new OntapFileSystem(this, 'FsxOntapFileSystem', {
  ontapConfiguration: {
    deploymentType: OntapDeploymentType.SINGLE_AZ_2,
    haPairs: 4,
    // Set the total throughput capacity to 6144 MiB/s
    throughputCapacity: SingleAz2ThroughputCapacityPerHaPair.MB_PER_SEC_1536,
  },
  storageCapacityGiB: 4096,
  vpc,
  vpcSubnet: vpc.privateSubnets,
});
```

### Maintenance Window

As a fully-managed service, FSx for ONTAP regularly performs maintenance on and updates to your file system.
This maintenance has no impact for most workloads.

For workloads that are performance-sensitive,
on rare occasions you may notice a brief (<60 seconds) impact on performance when maintenance is occurring;
Amazon FSx enables you to use the maintenance window to control when any such potential maintenance activity occurs.

To set the maintenance window, specify the `maintenanceWindow` property in the `ontapConfiguration`:

```python
declare const vpc: ec2.Vpc;

const fileSystem = new OntapFileSystem(this, 'FsxOntapFileSystem', {
  ontapConfiguration: {
    deploymentType: OntapDeploymentType.SINGLE_AZ_2,
    // Set the weekly maintenance window to SUNDAY 1:00 AM UTC
    weeklyMaintenanceStartTime: new MaintenanceTime({
      day: fsx.Weekday.SUNDAY,
      hour: 1,
      minute: 0,
    }),
  },
  storageCapacityGiB: 1200,
  vpc,
  vpcSubnet: vpc.privateSubnets,
});
```

### Import an existing file system

To import an existing FSx for ONTAP file system, use the `OntapFileSystem.fromOntapFileSystemAttributes` method:

```python
declare const existingFileSystem: fsx.IFileSystemBase;
declare const vpc: ec2.Vpc;

const fileSystem = OntapFileSystem.fromOntapFileSystemAttributes(this, 'FsxOntapFileSystem', {
  dnsName: existingFileSystem.dnsName,
  fileSystemId: existingFileSystem.fileSystemId,
  securityGroup: existingFileSystem.securityGroup,
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
import aws_cdk.aws_fsx as _aws_cdk_aws_fsx_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import constructs as _constructs_77d1e7e8


class DailyAutomaticBackupStartTime(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.DailyAutomaticBackupStartTime",
):
    '''Class for scheduling a daily automatic backup time.'''

    def __init__(self, *, hour: jsii.Number, minute: jsii.Number) -> None:
        '''
        :param hour: The hour of the day (from 0-23) for automatic backup starts.
        :param minute: The minute of the hour (from 0-59) for automatic backup starts.
        '''
        props = DailyAutomaticBackupStartTimeProps(hour=hour, minute=minute)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toTimestamp")
    def to_timestamp(self) -> builtins.str:
        '''Converts an hour, and minute into HH:MM string.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toTimestamp", []))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_fsx.DailyAutomaticBackupStartTimeProps",
    jsii_struct_bases=[],
    name_mapping={"hour": "hour", "minute": "minute"},
)
class DailyAutomaticBackupStartTimeProps:
    def __init__(self, *, hour: jsii.Number, minute: jsii.Number) -> None:
        '''Properties required for setting up a daily automatic backup time.

        :param hour: The hour of the day (from 0-23) for automatic backup starts.
        :param minute: The minute of the hour (from 0-59) for automatic backup starts.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9449a2a732350e1d30396c7541f141ef448f748f403848275c872efda0267768)
            check_type(argname="argument hour", value=hour, expected_type=type_hints["hour"])
            check_type(argname="argument minute", value=minute, expected_type=type_hints["minute"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hour": hour,
            "minute": minute,
        }

    @builtins.property
    def hour(self) -> jsii.Number:
        '''The hour of the day (from 0-23) for automatic backup starts.'''
        result = self._values.get("hour")
        assert result is not None, "Required property 'hour' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def minute(self) -> jsii.Number:
        '''The minute of the hour (from 0-59) for automatic backup starts.'''
        result = self._values.get("minute")
        assert result is not None, "Required property 'minute' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DailyAutomaticBackupStartTimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MaintenanceTime(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.MaintenanceTime",
):
    '''Class for scheduling a weekly maintenance time.'''

    def __init__(
        self,
        *,
        day: _aws_cdk_aws_fsx_ceddda9d.Weekday,
        hour: jsii.Number,
        minute: jsii.Number,
    ) -> None:
        '''
        :param day: The day of the week for maintenance to be performed.
        :param hour: The hour of the day (from 0-23) for maintenance to be performed.
        :param minute: The minute of the hour (from 0-59) for maintenance to be performed.
        '''
        props = MaintenanceTimeProps(day=day, hour=hour, minute=minute)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="toTimestamp")
    def to_timestamp(self) -> builtins.str:
        '''Converts a day, hour, and minute into a timestamp as used by FSx for Lustre's weeklyMaintenanceStartTime field.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toTimestamp", []))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_fsx.MaintenanceTimeProps",
    jsii_struct_bases=[],
    name_mapping={"day": "day", "hour": "hour", "minute": "minute"},
)
class MaintenanceTimeProps:
    def __init__(
        self,
        *,
        day: _aws_cdk_aws_fsx_ceddda9d.Weekday,
        hour: jsii.Number,
        minute: jsii.Number,
    ) -> None:
        '''Properties required for setting up a weekly maintenance time.

        :param day: The day of the week for maintenance to be performed.
        :param hour: The hour of the day (from 0-23) for maintenance to be performed.
        :param minute: The minute of the hour (from 0-59) for maintenance to be performed.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11d208842ee8c5fee728687b5f5db85548e640bada292d5ba02d953406ebe840)
            check_type(argname="argument day", value=day, expected_type=type_hints["day"])
            check_type(argname="argument hour", value=hour, expected_type=type_hints["hour"])
            check_type(argname="argument minute", value=minute, expected_type=type_hints["minute"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "day": day,
            "hour": hour,
            "minute": minute,
        }

    @builtins.property
    def day(self) -> _aws_cdk_aws_fsx_ceddda9d.Weekday:
        '''The day of the week for maintenance to be performed.'''
        result = self._values.get("day")
        assert result is not None, "Required property 'day' is missing"
        return typing.cast(_aws_cdk_aws_fsx_ceddda9d.Weekday, result)

    @builtins.property
    def hour(self) -> jsii.Number:
        '''The hour of the day (from 0-23) for maintenance to be performed.'''
        result = self._values.get("hour")
        assert result is not None, "Required property 'hour' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def minute(self) -> jsii.Number:
        '''The minute of the hour (from 0-59) for maintenance to be performed.'''
        result = self._values.get("minute")
        assert result is not None, "Required property 'minute' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MaintenanceTimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_fsx.OntapConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "automatic_backup_retention": "automaticBackupRetention",
        "daily_automatic_backup_start_time": "dailyAutomaticBackupStartTime",
        "deployment_type": "deploymentType",
        "disk_iops": "diskIops",
        "endpoint_ip_address_range": "endpointIpAddressRange",
        "fsx_admin_password": "fsxAdminPassword",
        "ha_pairs": "haPairs",
        "preferred_subnet": "preferredSubnet",
        "route_tables": "routeTables",
        "throughput_capacity_per_ha_pair": "throughputCapacityPerHaPair",
        "weekly_maintenance_start_time": "weeklyMaintenanceStartTime",
    },
)
class OntapConfiguration:
    def __init__(
        self,
        *,
        automatic_backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        daily_automatic_backup_start_time: typing.Optional[DailyAutomaticBackupStartTime] = None,
        deployment_type: typing.Optional["OntapDeploymentType"] = None,
        disk_iops: typing.Optional[jsii.Number] = None,
        endpoint_ip_address_range: typing.Optional[builtins.str] = None,
        fsx_admin_password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        ha_pairs: typing.Optional[jsii.Number] = None,
        preferred_subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
        route_tables: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.IRouteTable]] = None,
        throughput_capacity_per_ha_pair: typing.Optional["ThroughputCapacityPerHaPair"] = None,
        weekly_maintenance_start_time: typing.Optional[MaintenanceTime] = None,
    ) -> None:
        '''The configuration for the Amazon FSx for NetApp ONTAP file system.

        :param automatic_backup_retention: The number of days to retain automatic backups. Setting this property to 0 disables automatic backups. You can retain automatic backups for a maximum of 90 days. Default: - 30 days
        :param daily_automatic_backup_start_time: Start time for 30-minute daily automatic backup window in Coordinated Universal Time (UTC). Default: - no backup window
        :param deployment_type: The FSx for ONTAP file system deployment type to use in creating the file system. Default: OntapDeploymentType.MULTI_AZ_2
        :param disk_iops: The total number of SSD IOPS provisioned for the file system. The minimum and maximum values for this property depend on the value of HAPairs and StorageCapacity. The minimum value is calculated as StorageCapacity * 3 * HAPairs (3 IOPS per GB of StorageCapacity). The maximum value is calculated as 200,000 * HAPairs. Default: - 3 IOPS * GB of storage capacity * HAPairs
        :param endpoint_ip_address_range: The IP address range in which the endpoints to access your file system will be created. You can have overlapping endpoint IP addresses for file systems deployed in the same VPC/route tables, as long as they don't overlap with any subnet. Default: - an unused IP address range from the 198.19.* range
        :param fsx_admin_password: The ONTAP administrative password for the ``fsxadmin`` user with which you administer your file system using the NetApp ONTAP CLI and REST API. If you don't specify a password, Amazon FSx will not set one. In that case, the user will not be able to log in. You can change the admin password at any time through the management console. Default: - do not set an admin password
        :param ha_pairs: How many high-availability (HA) pairs of file servers will power your file system. First-generation file systems are powered by 1 HA pair. Second-generation multi-AZ file systems are powered by 1 HA pair. Second generation single-AZ file systems are powered by up to 12 HA pairs. The value of this property affects the values of ``storageCapacity``, ``iops``, and ``throughputCapacity``. Block storage protocol support (iSCSI and NVMe over TCP) is disabled on file systems with more than 6 HA pairs. Default: 1
        :param preferred_subnet: The subnet in which you want the preferred file server to be located. This value is required when ``deploymentType`` is set to ``MULTI_AZ_1`` or ``MULTI_AZ_2``. Default: - no default value (This value is not used for single-AZ file systems, but it is required for multi-AZ file systems)
        :param route_tables: The route tables in which Amazon FSx creates the rules for routing traffic to the correct file server. You should specify all virtual private cloud (VPC) route tables associated with the subnets in which your clients are located. Amazon FSx manages VPC route tables for Multi-AZ file systems using tag-based authentication. These route tables are tagged with Key: AmazonFSx; Value: ManagedByAmazonFSx. Default: - Amazon FSx selects your VPC's default route table.
        :param throughput_capacity_per_ha_pair: The throughput capacity per HA pair for the file system. Default: - Amazon FSx determines the throughput capacity based on the storage capacity
        :param weekly_maintenance_start_time: The preferred day and time to perform weekly maintenance. Default: - automatically set by Amazon FSx

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-fsx-filesystem-ontapconfiguration.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91e49411f1207b1cc0f6c3c6319b4136d76a311865f8733f63c7c56fd7303ef6)
            check_type(argname="argument automatic_backup_retention", value=automatic_backup_retention, expected_type=type_hints["automatic_backup_retention"])
            check_type(argname="argument daily_automatic_backup_start_time", value=daily_automatic_backup_start_time, expected_type=type_hints["daily_automatic_backup_start_time"])
            check_type(argname="argument deployment_type", value=deployment_type, expected_type=type_hints["deployment_type"])
            check_type(argname="argument disk_iops", value=disk_iops, expected_type=type_hints["disk_iops"])
            check_type(argname="argument endpoint_ip_address_range", value=endpoint_ip_address_range, expected_type=type_hints["endpoint_ip_address_range"])
            check_type(argname="argument fsx_admin_password", value=fsx_admin_password, expected_type=type_hints["fsx_admin_password"])
            check_type(argname="argument ha_pairs", value=ha_pairs, expected_type=type_hints["ha_pairs"])
            check_type(argname="argument preferred_subnet", value=preferred_subnet, expected_type=type_hints["preferred_subnet"])
            check_type(argname="argument route_tables", value=route_tables, expected_type=type_hints["route_tables"])
            check_type(argname="argument throughput_capacity_per_ha_pair", value=throughput_capacity_per_ha_pair, expected_type=type_hints["throughput_capacity_per_ha_pair"])
            check_type(argname="argument weekly_maintenance_start_time", value=weekly_maintenance_start_time, expected_type=type_hints["weekly_maintenance_start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automatic_backup_retention is not None:
            self._values["automatic_backup_retention"] = automatic_backup_retention
        if daily_automatic_backup_start_time is not None:
            self._values["daily_automatic_backup_start_time"] = daily_automatic_backup_start_time
        if deployment_type is not None:
            self._values["deployment_type"] = deployment_type
        if disk_iops is not None:
            self._values["disk_iops"] = disk_iops
        if endpoint_ip_address_range is not None:
            self._values["endpoint_ip_address_range"] = endpoint_ip_address_range
        if fsx_admin_password is not None:
            self._values["fsx_admin_password"] = fsx_admin_password
        if ha_pairs is not None:
            self._values["ha_pairs"] = ha_pairs
        if preferred_subnet is not None:
            self._values["preferred_subnet"] = preferred_subnet
        if route_tables is not None:
            self._values["route_tables"] = route_tables
        if throughput_capacity_per_ha_pair is not None:
            self._values["throughput_capacity_per_ha_pair"] = throughput_capacity_per_ha_pair
        if weekly_maintenance_start_time is not None:
            self._values["weekly_maintenance_start_time"] = weekly_maintenance_start_time

    @builtins.property
    def automatic_backup_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The number of days to retain automatic backups.

        Setting this property to 0 disables automatic backups.
        You can retain automatic backups for a maximum of 90 days.

        :default: - 30 days
        '''
        result = self._values.get("automatic_backup_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def daily_automatic_backup_start_time(
        self,
    ) -> typing.Optional[DailyAutomaticBackupStartTime]:
        '''Start time for 30-minute daily automatic backup window in Coordinated Universal Time (UTC).

        :default: - no backup window
        '''
        result = self._values.get("daily_automatic_backup_start_time")
        return typing.cast(typing.Optional[DailyAutomaticBackupStartTime], result)

    @builtins.property
    def deployment_type(self) -> typing.Optional["OntapDeploymentType"]:
        '''The FSx for ONTAP file system deployment type to use in creating the file system.

        :default: OntapDeploymentType.MULTI_AZ_2
        '''
        result = self._values.get("deployment_type")
        return typing.cast(typing.Optional["OntapDeploymentType"], result)

    @builtins.property
    def disk_iops(self) -> typing.Optional[jsii.Number]:
        '''The total number of SSD IOPS provisioned for the file system.

        The minimum and maximum values for this property depend on the value of HAPairs and StorageCapacity.
        The minimum value is calculated as StorageCapacity * 3 * HAPairs (3 IOPS per GB of StorageCapacity).
        The maximum value is calculated as 200,000 * HAPairs.

        :default: - 3 IOPS * GB of storage capacity * HAPairs
        '''
        result = self._values.get("disk_iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def endpoint_ip_address_range(self) -> typing.Optional[builtins.str]:
        '''The IP address range in which the endpoints to access your file system will be created.

        You can have overlapping endpoint IP addresses for file systems deployed in the same VPC/route tables, as long as they don't overlap with any subnet.

        :default: - an unused IP address range from the 198.19.* range
        '''
        result = self._values.get("endpoint_ip_address_range")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fsx_admin_password(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''The ONTAP administrative password for the ``fsxadmin`` user with which you administer your file system using the NetApp ONTAP CLI and REST API.

        If you don't specify a password, Amazon FSx will not set one. In that case, the user will not be able to log in.

        You can change the admin password at any time through the management console.

        :default: - do not set an admin password
        '''
        result = self._values.get("fsx_admin_password")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def ha_pairs(self) -> typing.Optional[jsii.Number]:
        '''How many high-availability (HA) pairs of file servers will power your file system.

        First-generation file systems are powered by 1 HA pair.
        Second-generation multi-AZ file systems are powered by 1 HA pair.
        Second generation single-AZ file systems are powered by up to 12 HA pairs.

        The value of this property affects the values of ``storageCapacity``, ``iops``, and ``throughputCapacity``.

        Block storage protocol support (iSCSI and NVMe over TCP) is disabled on file systems with more than 6 HA pairs.

        :default: 1

        :see: https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/supported-fsx-clients.html#using-block-storage
        '''
        result = self._values.get("ha_pairs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_subnet(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''The subnet in which you want the preferred file server to be located.

        This value is required when ``deploymentType`` is set to ``MULTI_AZ_1`` or ``MULTI_AZ_2``.

        :default: - no default value (This value is not used for single-AZ file systems, but it is required for multi-AZ file systems)
        '''
        result = self._values.get("preferred_subnet")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

    @builtins.property
    def route_tables(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.IRouteTable]]:
        '''The route tables in which Amazon FSx creates the rules for routing traffic to the correct file server.

        You should specify all virtual private cloud (VPC) route tables associated with the subnets in which your clients are located.

        Amazon FSx manages VPC route tables for Multi-AZ file systems using tag-based authentication.
        These route tables are tagged with Key: AmazonFSx; Value: ManagedByAmazonFSx.

        :default: - Amazon FSx selects your VPC's default route table.

        :see: https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/unable-to-access.html#vpc-route-tables-not-tagged
        '''
        result = self._values.get("route_tables")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.IRouteTable]], result)

    @builtins.property
    def throughput_capacity_per_ha_pair(
        self,
    ) -> typing.Optional["ThroughputCapacityPerHaPair"]:
        '''The throughput capacity per HA pair for the file system.

        :default: - Amazon FSx determines the throughput capacity based on the storage capacity

        :see: https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/managing-throughput-capacity.html
        '''
        result = self._values.get("throughput_capacity_per_ha_pair")
        return typing.cast(typing.Optional["ThroughputCapacityPerHaPair"], result)

    @builtins.property
    def weekly_maintenance_start_time(self) -> typing.Optional[MaintenanceTime]:
        '''The preferred day and time to perform weekly maintenance.

        :default: - automatically set by Amazon FSx
        '''
        result = self._values.get("weekly_maintenance_start_time")
        return typing.cast(typing.Optional[MaintenanceTime], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OntapConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@open-constructs/aws-cdk.aws_fsx.OntapDeploymentType")
class OntapDeploymentType(enum.Enum):
    '''The different kinds of file system deployments used by NetApp ONTAP.'''

    MULTI_AZ_1 = "MULTI_AZ_1"
    '''A high availability file system configured for Multi-AZ redundancy to tolerate temporary Availability Zone (AZ) unavailability.

    This is a first-generation FSx for ONTAP file system.
    '''
    MULTI_AZ_2 = "MULTI_AZ_2"
    '''A high availability file system configured for Multi-AZ redundancy to tolerate temporary AZ unavailability.

    This is a second-generation FSx for ONTAP file system.
    '''
    SINGLE_AZ_1 = "SINGLE_AZ_1"
    '''A file system configured for Single-AZ redundancy.

    This is a first-generation FSx for ONTAP file system.
    '''
    SINGLE_AZ_2 = "SINGLE_AZ_2"
    '''A file system configured with multiple high-availability (HA) pairs for Single-AZ redundancy.

    This is a second-generation FSx for ONTAP file system.
    '''


class OntapFileSystem(
    _aws_cdk_aws_fsx_ceddda9d.FileSystemBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.OntapFileSystem",
):
    '''The FSx for NetApp ONTAP File System implementation of IFileSystem.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html
    :resource: AWS::FSx::FileSystem
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        ontap_configuration: typing.Union[OntapConfiguration, typing.Dict[builtins.str, typing.Any]],
        vpc_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
        storage_capacity_gib: jsii.Number,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        backup_id: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        storage_type: typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ontap_configuration: Additional configuration for FSx specific to NetApp ONTAP.
        :param vpc_subnets: The subnet that the file system will be accessible from. For MULTI_AZ_1 deployment types, provide exactly two subnets, one for the preferred file server and one for the standby file server. Specify one of these subnets as the preferred subnet using ``OntapConfiguration.preferredSubnet`` property for multi-AZ file system.
        :param storage_capacity_gib: The storage capacity of the file system being created. For Windows file systems, valid values are 32 GiB to 65,536 GiB. For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB. For SCRATCH_2, PERSISTENT_2 and PERSISTENT_1 deployment types using SSD storage type, the valid values are 1200 GiB, 2400 GiB, and increments of 2400 GiB. For PERSISTENT_1 HDD file systems, valid values are increments of 6000 GiB for 12 MB/s/TiB file systems and increments of 1800 GiB for 40 MB/s/TiB file systems.
        :param vpc: The VPC to launch the file system in.
        :param backup_id: The ID of the backup. Specifies the backup to use if you're creating a file system from an existing backup. Default: - no backup will be used.
        :param kms_key: The KMS key used for encryption to protect your data at rest. Default: - the aws/fsx default KMS key for the AWS account being deployed into.
        :param removal_policy: Policy to apply when the file system is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic.
        :param storage_type: The storage type for the file system that you're creating. Default: StorageType.SSD
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__138c85de86b7efbc11ef7a1ac24f24c69a83fa6ae6f9fdd646af509abc9290fc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OntapFileSystemProps(
            ontap_configuration=ontap_configuration,
            vpc_subnets=vpc_subnets,
            storage_capacity_gib=storage_capacity_gib,
            vpc=vpc,
            backup_id=backup_id,
            kms_key=kms_key,
            removal_policy=removal_policy,
            security_group=security_group,
            storage_type=storage_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="configureConnections")
    @builtins.classmethod
    def configure_connections(
        cls,
        security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''Configures a Connections object.

        :param security_group: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc7905ebee81e30a8c82b6b4f456fb8cc700e12fe390eaaf0294fbe388b1968a)
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.sinvoke(cls, "configureConnections", [security_group]))

    @jsii.member(jsii_name="fromOntapFileSystemAttributes")
    @builtins.classmethod
    def from_ontap_file_system_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        dns_name: builtins.str,
        file_system_id: builtins.str,
        security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    ) -> _aws_cdk_aws_fsx_ceddda9d.IFileSystem:
        '''Import an existing FSx for NetApp ONTAP file system from the given properties.

        :param scope: -
        :param id: -
        :param dns_name: The DNS name assigned to this file system.
        :param file_system_id: The ID of the file system, assigned by Amazon FSx.
        :param security_group: The security group of the file system.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0206955b8f421c1e98ecfbd1606e8a5119b922f3327ba9c415084e1c611d42e4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = _aws_cdk_aws_fsx_ceddda9d.FileSystemAttributes(
            dns_name=dns_name,
            file_system_id=file_system_id,
            security_group=security_group,
        )

        return typing.cast(_aws_cdk_aws_fsx_ceddda9d.IFileSystem, jsii.sinvoke(cls, "fromOntapFileSystemAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="createOntapFileSystem")
    def _create_ontap_file_system(
        self,
        file_system_security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
        *,
        ontap_configuration: typing.Union[OntapConfiguration, typing.Dict[builtins.str, typing.Any]],
        vpc_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
        storage_capacity_gib: jsii.Number,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        backup_id: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        storage_type: typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType] = None,
    ) -> _aws_cdk_aws_fsx_ceddda9d.CfnFileSystem:
        '''
        :param file_system_security_group: -
        :param ontap_configuration: Additional configuration for FSx specific to NetApp ONTAP.
        :param vpc_subnets: The subnet that the file system will be accessible from. For MULTI_AZ_1 deployment types, provide exactly two subnets, one for the preferred file server and one for the standby file server. Specify one of these subnets as the preferred subnet using ``OntapConfiguration.preferredSubnet`` property for multi-AZ file system.
        :param storage_capacity_gib: The storage capacity of the file system being created. For Windows file systems, valid values are 32 GiB to 65,536 GiB. For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB. For SCRATCH_2, PERSISTENT_2 and PERSISTENT_1 deployment types using SSD storage type, the valid values are 1200 GiB, 2400 GiB, and increments of 2400 GiB. For PERSISTENT_1 HDD file systems, valid values are increments of 6000 GiB for 12 MB/s/TiB file systems and increments of 1800 GiB for 40 MB/s/TiB file systems.
        :param vpc: The VPC to launch the file system in.
        :param backup_id: The ID of the backup. Specifies the backup to use if you're creating a file system from an existing backup. Default: - no backup will be used.
        :param kms_key: The KMS key used for encryption to protect your data at rest. Default: - the aws/fsx default KMS key for the AWS account being deployed into.
        :param removal_policy: Policy to apply when the file system is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic.
        :param storage_type: The storage type for the file system that you're creating. Default: StorageType.SSD
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c5ab2cd5ad7e7144a9f72019cef811516bb6081028e8f07539b626743e88adf)
            check_type(argname="argument file_system_security_group", value=file_system_security_group, expected_type=type_hints["file_system_security_group"])
        props = OntapFileSystemProps(
            ontap_configuration=ontap_configuration,
            vpc_subnets=vpc_subnets,
            storage_capacity_gib=storage_capacity_gib,
            vpc=vpc,
            backup_id=backup_id,
            kms_key=kms_key,
            removal_policy=removal_policy,
            security_group=security_group,
            storage_type=storage_type,
        )

        return typing.cast(_aws_cdk_aws_fsx_ceddda9d.CfnFileSystem, jsii.invoke(self, "createOntapFileSystem", [file_system_security_group, props]))

    @jsii.member(jsii_name="createSecurityGroup")
    def _create_security_group(
        self,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    ) -> _aws_cdk_aws_ec2_ceddda9d.SecurityGroup:
        '''
        :param vpc: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1fbb11bfb7e7efe86c4d6cb03c6fd4f8cf6cecce8e24c559112c7f601afc90f)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.SecurityGroup, jsii.invoke(self, "createSecurityGroup", [vpc]))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''The security groups/rules used to allow network connections to the file system.'''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        '''The management endpoint DNS name assigned to this file system.'''
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property
    @jsii.member(jsii_name="fileSystemId")
    def file_system_id(self) -> builtins.str:
        '''The ID that AWS assigns to the file system.'''
        return typing.cast(builtins.str, jsii.get(self, "fileSystemId"))

    @builtins.property
    @jsii.member(jsii_name="interClusterDnsName")
    def inter_cluster_dns_name(self) -> builtins.str:
        '''The inter cluster endpoint DNS name assigned to this file system.'''
        return typing.cast(builtins.str, jsii.get(self, "interClusterDnsName"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_fsx.OntapFileSystemProps",
    jsii_struct_bases=[_aws_cdk_aws_fsx_ceddda9d.FileSystemProps],
    name_mapping={
        "storage_capacity_gib": "storageCapacityGiB",
        "vpc": "vpc",
        "backup_id": "backupId",
        "kms_key": "kmsKey",
        "removal_policy": "removalPolicy",
        "security_group": "securityGroup",
        "storage_type": "storageType",
        "ontap_configuration": "ontapConfiguration",
        "vpc_subnets": "vpcSubnets",
    },
)
class OntapFileSystemProps(_aws_cdk_aws_fsx_ceddda9d.FileSystemProps):
    def __init__(
        self,
        *,
        storage_capacity_gib: jsii.Number,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        backup_id: typing.Optional[builtins.str] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        storage_type: typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType] = None,
        ontap_configuration: typing.Union[OntapConfiguration, typing.Dict[builtins.str, typing.Any]],
        vpc_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    ) -> None:
        '''Properties specific to the NetApp ONTAP version of the FSx file system.

        :param storage_capacity_gib: The storage capacity of the file system being created. For Windows file systems, valid values are 32 GiB to 65,536 GiB. For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB. For SCRATCH_2, PERSISTENT_2 and PERSISTENT_1 deployment types using SSD storage type, the valid values are 1200 GiB, 2400 GiB, and increments of 2400 GiB. For PERSISTENT_1 HDD file systems, valid values are increments of 6000 GiB for 12 MB/s/TiB file systems and increments of 1800 GiB for 40 MB/s/TiB file systems.
        :param vpc: The VPC to launch the file system in.
        :param backup_id: The ID of the backup. Specifies the backup to use if you're creating a file system from an existing backup. Default: - no backup will be used.
        :param kms_key: The KMS key used for encryption to protect your data at rest. Default: - the aws/fsx default KMS key for the AWS account being deployed into.
        :param removal_policy: Policy to apply when the file system is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_group: Security Group to assign to this file system. Default: - creates new security group which allows all outbound traffic.
        :param storage_type: The storage type for the file system that you're creating. Default: StorageType.SSD
        :param ontap_configuration: Additional configuration for FSx specific to NetApp ONTAP.
        :param vpc_subnets: The subnet that the file system will be accessible from. For MULTI_AZ_1 deployment types, provide exactly two subnets, one for the preferred file server and one for the standby file server. Specify one of these subnets as the preferred subnet using ``OntapConfiguration.preferredSubnet`` property for multi-AZ file system.
        '''
        if isinstance(ontap_configuration, dict):
            ontap_configuration = OntapConfiguration(**ontap_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a31f6a8c112d26fa9acf6b3443573ab3d70c464db78732060e025dddaf5ac18)
            check_type(argname="argument storage_capacity_gib", value=storage_capacity_gib, expected_type=type_hints["storage_capacity_gib"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument backup_id", value=backup_id, expected_type=type_hints["backup_id"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
            check_type(argname="argument ontap_configuration", value=ontap_configuration, expected_type=type_hints["ontap_configuration"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "storage_capacity_gib": storage_capacity_gib,
            "vpc": vpc,
            "ontap_configuration": ontap_configuration,
            "vpc_subnets": vpc_subnets,
        }
        if backup_id is not None:
            self._values["backup_id"] = backup_id
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_group is not None:
            self._values["security_group"] = security_group
        if storage_type is not None:
            self._values["storage_type"] = storage_type

    @builtins.property
    def storage_capacity_gib(self) -> jsii.Number:
        '''The storage capacity of the file system being created.

        For Windows file systems, valid values are 32 GiB to 65,536 GiB.
        For SCRATCH_1 deployment types, valid values are 1,200, 2,400, 3,600, then continuing in increments of 3,600 GiB.
        For SCRATCH_2, PERSISTENT_2 and PERSISTENT_1 deployment types using SSD storage type, the valid values are 1200 GiB, 2400 GiB, and increments of 2400 GiB.
        For PERSISTENT_1 HDD file systems, valid values are increments of 6000 GiB for 12 MB/s/TiB file systems and increments of 1800 GiB for 40 MB/s/TiB file systems.
        '''
        result = self._values.get("storage_capacity_gib")
        assert result is not None, "Required property 'storage_capacity_gib' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''The VPC to launch the file system in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def backup_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the backup.

        Specifies the backup to use if you're creating a file system from an existing backup.

        :default: - no backup will be used.
        '''
        result = self._values.get("backup_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''The KMS key used for encryption to protect your data at rest.

        :default: - the aws/fsx default KMS key for the AWS account being deployed into.
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the file system is removed from the stack.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security Group to assign to this file system.

        :default: - creates new security group which allows all outbound traffic.
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def storage_type(self) -> typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType]:
        '''The storage type for the file system that you're creating.

        :default: StorageType.SSD

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagetype
        '''
        result = self._values.get("storage_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType], result)

    @builtins.property
    def ontap_configuration(self) -> OntapConfiguration:
        '''Additional configuration for FSx specific to NetApp ONTAP.'''
        result = self._values.get("ontap_configuration")
        assert result is not None, "Required property 'ontap_configuration' is missing"
        return typing.cast(OntapConfiguration, result)

    @builtins.property
    def vpc_subnets(self) -> typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet]:
        '''The subnet that the file system will be accessible from.

        For MULTI_AZ_1 deployment types,
        provide exactly two subnets, one for the preferred file server and one for the standby file server.

        Specify one of these subnets as the preferred subnet using ``OntapConfiguration.preferredSubnet`` property for multi-AZ file system.
        '''
        result = self._values.get("vpc_subnets")
        assert result is not None, "Required property 'vpc_subnets' is missing"
        return typing.cast(typing.List[_aws_cdk_aws_ec2_ceddda9d.ISubnet], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OntapFileSystemProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ThroughputCapacityPerHaPair(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.ThroughputCapacityPerHaPair",
):
    '''The throughput capacity per HA pair for an Amazon FSx for NetApp ONTAP file system.'''

    def __init__(self, capacity: jsii.Number) -> None:
        '''
        :param capacity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__378d01ae66ae7fe0bcabffda48d2afaca2d55d506707d573355a94c114e06bef)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
        jsii.create(self.__class__, self, [capacity])

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacity"))

    @builtins.property
    @jsii.member(jsii_name="deploymentType")
    @abc.abstractmethod
    def deployment_type(self) -> OntapDeploymentType:
        '''The deployment type of the throughput capacity.'''
        ...


class _ThroughputCapacityPerHaPairProxy(ThroughputCapacityPerHaPair):
    @builtins.property
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> OntapDeploymentType:
        '''The deployment type of the throughput capacity.'''
        return typing.cast(OntapDeploymentType, jsii.get(self, "deploymentType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ThroughputCapacityPerHaPair).__jsii_proxy_class__ = lambda : _ThroughputCapacityPerHaPairProxy


class MultiAz1ThroughputCapacityPerHaPair(
    ThroughputCapacityPerHaPair,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.MultiAz1ThroughputCapacityPerHaPair",
):
    '''The throughput capacity for the Multi-AZ 1 deployment type.'''

    def __init__(self, capacity: jsii.Number) -> None:
        '''
        :param capacity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7e107498ff0becf3370101bbfe873db0577f83879d4a8d5f4f9ed903b656670)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
        jsii.create(self.__class__, self, [capacity])

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_1024")
    def MB_PER_SEC_1024(cls) -> "MultiAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 1024 MBps per HA pair.'''
        return typing.cast("MultiAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_1024"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_128")
    def MB_PER_SEC_128(cls) -> "MultiAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 128 MBps per HA pair.'''
        return typing.cast("MultiAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_128"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_2048")
    def MB_PER_SEC_2048(cls) -> "MultiAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 2048 MBps per HA pair.'''
        return typing.cast("MultiAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_2048"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_256")
    def MB_PER_SEC_256(cls) -> "MultiAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 256 MBps per HA pair.'''
        return typing.cast("MultiAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_256"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_4096")
    def MB_PER_SEC_4096(cls) -> "MultiAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 4096 MBps per HA pair.'''
        return typing.cast("MultiAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_4096"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_512")
    def MB_PER_SEC_512(cls) -> "MultiAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 512 MBps per HA pair.'''
        return typing.cast("MultiAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_512"))

    @builtins.property
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> OntapDeploymentType:
        '''The deployment type of the throughput capacity.'''
        return typing.cast(OntapDeploymentType, jsii.get(self, "deploymentType"))


class MultiAz2ThroughputCapacityPerHaPair(
    ThroughputCapacityPerHaPair,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.MultiAz2ThroughputCapacityPerHaPair",
):
    '''The throughput capacity for the Multi-AZ 2 deployment type.'''

    def __init__(self, capacity: jsii.Number) -> None:
        '''
        :param capacity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28dba947d6f8a78cc70f0823953065b77d9a47a3826d2111ebab843362ad06e0)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
        jsii.create(self.__class__, self, [capacity])

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_1536")
    def MB_PER_SEC_1536(cls) -> "MultiAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 1536 MBps per HA pair.'''
        return typing.cast("MultiAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_1536"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_3072")
    def MB_PER_SEC_3072(cls) -> "MultiAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 3072 MBps per HA pair.'''
        return typing.cast("MultiAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_3072"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_384")
    def MB_PER_SEC_384(cls) -> "MultiAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 384 MBps per HA pair.'''
        return typing.cast("MultiAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_384"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_6144")
    def MB_PER_SEC_6144(cls) -> "MultiAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 6144 MBps per HA pair.'''
        return typing.cast("MultiAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_6144"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_768")
    def MB_PER_SEC_768(cls) -> "MultiAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 768 MBps per HA pair.'''
        return typing.cast("MultiAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_768"))

    @builtins.property
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> OntapDeploymentType:
        '''The deployment type of the throughput capacity.'''
        return typing.cast(OntapDeploymentType, jsii.get(self, "deploymentType"))


class SingleAz1ThroughputCapacityPerHaPair(
    ThroughputCapacityPerHaPair,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.SingleAz1ThroughputCapacityPerHaPair",
):
    '''The throughput capacity for the Single-AZ 1 deployment type.'''

    def __init__(self, capacity: jsii.Number) -> None:
        '''
        :param capacity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3843bb6d5bd56693ff7ba9c6bbd184b1f3be6f40aa3e4143c68c7714abeb37e)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
        jsii.create(self.__class__, self, [capacity])

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_1024")
    def MB_PER_SEC_1024(cls) -> "SingleAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 1024 MBps per HA pair.'''
        return typing.cast("SingleAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_1024"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_128")
    def MB_PER_SEC_128(cls) -> "SingleAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 128 MBps per HA pair.'''
        return typing.cast("SingleAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_128"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_2048")
    def MB_PER_SEC_2048(cls) -> "SingleAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 2048 MBps per HA pair.'''
        return typing.cast("SingleAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_2048"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_256")
    def MB_PER_SEC_256(cls) -> "SingleAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 256 MBps per HA pair.'''
        return typing.cast("SingleAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_256"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_4096")
    def MB_PER_SEC_4096(cls) -> "SingleAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 4096 MBps per HA pair.'''
        return typing.cast("SingleAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_4096"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_512")
    def MB_PER_SEC_512(cls) -> "SingleAz1ThroughputCapacityPerHaPair":
        '''The throughput capacity of 512 MBps per HA pair.'''
        return typing.cast("SingleAz1ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_512"))

    @builtins.property
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> OntapDeploymentType:
        '''The deployment type of the throughput capacity.'''
        return typing.cast(OntapDeploymentType, jsii.get(self, "deploymentType"))


class SingleAz2ThroughputCapacityPerHaPair(
    ThroughputCapacityPerHaPair,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_fsx.SingleAz2ThroughputCapacityPerHaPair",
):
    '''The throughput capacity for the Single-AZ 2 deployment type.'''

    def __init__(self, capacity: jsii.Number) -> None:
        '''
        :param capacity: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35502f1e42b6993061fc3ddf4323ae469f75d130d04bded53501ee629afe0acc)
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
        jsii.create(self.__class__, self, [capacity])

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_1536")
    def MB_PER_SEC_1536(cls) -> "SingleAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 1536 MBps per HA pair.'''
        return typing.cast("SingleAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_1536"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_3072")
    def MB_PER_SEC_3072(cls) -> "SingleAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 3072 MBps per HA pair.'''
        return typing.cast("SingleAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_3072"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MB_PER_SEC_6144")
    def MB_PER_SEC_6144(cls) -> "SingleAz2ThroughputCapacityPerHaPair":
        '''The throughput capacity of 6144 MBps per HA pair.'''
        return typing.cast("SingleAz2ThroughputCapacityPerHaPair", jsii.sget(cls, "MB_PER_SEC_6144"))

    @builtins.property
    @jsii.member(jsii_name="deploymentType")
    def deployment_type(self) -> OntapDeploymentType:
        '''The deployment type of the throughput capacity.'''
        return typing.cast(OntapDeploymentType, jsii.get(self, "deploymentType"))


__all__ = [
    "DailyAutomaticBackupStartTime",
    "DailyAutomaticBackupStartTimeProps",
    "MaintenanceTime",
    "MaintenanceTimeProps",
    "MultiAz1ThroughputCapacityPerHaPair",
    "MultiAz2ThroughputCapacityPerHaPair",
    "OntapConfiguration",
    "OntapDeploymentType",
    "OntapFileSystem",
    "OntapFileSystemProps",
    "SingleAz1ThroughputCapacityPerHaPair",
    "SingleAz2ThroughputCapacityPerHaPair",
    "ThroughputCapacityPerHaPair",
]

publication.publish()

def _typecheckingstub__9449a2a732350e1d30396c7541f141ef448f748f403848275c872efda0267768(
    *,
    hour: jsii.Number,
    minute: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11d208842ee8c5fee728687b5f5db85548e640bada292d5ba02d953406ebe840(
    *,
    day: _aws_cdk_aws_fsx_ceddda9d.Weekday,
    hour: jsii.Number,
    minute: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e49411f1207b1cc0f6c3c6319b4136d76a311865f8733f63c7c56fd7303ef6(
    *,
    automatic_backup_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    daily_automatic_backup_start_time: typing.Optional[DailyAutomaticBackupStartTime] = None,
    deployment_type: typing.Optional[OntapDeploymentType] = None,
    disk_iops: typing.Optional[jsii.Number] = None,
    endpoint_ip_address_range: typing.Optional[builtins.str] = None,
    fsx_admin_password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ha_pairs: typing.Optional[jsii.Number] = None,
    preferred_subnet: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISubnet] = None,
    route_tables: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.IRouteTable]] = None,
    throughput_capacity_per_ha_pair: typing.Optional[ThroughputCapacityPerHaPair] = None,
    weekly_maintenance_start_time: typing.Optional[MaintenanceTime] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__138c85de86b7efbc11ef7a1ac24f24c69a83fa6ae6f9fdd646af509abc9290fc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    ontap_configuration: typing.Union[OntapConfiguration, typing.Dict[builtins.str, typing.Any]],
    vpc_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    storage_capacity_gib: jsii.Number,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    backup_id: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    storage_type: typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc7905ebee81e30a8c82b6b4f456fb8cc700e12fe390eaaf0294fbe388b1968a(
    security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0206955b8f421c1e98ecfbd1606e8a5119b922f3327ba9c415084e1c611d42e4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    dns_name: builtins.str,
    file_system_id: builtins.str,
    security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c5ab2cd5ad7e7144a9f72019cef811516bb6081028e8f07539b626743e88adf(
    file_system_security_group: _aws_cdk_aws_ec2_ceddda9d.ISecurityGroup,
    *,
    ontap_configuration: typing.Union[OntapConfiguration, typing.Dict[builtins.str, typing.Any]],
    vpc_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
    storage_capacity_gib: jsii.Number,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    backup_id: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    storage_type: typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1fbb11bfb7e7efe86c4d6cb03c6fd4f8cf6cecce8e24c559112c7f601afc90f(
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a31f6a8c112d26fa9acf6b3443573ab3d70c464db78732060e025dddaf5ac18(
    *,
    storage_capacity_gib: jsii.Number,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    backup_id: typing.Optional[builtins.str] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    storage_type: typing.Optional[_aws_cdk_aws_fsx_ceddda9d.StorageType] = None,
    ontap_configuration: typing.Union[OntapConfiguration, typing.Dict[builtins.str, typing.Any]],
    vpc_subnets: typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISubnet],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__378d01ae66ae7fe0bcabffda48d2afaca2d55d506707d573355a94c114e06bef(
    capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7e107498ff0becf3370101bbfe873db0577f83879d4a8d5f4f9ed903b656670(
    capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28dba947d6f8a78cc70f0823953065b77d9a47a3826d2111ebab843362ad06e0(
    capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3843bb6d5bd56693ff7ba9c6bbd184b1f3be6f40aa3e4143c68c7714abeb37e(
    capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35502f1e42b6993061fc3ddf4323ae469f75d130d04bded53501ee629afe0acc(
    capacity: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass
