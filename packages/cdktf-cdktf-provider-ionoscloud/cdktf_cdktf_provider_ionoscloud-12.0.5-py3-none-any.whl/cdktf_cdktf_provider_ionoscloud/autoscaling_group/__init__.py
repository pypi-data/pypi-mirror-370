r'''
# `ionoscloud_autoscaling_group`

Refer to the Terraform Registry for docs: [`ionoscloud_autoscaling_group`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group).
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


class AutoscalingGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group ionoscloud_autoscaling_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        datacenter_id: builtins.str,
        max_replica_count: jsii.Number,
        min_replica_count: jsii.Number,
        name: builtins.str,
        policy: typing.Union["AutoscalingGroupPolicy", typing.Dict[builtins.str, typing.Any]],
        replica_configuration: typing.Union["AutoscalingGroupReplicaConfiguration", typing.Dict[builtins.str, typing.Any]],
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["AutoscalingGroupTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group ionoscloud_autoscaling_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param datacenter_id: Unique identifier for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#datacenter_id AutoscalingGroup#datacenter_id}
        :param max_replica_count: The maximum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#max_replica_count AutoscalingGroup#max_replica_count}
        :param min_replica_count: The minimum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#min_replica_count AutoscalingGroup#min_replica_count}
        :param name: User-defined name for the Autoscaling Group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param policy: policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#policy AutoscalingGroup#policy}
        :param replica_configuration: replica_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#replica_configuration AutoscalingGroup#replica_configuration}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#id AutoscalingGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#timeouts AutoscalingGroup#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3146dd62880db8c4a4a679ae36d31172810f23595b23353b8018fae683b4d75)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AutoscalingGroupConfig(
            datacenter_id=datacenter_id,
            max_replica_count=max_replica_count,
            min_replica_count=min_replica_count,
            name=name,
            policy=policy,
            replica_configuration=replica_configuration,
            id=id,
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
        '''Generates CDKTF code for importing a AutoscalingGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AutoscalingGroup to import.
        :param import_from_id: The id of the existing AutoscalingGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AutoscalingGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e086ea468bafd4c868fa25a191755facf3c01266c1ff7a5bb47db0a613324ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putPolicy")
    def put_policy(
        self,
        *,
        metric: builtins.str,
        scale_in_action: typing.Union["AutoscalingGroupPolicyScaleInAction", typing.Dict[builtins.str, typing.Any]],
        scale_in_threshold: jsii.Number,
        scale_out_action: typing.Union["AutoscalingGroupPolicyScaleOutAction", typing.Dict[builtins.str, typing.Any]],
        scale_out_threshold: jsii.Number,
        unit: builtins.str,
        range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric: The Metric that should trigger the scaling actions. Metric values are checked at fixed intervals. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#metric AutoscalingGroup#metric}
        :param scale_in_action: scale_in_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_in_action AutoscalingGroup#scale_in_action}
        :param scale_in_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scale_out_action' property. The value must have a lower minimum delta to the 'scale_in_threshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_in_threshold AutoscalingGroup#scale_in_threshold}
        :param scale_out_action: scale_out_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_out_action AutoscalingGroup#scale_out_action}
        :param scale_out_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scaleOutAction' property. The value must have a lower minimum delta to the 'scaleInThreshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_out_threshold AutoscalingGroup#scale_out_threshold}
        :param unit: Units of the applied Metric. Possible values are: PER_HOUR, PER_MINUTE, PER_SECOND, TOTAL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#unit AutoscalingGroup#unit}
        :param range: Specifies the time range for which the samples are to be aggregated. Must be >= 2 minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#range AutoscalingGroup#range}
        '''
        value = AutoscalingGroupPolicy(
            metric=metric,
            scale_in_action=scale_in_action,
            scale_in_threshold=scale_in_threshold,
            scale_out_action=scale_out_action,
            scale_out_threshold=scale_out_threshold,
            unit=unit,
            range=range,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicy", [value]))

    @jsii.member(jsii_name="putReplicaConfiguration")
    def put_replica_configuration(
        self,
        *,
        availability_zone: builtins.str,
        cores: jsii.Number,
        ram: jsii.Number,
        cpu_family: typing.Optional[builtins.str] = None,
        nic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationNic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        volume: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationVolume", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param availability_zone: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#availability_zone AutoscalingGroup#availability_zone}
        :param cores: The total number of cores for the VMs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cores AutoscalingGroup#cores}
        :param ram: The amount of memory for the VMs in MB, e.g. 2048. Size must be specified in multiples of 256 MB with a minimum of 256 MB; however, if you set ramHotPlug to TRUE then you must use a minimum of 1024 MB. If you set the RAM size more than 240GB, then ramHotPlug will be set to FALSE and can not be set to TRUE unless RAM size not set to less than 240GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#ram AutoscalingGroup#ram}
        :param cpu_family: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cpu_family AutoscalingGroup#cpu_family}
        :param nic: nic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#nic AutoscalingGroup#nic}
        :param volume: volume block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#volume AutoscalingGroup#volume}
        '''
        value = AutoscalingGroupReplicaConfiguration(
            availability_zone=availability_zone,
            cores=cores,
            ram=ram,
            cpu_family=cpu_family,
            nic=nic,
            volume=volume,
        )

        return typing.cast(None, jsii.invoke(self, "putReplicaConfiguration", [value]))

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
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#create AutoscalingGroup#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#default AutoscalingGroup#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#delete AutoscalingGroup#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#update AutoscalingGroup#update}.
        '''
        value = AutoscalingGroupTimeouts(
            create=create, default=default, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> "AutoscalingGroupPolicyOutputReference":
        return typing.cast("AutoscalingGroupPolicyOutputReference", jsii.get(self, "policy"))

    @builtins.property
    @jsii.member(jsii_name="replicaConfiguration")
    def replica_configuration(
        self,
    ) -> "AutoscalingGroupReplicaConfigurationOutputReference":
        return typing.cast("AutoscalingGroupReplicaConfigurationOutputReference", jsii.get(self, "replicaConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "AutoscalingGroupTimeoutsOutputReference":
        return typing.cast("AutoscalingGroupTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="datacenterIdInput")
    def datacenter_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxReplicaCountInput")
    def max_replica_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxReplicaCountInput"))

    @builtins.property
    @jsii.member(jsii_name="minReplicaCountInput")
    def min_replica_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minReplicaCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional["AutoscalingGroupPolicy"]:
        return typing.cast(typing.Optional["AutoscalingGroupPolicy"], jsii.get(self, "policyInput"))

    @builtins.property
    @jsii.member(jsii_name="replicaConfigurationInput")
    def replica_configuration_input(
        self,
    ) -> typing.Optional["AutoscalingGroupReplicaConfiguration"]:
        return typing.cast(typing.Optional["AutoscalingGroupReplicaConfiguration"], jsii.get(self, "replicaConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AutoscalingGroupTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AutoscalingGroupTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa64c750b5399ce01da6d4e11088ee4c48367961ecf1c44f2ee899a04a021b0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0e3648c651a76707b9cd8410b25e85cc93402e8bdbe2fe2fd1bac10b1541429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxReplicaCount")
    def max_replica_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxReplicaCount"))

    @max_replica_count.setter
    def max_replica_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13fac770d256340aac888c3ece63afaf41f65d6645126008b33dd5b5ca9532ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxReplicaCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minReplicaCount")
    def min_replica_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minReplicaCount"))

    @min_replica_count.setter
    def min_replica_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d0b42b145f0bdecd33b6a5f6f29c297e8586a933bda594d5a1926807677d46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minReplicaCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5eec38da3536bf995579a222f399ce03f33ff418f4e09671c17c535e2c8d6bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "datacenter_id": "datacenterId",
        "max_replica_count": "maxReplicaCount",
        "min_replica_count": "minReplicaCount",
        "name": "name",
        "policy": "policy",
        "replica_configuration": "replicaConfiguration",
        "id": "id",
        "timeouts": "timeouts",
    },
)
class AutoscalingGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        datacenter_id: builtins.str,
        max_replica_count: jsii.Number,
        min_replica_count: jsii.Number,
        name: builtins.str,
        policy: typing.Union["AutoscalingGroupPolicy", typing.Dict[builtins.str, typing.Any]],
        replica_configuration: typing.Union["AutoscalingGroupReplicaConfiguration", typing.Dict[builtins.str, typing.Any]],
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["AutoscalingGroupTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param datacenter_id: Unique identifier for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#datacenter_id AutoscalingGroup#datacenter_id}
        :param max_replica_count: The maximum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#max_replica_count AutoscalingGroup#max_replica_count}
        :param min_replica_count: The minimum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#min_replica_count AutoscalingGroup#min_replica_count}
        :param name: User-defined name for the Autoscaling Group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param policy: policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#policy AutoscalingGroup#policy}
        :param replica_configuration: replica_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#replica_configuration AutoscalingGroup#replica_configuration}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#id AutoscalingGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#timeouts AutoscalingGroup#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(policy, dict):
            policy = AutoscalingGroupPolicy(**policy)
        if isinstance(replica_configuration, dict):
            replica_configuration = AutoscalingGroupReplicaConfiguration(**replica_configuration)
        if isinstance(timeouts, dict):
            timeouts = AutoscalingGroupTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58053b66870c47f3bc0ab5e617378b61c4bb34d67bb04bc14365e28392ae1fa3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument datacenter_id", value=datacenter_id, expected_type=type_hints["datacenter_id"])
            check_type(argname="argument max_replica_count", value=max_replica_count, expected_type=type_hints["max_replica_count"])
            check_type(argname="argument min_replica_count", value=min_replica_count, expected_type=type_hints["min_replica_count"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument replica_configuration", value=replica_configuration, expected_type=type_hints["replica_configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datacenter_id": datacenter_id,
            "max_replica_count": max_replica_count,
            "min_replica_count": min_replica_count,
            "name": name,
            "policy": policy,
            "replica_configuration": replica_configuration,
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
    def datacenter_id(self) -> builtins.str:
        '''Unique identifier for the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#datacenter_id AutoscalingGroup#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        assert result is not None, "Required property 'datacenter_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_replica_count(self) -> jsii.Number:
        '''The maximum value for the number of replicas on a VM Auto Scaling Group.

        Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#max_replica_count AutoscalingGroup#max_replica_count}
        '''
        result = self._values.get("max_replica_count")
        assert result is not None, "Required property 'max_replica_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_replica_count(self) -> jsii.Number:
        '''The minimum value for the number of replicas on a VM Auto Scaling Group.

        Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#min_replica_count AutoscalingGroup#min_replica_count}
        '''
        result = self._values.get("min_replica_count")
        assert result is not None, "Required property 'min_replica_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''User-defined name for the Autoscaling Group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> "AutoscalingGroupPolicy":
        '''policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#policy AutoscalingGroup#policy}
        '''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast("AutoscalingGroupPolicy", result)

    @builtins.property
    def replica_configuration(self) -> "AutoscalingGroupReplicaConfiguration":
        '''replica_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#replica_configuration AutoscalingGroup#replica_configuration}
        '''
        result = self._values.get("replica_configuration")
        assert result is not None, "Required property 'replica_configuration' is missing"
        return typing.cast("AutoscalingGroupReplicaConfiguration", result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#id AutoscalingGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["AutoscalingGroupTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#timeouts AutoscalingGroup#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["AutoscalingGroupTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "metric": "metric",
        "scale_in_action": "scaleInAction",
        "scale_in_threshold": "scaleInThreshold",
        "scale_out_action": "scaleOutAction",
        "scale_out_threshold": "scaleOutThreshold",
        "unit": "unit",
        "range": "range",
    },
)
class AutoscalingGroupPolicy:
    def __init__(
        self,
        *,
        metric: builtins.str,
        scale_in_action: typing.Union["AutoscalingGroupPolicyScaleInAction", typing.Dict[builtins.str, typing.Any]],
        scale_in_threshold: jsii.Number,
        scale_out_action: typing.Union["AutoscalingGroupPolicyScaleOutAction", typing.Dict[builtins.str, typing.Any]],
        scale_out_threshold: jsii.Number,
        unit: builtins.str,
        range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric: The Metric that should trigger the scaling actions. Metric values are checked at fixed intervals. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#metric AutoscalingGroup#metric}
        :param scale_in_action: scale_in_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_in_action AutoscalingGroup#scale_in_action}
        :param scale_in_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scale_out_action' property. The value must have a lower minimum delta to the 'scale_in_threshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_in_threshold AutoscalingGroup#scale_in_threshold}
        :param scale_out_action: scale_out_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_out_action AutoscalingGroup#scale_out_action}
        :param scale_out_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scaleOutAction' property. The value must have a lower minimum delta to the 'scaleInThreshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_out_threshold AutoscalingGroup#scale_out_threshold}
        :param unit: Units of the applied Metric. Possible values are: PER_HOUR, PER_MINUTE, PER_SECOND, TOTAL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#unit AutoscalingGroup#unit}
        :param range: Specifies the time range for which the samples are to be aggregated. Must be >= 2 minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#range AutoscalingGroup#range}
        '''
        if isinstance(scale_in_action, dict):
            scale_in_action = AutoscalingGroupPolicyScaleInAction(**scale_in_action)
        if isinstance(scale_out_action, dict):
            scale_out_action = AutoscalingGroupPolicyScaleOutAction(**scale_out_action)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68e702088158ad817c233bb2fdb4a934ac0d83af64565b75932648127031421f)
            check_type(argname="argument metric", value=metric, expected_type=type_hints["metric"])
            check_type(argname="argument scale_in_action", value=scale_in_action, expected_type=type_hints["scale_in_action"])
            check_type(argname="argument scale_in_threshold", value=scale_in_threshold, expected_type=type_hints["scale_in_threshold"])
            check_type(argname="argument scale_out_action", value=scale_out_action, expected_type=type_hints["scale_out_action"])
            check_type(argname="argument scale_out_threshold", value=scale_out_threshold, expected_type=type_hints["scale_out_threshold"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument range", value=range, expected_type=type_hints["range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric": metric,
            "scale_in_action": scale_in_action,
            "scale_in_threshold": scale_in_threshold,
            "scale_out_action": scale_out_action,
            "scale_out_threshold": scale_out_threshold,
            "unit": unit,
        }
        if range is not None:
            self._values["range"] = range

    @builtins.property
    def metric(self) -> builtins.str:
        '''The Metric that should trigger the scaling actions. Metric values are checked at fixed intervals.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#metric AutoscalingGroup#metric}
        '''
        result = self._values.get("metric")
        assert result is not None, "Required property 'metric' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scale_in_action(self) -> "AutoscalingGroupPolicyScaleInAction":
        '''scale_in_action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_in_action AutoscalingGroup#scale_in_action}
        '''
        result = self._values.get("scale_in_action")
        assert result is not None, "Required property 'scale_in_action' is missing"
        return typing.cast("AutoscalingGroupPolicyScaleInAction", result)

    @builtins.property
    def scale_in_threshold(self) -> jsii.Number:
        '''The upper threshold for the value of the 'metric'.

        Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scale_out_action' property. The value must have a lower minimum delta to the 'scale_in_threshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_in_threshold AutoscalingGroup#scale_in_threshold}
        '''
        result = self._values.get("scale_in_threshold")
        assert result is not None, "Required property 'scale_in_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def scale_out_action(self) -> "AutoscalingGroupPolicyScaleOutAction":
        '''scale_out_action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_out_action AutoscalingGroup#scale_out_action}
        '''
        result = self._values.get("scale_out_action")
        assert result is not None, "Required property 'scale_out_action' is missing"
        return typing.cast("AutoscalingGroupPolicyScaleOutAction", result)

    @builtins.property
    def scale_out_threshold(self) -> jsii.Number:
        '''The upper threshold for the value of the 'metric'.

        Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scaleOutAction' property. The value must have a lower minimum delta to the 'scaleInThreshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#scale_out_threshold AutoscalingGroup#scale_out_threshold}
        '''
        result = self._values.get("scale_out_threshold")
        assert result is not None, "Required property 'scale_out_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Units of the applied Metric. Possible values are: PER_HOUR, PER_MINUTE, PER_SECOND, TOTAL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#unit AutoscalingGroup#unit}
        '''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def range(self) -> typing.Optional[builtins.str]:
        '''Specifies the time range for which the samples are to be aggregated. Must be >= 2 minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#range AutoscalingGroup#range}
        '''
        result = self._values.get("range")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3b7f459aba3a8708621521fed4b6fdbc83c8c574108f722c3e9b6b267d9a79de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putScaleInAction")
    def put_scale_in_action(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        delete_volumes: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        cooldown_period: typing.Optional[builtins.str] = None,
        termination_policy_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are removed. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always removed. Note that for 'SCALE_IN' operations, volumes are not deleted after the server is deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param delete_volumes: If set to 'true', when deleting an replica during scale in, any attached volume will also be deleted. When set to 'false', all volumes remain in the datacenter and must be deleted manually. Note that every scale-out creates new volumes. When they are not deleted, they will eventually use all of your contracts resource limits. At this point, scaling out would not be possible anymore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#delete_volumes AutoscalingGroup#delete_volumes}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        :param termination_policy_type: The type of termination policy for the VM Auto Scaling Group to follow a specific pattern for scaling-in replicas. The default termination policy is 'OLDEST_SERVER_FIRST'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#termination_policy_type AutoscalingGroup#termination_policy_type}
        '''
        value = AutoscalingGroupPolicyScaleInAction(
            amount=amount,
            amount_type=amount_type,
            delete_volumes=delete_volumes,
            cooldown_period=cooldown_period,
            termination_policy_type=termination_policy_type,
        )

        return typing.cast(None, jsii.invoke(self, "putScaleInAction", [value]))

    @jsii.member(jsii_name="putScaleOutAction")
    def put_scale_out_action(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        cooldown_period: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are added. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always added or removed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        value = AutoscalingGroupPolicyScaleOutAction(
            amount=amount, amount_type=amount_type, cooldown_period=cooldown_period
        )

        return typing.cast(None, jsii.invoke(self, "putScaleOutAction", [value]))

    @jsii.member(jsii_name="resetRange")
    def reset_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRange", []))

    @builtins.property
    @jsii.member(jsii_name="scaleInAction")
    def scale_in_action(self) -> "AutoscalingGroupPolicyScaleInActionOutputReference":
        return typing.cast("AutoscalingGroupPolicyScaleInActionOutputReference", jsii.get(self, "scaleInAction"))

    @builtins.property
    @jsii.member(jsii_name="scaleOutAction")
    def scale_out_action(self) -> "AutoscalingGroupPolicyScaleOutActionOutputReference":
        return typing.cast("AutoscalingGroupPolicyScaleOutActionOutputReference", jsii.get(self, "scaleOutAction"))

    @builtins.property
    @jsii.member(jsii_name="metricInput")
    def metric_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricInput"))

    @builtins.property
    @jsii.member(jsii_name="rangeInput")
    def range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleInActionInput")
    def scale_in_action_input(
        self,
    ) -> typing.Optional["AutoscalingGroupPolicyScaleInAction"]:
        return typing.cast(typing.Optional["AutoscalingGroupPolicyScaleInAction"], jsii.get(self, "scaleInActionInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleInThresholdInput")
    def scale_in_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scaleInThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleOutActionInput")
    def scale_out_action_input(
        self,
    ) -> typing.Optional["AutoscalingGroupPolicyScaleOutAction"]:
        return typing.cast(typing.Optional["AutoscalingGroupPolicyScaleOutAction"], jsii.get(self, "scaleOutActionInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleOutThresholdInput")
    def scale_out_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scaleOutThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property
    @jsii.member(jsii_name="metric")
    def metric(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metric"))

    @metric.setter
    def metric(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2764da5d65fc915f2a7f0f315e2b9c3725b0991e79391c2ec3b17b384419d949)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metric", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="range")
    def range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "range"))

    @range.setter
    def range(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa5f2570afc38dd5c1a2eb3f43b50274b24280761b7a3ac5f088f4baccb726b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "range", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleInThreshold")
    def scale_in_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scaleInThreshold"))

    @scale_in_threshold.setter
    def scale_in_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6ae6f86524c15798e2b2be53d7412b883d806d85cb08f0b741fb762002c97cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleInThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scaleOutThreshold")
    def scale_out_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scaleOutThreshold"))

    @scale_out_threshold.setter
    def scale_out_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2df5e1d6d313726a46de06118313eb60eb081ffaf64af4424c4c4dae38a0db25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleOutThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd42ad0b6666b52acf4ec9a56d2b7a56b046d162627727f4e01bf8611fbeec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupPolicy]:
        return typing.cast(typing.Optional[AutoscalingGroupPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AutoscalingGroupPolicy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fc8e1835a175893e3aa46a6a9d35b813890d9ba43e8449ce5b5ba63c1aba574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleInAction",
    jsii_struct_bases=[],
    name_mapping={
        "amount": "amount",
        "amount_type": "amountType",
        "delete_volumes": "deleteVolumes",
        "cooldown_period": "cooldownPeriod",
        "termination_policy_type": "terminationPolicyType",
    },
)
class AutoscalingGroupPolicyScaleInAction:
    def __init__(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        delete_volumes: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        cooldown_period: typing.Optional[builtins.str] = None,
        termination_policy_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are removed. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always removed. Note that for 'SCALE_IN' operations, volumes are not deleted after the server is deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param delete_volumes: If set to 'true', when deleting an replica during scale in, any attached volume will also be deleted. When set to 'false', all volumes remain in the datacenter and must be deleted manually. Note that every scale-out creates new volumes. When they are not deleted, they will eventually use all of your contracts resource limits. At this point, scaling out would not be possible anymore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#delete_volumes AutoscalingGroup#delete_volumes}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        :param termination_policy_type: The type of termination policy for the VM Auto Scaling Group to follow a specific pattern for scaling-in replicas. The default termination policy is 'OLDEST_SERVER_FIRST'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#termination_policy_type AutoscalingGroup#termination_policy_type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df38e3cdf7b235f5f6fe179e59631a45c22f33edab46beae2d4c68ce6235f891)
            check_type(argname="argument amount", value=amount, expected_type=type_hints["amount"])
            check_type(argname="argument amount_type", value=amount_type, expected_type=type_hints["amount_type"])
            check_type(argname="argument delete_volumes", value=delete_volumes, expected_type=type_hints["delete_volumes"])
            check_type(argname="argument cooldown_period", value=cooldown_period, expected_type=type_hints["cooldown_period"])
            check_type(argname="argument termination_policy_type", value=termination_policy_type, expected_type=type_hints["termination_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "amount": amount,
            "amount_type": amount_type,
            "delete_volumes": delete_volumes,
        }
        if cooldown_period is not None:
            self._values["cooldown_period"] = cooldown_period
        if termination_policy_type is not None:
            self._values["termination_policy_type"] = termination_policy_type

    @builtins.property
    def amount(self) -> jsii.Number:
        '''When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are removed.

        The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always removed. Note that for 'SCALE_IN' operations, volumes are not deleted after the server is deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        '''
        result = self._values.get("amount")
        assert result is not None, "Required property 'amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def amount_type(self) -> builtins.str:
        '''The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        '''
        result = self._values.get("amount_type")
        assert result is not None, "Required property 'amount_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_volumes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''If set to 'true', when deleting an replica during scale in, any attached volume will also be deleted.

        When set to 'false', all volumes remain in the datacenter and must be deleted manually. Note that every scale-out creates new volumes. When they are not deleted, they will eventually use all of your contracts resource limits. At this point, scaling out would not be possible anymore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#delete_volumes AutoscalingGroup#delete_volumes}
        '''
        result = self._values.get("delete_volumes")
        assert result is not None, "Required property 'delete_volumes' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def cooldown_period(self) -> typing.Optional[builtins.str]:
        '''The minimum time that elapses after the start of this scaling action until the following scaling action is started.

        While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        result = self._values.get("cooldown_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def termination_policy_type(self) -> typing.Optional[builtins.str]:
        '''The type of termination policy for the VM Auto Scaling Group to follow a specific pattern for scaling-in replicas.

        The default termination policy is 'OLDEST_SERVER_FIRST'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#termination_policy_type AutoscalingGroup#termination_policy_type}
        '''
        result = self._values.get("termination_policy_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupPolicyScaleInAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupPolicyScaleInActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleInActionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ea303df8e2d25f599cbf66afd9f6bfe4268a8fbe0494ffb893c7fa19160fb62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCooldownPeriod")
    def reset_cooldown_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldownPeriod", []))

    @jsii.member(jsii_name="resetTerminationPolicyType")
    def reset_termination_policy_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationPolicyType", []))

    @builtins.property
    @jsii.member(jsii_name="amountInput")
    def amount_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "amountInput"))

    @builtins.property
    @jsii.member(jsii_name="amountTypeInput")
    def amount_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amountTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriodInput")
    def cooldown_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cooldownPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteVolumesInput")
    def delete_volumes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteVolumesInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationPolicyTypeInput")
    def termination_policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "terminationPolicyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="amount")
    def amount(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "amount"))

    @amount.setter
    def amount(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204cfc21e156ebe762e24140c5b9b5b53909fdb1c1504d62b7434077e6403cfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="amountType")
    def amount_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amountType"))

    @amount_type.setter
    def amount_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a981dac662cf18dc8dd7ee59ecb8df8d1001f0779f1d0c741940cc0f06e05a89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amountType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriod")
    def cooldown_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cooldownPeriod"))

    @cooldown_period.setter
    def cooldown_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__536be0162f40286b13583f2bdff4f1d3342e75965e5abdff6113eb7a33c1bfc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldownPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteVolumes")
    def delete_volumes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deleteVolumes"))

    @delete_volumes.setter
    def delete_volumes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c3730c0315324813b2ab8c5b73827c72b8bc5e340b1996a216ab5471d01ead)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteVolumes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminationPolicyType")
    def termination_policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "terminationPolicyType"))

    @termination_policy_type.setter
    def termination_policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a450bf2c72d16cb4f5d97e1e020c1f26b63f43573a0d4c42cc7ff9a9d80c6219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationPolicyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupPolicyScaleInAction]:
        return typing.cast(typing.Optional[AutoscalingGroupPolicyScaleInAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupPolicyScaleInAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555c5ec7b1809bb4d55c43985370defd1502475f8f112eab09150d6d2fbdbd70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleOutAction",
    jsii_struct_bases=[],
    name_mapping={
        "amount": "amount",
        "amount_type": "amountType",
        "cooldown_period": "cooldownPeriod",
    },
)
class AutoscalingGroupPolicyScaleOutAction:
    def __init__(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        cooldown_period: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are added. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always added or removed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16787c31ff992b6598a275a4db90ce816824c4ad8fccc7daf7512172120c4a7d)
            check_type(argname="argument amount", value=amount, expected_type=type_hints["amount"])
            check_type(argname="argument amount_type", value=amount_type, expected_type=type_hints["amount_type"])
            check_type(argname="argument cooldown_period", value=cooldown_period, expected_type=type_hints["cooldown_period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "amount": amount,
            "amount_type": amount_type,
        }
        if cooldown_period is not None:
            self._values["cooldown_period"] = cooldown_period

    @builtins.property
    def amount(self) -> jsii.Number:
        '''When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are added.

        The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always added or removed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        '''
        result = self._values.get("amount")
        assert result is not None, "Required property 'amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def amount_type(self) -> builtins.str:
        '''The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        '''
        result = self._values.get("amount_type")
        assert result is not None, "Required property 'amount_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cooldown_period(self) -> typing.Optional[builtins.str]:
        '''The minimum time that elapses after the start of this scaling action until the following scaling action is started.

        While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        result = self._values.get("cooldown_period")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupPolicyScaleOutAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupPolicyScaleOutActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleOutActionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__165b096930701475659b425b1c1d1b799c5e7d92a4f7696b0117b0a8d44a4e02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCooldownPeriod")
    def reset_cooldown_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldownPeriod", []))

    @builtins.property
    @jsii.member(jsii_name="amountInput")
    def amount_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "amountInput"))

    @builtins.property
    @jsii.member(jsii_name="amountTypeInput")
    def amount_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amountTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriodInput")
    def cooldown_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cooldownPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="amount")
    def amount(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "amount"))

    @amount.setter
    def amount(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9d5b374cc13b0ad43c9c58ec95707bfb697ea13f24e2616526adca15048e618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="amountType")
    def amount_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amountType"))

    @amount_type.setter
    def amount_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ceb1e010f2840fd631a64e69ba9bdcad0f6f88bf01f8283d9bb0f3c2285c23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amountType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriod")
    def cooldown_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cooldownPeriod"))

    @cooldown_period.setter
    def cooldown_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ae6465cbf87029321d558b10af2eeca7a6d03f88ab82ab786f8fcd660e6c0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldownPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupPolicyScaleOutAction]:
        return typing.cast(typing.Optional[AutoscalingGroupPolicyScaleOutAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupPolicyScaleOutAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0cca00adac567f779cbb4c62cc55ebdbb7285f2288cabefdea29c0b3565e072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone": "availabilityZone",
        "cores": "cores",
        "ram": "ram",
        "cpu_family": "cpuFamily",
        "nic": "nic",
        "volume": "volume",
    },
)
class AutoscalingGroupReplicaConfiguration:
    def __init__(
        self,
        *,
        availability_zone: builtins.str,
        cores: jsii.Number,
        ram: jsii.Number,
        cpu_family: typing.Optional[builtins.str] = None,
        nic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationNic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        volume: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationVolume", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param availability_zone: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#availability_zone AutoscalingGroup#availability_zone}
        :param cores: The total number of cores for the VMs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cores AutoscalingGroup#cores}
        :param ram: The amount of memory for the VMs in MB, e.g. 2048. Size must be specified in multiples of 256 MB with a minimum of 256 MB; however, if you set ramHotPlug to TRUE then you must use a minimum of 1024 MB. If you set the RAM size more than 240GB, then ramHotPlug will be set to FALSE and can not be set to TRUE unless RAM size not set to less than 240GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#ram AutoscalingGroup#ram}
        :param cpu_family: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cpu_family AutoscalingGroup#cpu_family}
        :param nic: nic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#nic AutoscalingGroup#nic}
        :param volume: volume block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#volume AutoscalingGroup#volume}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9753c8e0b92272664f4f8fa7334c36abeafa315c55a3a421d6b61d3d28fc2a)
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
            check_type(argname="argument cores", value=cores, expected_type=type_hints["cores"])
            check_type(argname="argument ram", value=ram, expected_type=type_hints["ram"])
            check_type(argname="argument cpu_family", value=cpu_family, expected_type=type_hints["cpu_family"])
            check_type(argname="argument nic", value=nic, expected_type=type_hints["nic"])
            check_type(argname="argument volume", value=volume, expected_type=type_hints["volume"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "availability_zone": availability_zone,
            "cores": cores,
            "ram": ram,
        }
        if cpu_family is not None:
            self._values["cpu_family"] = cpu_family
        if nic is not None:
            self._values["nic"] = nic
        if volume is not None:
            self._values["volume"] = volume

    @builtins.property
    def availability_zone(self) -> builtins.str:
        '''The zone where the VMs are created using this configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#availability_zone AutoscalingGroup#availability_zone}
        '''
        result = self._values.get("availability_zone")
        assert result is not None, "Required property 'availability_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cores(self) -> jsii.Number:
        '''The total number of cores for the VMs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cores AutoscalingGroup#cores}
        '''
        result = self._values.get("cores")
        assert result is not None, "Required property 'cores' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def ram(self) -> jsii.Number:
        '''The amount of memory for the VMs in MB, e.g. 2048. Size must be specified in multiples of 256 MB with a minimum of 256 MB; however, if you set ramHotPlug to TRUE then you must use a minimum of 1024 MB. If you set the RAM size more than 240GB, then ramHotPlug will be set to FALSE and can not be set to TRUE unless RAM size not set to less than 240GB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#ram AutoscalingGroup#ram}
        '''
        result = self._values.get("ram")
        assert result is not None, "Required property 'ram' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_family(self) -> typing.Optional[builtins.str]:
        '''The zone where the VMs are created using this configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#cpu_family AutoscalingGroup#cpu_family}
        '''
        result = self._values.get("cpu_family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nic(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNic"]]]:
        '''nic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#nic AutoscalingGroup#nic}
        '''
        result = self._values.get("nic")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNic"]]], result)

    @builtins.property
    def volume(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]]:
        '''volume block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#volume AutoscalingGroup#volume}
        '''
        result = self._values.get("volume")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNic",
    jsii_struct_bases=[],
    name_mapping={
        "lan": "lan",
        "name": "name",
        "dhcp": "dhcp",
        "firewall_active": "firewallActive",
        "firewall_rule": "firewallRule",
        "firewall_type": "firewallType",
        "flow_log": "flowLog",
        "target_group": "targetGroup",
    },
)
class AutoscalingGroupReplicaConfigurationNic:
    def __init__(
        self,
        *,
        lan: jsii.Number,
        name: builtins.str,
        dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firewall_active: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firewall_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationNicFirewallRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
        firewall_type: typing.Optional[builtins.str] = None,
        flow_log: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationNicFlowLog", typing.Dict[builtins.str, typing.Any]]]]] = None,
        target_group: typing.Optional[typing.Union["AutoscalingGroupReplicaConfigurationNicTargetGroup", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param lan: Lan ID for this replica Nic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#lan AutoscalingGroup#lan}
        :param name: Name for this replica NIC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param dhcp: Dhcp flag for this replica Nic. This is an optional attribute with default value of 'true' if not given in the request payload or given as null. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#dhcp AutoscalingGroup#dhcp}
        :param firewall_active: Activate or deactivate the firewall. By default, an active firewall without any defined rules will block all incoming network traffic except for the firewall rules that explicitly allows certain protocols, IP addresses and ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#firewall_active AutoscalingGroup#firewall_active}
        :param firewall_rule: firewall_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#firewall_rule AutoscalingGroup#firewall_rule}
        :param firewall_type: The type of firewall rules that will be allowed on the NIC. If not specified, the default INGRESS value is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#firewall_type AutoscalingGroup#firewall_type}
        :param flow_log: flow_log block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#flow_log AutoscalingGroup#flow_log}
        :param target_group: target_group block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_group AutoscalingGroup#target_group}
        '''
        if isinstance(target_group, dict):
            target_group = AutoscalingGroupReplicaConfigurationNicTargetGroup(**target_group)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7db78f4556b0eba4b01ccef6c2598a45961bb34cbe79a3e74e1752233cc5380)
            check_type(argname="argument lan", value=lan, expected_type=type_hints["lan"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument dhcp", value=dhcp, expected_type=type_hints["dhcp"])
            check_type(argname="argument firewall_active", value=firewall_active, expected_type=type_hints["firewall_active"])
            check_type(argname="argument firewall_rule", value=firewall_rule, expected_type=type_hints["firewall_rule"])
            check_type(argname="argument firewall_type", value=firewall_type, expected_type=type_hints["firewall_type"])
            check_type(argname="argument flow_log", value=flow_log, expected_type=type_hints["flow_log"])
            check_type(argname="argument target_group", value=target_group, expected_type=type_hints["target_group"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lan": lan,
            "name": name,
        }
        if dhcp is not None:
            self._values["dhcp"] = dhcp
        if firewall_active is not None:
            self._values["firewall_active"] = firewall_active
        if firewall_rule is not None:
            self._values["firewall_rule"] = firewall_rule
        if firewall_type is not None:
            self._values["firewall_type"] = firewall_type
        if flow_log is not None:
            self._values["flow_log"] = flow_log
        if target_group is not None:
            self._values["target_group"] = target_group

    @builtins.property
    def lan(self) -> jsii.Number:
        '''Lan ID for this replica Nic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#lan AutoscalingGroup#lan}
        '''
        result = self._values.get("lan")
        assert result is not None, "Required property 'lan' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name for this replica NIC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Dhcp flag for this replica Nic.

        This is an optional attribute with default value of 'true' if not given in the request payload or given as null.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#dhcp AutoscalingGroup#dhcp}
        '''
        result = self._values.get("dhcp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def firewall_active(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Activate or deactivate the firewall.

        By default, an active firewall without any defined rules will block all incoming network traffic except for the firewall rules that explicitly allows certain protocols, IP addresses and ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#firewall_active AutoscalingGroup#firewall_active}
        '''
        result = self._values.get("firewall_active")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def firewall_rule(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNicFirewallRule"]]]:
        '''firewall_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#firewall_rule AutoscalingGroup#firewall_rule}
        '''
        result = self._values.get("firewall_rule")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNicFirewallRule"]]], result)

    @builtins.property
    def firewall_type(self) -> typing.Optional[builtins.str]:
        '''The type of firewall rules that will be allowed on the NIC.

        If not specified, the default INGRESS value is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#firewall_type AutoscalingGroup#firewall_type}
        '''
        result = self._values.get("firewall_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def flow_log(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNicFlowLog"]]]:
        '''flow_log block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#flow_log AutoscalingGroup#flow_log}
        '''
        result = self._values.get("flow_log")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNicFlowLog"]]], result)

    @builtins.property
    def target_group(
        self,
    ) -> typing.Optional["AutoscalingGroupReplicaConfigurationNicTargetGroup"]:
        '''target_group block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_group AutoscalingGroup#target_group}
        '''
        result = self._values.get("target_group")
        return typing.cast(typing.Optional["AutoscalingGroupReplicaConfigurationNicTargetGroup"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationNic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicFirewallRule",
    jsii_struct_bases=[],
    name_mapping={
        "protocol": "protocol",
        "icmp_code": "icmpCode",
        "icmp_type": "icmpType",
        "name": "name",
        "port_range_end": "portRangeEnd",
        "port_range_start": "portRangeStart",
        "source_ip": "sourceIp",
        "source_mac": "sourceMac",
        "target_ip": "targetIp",
        "type": "type",
    },
)
class AutoscalingGroupReplicaConfigurationNicFirewallRule:
    def __init__(
        self,
        *,
        protocol: builtins.str,
        icmp_code: typing.Optional[jsii.Number] = None,
        icmp_type: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        port_range_end: typing.Optional[jsii.Number] = None,
        port_range_start: typing.Optional[jsii.Number] = None,
        source_ip: typing.Optional[builtins.str] = None,
        source_mac: typing.Optional[builtins.str] = None,
        target_ip: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param protocol: The protocol for the rule. The property cannot be modified after its creation (not allowed in update requests). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#protocol AutoscalingGroup#protocol}
        :param icmp_code: Sets the allowed code (from 0 to 254) when ICMP protocol is selected. The value 'null' allows all codes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#icmp_code AutoscalingGroup#icmp_code}
        :param icmp_type: Sets the allowed type (from 0 to 254) if the protocol ICMP is selected. The value 'null' allows all types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#icmp_type AutoscalingGroup#icmp_type}
        :param name: The name of the firewall rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param port_range_end: Sets the end range of the allowed port (from 1 to 65535) if the protocol TCP or UDP is selected. The value 'null' for 'port_range_start' and 'port_range_end' allows all ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port_range_end AutoscalingGroup#port_range_end}
        :param port_range_start: Sets the initial range of the allowed port (from 1 to 65535) if the protocol TCP or UDP is selected. The value 'null' for 'port_range_start' and 'port_range_end' allows all ports. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port_range_start AutoscalingGroup#port_range_start}
        :param source_ip: Only traffic originating from the respective IPv4 address is permitted. The value 'null' allows traffic from any IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#source_ip AutoscalingGroup#source_ip}
        :param source_mac: Only traffic originating from the respective MAC address is permitted. Valid format: 'aa:bb:cc:dd:ee:ff'. The value 'null' allows traffic from any MAC address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#source_mac AutoscalingGroup#source_mac}
        :param target_ip: If the target NIC has multiple IP addresses, only the traffic directed to the respective IP address of the NIC is allowed. The value 'null' allows traffic to any target IP address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_ip AutoscalingGroup#target_ip}
        :param type: The firewall rule type. If not specified, the default value 'INGRESS' is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#type AutoscalingGroup#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ead80a103008af2ecb9a22f3ef774f8e4177150417ab29d7debff34af3d5f9b)
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument icmp_code", value=icmp_code, expected_type=type_hints["icmp_code"])
            check_type(argname="argument icmp_type", value=icmp_type, expected_type=type_hints["icmp_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument port_range_end", value=port_range_end, expected_type=type_hints["port_range_end"])
            check_type(argname="argument port_range_start", value=port_range_start, expected_type=type_hints["port_range_start"])
            check_type(argname="argument source_ip", value=source_ip, expected_type=type_hints["source_ip"])
            check_type(argname="argument source_mac", value=source_mac, expected_type=type_hints["source_mac"])
            check_type(argname="argument target_ip", value=target_ip, expected_type=type_hints["target_ip"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "protocol": protocol,
        }
        if icmp_code is not None:
            self._values["icmp_code"] = icmp_code
        if icmp_type is not None:
            self._values["icmp_type"] = icmp_type
        if name is not None:
            self._values["name"] = name
        if port_range_end is not None:
            self._values["port_range_end"] = port_range_end
        if port_range_start is not None:
            self._values["port_range_start"] = port_range_start
        if source_ip is not None:
            self._values["source_ip"] = source_ip
        if source_mac is not None:
            self._values["source_mac"] = source_mac
        if target_ip is not None:
            self._values["target_ip"] = target_ip
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def protocol(self) -> builtins.str:
        '''The protocol for the rule. The property cannot be modified after its creation (not allowed in update requests).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#protocol AutoscalingGroup#protocol}
        '''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def icmp_code(self) -> typing.Optional[jsii.Number]:
        '''Sets the allowed code (from 0 to 254) when ICMP protocol is selected. The value 'null' allows all codes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#icmp_code AutoscalingGroup#icmp_code}
        '''
        result = self._values.get("icmp_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def icmp_type(self) -> typing.Optional[jsii.Number]:
        '''Sets the allowed type (from 0 to 254) if the protocol ICMP is selected.

        The value 'null' allows all types.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#icmp_type AutoscalingGroup#icmp_type}
        '''
        result = self._values.get("icmp_type")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the firewall rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port_range_end(self) -> typing.Optional[jsii.Number]:
        '''Sets the end range of the allowed port (from 1 to 65535) if the protocol TCP or UDP is selected.

        The value 'null' for 'port_range_start' and 'port_range_end' allows all ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port_range_end AutoscalingGroup#port_range_end}
        '''
        result = self._values.get("port_range_end")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def port_range_start(self) -> typing.Optional[jsii.Number]:
        '''Sets the initial range of the allowed port (from 1 to 65535) if the protocol TCP or UDP is selected.

        The value 'null' for 'port_range_start' and 'port_range_end' allows all ports.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port_range_start AutoscalingGroup#port_range_start}
        '''
        result = self._values.get("port_range_start")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def source_ip(self) -> typing.Optional[builtins.str]:
        '''Only traffic originating from the respective IPv4 address is permitted. The value 'null' allows traffic from any IP address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#source_ip AutoscalingGroup#source_ip}
        '''
        result = self._values.get("source_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_mac(self) -> typing.Optional[builtins.str]:
        '''Only traffic originating from the respective MAC address is permitted.

        Valid format: 'aa:bb:cc:dd:ee:ff'. The value 'null' allows traffic from any MAC address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#source_mac AutoscalingGroup#source_mac}
        '''
        result = self._values.get("source_mac")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_ip(self) -> typing.Optional[builtins.str]:
        '''If the target NIC has multiple IP addresses, only the traffic directed to the respective IP address of the NIC is allowed.

        The value 'null' allows traffic to any target IP address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_ip AutoscalingGroup#target_ip}
        '''
        result = self._values.get("target_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The firewall rule type. If not specified, the default value 'INGRESS' is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#type AutoscalingGroup#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationNicFirewallRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupReplicaConfigurationNicFirewallRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicFirewallRuleList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d451d63852043855f09d0e7c54d78dda1587a261742294786d47c1cd431d6bb1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AutoscalingGroupReplicaConfigurationNicFirewallRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8b3968d930d1ede47db95c30e064be319b430a686d68de3f8c8788834bfbc57)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AutoscalingGroupReplicaConfigurationNicFirewallRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c813d0f4f87b9b0513168108c9cd63d62c58a62b7f7a744c34e59f8369b68c54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__965819c5a17b923dc8e4d8819028cd68cf1ee9160549fd0e138ca0ee424fcaee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fb43f05993c0af9899cd3bc86ab60672be02e2aa581ab6a1eab43c27a0f8bd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFirewallRule]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFirewallRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFirewallRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2720bddd4d2e0b7bf50fe34aaa8ef7582c6515f265a396b64688a7c9f44d95b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AutoscalingGroupReplicaConfigurationNicFirewallRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicFirewallRuleOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a7f05aff3c63e8ed0b49effa946321f545286e7d7b64f9c88de96c56d6a7039)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIcmpCode")
    def reset_icmp_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIcmpCode", []))

    @jsii.member(jsii_name="resetIcmpType")
    def reset_icmp_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIcmpType", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPortRangeEnd")
    def reset_port_range_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortRangeEnd", []))

    @jsii.member(jsii_name="resetPortRangeStart")
    def reset_port_range_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPortRangeStart", []))

    @jsii.member(jsii_name="resetSourceIp")
    def reset_source_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceIp", []))

    @jsii.member(jsii_name="resetSourceMac")
    def reset_source_mac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceMac", []))

    @jsii.member(jsii_name="resetTargetIp")
    def reset_target_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetIp", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="icmpCodeInput")
    def icmp_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "icmpCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="icmpTypeInput")
    def icmp_type_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "icmpTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="portRangeEndInput")
    def port_range_end_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portRangeEndInput"))

    @builtins.property
    @jsii.member(jsii_name="portRangeStartInput")
    def port_range_start_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portRangeStartInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceIpInput")
    def source_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceIpInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceMacInput")
    def source_mac_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceMacInput"))

    @builtins.property
    @jsii.member(jsii_name="targetIpInput")
    def target_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetIpInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="icmpCode")
    def icmp_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "icmpCode"))

    @icmp_code.setter
    def icmp_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ff77d4d8fde5223be8a8fd77cc634c12b8374de9671b48e82f21c85fc173abc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "icmpCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="icmpType")
    def icmp_type(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "icmpType"))

    @icmp_type.setter
    def icmp_type(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__815406b204a94f503e9ae8281d2b8e9d69b27157d16f4b5097f30280d12c13f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "icmpType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__912e643e073fd23fc83bd48cf35871f763452606f592c7d79aa523e06e17dace)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portRangeEnd")
    def port_range_end(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "portRangeEnd"))

    @port_range_end.setter
    def port_range_end(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff90b35c5ec8baa844ee16637e46d863900088afa1f2d0c441f1670984fa88a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portRangeEnd", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="portRangeStart")
    def port_range_start(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "portRangeStart"))

    @port_range_start.setter
    def port_range_start(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__664a0db1ee37f6648a2500256813d1ff6966d9f99e5531c8d304abeb6e0f1892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "portRangeStart", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22c184e439d5a8ce4a9d88a8684d475dcc10e0d112bc1b644a0ff96dc9720f40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceIp")
    def source_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceIp"))

    @source_ip.setter
    def source_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e1e979e7e029c5a97cbc086807b2fbfeaef0f9019564fe512b86a09876bc1ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceMac")
    def source_mac(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceMac"))

    @source_mac.setter
    def source_mac(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c92ac0694e3b9cf1f7867cc906e8706d36eca246c37a6d4ee98fef375d72e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceMac", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetIp")
    def target_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetIp"))

    @target_ip.setter
    def target_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__152431dfb1c14a86badc3c54d01a5deeb434cd8eb70be2b89124dc62b9cfa5c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cfd203c200783078dd0e57260aaefc94829fc26e96f7497cd2a75a1ce31de6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFirewallRule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFirewallRule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFirewallRule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7945afdc93fa3ede9919da4dcd43f84778fde0b0a93d925ff28d7e5b3f80f33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicFlowLog",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "bucket": "bucket",
        "direction": "direction",
        "name": "name",
    },
)
class AutoscalingGroupReplicaConfigurationNicFlowLog:
    def __init__(
        self,
        *,
        action: builtins.str,
        bucket: builtins.str,
        direction: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param action: Specifies the traffic direction pattern. Valid values: ACCEPTED, REJECTED, ALL. Immutable, forces re-recreation of the nic resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#action AutoscalingGroup#action}
        :param bucket: The bucket name of an existing IONOS Object Storage bucket. Immutable, forces re-recreation of the nic resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#bucket AutoscalingGroup#bucket}
        :param direction: Specifies the traffic direction pattern. Valid values: INGRESS, EGRESS, BIDIRECTIONAL. Immutable, forces re-recreation of the nic resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#direction AutoscalingGroup#direction}
        :param name: The resource name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a364f3120c42570462a51bcc3ab1295324701271c55cb3fbd3442411b9494660)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument direction", value=direction, expected_type=type_hints["direction"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "action": action,
            "bucket": bucket,
            "direction": direction,
            "name": name,
        }

    @builtins.property
    def action(self) -> builtins.str:
        '''Specifies the traffic direction pattern. Valid values: ACCEPTED, REJECTED, ALL. Immutable, forces re-recreation of the nic resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#action AutoscalingGroup#action}
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket(self) -> builtins.str:
        '''The bucket name of an existing IONOS Object Storage bucket. Immutable, forces re-recreation of the nic resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#bucket AutoscalingGroup#bucket}
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def direction(self) -> builtins.str:
        '''Specifies the traffic direction pattern. Valid values: INGRESS, EGRESS, BIDIRECTIONAL. Immutable, forces re-recreation of the nic resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#direction AutoscalingGroup#direction}
        '''
        result = self._values.get("direction")
        assert result is not None, "Required property 'direction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The resource name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationNicFlowLog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupReplicaConfigurationNicFlowLogList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicFlowLogList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5934012e6567c1549fa8866b30e480b03eda5544818456b4b8244205ae167c01)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AutoscalingGroupReplicaConfigurationNicFlowLogOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0da36fa9ee83c6a4b1224597c1d450c4a81e4403f8689838289064c9bf9eb2b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AutoscalingGroupReplicaConfigurationNicFlowLogOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cc988ce8aa367e2706983d52dac3b4f106a7fbd23c1a552f712837c60679a4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05df2a47d26bfbd5a433e4983568163732b296a73a2728eefa919edeaf44a0fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06a5be759374fb5fb8e850e4b98bcdde94ecb3dce732353c6dc8c42e80ad9e98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFlowLog]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFlowLog]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFlowLog]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8b37379c587b608a1f023a88a21682895f91df05ab08465996435528e951cf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AutoscalingGroupReplicaConfigurationNicFlowLogOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicFlowLogOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b707a5dc87f43cb709fdc10d57162aac8023a5a5de4320cfff16b1b86d6bc88)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="actionInput")
    def action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="directionInput")
    def direction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @action.setter
    def action(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11f8bb1201ae29410cd1d3ba223e4b83fd1de4df6846c736b3dc3494938d0c41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "action", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e84bbd081a812dbc19d56eaa655668535bab9020da8efc7fadd3f616b06913)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="direction")
    def direction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "direction"))

    @direction.setter
    def direction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0cb6fe58ce37bec03c7462cd16d1b2f02581973c7031aaab366aaad89301299)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "direction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09c817ac75ed1a854ab19b229c55d6214ce1e6f1112ccba562d0a6da7eac5070)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFlowLog]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFlowLog]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFlowLog]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8c53f76a044e8f142a5dfd7d35acb0488ae9621740a73efa962d0be39eae431)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AutoscalingGroupReplicaConfigurationNicList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf3052063fd3ab488ef7e4e2f592d47d55eed716301ace563fe9ae7dd07af33)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AutoscalingGroupReplicaConfigurationNicOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4bf77b8c96d5a8cdb1de14fc706dcaf1ff03cbecd77b5a331ecc6f44786cd7e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AutoscalingGroupReplicaConfigurationNicOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d827d67c0b4d0a288bf9d5b489a9b0acb439c094598de6421605a82259156d8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adbf0a00215fc01f03b86f0782a02e23188e89eabd9d6c3bafa10474e093505a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__694fb45fb5662d8a15068c3761890f6b6dc9cf4efd18cf07369f0989b4195490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080c71c5aa2f339511c040a723332d3070de7124e4050607adbf983c2226804b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AutoscalingGroupReplicaConfigurationNicOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c1056ab7fcde8218a157992345e8eea145cb01708657524254c7d191161d2d5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFirewallRule")
    def put_firewall_rule(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNicFirewallRule, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c5971beaef2cf65cd751b95105a04afa25f821770e24a4b1331d6474c9620f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFirewallRule", [value]))

    @jsii.member(jsii_name="putFlowLog")
    def put_flow_log(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNicFlowLog, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fe23fd96f7221ef8913856294a9d52bebc26c3a9282e025d530c830322d7272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFlowLog", [value]))

    @jsii.member(jsii_name="putTargetGroup")
    def put_target_group(
        self,
        *,
        port: jsii.Number,
        target_group_id: builtins.str,
        weight: jsii.Number,
    ) -> None:
        '''
        :param port: The port for the target group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port AutoscalingGroup#port}
        :param target_group_id: The ID of the target group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_group_id AutoscalingGroup#target_group_id}
        :param weight: The weight for the target group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#weight AutoscalingGroup#weight}
        '''
        value = AutoscalingGroupReplicaConfigurationNicTargetGroup(
            port=port, target_group_id=target_group_id, weight=weight
        )

        return typing.cast(None, jsii.invoke(self, "putTargetGroup", [value]))

    @jsii.member(jsii_name="resetDhcp")
    def reset_dhcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcp", []))

    @jsii.member(jsii_name="resetFirewallActive")
    def reset_firewall_active(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewallActive", []))

    @jsii.member(jsii_name="resetFirewallRule")
    def reset_firewall_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewallRule", []))

    @jsii.member(jsii_name="resetFirewallType")
    def reset_firewall_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewallType", []))

    @jsii.member(jsii_name="resetFlowLog")
    def reset_flow_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFlowLog", []))

    @jsii.member(jsii_name="resetTargetGroup")
    def reset_target_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetGroup", []))

    @builtins.property
    @jsii.member(jsii_name="firewallRule")
    def firewall_rule(self) -> AutoscalingGroupReplicaConfigurationNicFirewallRuleList:
        return typing.cast(AutoscalingGroupReplicaConfigurationNicFirewallRuleList, jsii.get(self, "firewallRule"))

    @builtins.property
    @jsii.member(jsii_name="flowLog")
    def flow_log(self) -> AutoscalingGroupReplicaConfigurationNicFlowLogList:
        return typing.cast(AutoscalingGroupReplicaConfigurationNicFlowLogList, jsii.get(self, "flowLog"))

    @builtins.property
    @jsii.member(jsii_name="targetGroup")
    def target_group(
        self,
    ) -> "AutoscalingGroupReplicaConfigurationNicTargetGroupOutputReference":
        return typing.cast("AutoscalingGroupReplicaConfigurationNicTargetGroupOutputReference", jsii.get(self, "targetGroup"))

    @builtins.property
    @jsii.member(jsii_name="dhcpInput")
    def dhcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dhcpInput"))

    @builtins.property
    @jsii.member(jsii_name="firewallActiveInput")
    def firewall_active_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "firewallActiveInput"))

    @builtins.property
    @jsii.member(jsii_name="firewallRuleInput")
    def firewall_rule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFirewallRule]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFirewallRule]]], jsii.get(self, "firewallRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="firewallTypeInput")
    def firewall_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "firewallTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="flowLogInput")
    def flow_log_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFlowLog]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFlowLog]]], jsii.get(self, "flowLogInput"))

    @builtins.property
    @jsii.member(jsii_name="lanInput")
    def lan_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lanInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="targetGroupInput")
    def target_group_input(
        self,
    ) -> typing.Optional["AutoscalingGroupReplicaConfigurationNicTargetGroup"]:
        return typing.cast(typing.Optional["AutoscalingGroupReplicaConfigurationNicTargetGroup"], jsii.get(self, "targetGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dhcp"))

    @dhcp.setter
    def dhcp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3412c9bddf61b5e6eb31daa6abe1d1edfacf59753ea5084489d5efc45c10a7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firewallActive")
    def firewall_active(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "firewallActive"))

    @firewall_active.setter
    def firewall_active(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f7dd1b29cbfb03622825c9752952fba4ab026792e01f6473668427ebcaeb1f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firewallActive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="firewallType")
    def firewall_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firewallType"))

    @firewall_type.setter
    def firewall_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00ba45247d4fb1ea0caf350b9925920c829dc852dac15ba235b12815b7194297)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "firewallType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lan")
    def lan(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lan"))

    @lan.setter
    def lan(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb7e090377b2bb156aeaa591bedef2d760b7b7c8496820d54bbd1c137b6a8341)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f051c5aea2f72a66830f4f96b577ff4cbb61f62fe6033852a24b8c652b1fe90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__966666570e4b5b7856e18b615f56436d2ccdfb63090907b4dfc4377a01a837aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicTargetGroup",
    jsii_struct_bases=[],
    name_mapping={
        "port": "port",
        "target_group_id": "targetGroupId",
        "weight": "weight",
    },
)
class AutoscalingGroupReplicaConfigurationNicTargetGroup:
    def __init__(
        self,
        *,
        port: jsii.Number,
        target_group_id: builtins.str,
        weight: jsii.Number,
    ) -> None:
        '''
        :param port: The port for the target group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port AutoscalingGroup#port}
        :param target_group_id: The ID of the target group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_group_id AutoscalingGroup#target_group_id}
        :param weight: The weight for the target group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#weight AutoscalingGroup#weight}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eacfbcd54a53ca6475031c6579e107b5ab20f38087afa3c1042e348e94708e25)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument target_group_id", value=target_group_id, expected_type=type_hints["target_group_id"])
            check_type(argname="argument weight", value=weight, expected_type=type_hints["weight"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "port": port,
            "target_group_id": target_group_id,
            "weight": weight,
        }

    @builtins.property
    def port(self) -> jsii.Number:
        '''The port for the target group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#port AutoscalingGroup#port}
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target_group_id(self) -> builtins.str:
        '''The ID of the target group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#target_group_id AutoscalingGroup#target_group_id}
        '''
        result = self._values.get("target_group_id")
        assert result is not None, "Required property 'target_group_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def weight(self) -> jsii.Number:
        '''The weight for the target group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#weight AutoscalingGroup#weight}
        '''
        result = self._values.get("weight")
        assert result is not None, "Required property 'weight' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationNicTargetGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupReplicaConfigurationNicTargetGroupOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicTargetGroupOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aad9fbd623db03510e33c088ea5561404d83bba3ab34e9fb4ef289dd535407a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="targetGroupIdInput")
    def target_group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetGroupIdInput"))

    @builtins.property
    @jsii.member(jsii_name="weightInput")
    def weight_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "weightInput"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f031b41932f0a34c51fff664a2f45567ff2c8b7d4a0f4dedc0896c2aabf7f778)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetGroupId")
    def target_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetGroupId"))

    @target_group_id.setter
    def target_group_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7bdc1dadca86e01492f08ba3477e83b6c40dd98ea531499c77f2ccdfe620387)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetGroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="weight")
    def weight(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "weight"))

    @weight.setter
    def weight(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b1cf9a8d732f672a2e6732b446d0e20184a770cd56831cc79871f3cb460e474)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "weight", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AutoscalingGroupReplicaConfigurationNicTargetGroup]:
        return typing.cast(typing.Optional[AutoscalingGroupReplicaConfigurationNicTargetGroup], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupReplicaConfigurationNicTargetGroup],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6217dc7e4a96165ba0b4c40820883ed58c50f303a472b50b4be687be223eb49c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AutoscalingGroupReplicaConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c98eb701e487a04d289694169f4f1462a1c514bf9f3fe992d38f214f308a046b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNic")
    def put_nic(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNic, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__198b6b23b6c02d366401147df266493eb117c9fab0111a9b36b4d435f8ce185a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNic", [value]))

    @jsii.member(jsii_name="putVolume")
    def put_volume(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationVolume", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55dcb3fe0650b211894bf7c976ea8efc9db19a70106ef566b10168a2a4a80a1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVolume", [value]))

    @jsii.member(jsii_name="resetCpuFamily")
    def reset_cpu_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuFamily", []))

    @jsii.member(jsii_name="resetNic")
    def reset_nic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNic", []))

    @jsii.member(jsii_name="resetVolume")
    def reset_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolume", []))

    @builtins.property
    @jsii.member(jsii_name="nic")
    def nic(self) -> AutoscalingGroupReplicaConfigurationNicList:
        return typing.cast(AutoscalingGroupReplicaConfigurationNicList, jsii.get(self, "nic"))

    @builtins.property
    @jsii.member(jsii_name="volume")
    def volume(self) -> "AutoscalingGroupReplicaConfigurationVolumeList":
        return typing.cast("AutoscalingGroupReplicaConfigurationVolumeList", jsii.get(self, "volume"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="coresInput")
    def cores_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coresInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuFamilyInput")
    def cpu_family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuFamilyInput"))

    @builtins.property
    @jsii.member(jsii_name="nicInput")
    def nic_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]], jsii.get(self, "nicInput"))

    @builtins.property
    @jsii.member(jsii_name="ramInput")
    def ram_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ramInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeInput")
    def volume_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]], jsii.get(self, "volumeInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ecd5f002c4fb199acb7a64fc64fd7b7eed894c6b4f54f65ff321f07c3505655)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cores")
    def cores(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cores"))

    @cores.setter
    def cores(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ec8e06e2a6463598d1d2f9f050614f917f79b0aa958e6305a38f8091f872a2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cores", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cpuFamily")
    def cpu_family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuFamily"))

    @cpu_family.setter
    def cpu_family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236909ef7417a78ba6fe76c8eb36c9c11ad6ee29e8f7f1d4c7c2527a29c81dcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuFamily", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ram")
    def ram(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ram"))

    @ram.setter
    def ram(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3e42aaed6cfdbc4a7624f2eb9264283c30b57336853ecd053dfa50d4592bdde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ram", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupReplicaConfiguration]:
        return typing.cast(typing.Optional[AutoscalingGroupReplicaConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupReplicaConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c68c26597a550e588bbd9e71cef00a66c4c5c442d4acfc82b7223d8229f5395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationVolume",
    jsii_struct_bases=[],
    name_mapping={
        "boot_order": "bootOrder",
        "name": "name",
        "size": "size",
        "type": "type",
        "backup_unit_id": "backupUnitId",
        "bus": "bus",
        "image": "image",
        "image_alias": "imageAlias",
        "image_password": "imagePassword",
        "ssh_keys": "sshKeys",
        "user_data": "userData",
    },
)
class AutoscalingGroupReplicaConfigurationVolume:
    def __init__(
        self,
        *,
        boot_order: builtins.str,
        name: builtins.str,
        size: jsii.Number,
        type: builtins.str,
        backup_unit_id: typing.Optional[builtins.str] = None,
        bus: typing.Optional[builtins.str] = None,
        image: typing.Optional[builtins.str] = None,
        image_alias: typing.Optional[builtins.str] = None,
        image_password: typing.Optional[builtins.str] = None,
        ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param boot_order: Determines whether the volume will be used as a boot volume. Set to NONE, the volume will not be used as boot volume. Set to PRIMARY, the volume will be used as boot volume and set to AUTO will delegate the decision to the provisioning engine to decide whether to use the volume as boot volume. Notice that exactly one volume can be set to PRIMARY or all of them set to AUTO. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#boot_order AutoscalingGroup#boot_order}
        :param name: Name for this replica volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param size: User-defined size for this replica volume in GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#size AutoscalingGroup#size}
        :param type: Storage Type for this replica volume. Possible values: SSD, HDD, SSD_STANDARD or SSD_PREMIUM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#type AutoscalingGroup#type}
        :param backup_unit_id: The uuid of the Backup Unit that user has access to. The property is immutable and is only allowed to be set on a new volume creation. It is mandatory to provide either 'public image' or 'imageAlias' in conjunction with this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#backup_unit_id AutoscalingGroup#backup_unit_id}
        :param bus: The bus type of the volume. Default setting is 'VIRTIO'. The bus type 'IDE' is also supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#bus AutoscalingGroup#bus}
        :param image: The image installed on the disk. Currently, only the UUID of the image is supported. Note that either 'image' or 'imageAlias' must be specified, but not both. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#image AutoscalingGroup#image}
        :param image_alias: The image installed on the volume. Must be an 'imageAlias' as specified via the images API. Note that one of 'image' or 'imageAlias' must be set, but not both. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#image_alias AutoscalingGroup#image_alias}
        :param image_password: Image password for this replica volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#image_password AutoscalingGroup#image_password}
        :param ssh_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#ssh_keys AutoscalingGroup#ssh_keys}.
        :param user_data: User-data (Cloud Init) for this replica volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#user_data AutoscalingGroup#user_data}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6f15e1974841b2872a9d8ddd17de311f008024ec20bffb1a82b7f01663eb61)
            check_type(argname="argument boot_order", value=boot_order, expected_type=type_hints["boot_order"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument backup_unit_id", value=backup_unit_id, expected_type=type_hints["backup_unit_id"])
            check_type(argname="argument bus", value=bus, expected_type=type_hints["bus"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument image_alias", value=image_alias, expected_type=type_hints["image_alias"])
            check_type(argname="argument image_password", value=image_password, expected_type=type_hints["image_password"])
            check_type(argname="argument ssh_keys", value=ssh_keys, expected_type=type_hints["ssh_keys"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "boot_order": boot_order,
            "name": name,
            "size": size,
            "type": type,
        }
        if backup_unit_id is not None:
            self._values["backup_unit_id"] = backup_unit_id
        if bus is not None:
            self._values["bus"] = bus
        if image is not None:
            self._values["image"] = image
        if image_alias is not None:
            self._values["image_alias"] = image_alias
        if image_password is not None:
            self._values["image_password"] = image_password
        if ssh_keys is not None:
            self._values["ssh_keys"] = ssh_keys
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def boot_order(self) -> builtins.str:
        '''Determines whether the volume will be used as a boot volume.

        Set to NONE, the volume will not be used as boot volume.
        Set to PRIMARY, the volume will be used as boot volume and set to AUTO will delegate the decision to the provisioning engine to decide whether to use the volume as boot volume.
        Notice that exactly one volume can be set to PRIMARY or all of them set to AUTO.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#boot_order AutoscalingGroup#boot_order}
        '''
        result = self._values.get("boot_order")
        assert result is not None, "Required property 'boot_order' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name for this replica volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''User-defined size for this replica volume in GB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#size AutoscalingGroup#size}
        '''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Storage Type for this replica volume. Possible values: SSD, HDD, SSD_STANDARD or SSD_PREMIUM.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#type AutoscalingGroup#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backup_unit_id(self) -> typing.Optional[builtins.str]:
        '''The uuid of the Backup Unit that user has access to.

        The property is immutable and is only allowed to be set on a new volume creation. It is mandatory to provide either 'public image' or 'imageAlias' in conjunction with this property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#backup_unit_id AutoscalingGroup#backup_unit_id}
        '''
        result = self._values.get("backup_unit_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bus(self) -> typing.Optional[builtins.str]:
        '''The bus type of the volume. Default setting is 'VIRTIO'. The bus type 'IDE' is also supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#bus AutoscalingGroup#bus}
        '''
        result = self._values.get("bus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''The image installed on the disk.

        Currently, only the UUID of the image is supported. Note that either 'image' or 'imageAlias' must be specified, but not both.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#image AutoscalingGroup#image}
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_alias(self) -> typing.Optional[builtins.str]:
        '''The image installed on the volume.

        Must be an 'imageAlias' as specified via the images API. Note that one of 'image' or 'imageAlias' must be set, but not both.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#image_alias AutoscalingGroup#image_alias}
        '''
        result = self._values.get("image_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_password(self) -> typing.Optional[builtins.str]:
        '''Image password for this replica volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#image_password AutoscalingGroup#image_password}
        '''
        result = self._values.get("image_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#ssh_keys AutoscalingGroup#ssh_keys}.'''
        result = self._values.get("ssh_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''User-data (Cloud Init) for this replica volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#user_data AutoscalingGroup#user_data}
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupReplicaConfigurationVolumeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationVolumeList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__991f24dea0804dbb901311fb3f27db77f4184d038526eb9832230701c28da5ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AutoscalingGroupReplicaConfigurationVolumeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80dd3d402ba9b006ff1392dd4099eeeaba3c0019078750d781e793ed7d80cc7c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AutoscalingGroupReplicaConfigurationVolumeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8814b4426559baa049e597e6499134643f94242bdbe7ca94b50667cf8dec0d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4b574519d2ac8197c5b6756153523f66e740c1d0b251162385c53acce078f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__678677ebd665a33ae1f692dda8e7828e2da2812c72a6aacf0525f4a3559538e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__637ae6e6839bf25443b0f38165a5c07dc10703c879fb9c7b746c03b670090603)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AutoscalingGroupReplicaConfigurationVolumeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationVolumeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71307a76483f2b83b0d65e5b204e07d5673267c84ffcaf69113dbb92678f2142)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBackupUnitId")
    def reset_backup_unit_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupUnitId", []))

    @jsii.member(jsii_name="resetBus")
    def reset_bus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBus", []))

    @jsii.member(jsii_name="resetImage")
    def reset_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImage", []))

    @jsii.member(jsii_name="resetImageAlias")
    def reset_image_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageAlias", []))

    @jsii.member(jsii_name="resetImagePassword")
    def reset_image_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImagePassword", []))

    @jsii.member(jsii_name="resetSshKeys")
    def reset_ssh_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshKeys", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @builtins.property
    @jsii.member(jsii_name="backupUnitIdInput")
    def backup_unit_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupUnitIdInput"))

    @builtins.property
    @jsii.member(jsii_name="bootOrderInput")
    def boot_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bootOrderInput"))

    @builtins.property
    @jsii.member(jsii_name="busInput")
    def bus_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "busInput"))

    @builtins.property
    @jsii.member(jsii_name="imageAliasInput")
    def image_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property
    @jsii.member(jsii_name="imagePasswordInput")
    def image_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imagePasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sshKeysInput")
    def ssh_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property
    @jsii.member(jsii_name="backupUnitId")
    def backup_unit_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupUnitId"))

    @backup_unit_id.setter
    def backup_unit_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe4ebb5c2b34c15869f2a274dee54ffc22cc698a9f2842c043ef2f81455b98e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupUnitId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootOrder")
    def boot_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootOrder"))

    @boot_order.setter
    def boot_order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c15afae5963ab5d9e7128954d25a634c8b3c2177e2d29fcb8d86d340c6a1584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootOrder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bus")
    def bus(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bus"))

    @bus.setter
    def bus(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__219d3440216754d2e94e8821f2fc2f83e39667fef9c5857c9433212bcd5f52cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bus", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0b9731f9c3928a51ff4ccdb665e43a5a902fe5384b38d1d6fb084a7ad07e2ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "image", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imageAlias")
    def image_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageAlias"))

    @image_alias.setter
    def image_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b84d56ab1bf338d9fef3b1c89dd50ccb8811468e81fb60da6eb182fff213718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imagePassword")
    def image_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imagePassword"))

    @image_password.setter
    def image_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6b372869f3f600bb1e1e43fc22c825bb9a1a69d93ae416719f1f0ad23cc9883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bb2a5fd033dc56a594d9ccefa2d239da84f083906ef193d91bf32d5bee512f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2bb415086158881298c5a20c485c23e56e52328bf0f732d46b30bdd51e4812b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "size", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshKeys")
    def ssh_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshKeys"))

    @ssh_keys.setter
    def ssh_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59c1b77a447d513bc7ed0e6ba267753da0ddb1879792173f7ef44ec3db18dd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4678e5ceae510d3489c714fd8ab3ff18ffa1e98316dfa40cc485febc6e01df82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0990c43e2fca8b77121558685be394694901ee237e31f3871214252c58a02881)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f32509204ec20a09e0742290af4f8ee8a6429e0d9e2efd21a5b22a33ced9cd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "default": "default",
        "delete": "delete",
        "update": "update",
    },
)
class AutoscalingGroupTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#create AutoscalingGroup#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#default AutoscalingGroup#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#delete AutoscalingGroup#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#update AutoscalingGroup#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c6c5ca22dcf261bc31cfb498b2824237993b5fb4c8044ff4348550c19be06d8)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#create AutoscalingGroup#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#default AutoscalingGroup#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#delete AutoscalingGroup#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/autoscaling_group#update AutoscalingGroup#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b3a8029091ff0c2b48a0aaf882de6820e10cf883b36a02744403e3e07d1a191)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2f952ca7731e9f541ac83cb55cd1fc75b92958e3250b06af2383349c4810101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b6dc65d6dc352077be3c8d13aef669b83d4de63fdbd7cffb24a8f136b5de8f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cc2d786f9f9c08a29add9586eec206bbf8e6cd06c8f46dcd72dd385e618b7ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d102433a8692d8d1f0456e08f4db778993a0d747d8a999a0843d2c585f3f2e24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67366fd29382da65b20b101789e84d8f115f72c498f993e335f8497be89d3e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AutoscalingGroup",
    "AutoscalingGroupConfig",
    "AutoscalingGroupPolicy",
    "AutoscalingGroupPolicyOutputReference",
    "AutoscalingGroupPolicyScaleInAction",
    "AutoscalingGroupPolicyScaleInActionOutputReference",
    "AutoscalingGroupPolicyScaleOutAction",
    "AutoscalingGroupPolicyScaleOutActionOutputReference",
    "AutoscalingGroupReplicaConfiguration",
    "AutoscalingGroupReplicaConfigurationNic",
    "AutoscalingGroupReplicaConfigurationNicFirewallRule",
    "AutoscalingGroupReplicaConfigurationNicFirewallRuleList",
    "AutoscalingGroupReplicaConfigurationNicFirewallRuleOutputReference",
    "AutoscalingGroupReplicaConfigurationNicFlowLog",
    "AutoscalingGroupReplicaConfigurationNicFlowLogList",
    "AutoscalingGroupReplicaConfigurationNicFlowLogOutputReference",
    "AutoscalingGroupReplicaConfigurationNicList",
    "AutoscalingGroupReplicaConfigurationNicOutputReference",
    "AutoscalingGroupReplicaConfigurationNicTargetGroup",
    "AutoscalingGroupReplicaConfigurationNicTargetGroupOutputReference",
    "AutoscalingGroupReplicaConfigurationOutputReference",
    "AutoscalingGroupReplicaConfigurationVolume",
    "AutoscalingGroupReplicaConfigurationVolumeList",
    "AutoscalingGroupReplicaConfigurationVolumeOutputReference",
    "AutoscalingGroupTimeouts",
    "AutoscalingGroupTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__c3146dd62880db8c4a4a679ae36d31172810f23595b23353b8018fae683b4d75(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    datacenter_id: builtins.str,
    max_replica_count: jsii.Number,
    min_replica_count: jsii.Number,
    name: builtins.str,
    policy: typing.Union[AutoscalingGroupPolicy, typing.Dict[builtins.str, typing.Any]],
    replica_configuration: typing.Union[AutoscalingGroupReplicaConfiguration, typing.Dict[builtins.str, typing.Any]],
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[AutoscalingGroupTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__0e086ea468bafd4c868fa25a191755facf3c01266c1ff7a5bb47db0a613324ca(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa64c750b5399ce01da6d4e11088ee4c48367961ecf1c44f2ee899a04a021b0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0e3648c651a76707b9cd8410b25e85cc93402e8bdbe2fe2fd1bac10b1541429(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13fac770d256340aac888c3ece63afaf41f65d6645126008b33dd5b5ca9532ae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d0b42b145f0bdecd33b6a5f6f29c297e8586a933bda594d5a1926807677d46(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5eec38da3536bf995579a222f399ce03f33ff418f4e09671c17c535e2c8d6bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58053b66870c47f3bc0ab5e617378b61c4bb34d67bb04bc14365e28392ae1fa3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    datacenter_id: builtins.str,
    max_replica_count: jsii.Number,
    min_replica_count: jsii.Number,
    name: builtins.str,
    policy: typing.Union[AutoscalingGroupPolicy, typing.Dict[builtins.str, typing.Any]],
    replica_configuration: typing.Union[AutoscalingGroupReplicaConfiguration, typing.Dict[builtins.str, typing.Any]],
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[AutoscalingGroupTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68e702088158ad817c233bb2fdb4a934ac0d83af64565b75932648127031421f(
    *,
    metric: builtins.str,
    scale_in_action: typing.Union[AutoscalingGroupPolicyScaleInAction, typing.Dict[builtins.str, typing.Any]],
    scale_in_threshold: jsii.Number,
    scale_out_action: typing.Union[AutoscalingGroupPolicyScaleOutAction, typing.Dict[builtins.str, typing.Any]],
    scale_out_threshold: jsii.Number,
    unit: builtins.str,
    range: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b7f459aba3a8708621521fed4b6fdbc83c8c574108f722c3e9b6b267d9a79de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2764da5d65fc915f2a7f0f315e2b9c3725b0991e79391c2ec3b17b384419d949(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa5f2570afc38dd5c1a2eb3f43b50274b24280761b7a3ac5f088f4baccb726b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6ae6f86524c15798e2b2be53d7412b883d806d85cb08f0b741fb762002c97cd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2df5e1d6d313726a46de06118313eb60eb081ffaf64af4424c4c4dae38a0db25(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd42ad0b6666b52acf4ec9a56d2b7a56b046d162627727f4e01bf8611fbeec3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fc8e1835a175893e3aa46a6a9d35b813890d9ba43e8449ce5b5ba63c1aba574(
    value: typing.Optional[AutoscalingGroupPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df38e3cdf7b235f5f6fe179e59631a45c22f33edab46beae2d4c68ce6235f891(
    *,
    amount: jsii.Number,
    amount_type: builtins.str,
    delete_volumes: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    cooldown_period: typing.Optional[builtins.str] = None,
    termination_policy_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea303df8e2d25f599cbf66afd9f6bfe4268a8fbe0494ffb893c7fa19160fb62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204cfc21e156ebe762e24140c5b9b5b53909fdb1c1504d62b7434077e6403cfa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a981dac662cf18dc8dd7ee59ecb8df8d1001f0779f1d0c741940cc0f06e05a89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__536be0162f40286b13583f2bdff4f1d3342e75965e5abdff6113eb7a33c1bfc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c3730c0315324813b2ab8c5b73827c72b8bc5e340b1996a216ab5471d01ead(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a450bf2c72d16cb4f5d97e1e020c1f26b63f43573a0d4c42cc7ff9a9d80c6219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555c5ec7b1809bb4d55c43985370defd1502475f8f112eab09150d6d2fbdbd70(
    value: typing.Optional[AutoscalingGroupPolicyScaleInAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16787c31ff992b6598a275a4db90ce816824c4ad8fccc7daf7512172120c4a7d(
    *,
    amount: jsii.Number,
    amount_type: builtins.str,
    cooldown_period: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__165b096930701475659b425b1c1d1b799c5e7d92a4f7696b0117b0a8d44a4e02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9d5b374cc13b0ad43c9c58ec95707bfb697ea13f24e2616526adca15048e618(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ceb1e010f2840fd631a64e69ba9bdcad0f6f88bf01f8283d9bb0f3c2285c23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ae6465cbf87029321d558b10af2eeca7a6d03f88ab82ab786f8fcd660e6c0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0cca00adac567f779cbb4c62cc55ebdbb7285f2288cabefdea29c0b3565e072(
    value: typing.Optional[AutoscalingGroupPolicyScaleOutAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9753c8e0b92272664f4f8fa7334c36abeafa315c55a3a421d6b61d3d28fc2a(
    *,
    availability_zone: builtins.str,
    cores: jsii.Number,
    ram: jsii.Number,
    cpu_family: typing.Optional[builtins.str] = None,
    nic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNic, typing.Dict[builtins.str, typing.Any]]]]] = None,
    volume: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationVolume, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7db78f4556b0eba4b01ccef6c2598a45961bb34cbe79a3e74e1752233cc5380(
    *,
    lan: jsii.Number,
    name: builtins.str,
    dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firewall_active: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firewall_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNicFirewallRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
    firewall_type: typing.Optional[builtins.str] = None,
    flow_log: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNicFlowLog, typing.Dict[builtins.str, typing.Any]]]]] = None,
    target_group: typing.Optional[typing.Union[AutoscalingGroupReplicaConfigurationNicTargetGroup, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ead80a103008af2ecb9a22f3ef774f8e4177150417ab29d7debff34af3d5f9b(
    *,
    protocol: builtins.str,
    icmp_code: typing.Optional[jsii.Number] = None,
    icmp_type: typing.Optional[jsii.Number] = None,
    name: typing.Optional[builtins.str] = None,
    port_range_end: typing.Optional[jsii.Number] = None,
    port_range_start: typing.Optional[jsii.Number] = None,
    source_ip: typing.Optional[builtins.str] = None,
    source_mac: typing.Optional[builtins.str] = None,
    target_ip: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d451d63852043855f09d0e7c54d78dda1587a261742294786d47c1cd431d6bb1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b3968d930d1ede47db95c30e064be319b430a686d68de3f8c8788834bfbc57(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c813d0f4f87b9b0513168108c9cd63d62c58a62b7f7a744c34e59f8369b68c54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__965819c5a17b923dc8e4d8819028cd68cf1ee9160549fd0e138ca0ee424fcaee(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb43f05993c0af9899cd3bc86ab60672be02e2aa581ab6a1eab43c27a0f8bd1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2720bddd4d2e0b7bf50fe34aaa8ef7582c6515f265a396b64688a7c9f44d95b9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFirewallRule]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7f05aff3c63e8ed0b49effa946321f545286e7d7b64f9c88de96c56d6a7039(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ff77d4d8fde5223be8a8fd77cc634c12b8374de9671b48e82f21c85fc173abc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__815406b204a94f503e9ae8281d2b8e9d69b27157d16f4b5097f30280d12c13f7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912e643e073fd23fc83bd48cf35871f763452606f592c7d79aa523e06e17dace(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff90b35c5ec8baa844ee16637e46d863900088afa1f2d0c441f1670984fa88a8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__664a0db1ee37f6648a2500256813d1ff6966d9f99e5531c8d304abeb6e0f1892(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22c184e439d5a8ce4a9d88a8684d475dcc10e0d112bc1b644a0ff96dc9720f40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e1e979e7e029c5a97cbc086807b2fbfeaef0f9019564fe512b86a09876bc1ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73c92ac0694e3b9cf1f7867cc906e8706d36eca246c37a6d4ee98fef375d72e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__152431dfb1c14a86badc3c54d01a5deeb434cd8eb70be2b89124dc62b9cfa5c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cfd203c200783078dd0e57260aaefc94829fc26e96f7497cd2a75a1ce31de6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7945afdc93fa3ede9919da4dcd43f84778fde0b0a93d925ff28d7e5b3f80f33(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFirewallRule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a364f3120c42570462a51bcc3ab1295324701271c55cb3fbd3442411b9494660(
    *,
    action: builtins.str,
    bucket: builtins.str,
    direction: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5934012e6567c1549fa8866b30e480b03eda5544818456b4b8244205ae167c01(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0da36fa9ee83c6a4b1224597c1d450c4a81e4403f8689838289064c9bf9eb2b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cc988ce8aa367e2706983d52dac3b4f106a7fbd23c1a552f712837c60679a4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05df2a47d26bfbd5a433e4983568163732b296a73a2728eefa919edeaf44a0fb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06a5be759374fb5fb8e850e4b98bcdde94ecb3dce732353c6dc8c42e80ad9e98(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8b37379c587b608a1f023a88a21682895f91df05ab08465996435528e951cf8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNicFlowLog]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b707a5dc87f43cb709fdc10d57162aac8023a5a5de4320cfff16b1b86d6bc88(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11f8bb1201ae29410cd1d3ba223e4b83fd1de4df6846c736b3dc3494938d0c41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e84bbd081a812dbc19d56eaa655668535bab9020da8efc7fadd3f616b06913(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0cb6fe58ce37bec03c7462cd16d1b2f02581973c7031aaab366aaad89301299(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09c817ac75ed1a854ab19b229c55d6214ce1e6f1112ccba562d0a6da7eac5070(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c53f76a044e8f142a5dfd7d35acb0488ae9621740a73efa962d0be39eae431(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNicFlowLog]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf3052063fd3ab488ef7e4e2f592d47d55eed716301ace563fe9ae7dd07af33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4bf77b8c96d5a8cdb1de14fc706dcaf1ff03cbecd77b5a331ecc6f44786cd7e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d827d67c0b4d0a288bf9d5b489a9b0acb439c094598de6421605a82259156d8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adbf0a00215fc01f03b86f0782a02e23188e89eabd9d6c3bafa10474e093505a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__694fb45fb5662d8a15068c3761890f6b6dc9cf4efd18cf07369f0989b4195490(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080c71c5aa2f339511c040a723332d3070de7124e4050607adbf983c2226804b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c1056ab7fcde8218a157992345e8eea145cb01708657524254c7d191161d2d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c5971beaef2cf65cd751b95105a04afa25f821770e24a4b1331d6474c9620f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNicFirewallRule, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fe23fd96f7221ef8913856294a9d52bebc26c3a9282e025d530c830322d7272(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNicFlowLog, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3412c9bddf61b5e6eb31daa6abe1d1edfacf59753ea5084489d5efc45c10a7b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7dd1b29cbfb03622825c9752952fba4ab026792e01f6473668427ebcaeb1f4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00ba45247d4fb1ea0caf350b9925920c829dc852dac15ba235b12815b7194297(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7e090377b2bb156aeaa591bedef2d760b7b7c8496820d54bbd1c137b6a8341(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f051c5aea2f72a66830f4f96b577ff4cbb61f62fe6033852a24b8c652b1fe90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__966666570e4b5b7856e18b615f56436d2ccdfb63090907b4dfc4377a01a837aa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eacfbcd54a53ca6475031c6579e107b5ab20f38087afa3c1042e348e94708e25(
    *,
    port: jsii.Number,
    target_group_id: builtins.str,
    weight: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aad9fbd623db03510e33c088ea5561404d83bba3ab34e9fb4ef289dd535407a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f031b41932f0a34c51fff664a2f45567ff2c8b7d4a0f4dedc0896c2aabf7f778(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7bdc1dadca86e01492f08ba3477e83b6c40dd98ea531499c77f2ccdfe620387(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b1cf9a8d732f672a2e6732b446d0e20184a770cd56831cc79871f3cb460e474(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6217dc7e4a96165ba0b4c40820883ed58c50f303a472b50b4be687be223eb49c(
    value: typing.Optional[AutoscalingGroupReplicaConfigurationNicTargetGroup],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c98eb701e487a04d289694169f4f1462a1c514bf9f3fe992d38f214f308a046b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198b6b23b6c02d366401147df266493eb117c9fab0111a9b36b4d435f8ce185a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNic, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55dcb3fe0650b211894bf7c976ea8efc9db19a70106ef566b10168a2a4a80a1f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationVolume, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ecd5f002c4fb199acb7a64fc64fd7b7eed894c6b4f54f65ff321f07c3505655(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ec8e06e2a6463598d1d2f9f050614f917f79b0aa958e6305a38f8091f872a2f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__236909ef7417a78ba6fe76c8eb36c9c11ad6ee29e8f7f1d4c7c2527a29c81dcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3e42aaed6cfdbc4a7624f2eb9264283c30b57336853ecd053dfa50d4592bdde(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c68c26597a550e588bbd9e71cef00a66c4c5c442d4acfc82b7223d8229f5395(
    value: typing.Optional[AutoscalingGroupReplicaConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6f15e1974841b2872a9d8ddd17de311f008024ec20bffb1a82b7f01663eb61(
    *,
    boot_order: builtins.str,
    name: builtins.str,
    size: jsii.Number,
    type: builtins.str,
    backup_unit_id: typing.Optional[builtins.str] = None,
    bus: typing.Optional[builtins.str] = None,
    image: typing.Optional[builtins.str] = None,
    image_alias: typing.Optional[builtins.str] = None,
    image_password: typing.Optional[builtins.str] = None,
    ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_data: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__991f24dea0804dbb901311fb3f27db77f4184d038526eb9832230701c28da5ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80dd3d402ba9b006ff1392dd4099eeeaba3c0019078750d781e793ed7d80cc7c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8814b4426559baa049e597e6499134643f94242bdbe7ca94b50667cf8dec0d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4b574519d2ac8197c5b6756153523f66e740c1d0b251162385c53acce078f9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678677ebd665a33ae1f692dda8e7828e2da2812c72a6aacf0525f4a3559538e4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__637ae6e6839bf25443b0f38165a5c07dc10703c879fb9c7b746c03b670090603(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71307a76483f2b83b0d65e5b204e07d5673267c84ffcaf69113dbb92678f2142(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe4ebb5c2b34c15869f2a274dee54ffc22cc698a9f2842c043ef2f81455b98e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c15afae5963ab5d9e7128954d25a634c8b3c2177e2d29fcb8d86d340c6a1584(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__219d3440216754d2e94e8821f2fc2f83e39667fef9c5857c9433212bcd5f52cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0b9731f9c3928a51ff4ccdb665e43a5a902fe5384b38d1d6fb084a7ad07e2ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b84d56ab1bf338d9fef3b1c89dd50ccb8811468e81fb60da6eb182fff213718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6b372869f3f600bb1e1e43fc22c825bb9a1a69d93ae416719f1f0ad23cc9883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bb2a5fd033dc56a594d9ccefa2d239da84f083906ef193d91bf32d5bee512f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2bb415086158881298c5a20c485c23e56e52328bf0f732d46b30bdd51e4812b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59c1b77a447d513bc7ed0e6ba267753da0ddb1879792173f7ef44ec3db18dd3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4678e5ceae510d3489c714fd8ab3ff18ffa1e98316dfa40cc485febc6e01df82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0990c43e2fca8b77121558685be394694901ee237e31f3871214252c58a02881(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f32509204ec20a09e0742290af4f8ee8a6429e0d9e2efd21a5b22a33ced9cd9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c6c5ca22dcf261bc31cfb498b2824237993b5fb4c8044ff4348550c19be06d8(
    *,
    create: typing.Optional[builtins.str] = None,
    default: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b3a8029091ff0c2b48a0aaf882de6820e10cf883b36a02744403e3e07d1a191(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f952ca7731e9f541ac83cb55cd1fc75b92958e3250b06af2383349c4810101(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b6dc65d6dc352077be3c8d13aef669b83d4de63fdbd7cffb24a8f136b5de8f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cc2d786f9f9c08a29add9586eec206bbf8e6cd06c8f46dcd72dd385e618b7ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d102433a8692d8d1f0456e08f4db778993a0d747d8a999a0843d2c585f3f2e24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67366fd29382da65b20b101789e84d8f115f72c498f993e335f8497be89d3e55(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
