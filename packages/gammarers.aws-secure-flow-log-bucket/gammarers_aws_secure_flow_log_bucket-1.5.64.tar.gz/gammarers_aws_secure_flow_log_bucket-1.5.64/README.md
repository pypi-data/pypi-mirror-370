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
