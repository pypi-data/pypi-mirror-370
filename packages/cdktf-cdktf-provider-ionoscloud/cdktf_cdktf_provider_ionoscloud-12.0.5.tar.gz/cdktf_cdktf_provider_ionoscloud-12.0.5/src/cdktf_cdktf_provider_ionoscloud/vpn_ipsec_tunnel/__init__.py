r'''
# `ionoscloud_vpn_ipsec_tunnel`

Refer to the Terraform Registry for docs: [`ionoscloud_vpn_ipsec_tunnel`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel).
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


class VpnIpsecTunnel(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnel",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel ionoscloud_vpn_ipsec_tunnel}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        auth: typing.Union["VpnIpsecTunnelAuth", typing.Dict[builtins.str, typing.Any]],
        cloud_network_cidrs: typing.Sequence[builtins.str],
        esp: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VpnIpsecTunnelEsp", typing.Dict[builtins.str, typing.Any]]]],
        gateway_id: builtins.str,
        ike: typing.Union["VpnIpsecTunnelIke", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        peer_network_cidrs: typing.Sequence[builtins.str],
        remote_host: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["VpnIpsecTunnelTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel ionoscloud_vpn_ipsec_tunnel} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param auth: auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#auth VpnIpsecTunnel#auth}
        :param cloud_network_cidrs: The network CIDRs on the "Left" side that are allowed to connect to the IPSec tunnel, i.e. the CIDRs within your IONOS Cloud LAN. Specify "0.0.0.0/0" or "::/0" for all addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#cloud_network_cidrs VpnIpsecTunnel#cloud_network_cidrs}
        :param esp: esp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#esp VpnIpsecTunnel#esp}
        :param gateway_id: The ID of the IPSec Gateway that the tunnel belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#gateway_id VpnIpsecTunnel#gateway_id}
        :param ike: ike block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#ike VpnIpsecTunnel#ike}
        :param name: The human-readable name of your IPSec Gateway Tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#name VpnIpsecTunnel#name}
        :param peer_network_cidrs: The network CIDRs on the "Right" side that are allowed to connect to the IPSec tunnel. Specify "0.0.0.0/0" or "::/0" for all addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#peer_network_cidrs VpnIpsecTunnel#peer_network_cidrs}
        :param remote_host: The remote peer host fully qualified domain name or public IPV4 IP to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#remote_host VpnIpsecTunnel#remote_host}
        :param description: The human-readable description of your IPSec Gateway Tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#description VpnIpsecTunnel#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#id VpnIpsecTunnel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param location: The location of the IPSec Gateway Tunnel. Supported locations: de/fra, de/fra/2, de/txl, es/vit, gb/bhx, gb/lhr, us/ewr, us/las, us/mci, fr/par. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#location VpnIpsecTunnel#location}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#timeouts VpnIpsecTunnel#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d339d4368b171c0eccad9578bd020ca225f63064e5f07946247f0d69c923f57)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = VpnIpsecTunnelConfig(
            auth=auth,
            cloud_network_cidrs=cloud_network_cidrs,
            esp=esp,
            gateway_id=gateway_id,
            ike=ike,
            name=name,
            peer_network_cidrs=peer_network_cidrs,
            remote_host=remote_host,
            description=description,
            id=id,
            location=location,
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
        '''Generates CDKTF code for importing a VpnIpsecTunnel resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VpnIpsecTunnel to import.
        :param import_from_id: The id of the existing VpnIpsecTunnel that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VpnIpsecTunnel to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__993d1b888b6052ee7bfa933e21e1ec881eb176711c3ea435ad9d0bd24ef4896f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAuth")
    def put_auth(
        self,
        *,
        method: typing.Optional[builtins.str] = None,
        psk_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: The Authentication Method to use for IPSec Authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#method VpnIpsecTunnel#method}
        :param psk_key: The Pre-Shared Key to use for IPSec Authentication. Note: Required if method is PSK. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#psk_key VpnIpsecTunnel#psk_key}
        '''
        value = VpnIpsecTunnelAuth(method=method, psk_key=psk_key)

        return typing.cast(None, jsii.invoke(self, "putAuth", [value]))

    @jsii.member(jsii_name="putEsp")
    def put_esp(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VpnIpsecTunnelEsp", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe132af9ab2784da63e2ceb7985bc2f2cd6fe74cbe4b7ebc13a2ab48780397c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEsp", [value]))

    @jsii.member(jsii_name="putIke")
    def put_ike(
        self,
        *,
        diffie_hellman_group: typing.Optional[builtins.str] = None,
        encryption_algorithm: typing.Optional[builtins.str] = None,
        integrity_algorithm: typing.Optional[builtins.str] = None,
        lifetime: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param diffie_hellman_group: The Diffie-Hellman Group to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#diffie_hellman_group VpnIpsecTunnel#diffie_hellman_group}
        :param encryption_algorithm: The encryption algorithm to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#encryption_algorithm VpnIpsecTunnel#encryption_algorithm}
        :param integrity_algorithm: The integrity algorithm to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#integrity_algorithm VpnIpsecTunnel#integrity_algorithm}
        :param lifetime: The phase lifetime in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#lifetime VpnIpsecTunnel#lifetime}
        '''
        value = VpnIpsecTunnelIke(
            diffie_hellman_group=diffie_hellman_group,
            encryption_algorithm=encryption_algorithm,
            integrity_algorithm=integrity_algorithm,
            lifetime=lifetime,
        )

        return typing.cast(None, jsii.invoke(self, "putIke", [value]))

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
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#create VpnIpsecTunnel#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#default VpnIpsecTunnel#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#delete VpnIpsecTunnel#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#update VpnIpsecTunnel#update}.
        '''
        value = VpnIpsecTunnelTimeouts(
            create=create, default=default, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLocation")
    def reset_location(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocation", []))

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
    @jsii.member(jsii_name="auth")
    def auth(self) -> "VpnIpsecTunnelAuthOutputReference":
        return typing.cast("VpnIpsecTunnelAuthOutputReference", jsii.get(self, "auth"))

    @builtins.property
    @jsii.member(jsii_name="esp")
    def esp(self) -> "VpnIpsecTunnelEspList":
        return typing.cast("VpnIpsecTunnelEspList", jsii.get(self, "esp"))

    @builtins.property
    @jsii.member(jsii_name="ike")
    def ike(self) -> "VpnIpsecTunnelIkeOutputReference":
        return typing.cast("VpnIpsecTunnelIkeOutputReference", jsii.get(self, "ike"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "VpnIpsecTunnelTimeoutsOutputReference":
        return typing.cast("VpnIpsecTunnelTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="authInput")
    def auth_input(self) -> typing.Optional["VpnIpsecTunnelAuth"]:
        return typing.cast(typing.Optional["VpnIpsecTunnelAuth"], jsii.get(self, "authInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudNetworkCidrsInput")
    def cloud_network_cidrs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cloudNetworkCidrsInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="espInput")
    def esp_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VpnIpsecTunnelEsp"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VpnIpsecTunnelEsp"]]], jsii.get(self, "espInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewayIdInput")
    def gateway_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ikeInput")
    def ike_input(self) -> typing.Optional["VpnIpsecTunnelIke"]:
        return typing.cast(typing.Optional["VpnIpsecTunnelIke"], jsii.get(self, "ikeInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="peerNetworkCidrsInput")
    def peer_network_cidrs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "peerNetworkCidrsInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteHostInput")
    def remote_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "remoteHostInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "VpnIpsecTunnelTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "VpnIpsecTunnelTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudNetworkCidrs")
    def cloud_network_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cloudNetworkCidrs"))

    @cloud_network_cidrs.setter
    def cloud_network_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7785561df20423487fa82a94d065b0949caeac2b4acbc34b58eafc09e6ec26f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudNetworkCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b9ef9ca9588dc4d11ac6b0b4f7d310cfc41ffbceab8e1c7b7beb0d832c55a93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gatewayId")
    def gateway_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayId"))

    @gateway_id.setter
    def gateway_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cf8fc1ce031ca2152842b278cf656e777edf7f64cc84de08149850ee0337e53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewayId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3079628f6095b7c6d595c3381b8b2caee59969921d933a548b6c8445b580b5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__307bacd4fa7045838a0d2281fda0d89a5bd352ddf130aeb60862dd58cece5f69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bfac453937eac9e4f542e68422c11ad961a8f3580610baf28d79ca7b5e7ed12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerNetworkCidrs")
    def peer_network_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "peerNetworkCidrs"))

    @peer_network_cidrs.setter
    def peer_network_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7efda0a2abe40d6b98a1a48526cbb480de2719d2b37a53b530c1bcb101015c0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerNetworkCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteHost")
    def remote_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteHost"))

    @remote_host.setter
    def remote_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f5410e5fdbd9424f3dab61876a23220ea060ca05faf4d960e07fd2a638849d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteHost", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelAuth",
    jsii_struct_bases=[],
    name_mapping={"method": "method", "psk_key": "pskKey"},
)
class VpnIpsecTunnelAuth:
    def __init__(
        self,
        *,
        method: typing.Optional[builtins.str] = None,
        psk_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param method: The Authentication Method to use for IPSec Authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#method VpnIpsecTunnel#method}
        :param psk_key: The Pre-Shared Key to use for IPSec Authentication. Note: Required if method is PSK. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#psk_key VpnIpsecTunnel#psk_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d7bd255cec4493404e3be65f3e662ee6015769e6ac84597ef4f09a068d27b8c)
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument psk_key", value=psk_key, expected_type=type_hints["psk_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if psk_key is not None:
            self._values["psk_key"] = psk_key

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''The Authentication Method to use for IPSec Authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#method VpnIpsecTunnel#method}
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def psk_key(self) -> typing.Optional[builtins.str]:
        '''The Pre-Shared Key to use for IPSec Authentication. Note: Required if method is PSK.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#psk_key VpnIpsecTunnel#psk_key}
        '''
        result = self._values.get("psk_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnIpsecTunnelAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpnIpsecTunnelAuthOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelAuthOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__75a02c49232b90e2d26e4de45e1b0661f9709cc54c21bb5eefeb2b2ee4ce32e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMethod")
    def reset_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMethod", []))

    @jsii.member(jsii_name="resetPskKey")
    def reset_psk_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPskKey", []))

    @builtins.property
    @jsii.member(jsii_name="methodInput")
    def method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "methodInput"))

    @builtins.property
    @jsii.member(jsii_name="pskKeyInput")
    def psk_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pskKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @method.setter
    def method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6177ab2ced51e2a8582764eed7e7c5a2b957791091a4b34702bd1b6ea352be43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "method", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pskKey")
    def psk_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pskKey"))

    @psk_key.setter
    def psk_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d01c517664f82090d0576dc1f803772ea53236e654c9fb033791990b5f0f26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pskKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VpnIpsecTunnelAuth]:
        return typing.cast(typing.Optional[VpnIpsecTunnelAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VpnIpsecTunnelAuth]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3def6dd3edbecba417f906f27d0c03a3d67ff1da2e974492da7d29e042cdb874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "auth": "auth",
        "cloud_network_cidrs": "cloudNetworkCidrs",
        "esp": "esp",
        "gateway_id": "gatewayId",
        "ike": "ike",
        "name": "name",
        "peer_network_cidrs": "peerNetworkCidrs",
        "remote_host": "remoteHost",
        "description": "description",
        "id": "id",
        "location": "location",
        "timeouts": "timeouts",
    },
)
class VpnIpsecTunnelConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        auth: typing.Union[VpnIpsecTunnelAuth, typing.Dict[builtins.str, typing.Any]],
        cloud_network_cidrs: typing.Sequence[builtins.str],
        esp: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VpnIpsecTunnelEsp", typing.Dict[builtins.str, typing.Any]]]],
        gateway_id: builtins.str,
        ike: typing.Union["VpnIpsecTunnelIke", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        peer_network_cidrs: typing.Sequence[builtins.str],
        remote_host: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["VpnIpsecTunnelTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param auth: auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#auth VpnIpsecTunnel#auth}
        :param cloud_network_cidrs: The network CIDRs on the "Left" side that are allowed to connect to the IPSec tunnel, i.e. the CIDRs within your IONOS Cloud LAN. Specify "0.0.0.0/0" or "::/0" for all addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#cloud_network_cidrs VpnIpsecTunnel#cloud_network_cidrs}
        :param esp: esp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#esp VpnIpsecTunnel#esp}
        :param gateway_id: The ID of the IPSec Gateway that the tunnel belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#gateway_id VpnIpsecTunnel#gateway_id}
        :param ike: ike block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#ike VpnIpsecTunnel#ike}
        :param name: The human-readable name of your IPSec Gateway Tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#name VpnIpsecTunnel#name}
        :param peer_network_cidrs: The network CIDRs on the "Right" side that are allowed to connect to the IPSec tunnel. Specify "0.0.0.0/0" or "::/0" for all addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#peer_network_cidrs VpnIpsecTunnel#peer_network_cidrs}
        :param remote_host: The remote peer host fully qualified domain name or public IPV4 IP to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#remote_host VpnIpsecTunnel#remote_host}
        :param description: The human-readable description of your IPSec Gateway Tunnel. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#description VpnIpsecTunnel#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#id VpnIpsecTunnel#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param location: The location of the IPSec Gateway Tunnel. Supported locations: de/fra, de/fra/2, de/txl, es/vit, gb/bhx, gb/lhr, us/ewr, us/las, us/mci, fr/par. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#location VpnIpsecTunnel#location}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#timeouts VpnIpsecTunnel#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(auth, dict):
            auth = VpnIpsecTunnelAuth(**auth)
        if isinstance(ike, dict):
            ike = VpnIpsecTunnelIke(**ike)
        if isinstance(timeouts, dict):
            timeouts = VpnIpsecTunnelTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12dab8e30aae75bdad1012c11f080b6b69e92e570f1659953071cf17ff14948c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument auth", value=auth, expected_type=type_hints["auth"])
            check_type(argname="argument cloud_network_cidrs", value=cloud_network_cidrs, expected_type=type_hints["cloud_network_cidrs"])
            check_type(argname="argument esp", value=esp, expected_type=type_hints["esp"])
            check_type(argname="argument gateway_id", value=gateway_id, expected_type=type_hints["gateway_id"])
            check_type(argname="argument ike", value=ike, expected_type=type_hints["ike"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument peer_network_cidrs", value=peer_network_cidrs, expected_type=type_hints["peer_network_cidrs"])
            check_type(argname="argument remote_host", value=remote_host, expected_type=type_hints["remote_host"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth": auth,
            "cloud_network_cidrs": cloud_network_cidrs,
            "esp": esp,
            "gateway_id": gateway_id,
            "ike": ike,
            "name": name,
            "peer_network_cidrs": peer_network_cidrs,
            "remote_host": remote_host,
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
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if location is not None:
            self._values["location"] = location
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
    def auth(self) -> VpnIpsecTunnelAuth:
        '''auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#auth VpnIpsecTunnel#auth}
        '''
        result = self._values.get("auth")
        assert result is not None, "Required property 'auth' is missing"
        return typing.cast(VpnIpsecTunnelAuth, result)

    @builtins.property
    def cloud_network_cidrs(self) -> typing.List[builtins.str]:
        '''The network CIDRs on the "Left" side that are allowed to connect to the IPSec tunnel, i.e. the CIDRs within your IONOS Cloud LAN. Specify "0.0.0.0/0" or "::/0" for all addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#cloud_network_cidrs VpnIpsecTunnel#cloud_network_cidrs}
        '''
        result = self._values.get("cloud_network_cidrs")
        assert result is not None, "Required property 'cloud_network_cidrs' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def esp(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VpnIpsecTunnelEsp"]]:
        '''esp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#esp VpnIpsecTunnel#esp}
        '''
        result = self._values.get("esp")
        assert result is not None, "Required property 'esp' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VpnIpsecTunnelEsp"]], result)

    @builtins.property
    def gateway_id(self) -> builtins.str:
        '''The ID of the IPSec Gateway that the tunnel belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#gateway_id VpnIpsecTunnel#gateway_id}
        '''
        result = self._values.get("gateway_id")
        assert result is not None, "Required property 'gateway_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ike(self) -> "VpnIpsecTunnelIke":
        '''ike block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#ike VpnIpsecTunnel#ike}
        '''
        result = self._values.get("ike")
        assert result is not None, "Required property 'ike' is missing"
        return typing.cast("VpnIpsecTunnelIke", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The human-readable name of your IPSec Gateway Tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#name VpnIpsecTunnel#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def peer_network_cidrs(self) -> typing.List[builtins.str]:
        '''The network CIDRs on the "Right" side that are allowed to connect to the IPSec tunnel.

        Specify "0.0.0.0/0" or "::/0" for all addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#peer_network_cidrs VpnIpsecTunnel#peer_network_cidrs}
        '''
        result = self._values.get("peer_network_cidrs")
        assert result is not None, "Required property 'peer_network_cidrs' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def remote_host(self) -> builtins.str:
        '''The remote peer host fully qualified domain name or public IPV4 IP to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#remote_host VpnIpsecTunnel#remote_host}
        '''
        result = self._values.get("remote_host")
        assert result is not None, "Required property 'remote_host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The human-readable description of your IPSec Gateway Tunnel.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#description VpnIpsecTunnel#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#id VpnIpsecTunnel#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''The location of the IPSec Gateway Tunnel. Supported locations: de/fra, de/fra/2, de/txl, es/vit, gb/bhx, gb/lhr, us/ewr, us/las, us/mci, fr/par.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#location VpnIpsecTunnel#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["VpnIpsecTunnelTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#timeouts VpnIpsecTunnel#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["VpnIpsecTunnelTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnIpsecTunnelConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelEsp",
    jsii_struct_bases=[],
    name_mapping={
        "diffie_hellman_group": "diffieHellmanGroup",
        "encryption_algorithm": "encryptionAlgorithm",
        "integrity_algorithm": "integrityAlgorithm",
        "lifetime": "lifetime",
    },
)
class VpnIpsecTunnelEsp:
    def __init__(
        self,
        *,
        diffie_hellman_group: typing.Optional[builtins.str] = None,
        encryption_algorithm: typing.Optional[builtins.str] = None,
        integrity_algorithm: typing.Optional[builtins.str] = None,
        lifetime: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param diffie_hellman_group: The Diffie-Hellman Group to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#diffie_hellman_group VpnIpsecTunnel#diffie_hellman_group}
        :param encryption_algorithm: The encryption algorithm to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#encryption_algorithm VpnIpsecTunnel#encryption_algorithm}
        :param integrity_algorithm: The integrity algorithm to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#integrity_algorithm VpnIpsecTunnel#integrity_algorithm}
        :param lifetime: The phase lifetime in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#lifetime VpnIpsecTunnel#lifetime}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__165b3c7068943409c6b194606b28b45042f8904464de974a2d07af56c1fd6ddb)
            check_type(argname="argument diffie_hellman_group", value=diffie_hellman_group, expected_type=type_hints["diffie_hellman_group"])
            check_type(argname="argument encryption_algorithm", value=encryption_algorithm, expected_type=type_hints["encryption_algorithm"])
            check_type(argname="argument integrity_algorithm", value=integrity_algorithm, expected_type=type_hints["integrity_algorithm"])
            check_type(argname="argument lifetime", value=lifetime, expected_type=type_hints["lifetime"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if diffie_hellman_group is not None:
            self._values["diffie_hellman_group"] = diffie_hellman_group
        if encryption_algorithm is not None:
            self._values["encryption_algorithm"] = encryption_algorithm
        if integrity_algorithm is not None:
            self._values["integrity_algorithm"] = integrity_algorithm
        if lifetime is not None:
            self._values["lifetime"] = lifetime

    @builtins.property
    def diffie_hellman_group(self) -> typing.Optional[builtins.str]:
        '''The Diffie-Hellman Group to use for IPSec Encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#diffie_hellman_group VpnIpsecTunnel#diffie_hellman_group}
        '''
        result = self._values.get("diffie_hellman_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_algorithm(self) -> typing.Optional[builtins.str]:
        '''The encryption algorithm to use for IPSec Encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#encryption_algorithm VpnIpsecTunnel#encryption_algorithm}
        '''
        result = self._values.get("encryption_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integrity_algorithm(self) -> typing.Optional[builtins.str]:
        '''The integrity algorithm to use for IPSec Encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#integrity_algorithm VpnIpsecTunnel#integrity_algorithm}
        '''
        result = self._values.get("integrity_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifetime(self) -> typing.Optional[jsii.Number]:
        '''The phase lifetime in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#lifetime VpnIpsecTunnel#lifetime}
        '''
        result = self._values.get("lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnIpsecTunnelEsp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpnIpsecTunnelEspList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelEspList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32ab75921cddbe00ad1589bfadc6152870f28142f590d727437bc9fb6c0fc170)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VpnIpsecTunnelEspOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b092a7ac5e3d9675db024e7bbcd1357f6fef56f89b1a0ef1dab843915a54e865)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VpnIpsecTunnelEspOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a29c6e4a9ec1e3ddab12fb50340a091b9ee464d0774062a8cf250bf11d0db73)
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
            type_hints = typing.get_type_hints(_typecheckingstub__edc5e544bd3b069c744c5aa4e199e9ae62ade9d01413ec4844507f26dde9d05c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a47b6972886051a917eca8c4157e7ac5663621a6de5f401756a52088c45ad5b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VpnIpsecTunnelEsp]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VpnIpsecTunnelEsp]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VpnIpsecTunnelEsp]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d93bcf81a2646b7c5daa8c9a284049118060e5ef15f12bd5eb93bfa3d864f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VpnIpsecTunnelEspOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelEspOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__838d946724decab9eab4ef74b38ee742095d2c2a51cb0c68aa620b8c58defd98)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDiffieHellmanGroup")
    def reset_diffie_hellman_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiffieHellmanGroup", []))

    @jsii.member(jsii_name="resetEncryptionAlgorithm")
    def reset_encryption_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAlgorithm", []))

    @jsii.member(jsii_name="resetIntegrityAlgorithm")
    def reset_integrity_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrityAlgorithm", []))

    @jsii.member(jsii_name="resetLifetime")
    def reset_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLifetime", []))

    @builtins.property
    @jsii.member(jsii_name="diffieHellmanGroupInput")
    def diffie_hellman_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diffieHellmanGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAlgorithmInput")
    def encryption_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="integrityAlgorithmInput")
    def integrity_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrityAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="lifetimeInput")
    def lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="diffieHellmanGroup")
    def diffie_hellman_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diffieHellmanGroup"))

    @diffie_hellman_group.setter
    def diffie_hellman_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58d3dc9ea34b25526de1af6ac8b8ece82c2e162813eca51c9fe45bf105055a92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diffieHellmanGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionAlgorithm")
    def encryption_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionAlgorithm"))

    @encryption_algorithm.setter
    def encryption_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff16c4a280c86f6a5e818eceaedb7c9e12ee3fe383a1210f93e9434d0ba59e05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="integrityAlgorithm")
    def integrity_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrityAlgorithm"))

    @integrity_algorithm.setter
    def integrity_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79aebe901a8e1496af52c77e629e3ff8c447aaccf8de0f2249470ba07b0816a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrityAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lifetime")
    def lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lifetime"))

    @lifetime.setter
    def lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beccee8aae7263899eb1cc69336acf82b527e5849c56708f68c721527e6e6a92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelEsp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelEsp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelEsp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9a3e5375bbfece42f7ed7f2e1680716db78e7f5211d7d7408603cb3fe852978)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelIke",
    jsii_struct_bases=[],
    name_mapping={
        "diffie_hellman_group": "diffieHellmanGroup",
        "encryption_algorithm": "encryptionAlgorithm",
        "integrity_algorithm": "integrityAlgorithm",
        "lifetime": "lifetime",
    },
)
class VpnIpsecTunnelIke:
    def __init__(
        self,
        *,
        diffie_hellman_group: typing.Optional[builtins.str] = None,
        encryption_algorithm: typing.Optional[builtins.str] = None,
        integrity_algorithm: typing.Optional[builtins.str] = None,
        lifetime: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param diffie_hellman_group: The Diffie-Hellman Group to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#diffie_hellman_group VpnIpsecTunnel#diffie_hellman_group}
        :param encryption_algorithm: The encryption algorithm to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#encryption_algorithm VpnIpsecTunnel#encryption_algorithm}
        :param integrity_algorithm: The integrity algorithm to use for IPSec Encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#integrity_algorithm VpnIpsecTunnel#integrity_algorithm}
        :param lifetime: The phase lifetime in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#lifetime VpnIpsecTunnel#lifetime}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__935fcaf356f89386df57ac570a1ba881a1880fa1a10f29723db720742b1bcc28)
            check_type(argname="argument diffie_hellman_group", value=diffie_hellman_group, expected_type=type_hints["diffie_hellman_group"])
            check_type(argname="argument encryption_algorithm", value=encryption_algorithm, expected_type=type_hints["encryption_algorithm"])
            check_type(argname="argument integrity_algorithm", value=integrity_algorithm, expected_type=type_hints["integrity_algorithm"])
            check_type(argname="argument lifetime", value=lifetime, expected_type=type_hints["lifetime"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if diffie_hellman_group is not None:
            self._values["diffie_hellman_group"] = diffie_hellman_group
        if encryption_algorithm is not None:
            self._values["encryption_algorithm"] = encryption_algorithm
        if integrity_algorithm is not None:
            self._values["integrity_algorithm"] = integrity_algorithm
        if lifetime is not None:
            self._values["lifetime"] = lifetime

    @builtins.property
    def diffie_hellman_group(self) -> typing.Optional[builtins.str]:
        '''The Diffie-Hellman Group to use for IPSec Encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#diffie_hellman_group VpnIpsecTunnel#diffie_hellman_group}
        '''
        result = self._values.get("diffie_hellman_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_algorithm(self) -> typing.Optional[builtins.str]:
        '''The encryption algorithm to use for IPSec Encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#encryption_algorithm VpnIpsecTunnel#encryption_algorithm}
        '''
        result = self._values.get("encryption_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def integrity_algorithm(self) -> typing.Optional[builtins.str]:
        '''The integrity algorithm to use for IPSec Encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#integrity_algorithm VpnIpsecTunnel#integrity_algorithm}
        '''
        result = self._values.get("integrity_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifetime(self) -> typing.Optional[jsii.Number]:
        '''The phase lifetime in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#lifetime VpnIpsecTunnel#lifetime}
        '''
        result = self._values.get("lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnIpsecTunnelIke(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpnIpsecTunnelIkeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelIkeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd709da232fc7c48ca9d943aa6a78806130b2d5bec331b64a0b166911dd41b2d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDiffieHellmanGroup")
    def reset_diffie_hellman_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiffieHellmanGroup", []))

    @jsii.member(jsii_name="resetEncryptionAlgorithm")
    def reset_encryption_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAlgorithm", []))

    @jsii.member(jsii_name="resetIntegrityAlgorithm")
    def reset_integrity_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrityAlgorithm", []))

    @jsii.member(jsii_name="resetLifetime")
    def reset_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLifetime", []))

    @builtins.property
    @jsii.member(jsii_name="diffieHellmanGroupInput")
    def diffie_hellman_group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "diffieHellmanGroupInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAlgorithmInput")
    def encryption_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="integrityAlgorithmInput")
    def integrity_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrityAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="lifetimeInput")
    def lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="diffieHellmanGroup")
    def diffie_hellman_group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "diffieHellmanGroup"))

    @diffie_hellman_group.setter
    def diffie_hellman_group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a39038ecb154694f79533f8a7a8dd6bfef77ac825df8ffbdebcd1063d50ea01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diffieHellmanGroup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionAlgorithm")
    def encryption_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionAlgorithm"))

    @encryption_algorithm.setter
    def encryption_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67a6f2601eb9688a529872775209b00ae049e6034157e74838421b42e2e061dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="integrityAlgorithm")
    def integrity_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrityAlgorithm"))

    @integrity_algorithm.setter
    def integrity_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68d5040ede1a23c519faa5347b49e0bfffff17459e5826bc5b5303512821a54b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrityAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lifetime")
    def lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lifetime"))

    @lifetime.setter
    def lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b145465172fbad967ca84f968e32dc1163414cdaee471733ef79d8cbbebf77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[VpnIpsecTunnelIke]:
        return typing.cast(typing.Optional[VpnIpsecTunnelIke], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[VpnIpsecTunnelIke]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d88365540bf7b3d10d8928744949bf822be1b316237d4f8595f345b7d477ce19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "default": "default",
        "delete": "delete",
        "update": "update",
    },
)
class VpnIpsecTunnelTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#create VpnIpsecTunnel#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#default VpnIpsecTunnel#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#delete VpnIpsecTunnel#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#update VpnIpsecTunnel#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2f091d3ff4a5dffad1d95c2095721d656b19ad33e10664e34f18640a59239b2)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#create VpnIpsecTunnel#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#default VpnIpsecTunnel#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#delete VpnIpsecTunnel#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/vpn_ipsec_tunnel#update VpnIpsecTunnel#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpnIpsecTunnelTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VpnIpsecTunnelTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.vpnIpsecTunnel.VpnIpsecTunnelTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__829205046bedd849271671d95d9c0269ef493e1d2ce1b286801c9ab7ec957e7c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__78c697715c8927b69b8350cfe8dc4cd122bc281869f7e94caba818eddd451bed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44e20ac6eb0b99d1a3628637bc26e45f8e2e956471b32c024f92c87cea8585b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a0f71b19d8c7b531b6db90176625434dfd5c8260deee21cb14115d5e670400)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6605611658f9412713f1e80482a2e627df0fd1d1b64b7e081eebf2bfb628bbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0304ab15b83496ea6555c0b5ac2b72f0fb815912a3ecd99d20d92ee56f67bb4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "VpnIpsecTunnel",
    "VpnIpsecTunnelAuth",
    "VpnIpsecTunnelAuthOutputReference",
    "VpnIpsecTunnelConfig",
    "VpnIpsecTunnelEsp",
    "VpnIpsecTunnelEspList",
    "VpnIpsecTunnelEspOutputReference",
    "VpnIpsecTunnelIke",
    "VpnIpsecTunnelIkeOutputReference",
    "VpnIpsecTunnelTimeouts",
    "VpnIpsecTunnelTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__7d339d4368b171c0eccad9578bd020ca225f63064e5f07946247f0d69c923f57(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    auth: typing.Union[VpnIpsecTunnelAuth, typing.Dict[builtins.str, typing.Any]],
    cloud_network_cidrs: typing.Sequence[builtins.str],
    esp: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VpnIpsecTunnelEsp, typing.Dict[builtins.str, typing.Any]]]],
    gateway_id: builtins.str,
    ike: typing.Union[VpnIpsecTunnelIke, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    peer_network_cidrs: typing.Sequence[builtins.str],
    remote_host: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    location: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[VpnIpsecTunnelTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__993d1b888b6052ee7bfa933e21e1ec881eb176711c3ea435ad9d0bd24ef4896f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe132af9ab2784da63e2ceb7985bc2f2cd6fe74cbe4b7ebc13a2ab48780397c3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VpnIpsecTunnelEsp, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7785561df20423487fa82a94d065b0949caeac2b4acbc34b58eafc09e6ec26f7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b9ef9ca9588dc4d11ac6b0b4f7d310cfc41ffbceab8e1c7b7beb0d832c55a93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cf8fc1ce031ca2152842b278cf656e777edf7f64cc84de08149850ee0337e53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3079628f6095b7c6d595c3381b8b2caee59969921d933a548b6c8445b580b5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307bacd4fa7045838a0d2281fda0d89a5bd352ddf130aeb60862dd58cece5f69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bfac453937eac9e4f542e68422c11ad961a8f3580610baf28d79ca7b5e7ed12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7efda0a2abe40d6b98a1a48526cbb480de2719d2b37a53b530c1bcb101015c0d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f5410e5fdbd9424f3dab61876a23220ea060ca05faf4d960e07fd2a638849d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d7bd255cec4493404e3be65f3e662ee6015769e6ac84597ef4f09a068d27b8c(
    *,
    method: typing.Optional[builtins.str] = None,
    psk_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75a02c49232b90e2d26e4de45e1b0661f9709cc54c21bb5eefeb2b2ee4ce32e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6177ab2ced51e2a8582764eed7e7c5a2b957791091a4b34702bd1b6ea352be43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d01c517664f82090d0576dc1f803772ea53236e654c9fb033791990b5f0f26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3def6dd3edbecba417f906f27d0c03a3d67ff1da2e974492da7d29e042cdb874(
    value: typing.Optional[VpnIpsecTunnelAuth],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12dab8e30aae75bdad1012c11f080b6b69e92e570f1659953071cf17ff14948c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth: typing.Union[VpnIpsecTunnelAuth, typing.Dict[builtins.str, typing.Any]],
    cloud_network_cidrs: typing.Sequence[builtins.str],
    esp: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VpnIpsecTunnelEsp, typing.Dict[builtins.str, typing.Any]]]],
    gateway_id: builtins.str,
    ike: typing.Union[VpnIpsecTunnelIke, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
    peer_network_cidrs: typing.Sequence[builtins.str],
    remote_host: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    location: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[VpnIpsecTunnelTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__165b3c7068943409c6b194606b28b45042f8904464de974a2d07af56c1fd6ddb(
    *,
    diffie_hellman_group: typing.Optional[builtins.str] = None,
    encryption_algorithm: typing.Optional[builtins.str] = None,
    integrity_algorithm: typing.Optional[builtins.str] = None,
    lifetime: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32ab75921cddbe00ad1589bfadc6152870f28142f590d727437bc9fb6c0fc170(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b092a7ac5e3d9675db024e7bbcd1357f6fef56f89b1a0ef1dab843915a54e865(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a29c6e4a9ec1e3ddab12fb50340a091b9ee464d0774062a8cf250bf11d0db73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edc5e544bd3b069c744c5aa4e199e9ae62ade9d01413ec4844507f26dde9d05c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a47b6972886051a917eca8c4157e7ac5663621a6de5f401756a52088c45ad5b0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d93bcf81a2646b7c5daa8c9a284049118060e5ef15f12bd5eb93bfa3d864f7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VpnIpsecTunnelEsp]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__838d946724decab9eab4ef74b38ee742095d2c2a51cb0c68aa620b8c58defd98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d3dc9ea34b25526de1af6ac8b8ece82c2e162813eca51c9fe45bf105055a92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff16c4a280c86f6a5e818eceaedb7c9e12ee3fe383a1210f93e9434d0ba59e05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79aebe901a8e1496af52c77e629e3ff8c447aaccf8de0f2249470ba07b0816a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beccee8aae7263899eb1cc69336acf82b527e5849c56708f68c721527e6e6a92(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9a3e5375bbfece42f7ed7f2e1680716db78e7f5211d7d7408603cb3fe852978(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelEsp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__935fcaf356f89386df57ac570a1ba881a1880fa1a10f29723db720742b1bcc28(
    *,
    diffie_hellman_group: typing.Optional[builtins.str] = None,
    encryption_algorithm: typing.Optional[builtins.str] = None,
    integrity_algorithm: typing.Optional[builtins.str] = None,
    lifetime: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd709da232fc7c48ca9d943aa6a78806130b2d5bec331b64a0b166911dd41b2d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a39038ecb154694f79533f8a7a8dd6bfef77ac825df8ffbdebcd1063d50ea01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67a6f2601eb9688a529872775209b00ae049e6034157e74838421b42e2e061dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68d5040ede1a23c519faa5347b49e0bfffff17459e5826bc5b5303512821a54b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b145465172fbad967ca84f968e32dc1163414cdaee471733ef79d8cbbebf77(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d88365540bf7b3d10d8928744949bf822be1b316237d4f8595f345b7d477ce19(
    value: typing.Optional[VpnIpsecTunnelIke],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f091d3ff4a5dffad1d95c2095721d656b19ad33e10664e34f18640a59239b2(
    *,
    create: typing.Optional[builtins.str] = None,
    default: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__829205046bedd849271671d95d9c0269ef493e1d2ce1b286801c9ab7ec957e7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78c697715c8927b69b8350cfe8dc4cd122bc281869f7e94caba818eddd451bed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44e20ac6eb0b99d1a3628637bc26e45f8e2e956471b32c024f92c87cea8585b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a0f71b19d8c7b531b6db90176625434dfd5c8260deee21cb14115d5e670400(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6605611658f9412713f1e80482a2e627df0fd1d1b64b7e081eebf2bfb628bbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0304ab15b83496ea6555c0b5ac2b72f0fb815912a3ecd99d20d92ee56f67bb4a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, VpnIpsecTunnelTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
