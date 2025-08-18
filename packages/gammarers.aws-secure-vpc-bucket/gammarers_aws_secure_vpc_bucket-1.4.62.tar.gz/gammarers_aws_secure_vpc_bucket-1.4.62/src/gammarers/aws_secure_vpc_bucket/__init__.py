r'''
# AWS Secure VPC Bucket

[![GitHub](https://img.shields.io/github/license/gammarers/aws-secure-vpc-bucket?style=flat-square)](https://github.com/gammarers/aws-secure-vpc-bucket/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarers/aws-secure-vpc-bucket?style=flat-square)](https://www.npmjs.com/package/@gammarers/aws-secure-vpc-bucket)
[![PyPI](https://img.shields.io/pypi/v/gammarers.aws-secure-vpc-bucket?style=flat-square)](https://pypi.org/project/gammarers.aws-secure-vpc-bucket/)
[![Nuget](https://img.shields.io/nuget/v/Gammarers.CDK.AWS.SecureVpcBucket?style=flat-square)](https://www.nuget.org/packages/Gammarers.CDK.AWS.SecureVpcBucket/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarers/aws-secure-vpc-bucket/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarers/aws-secure-vpc-bucket/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarers/aws-secure-vpc-bucket?sort=semver&style=flat-square)](https://github.com/gammarers/aws-secure-vpc-bucket/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarers/aws-secure-vpc-bucket)](https://constructs.dev/packages/@gammarers/aws-secure-vpc-bucket)

Access from specific VPC Endpoint only Bucket

## Install

### TypeScript

```shell
npm install @gammarers/aws-secure-vpc-bucket
```

or

```shell
yarn add @gammarers/aws-secure-vpc-bucket
```

or

```shell
pnpm add @gammarers/aws-secure-vpc-bucket
```

or

```shell
bun add @gammarers/aws-secure-vpc-bucket
```

### Python

```shell
pip install gammarers.aws-secure-vpc-bucket
```

### C# / .NET

```shell
dotnet add package gammarers.CDK.AWS.SecureVpcBucket
```

## Example

```python
import { SecureSpecificVpcOnlyBucket } from '@gammarers/aws-secure-vpc-bucket';

new SecureVpcBucket(stack, 'SecureVpcBucket', {
  bucketName: 'example-origin-bucket',
  vpcEndpointId: 'vpce-0xxxxxxxxxxxxxxxx', // already created vpc endpoint id
});
```

## License

This project is licensed under the Apache-2.0 License.
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

import constructs as _constructs_77d1e7e8
import gammarers.aws_secure_bucket as _gammarers_aws_secure_bucket_0aa7e232


class SecureVpcBucket(
    _gammarers_aws_secure_bucket_0aa7e232.SecureBucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarers/aws-secure-vpc-bucket.SecureVpcBucket",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        vpc_endpoint_id: builtins.str,
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc_endpoint_id: 
        :param bucket_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__858594bea18d05487c9eaa3bbf7d6a6ee8db2707084fd9a04ff1e3cda855ed8f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SecureVpcBucketProps(
            vpc_endpoint_id=vpc_endpoint_id, bucket_name=bucket_name
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-vpc-bucket.SecureVpcBucketProps",
    jsii_struct_bases=[],
    name_mapping={"vpc_endpoint_id": "vpcEndpointId", "bucket_name": "bucketName"},
)
class SecureVpcBucketProps:
    def __init__(
        self,
        *,
        vpc_endpoint_id: builtins.str,
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param vpc_endpoint_id: 
        :param bucket_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a24b4bfeec966e91116e7580dfedd0448df920ae5b18311c6c8545eca5d49b74)
            check_type(argname="argument vpc_endpoint_id", value=vpc_endpoint_id, expected_type=type_hints["vpc_endpoint_id"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc_endpoint_id": vpc_endpoint_id,
        }
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name

    @builtins.property
    def vpc_endpoint_id(self) -> builtins.str:
        result = self._values.get("vpc_endpoint_id")
        assert result is not None, "Required property 'vpc_endpoint_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureVpcBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecureVpcBucket",
    "SecureVpcBucketProps",
]

publication.publish()

def _typecheckingstub__858594bea18d05487c9eaa3bbf7d6a6ee8db2707084fd9a04ff1e3cda855ed8f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    vpc_endpoint_id: builtins.str,
    bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a24b4bfeec966e91116e7580dfedd0448df920ae5b18311c6c8545eca5d49b74(
    *,
    vpc_endpoint_id: builtins.str,
    bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
