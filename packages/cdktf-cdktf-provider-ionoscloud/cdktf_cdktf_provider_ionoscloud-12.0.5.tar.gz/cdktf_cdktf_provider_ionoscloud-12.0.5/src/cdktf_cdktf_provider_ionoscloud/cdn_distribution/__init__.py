r'''
# `ionoscloud_cdn_distribution`

Refer to the Terraform Registry for docs: [`ionoscloud_cdn_distribution`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution).
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


class CdnDistribution(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistribution",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution ionoscloud_cdn_distribution}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        domain: builtins.str,
        routing_rules: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CdnDistributionRoutingRules", typing.Dict[builtins.str, typing.Any]]]],
        certificate_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["CdnDistributionTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution ionoscloud_cdn_distribution} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: The domain of the distribution. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#domain CdnDistribution#domain}
        :param routing_rules: routing_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#routing_rules CdnDistribution#routing_rules}
        :param certificate_id: The ID of the certificate to use for the distribution. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#certificate_id CdnDistribution#certificate_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#id CdnDistribution#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#timeouts CdnDistribution#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a445de0d8d49e05e319fdd0d50672b98811b97c6d8fb3e9091047653145a6586)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CdnDistributionConfig(
            domain=domain,
            routing_rules=routing_rules,
            certificate_id=certificate_id,
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
        '''Generates CDKTF code for importing a CdnDistribution resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CdnDistribution to import.
        :param import_from_id: The id of the existing CdnDistribution that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CdnDistribution to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f182fe118840f402e6bd4e047ee828f02b2097ba0ec2f9735e543320a354cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRoutingRules")
    def put_routing_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CdnDistributionRoutingRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f02e97505a73ae0b7e08e5b80019c7ded4c47df3ea23faac45f2871241af4f4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutingRules", [value]))

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
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#create CdnDistribution#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#default CdnDistribution#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#delete CdnDistribution#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#update CdnDistribution#update}.
        '''
        value = CdnDistributionTimeouts(
            create=create, default=default, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetCertificateId")
    def reset_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateId", []))

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
    @jsii.member(jsii_name="publicEndpointV4")
    def public_endpoint_v4(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicEndpointV4"))

    @builtins.property
    @jsii.member(jsii_name="publicEndpointV6")
    def public_endpoint_v6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicEndpointV6"))

    @builtins.property
    @jsii.member(jsii_name="resourceUrn")
    def resource_urn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceUrn"))

    @builtins.property
    @jsii.member(jsii_name="routingRules")
    def routing_rules(self) -> "CdnDistributionRoutingRulesList":
        return typing.cast("CdnDistributionRoutingRulesList", jsii.get(self, "routingRules"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CdnDistributionTimeoutsOutputReference":
        return typing.cast("CdnDistributionTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="routingRulesInput")
    def routing_rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CdnDistributionRoutingRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CdnDistributionRoutingRules"]]], jsii.get(self, "routingRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CdnDistributionTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CdnDistributionTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2237331bf1bee5dee193edc3c66cf8835999b4be1185e28c7be3b83bed706da1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd3e36b42e7b41bc66d3d317c856bf5dfa07dd4e0d4aa0dcc1660639568b0274)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2cf3803ed81e480177b3a3586db1edf01b5e24922d5ac935430e1e221c4feda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "domain": "domain",
        "routing_rules": "routingRules",
        "certificate_id": "certificateId",
        "id": "id",
        "timeouts": "timeouts",
    },
)
class CdnDistributionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        domain: builtins.str,
        routing_rules: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CdnDistributionRoutingRules", typing.Dict[builtins.str, typing.Any]]]],
        certificate_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["CdnDistributionTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param domain: The domain of the distribution. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#domain CdnDistribution#domain}
        :param routing_rules: routing_rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#routing_rules CdnDistribution#routing_rules}
        :param certificate_id: The ID of the certificate to use for the distribution. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#certificate_id CdnDistribution#certificate_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#id CdnDistribution#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#timeouts CdnDistribution#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = CdnDistributionTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e037804aa525abfa7e78375df4c78b879cd1d779e95805a3a7dad427886d1dd)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument routing_rules", value=routing_rules, expected_type=type_hints["routing_rules"])
            check_type(argname="argument certificate_id", value=certificate_id, expected_type=type_hints["certificate_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain": domain,
            "routing_rules": routing_rules,
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
        if certificate_id is not None:
            self._values["certificate_id"] = certificate_id
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
    def domain(self) -> builtins.str:
        '''The domain of the distribution.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#domain CdnDistribution#domain}
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def routing_rules(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CdnDistributionRoutingRules"]]:
        '''routing_rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#routing_rules CdnDistribution#routing_rules}
        '''
        result = self._values.get("routing_rules")
        assert result is not None, "Required property 'routing_rules' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CdnDistributionRoutingRules"]], result)

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the certificate to use for the distribution.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#certificate_id CdnDistribution#certificate_id}
        '''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#id CdnDistribution#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CdnDistributionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#timeouts CdnDistribution#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CdnDistributionTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdnDistributionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRules",
    jsii_struct_bases=[],
    name_mapping={"prefix": "prefix", "scheme": "scheme", "upstream": "upstream"},
)
class CdnDistributionRoutingRules:
    def __init__(
        self,
        *,
        prefix: builtins.str,
        scheme: builtins.str,
        upstream: typing.Union["CdnDistributionRoutingRulesUpstream", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param prefix: The prefix of the routing rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#prefix CdnDistribution#prefix}
        :param scheme: The scheme of the routing rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#scheme CdnDistribution#scheme}
        :param upstream: upstream block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#upstream CdnDistribution#upstream}
        '''
        if isinstance(upstream, dict):
            upstream = CdnDistributionRoutingRulesUpstream(**upstream)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b412f5050d06efaa754f8d3d71f2bbe557b36c67d8e4febbba170aadfae877c)
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
            check_type(argname="argument upstream", value=upstream, expected_type=type_hints["upstream"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "prefix": prefix,
            "scheme": scheme,
            "upstream": upstream,
        }

    @builtins.property
    def prefix(self) -> builtins.str:
        '''The prefix of the routing rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#prefix CdnDistribution#prefix}
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scheme(self) -> builtins.str:
        '''The scheme of the routing rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#scheme CdnDistribution#scheme}
        '''
        result = self._values.get("scheme")
        assert result is not None, "Required property 'scheme' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def upstream(self) -> "CdnDistributionRoutingRulesUpstream":
        '''upstream block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#upstream CdnDistribution#upstream}
        '''
        result = self._values.get("upstream")
        assert result is not None, "Required property 'upstream' is missing"
        return typing.cast("CdnDistributionRoutingRulesUpstream", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdnDistributionRoutingRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdnDistributionRoutingRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRulesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bc13e727a63bdec987f9d570c55a9122e3ddfd05f4139eb1c15126c9b67216bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CdnDistributionRoutingRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb9c6d56d79276f42c819ceecceb4c8d7a99b6f39186424587555e8d8e7a0ca7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CdnDistributionRoutingRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b69155f5bdee7c5b3fa101427d68143e8ae499e678951a1a224a977acc580c7d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d7432e50c0e5c63d7355b72e88b355a87fafe32220d395e80c2aff9fbdf1908)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebdf0f9edb8552c8c02af2e2c95280831627d0437b3cffbd96530747542c26be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CdnDistributionRoutingRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CdnDistributionRoutingRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CdnDistributionRoutingRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__802eb4c8cade2d5513839a2b7d6ef61957247bc289f0871d43f27c678c4d0287)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CdnDistributionRoutingRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRulesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__019c32884740d80db583bab4582a1eb5962a324b15cc35284e307816b08708bc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putUpstream")
    def put_upstream(
        self,
        *,
        caching: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        host: builtins.str,
        rate_limit_class: builtins.str,
        sni_mode: builtins.str,
        waf: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        geo_restrictions: typing.Optional[typing.Union["CdnDistributionRoutingRulesUpstreamGeoRestrictions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param caching: Enable or disable caching. If enabled, the CDN will cache the responses from the upstream host. Subsequent requests for the same resource will be served from the cache. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#caching CdnDistribution#caching}
        :param host: The upstream host that handles the requests if not already cached. This host will be protected by the WAF if the option is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#host CdnDistribution#host}
        :param rate_limit_class: Rate limit class that will be applied to limit the number of incoming requests per IP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#rate_limit_class CdnDistribution#rate_limit_class}
        :param sni_mode: The SNI (Server Name Indication) mode of the upstream host. It supports two modes: 'distribution' and 'origin', for more information about these modes please check the resource docs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#sni_mode CdnDistribution#sni_mode}
        :param waf: Enable or disable WAF to protect the upstream host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#waf CdnDistribution#waf}
        :param geo_restrictions: geo_restrictions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#geo_restrictions CdnDistribution#geo_restrictions}
        '''
        value = CdnDistributionRoutingRulesUpstream(
            caching=caching,
            host=host,
            rate_limit_class=rate_limit_class,
            sni_mode=sni_mode,
            waf=waf,
            geo_restrictions=geo_restrictions,
        )

        return typing.cast(None, jsii.invoke(self, "putUpstream", [value]))

    @builtins.property
    @jsii.member(jsii_name="upstream")
    def upstream(self) -> "CdnDistributionRoutingRulesUpstreamOutputReference":
        return typing.cast("CdnDistributionRoutingRulesUpstreamOutputReference", jsii.get(self, "upstream"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="schemeInput")
    def scheme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemeInput"))

    @builtins.property
    @jsii.member(jsii_name="upstreamInput")
    def upstream_input(self) -> typing.Optional["CdnDistributionRoutingRulesUpstream"]:
        return typing.cast(typing.Optional["CdnDistributionRoutingRulesUpstream"], jsii.get(self, "upstreamInput"))

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57ba7a18b54635a6c224756a60a0d8b3536570e9f9db5794a3e00892dc9dc69d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb8e6fa7d1f8efebbb6ce26ed9756b446d686ccfa39dea9a32545751423ecf15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionRoutingRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionRoutingRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionRoutingRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7ddf76ca5fa0d31cb06f1494abeff52154515c734c8e4444591509fcf6f84bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRulesUpstream",
    jsii_struct_bases=[],
    name_mapping={
        "caching": "caching",
        "host": "host",
        "rate_limit_class": "rateLimitClass",
        "sni_mode": "sniMode",
        "waf": "waf",
        "geo_restrictions": "geoRestrictions",
    },
)
class CdnDistributionRoutingRulesUpstream:
    def __init__(
        self,
        *,
        caching: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        host: builtins.str,
        rate_limit_class: builtins.str,
        sni_mode: builtins.str,
        waf: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        geo_restrictions: typing.Optional[typing.Union["CdnDistributionRoutingRulesUpstreamGeoRestrictions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param caching: Enable or disable caching. If enabled, the CDN will cache the responses from the upstream host. Subsequent requests for the same resource will be served from the cache. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#caching CdnDistribution#caching}
        :param host: The upstream host that handles the requests if not already cached. This host will be protected by the WAF if the option is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#host CdnDistribution#host}
        :param rate_limit_class: Rate limit class that will be applied to limit the number of incoming requests per IP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#rate_limit_class CdnDistribution#rate_limit_class}
        :param sni_mode: The SNI (Server Name Indication) mode of the upstream host. It supports two modes: 'distribution' and 'origin', for more information about these modes please check the resource docs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#sni_mode CdnDistribution#sni_mode}
        :param waf: Enable or disable WAF to protect the upstream host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#waf CdnDistribution#waf}
        :param geo_restrictions: geo_restrictions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#geo_restrictions CdnDistribution#geo_restrictions}
        '''
        if isinstance(geo_restrictions, dict):
            geo_restrictions = CdnDistributionRoutingRulesUpstreamGeoRestrictions(**geo_restrictions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23049f94a1fa85833740d15ef5af694ec3de400ad002ed00e0c371f3af8fc7a6)
            check_type(argname="argument caching", value=caching, expected_type=type_hints["caching"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument rate_limit_class", value=rate_limit_class, expected_type=type_hints["rate_limit_class"])
            check_type(argname="argument sni_mode", value=sni_mode, expected_type=type_hints["sni_mode"])
            check_type(argname="argument waf", value=waf, expected_type=type_hints["waf"])
            check_type(argname="argument geo_restrictions", value=geo_restrictions, expected_type=type_hints["geo_restrictions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "caching": caching,
            "host": host,
            "rate_limit_class": rate_limit_class,
            "sni_mode": sni_mode,
            "waf": waf,
        }
        if geo_restrictions is not None:
            self._values["geo_restrictions"] = geo_restrictions

    @builtins.property
    def caching(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable or disable caching.

        If enabled, the CDN will cache the responses from the upstream host. Subsequent requests for the same resource will be served from the cache.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#caching CdnDistribution#caching}
        '''
        result = self._values.get("caching")
        assert result is not None, "Required property 'caching' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def host(self) -> builtins.str:
        '''The upstream host that handles the requests if not already cached.

        This host will be protected by the WAF if the option is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#host CdnDistribution#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rate_limit_class(self) -> builtins.str:
        '''Rate limit class that will be applied to limit the number of incoming requests per IP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#rate_limit_class CdnDistribution#rate_limit_class}
        '''
        result = self._values.get("rate_limit_class")
        assert result is not None, "Required property 'rate_limit_class' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sni_mode(self) -> builtins.str:
        '''The SNI (Server Name Indication) mode of the upstream host.

        It supports two modes: 'distribution' and 'origin', for more information about these modes please check the resource docs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#sni_mode CdnDistribution#sni_mode}
        '''
        result = self._values.get("sni_mode")
        assert result is not None, "Required property 'sni_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def waf(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Enable or disable WAF to protect the upstream host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#waf CdnDistribution#waf}
        '''
        result = self._values.get("waf")
        assert result is not None, "Required property 'waf' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def geo_restrictions(
        self,
    ) -> typing.Optional["CdnDistributionRoutingRulesUpstreamGeoRestrictions"]:
        '''geo_restrictions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#geo_restrictions CdnDistribution#geo_restrictions}
        '''
        result = self._values.get("geo_restrictions")
        return typing.cast(typing.Optional["CdnDistributionRoutingRulesUpstreamGeoRestrictions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdnDistributionRoutingRulesUpstream(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRulesUpstreamGeoRestrictions",
    jsii_struct_bases=[],
    name_mapping={"allow_list": "allowList", "block_list": "blockList"},
)
class CdnDistributionRoutingRulesUpstreamGeoRestrictions:
    def __init__(
        self,
        *,
        allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        block_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allow_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#allow_list CdnDistribution#allow_list}.
        :param block_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#block_list CdnDistribution#block_list}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e4a5c5421ad42479a54c440340a8560a4495bc74781d1920321c8e86ad302c8)
            check_type(argname="argument allow_list", value=allow_list, expected_type=type_hints["allow_list"])
            check_type(argname="argument block_list", value=block_list, expected_type=type_hints["block_list"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_list is not None:
            self._values["allow_list"] = allow_list
        if block_list is not None:
            self._values["block_list"] = block_list

    @builtins.property
    def allow_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#allow_list CdnDistribution#allow_list}.'''
        result = self._values.get("allow_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def block_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#block_list CdnDistribution#block_list}.'''
        result = self._values.get("block_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdnDistributionRoutingRulesUpstreamGeoRestrictions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdnDistributionRoutingRulesUpstreamGeoRestrictionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRulesUpstreamGeoRestrictionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea02440e05de204ea72b240d1b8e8e0657301ea25fae04cb123240ffd89f0d8c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllowList")
    def reset_allow_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowList", []))

    @jsii.member(jsii_name="resetBlockList")
    def reset_block_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBlockList", []))

    @builtins.property
    @jsii.member(jsii_name="allowListInput")
    def allow_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowListInput"))

    @builtins.property
    @jsii.member(jsii_name="blockListInput")
    def block_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "blockListInput"))

    @builtins.property
    @jsii.member(jsii_name="allowList")
    def allow_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowList"))

    @allow_list.setter
    def allow_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98026a5954f5aa80fb10c3b2453d5e4bc79723312a7a840def3655b89f672502)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="blockList")
    def block_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "blockList"))

    @block_list.setter
    def block_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b773554b570d4691dd7c0c3b855d1658daa220eeee8e613bb62c52eba2a10191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "blockList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CdnDistributionRoutingRulesUpstreamGeoRestrictions]:
        return typing.cast(typing.Optional[CdnDistributionRoutingRulesUpstreamGeoRestrictions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CdnDistributionRoutingRulesUpstreamGeoRestrictions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6ed8cbbe2b8921706b5a66c8572ca4fdf70b855111664fd16679c80d93946a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CdnDistributionRoutingRulesUpstreamOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionRoutingRulesUpstreamOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e81a86bf666af4005790ad627070d9f560dfc29aaf97795c2e32b63462ed2f71)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putGeoRestrictions")
    def put_geo_restrictions(
        self,
        *,
        allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        block_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allow_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#allow_list CdnDistribution#allow_list}.
        :param block_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#block_list CdnDistribution#block_list}.
        '''
        value = CdnDistributionRoutingRulesUpstreamGeoRestrictions(
            allow_list=allow_list, block_list=block_list
        )

        return typing.cast(None, jsii.invoke(self, "putGeoRestrictions", [value]))

    @jsii.member(jsii_name="resetGeoRestrictions")
    def reset_geo_restrictions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeoRestrictions", []))

    @builtins.property
    @jsii.member(jsii_name="geoRestrictions")
    def geo_restrictions(
        self,
    ) -> CdnDistributionRoutingRulesUpstreamGeoRestrictionsOutputReference:
        return typing.cast(CdnDistributionRoutingRulesUpstreamGeoRestrictionsOutputReference, jsii.get(self, "geoRestrictions"))

    @builtins.property
    @jsii.member(jsii_name="cachingInput")
    def caching_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cachingInput"))

    @builtins.property
    @jsii.member(jsii_name="geoRestrictionsInput")
    def geo_restrictions_input(
        self,
    ) -> typing.Optional[CdnDistributionRoutingRulesUpstreamGeoRestrictions]:
        return typing.cast(typing.Optional[CdnDistributionRoutingRulesUpstreamGeoRestrictions], jsii.get(self, "geoRestrictionsInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="rateLimitClassInput")
    def rate_limit_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rateLimitClassInput"))

    @builtins.property
    @jsii.member(jsii_name="sniModeInput")
    def sni_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sniModeInput"))

    @builtins.property
    @jsii.member(jsii_name="wafInput")
    def waf_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "wafInput"))

    @builtins.property
    @jsii.member(jsii_name="caching")
    def caching(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "caching"))

    @caching.setter
    def caching(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b53e0b1a631f377001561e27b36b915ca01ee89b828aa1cf4b87b4206376915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caching", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2415e62da5af534f27ab03755b053b929fb91b07cc222a268993908672d7c6de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rateLimitClass")
    def rate_limit_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rateLimitClass"))

    @rate_limit_class.setter
    def rate_limit_class(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f444a95026a569812eab50b0d2476d2e5cef0fc1c6d9f5a8c27836b0eb0c2052)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rateLimitClass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sniMode")
    def sni_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sniMode"))

    @sni_mode.setter
    def sni_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f52655d624eb4a646a10f4d9a5b6430c9c482db62eee6a4c73ecee3463475233)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sniMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waf")
    def waf(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "waf"))

    @waf.setter
    def waf(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7503859a1cbe42d4a42d74812b1002e52074891014bc55a86471fef49d2d9716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waf", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CdnDistributionRoutingRulesUpstream]:
        return typing.cast(typing.Optional[CdnDistributionRoutingRulesUpstream], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CdnDistributionRoutingRulesUpstream],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d6e9d193ab31b82361aa5c97f178985dcc85b8ce5b76ff145d2bf0c8c59784a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "default": "default",
        "delete": "delete",
        "update": "update",
    },
)
class CdnDistributionTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#create CdnDistribution#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#default CdnDistribution#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#delete CdnDistribution#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#update CdnDistribution#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58dae6c0ee3c001904e602454c87b82f50162c123c141a2e2928812f4d86f81d)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#create CdnDistribution#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#default CdnDistribution#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#delete CdnDistribution#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/cdn_distribution#update CdnDistribution#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdnDistributionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdnDistributionTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.cdnDistribution.CdnDistributionTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d1a8b3a4b228c3b48c2a9fb0c341fed355961d6756d1cdee74087d70167dc1fb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__427abbce5e7ab091ba4f152c08f78400edf72a764543e44496eae1c0077fb439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6a5c0cba3fc3ae5986a5cb074e1fbd09ed7a2ef022c347a65558b982efda15e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__378ca5d3ca0e65430d9e67d05874b84eaae89fca53dc1eb1159a2c7e1af8d86c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b946ee8148f4600136a8524b72ab91bc17c0e11e2d2a0c6beb9ec6330b7d228)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91bc8333cdfee040cfdf3ebfb7074c38fc1e41afea612de49d6ab716751d7d65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CdnDistribution",
    "CdnDistributionConfig",
    "CdnDistributionRoutingRules",
    "CdnDistributionRoutingRulesList",
    "CdnDistributionRoutingRulesOutputReference",
    "CdnDistributionRoutingRulesUpstream",
    "CdnDistributionRoutingRulesUpstreamGeoRestrictions",
    "CdnDistributionRoutingRulesUpstreamGeoRestrictionsOutputReference",
    "CdnDistributionRoutingRulesUpstreamOutputReference",
    "CdnDistributionTimeouts",
    "CdnDistributionTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__a445de0d8d49e05e319fdd0d50672b98811b97c6d8fb3e9091047653145a6586(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    domain: builtins.str,
    routing_rules: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CdnDistributionRoutingRules, typing.Dict[builtins.str, typing.Any]]]],
    certificate_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[CdnDistributionTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__87f182fe118840f402e6bd4e047ee828f02b2097ba0ec2f9735e543320a354cd(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f02e97505a73ae0b7e08e5b80019c7ded4c47df3ea23faac45f2871241af4f4a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CdnDistributionRoutingRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2237331bf1bee5dee193edc3c66cf8835999b4be1185e28c7be3b83bed706da1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd3e36b42e7b41bc66d3d317c856bf5dfa07dd4e0d4aa0dcc1660639568b0274(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2cf3803ed81e480177b3a3586db1edf01b5e24922d5ac935430e1e221c4feda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e037804aa525abfa7e78375df4c78b879cd1d779e95805a3a7dad427886d1dd(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    domain: builtins.str,
    routing_rules: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CdnDistributionRoutingRules, typing.Dict[builtins.str, typing.Any]]]],
    certificate_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[CdnDistributionTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b412f5050d06efaa754f8d3d71f2bbe557b36c67d8e4febbba170aadfae877c(
    *,
    prefix: builtins.str,
    scheme: builtins.str,
    upstream: typing.Union[CdnDistributionRoutingRulesUpstream, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc13e727a63bdec987f9d570c55a9122e3ddfd05f4139eb1c15126c9b67216bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb9c6d56d79276f42c819ceecceb4c8d7a99b6f39186424587555e8d8e7a0ca7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b69155f5bdee7c5b3fa101427d68143e8ae499e678951a1a224a977acc580c7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d7432e50c0e5c63d7355b72e88b355a87fafe32220d395e80c2aff9fbdf1908(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebdf0f9edb8552c8c02af2e2c95280831627d0437b3cffbd96530747542c26be(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__802eb4c8cade2d5513839a2b7d6ef61957247bc289f0871d43f27c678c4d0287(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CdnDistributionRoutingRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__019c32884740d80db583bab4582a1eb5962a324b15cc35284e307816b08708bc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57ba7a18b54635a6c224756a60a0d8b3536570e9f9db5794a3e00892dc9dc69d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb8e6fa7d1f8efebbb6ce26ed9756b446d686ccfa39dea9a32545751423ecf15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7ddf76ca5fa0d31cb06f1494abeff52154515c734c8e4444591509fcf6f84bf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionRoutingRules]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23049f94a1fa85833740d15ef5af694ec3de400ad002ed00e0c371f3af8fc7a6(
    *,
    caching: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    host: builtins.str,
    rate_limit_class: builtins.str,
    sni_mode: builtins.str,
    waf: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    geo_restrictions: typing.Optional[typing.Union[CdnDistributionRoutingRulesUpstreamGeoRestrictions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e4a5c5421ad42479a54c440340a8560a4495bc74781d1920321c8e86ad302c8(
    *,
    allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    block_list: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea02440e05de204ea72b240d1b8e8e0657301ea25fae04cb123240ffd89f0d8c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98026a5954f5aa80fb10c3b2453d5e4bc79723312a7a840def3655b89f672502(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b773554b570d4691dd7c0c3b855d1658daa220eeee8e613bb62c52eba2a10191(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6ed8cbbe2b8921706b5a66c8572ca4fdf70b855111664fd16679c80d93946a(
    value: typing.Optional[CdnDistributionRoutingRulesUpstreamGeoRestrictions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e81a86bf666af4005790ad627070d9f560dfc29aaf97795c2e32b63462ed2f71(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b53e0b1a631f377001561e27b36b915ca01ee89b828aa1cf4b87b4206376915(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2415e62da5af534f27ab03755b053b929fb91b07cc222a268993908672d7c6de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f444a95026a569812eab50b0d2476d2e5cef0fc1c6d9f5a8c27836b0eb0c2052(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f52655d624eb4a646a10f4d9a5b6430c9c482db62eee6a4c73ecee3463475233(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7503859a1cbe42d4a42d74812b1002e52074891014bc55a86471fef49d2d9716(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d6e9d193ab31b82361aa5c97f178985dcc85b8ce5b76ff145d2bf0c8c59784a(
    value: typing.Optional[CdnDistributionRoutingRulesUpstream],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58dae6c0ee3c001904e602454c87b82f50162c123c141a2e2928812f4d86f81d(
    *,
    create: typing.Optional[builtins.str] = None,
    default: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1a8b3a4b228c3b48c2a9fb0c341fed355961d6756d1cdee74087d70167dc1fb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427abbce5e7ab091ba4f152c08f78400edf72a764543e44496eae1c0077fb439(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6a5c0cba3fc3ae5986a5cb074e1fbd09ed7a2ef022c347a65558b982efda15e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__378ca5d3ca0e65430d9e67d05874b84eaae89fca53dc1eb1159a2c7e1af8d86c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b946ee8148f4600136a8524b72ab91bc17c0e11e2d2a0c6beb9ec6330b7d228(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91bc8333cdfee040cfdf3ebfb7074c38fc1e41afea612de49d6ab716751d7d65(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CdnDistributionTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
