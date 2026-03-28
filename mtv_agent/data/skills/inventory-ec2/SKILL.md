---
name: inventory-ec2
description: Amazon EC2 inventory field reference and TSL query examples. Use when querying EC2 provider inventory (instances, volumes, networks, storage types).
---

# EC2 Inventory Reference

Field names and query examples for Amazon EC2 providers. Replace `<PROVIDER>` and `<NS>` with actual values.

**Key differences**: EC2 field names use **PascalCase** (AWS SDK convention), unlike other providers which use camelCase. Resources are wrapped in an `object` envelope from the AWS SDK.

---

## VM (Instance) Fields

Each EC2 VM wraps AWS SDK `ec2types.Instance`. Key fields:

### Envelope

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | instance name (from Name tag) |
| `revision` | number | `1` |
| `path` | string | resource path |
| `selfLink` | string | API self-link |

### Instance Details (from AWS SDK)

| Field | Type | Example |
|-------|------|---------|
| `InstanceId` | string | `"i-0abcdef1234567890"` |
| `InstanceType` | string | `"m5.xlarge"`, `"t3.micro"` |
| `ImageId` | string | AMI ID |
| `State.Name` | string | `"running"`, `"stopped"`, `"terminated"` |
| `Placement.AvailabilityZone` | string | `"us-east-1a"` |
| `LaunchTime` | string | ISO 8601 timestamp |
| `Platform` | string | `"windows"` or empty (Linux) |
| `PrivateIpAddress` | string | `"10.0.1.5"` |
| `PublicIpAddress` | string | `"54.12.34.56"` |
| `VpcId` | string | VPC ID |
| `SubnetId` | string | subnet ID |
| `Architecture` | string | `"x86_64"`, `"arm64"` |
| `RootDeviceName` | string | `"/dev/xvda"` |
| `RootDeviceType` | string | `"ebs"` |

### Block Devices and NICs

| Field | Type | Example |
|-------|------|---------|
| `BlockDeviceMappings[*].DeviceName` | string | `"/dev/xvda"` |
| `BlockDeviceMappings[*].Ebs.VolumeId` | string | volume ID |
| `NetworkInterfaces[*].SubnetId` | string | subnet ID |
| `NetworkInterfaces[*].MacAddress` | string | MAC address |

---

## Volume Fields

Query with `get inventory volume --provider <PROVIDER>`. Wraps `ec2types.Volume`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | volume name |
| `VolumeId` | string | `"vol-0abcdef1234567890"` |
| `VolumeType` | string | `"gp3"`, `"io1"`, `"st1"`, `"sc1"` |
| `Size` | number | `100` (GB) |
| `State` | string | `"available"`, `"in-use"` |
| `AvailabilityZone` | string | `"us-east-1a"` |
| `Encrypted` | bool | `true` |
| `Iops` | number | `3000` |
| `Throughput` | number | `125` (MiB/s) |
| `CreateTime` | string | ISO 8601 timestamp |
| `Attachments[*]` | object | attachment details |

---

## Network Fields

Query with `get inventory network --provider <PROVIDER>`. Wraps `ec2types.Subnet`.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | subnet name |
| `SubnetId` | string | `"subnet-0abcdef..."` |
| `VpcId` | string | VPC ID |
| `CidrBlock` | string | `"10.0.1.0/24"` |
| `AvailabilityZone` | string | `"us-east-1a"` |
| `State` | string | `"available"` |
| `MapPublicIpOnLaunch` | bool | `false` |

---

## Storage Fields (EBS Volume Type Catalog)

Query with `get inventory storage --provider <PROVIDER>`. Lists available EBS volume types.

| Field | Type | Example |
|-------|------|---------|
| `id` | string | Forklift internal ID |
| `name` | string | `"gp3"` |
| `type` | string | volume type identifier |
| `description` | string | `"General Purpose SSD"` |
| `maxIOPS` | number | `16000` |
| `maxThroughput` | number | `1000` |

---

## VM Query Examples

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where State.Name = 'running'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where InstanceType = 'm5.xlarge'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where Placement.AvailabilityZone = 'us-east-1a'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where Platform = 'windows'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where Architecture = 'arm64'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory vm", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where name ~= 'prod-.*'", "output": "markdown" } }
```

---

## Volume Query Examples

```json
mtv_read { "command": "get inventory volume", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where VolumeType = 'gp3'", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory volume", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where Encrypted = true", "output": "markdown" } }
```

```json
mtv_read { "command": "get inventory volume", "flags": { "provider": "<PROVIDER>", "namespace": "<NS>", "query": "where Size > 500", "output": "markdown" } }
```
