r'''
# `ionoscloud_s3_bucket_website_configuration`

Refer to the Terraform Registry for docs: [`ionoscloud_s3_bucket_website_configuration`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration).
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


class S3BucketWebsiteConfiguration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfiguration",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration ionoscloud_s3_bucket_website_configuration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        error_document: typing.Optional[typing.Union["S3BucketWebsiteConfigurationErrorDocument", typing.Dict[builtins.str, typing.Any]]] = None,
        index_document: typing.Optional[typing.Union["S3BucketWebsiteConfigurationIndexDocument", typing.Dict[builtins.str, typing.Any]]] = None,
        redirect_all_requests_to: typing.Optional[typing.Union["S3BucketWebsiteConfigurationRedirectAllRequestsTo", typing.Dict[builtins.str, typing.Any]]] = None,
        routing_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["S3BucketWebsiteConfigurationRoutingRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration ionoscloud_s3_bucket_website_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: The name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#bucket S3BucketWebsiteConfiguration#bucket}
        :param error_document: error_document block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#error_document S3BucketWebsiteConfiguration#error_document}
        :param index_document: index_document block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#index_document S3BucketWebsiteConfiguration#index_document}
        :param redirect_all_requests_to: redirect_all_requests_to block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#redirect_all_requests_to S3BucketWebsiteConfiguration#redirect_all_requests_to}
        :param routing_rule: routing_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#routing_rule S3BucketWebsiteConfiguration#routing_rule}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a408792e6be0150a4f7956d125634baa2456997c298363ffb14250f637a2675d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = S3BucketWebsiteConfigurationConfig(
            bucket=bucket,
            error_document=error_document,
            index_document=index_document,
            redirect_all_requests_to=redirect_all_requests_to,
            routing_rule=routing_rule,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a S3BucketWebsiteConfiguration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the S3BucketWebsiteConfiguration to import.
        :param import_from_id: The id of the existing S3BucketWebsiteConfiguration that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the S3BucketWebsiteConfiguration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43f8ca40a15ee1d8a0fe5e6f1b0efe905b25921db7c9101284f7c826d42da721)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putErrorDocument")
    def put_error_document(self, *, key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param key: The object key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#key S3BucketWebsiteConfiguration#key}
        '''
        value = S3BucketWebsiteConfigurationErrorDocument(key=key)

        return typing.cast(None, jsii.invoke(self, "putErrorDocument", [value]))

    @jsii.member(jsii_name="putIndexDocument")
    def put_index_document(
        self,
        *,
        suffix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param suffix: A suffix that is appended to a request that is for a directory on the website endpoint (for example, if the suffix is index.html and you make a request to samplebucket/images/ the data that is returned will be for the object with the key name images/index.html) The suffix must not be empty and must not include a slash character. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#suffix S3BucketWebsiteConfiguration#suffix}
        '''
        value = S3BucketWebsiteConfigurationIndexDocument(suffix=suffix)

        return typing.cast(None, jsii.invoke(self, "putIndexDocument", [value]))

    @jsii.member(jsii_name="putRedirectAllRequestsTo")
    def put_redirect_all_requests_to(
        self,
        *,
        host_name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_name: The host name to use in the redirect request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#host_name S3BucketWebsiteConfiguration#host_name}
        :param protocol: Protocol to use when redirecting requests. The default is the protocol that is used in the original request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#protocol S3BucketWebsiteConfiguration#protocol}
        '''
        value = S3BucketWebsiteConfigurationRedirectAllRequestsTo(
            host_name=host_name, protocol=protocol
        )

        return typing.cast(None, jsii.invoke(self, "putRedirectAllRequestsTo", [value]))

    @jsii.member(jsii_name="putRoutingRule")
    def put_routing_rule(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["S3BucketWebsiteConfigurationRoutingRule", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11163039321cef117b54a55e720203e4367c5e2b2a01506e2eef3c8341e37739)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRoutingRule", [value]))

    @jsii.member(jsii_name="resetErrorDocument")
    def reset_error_document(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetErrorDocument", []))

    @jsii.member(jsii_name="resetIndexDocument")
    def reset_index_document(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexDocument", []))

    @jsii.member(jsii_name="resetRedirectAllRequestsTo")
    def reset_redirect_all_requests_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectAllRequestsTo", []))

    @jsii.member(jsii_name="resetRoutingRule")
    def reset_routing_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoutingRule", []))

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
    @jsii.member(jsii_name="errorDocument")
    def error_document(
        self,
    ) -> "S3BucketWebsiteConfigurationErrorDocumentOutputReference":
        return typing.cast("S3BucketWebsiteConfigurationErrorDocumentOutputReference", jsii.get(self, "errorDocument"))

    @builtins.property
    @jsii.member(jsii_name="indexDocument")
    def index_document(
        self,
    ) -> "S3BucketWebsiteConfigurationIndexDocumentOutputReference":
        return typing.cast("S3BucketWebsiteConfigurationIndexDocumentOutputReference", jsii.get(self, "indexDocument"))

    @builtins.property
    @jsii.member(jsii_name="redirectAllRequestsTo")
    def redirect_all_requests_to(
        self,
    ) -> "S3BucketWebsiteConfigurationRedirectAllRequestsToOutputReference":
        return typing.cast("S3BucketWebsiteConfigurationRedirectAllRequestsToOutputReference", jsii.get(self, "redirectAllRequestsTo"))

    @builtins.property
    @jsii.member(jsii_name="routingRule")
    def routing_rule(self) -> "S3BucketWebsiteConfigurationRoutingRuleList":
        return typing.cast("S3BucketWebsiteConfigurationRoutingRuleList", jsii.get(self, "routingRule"))

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="errorDocumentInput")
    def error_document_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationErrorDocument"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationErrorDocument"]], jsii.get(self, "errorDocumentInput"))

    @builtins.property
    @jsii.member(jsii_name="indexDocumentInput")
    def index_document_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationIndexDocument"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationIndexDocument"]], jsii.get(self, "indexDocumentInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectAllRequestsToInput")
    def redirect_all_requests_to_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationRedirectAllRequestsTo"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationRedirectAllRequestsTo"]], jsii.get(self, "redirectAllRequestsToInput"))

    @builtins.property
    @jsii.member(jsii_name="routingRuleInput")
    def routing_rule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["S3BucketWebsiteConfigurationRoutingRule"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["S3BucketWebsiteConfigurationRoutingRule"]]], jsii.get(self, "routingRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__147276d9198fa27dbc5b910546dc373e8d2e2f5c295b6cd64ab70b81dd619639)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "bucket": "bucket",
        "error_document": "errorDocument",
        "index_document": "indexDocument",
        "redirect_all_requests_to": "redirectAllRequestsTo",
        "routing_rule": "routingRule",
    },
)
class S3BucketWebsiteConfigurationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        bucket: builtins.str,
        error_document: typing.Optional[typing.Union["S3BucketWebsiteConfigurationErrorDocument", typing.Dict[builtins.str, typing.Any]]] = None,
        index_document: typing.Optional[typing.Union["S3BucketWebsiteConfigurationIndexDocument", typing.Dict[builtins.str, typing.Any]]] = None,
        redirect_all_requests_to: typing.Optional[typing.Union["S3BucketWebsiteConfigurationRedirectAllRequestsTo", typing.Dict[builtins.str, typing.Any]]] = None,
        routing_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["S3BucketWebsiteConfigurationRoutingRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param bucket: The name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#bucket S3BucketWebsiteConfiguration#bucket}
        :param error_document: error_document block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#error_document S3BucketWebsiteConfiguration#error_document}
        :param index_document: index_document block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#index_document S3BucketWebsiteConfiguration#index_document}
        :param redirect_all_requests_to: redirect_all_requests_to block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#redirect_all_requests_to S3BucketWebsiteConfiguration#redirect_all_requests_to}
        :param routing_rule: routing_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#routing_rule S3BucketWebsiteConfiguration#routing_rule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(error_document, dict):
            error_document = S3BucketWebsiteConfigurationErrorDocument(**error_document)
        if isinstance(index_document, dict):
            index_document = S3BucketWebsiteConfigurationIndexDocument(**index_document)
        if isinstance(redirect_all_requests_to, dict):
            redirect_all_requests_to = S3BucketWebsiteConfigurationRedirectAllRequestsTo(**redirect_all_requests_to)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bee36cb17757ef2db94022e05e6ab18ccb25961ac20931607aee2c9828aed2bf)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument error_document", value=error_document, expected_type=type_hints["error_document"])
            check_type(argname="argument index_document", value=index_document, expected_type=type_hints["index_document"])
            check_type(argname="argument redirect_all_requests_to", value=redirect_all_requests_to, expected_type=type_hints["redirect_all_requests_to"])
            check_type(argname="argument routing_rule", value=routing_rule, expected_type=type_hints["routing_rule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
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
        if error_document is not None:
            self._values["error_document"] = error_document
        if index_document is not None:
            self._values["index_document"] = index_document
        if redirect_all_requests_to is not None:
            self._values["redirect_all_requests_to"] = redirect_all_requests_to
        if routing_rule is not None:
            self._values["routing_rule"] = routing_rule

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
    def bucket(self) -> builtins.str:
        '''The name of the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#bucket S3BucketWebsiteConfiguration#bucket}
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def error_document(
        self,
    ) -> typing.Optional["S3BucketWebsiteConfigurationErrorDocument"]:
        '''error_document block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#error_document S3BucketWebsiteConfiguration#error_document}
        '''
        result = self._values.get("error_document")
        return typing.cast(typing.Optional["S3BucketWebsiteConfigurationErrorDocument"], result)

    @builtins.property
    def index_document(
        self,
    ) -> typing.Optional["S3BucketWebsiteConfigurationIndexDocument"]:
        '''index_document block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#index_document S3BucketWebsiteConfiguration#index_document}
        '''
        result = self._values.get("index_document")
        return typing.cast(typing.Optional["S3BucketWebsiteConfigurationIndexDocument"], result)

    @builtins.property
    def redirect_all_requests_to(
        self,
    ) -> typing.Optional["S3BucketWebsiteConfigurationRedirectAllRequestsTo"]:
        '''redirect_all_requests_to block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#redirect_all_requests_to S3BucketWebsiteConfiguration#redirect_all_requests_to}
        '''
        result = self._values.get("redirect_all_requests_to")
        return typing.cast(typing.Optional["S3BucketWebsiteConfigurationRedirectAllRequestsTo"], result)

    @builtins.property
    def routing_rule(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["S3BucketWebsiteConfigurationRoutingRule"]]]:
        '''routing_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#routing_rule S3BucketWebsiteConfiguration#routing_rule}
        '''
        result = self._values.get("routing_rule")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["S3BucketWebsiteConfigurationRoutingRule"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationErrorDocument",
    jsii_struct_bases=[],
    name_mapping={"key": "key"},
)
class S3BucketWebsiteConfigurationErrorDocument:
    def __init__(self, *, key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param key: The object key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#key S3BucketWebsiteConfiguration#key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__268c37ec094c1b068e493b53329e632d54e57b31a061f61eb413c37772232800)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''The object key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#key S3BucketWebsiteConfiguration#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationErrorDocument(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketWebsiteConfigurationErrorDocumentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationErrorDocumentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9a644559fd10fa98949e7f19d90c015bbd8bb6b3b4807baa7738c69b4ee9b17)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed8ee253a5e550f150318250489610dc841a0b1b709742ba2e5cc6205ce9890b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationErrorDocument]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationErrorDocument]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationErrorDocument]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ef5f72f7c268731da86385a18a4710935052242685363cc9557509bee27efea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationIndexDocument",
    jsii_struct_bases=[],
    name_mapping={"suffix": "suffix"},
)
class S3BucketWebsiteConfigurationIndexDocument:
    def __init__(self, *, suffix: typing.Optional[builtins.str] = None) -> None:
        '''
        :param suffix: A suffix that is appended to a request that is for a directory on the website endpoint (for example, if the suffix is index.html and you make a request to samplebucket/images/ the data that is returned will be for the object with the key name images/index.html) The suffix must not be empty and must not include a slash character. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#suffix S3BucketWebsiteConfiguration#suffix}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8bdbc0eae9f00b81c8bb1577d95afdd38bcd00ee4498bea9d2bdbbedc141606)
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if suffix is not None:
            self._values["suffix"] = suffix

    @builtins.property
    def suffix(self) -> typing.Optional[builtins.str]:
        '''A suffix that is appended to a request that is for a directory on the website endpoint (for example, if the suffix is index.html and you make a request to samplebucket/images/ the data that is returned will be for the object with the key name images/index.html) The suffix must not be empty and must not include a slash character. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#suffix S3BucketWebsiteConfiguration#suffix}
        '''
        result = self._values.get("suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationIndexDocument(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketWebsiteConfigurationIndexDocumentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationIndexDocumentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a71b0a4a62e585c11fa3d7140410b66a4798bd4bbcc047e54c9040bfa33430cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetSuffix")
    def reset_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuffix", []))

    @builtins.property
    @jsii.member(jsii_name="suffixInput")
    def suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "suffixInput"))

    @builtins.property
    @jsii.member(jsii_name="suffix")
    def suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "suffix"))

    @suffix.setter
    def suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e41ae797e2c9fc0561c7793779effa68ef2ec67bff3b10387a5fdcd8c21f5e45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "suffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationIndexDocument]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationIndexDocument]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationIndexDocument]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48ec2fd423f01fd13ae13e91a0cf89b9ecc313a52833c2870c5d5d63c041179b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRedirectAllRequestsTo",
    jsii_struct_bases=[],
    name_mapping={"host_name": "hostName", "protocol": "protocol"},
)
class S3BucketWebsiteConfigurationRedirectAllRequestsTo:
    def __init__(
        self,
        *,
        host_name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_name: The host name to use in the redirect request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#host_name S3BucketWebsiteConfiguration#host_name}
        :param protocol: Protocol to use when redirecting requests. The default is the protocol that is used in the original request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#protocol S3BucketWebsiteConfiguration#protocol}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdd96095cf81ef0c9c5fbccaaf3453a0537e82300418c902a164321042e919ed)
            check_type(argname="argument host_name", value=host_name, expected_type=type_hints["host_name"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host_name is not None:
            self._values["host_name"] = host_name
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def host_name(self) -> typing.Optional[builtins.str]:
        '''The host name to use in the redirect request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#host_name S3BucketWebsiteConfiguration#host_name}
        '''
        result = self._values.get("host_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Protocol to use when redirecting requests. The default is the protocol that is used in the original request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#protocol S3BucketWebsiteConfiguration#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationRedirectAllRequestsTo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketWebsiteConfigurationRedirectAllRequestsToOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRedirectAllRequestsToOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5131173d67fbdabbaae231ff9044bee7907c3fc758240659f5b98fb5b941e3d6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHostName")
    def reset_host_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostName", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @builtins.property
    @jsii.member(jsii_name="hostNameInput")
    def host_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostNameInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="hostName")
    def host_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostName"))

    @host_name.setter
    def host_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe5a2ed4d25e4fc021bd0bd0fe94fc12fd22f1cea20d82d1e736be62a4e85ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1be71922ce164aab8b87ff2898b130d8153d274669b46787a39896d87117ac04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRedirectAllRequestsTo]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRedirectAllRequestsTo]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRedirectAllRequestsTo]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ead6e48de470b8261c9e28e5b171b7006bf0d67ca6f2206af397b1105391f41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRule",
    jsii_struct_bases=[],
    name_mapping={"condition": "condition", "redirect": "redirect"},
)
class S3BucketWebsiteConfigurationRoutingRule:
    def __init__(
        self,
        *,
        condition: typing.Optional[typing.Union["S3BucketWebsiteConfigurationRoutingRuleCondition", typing.Dict[builtins.str, typing.Any]]] = None,
        redirect: typing.Optional[typing.Union["S3BucketWebsiteConfigurationRoutingRuleRedirect", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param condition: condition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#condition S3BucketWebsiteConfiguration#condition}
        :param redirect: redirect block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#redirect S3BucketWebsiteConfiguration#redirect}
        '''
        if isinstance(condition, dict):
            condition = S3BucketWebsiteConfigurationRoutingRuleCondition(**condition)
        if isinstance(redirect, dict):
            redirect = S3BucketWebsiteConfigurationRoutingRuleRedirect(**redirect)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb30977a5c2b1cd53ebb038ddbd11b73e0f7edd48de9171016c1d9585dddc977)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument redirect", value=redirect, expected_type=type_hints["redirect"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if redirect is not None:
            self._values["redirect"] = redirect

    @builtins.property
    def condition(
        self,
    ) -> typing.Optional["S3BucketWebsiteConfigurationRoutingRuleCondition"]:
        '''condition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#condition S3BucketWebsiteConfiguration#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional["S3BucketWebsiteConfigurationRoutingRuleCondition"], result)

    @builtins.property
    def redirect(
        self,
    ) -> typing.Optional["S3BucketWebsiteConfigurationRoutingRuleRedirect"]:
        '''redirect block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#redirect S3BucketWebsiteConfiguration#redirect}
        '''
        result = self._values.get("redirect")
        return typing.cast(typing.Optional["S3BucketWebsiteConfigurationRoutingRuleRedirect"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationRoutingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRuleCondition",
    jsii_struct_bases=[],
    name_mapping={
        "http_error_code_returned_equals": "httpErrorCodeReturnedEquals",
        "key_prefix_equals": "keyPrefixEquals",
    },
)
class S3BucketWebsiteConfigurationRoutingRuleCondition:
    def __init__(
        self,
        *,
        http_error_code_returned_equals: typing.Optional[builtins.str] = None,
        key_prefix_equals: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param http_error_code_returned_equals: The HTTP error code when the redirect is applied. In the event of an error, if the error code equals this value, then the specified redirect is applied. Required when parent element Condition is specified and sibling KeyPrefixEquals is not specified. If both are specified, then both must be true for the redirect to be applied Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#http_error_code_returned_equals S3BucketWebsiteConfiguration#http_error_code_returned_equals}
        :param key_prefix_equals: The object key name prefix when the redirect is applied. For example, to redirect requests for ``ExamplePage.html``, the key prefix will be ``ExamplePage.html``. To redirect request for all pages with the prefix ``docs/``, the key prefix will be ``/docs``, which identifies all objects in the ``docs/`` folder. Required when the parent element ``Condition`` is specified and sibling ``HTTPErrorCodeReturnedEquals`` is not specified. If both conditions are specified, both must be true for the redirect to be applied. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#key_prefix_equals S3BucketWebsiteConfiguration#key_prefix_equals}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcce8375d15101ec8f8e6b7621bec7336379bedd049cff439d6ac183f894f06f)
            check_type(argname="argument http_error_code_returned_equals", value=http_error_code_returned_equals, expected_type=type_hints["http_error_code_returned_equals"])
            check_type(argname="argument key_prefix_equals", value=key_prefix_equals, expected_type=type_hints["key_prefix_equals"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if http_error_code_returned_equals is not None:
            self._values["http_error_code_returned_equals"] = http_error_code_returned_equals
        if key_prefix_equals is not None:
            self._values["key_prefix_equals"] = key_prefix_equals

    @builtins.property
    def http_error_code_returned_equals(self) -> typing.Optional[builtins.str]:
        '''The HTTP error code when the redirect is applied.

        In the event of an error, if the error code equals this value, then the specified redirect is applied. Required when parent element Condition is specified and sibling KeyPrefixEquals is not specified. If both are specified, then both must be true for the redirect to be applied

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#http_error_code_returned_equals S3BucketWebsiteConfiguration#http_error_code_returned_equals}
        '''
        result = self._values.get("http_error_code_returned_equals")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_prefix_equals(self) -> typing.Optional[builtins.str]:
        '''The object key name prefix when the redirect is applied.

        For example, to redirect requests for ``ExamplePage.html``, the key prefix will be ``ExamplePage.html``. To redirect request for all pages with the prefix ``docs/``, the key prefix will be ``/docs``, which identifies all objects in the ``docs/`` folder. Required when the parent element ``Condition`` is specified and sibling ``HTTPErrorCodeReturnedEquals`` is not specified. If both conditions are specified, both must be true for the redirect to be applied. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#key_prefix_equals S3BucketWebsiteConfiguration#key_prefix_equals}
        '''
        result = self._values.get("key_prefix_equals")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationRoutingRuleCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketWebsiteConfigurationRoutingRuleConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRuleConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5c3e9a40c1cb6172e63dc386e3cea24f4ca58763c926f94db0d563692c24df6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHttpErrorCodeReturnedEquals")
    def reset_http_error_code_returned_equals(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpErrorCodeReturnedEquals", []))

    @jsii.member(jsii_name="resetKeyPrefixEquals")
    def reset_key_prefix_equals(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyPrefixEquals", []))

    @builtins.property
    @jsii.member(jsii_name="httpErrorCodeReturnedEqualsInput")
    def http_error_code_returned_equals_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpErrorCodeReturnedEqualsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyPrefixEqualsInput")
    def key_prefix_equals_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPrefixEqualsInput"))

    @builtins.property
    @jsii.member(jsii_name="httpErrorCodeReturnedEquals")
    def http_error_code_returned_equals(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpErrorCodeReturnedEquals"))

    @http_error_code_returned_equals.setter
    def http_error_code_returned_equals(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57503eb0f917f2c79b9ad3e2f19b73fc2a9d411714034b305de9dc6213ac3eda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpErrorCodeReturnedEquals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyPrefixEquals")
    def key_prefix_equals(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyPrefixEquals"))

    @key_prefix_equals.setter
    def key_prefix_equals(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96558f9e9b5adbd66fefff4f3a1f95479af0ae0319e68057282d9136e0bbdecb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyPrefixEquals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleCondition]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleCondition]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20ca018edfd3f2d94acfc7538249dd8005aaba4396edc160a0b5321363f06c00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class S3BucketWebsiteConfigurationRoutingRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRuleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0dcc4f5ba9b9111b19d0585f32339cc8505ab55ece0f19a60a02d69727a1398)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "S3BucketWebsiteConfigurationRoutingRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f52daffee6998d1a3acff4c02f3cdc186f34c253e58011be36bf6d372feff3e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("S3BucketWebsiteConfigurationRoutingRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c27e9f8350973fda577fc79de3f8f9bb1b6f7e457d86248de03224f5566ef49b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b33375a437f782dfe44af58d0d4b01831625d76ec09788b61af380a4e89e6f9e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a89cefc462cd2b461a25b336840711dac4269e439e8ad81ba1ad5a517795bc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[S3BucketWebsiteConfigurationRoutingRule]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[S3BucketWebsiteConfigurationRoutingRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[S3BucketWebsiteConfigurationRoutingRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffa06fcd8110774793df30df5075de14d765f398139543ea5abdca3c75b710d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class S3BucketWebsiteConfigurationRoutingRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__744443845e08dc610b437f57a42b4963c2a31be30ec95ac585acfca1bffc27df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        *,
        http_error_code_returned_equals: typing.Optional[builtins.str] = None,
        key_prefix_equals: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param http_error_code_returned_equals: The HTTP error code when the redirect is applied. In the event of an error, if the error code equals this value, then the specified redirect is applied. Required when parent element Condition is specified and sibling KeyPrefixEquals is not specified. If both are specified, then both must be true for the redirect to be applied Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#http_error_code_returned_equals S3BucketWebsiteConfiguration#http_error_code_returned_equals}
        :param key_prefix_equals: The object key name prefix when the redirect is applied. For example, to redirect requests for ``ExamplePage.html``, the key prefix will be ``ExamplePage.html``. To redirect request for all pages with the prefix ``docs/``, the key prefix will be ``/docs``, which identifies all objects in the ``docs/`` folder. Required when the parent element ``Condition`` is specified and sibling ``HTTPErrorCodeReturnedEquals`` is not specified. If both conditions are specified, both must be true for the redirect to be applied. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#key_prefix_equals S3BucketWebsiteConfiguration#key_prefix_equals}
        '''
        value = S3BucketWebsiteConfigurationRoutingRuleCondition(
            http_error_code_returned_equals=http_error_code_returned_equals,
            key_prefix_equals=key_prefix_equals,
        )

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @jsii.member(jsii_name="putRedirect")
    def put_redirect(
        self,
        *,
        host_name: typing.Optional[builtins.str] = None,
        http_redirect_code: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        replace_key_prefix_with: typing.Optional[builtins.str] = None,
        replace_key_with: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_name: The host name to use in the redirect request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#host_name S3BucketWebsiteConfiguration#host_name}
        :param http_redirect_code: The HTTP redirect code to use on the response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#http_redirect_code S3BucketWebsiteConfiguration#http_redirect_code}
        :param protocol: The protocol to use in the redirect request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#protocol S3BucketWebsiteConfiguration#protocol}
        :param replace_key_prefix_with: The object key prefix to use in the redirect request. For example, to redirect requests for all pages with prefix ``docs/`` (objects in the ``docs/`` folder) to ``documents/``, you can set a condition block with ``KeyPrefixEquals`` set to ``docs/`` and in the Redirect set ``ReplaceKeyPrefixWith`` to ``/documents``. Not required if one of the siblings is present. Can be present only if ``ReplaceKeyWith`` is not provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#replace_key_prefix_with S3BucketWebsiteConfiguration#replace_key_prefix_with}
        :param replace_key_with: The specific object key to use in the redirect request. For example, redirect request to error.html. Not required if one of the siblings is present. Can be present only if ReplaceKeyPrefixWith is not provided. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#replace_key_with S3BucketWebsiteConfiguration#replace_key_with}
        '''
        value = S3BucketWebsiteConfigurationRoutingRuleRedirect(
            host_name=host_name,
            http_redirect_code=http_redirect_code,
            protocol=protocol,
            replace_key_prefix_with=replace_key_prefix_with,
            replace_key_with=replace_key_with,
        )

        return typing.cast(None, jsii.invoke(self, "putRedirect", [value]))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @jsii.member(jsii_name="resetRedirect")
    def reset_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirect", []))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(
        self,
    ) -> S3BucketWebsiteConfigurationRoutingRuleConditionOutputReference:
        return typing.cast(S3BucketWebsiteConfigurationRoutingRuleConditionOutputReference, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(
        self,
    ) -> "S3BucketWebsiteConfigurationRoutingRuleRedirectOutputReference":
        return typing.cast("S3BucketWebsiteConfigurationRoutingRuleRedirectOutputReference", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleCondition]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleCondition]], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectInput")
    def redirect_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationRoutingRuleRedirect"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "S3BucketWebsiteConfigurationRoutingRuleRedirect"]], jsii.get(self, "redirectInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e582ed0b454b66e93482530de449327be5266daccf41f981a61ca36369aeba7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRuleRedirect",
    jsii_struct_bases=[],
    name_mapping={
        "host_name": "hostName",
        "http_redirect_code": "httpRedirectCode",
        "protocol": "protocol",
        "replace_key_prefix_with": "replaceKeyPrefixWith",
        "replace_key_with": "replaceKeyWith",
    },
)
class S3BucketWebsiteConfigurationRoutingRuleRedirect:
    def __init__(
        self,
        *,
        host_name: typing.Optional[builtins.str] = None,
        http_redirect_code: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        replace_key_prefix_with: typing.Optional[builtins.str] = None,
        replace_key_with: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_name: The host name to use in the redirect request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#host_name S3BucketWebsiteConfiguration#host_name}
        :param http_redirect_code: The HTTP redirect code to use on the response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#http_redirect_code S3BucketWebsiteConfiguration#http_redirect_code}
        :param protocol: The protocol to use in the redirect request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#protocol S3BucketWebsiteConfiguration#protocol}
        :param replace_key_prefix_with: The object key prefix to use in the redirect request. For example, to redirect requests for all pages with prefix ``docs/`` (objects in the ``docs/`` folder) to ``documents/``, you can set a condition block with ``KeyPrefixEquals`` set to ``docs/`` and in the Redirect set ``ReplaceKeyPrefixWith`` to ``/documents``. Not required if one of the siblings is present. Can be present only if ``ReplaceKeyWith`` is not provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#replace_key_prefix_with S3BucketWebsiteConfiguration#replace_key_prefix_with}
        :param replace_key_with: The specific object key to use in the redirect request. For example, redirect request to error.html. Not required if one of the siblings is present. Can be present only if ReplaceKeyPrefixWith is not provided. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#replace_key_with S3BucketWebsiteConfiguration#replace_key_with}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2bc1804ef87cc8a6560078cac13dbfaff7561b2873e8d008a5749f5e1e677ef)
            check_type(argname="argument host_name", value=host_name, expected_type=type_hints["host_name"])
            check_type(argname="argument http_redirect_code", value=http_redirect_code, expected_type=type_hints["http_redirect_code"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument replace_key_prefix_with", value=replace_key_prefix_with, expected_type=type_hints["replace_key_prefix_with"])
            check_type(argname="argument replace_key_with", value=replace_key_with, expected_type=type_hints["replace_key_with"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if host_name is not None:
            self._values["host_name"] = host_name
        if http_redirect_code is not None:
            self._values["http_redirect_code"] = http_redirect_code
        if protocol is not None:
            self._values["protocol"] = protocol
        if replace_key_prefix_with is not None:
            self._values["replace_key_prefix_with"] = replace_key_prefix_with
        if replace_key_with is not None:
            self._values["replace_key_with"] = replace_key_with

    @builtins.property
    def host_name(self) -> typing.Optional[builtins.str]:
        '''The host name to use in the redirect request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#host_name S3BucketWebsiteConfiguration#host_name}
        '''
        result = self._values.get("host_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_redirect_code(self) -> typing.Optional[builtins.str]:
        '''The HTTP redirect code to use on the response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#http_redirect_code S3BucketWebsiteConfiguration#http_redirect_code}
        '''
        result = self._values.get("http_redirect_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''The protocol to use in the redirect request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#protocol S3BucketWebsiteConfiguration#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replace_key_prefix_with(self) -> typing.Optional[builtins.str]:
        '''The object key prefix to use in the redirect request.

        For example, to redirect requests for all pages with prefix ``docs/`` (objects in the ``docs/`` folder) to ``documents/``, you can set a condition block with ``KeyPrefixEquals`` set to ``docs/`` and in the Redirect set ``ReplaceKeyPrefixWith`` to ``/documents``. Not required if one of the siblings is present. Can be present only if ``ReplaceKeyWith`` is not provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#replace_key_prefix_with S3BucketWebsiteConfiguration#replace_key_prefix_with}
        '''
        result = self._values.get("replace_key_prefix_with")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replace_key_with(self) -> typing.Optional[builtins.str]:
        '''The specific object key to use in the redirect request.

        For example, redirect request to error.html. Not required if one of the siblings is present. Can be present only if ReplaceKeyPrefixWith is not provided. Replacement must be made for object keys containing special characters (such as carriage returns) when using XML requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_bucket_website_configuration#replace_key_with S3BucketWebsiteConfiguration#replace_key_with}
        '''
        result = self._values.get("replace_key_with")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketWebsiteConfigurationRoutingRuleRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3BucketWebsiteConfigurationRoutingRuleRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3BucketWebsiteConfiguration.S3BucketWebsiteConfigurationRoutingRuleRedirectOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f238057c3b9160649a535d9e333896e023a5ba1ccc816c73999d1aa63fb334bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHostName")
    def reset_host_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostName", []))

    @jsii.member(jsii_name="resetHttpRedirectCode")
    def reset_http_redirect_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpRedirectCode", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @jsii.member(jsii_name="resetReplaceKeyPrefixWith")
    def reset_replace_key_prefix_with(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplaceKeyPrefixWith", []))

    @jsii.member(jsii_name="resetReplaceKeyWith")
    def reset_replace_key_with(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplaceKeyWith", []))

    @builtins.property
    @jsii.member(jsii_name="hostNameInput")
    def host_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostNameInput"))

    @builtins.property
    @jsii.member(jsii_name="httpRedirectCodeInput")
    def http_redirect_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpRedirectCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="replaceKeyPrefixWithInput")
    def replace_key_prefix_with_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replaceKeyPrefixWithInput"))

    @builtins.property
    @jsii.member(jsii_name="replaceKeyWithInput")
    def replace_key_with_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replaceKeyWithInput"))

    @builtins.property
    @jsii.member(jsii_name="hostName")
    def host_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostName"))

    @host_name.setter
    def host_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a71c6f1c4f74f3079f4439deb2ea5f49d335d0dafe3809a0d98b2de64b7f0a7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpRedirectCode")
    def http_redirect_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpRedirectCode"))

    @http_redirect_code.setter
    def http_redirect_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9c5520a42decb27c1c3421e7eca4ca88993156ab9f08ad5f6a5935757f41acf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpRedirectCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a097ba9f9f1c12d1a88732b213cd8521dcf3cacb1416fa0f230f202f91cb08d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replaceKeyPrefixWith")
    def replace_key_prefix_with(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replaceKeyPrefixWith"))

    @replace_key_prefix_with.setter
    def replace_key_prefix_with(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf421237b3ff8fe068a004a4401d6f7df2e8b67cb64955e8ed89b3501b150c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replaceKeyPrefixWith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replaceKeyWith")
    def replace_key_with(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replaceKeyWith"))

    @replace_key_with.setter
    def replace_key_with(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13f75c917500ac2bb363d75c4c9674ce076e116790a5728cb1de8737f3b63b36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replaceKeyWith", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleRedirect]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleRedirect]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleRedirect]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9fb1be567cdbbd25c625a0297aa5ec61cd9a97ef79efa0b6ca7cd06c89a3f2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "S3BucketWebsiteConfiguration",
    "S3BucketWebsiteConfigurationConfig",
    "S3BucketWebsiteConfigurationErrorDocument",
    "S3BucketWebsiteConfigurationErrorDocumentOutputReference",
    "S3BucketWebsiteConfigurationIndexDocument",
    "S3BucketWebsiteConfigurationIndexDocumentOutputReference",
    "S3BucketWebsiteConfigurationRedirectAllRequestsTo",
    "S3BucketWebsiteConfigurationRedirectAllRequestsToOutputReference",
    "S3BucketWebsiteConfigurationRoutingRule",
    "S3BucketWebsiteConfigurationRoutingRuleCondition",
    "S3BucketWebsiteConfigurationRoutingRuleConditionOutputReference",
    "S3BucketWebsiteConfigurationRoutingRuleList",
    "S3BucketWebsiteConfigurationRoutingRuleOutputReference",
    "S3BucketWebsiteConfigurationRoutingRuleRedirect",
    "S3BucketWebsiteConfigurationRoutingRuleRedirectOutputReference",
]

publication.publish()

def _typecheckingstub__a408792e6be0150a4f7956d125634baa2456997c298363ffb14250f637a2675d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: builtins.str,
    error_document: typing.Optional[typing.Union[S3BucketWebsiteConfigurationErrorDocument, typing.Dict[builtins.str, typing.Any]]] = None,
    index_document: typing.Optional[typing.Union[S3BucketWebsiteConfigurationIndexDocument, typing.Dict[builtins.str, typing.Any]]] = None,
    redirect_all_requests_to: typing.Optional[typing.Union[S3BucketWebsiteConfigurationRedirectAllRequestsTo, typing.Dict[builtins.str, typing.Any]]] = None,
    routing_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[S3BucketWebsiteConfigurationRoutingRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__43f8ca40a15ee1d8a0fe5e6f1b0efe905b25921db7c9101284f7c826d42da721(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11163039321cef117b54a55e720203e4367c5e2b2a01506e2eef3c8341e37739(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[S3BucketWebsiteConfigurationRoutingRule, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__147276d9198fa27dbc5b910546dc373e8d2e2f5c295b6cd64ab70b81dd619639(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee36cb17757ef2db94022e05e6ab18ccb25961ac20931607aee2c9828aed2bf(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bucket: builtins.str,
    error_document: typing.Optional[typing.Union[S3BucketWebsiteConfigurationErrorDocument, typing.Dict[builtins.str, typing.Any]]] = None,
    index_document: typing.Optional[typing.Union[S3BucketWebsiteConfigurationIndexDocument, typing.Dict[builtins.str, typing.Any]]] = None,
    redirect_all_requests_to: typing.Optional[typing.Union[S3BucketWebsiteConfigurationRedirectAllRequestsTo, typing.Dict[builtins.str, typing.Any]]] = None,
    routing_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[S3BucketWebsiteConfigurationRoutingRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__268c37ec094c1b068e493b53329e632d54e57b31a061f61eb413c37772232800(
    *,
    key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a644559fd10fa98949e7f19d90c015bbd8bb6b3b4807baa7738c69b4ee9b17(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed8ee253a5e550f150318250489610dc841a0b1b709742ba2e5cc6205ce9890b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ef5f72f7c268731da86385a18a4710935052242685363cc9557509bee27efea(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationErrorDocument]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8bdbc0eae9f00b81c8bb1577d95afdd38bcd00ee4498bea9d2bdbbedc141606(
    *,
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a71b0a4a62e585c11fa3d7140410b66a4798bd4bbcc047e54c9040bfa33430cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e41ae797e2c9fc0561c7793779effa68ef2ec67bff3b10387a5fdcd8c21f5e45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ec2fd423f01fd13ae13e91a0cf89b9ecc313a52833c2870c5d5d63c041179b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationIndexDocument]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdd96095cf81ef0c9c5fbccaaf3453a0537e82300418c902a164321042e919ed(
    *,
    host_name: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5131173d67fbdabbaae231ff9044bee7907c3fc758240659f5b98fb5b941e3d6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe5a2ed4d25e4fc021bd0bd0fe94fc12fd22f1cea20d82d1e736be62a4e85ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1be71922ce164aab8b87ff2898b130d8153d274669b46787a39896d87117ac04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ead6e48de470b8261c9e28e5b171b7006bf0d67ca6f2206af397b1105391f41(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRedirectAllRequestsTo]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb30977a5c2b1cd53ebb038ddbd11b73e0f7edd48de9171016c1d9585dddc977(
    *,
    condition: typing.Optional[typing.Union[S3BucketWebsiteConfigurationRoutingRuleCondition, typing.Dict[builtins.str, typing.Any]]] = None,
    redirect: typing.Optional[typing.Union[S3BucketWebsiteConfigurationRoutingRuleRedirect, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcce8375d15101ec8f8e6b7621bec7336379bedd049cff439d6ac183f894f06f(
    *,
    http_error_code_returned_equals: typing.Optional[builtins.str] = None,
    key_prefix_equals: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c3e9a40c1cb6172e63dc386e3cea24f4ca58763c926f94db0d563692c24df6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57503eb0f917f2c79b9ad3e2f19b73fc2a9d411714034b305de9dc6213ac3eda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96558f9e9b5adbd66fefff4f3a1f95479af0ae0319e68057282d9136e0bbdecb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ca018edfd3f2d94acfc7538249dd8005aaba4396edc160a0b5321363f06c00(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleCondition]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0dcc4f5ba9b9111b19d0585f32339cc8505ab55ece0f19a60a02d69727a1398(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f52daffee6998d1a3acff4c02f3cdc186f34c253e58011be36bf6d372feff3e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c27e9f8350973fda577fc79de3f8f9bb1b6f7e457d86248de03224f5566ef49b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b33375a437f782dfe44af58d0d4b01831625d76ec09788b61af380a4e89e6f9e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a89cefc462cd2b461a25b336840711dac4269e439e8ad81ba1ad5a517795bc8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa06fcd8110774793df30df5075de14d765f398139543ea5abdca3c75b710d9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[S3BucketWebsiteConfigurationRoutingRule]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__744443845e08dc610b437f57a42b4963c2a31be30ec95ac585acfca1bffc27df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e582ed0b454b66e93482530de449327be5266daccf41f981a61ca36369aeba7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2bc1804ef87cc8a6560078cac13dbfaff7561b2873e8d008a5749f5e1e677ef(
    *,
    host_name: typing.Optional[builtins.str] = None,
    http_redirect_code: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
    replace_key_prefix_with: typing.Optional[builtins.str] = None,
    replace_key_with: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f238057c3b9160649a535d9e333896e023a5ba1ccc816c73999d1aa63fb334bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a71c6f1c4f74f3079f4439deb2ea5f49d335d0dafe3809a0d98b2de64b7f0a7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9c5520a42decb27c1c3421e7eca4ca88993156ab9f08ad5f6a5935757f41acf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a097ba9f9f1c12d1a88732b213cd8521dcf3cacb1416fa0f230f202f91cb08d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf421237b3ff8fe068a004a4401d6f7df2e8b67cb64955e8ed89b3501b150c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13f75c917500ac2bb363d75c4c9674ce076e116790a5728cb1de8737f3b63b36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9fb1be567cdbbd25c625a0297aa5ec61cd9a97ef79efa0b6ca7cd06c89a3f2e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, S3BucketWebsiteConfigurationRoutingRuleRedirect]],
) -> None:
    """Type checking stubs"""
    pass
