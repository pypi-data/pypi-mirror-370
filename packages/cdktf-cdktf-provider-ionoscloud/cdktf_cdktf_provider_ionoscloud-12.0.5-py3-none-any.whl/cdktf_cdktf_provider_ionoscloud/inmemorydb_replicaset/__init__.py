r'''
# `ionoscloud_inmemorydb_replicaset`

Refer to the Terraform Registry for docs: [`ionoscloud_inmemorydb_replicaset`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset).
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


class InmemorydbReplicaset(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicaset",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset ionoscloud_inmemorydb_replicaset}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        connections: typing.Union["InmemorydbReplicasetConnections", typing.Dict[builtins.str, typing.Any]],
        credentials: typing.Union["InmemorydbReplicasetCredentials", typing.Dict[builtins.str, typing.Any]],
        display_name: builtins.str,
        eviction_policy: builtins.str,
        persistence_mode: builtins.str,
        replicas: jsii.Number,
        resources: typing.Union["InmemorydbReplicasetResources", typing.Dict[builtins.str, typing.Any]],
        version: builtins.str,
        id: typing.Optional[builtins.str] = None,
        initial_snapshot_id: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[typing.Union["InmemorydbReplicasetMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["InmemorydbReplicasetTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset ionoscloud_inmemorydb_replicaset} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connections: connections block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#connections InmemorydbReplicaset#connections}
        :param credentials: credentials block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#credentials InmemorydbReplicaset#credentials}
        :param display_name: The human readable name of your replica set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#display_name InmemorydbReplicaset#display_name}
        :param eviction_policy: The eviction policy for the replica set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#eviction_policy InmemorydbReplicaset#eviction_policy}
        :param persistence_mode: Specifies How and If data is persisted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#persistence_mode InmemorydbReplicaset#persistence_mode}
        :param replicas: The total number of replicas in the replica set (one active and n-1 passive). In case of a standalone instance, the value is 1. In all other cases, the value is > 1. The replicas will not be available as read replicas, they are only standby for a failure of the active instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#replicas InmemorydbReplicaset#replicas}
        :param resources: resources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#resources InmemorydbReplicaset#resources}
        :param version: The InMemoryDB version of your replica set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#version InmemorydbReplicaset#version}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#id InmemorydbReplicaset#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param initial_snapshot_id: The ID of a snapshot to restore the replica set from. If set, the replica set will be created from the snapshot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#initial_snapshot_id InmemorydbReplicaset#initial_snapshot_id}
        :param location: The replica set location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#location InmemorydbReplicaset#location}
        :param maintenance_window: maintenance_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#maintenance_window InmemorydbReplicaset#maintenance_window}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#timeouts InmemorydbReplicaset#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e04212e8faad4b36c73415255bcf12bd749e454df91f5398f5bff5de45236f0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = InmemorydbReplicasetConfig(
            connections=connections,
            credentials=credentials,
            display_name=display_name,
            eviction_policy=eviction_policy,
            persistence_mode=persistence_mode,
            replicas=replicas,
            resources=resources,
            version=version,
            id=id,
            initial_snapshot_id=initial_snapshot_id,
            location=location,
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
        '''Generates CDKTF code for importing a InmemorydbReplicaset resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the InmemorydbReplicaset to import.
        :param import_from_id: The id of the existing InmemorydbReplicaset that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the InmemorydbReplicaset to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ddf6c9bd4ff263ac96d4a54125417af55e9a9b529fa3f8f7f72374567e5b381)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConnections")
    def put_connections(
        self,
        *,
        cidr: builtins.str,
        datacenter_id: builtins.str,
        lan_id: builtins.str,
    ) -> None:
        '''
        :param cidr: The IP and subnet for your instance. Note the following unavailable IP ranges: 10.233.64.0/18, 10.233.0.0/18, 10.233.114.0/24. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#cidr InmemorydbReplicaset#cidr}
        :param datacenter_id: The datacenter to connect your instance to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#datacenter_id InmemorydbReplicaset#datacenter_id}
        :param lan_id: The numeric LAN ID to connect your instance to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#lan_id InmemorydbReplicaset#lan_id}
        '''
        value = InmemorydbReplicasetConnections(
            cidr=cidr, datacenter_id=datacenter_id, lan_id=lan_id
        )

        return typing.cast(None, jsii.invoke(self, "putConnections", [value]))

    @jsii.member(jsii_name="putCredentials")
    def put_credentials(
        self,
        *,
        username: builtins.str,
        hashed_password: typing.Optional[typing.Union["InmemorydbReplicasetCredentialsHashedPassword", typing.Dict[builtins.str, typing.Any]]] = None,
        plain_text_password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param username: The username for the initial InMemoryDB user. Some system usernames are restricted (e.g. 'admin', 'standby'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#username InmemorydbReplicaset#username}
        :param hashed_password: hashed_password block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#hashed_password InmemorydbReplicaset#hashed_password}
        :param plain_text_password: The password for a InMemoryDB user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#plain_text_password InmemorydbReplicaset#plain_text_password}
        '''
        value = InmemorydbReplicasetCredentials(
            username=username,
            hashed_password=hashed_password,
            plain_text_password=plain_text_password,
        )

        return typing.cast(None, jsii.invoke(self, "putCredentials", [value]))

    @jsii.member(jsii_name="putMaintenanceWindow")
    def put_maintenance_window(
        self,
        *,
        day_of_the_week: builtins.str,
        time: builtins.str,
    ) -> None:
        '''
        :param day_of_the_week: The name of the week day. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#day_of_the_week InmemorydbReplicaset#day_of_the_week}
        :param time: Start of the maintenance window in UTC time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#time InmemorydbReplicaset#time}
        '''
        value = InmemorydbReplicasetMaintenanceWindow(
            day_of_the_week=day_of_the_week, time=time
        )

        return typing.cast(None, jsii.invoke(self, "putMaintenanceWindow", [value]))

    @jsii.member(jsii_name="putResources")
    def put_resources(self, *, cores: jsii.Number, ram: jsii.Number) -> None:
        '''
        :param cores: The number of CPU cores per instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#cores InmemorydbReplicaset#cores}
        :param ram: The amount of memory per instance in gigabytes (GB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#ram InmemorydbReplicaset#ram}
        '''
        value = InmemorydbReplicasetResources(cores=cores, ram=ram)

        return typing.cast(None, jsii.invoke(self, "putResources", [value]))

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
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#create InmemorydbReplicaset#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#default InmemorydbReplicaset#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#delete InmemorydbReplicaset#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#update InmemorydbReplicaset#update}.
        '''
        value = InmemorydbReplicasetTimeouts(
            create=create, default=default, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInitialSnapshotId")
    def reset_initial_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInitialSnapshotId", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

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
    @jsii.member(jsii_name="connections")
    def connections(self) -> "InmemorydbReplicasetConnectionsOutputReference":
        return typing.cast("InmemorydbReplicasetConnectionsOutputReference", jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> "InmemorydbReplicasetCredentialsOutputReference":
        return typing.cast("InmemorydbReplicasetCredentialsOutputReference", jsii.get(self, "credentials"))

    @builtins.property
    @jsii.member(jsii_name="dnsName")
    def dns_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsName"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(
        self,
    ) -> "InmemorydbReplicasetMaintenanceWindowOutputReference":
        return typing.cast("InmemorydbReplicasetMaintenanceWindowOutputReference", jsii.get(self, "maintenanceWindow"))

    @builtins.property
    @jsii.member(jsii_name="resources")
    def resources(self) -> "InmemorydbReplicasetResourcesOutputReference":
        return typing.cast("InmemorydbReplicasetResourcesOutputReference", jsii.get(self, "resources"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "InmemorydbReplicasetTimeoutsOutputReference":
        return typing.cast("InmemorydbReplicasetTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="connectionsInput")
    def connections_input(self) -> typing.Optional["InmemorydbReplicasetConnections"]:
        return typing.cast(typing.Optional["InmemorydbReplicasetConnections"], jsii.get(self, "connectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="credentialsInput")
    def credentials_input(self) -> typing.Optional["InmemorydbReplicasetCredentials"]:
        return typing.cast(typing.Optional["InmemorydbReplicasetCredentials"], jsii.get(self, "credentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="evictionPolicyInput")
    def eviction_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "evictionPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="initialSnapshotIdInput")
    def initial_snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "initialSnapshotIdInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(
        self,
    ) -> typing.Optional["InmemorydbReplicasetMaintenanceWindow"]:
        return typing.cast(typing.Optional["InmemorydbReplicasetMaintenanceWindow"], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="persistenceModeInput")
    def persistence_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "persistenceModeInput"))

    @builtins.property
    @jsii.member(jsii_name="replicasInput")
    def replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicasInput"))

    @builtins.property
    @jsii.member(jsii_name="resourcesInput")
    def resources_input(self) -> typing.Optional["InmemorydbReplicasetResources"]:
        return typing.cast(typing.Optional["InmemorydbReplicasetResources"], jsii.get(self, "resourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "InmemorydbReplicasetTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "InmemorydbReplicasetTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5c0f923012f413e967877bfeee581d2bebe2edfd1c38f9dcc756bc8ac6ab2f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="evictionPolicy")
    def eviction_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evictionPolicy"))

    @eviction_policy.setter
    def eviction_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b573163c9bdf8dcfa03df605cc5f4a9e32d3c800004eb2f7c85b85df063f1dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "evictionPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b66dec82ec856083102afe0f0f9583aede2e5f9545c31231571430b9f75598a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="initialSnapshotId")
    def initial_snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "initialSnapshotId"))

    @initial_snapshot_id.setter
    def initial_snapshot_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa0e328d092bd80b30b32265f0387e2e55cfc440168a643792b2678608302f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "initialSnapshotId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__442df17b5b0a6dfff6cb71799c57a9349bc08180210d1b4e18494174f7cf8451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistenceMode")
    def persistence_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "persistenceMode"))

    @persistence_mode.setter
    def persistence_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d1c80d765b012f7d67e91242a7ad3bbf697bb0945262fe98d1e9dedab0a0e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistenceMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replicas")
    def replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicas"))

    @replicas.setter
    def replicas(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__febfa35c6a0eb0213a3451da6b00300dec49c8aaa9166366d4e81a9c47ec886b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replicas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c0fd3c121244bbfe4a8dc0a736f5ca12db60a5697f5030e40a2254b3f80acaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "connections": "connections",
        "credentials": "credentials",
        "display_name": "displayName",
        "eviction_policy": "evictionPolicy",
        "persistence_mode": "persistenceMode",
        "replicas": "replicas",
        "resources": "resources",
        "version": "version",
        "id": "id",
        "initial_snapshot_id": "initialSnapshotId",
        "location": "location",
        "maintenance_window": "maintenanceWindow",
        "timeouts": "timeouts",
    },
)
class InmemorydbReplicasetConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        connections: typing.Union["InmemorydbReplicasetConnections", typing.Dict[builtins.str, typing.Any]],
        credentials: typing.Union["InmemorydbReplicasetCredentials", typing.Dict[builtins.str, typing.Any]],
        display_name: builtins.str,
        eviction_policy: builtins.str,
        persistence_mode: builtins.str,
        replicas: jsii.Number,
        resources: typing.Union["InmemorydbReplicasetResources", typing.Dict[builtins.str, typing.Any]],
        version: builtins.str,
        id: typing.Optional[builtins.str] = None,
        initial_snapshot_id: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[typing.Union["InmemorydbReplicasetMaintenanceWindow", typing.Dict[builtins.str, typing.Any]]] = None,
        timeouts: typing.Optional[typing.Union["InmemorydbReplicasetTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param connections: connections block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#connections InmemorydbReplicaset#connections}
        :param credentials: credentials block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#credentials InmemorydbReplicaset#credentials}
        :param display_name: The human readable name of your replica set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#display_name InmemorydbReplicaset#display_name}
        :param eviction_policy: The eviction policy for the replica set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#eviction_policy InmemorydbReplicaset#eviction_policy}
        :param persistence_mode: Specifies How and If data is persisted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#persistence_mode InmemorydbReplicaset#persistence_mode}
        :param replicas: The total number of replicas in the replica set (one active and n-1 passive). In case of a standalone instance, the value is 1. In all other cases, the value is > 1. The replicas will not be available as read replicas, they are only standby for a failure of the active instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#replicas InmemorydbReplicaset#replicas}
        :param resources: resources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#resources InmemorydbReplicaset#resources}
        :param version: The InMemoryDB version of your replica set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#version InmemorydbReplicaset#version}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#id InmemorydbReplicaset#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param initial_snapshot_id: The ID of a snapshot to restore the replica set from. If set, the replica set will be created from the snapshot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#initial_snapshot_id InmemorydbReplicaset#initial_snapshot_id}
        :param location: The replica set location. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#location InmemorydbReplicaset#location}
        :param maintenance_window: maintenance_window block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#maintenance_window InmemorydbReplicaset#maintenance_window}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#timeouts InmemorydbReplicaset#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(connections, dict):
            connections = InmemorydbReplicasetConnections(**connections)
        if isinstance(credentials, dict):
            credentials = InmemorydbReplicasetCredentials(**credentials)
        if isinstance(resources, dict):
            resources = InmemorydbReplicasetResources(**resources)
        if isinstance(maintenance_window, dict):
            maintenance_window = InmemorydbReplicasetMaintenanceWindow(**maintenance_window)
        if isinstance(timeouts, dict):
            timeouts = InmemorydbReplicasetTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0397e0e30f2c4e6c6ed2eec4bbd35726dfb118332b4c4797c2e1afc520dffc5e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument connections", value=connections, expected_type=type_hints["connections"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument eviction_policy", value=eviction_policy, expected_type=type_hints["eviction_policy"])
            check_type(argname="argument persistence_mode", value=persistence_mode, expected_type=type_hints["persistence_mode"])
            check_type(argname="argument replicas", value=replicas, expected_type=type_hints["replicas"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument initial_snapshot_id", value=initial_snapshot_id, expected_type=type_hints["initial_snapshot_id"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument maintenance_window", value=maintenance_window, expected_type=type_hints["maintenance_window"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connections": connections,
            "credentials": credentials,
            "display_name": display_name,
            "eviction_policy": eviction_policy,
            "persistence_mode": persistence_mode,
            "replicas": replicas,
            "resources": resources,
            "version": version,
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
        if id is not None:
            self._values["id"] = id
        if initial_snapshot_id is not None:
            self._values["initial_snapshot_id"] = initial_snapshot_id
        if location is not None:
            self._values["location"] = location
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
    def connections(self) -> "InmemorydbReplicasetConnections":
        '''connections block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#connections InmemorydbReplicaset#connections}
        '''
        result = self._values.get("connections")
        assert result is not None, "Required property 'connections' is missing"
        return typing.cast("InmemorydbReplicasetConnections", result)

    @builtins.property
    def credentials(self) -> "InmemorydbReplicasetCredentials":
        '''credentials block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#credentials InmemorydbReplicaset#credentials}
        '''
        result = self._values.get("credentials")
        assert result is not None, "Required property 'credentials' is missing"
        return typing.cast("InmemorydbReplicasetCredentials", result)

    @builtins.property
    def display_name(self) -> builtins.str:
        '''The human readable name of your replica set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#display_name InmemorydbReplicaset#display_name}
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eviction_policy(self) -> builtins.str:
        '''The eviction policy for the replica set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#eviction_policy InmemorydbReplicaset#eviction_policy}
        '''
        result = self._values.get("eviction_policy")
        assert result is not None, "Required property 'eviction_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def persistence_mode(self) -> builtins.str:
        '''Specifies How and If data is persisted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#persistence_mode InmemorydbReplicaset#persistence_mode}
        '''
        result = self._values.get("persistence_mode")
        assert result is not None, "Required property 'persistence_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def replicas(self) -> jsii.Number:
        '''The total number of replicas in the replica set (one active and n-1 passive).

        In case of a standalone instance, the value is 1. In all other cases, the value is > 1. The replicas will not be available as read replicas, they are only standby for a failure of the active instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#replicas InmemorydbReplicaset#replicas}
        '''
        result = self._values.get("replicas")
        assert result is not None, "Required property 'replicas' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def resources(self) -> "InmemorydbReplicasetResources":
        '''resources block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#resources InmemorydbReplicaset#resources}
        '''
        result = self._values.get("resources")
        assert result is not None, "Required property 'resources' is missing"
        return typing.cast("InmemorydbReplicasetResources", result)

    @builtins.property
    def version(self) -> builtins.str:
        '''The InMemoryDB version of your replica set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#version InmemorydbReplicaset#version}
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#id InmemorydbReplicaset#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initial_snapshot_id(self) -> typing.Optional[builtins.str]:
        '''The ID of a snapshot to restore the replica set from.

        If set, the replica set will be created from the snapshot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#initial_snapshot_id InmemorydbReplicaset#initial_snapshot_id}
        '''
        result = self._values.get("initial_snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''The replica set location.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#location InmemorydbReplicaset#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(
        self,
    ) -> typing.Optional["InmemorydbReplicasetMaintenanceWindow"]:
        '''maintenance_window block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#maintenance_window InmemorydbReplicaset#maintenance_window}
        '''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional["InmemorydbReplicasetMaintenanceWindow"], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["InmemorydbReplicasetTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#timeouts InmemorydbReplicaset#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["InmemorydbReplicasetTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetConnections",
    jsii_struct_bases=[],
    name_mapping={"cidr": "cidr", "datacenter_id": "datacenterId", "lan_id": "lanId"},
)
class InmemorydbReplicasetConnections:
    def __init__(
        self,
        *,
        cidr: builtins.str,
        datacenter_id: builtins.str,
        lan_id: builtins.str,
    ) -> None:
        '''
        :param cidr: The IP and subnet for your instance. Note the following unavailable IP ranges: 10.233.64.0/18, 10.233.0.0/18, 10.233.114.0/24. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#cidr InmemorydbReplicaset#cidr}
        :param datacenter_id: The datacenter to connect your instance to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#datacenter_id InmemorydbReplicaset#datacenter_id}
        :param lan_id: The numeric LAN ID to connect your instance to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#lan_id InmemorydbReplicaset#lan_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57636ebff604b6d80ff6854584954d3a3c2bbea25ad48231b25d065c43181cb5)
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
        '''The IP and subnet for your instance. Note the following unavailable IP ranges: 10.233.64.0/18, 10.233.0.0/18, 10.233.114.0/24.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#cidr InmemorydbReplicaset#cidr}
        '''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def datacenter_id(self) -> builtins.str:
        '''The datacenter to connect your instance to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#datacenter_id InmemorydbReplicaset#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        assert result is not None, "Required property 'datacenter_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lan_id(self) -> builtins.str:
        '''The numeric LAN ID to connect your instance to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#lan_id InmemorydbReplicaset#lan_id}
        '''
        result = self._values.get("lan_id")
        assert result is not None, "Required property 'lan_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetConnections(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InmemorydbReplicasetConnectionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetConnectionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__76d8750a3b1f46e7d92635b3c7a0cd78ca175cf42d8247ca4dc6b7b42906fcd2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16a163638c3d85d831e7d3f8ba1d549250d826b23a1c7c0ae4e9085a4dd3a58e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5778417dbf9568ba8f35273b8cb05978025ccf34b86cd7660b116514dc1b6ae3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lanId")
    def lan_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lanId"))

    @lan_id.setter
    def lan_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d1386166cfcfd0f63cab5c8c56f02d9d07ca48a6c51b3267989bceccc45e72a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lanId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InmemorydbReplicasetConnections]:
        return typing.cast(typing.Optional[InmemorydbReplicasetConnections], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InmemorydbReplicasetConnections],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e51f3bf957dd924de5f877d312967c2e5198791e2926b6439325e2e357f3a04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetCredentials",
    jsii_struct_bases=[],
    name_mapping={
        "username": "username",
        "hashed_password": "hashedPassword",
        "plain_text_password": "plainTextPassword",
    },
)
class InmemorydbReplicasetCredentials:
    def __init__(
        self,
        *,
        username: builtins.str,
        hashed_password: typing.Optional[typing.Union["InmemorydbReplicasetCredentialsHashedPassword", typing.Dict[builtins.str, typing.Any]]] = None,
        plain_text_password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param username: The username for the initial InMemoryDB user. Some system usernames are restricted (e.g. 'admin', 'standby'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#username InmemorydbReplicaset#username}
        :param hashed_password: hashed_password block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#hashed_password InmemorydbReplicaset#hashed_password}
        :param plain_text_password: The password for a InMemoryDB user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#plain_text_password InmemorydbReplicaset#plain_text_password}
        '''
        if isinstance(hashed_password, dict):
            hashed_password = InmemorydbReplicasetCredentialsHashedPassword(**hashed_password)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67704e87244baefd21bf1fe3fc9e9c94b54688042506f26039a4d318213cca69)
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument hashed_password", value=hashed_password, expected_type=type_hints["hashed_password"])
            check_type(argname="argument plain_text_password", value=plain_text_password, expected_type=type_hints["plain_text_password"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "username": username,
        }
        if hashed_password is not None:
            self._values["hashed_password"] = hashed_password
        if plain_text_password is not None:
            self._values["plain_text_password"] = plain_text_password

    @builtins.property
    def username(self) -> builtins.str:
        '''The username for the initial InMemoryDB user. Some system usernames are restricted (e.g. 'admin', 'standby').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#username InmemorydbReplicaset#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hashed_password(
        self,
    ) -> typing.Optional["InmemorydbReplicasetCredentialsHashedPassword"]:
        '''hashed_password block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#hashed_password InmemorydbReplicaset#hashed_password}
        '''
        result = self._values.get("hashed_password")
        return typing.cast(typing.Optional["InmemorydbReplicasetCredentialsHashedPassword"], result)

    @builtins.property
    def plain_text_password(self) -> typing.Optional[builtins.str]:
        '''The password for a InMemoryDB user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#plain_text_password InmemorydbReplicaset#plain_text_password}
        '''
        result = self._values.get("plain_text_password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetCredentials(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetCredentialsHashedPassword",
    jsii_struct_bases=[],
    name_mapping={"algorithm": "algorithm", "hash": "hash"},
)
class InmemorydbReplicasetCredentialsHashedPassword:
    def __init__(self, *, algorithm: builtins.str, hash: builtins.str) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#algorithm InmemorydbReplicaset#algorithm}.
        :param hash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#hash InmemorydbReplicaset#hash}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b668989fe1500f3b1f79ae901f41a8867e08f437fe8d58b3d1663e951d4f342)
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument hash", value=hash, expected_type=type_hints["hash"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "algorithm": algorithm,
            "hash": hash,
        }

    @builtins.property
    def algorithm(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#algorithm InmemorydbReplicaset#algorithm}.'''
        result = self._values.get("algorithm")
        assert result is not None, "Required property 'algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hash(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#hash InmemorydbReplicaset#hash}.'''
        result = self._values.get("hash")
        assert result is not None, "Required property 'hash' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetCredentialsHashedPassword(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InmemorydbReplicasetCredentialsHashedPasswordOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetCredentialsHashedPasswordOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d768c7d28efdc92ad756889bb65f6785c93d506fecdf772ca380658f83b7f443)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="hashInput")
    def hash_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551e142d171996bf4d8b4e2199a5997033e796f3e887357bdcb16b5239a622f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hash")
    def hash(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hash"))

    @hash.setter
    def hash(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a03fca402e2fd564d850eeb316ca57054c36e3e7318a11c2d6914d32f8b8585f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hash", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[InmemorydbReplicasetCredentialsHashedPassword]:
        return typing.cast(typing.Optional[InmemorydbReplicasetCredentialsHashedPassword], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InmemorydbReplicasetCredentialsHashedPassword],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d74b7c77d7f46f044ed639971cd5a9a32c1fcbf38fcfd457a10e8fb958de91de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class InmemorydbReplicasetCredentialsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetCredentialsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c86addb4786a09ca4fa4e0bcd703e3e863cbc37cbd7c2f5a4270d429661cd765)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putHashedPassword")
    def put_hashed_password(
        self,
        *,
        algorithm: builtins.str,
        hash: builtins.str,
    ) -> None:
        '''
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#algorithm InmemorydbReplicaset#algorithm}.
        :param hash: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#hash InmemorydbReplicaset#hash}.
        '''
        value = InmemorydbReplicasetCredentialsHashedPassword(
            algorithm=algorithm, hash=hash
        )

        return typing.cast(None, jsii.invoke(self, "putHashedPassword", [value]))

    @jsii.member(jsii_name="resetHashedPassword")
    def reset_hashed_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashedPassword", []))

    @jsii.member(jsii_name="resetPlainTextPassword")
    def reset_plain_text_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlainTextPassword", []))

    @builtins.property
    @jsii.member(jsii_name="hashedPassword")
    def hashed_password(
        self,
    ) -> InmemorydbReplicasetCredentialsHashedPasswordOutputReference:
        return typing.cast(InmemorydbReplicasetCredentialsHashedPasswordOutputReference, jsii.get(self, "hashedPassword"))

    @builtins.property
    @jsii.member(jsii_name="hashedPasswordInput")
    def hashed_password_input(
        self,
    ) -> typing.Optional[InmemorydbReplicasetCredentialsHashedPassword]:
        return typing.cast(typing.Optional[InmemorydbReplicasetCredentialsHashedPassword], jsii.get(self, "hashedPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="plainTextPasswordInput")
    def plain_text_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "plainTextPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="plainTextPassword")
    def plain_text_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "plainTextPassword"))

    @plain_text_password.setter
    def plain_text_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9996795d3f0fe6ab72904ed1d24bf206099a1826e39e97e72ad9497893fe5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "plainTextPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d379a51c885f0c9c0b7a62f2dc4df114a2bfe9c35818f66142d4a22cca7e985)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InmemorydbReplicasetCredentials]:
        return typing.cast(typing.Optional[InmemorydbReplicasetCredentials], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InmemorydbReplicasetCredentials],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39abbe2a441b17b843a7750cae86a323d14f719f020712ef61f6a85aa95e160e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetMaintenanceWindow",
    jsii_struct_bases=[],
    name_mapping={"day_of_the_week": "dayOfTheWeek", "time": "time"},
)
class InmemorydbReplicasetMaintenanceWindow:
    def __init__(self, *, day_of_the_week: builtins.str, time: builtins.str) -> None:
        '''
        :param day_of_the_week: The name of the week day. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#day_of_the_week InmemorydbReplicaset#day_of_the_week}
        :param time: Start of the maintenance window in UTC time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#time InmemorydbReplicaset#time}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c529fc9bb254aa5366b12e4b12d7933dde125ce8da71d1a9c3414bb4847180)
            check_type(argname="argument day_of_the_week", value=day_of_the_week, expected_type=type_hints["day_of_the_week"])
            check_type(argname="argument time", value=time, expected_type=type_hints["time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "day_of_the_week": day_of_the_week,
            "time": time,
        }

    @builtins.property
    def day_of_the_week(self) -> builtins.str:
        '''The name of the week day.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#day_of_the_week InmemorydbReplicaset#day_of_the_week}
        '''
        result = self._values.get("day_of_the_week")
        assert result is not None, "Required property 'day_of_the_week' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def time(self) -> builtins.str:
        '''Start of the maintenance window in UTC time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#time InmemorydbReplicaset#time}
        '''
        result = self._values.get("time")
        assert result is not None, "Required property 'time' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetMaintenanceWindow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InmemorydbReplicasetMaintenanceWindowOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetMaintenanceWindowOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__619c8053e308831c10d5b11707d7ea71bc324db82804aa9b2df92de49cd7b414)
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
            type_hints = typing.get_type_hints(_typecheckingstub__35d9b6c3fc368b0a087198ec79b65434b8248f4b21653b46327c0cc4dd823f00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfTheWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="time")
    def time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "time"))

    @time.setter
    def time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c713584d76da7af68b5b91024a60c1e9a4675f1af0ea6e738f39b3e3578d680)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "time", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InmemorydbReplicasetMaintenanceWindow]:
        return typing.cast(typing.Optional[InmemorydbReplicasetMaintenanceWindow], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InmemorydbReplicasetMaintenanceWindow],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0cdc04084ddb3b500a0351ba0001db3b3c287f889986bebac14c2356d6e8302)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetResources",
    jsii_struct_bases=[],
    name_mapping={"cores": "cores", "ram": "ram"},
)
class InmemorydbReplicasetResources:
    def __init__(self, *, cores: jsii.Number, ram: jsii.Number) -> None:
        '''
        :param cores: The number of CPU cores per instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#cores InmemorydbReplicaset#cores}
        :param ram: The amount of memory per instance in gigabytes (GB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#ram InmemorydbReplicaset#ram}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d8553df6ccbdf3ec60229719a3822782cd8479a99d6cedb138be4806ef36c52)
            check_type(argname="argument cores", value=cores, expected_type=type_hints["cores"])
            check_type(argname="argument ram", value=ram, expected_type=type_hints["ram"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cores": cores,
            "ram": ram,
        }

    @builtins.property
    def cores(self) -> jsii.Number:
        '''The number of CPU cores per instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#cores InmemorydbReplicaset#cores}
        '''
        result = self._values.get("cores")
        assert result is not None, "Required property 'cores' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def ram(self) -> jsii.Number:
        '''The amount of memory per instance in gigabytes (GB).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#ram InmemorydbReplicaset#ram}
        '''
        result = self._values.get("ram")
        assert result is not None, "Required property 'ram' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InmemorydbReplicasetResourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetResourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e67f3d8f93e8494476103be6f401a3eb8342a7b54dc3b4a5070e70f6425951a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="storage")
    def storage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "storage"))

    @builtins.property
    @jsii.member(jsii_name="coresInput")
    def cores_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coresInput"))

    @builtins.property
    @jsii.member(jsii_name="ramInput")
    def ram_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ramInput"))

    @builtins.property
    @jsii.member(jsii_name="cores")
    def cores(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cores"))

    @cores.setter
    def cores(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0767818e1540182e3a02837c3d74a8e669adb1150207109161536c23cb0fe0cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cores", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ram")
    def ram(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ram"))

    @ram.setter
    def ram(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef635e6c2178c1b4b75d10bb039511d162d34cdfb4e121f99d8d7374081d9fab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ram", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[InmemorydbReplicasetResources]:
        return typing.cast(typing.Optional[InmemorydbReplicasetResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[InmemorydbReplicasetResources],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10821c20264ddfb819cbdcab3851ed0aaa14bcc30ebd4ff4cb287e9a016ddfa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "default": "default",
        "delete": "delete",
        "update": "update",
    },
)
class InmemorydbReplicasetTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#create InmemorydbReplicaset#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#default InmemorydbReplicaset#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#delete InmemorydbReplicaset#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#update InmemorydbReplicaset#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd423c5333f9408dd9626ab5f468dedd62a6a69cb3e12f0644234e05b5adcf96)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#create InmemorydbReplicaset#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#default InmemorydbReplicaset#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#delete InmemorydbReplicaset#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/inmemorydb_replicaset#update InmemorydbReplicaset#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InmemorydbReplicasetTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class InmemorydbReplicasetTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.inmemorydbReplicaset.InmemorydbReplicasetTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__40a6437d913a5f095a2202e2a0f14c0abf668bb852d302b6ae913839be2ae881)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3523dbab4d994fa3e306b479a8e64e86bd1ecd326cb7f7ab0f269307c1efc7fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d68a8b2386a6e8535b3733aaed883aac6d3462dbf1f5aab9f2b7b732f307f0c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65a5dc97c67ad2163fa8ddc05016dab4843f687fb0295f93593d15e880784133)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4084a8051f6e36527aea3e3247e403363c0a621a7834525fa5838f7ec0303dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InmemorydbReplicasetTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InmemorydbReplicasetTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InmemorydbReplicasetTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63c11ad822b45c617ff0b9cd17259fa2ae7acdd717c3930abf1f87fd8b5cf840)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "InmemorydbReplicaset",
    "InmemorydbReplicasetConfig",
    "InmemorydbReplicasetConnections",
    "InmemorydbReplicasetConnectionsOutputReference",
    "InmemorydbReplicasetCredentials",
    "InmemorydbReplicasetCredentialsHashedPassword",
    "InmemorydbReplicasetCredentialsHashedPasswordOutputReference",
    "InmemorydbReplicasetCredentialsOutputReference",
    "InmemorydbReplicasetMaintenanceWindow",
    "InmemorydbReplicasetMaintenanceWindowOutputReference",
    "InmemorydbReplicasetResources",
    "InmemorydbReplicasetResourcesOutputReference",
    "InmemorydbReplicasetTimeouts",
    "InmemorydbReplicasetTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__3e04212e8faad4b36c73415255bcf12bd749e454df91f5398f5bff5de45236f0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    connections: typing.Union[InmemorydbReplicasetConnections, typing.Dict[builtins.str, typing.Any]],
    credentials: typing.Union[InmemorydbReplicasetCredentials, typing.Dict[builtins.str, typing.Any]],
    display_name: builtins.str,
    eviction_policy: builtins.str,
    persistence_mode: builtins.str,
    replicas: jsii.Number,
    resources: typing.Union[InmemorydbReplicasetResources, typing.Dict[builtins.str, typing.Any]],
    version: builtins.str,
    id: typing.Optional[builtins.str] = None,
    initial_snapshot_id: typing.Optional[builtins.str] = None,
    location: typing.Optional[builtins.str] = None,
    maintenance_window: typing.Optional[typing.Union[InmemorydbReplicasetMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[InmemorydbReplicasetTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__7ddf6c9bd4ff263ac96d4a54125417af55e9a9b529fa3f8f7f72374567e5b381(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c0f923012f413e967877bfeee581d2bebe2edfd1c38f9dcc756bc8ac6ab2f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b573163c9bdf8dcfa03df605cc5f4a9e32d3c800004eb2f7c85b85df063f1dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b66dec82ec856083102afe0f0f9583aede2e5f9545c31231571430b9f75598a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa0e328d092bd80b30b32265f0387e2e55cfc440168a643792b2678608302f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__442df17b5b0a6dfff6cb71799c57a9349bc08180210d1b4e18494174f7cf8451(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d1c80d765b012f7d67e91242a7ad3bbf697bb0945262fe98d1e9dedab0a0e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__febfa35c6a0eb0213a3451da6b00300dec49c8aaa9166366d4e81a9c47ec886b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c0fd3c121244bbfe4a8dc0a736f5ca12db60a5697f5030e40a2254b3f80acaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0397e0e30f2c4e6c6ed2eec4bbd35726dfb118332b4c4797c2e1afc520dffc5e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    connections: typing.Union[InmemorydbReplicasetConnections, typing.Dict[builtins.str, typing.Any]],
    credentials: typing.Union[InmemorydbReplicasetCredentials, typing.Dict[builtins.str, typing.Any]],
    display_name: builtins.str,
    eviction_policy: builtins.str,
    persistence_mode: builtins.str,
    replicas: jsii.Number,
    resources: typing.Union[InmemorydbReplicasetResources, typing.Dict[builtins.str, typing.Any]],
    version: builtins.str,
    id: typing.Optional[builtins.str] = None,
    initial_snapshot_id: typing.Optional[builtins.str] = None,
    location: typing.Optional[builtins.str] = None,
    maintenance_window: typing.Optional[typing.Union[InmemorydbReplicasetMaintenanceWindow, typing.Dict[builtins.str, typing.Any]]] = None,
    timeouts: typing.Optional[typing.Union[InmemorydbReplicasetTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57636ebff604b6d80ff6854584954d3a3c2bbea25ad48231b25d065c43181cb5(
    *,
    cidr: builtins.str,
    datacenter_id: builtins.str,
    lan_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d8750a3b1f46e7d92635b3c7a0cd78ca175cf42d8247ca4dc6b7b42906fcd2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16a163638c3d85d831e7d3f8ba1d549250d826b23a1c7c0ae4e9085a4dd3a58e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5778417dbf9568ba8f35273b8cb05978025ccf34b86cd7660b116514dc1b6ae3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d1386166cfcfd0f63cab5c8c56f02d9d07ca48a6c51b3267989bceccc45e72a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e51f3bf957dd924de5f877d312967c2e5198791e2926b6439325e2e357f3a04(
    value: typing.Optional[InmemorydbReplicasetConnections],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67704e87244baefd21bf1fe3fc9e9c94b54688042506f26039a4d318213cca69(
    *,
    username: builtins.str,
    hashed_password: typing.Optional[typing.Union[InmemorydbReplicasetCredentialsHashedPassword, typing.Dict[builtins.str, typing.Any]]] = None,
    plain_text_password: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b668989fe1500f3b1f79ae901f41a8867e08f437fe8d58b3d1663e951d4f342(
    *,
    algorithm: builtins.str,
    hash: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d768c7d28efdc92ad756889bb65f6785c93d506fecdf772ca380658f83b7f443(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551e142d171996bf4d8b4e2199a5997033e796f3e887357bdcb16b5239a622f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a03fca402e2fd564d850eeb316ca57054c36e3e7318a11c2d6914d32f8b8585f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d74b7c77d7f46f044ed639971cd5a9a32c1fcbf38fcfd457a10e8fb958de91de(
    value: typing.Optional[InmemorydbReplicasetCredentialsHashedPassword],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86addb4786a09ca4fa4e0bcd703e3e863cbc37cbd7c2f5a4270d429661cd765(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9996795d3f0fe6ab72904ed1d24bf206099a1826e39e97e72ad9497893fe5c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d379a51c885f0c9c0b7a62f2dc4df114a2bfe9c35818f66142d4a22cca7e985(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39abbe2a441b17b843a7750cae86a323d14f719f020712ef61f6a85aa95e160e(
    value: typing.Optional[InmemorydbReplicasetCredentials],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c529fc9bb254aa5366b12e4b12d7933dde125ce8da71d1a9c3414bb4847180(
    *,
    day_of_the_week: builtins.str,
    time: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__619c8053e308831c10d5b11707d7ea71bc324db82804aa9b2df92de49cd7b414(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35d9b6c3fc368b0a087198ec79b65434b8248f4b21653b46327c0cc4dd823f00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c713584d76da7af68b5b91024a60c1e9a4675f1af0ea6e738f39b3e3578d680(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0cdc04084ddb3b500a0351ba0001db3b3c287f889986bebac14c2356d6e8302(
    value: typing.Optional[InmemorydbReplicasetMaintenanceWindow],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d8553df6ccbdf3ec60229719a3822782cd8479a99d6cedb138be4806ef36c52(
    *,
    cores: jsii.Number,
    ram: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e67f3d8f93e8494476103be6f401a3eb8342a7b54dc3b4a5070e70f6425951a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0767818e1540182e3a02837c3d74a8e669adb1150207109161536c23cb0fe0cc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef635e6c2178c1b4b75d10bb039511d162d34cdfb4e121f99d8d7374081d9fab(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10821c20264ddfb819cbdcab3851ed0aaa14bcc30ebd4ff4cb287e9a016ddfa4(
    value: typing.Optional[InmemorydbReplicasetResources],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd423c5333f9408dd9626ab5f468dedd62a6a69cb3e12f0644234e05b5adcf96(
    *,
    create: typing.Optional[builtins.str] = None,
    default: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40a6437d913a5f095a2202e2a0f14c0abf668bb852d302b6ae913839be2ae881(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3523dbab4d994fa3e306b479a8e64e86bd1ecd326cb7f7ab0f269307c1efc7fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d68a8b2386a6e8535b3733aaed883aac6d3462dbf1f5aab9f2b7b732f307f0c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65a5dc97c67ad2163fa8ddc05016dab4843f687fb0295f93593d15e880784133(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4084a8051f6e36527aea3e3247e403363c0a621a7834525fa5838f7ec0303dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63c11ad822b45c617ff0b9cd17259fa2ae7acdd717c3930abf1f87fd8b5cf840(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, InmemorydbReplicasetTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
