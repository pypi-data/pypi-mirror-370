r'''
Constructs for the AWS Cost and Usage reports

# CostReport CDK Construct

## Overview

The `CostReport` construct facilitates the creation and management of AWS Cost and Usage Reports (CUR)
within AWS CDK applications. This construct automates the setup of the necessary S3 bucket for storing
the reports and configures permissions for AWS billing to write to this bucket. You can specify
various properties of the report like name, format, and granularity.

## Usage

Import the necessary classes and enums from AWS CDK and this construct:

```python
import { App, Stack } from 'aws-cdk-lib';
import { CostReport, ReportGranularity, CurFormat } from '@open-constructs/aws-cdk/aws-cur';
```

### Basic Example

Here's how you can create a monthly cost and usage report in Parquet format:

```python
const app = new App();
// Cannot specify regions other than us-east-1
const stack = new Stack(app, 'CostReportStack', { env: { region: 'us-east-1' } });

new CostReport(stack, 'MyCostReport', {
  costReportName: 'monthly-business-report',
  reportGranularity: ReportGranularity.MONTHLY,
  format: CurFormat.PARQUET,
});
```

### Advanced Example

Creating a report with a custom S3 bucket and hourly granularity:

```python
import { Bucket } from 'aws-cdk-lib/aws-s3';

const customBucket = new Bucket(stack, 'MyCustomBucket');

new CostReport(stack, 'MyDetailedCostReport', {
  costReportName: 'detailed-hourly-report',
  bucket: customBucket,
  reportGranularity: ReportGranularity.HOURLY,
  format: CurFormat.TEXT_OR_CSV,
});
```

### Generating Unique Report Name By Default

If you set the `enableDefaultUniqueReportName` property to `true`, the construct will automatically
generate a unique report name by default.

The cost report name must be unique within your AWS account. So this property is useful when you want
to create multiple reports without specifying a report name for each one.

If you specify a report name directly via the `costReportName`, the construct will use that name instead
of generating a unique one.

```python
new CostReport(stack, 'MyCostReport', {
  enableDefaultUniqueReportName: true,
});
```

### Additional Notes

The construct automatically handles the permissions required for AWS billing services to access the S3 bucket.
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
import aws_cdk.aws_cur as _aws_cdk_aws_cur_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class CostReport(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_cur.CostReport",
):
    '''Represents a Cost Report construct in AWS CDK.

    This class creates an AWS Cost and Usage Report, stored in an S3 bucket, and configures the necessary permissions.

    Example::

        const report = new CostReport(stack, 'MyReport', {
          costReportName: 'business-report',
          reportGranularity: ReportGranularity.MONTHLY,
          format: CurFormat.PARQUET
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        cost_report_name: typing.Optional[builtins.str] = None,
        enable_default_unique_report_name: typing.Optional[builtins.bool] = None,
        format: typing.Optional["CurFormat"] = None,
        report_granularity: typing.Optional["ReportGranularity"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket: The bucket to place the cost report into. If non is provided, a new bucket will be created. Default: - a new bucket will be created.
        :param cost_report_name: The name of the cost report. The name must be unique, is case sensitive, and can't include spaces. The length of this name must be between 1 and 256. Default: - a unique name automatically generated if ``enableDefaultUniqueReportName`` is true, otherwise 'default-cur'.
        :param enable_default_unique_report_name: Whether to generate a unique report name automatically if the ``costReportName`` property is not specified. The default value of the ``costReportName`` is normally ‘default-cur’, but setting this flag to true will generate a unique default value. This flag is ignored if the ``costReportName`` property is specified. Default: false
        :param format: The format to use for the cost and usage report. Default: - TEXT_OR_CSV
        :param report_granularity: The granularity of the line items in the report. Default: - HOURLY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__713094b18d34e7005ee6ed8be7c9d39b5bda6b05ac8b063b9eb580ca84e93dcf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CostReportProps(
            bucket=bucket,
            cost_report_name=cost_report_name,
            enable_default_unique_report_name=enable_default_unique_report_name,
            format=format,
            report_granularity=report_granularity,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createReportBucket")
    def _create_report_bucket(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''
        :param scope: -
        :param id: -
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``UNENCRYPTED`` otherwise. But if ``UNENCRYPTED`` is specified, the bucket will be encrypted as ``S3_MANAGED`` automatically.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Inteligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b1156351e5d0b2a6b745d4c90a82ce705691f81cb9d9d5b0c83108a116173c8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_s3_ceddda9d.BucketProps(
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            event_bridge_enabled=event_bridge_enabled,
            intelligent_tiering_configurations=intelligent_tiering_configurations,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            minimum_tls_version=minimum_tls_version,
            notifications_handler_role=notifications_handler_role,
            notifications_skip_destination_validation=notifications_skip_destination_validation,
            object_lock_default_retention=object_lock_default_retention,
            object_lock_enabled=object_lock_enabled,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            target_object_key_format=target_object_key_format,
            transfer_acceleration=transfer_acceleration,
            transition_default_minimum_object_size=transition_default_minimum_object_size,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.invoke(self, "createReportBucket", [scope, id, props]))

    @jsii.member(jsii_name="createReportDefinition")
    def _create_report_definition(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        compression: builtins.str,
        format: builtins.str,
        refresh_closed_reports: typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable],
        report_name: builtins.str,
        report_versioning: builtins.str,
        s3_bucket: builtins.str,
        s3_prefix: builtins.str,
        s3_region: builtins.str,
        time_unit: builtins.str,
        additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
        additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
        billing_view_arn: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_cur_ceddda9d.CfnReportDefinition:
        '''
        :param scope: -
        :param id: -
        :param compression: The compression format that Amazon Web Services uses for the report.
        :param format: The format that Amazon Web Services saves the report in.
        :param refresh_closed_reports: Whether you want AWS to update your reports after they have been finalized if AWS detects charges related to previous months. These charges can include refunds, credits, or support fees.
        :param report_name: The name of the report that you want to create. The name must be unique, is case sensitive, and can't include spaces.
        :param report_versioning: Whether you want AWS to overwrite the previous version of each report or to deliver the report in addition to the previous versions.
        :param s3_bucket: The S3 bucket where Amazon Web Services delivers the report.
        :param s3_prefix: The prefix that Amazon Web Services adds to the report name when Amazon Web Services delivers the report. Your prefix can't include spaces.
        :param s3_region: The Region of the S3 bucket that Amazon Web Services delivers the report into.
        :param time_unit: The granularity of the line items in the report.
        :param additional_artifacts: A list of manifests that you want AWS to create for this report.
        :param additional_schema_elements: A list of strings that indicate additional content that AWS includes in the report, such as individual resource IDs.
        :param billing_view_arn: The Amazon Resource Name (ARN) of the billing view. You can get this value by using the billing view service public APIs.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__110b81704cf43065a72671818385f4281a238989cde31455bb8dd9fdaeba4497)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_cur_ceddda9d.CfnReportDefinitionProps(
            compression=compression,
            format=format,
            refresh_closed_reports=refresh_closed_reports,
            report_name=report_name,
            report_versioning=report_versioning,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            s3_region=s3_region,
            time_unit=time_unit,
            additional_artifacts=additional_artifacts,
            additional_schema_elements=additional_schema_elements,
            billing_view_arn=billing_view_arn,
        )

        return typing.cast(_aws_cdk_aws_cur_ceddda9d.CfnReportDefinition, jsii.invoke(self, "createReportDefinition", [scope, id, props]))

    @builtins.property
    @jsii.member(jsii_name="costReportName")
    def cost_report_name(self) -> builtins.str:
        '''The name of the cost report.'''
        return typing.cast(builtins.str, jsii.get(self, "costReportName"))

    @builtins.property
    @jsii.member(jsii_name="reportBucket")
    def report_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''The S3 bucket that stores the cost report.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, jsii.get(self, "reportBucket"))


@jsii.data_type(
    jsii_type="@open-constructs/aws-cdk.aws_cur.CostReportProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "cost_report_name": "costReportName",
        "enable_default_unique_report_name": "enableDefaultUniqueReportName",
        "format": "format",
        "report_granularity": "reportGranularity",
    },
)
class CostReportProps:
    def __init__(
        self,
        *,
        bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        cost_report_name: typing.Optional[builtins.str] = None,
        enable_default_unique_report_name: typing.Optional[builtins.bool] = None,
        format: typing.Optional["CurFormat"] = None,
        report_granularity: typing.Optional["ReportGranularity"] = None,
    ) -> None:
        '''Properties for defining a Cost and Usage Report.

        :param bucket: The bucket to place the cost report into. If non is provided, a new bucket will be created. Default: - a new bucket will be created.
        :param cost_report_name: The name of the cost report. The name must be unique, is case sensitive, and can't include spaces. The length of this name must be between 1 and 256. Default: - a unique name automatically generated if ``enableDefaultUniqueReportName`` is true, otherwise 'default-cur'.
        :param enable_default_unique_report_name: Whether to generate a unique report name automatically if the ``costReportName`` property is not specified. The default value of the ``costReportName`` is normally ‘default-cur’, but setting this flag to true will generate a unique default value. This flag is ignored if the ``costReportName`` property is specified. Default: false
        :param format: The format to use for the cost and usage report. Default: - TEXT_OR_CSV
        :param report_granularity: The granularity of the line items in the report. Default: - HOURLY
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fda1bb00cbc4a9665ff3fd4a838cdd6ad46c058027f15b74457da42ca21edae8)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument cost_report_name", value=cost_report_name, expected_type=type_hints["cost_report_name"])
            check_type(argname="argument enable_default_unique_report_name", value=enable_default_unique_report_name, expected_type=type_hints["enable_default_unique_report_name"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument report_granularity", value=report_granularity, expected_type=type_hints["report_granularity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket is not None:
            self._values["bucket"] = bucket
        if cost_report_name is not None:
            self._values["cost_report_name"] = cost_report_name
        if enable_default_unique_report_name is not None:
            self._values["enable_default_unique_report_name"] = enable_default_unique_report_name
        if format is not None:
            self._values["format"] = format
        if report_granularity is not None:
            self._values["report_granularity"] = report_granularity

    @builtins.property
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''The bucket to place the cost report into.

        If non is provided, a new bucket will be created.

        :default: - a new bucket will be created.
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def cost_report_name(self) -> typing.Optional[builtins.str]:
        '''The name of the cost report.

        The name must be unique, is case sensitive, and can't include spaces.

        The length of this name must be between 1 and 256.

        :default:

        - a unique name automatically generated if ``enableDefaultUniqueReportName`` is
        true, otherwise 'default-cur'.
        '''
        result = self._values.get("cost_report_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_default_unique_report_name(self) -> typing.Optional[builtins.bool]:
        '''Whether to generate a unique report name automatically if the ``costReportName`` property is not specified.

        The default value of the ``costReportName`` is normally ‘default-cur’, but setting this flag
        to true will generate a unique default value.

        This flag is ignored if the ``costReportName`` property is specified.

        :default: false
        '''
        result = self._values.get("enable_default_unique_report_name")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def format(self) -> typing.Optional["CurFormat"]:
        '''The format to use for the cost and usage report.

        :default: - TEXT_OR_CSV
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional["CurFormat"], result)

    @builtins.property
    def report_granularity(self) -> typing.Optional["ReportGranularity"]:
        '''The granularity of the line items in the report.

        :default: - HOURLY
        '''
        result = self._values.get("report_granularity")
        return typing.cast(typing.Optional["ReportGranularity"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CostReportProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CurFormat(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_cur.CurFormat",
):
    '''Enum for the possible formats of a cost report.'''

    def __init__(self, compression: builtins.str, format: builtins.str) -> None:
        '''
        :param compression: -
        :param format: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fdd505fae99750332c8685a261e1d52754d0cd6c7b29556c8982b902ecf4430)
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
        jsii.create(self.__class__, self, [compression, format])

    @jsii.member(jsii_name="for")
    @builtins.classmethod
    def for_(cls, compression: builtins.str, format: builtins.str) -> "CurFormat":
        '''Returns a CurFormat instance for the given compression and format string values.

        :param compression: - The compression string value.
        :param format: - The format string value.

        :return: A CurFormat instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9883e0e6a328dd18cfd05780f2e8522db5853667a9ea86bd9206d9c5b6eef152)
            check_type(argname="argument compression", value=compression, expected_type=type_hints["compression"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
        return typing.cast("CurFormat", jsii.sinvoke(cls, "for", [compression, format]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PARQUET")
    def PARQUET(cls) -> "CurFormat":
        '''Parquet format.'''
        return typing.cast("CurFormat", jsii.sget(cls, "PARQUET"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="TEXT_OR_CSV")
    def TEXT_OR_CSV(cls) -> "CurFormat":
        '''GZIP compressed text or CSV format.'''
        return typing.cast("CurFormat", jsii.sget(cls, "TEXT_OR_CSV"))

    @builtins.property
    @jsii.member(jsii_name="compression")
    def compression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compression"))

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))


class ReportGranularity(
    metaclass=jsii.JSIIMeta,
    jsii_type="@open-constructs/aws-cdk.aws_cur.ReportGranularity",
):
    '''Enum for the possible granularities of a cost report.'''

    def __init__(self, value: builtins.str) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e55d8bdcc29e6810ce8a803b8821d44a0d141536c68398958c8709120c7225a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.create(self.__class__, self, [value])

    @jsii.member(jsii_name="for")
    @builtins.classmethod
    def for_(cls, granularity: builtins.str) -> "ReportGranularity":
        '''Returns a ReportGranularity instance for the given granularity string value.

        :param granularity: - The granularity string value to create an instance for.

        :return: A ReportGranularity instance.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4733bd071871f5490f11eb78bfa4e7a31d4ee5c260359f62efbb2677c6936386)
            check_type(argname="argument granularity", value=granularity, expected_type=type_hints["granularity"])
        return typing.cast("ReportGranularity", jsii.sinvoke(cls, "for", [granularity]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="DAILY")
    def DAILY(cls) -> "ReportGranularity":
        '''Daily granularity.'''
        return typing.cast("ReportGranularity", jsii.sget(cls, "DAILY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="HOURLY")
    def HOURLY(cls) -> "ReportGranularity":
        '''Hourly granularity.'''
        return typing.cast("ReportGranularity", jsii.sget(cls, "HOURLY"))

    @jsii.python.classproperty
    @jsii.member(jsii_name="MONTHLY")
    def MONTHLY(cls) -> "ReportGranularity":
        '''Weekly granularity.'''
        return typing.cast("ReportGranularity", jsii.sget(cls, "MONTHLY"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))


__all__ = [
    "CostReport",
    "CostReportProps",
    "CurFormat",
    "ReportGranularity",
]

publication.publish()

def _typecheckingstub__713094b18d34e7005ee6ed8be7c9d39b5bda6b05ac8b063b9eb580ca84e93dcf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    cost_report_name: typing.Optional[builtins.str] = None,
    enable_default_unique_report_name: typing.Optional[builtins.bool] = None,
    format: typing.Optional[CurFormat] = None,
    report_granularity: typing.Optional[ReportGranularity] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b1156351e5d0b2a6b745d4c90a82ce705691f81cb9d9d5b0c83108a116173c8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
    auto_delete_objects: typing.Optional[builtins.bool] = None,
    block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
    bucket_key_enabled: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    enforce_ssl: typing.Optional[builtins.bool] = None,
    event_bridge_enabled: typing.Optional[builtins.bool] = None,
    intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
    lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
    minimum_tls_version: typing.Optional[jsii.Number] = None,
    notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
    object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
    object_lock_enabled: typing.Optional[builtins.bool] = None,
    object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
    public_read_access: typing.Optional[builtins.bool] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    server_access_logs_prefix: typing.Optional[builtins.str] = None,
    target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
    transfer_acceleration: typing.Optional[builtins.bool] = None,
    transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
    versioned: typing.Optional[builtins.bool] = None,
    website_error_document: typing.Optional[builtins.str] = None,
    website_index_document: typing.Optional[builtins.str] = None,
    website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
    website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__110b81704cf43065a72671818385f4281a238989cde31455bb8dd9fdaeba4497(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    compression: builtins.str,
    format: builtins.str,
    refresh_closed_reports: typing.Union[builtins.bool, _aws_cdk_ceddda9d.IResolvable],
    report_name: builtins.str,
    report_versioning: builtins.str,
    s3_bucket: builtins.str,
    s3_prefix: builtins.str,
    s3_region: builtins.str,
    time_unit: builtins.str,
    additional_artifacts: typing.Optional[typing.Sequence[builtins.str]] = None,
    additional_schema_elements: typing.Optional[typing.Sequence[builtins.str]] = None,
    billing_view_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fda1bb00cbc4a9665ff3fd4a838cdd6ad46c058027f15b74457da42ca21edae8(
    *,
    bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    cost_report_name: typing.Optional[builtins.str] = None,
    enable_default_unique_report_name: typing.Optional[builtins.bool] = None,
    format: typing.Optional[CurFormat] = None,
    report_granularity: typing.Optional[ReportGranularity] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fdd505fae99750332c8685a261e1d52754d0cd6c7b29556c8982b902ecf4430(
    compression: builtins.str,
    format: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9883e0e6a328dd18cfd05780f2e8522db5853667a9ea86bd9206d9c5b6eef152(
    compression: builtins.str,
    format: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e55d8bdcc29e6810ce8a803b8821d44a0d141536c68398958c8709120c7225a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4733bd071871f5490f11eb78bfa4e7a31d4ee5c260359f62efbb2677c6936386(
    granularity: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
