r'''
# Open Constructs Library

Welcome to the Open Constructs Library, an innovative solution designed to enhance cloud infrastructure deployment and management.
Our library aims to provide a comprehensive set of tools and constructs that streamline the process of using AWS Cloud Development Kit (AWS CDK) for automation and deployment tasks.

## About The Project

The Open Constructs Library is an open-source initiative aimed at supporting and simplifying the development and management of cloud-native applications.
By leveraging the power of AWS CDK, our library offers developers a wide range of pre-built constructs that encapsulate best practices, reduce boilerplate code, and accelerate the development process.

### Features

* **Pre-built Constructs**: A wide variety of constructs for common cloud infrastructure patterns.
* **Best Practices Encapsulation**: Implements AWS best practices out of the box.
* **Customizability**: Easily extend and customize constructs to fit your specific requirements.
* **Community-driven**: Contributed to and used by a growing community of cloud professionals.

## Getting Started

To get started with the Open Constructs Library, you'll need to have Node.js and the AWS CDK installed on your machine (Other languages will follow very soon). Follow these steps to set up your project.

### Prerequisites

* Node.js (version 18.x or later)
* AWS CDK (version 2.120.0 or later)

### Installation

1. Install the library via npm:

```bash
npm install @open-constructs/aws-cdk
```

1. Import the constructs you need in your CDK stack:

```python
import { SomeConstruct } from '@open-constructs/aws-cdk';
```

1. Follow the library documentation to see how to use the constructs in your application.

## Documentation

For more detailed documentation, including API references and examples, please visit our [documentation site](./API.md).

## Contributing

We welcome contributions from the community! If you're interested in contributing to the Open Constructs Library, please read our [Contributing Guide](./CONTRIBUTING.md) for more information on how to get started.

## Support and Community

If you need help or want to discuss the Open Constructs Library, join our community on cdk.dev Slack.

## License

The Open Constructs Library is open-source software licensed under the [Apache License](./LICENSE).

## Acknowledgements

* AWS CDK
* [Contributors](https://github.com/open-constructs/aws-cdk-library/graphs/contributors)

We are grateful to all the contributors who have helped to build and maintain this library.

---


For more information, please visit our [official website](https://www.open-constructs.org).
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

__all__ = [
    "aws_codeartifact",
    "aws_cur",
    "aws_ec2",
    "aws_elasticache",
    "aws_fsx",
    "aws_redshiftserverless",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import aws_codeartifact
from . import aws_cur
from . import aws_ec2
from . import aws_elasticache
from . import aws_fsx
from . import aws_redshiftserverless
