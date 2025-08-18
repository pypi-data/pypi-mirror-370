r'''
# AWS Secure Flow Log Bucket

[![GitHub](https://img.shields.io/github/license/gammarers/aws-secure-flow-log-bucket?style=flat-square)](https://github.com/gammarers/aws-secure-flow-log-bucket/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@gammarers/aws-secure-flow-log-bucket?style=flat-square)](https://www.npmjs.com/package/@gammarers/aws-secure-flow-log-bucket)
[![PyPI](https://img.shields.io/pypi/v/gammarers.aws-secure-flow-log-bucket?style=flat-square)](https://pypi.org/project/gammarers.aws-secure-flow-log-bucket/)
[![Nuget](https://img.shields.io/nuget/v/gammarers.CDK.AWS.SecureFlowLogBucket?style=flat-square)](https://www.nuget.org/packages/Gammarers.CDK.AWS.SecureFlowLogBucket/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/gammarers/aws-secure-flow-log-bucket/release.yml?branch=main&label=release&style=flat-square)](https://github.com/gammarers/aws-secure-flow-log-bucket/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/gammarers/aws-secure-flow-log-bucket?sort=semver&style=flat-square)](https://github.com/gammarers/aws-secure-flow-log-bucket/releases)

[![View on Construct Hub](https://constructs.dev/badge?package=@gammarers/aws-secure-flow-log-bucket)](https://constructs.dev/packages/@gammarers/aws-secure-flow-log-bucket)

Specific AWS VPC FlowLog Bucket

## Install

### TypeScript

#### install by npm

```shell
npm install @gammarers/aws-secure-flow-log-bucket
```

#### install by yarn

```shell
yarn add @gammarers/aws-secure-flow-log-bucket
```

#### install by pnpm

```shell
pnpm add @gammarers/aws-secure-flow-log-bucket
```

#### install by bun

```shell
bun add @gammarers/aws-secure-flow-log-bucket
```

### Python

```shell
pip install gammarers.aws-secure-flow-log-bucket
```

### C# / .NET

```shell
dotnet add package Gammarers.CDK.AWS.SecureFlowLogBucket
```

## Example

```shell
npm install @gammarers/aws-secure-flow-log-bucket
```

```python
import { SecureFlowLogBucket } from '@gammarers/aws-secure-flow-log-bucket';

const bucket = new SecureFlowLogBucket(stack, 'SecureFlowLogBucket', {
  keyPrefixes: [
    'example-prefix-a',
    'example-prefix-b',
  ],
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
import gammarers.aws_secure_log_bucket as _gammarers_aws_secure_log_bucket_f4802cc2


class SecureFlowLogBucket(
    _gammarers_aws_secure_log_bucket_f4802cc2.SecureLogBucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="@gammarers/aws-secure-flow-log-bucket.SecureFlowLogBucket",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        key_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        change_class_transition: typing.Optional[typing.Union[_gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        encryption: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketEncryption] = None,
        object_ownership: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureObjectOwnership] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param key_prefixes: 
        :param bucket_name: 
        :param change_class_transition: 
        :param encryption: 
        :param object_ownership: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b246e00918e3ee6a95ad81a8c8d1c2d925464b767dbcedd0ed377d79e3fc8169)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SecureFlowLogBucketProps(
            key_prefixes=key_prefixes,
            bucket_name=bucket_name,
            change_class_transition=change_class_transition,
            encryption=encryption,
            object_ownership=object_ownership,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@gammarers/aws-secure-flow-log-bucket.SecureFlowLogBucketProps",
    jsii_struct_bases=[_gammarers_aws_secure_log_bucket_f4802cc2.SecureLogBucketProps],
    name_mapping={
        "bucket_name": "bucketName",
        "change_class_transition": "changeClassTransition",
        "encryption": "encryption",
        "object_ownership": "objectOwnership",
        "key_prefixes": "keyPrefixes",
    },
)
class SecureFlowLogBucketProps(
    _gammarers_aws_secure_log_bucket_f4802cc2.SecureLogBucketProps,
):
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        change_class_transition: typing.Optional[typing.Union[_gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        encryption: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketEncryption] = None,
        object_ownership: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureObjectOwnership] = None,
        key_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param bucket_name: 
        :param change_class_transition: 
        :param encryption: 
        :param object_ownership: 
        :param key_prefixes: 
        '''
        if isinstance(change_class_transition, dict):
            change_class_transition = _gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty(**change_class_transition)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f55bbb4d86d0ff76bdbde2770dfce6ae60f4e62f9cdd0ade81cf293b6593c089)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument change_class_transition", value=change_class_transition, expected_type=type_hints["change_class_transition"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument object_ownership", value=object_ownership, expected_type=type_hints["object_ownership"])
            check_type(argname="argument key_prefixes", value=key_prefixes, expected_type=type_hints["key_prefixes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if change_class_transition is not None:
            self._values["change_class_transition"] = change_class_transition
        if encryption is not None:
            self._values["encryption"] = encryption
        if object_ownership is not None:
            self._values["object_ownership"] = object_ownership
        if key_prefixes is not None:
            self._values["key_prefixes"] = key_prefixes

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def change_class_transition(
        self,
    ) -> typing.Optional[_gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty]:
        result = self._values.get("change_class_transition")
        return typing.cast(typing.Optional[_gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty], result)

    @builtins.property
    def encryption(
        self,
    ) -> typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketEncryption]:
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketEncryption], result)

    @builtins.property
    def object_ownership(
        self,
    ) -> typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureObjectOwnership]:
        result = self._values.get("object_ownership")
        return typing.cast(typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureObjectOwnership], result)

    @builtins.property
    def key_prefixes(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("key_prefixes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecureFlowLogBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecureFlowLogBucket",
    "SecureFlowLogBucketProps",
]

publication.publish()

def _typecheckingstub__b246e00918e3ee6a95ad81a8c8d1c2d925464b767dbcedd0ed377d79e3fc8169(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    key_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    change_class_transition: typing.Optional[typing.Union[_gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    encryption: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketEncryption] = None,
    object_ownership: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureObjectOwnership] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f55bbb4d86d0ff76bdbde2770dfce6ae60f4e62f9cdd0ade81cf293b6593c089(
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    change_class_transition: typing.Optional[typing.Union[_gammarers_aws_secure_log_bucket_f4802cc2.StorageClassTransitionProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    encryption: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureBucketEncryption] = None,
    object_ownership: typing.Optional[_gammarers_aws_secure_bucket_0aa7e232.SecureObjectOwnership] = None,
    key_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
