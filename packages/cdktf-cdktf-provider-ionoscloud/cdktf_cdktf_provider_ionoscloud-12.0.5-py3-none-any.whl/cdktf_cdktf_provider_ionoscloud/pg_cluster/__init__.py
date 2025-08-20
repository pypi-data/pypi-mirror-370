r'''
# `ionoscloud_pg_cluster`

Refer to the Terraform Registry for docs: [`ionoscloud_pg_cluster`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster).
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

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class PgCluster(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgCluster",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster ionoscloud_pg_cluster}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cores: jsii.Number,
        credentials: typing.Union["PgClusterCredentials", typing.Dict[builtins.str, typing.Any]],
        display_name: builtins.str,
        instances: jsii.Number,
        location: builtins.str,
        postgres_version: builtins.str,
        ram: jsii.Number,
        storage_size: jsii.Number,
        storage_type: builtins.str,
        synchronization_mode: builtins.str,
        allow_replace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backup_location: typing.Optional[builtins.str] = None,
        connection_pooler: typing.Optional[typing.Union["PgClusterConnectionPooler", typing.Dict[builtins.str, typing.Any]]] = None,
        connections: typing.Optional[typing.Union["PgClusterConnections", typing.Dict[builtins.str, typing.Any]]] = None,
        from_backup: typing.Optional[typing.Union["PgClusterFromBackup", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[typing.Union["PgClusterMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["PgClusterTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster ionoscloud_pg_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cores: The number of CPU cores per replica. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#cores PgCluster#cores}
        :param credentials: credentials block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#credentials PgCluster#credentials}
        :param display_name: The friendly name of your cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#display_name PgCluster#display_name}
        :param instances: The total number of instances in the cluster (one master and n-1 standbys). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#instances PgCluster#instances}
        :param location: The physical location where the cluster will be created. This will be where all of your instances live. Property cannot be modified after datacenter creation (disallowed in update requests) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#location PgCluster#location}
        :param postgres_version: The PostgreSQL version of your cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#postgres_version PgCluster#postgres_version}
        :param ram: The amount of memory per instance in megabytes. Has to be a multiple of 1024. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#ram PgCluster#ram}
        :param storage_size: The amount of storage per instance in megabytes. Has to be a multiple of 2048. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#storage_size PgCluster#storage_size}
        :param storage_type: The storage type used in your cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#storage_type PgCluster#storage_type}
        :param synchronization_mode: Represents different modes of replication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#synchronization_mode PgCluster#synchronization_mode}
        :param allow_replace: When set to true, allows the update of immutable fields by destroying and re-creating the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#allow_replace PgCluster#allow_replace}
        :param backup_location: The Object Storage location where the backups will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#backup_location PgCluster#backup_location}
        :param connection_pooler: connection_pooler block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#connection_pooler PgCluster#connection_pooler}
        :param connections: connections block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#connections PgCluster#connections}
        :param from_backup: from_backup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#from_backup PgCluster#from_backup}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#id PgCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance_window: maintenance_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#maintenance_window PgCluster#maintenance_window}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#timeouts PgCluster#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fa2b2c6f2043e70d4e6bfac3934d7ffbf04311cc907c26d678276885c5fd51d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PgClusterConfig(
            cores=cores,
            credentials=credentials,
            display_name=display_name,
            instances=instances,
            location=location,
            postgres_version=postgres_version,
            ram=ram,
            storage_size=storage_size,
            storage_type=storage_type,
            synchronization_mode=synchronization_mode,
            allow_replace=allow_replace,
            backup_location=backup_location,
            connection_pooler=connection_pooler,
            connections=connections,
            from_backup=from_backup,
            id=id,
            maintenance_window=maintenance_window,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a PgCluster resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PgCluster to import.
        :param import_from_id: The id of the existing PgCluster that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PgCluster to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4da6b8180ad0f95b39fc7e480b6a76a593f921fdd3f47e87907c035eb6fef2f4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConnectionPooler")
    def put_connection_pooler(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        pool_mode: builtins.str,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#enabled PgCluster#enabled}.
        :param pool_mode: Represents different modes of connection pooling for the connection pooler. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#pool_mode PgCluster#pool_mode}
        '''
        value = PgClusterConnectionPooler(enabled=enabled, pool_mode=pool_mode)

        return typing.cast(None, jsii.invoke(self, "putConnectionPooler", [value]))

    @jsii.member(jsii_name="putConnections")
    def put_connections(
        self,
        *,
        cidr: builtins.str,
        datacenter_id: builtins.str,
        lan_id: builtins.str,
    ) -> None:
        '''
        :param cidr: The IP and subnet for the database. Note the following unavailable IP ranges: 10.233.64.0/18 10.233.0.0/18 10.233.114.0/24 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#cidr PgCluster#cidr}
        :param datacenter_id: The datacenter to connect your cluster to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#datacenter_id PgCluster#datacenter_id}
        :param lan_id: The LAN to connect your cluster to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#lan_id PgCluster#lan_id}
        '''
        value = PgClusterConnections(
            cidr=cidr, datacenter_id=datacenter_id, lan_id=lan_id
        )

        return typing.cast(None, jsii.invoke(self, "putConnections", [value]))

    @jsii.member(jsii_name="putCredentials")
    def put_credentials(
        self,
        *,
        password: builtins.str,
        username: builtins.str,
    ) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#password PgCluster#password}.
        :param username: the username for the initial postgres user. some system usernames are restricted (e.g. "postgres", "admin", "standby"). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#username PgCluster#username}
        '''
        value = PgClusterCredentials(password=password, username=username)

        return typing.cast(None, jsii.invoke(self, "putCredentials", [value]))

    @jsii.member(jsii_name="putFromBackup")
    def put_from_backup(
        self,
        *,
        backup_id: builtins.str,
        recovery_target_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param backup_id: The unique ID of the backup you want to restore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#backup_id PgCluster#backup_id}
        :param recovery_target_time: If this value is supplied as ISO 8601 timestamp, the backup will be replayed up until the given timestamp. If empty, the backup will be applied completely. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#recovery_target_time PgCluster#recovery_target_time}
        '''
        value = PgClusterFromBackup(
            backup_id=backup_id, recovery_target_time=recovery_target_time
        )

        return typing.cast(None, jsii.invoke(self, "putFromBackup", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        day_of_the_week: builtins.str,
        time: builtins.str,
    ) -> None:
        '''
        :param day_of_the_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#day_of_the_week PgCluster#day_of_the_week}.
        :param time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#time PgCluster#time}.
        '''
        value = PgClusterMaintenanceWindow(day_of_the_week=day_of_the_week, time=time)

        return typing.cast(None, jsii.invoke(self, "putMaintenanceWindow", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#create PgCluster#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#default PgCluster#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#delete PgCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#update PgCluster#update}.
        '''
        value = PgClusterTimeouts(
            create=create, default=default, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAllowReplace")
    def reset_allow_replace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowReplace", []))

    @jsii.member(jsii_name="resetBackupLocation")
    def reset_backup_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupLocation", []))

    @jsii.member(jsii_name="resetConnectionPooler")
    def reset_connection_pooler(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionPooler", []))

    @jsii.member(jsii_name="resetConnections")
    def reset_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnections", []))

    @jsii.member(jsii_name="resetFromBackup")
    def reset_from_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFromBackup", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="connectionPooler")
    def connection_pooler(self) -> "PgClusterConnectionPoolerOutputReference":
        return typing.cast("PgClusterConnectionPoolerOutputReference", jsii.get(self, "connectionPooler"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> "PgClusterConnectionsOutputReference":
        return typing.cast("PgClusterConnectionsOutputReference", jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> "PgClusterCredentialsOutputReference":
        return typing.cast("PgClusterCredentialsOutputReference", jsii.get(self, "credentials"))

    @builtins.property
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property
    @jsii.member(jsii_name="fromBackup")
    def from_backup(self) -> "PgClusterFromBackupOutputReference":
        return typing.cast("PgClusterFromBackupOutputReference", jsii.get(self, "fromBackup"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> "PgClusterMaintenanceWindowOutputReference":
        return typing.cast("PgClusterMaintenanceWindowOutputReference", jsii.get(self, "maintenanceWindow"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "PgClusterTimeoutsOutputReference":
        return typing.cast("PgClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="allowReplaceInput")
    def allow_replace_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowReplaceInput"))

    @builtins.property
    @jsii.member(jsii_name="backupLocationInput")
    def backup_location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupLocationInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionPoolerInput")
    def connection_pooler_input(self) -> typing.Optional["PgClusterConnectionPooler"]:
        return typing.cast(typing.Optional["PgClusterConnectionPooler"], jsii.get(self, "connectionPoolerInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionsInput")
    def connections_input(self) -> typing.Optional["PgClusterConnections"]:
        return typing.cast(typing.Optional["PgClusterConnections"], jsii.get(self, "connectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="coresInput")
    def cores_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coresInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialsInput")
    def credentials_input(self) -> typing.Optional["PgClusterCredentials"]:
        return typing.cast(typing.Optional["PgClusterCredentials"], jsii.get(self, "credentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="fromBackupInput")
    def from_backup_input(self) -> typing.Optional["PgClusterFromBackup"]:
        return typing.cast(typing.Optional["PgClusterFromBackup"], jsii.get(self, "fromBackupInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instancesInput")
    def instances_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instancesInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(self) -> typing.Optional["PgClusterMaintenanceWindow"]:
        return typing.cast(typing.Optional["PgClusterMaintenanceWindow"], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresVersionInput")
    def postgres_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postgresVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="ramInput")
    def ram_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ramInput"))

    @builtins.property
    @jsii.member(jsii_name="storageSizeInput")
    def storage_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "storageSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="storageTypeInput")
    def storage_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="synchronizationModeInput")
    def synchronization_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "synchronizationModeInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PgClusterTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PgClusterTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowReplace")
    def allow_replace(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowReplace"))

    @allow_replace.setter
    def allow_replace(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34a589949ca3fc96f4200fb3ef5e0ea7c44cf7765c8019bde16d7fc7a36f9c4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowReplace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupLocation")
    def backup_location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupLocation"))

    @backup_location.setter
    def backup_location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d797ee277b9e1858ab890b01c5412db18292adc1fc268598ba7b832ee99d706)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupLocation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cores")
    def cores(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cores"))

    @cores.setter
    def cores(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3dce8fdc6d9d541b43e09514ec57c00e6b368cb5e85f75f8a6f11b120aaaf46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cores", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddcc5db9af03ecb4329ac3409922b1c159bbd1b0920005c48cd2d7b95379bf79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ae4efa2b6bbc38787f264e81645d04279bcb1b238067e1f824289d879d93503)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instances")
    def instances(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instances"))

    @instances.setter
    def instances(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13a3ab5b41428a60854b842d2bd6cab4f9c556de4ac1778832ef5099a97da642)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e121054701a6f7acef2d975c985385334691c248413496300d5323de0a29ce7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postgresVersion")
    def postgres_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresVersion"))

    @postgres_version.setter
    def postgres_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcd92944efdc2b8cdba2807053c73f7cc02715a01f8c516e38c573752b3639d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ram")
    def ram(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ram"))

    @ram.setter
    def ram(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14dcf3dbb008d4e170a932a7f9e3aac37c9abab4bfdaffd13156a2908c9f7fe0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ram", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageSize")
    def storage_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storageSize"))

    @storage_size.setter
    def storage_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__543359e56a612f8654febe82fbf7fc963e5384d6f426166ee39aa4133e1efa90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageType")
    def storage_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageType"))

    @storage_type.setter
    def storage_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed4da8445f8d684a899246b3259733633170a04a0ee1f4f874cb30edc8efb4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="synchronizationMode")
    def synchronization_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "synchronizationMode"))

    @synchronization_mode.setter
    def synchronization_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8c718f1fbdf9a86e8d237aa98cefdf0c35daa994080e494f041e2a0657a08e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "synchronizationMode", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cores": "cores",
        "credentials": "credentials",
        "display_name": "displayName",
        "instances": "instances",
        "location": "location",
        "postgres_version": "postgresVersion",
        "ram": "ram",
        "storage_size": "storageSize",
        "storage_type": "storageType",
        "synchronization_mode": "synchronizationMode",
        "allow_replace": "allowReplace",
        "backup_location": "backupLocation",
        "connection_pooler": "connectionPooler",
        "connections": "connections",
        "from_backup": "fromBackup",
        "id": "id",
        "maintenance_window": "maintenanceWindow",
        "timeouts": "timeouts",
    },
)
class PgClusterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cores: jsii.Number,
        credentials: typing.Union["PgClusterCredentials", typing.Dict[builtins.str, typing.Any]],
        display_name: builtins.str,
        instances: jsii.Number,
        location: builtins.str,
        postgres_version: builtins.str,
        ram: jsii.Number,
        storage_size: jsii.Number,
        storage_type: builtins.str,
        synchronization_mode: builtins.str,
        allow_replace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backup_location: typing.Optional[builtins.str] = None,
        connection_pooler: typing.Optional[typing.Union["PgClusterConnectionPooler", typing.Dict[builtins.str, typing.Any]]] = None,
        connections: typing.Optional[typing.Union["PgClusterConnections", typing.Dict[builtins.str, typing.Any]]] = None,
        from_backup: typing.Optional[typing.Union["PgClusterFromBackup", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[typing.Union["PgClusterMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["PgClusterTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cores: The number of CPU cores per replica. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#cores PgCluster#cores}
        :param credentials: credentials block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#credentials PgCluster#credentials}
        :param display_name: The friendly name of your cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#display_name PgCluster#display_name}
        :param instances: The total number of instances in the cluster (one master and n-1 standbys). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#instances PgCluster#instances}
        :param location: The physical location where the cluster will be created. This will be where all of your instances live. Property cannot be modified after datacenter creation (disallowed in update requests) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#location PgCluster#location}
        :param postgres_version: The PostgreSQL version of your cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#postgres_version PgCluster#postgres_version}
        :param ram: The amount of memory per instance in megabytes. Has to be a multiple of 1024. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#ram PgCluster#ram}
        :param storage_size: The amount of storage per instance in megabytes. Has to be a multiple of 2048. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#storage_size PgCluster#storage_size}
        :param storage_type: The storage type used in your cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#storage_type PgCluster#storage_type}
        :param synchronization_mode: Represents different modes of replication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#synchronization_mode PgCluster#synchronization_mode}
        :param allow_replace: When set to true, allows the update of immutable fields by destroying and re-creating the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#allow_replace PgCluster#allow_replace}
        :param backup_location: The Object Storage location where the backups will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#backup_location PgCluster#backup_location}
        :param connection_pooler: connection_pooler block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#connection_pooler PgCluster#connection_pooler}
        :param connections: connections block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#connections PgCluster#connections}
        :param from_backup: from_backup block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#from_backup PgCluster#from_backup}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#id PgCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param maintenance_window: maintenance_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#maintenance_window PgCluster#maintenance_window}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#timeouts PgCluster#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(credentials, dict):
            credentials = PgClusterCredentials(**credentials)
        if isinstance(connection_pooler, dict):
            connection_pooler = PgClusterConnectionPooler(**connection_pooler)
        if isinstance(connections, dict):
            connections = PgClusterConnections(**connections)
        if isinstance(from_backup, dict):
            from_backup = PgClusterFromBackup(**from_backup)
        if isinstance(maintenance_window, dict):
            maintenance_window = PgClusterMaintenanceWindow(**maintenance_window)
        if isinstance(timeouts, dict):
            timeouts = PgClusterTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1fbe9e47e2bf954614d9c40bdb61844d9b4f08189b99f1334cbb3b1be205a03)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cores", value=cores, expected_type=type_hints["cores"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument instances", value=instances, expected_type=type_hints["instances"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument postgres_version", value=postgres_version, expected_type=type_hints["postgres_version"])
            check_type(argname="argument ram", value=ram, expected_type=type_hints["ram"])
            check_type(argname="argument storage_size", value=storage_size, expected_type=type_hints["storage_size"])
            check_type(argname="argument storage_type", value=storage_type, expected_type=type_hints["storage_type"])
            check_type(argname="argument synchronization_mode", value=synchronization_mode, expected_type=type_hints["synchronization_mode"])
            check_type(argname="argument allow_replace", value=allow_replace, expected_type=type_hints["allow_replace"])
            check_type(argname="argument backup_location", value=backup_location, expected_type=type_hints["backup_location"])
            check_type(argname="argument connection_pooler", value=connection_pooler, expected_type=type_hints["connection_pooler"])
            check_type(argname="argument connections", value=connections, expected_type=type_hints["connections"])
            check_type(argname="argument from_backup", value=from_backup, expected_type=type_hints["from_backup"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument maintenance_window", value=maintenance_window, expected_type=type_hints["maintenance_window"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cores": cores,
            "credentials": credentials,
            "display_name": display_name,
            "instances": instances,
            "location": location,
            "postgres_version": postgres_version,
            "ram": ram,
            "storage_size": storage_size,
            "storage_type": storage_type,
            "synchronization_mode": synchronization_mode,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if allow_replace is not None:
            self._values["allow_replace"] = allow_replace
        if backup_location is not None:
            self._values["backup_location"] = backup_location
        if connection_pooler is not None:
            self._values["connection_pooler"] = connection_pooler
        if connections is not None:
            self._values["connections"] = connections
        if from_backup is not None:
            self._values["from_backup"] = from_backup
        if id is not None:
            self._values["id"] = id
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def cores(self) -> jsii.Number:
        '''The number of CPU cores per replica.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#cores PgCluster#cores}
        '''
        result = self._values.get("cores")
        assert result is not None, "Required property 'cores' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def credentials(self) -> "PgClusterCredentials":
        '''credentials block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#credentials PgCluster#credentials}
        '''
        result = self._values.get("credentials")
        assert result is not None, "Required property 'credentials' is missing"
        return typing.cast("PgClusterCredentials", result)

    @builtins.property
    def display_name(self) -> builtins.str:
        '''The friendly name of your cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#display_name PgCluster#display_name}
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instances(self) -> jsii.Number:
        '''The total number of instances in the cluster (one master and n-1 standbys).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#instances PgCluster#instances}
        '''
        result = self._values.get("instances")
        assert result is not None, "Required property 'instances' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def location(self) -> builtins.str:
        '''The physical location where the cluster will be created.

        This will be where all of your instances live. Property cannot be modified after datacenter creation (disallowed in update requests)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#location PgCluster#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def postgres_version(self) -> builtins.str:
        '''The PostgreSQL version of your cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#postgres_version PgCluster#postgres_version}
        '''
        result = self._values.get("postgres_version")
        assert result is not None, "Required property 'postgres_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ram(self) -> jsii.Number:
        '''The amount of memory per instance in megabytes. Has to be a multiple of 1024.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#ram PgCluster#ram}
        '''
        result = self._values.get("ram")
        assert result is not None, "Required property 'ram' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_size(self) -> jsii.Number:
        '''The amount of storage per instance in megabytes. Has to be a multiple of 2048.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#storage_size PgCluster#storage_size}
        '''
        result = self._values.get("storage_size")
        assert result is not None, "Required property 'storage_size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def storage_type(self) -> builtins.str:
        '''The storage type used in your cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#storage_type PgCluster#storage_type}
        '''
        result = self._values.get("storage_type")
        assert result is not None, "Required property 'storage_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def synchronization_mode(self) -> builtins.str:
        '''Represents different modes of replication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#synchronization_mode PgCluster#synchronization_mode}
        '''
        result = self._values.get("synchronization_mode")
        assert result is not None, "Required property 'synchronization_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_replace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''When set to true, allows the update of immutable fields by destroying and re-creating the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#allow_replace PgCluster#allow_replace}
        '''
        result = self._values.get("allow_replace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backup_location(self) -> typing.Optional[builtins.str]:
        '''The Object Storage location where the backups will be stored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#backup_location PgCluster#backup_location}
        '''
        result = self._values.get("backup_location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_pooler(self) -> typing.Optional["PgClusterConnectionPooler"]:
        '''connection_pooler block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#connection_pooler PgCluster#connection_pooler}
        '''
        result = self._values.get("connection_pooler")
        return typing.cast(typing.Optional["PgClusterConnectionPooler"], result)

    @builtins.property
    def connections(self) -> typing.Optional["PgClusterConnections"]:
        '''connections block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#connections PgCluster#connections}
        '''
        result = self._values.get("connections")
        return typing.cast(typing.Optional["PgClusterConnections"], result)

    @builtins.property
    def from_backup(self) -> typing.Optional["PgClusterFromBackup"]:
        '''from_backup block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#from_backup PgCluster#from_backup}
        '''
        result = self._values.get("from_backup")
        return typing.cast(typing.Optional["PgClusterFromBackup"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#id PgCluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(self) -> typing.Optional["PgClusterMaintenanceWindow"]:
        '''maintenance_window block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#maintenance_window PgCluster#maintenance_window}
        '''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["PgClusterMaintenanceWindow"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["PgClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#timeouts PgCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["PgClusterTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterConnectionPooler",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "pool_mode": "poolMode"},
)
class PgClusterConnectionPooler:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        pool_mode: builtins.str,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#enabled PgCluster#enabled}.
        :param pool_mode: Represents different modes of connection pooling for the connection pooler. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#pool_mode PgCluster#pool_mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99a05525fc4bba10ad2287e3d4aae5dd6f6fcb967ac0597bae6dc84b0e8f4d7d)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument pool_mode", value=pool_mode, expected_type=type_hints["pool_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "enabled": enabled,
            "pool_mode": pool_mode,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#enabled PgCluster#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def pool_mode(self) -> builtins.str:
        '''Represents different modes of connection pooling for the connection pooler.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#pool_mode PgCluster#pool_mode}
        '''
        result = self._values.get("pool_mode")
        assert result is not None, "Required property 'pool_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterConnectionPooler(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PgClusterConnectionPoolerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterConnectionPoolerOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b1d8a87cd5b8fd6f361b22b432081736ac0e75ab768125de858ddf366dd5e72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="poolModeInput")
    def pool_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "poolModeInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30e5613ffb6ef95bb4eb80c9634263e36dcf7c735647912be22a473419281493)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="poolMode")
    def pool_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "poolMode"))

    @pool_mode.setter
    def pool_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72ef847f8438ca96ee493932ff3f7bf38ed8ac1dc6380625eb2e6de5bb11b88c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "poolMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PgClusterConnectionPooler]:
        return typing.cast(typing.Optional[PgClusterConnectionPooler], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PgClusterConnectionPooler]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a0fca67163a8763355ea0d61ae31a1c7758ec376e4292c4507442783ebab27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterConnections",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr", "datacenter_id": "datacenterId", "lan_id": "lanId"},
)
class PgClusterConnections:
    def __init__(
        self,
        *,
        cidr: builtins.str,
        datacenter_id: builtins.str,
        lan_id: builtins.str,
    ) -> None:
        '''
        :param cidr: The IP and subnet for the database. Note the following unavailable IP ranges: 10.233.64.0/18 10.233.0.0/18 10.233.114.0/24 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#cidr PgCluster#cidr}
        :param datacenter_id: The datacenter to connect your cluster to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#datacenter_id PgCluster#datacenter_id}
        :param lan_id: The LAN to connect your cluster to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#lan_id PgCluster#lan_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ba3a2cb3d3795824fac49aed31af127315831ec72dc16100585e32f17bfbb51)
            check_type(argname="argument cidr", value=cidr, expected_type=type_hints["cidr"])
            check_type(argname="argument datacenter_id", value=datacenter_id, expected_type=type_hints["datacenter_id"])
            check_type(argname="argument lan_id", value=lan_id, expected_type=type_hints["lan_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cidr": cidr,
            "datacenter_id": datacenter_id,
            "lan_id": lan_id,
        }

    @builtins.property
    def cidr(self) -> builtins.str:
        '''The IP and subnet for the database.

        Note the following unavailable IP ranges:
        10.233.64.0/18
        10.233.0.0/18
        10.233.114.0/24

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#cidr PgCluster#cidr}
        '''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datacenter_id(self) -> builtins.str:
        '''The datacenter to connect your cluster to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#datacenter_id PgCluster#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        assert result is not None, "Required property 'datacenter_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lan_id(self) -> builtins.str:
        '''The LAN to connect your cluster to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#lan_id PgCluster#lan_id}
        '''
        result = self._values.get("lan_id")
        assert result is not None, "Required property 'lan_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterConnections(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PgClusterConnectionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterConnectionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ed5ea8eeab859e22b46ebe3bafae92ed1be26a8578c48b0028b94d115224757)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="cidrInput")
    def cidr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cidrInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterIdInput")
    def datacenter_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="lanIdInput")
    def lan_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lanIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cidr")
    def cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cidr"))

    @cidr.setter
    def cidr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3ad0c14f54e861085123db5185ac9e6cee28781de5bec682dcbefd01d5b1a2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f70803b75d021a7cd0d911fd7bd048fe26119650b73084b42b208a9b419975ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanId")
    def lan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lanId"))

    @lan_id.setter
    def lan_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed41809e0aa1a1a45679516d1486d9b0bfcf7f79f5b5e3f3bd433bc23d90c4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PgClusterConnections]:
        return typing.cast(typing.Optional[PgClusterConnections], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PgClusterConnections]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbec246a8c250594bb38d7c7f6d687a69e242e1f72968990be26836b54748ccf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterCredentials",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class PgClusterCredentials:
    def __init__(self, *, password: builtins.str, username: builtins.str) -> None:
        '''
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#password PgCluster#password}.
        :param username: the username for the initial postgres user. some system usernames are restricted (e.g. "postgres", "admin", "standby"). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#username PgCluster#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd9b88d3ca31a321d862e729c86edad56b9d43314dd4e244638a4bb532b58ba0)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#password PgCluster#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''the username for the initial postgres user. some system usernames are restricted (e.g. "postgres", "admin", "standby").

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#username PgCluster#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterCredentials(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PgClusterCredentialsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterCredentialsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8746a745a22db7d4ac45bef500b77abaf6959bc2cc4ba4c7cda5190f31f76296)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a0652d0e6fdea4bcd2ea794e0ee0f4412b53c41c21c7eb5f6b2bf77edda5821)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ed8ad2145362d908c3f1b20df53e5b982b7464d1f57ac0b07fc04cf58cd5ab6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PgClusterCredentials]:
        return typing.cast(typing.Optional[PgClusterCredentials], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PgClusterCredentials]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1b6d736ceeeeaf75b75b24c50037b18871e2987412655210ff735f475d67d53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterFromBackup",
    jsii_struct_bases=[],
    name_mapping={
        "backup_id": "backupId",
        "recovery_target_time": "recoveryTargetTime",
    },
)
class PgClusterFromBackup:
    def __init__(
        self,
        *,
        backup_id: builtins.str,
        recovery_target_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param backup_id: The unique ID of the backup you want to restore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#backup_id PgCluster#backup_id}
        :param recovery_target_time: If this value is supplied as ISO 8601 timestamp, the backup will be replayed up until the given timestamp. If empty, the backup will be applied completely. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#recovery_target_time PgCluster#recovery_target_time}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27fc3fb4e4760bc5e53657550efb22dd20f5bfd9b276e880d41209745a31f7b8)
            check_type(argname="argument backup_id", value=backup_id, expected_type=type_hints["backup_id"])
            check_type(argname="argument recovery_target_time", value=recovery_target_time, expected_type=type_hints["recovery_target_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backup_id": backup_id,
        }
        if recovery_target_time is not None:
            self._values["recovery_target_time"] = recovery_target_time

    @builtins.property
    def backup_id(self) -> builtins.str:
        '''The unique ID of the backup you want to restore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#backup_id PgCluster#backup_id}
        '''
        result = self._values.get("backup_id")
        assert result is not None, "Required property 'backup_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def recovery_target_time(self) -> typing.Optional[builtins.str]:
        '''If this value is supplied as ISO 8601 timestamp, the backup will be replayed up until the given timestamp.

        If empty, the backup will be applied completely.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#recovery_target_time PgCluster#recovery_target_time}
        '''
        result = self._values.get("recovery_target_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterFromBackup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PgClusterFromBackupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterFromBackupOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0693b16b89557fc8b3452f216bc141f41ad69e43cc96abba62db9f68bf98432)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetRecoveryTargetTime")
    def reset_recovery_target_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecoveryTargetTime", []))

    @builtins.property
    @jsii.member(jsii_name="backupIdInput")
    def backup_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupIdInput"))

    @builtins.property
    @jsii.member(jsii_name="recoveryTargetTimeInput")
    def recovery_target_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recoveryTargetTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="backupId")
    def backup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupId"))

    @backup_id.setter
    def backup_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3a8e58a814a882143ab45f8ad4a27aac6905ec33f06fc6f1943c4536d5141b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="recoveryTargetTime")
    def recovery_target_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "recoveryTargetTime"))

    @recovery_target_time.setter
    def recovery_target_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e6d42640d27051a5d56aa2dd43b1714907334ec6269f4eaef118fb802d768ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recoveryTargetTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PgClusterFromBackup]:
        return typing.cast(typing.Optional[PgClusterFromBackup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PgClusterFromBackup]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c2e75aeb5255c82895a501477c017a04071318242bc4fde9b7c35e57ea0b46f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"day_of_the_week": "dayOfTheWeek", "time": "time"},
)
class PgClusterMaintenanceWindow:
    def __init__(self, *, day_of_the_week: builtins.str, time: builtins.str) -> None:
        '''
        :param day_of_the_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#day_of_the_week PgCluster#day_of_the_week}.
        :param time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#time PgCluster#time}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35afb442671dd722b187d29bd4540294194918f79fdb1e1ceacae7d721c1f0ad)
            check_type(argname="argument day_of_the_week", value=day_of_the_week, expected_type=type_hints["day_of_the_week"])
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "day_of_the_week": day_of_the_week,
            "time": time,
        }

    @builtins.property
    def day_of_the_week(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#day_of_the_week PgCluster#day_of_the_week}.'''
        result = self._values.get("day_of_the_week")
        assert result is not None, "Required property 'day_of_the_week' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def time(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#time PgCluster#time}.'''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PgClusterMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterMaintenanceWindowOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f037fc1fd772c8e6d2aad949c37d16285cad314361883b34036186934971d06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="dayOfTheWeekInput")
    def day_of_the_week_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dayOfTheWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="timeInput")
    def time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfTheWeek")
    def day_of_the_week(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dayOfTheWeek"))

    @day_of_the_week.setter
    def day_of_the_week(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6769d3400bd41398c3b6204f4a3c4125c239d7b5ddc9135b40a53671f4ca2e72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfTheWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="time")
    def time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "time"))

    @time.setter
    def time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66cfb1a7e9a2276a369c5d8aca07afc06f51e41614a819a529e27f40b16f273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "time", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PgClusterMaintenanceWindow]:
        return typing.cast(typing.Optional[PgClusterMaintenanceWindow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PgClusterMaintenanceWindow],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00c95919470a516b25ae27d4598c24246e51913da60a308f62a79601d8e9025d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "default": "default",
        "delete": "delete",
        "update": "update",
    },
)
class PgClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#create PgCluster#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#default PgCluster#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#delete PgCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#update PgCluster#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d10a4f7b5456f5079161aec2a8e884048ab8f40dba2d2657f1cb91a3224cf9f)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument default", value=default, expected_type=type_hints["default"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if default is not None:
            self._values["default"] = default
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#create PgCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#default PgCluster#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#delete PgCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/pg_cluster#update PgCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PgClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PgClusterTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.pgCluster.PgClusterTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d4372edd0c60f37ccc78756624b0830ca44ceb7c07bf978546ca4993a5ae44)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDefault")
    def reset_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefault", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultInput")
    def default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cec671f49d35c3bfc3009b3f86f6d9571646fde872ab6614f7a2fcc023503dd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__702bb7b13a71042fda9ab6c2f94bcb12920dabbeb68169be99d9faf4ea210e00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04ce81d5cf9743f0a6d11498ca84fcf9382f07df8579a4801072c1b9a28ebb3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6d05aedca3d0feb1628fbb4d1204848bab6a609152414d23c72100f634412fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PgClusterTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PgClusterTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PgClusterTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ddd70bb7450d91edce3c1ff98e37b8d291353b662a62c14aa0097986612d1b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PgCluster",
    "PgClusterConfig",
    "PgClusterConnectionPooler",
    "PgClusterConnectionPoolerOutputReference",
    "PgClusterConnections",
    "PgClusterConnectionsOutputReference",
    "PgClusterCredentials",
    "PgClusterCredentialsOutputReference",
    "PgClusterFromBackup",
    "PgClusterFromBackupOutputReference",
    "PgClusterMaintenanceWindow",
    "PgClusterMaintenanceWindowOutputReference",
    "PgClusterTimeouts",
    "PgClusterTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__1fa2b2c6f2043e70d4e6bfac3934d7ffbf04311cc907c26d678276885c5fd51d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cores: jsii.Number,
    credentials: typing.Union[PgClusterCredentials, typing.Dict[builtins.str, typing.Any]],
    display_name: builtins.str,
    instances: jsii.Number,
    location: builtins.str,
    postgres_version: builtins.str,
    ram: jsii.Number,
    storage_size: jsii.Number,
    storage_type: builtins.str,
    synchronization_mode: builtins.str,
    allow_replace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backup_location: typing.Optional[builtins.str] = None,
    connection_pooler: typing.Optional[typing.Union[PgClusterConnectionPooler, typing.Dict[builtins.str, typing.Any]]] = None,
    connections: typing.Optional[typing.Union[PgClusterConnections, typing.Dict[builtins.str, typing.Any]]] = None,
    from_backup: typing.Optional[typing.Union[PgClusterFromBackup, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance_window: typing.Optional[typing.Union[PgClusterMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[PgClusterTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4da6b8180ad0f95b39fc7e480b6a76a593f921fdd3f47e87907c035eb6fef2f4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a589949ca3fc96f4200fb3ef5e0ea7c44cf7765c8019bde16d7fc7a36f9c4a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d797ee277b9e1858ab890b01c5412db18292adc1fc268598ba7b832ee99d706(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3dce8fdc6d9d541b43e09514ec57c00e6b368cb5e85f75f8a6f11b120aaaf46(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddcc5db9af03ecb4329ac3409922b1c159bbd1b0920005c48cd2d7b95379bf79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae4efa2b6bbc38787f264e81645d04279bcb1b238067e1f824289d879d93503(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13a3ab5b41428a60854b842d2bd6cab4f9c556de4ac1778832ef5099a97da642(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e121054701a6f7acef2d975c985385334691c248413496300d5323de0a29ce7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcd92944efdc2b8cdba2807053c73f7cc02715a01f8c516e38c573752b3639d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14dcf3dbb008d4e170a932a7f9e3aac37c9abab4bfdaffd13156a2908c9f7fe0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__543359e56a612f8654febe82fbf7fc963e5384d6f426166ee39aa4133e1efa90(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ed4da8445f8d684a899246b3259733633170a04a0ee1f4f874cb30edc8efb4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8c718f1fbdf9a86e8d237aa98cefdf0c35daa994080e494f041e2a0657a08e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1fbe9e47e2bf954614d9c40bdb61844d9b4f08189b99f1334cbb3b1be205a03(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cores: jsii.Number,
    credentials: typing.Union[PgClusterCredentials, typing.Dict[builtins.str, typing.Any]],
    display_name: builtins.str,
    instances: jsii.Number,
    location: builtins.str,
    postgres_version: builtins.str,
    ram: jsii.Number,
    storage_size: jsii.Number,
    storage_type: builtins.str,
    synchronization_mode: builtins.str,
    allow_replace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backup_location: typing.Optional[builtins.str] = None,
    connection_pooler: typing.Optional[typing.Union[PgClusterConnectionPooler, typing.Dict[builtins.str, typing.Any]]] = None,
    connections: typing.Optional[typing.Union[PgClusterConnections, typing.Dict[builtins.str, typing.Any]]] = None,
    from_backup: typing.Optional[typing.Union[PgClusterFromBackup, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    maintenance_window: typing.Optional[typing.Union[PgClusterMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[PgClusterTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99a05525fc4bba10ad2287e3d4aae5dd6f6fcb967ac0597bae6dc84b0e8f4d7d(
    *,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    pool_mode: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b1d8a87cd5b8fd6f361b22b432081736ac0e75ab768125de858ddf366dd5e72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30e5613ffb6ef95bb4eb80c9634263e36dcf7c735647912be22a473419281493(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72ef847f8438ca96ee493932ff3f7bf38ed8ac1dc6380625eb2e6de5bb11b88c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a0fca67163a8763355ea0d61ae31a1c7758ec376e4292c4507442783ebab27(
    value: typing.Optional[PgClusterConnectionPooler],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ba3a2cb3d3795824fac49aed31af127315831ec72dc16100585e32f17bfbb51(
    *,
    cidr: builtins.str,
    datacenter_id: builtins.str,
    lan_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ed5ea8eeab859e22b46ebe3bafae92ed1be26a8578c48b0028b94d115224757(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ad0c14f54e861085123db5185ac9e6cee28781de5bec682dcbefd01d5b1a2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f70803b75d021a7cd0d911fd7bd048fe26119650b73084b42b208a9b419975ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ed41809e0aa1a1a45679516d1486d9b0bfcf7f79f5b5e3f3bd433bc23d90c4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbec246a8c250594bb38d7c7f6d687a69e242e1f72968990be26836b54748ccf(
    value: typing.Optional[PgClusterConnections],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd9b88d3ca31a321d862e729c86edad56b9d43314dd4e244638a4bb532b58ba0(
    *,
    password: builtins.str,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8746a745a22db7d4ac45bef500b77abaf6959bc2cc4ba4c7cda5190f31f76296(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a0652d0e6fdea4bcd2ea794e0ee0f4412b53c41c21c7eb5f6b2bf77edda5821(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ed8ad2145362d908c3f1b20df53e5b982b7464d1f57ac0b07fc04cf58cd5ab6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1b6d736ceeeeaf75b75b24c50037b18871e2987412655210ff735f475d67d53(
    value: typing.Optional[PgClusterCredentials],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27fc3fb4e4760bc5e53657550efb22dd20f5bfd9b276e880d41209745a31f7b8(
    *,
    backup_id: builtins.str,
    recovery_target_time: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0693b16b89557fc8b3452f216bc141f41ad69e43cc96abba62db9f68bf98432(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a8e58a814a882143ab45f8ad4a27aac6905ec33f06fc6f1943c4536d5141b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e6d42640d27051a5d56aa2dd43b1714907334ec6269f4eaef118fb802d768ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c2e75aeb5255c82895a501477c017a04071318242bc4fde9b7c35e57ea0b46f(
    value: typing.Optional[PgClusterFromBackup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35afb442671dd722b187d29bd4540294194918f79fdb1e1ceacae7d721c1f0ad(
    *,
    day_of_the_week: builtins.str,
    time: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f037fc1fd772c8e6d2aad949c37d16285cad314361883b34036186934971d06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6769d3400bd41398c3b6204f4a3c4125c239d7b5ddc9135b40a53671f4ca2e72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66cfb1a7e9a2276a369c5d8aca07afc06f51e41614a819a529e27f40b16f273(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00c95919470a516b25ae27d4598c24246e51913da60a308f62a79601d8e9025d(
    value: typing.Optional[PgClusterMaintenanceWindow],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d10a4f7b5456f5079161aec2a8e884048ab8f40dba2d2657f1cb91a3224cf9f(
    *,
    create: typing.Optional[builtins.str] = None,
    default: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d4372edd0c60f37ccc78756624b0830ca44ceb7c07bf978546ca4993a5ae44(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cec671f49d35c3bfc3009b3f86f6d9571646fde872ab6614f7a2fcc023503dd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__702bb7b13a71042fda9ab6c2f94bcb12920dabbeb68169be99d9faf4ea210e00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04ce81d5cf9743f0a6d11498ca84fcf9382f07df8579a4801072c1b9a28ebb3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d05aedca3d0feb1628fbb4d1204848bab6a609152414d23c72100f634412fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ddd70bb7450d91edce3c1ff98e37b8d291353b662a62c14aa0097986612d1b3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PgClusterTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
