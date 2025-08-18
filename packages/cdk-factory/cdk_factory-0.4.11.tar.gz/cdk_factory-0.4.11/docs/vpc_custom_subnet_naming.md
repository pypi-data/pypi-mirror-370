# VPC Custom Subnet Naming

This document describes how to use the custom subnet naming feature in the CDK Factory VPC stack.

## Overview

By default, AWS CDK creates subnets with generic names like "publicSubnet1", "privateSubnet1", etc. The CDK Factory now allows you to customize these subnet names to better reflect their purpose in your architecture.

## Configuration

To use custom subnet names, add the following properties to your VPC configuration:

```json
{
  "vpc": {
    "name": "my-vpc",
    "public_subnet_name": "web-tier",
    "private_subnet_name": "app-tier",
    "isolated_subnet_name": "data-tier"
  }
}
```

### Available Properties

| Property | Description | Default Value |
|----------|-------------|---------------|
| `public_subnet_name` | Name for public subnets | "public" |
| `private_subnet_name` | Name for private subnets | "private" |
| `isolated_subnet_name` | Name for isolated subnets | "isolated" |

## Example

Here's a complete example of a VPC configuration with custom subnet names:

```json
{
  "vpc": {
    "name": "custom-subnet-vpc",
    "cidr": "10.0.0.0/16",
    "max_azs": 2,
    "public_subnets": true,
    "private_subnets": true,
    "isolated_subnets": true,
    "public_subnet_name": "web-tier",
    "private_subnet_name": "app-tier",
    "isolated_subnet_name": "data-tier",
    "public_subnet_mask": 24,
    "private_subnet_mask": 24,
    "isolated_subnet_mask": 24
  }
}
```

This configuration will create subnets with names like "web-tier1", "app-tier1", and "data-tier1" instead of the default "publicSubnet1", "privateSubnet1", and "isolatedSubnet1".

## Impact on Resource Naming

When using custom subnet names, the AWS resources will be named according to the pattern:

```
{deployment-name}/Deploy/{vpc-name}/{subnet-name}{index}
```

For example, with the configuration above, you might see resources named:
- `my-app-dev-pipeline/Deploy/my-app-dev-vpc/web-tier1`
- `my-app-dev-pipeline/Deploy/my-app-dev-vpc/app-tier1`
- `my-app-dev-pipeline/Deploy/my-app-dev-vpc/data-tier1`

This naming pattern makes it easier to identify the purpose of each subnet in your AWS Console and CloudFormation templates.
