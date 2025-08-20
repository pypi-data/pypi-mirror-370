r'''
# CDKTF prebuilt bindings for ionos-cloud/ionoscloud provider version 6.7.13

This repo builds and publishes the [Terraform ionoscloud provider](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-ionoscloud](https://www.npmjs.com/package/@cdktf/provider-ionoscloud).

`npm install @cdktf/provider-ionoscloud`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-ionoscloud](https://pypi.org/project/cdktf-cdktf-provider-ionoscloud).

`pipenv install cdktf-cdktf-provider-ionoscloud`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Ionoscloud](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Ionoscloud).

`dotnet add package HashiCorp.Cdktf.Providers.Ionoscloud`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-ionoscloud](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-ionoscloud).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-ionoscloud</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-ionoscloud-go`](https://github.com/cdktf/cdktf-provider-ionoscloud-go) package.

`go get github.com/cdktf/cdktf-provider-ionoscloud-go/ionoscloud/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-ionoscloud-go/blob/main/ionoscloud/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-ionoscloud).

## Versioning

This project is explicitly not tracking the Terraform ionoscloud provider version 1:1. In fact, it always tracks `latest` of `~> 6.2` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform ionoscloud provider](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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
    "apigateway",
    "apigateway_route",
    "application_loadbalancer",
    "application_loadbalancer_forwardingrule",
    "auto_certificate",
    "auto_certificate_provider",
    "autoscaling_group",
    "backup_unit",
    "cdn_distribution",
    "certificate",
    "container_registry",
    "container_registry_token",
    "cube_server",
    "data_ionoscloud_apigateway",
    "data_ionoscloud_apigateway_route",
    "data_ionoscloud_application_loadbalancer",
    "data_ionoscloud_application_loadbalancer_forwardingrule",
    "data_ionoscloud_auto_certificate",
    "data_ionoscloud_auto_certificate_provider",
    "data_ionoscloud_autoscaling_group",
    "data_ionoscloud_autoscaling_group_servers",
    "data_ionoscloud_backup_unit",
    "data_ionoscloud_cdn_distribution",
    "data_ionoscloud_certificate",
    "data_ionoscloud_container_registry",
    "data_ionoscloud_container_registry_locations",
    "data_ionoscloud_container_registry_token",
    "data_ionoscloud_contracts",
    "data_ionoscloud_cube_server",
    "data_ionoscloud_datacenter",
    "data_ionoscloud_dataplatform_cluster",
    "data_ionoscloud_dataplatform_node_pool",
    "data_ionoscloud_dataplatform_node_pools",
    "data_ionoscloud_dataplatform_versions",
    "data_ionoscloud_dns_record",
    "data_ionoscloud_dns_zone",
    "data_ionoscloud_firewall",
    "data_ionoscloud_group",
    "data_ionoscloud_image",
    "data_ionoscloud_inmemorydb_replicaset",
    "data_ionoscloud_inmemorydb_snapshot",
    "data_ionoscloud_ipblock",
    "data_ionoscloud_ipfailover",
    "data_ionoscloud_k8_s_cluster",
    "data_ionoscloud_k8_s_clusters",
    "data_ionoscloud_k8_s_node_pool",
    "data_ionoscloud_k8_s_node_pool_nodes",
    "data_ionoscloud_kafka_cluster",
    "data_ionoscloud_kafka_cluster_topic",
    "data_ionoscloud_lan",
    "data_ionoscloud_location",
    "data_ionoscloud_logging_pipeline",
    "data_ionoscloud_mariadb_backups",
    "data_ionoscloud_mariadb_cluster",
    "data_ionoscloud_mongo_cluster",
    "data_ionoscloud_mongo_template",
    "data_ionoscloud_mongo_user",
    "data_ionoscloud_monitoring_pipeline",
    "data_ionoscloud_natgateway",
    "data_ionoscloud_natgateway_rule",
    "data_ionoscloud_networkloadbalancer",
    "data_ionoscloud_networkloadbalancer_forwardingrule",
    "data_ionoscloud_nfs_cluster",
    "data_ionoscloud_nfs_share",
    "data_ionoscloud_nic",
    "data_ionoscloud_nsg",
    "data_ionoscloud_object_storage_accesskey",
    "data_ionoscloud_object_storage_region",
    "data_ionoscloud_pg_backups",
    "data_ionoscloud_pg_cluster",
    "data_ionoscloud_pg_database",
    "data_ionoscloud_pg_databases",
    "data_ionoscloud_pg_user",
    "data_ionoscloud_pg_versions",
    "data_ionoscloud_private_crossconnect",
    "data_ionoscloud_resource",
    "data_ionoscloud_s3_bucket",
    "data_ionoscloud_s3_bucket_policy",
    "data_ionoscloud_s3_key",
    "data_ionoscloud_s3_object",
    "data_ionoscloud_s3_objects",
    "data_ionoscloud_server",
    "data_ionoscloud_servers",
    "data_ionoscloud_share",
    "data_ionoscloud_snapshot",
    "data_ionoscloud_target_group",
    "data_ionoscloud_template",
    "data_ionoscloud_user",
    "data_ionoscloud_vcpu_server",
    "data_ionoscloud_volume",
    "data_ionoscloud_vpn_ipsec_gateway",
    "data_ionoscloud_vpn_ipsec_tunnel",
    "data_ionoscloud_vpn_wireguard_gateway",
    "data_ionoscloud_vpn_wireguard_peer",
    "datacenter",
    "datacenter_nsg_selection",
    "dataplatform_cluster",
    "dataplatform_node_pool",
    "dns_record",
    "dns_zone",
    "firewall",
    "group",
    "inmemorydb_replicaset",
    "ipblock",
    "ipfailover",
    "k8_s_cluster",
    "k8_s_node_pool",
    "kafka_cluster",
    "kafka_cluster_topic",
    "lan",
    "loadbalancer",
    "logging_pipeline",
    "mariadb_cluster",
    "mongo_cluster",
    "mongo_user",
    "monitoring_pipeline",
    "natgateway",
    "natgateway_rule",
    "networkloadbalancer",
    "networkloadbalancer_forwardingrule",
    "nfs_cluster",
    "nfs_share",
    "nic",
    "nsg",
    "nsg_firewallrule",
    "object_storage_accesskey",
    "pg_cluster",
    "pg_database",
    "pg_user",
    "private_crossconnect",
    "provider",
    "s3_bucket",
    "s3_bucket_cors_configuration",
    "s3_bucket_lifecycle_configuration",
    "s3_bucket_object_lock_configuration",
    "s3_bucket_policy",
    "s3_bucket_public_access_block",
    "s3_bucket_server_side_encryption_configuration",
    "s3_bucket_versioning",
    "s3_bucket_website_configuration",
    "s3_key",
    "s3_object",
    "s3_object_copy",
    "server",
    "server_boot_device_selection",
    "share",
    "snapshot",
    "target_group",
    "user",
    "vcpu_server",
    "volume",
    "vpn_ipsec_gateway",
    "vpn_ipsec_tunnel",
    "vpn_wireguard_gateway",
    "vpn_wireguard_peer",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import apigateway
from . import apigateway_route
from . import application_loadbalancer
from . import application_loadbalancer_forwardingrule
from . import auto_certificate
from . import auto_certificate_provider
from . import autoscaling_group
from . import backup_unit
from . import cdn_distribution
from . import certificate
from . import container_registry
from . import container_registry_token
from . import cube_server
from . import data_ionoscloud_apigateway
from . import data_ionoscloud_apigateway_route
from . import data_ionoscloud_application_loadbalancer
from . import data_ionoscloud_application_loadbalancer_forwardingrule
from . import data_ionoscloud_auto_certificate
from . import data_ionoscloud_auto_certificate_provider
from . import data_ionoscloud_autoscaling_group
from . import data_ionoscloud_autoscaling_group_servers
from . import data_ionoscloud_backup_unit
from . import data_ionoscloud_cdn_distribution
from . import data_ionoscloud_certificate
from . import data_ionoscloud_container_registry
from . import data_ionoscloud_container_registry_locations
from . import data_ionoscloud_container_registry_token
from . import data_ionoscloud_contracts
from . import data_ionoscloud_cube_server
from . import data_ionoscloud_datacenter
from . import data_ionoscloud_dataplatform_cluster
from . import data_ionoscloud_dataplatform_node_pool
from . import data_ionoscloud_dataplatform_node_pools
from . import data_ionoscloud_dataplatform_versions
from . import data_ionoscloud_dns_record
from . import data_ionoscloud_dns_zone
from . import data_ionoscloud_firewall
from . import data_ionoscloud_group
from . import data_ionoscloud_image
from . import data_ionoscloud_inmemorydb_replicaset
from . import data_ionoscloud_inmemorydb_snapshot
from . import data_ionoscloud_ipblock
from . import data_ionoscloud_ipfailover
from . import data_ionoscloud_k8_s_cluster
from . import data_ionoscloud_k8_s_clusters
from . import data_ionoscloud_k8_s_node_pool
from . import data_ionoscloud_k8_s_node_pool_nodes
from . import data_ionoscloud_kafka_cluster
from . import data_ionoscloud_kafka_cluster_topic
from . import data_ionoscloud_lan
from . import data_ionoscloud_location
from . import data_ionoscloud_logging_pipeline
from . import data_ionoscloud_mariadb_backups
from . import data_ionoscloud_mariadb_cluster
from . import data_ionoscloud_mongo_cluster
from . import data_ionoscloud_mongo_template
from . import data_ionoscloud_mongo_user
from . import data_ionoscloud_monitoring_pipeline
from . import data_ionoscloud_natgateway
from . import data_ionoscloud_natgateway_rule
from . import data_ionoscloud_networkloadbalancer
from . import data_ionoscloud_networkloadbalancer_forwardingrule
from . import data_ionoscloud_nfs_cluster
from . import data_ionoscloud_nfs_share
from . import data_ionoscloud_nic
from . import data_ionoscloud_nsg
from . import data_ionoscloud_object_storage_accesskey
from . import data_ionoscloud_object_storage_region
from . import data_ionoscloud_pg_backups
from . import data_ionoscloud_pg_cluster
from . import data_ionoscloud_pg_database
from . import data_ionoscloud_pg_databases
from . import data_ionoscloud_pg_user
from . import data_ionoscloud_pg_versions
from . import data_ionoscloud_private_crossconnect
from . import data_ionoscloud_resource
from . import data_ionoscloud_s3_bucket
from . import data_ionoscloud_s3_bucket_policy
from . import data_ionoscloud_s3_key
from . import data_ionoscloud_s3_object
from . import data_ionoscloud_s3_objects
from . import data_ionoscloud_server
from . import data_ionoscloud_servers
from . import data_ionoscloud_share
from . import data_ionoscloud_snapshot
from . import data_ionoscloud_target_group
from . import data_ionoscloud_template
from . import data_ionoscloud_user
from . import data_ionoscloud_vcpu_server
from . import data_ionoscloud_volume
from . import data_ionoscloud_vpn_ipsec_gateway
from . import data_ionoscloud_vpn_ipsec_tunnel
from . import data_ionoscloud_vpn_wireguard_gateway
from . import data_ionoscloud_vpn_wireguard_peer
from . import datacenter
from . import datacenter_nsg_selection
from . import dataplatform_cluster
from . import dataplatform_node_pool
from . import dns_record
from . import dns_zone
from . import firewall
from . import group
from . import inmemorydb_replicaset
from . import ipblock
from . import ipfailover
from . import k8_s_cluster
from . import k8_s_node_pool
from . import kafka_cluster
from . import kafka_cluster_topic
from . import lan
from . import loadbalancer
from . import logging_pipeline
from . import mariadb_cluster
from . import mongo_cluster
from . import mongo_user
from . import monitoring_pipeline
from . import natgateway
from . import natgateway_rule
from . import networkloadbalancer
from . import networkloadbalancer_forwardingrule
from . import nfs_cluster
from . import nfs_share
from . import nic
from . import nsg
from . import nsg_firewallrule
from . import object_storage_accesskey
from . import pg_cluster
from . import pg_database
from . import pg_user
from . import private_crossconnect
from . import provider
from . import s3_bucket
from . import s3_bucket_cors_configuration
from . import s3_bucket_lifecycle_configuration
from . import s3_bucket_object_lock_configuration
from . import s3_bucket_policy
from . import s3_bucket_public_access_block
from . import s3_bucket_server_side_encryption_configuration
from . import s3_bucket_versioning
from . import s3_bucket_website_configuration
from . import s3_key
from . import s3_object
from . import s3_object_copy
from . import server
from . import server_boot_device_selection
from . import share
from . import snapshot
from . import target_group
from . import user
from . import vcpu_server
from . import volume
from . import vpn_ipsec_gateway
from . import vpn_ipsec_tunnel
from . import vpn_wireguard_gateway
from . import vpn_wireguard_peer
