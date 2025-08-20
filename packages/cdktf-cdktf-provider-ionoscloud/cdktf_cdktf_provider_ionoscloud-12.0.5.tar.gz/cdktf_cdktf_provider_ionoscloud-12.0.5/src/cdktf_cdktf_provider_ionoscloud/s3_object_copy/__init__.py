r'''
# `ionoscloud_s3_object_copy`

Refer to the Terraform Registry for docs: [`ionoscloud_s3_object_copy`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy).
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


class S3ObjectCopy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.s3ObjectCopy.S3ObjectCopy",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy ionoscloud_s3_object_copy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket: builtins.str,
        key: builtins.str,
        source: builtins.str,
        cache_control: typing.Optional[builtins.str] = None,
        content_disposition: typing.Optional[builtins.str] = None,
        content_encoding: typing.Optional[builtins.str] = None,
        content_language: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        copy_if_match: typing.Optional[builtins.str] = None,
        copy_if_modified_since: typing.Optional[builtins.str] = None,
        copy_if_none_match: typing.Optional[builtins.str] = None,
        copy_if_unmodified_since: typing.Optional[builtins.str] = None,
        expires: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        metadata_directive: typing.Optional[builtins.str] = None,
        object_lock_legal_hold: typing.Optional[builtins.str] = None,
        object_lock_mode: typing.Optional[builtins.str] = None,
        object_lock_retain_until_date: typing.Optional[builtins.str] = None,
        server_side_encryption: typing.Optional[builtins.str] = None,
        server_side_encryption_customer_algorithm: typing.Optional[builtins.str] = None,
        server_side_encryption_customer_key: typing.Optional[builtins.str] = None,
        server_side_encryption_customer_key_md5: typing.Optional[builtins.str] = None,
        source_customer_algorithm: typing.Optional[builtins.str] = None,
        source_customer_key: typing.Optional[builtins.str] = None,
        source_customer_key_md5: typing.Optional[builtins.str] = None,
        storage_class: typing.Optional[builtins.str] = None,
        tagging_directive: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        website_redirect: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy ionoscloud_s3_object_copy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bucket: The name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#bucket S3ObjectCopy#bucket}
        :param key: The key of the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#key S3ObjectCopy#key}
        :param source: The key of the source object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source S3ObjectCopy#source}
        :param cache_control: Can be used to specify caching behavior along the request/reply chain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#cache_control S3ObjectCopy#cache_control}
        :param content_disposition: Specifies presentational information for the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_disposition S3ObjectCopy#content_disposition}
        :param content_encoding: Specifies what content encodings have been applied to the object copy and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_encoding S3ObjectCopy#content_encoding}
        :param content_language: The natural language or languages of the intended audience for the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_language S3ObjectCopy#content_language}
        :param content_type: A standard MIME type describing the format of the contents. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_type S3ObjectCopy#content_type}
        :param copy_if_match: Copies the object if its entity tag (ETag) matches the specified tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_match S3ObjectCopy#copy_if_match}
        :param copy_if_modified_since: Copies the object if it has been modified since the specified time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_modified_since S3ObjectCopy#copy_if_modified_since}
        :param copy_if_none_match: Copies the object if its entity tag (ETag) is different than the specified ETag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_none_match S3ObjectCopy#copy_if_none_match}
        :param copy_if_unmodified_since: Copies the object if it hasn't been modified since the specified time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_unmodified_since S3ObjectCopy#copy_if_unmodified_since}
        :param expires: The date and time at which the object copy is no longer cacheable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#expires S3ObjectCopy#expires}
        :param force_destroy: Specifies whether to delete the object copy even if it has a governance-type Object Copy Lock in place. You must explicitly pass a value of true for this parameter to delete the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#force_destroy S3ObjectCopy#force_destroy}
        :param metadata: A map of metadata to store with the object copy in IONOS Object Storage Object Copy Storage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#metadata S3ObjectCopy#metadata}
        :param metadata_directive: Specifies whether the metadata is copied from the source object or replaced with metadata provided in the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#metadata_directive S3ObjectCopy#metadata_directive}
        :param object_lock_legal_hold: Specifies whether a legal hold will be applied to this object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_legal_hold S3ObjectCopy#object_lock_legal_hold}
        :param object_lock_mode: Confirms that the requester knows that they will be charged for the request. Bucket owners need not specify this parameter in their requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_mode S3ObjectCopy#object_lock_mode}
        :param object_lock_retain_until_date: The date and time when you want this object copy's Object Copy Lock to expire. Must be formatted as a timestamp parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_retain_until_date S3ObjectCopy#object_lock_retain_until_date}
        :param server_side_encryption: The server-side encryption algorithm used when storing this object copy in IONOS Object Storage Object Copy Storage (AES256). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption S3ObjectCopy#server_side_encryption}
        :param server_side_encryption_customer_algorithm: Specifies the algorithm to use to when encrypting the object copy (e.g., AES256). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_algorithm S3ObjectCopy#server_side_encryption_customer_algorithm}
        :param server_side_encryption_customer_key: Specifies the 256-bit, base64-encoded encryption key to use to encrypt and decrypt your data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_key S3ObjectCopy#server_side_encryption_customer_key}
        :param server_side_encryption_customer_key_md5: Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321. IONOS Object Storage Object Copy Storage uses this header for a message integrity check to ensure that the encryption key was transmitted without error Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_key_md5 S3ObjectCopy#server_side_encryption_customer_key_md5}
        :param source_customer_algorithm: Specifies the algorithm to use to when decrypting the source object (e.g., AES256). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_algorithm S3ObjectCopy#source_customer_algorithm}
        :param source_customer_key: Specifies the 256-bit, base64-encoded encryption key to use to decrypt the source object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_key S3ObjectCopy#source_customer_key}
        :param source_customer_key_md5: Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321. IONOS Object Storage Object Copy Storage uses this header for a message integrity check to ensure that the encryption key was transmitted without error Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_key_md5 S3ObjectCopy#source_customer_key_md5}
        :param storage_class: The storage class of the object copy. Valid value is 'STANDARD'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#storage_class S3ObjectCopy#storage_class}
        :param tagging_directive: Specifies whether the object copy tag-set is copied from the source object or replaced with tag-set provided in the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#tagging_directive S3ObjectCopy#tagging_directive}
        :param tags: The tag-set for the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#tags S3ObjectCopy#tags}
        :param website_redirect: If the bucket is configured as a website, redirects requests for this object copy to another object copy in the same bucket or to an external URL. IONOS Object Storage Object Copy Storage stores the value of this header in the object copy metadata Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#website_redirect S3ObjectCopy#website_redirect}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__496ab3efab151c061e3b5abf4064d4ad919526fa9ba61d633db55855693463ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = S3ObjectCopyConfig(
            bucket=bucket,
            key=key,
            source=source,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
            copy_if_match=copy_if_match,
            copy_if_modified_since=copy_if_modified_since,
            copy_if_none_match=copy_if_none_match,
            copy_if_unmodified_since=copy_if_unmodified_since,
            expires=expires,
            force_destroy=force_destroy,
            metadata=metadata,
            metadata_directive=metadata_directive,
            object_lock_legal_hold=object_lock_legal_hold,
            object_lock_mode=object_lock_mode,
            object_lock_retain_until_date=object_lock_retain_until_date,
            server_side_encryption=server_side_encryption,
            server_side_encryption_customer_algorithm=server_side_encryption_customer_algorithm,
            server_side_encryption_customer_key=server_side_encryption_customer_key,
            server_side_encryption_customer_key_md5=server_side_encryption_customer_key_md5,
            source_customer_algorithm=source_customer_algorithm,
            source_customer_key=source_customer_key,
            source_customer_key_md5=source_customer_key_md5,
            storage_class=storage_class,
            tagging_directive=tagging_directive,
            tags=tags,
            website_redirect=website_redirect,
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
        '''Generates CDKTF code for importing a S3ObjectCopy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the S3ObjectCopy to import.
        :param import_from_id: The id of the existing S3ObjectCopy that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the S3ObjectCopy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__402a7a162fc6f1a6b6e39a33b7acc7db016f16460cd91380b4494503b09f160c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCacheControl")
    def reset_cache_control(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheControl", []))

    @jsii.member(jsii_name="resetContentDisposition")
    def reset_content_disposition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentDisposition", []))

    @jsii.member(jsii_name="resetContentEncoding")
    def reset_content_encoding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentEncoding", []))

    @jsii.member(jsii_name="resetContentLanguage")
    def reset_content_language(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentLanguage", []))

    @jsii.member(jsii_name="resetContentType")
    def reset_content_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentType", []))

    @jsii.member(jsii_name="resetCopyIfMatch")
    def reset_copy_if_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfMatch", []))

    @jsii.member(jsii_name="resetCopyIfModifiedSince")
    def reset_copy_if_modified_since(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfModifiedSince", []))

    @jsii.member(jsii_name="resetCopyIfNoneMatch")
    def reset_copy_if_none_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfNoneMatch", []))

    @jsii.member(jsii_name="resetCopyIfUnmodifiedSince")
    def reset_copy_if_unmodified_since(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyIfUnmodifiedSince", []))

    @jsii.member(jsii_name="resetExpires")
    def reset_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpires", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetMetadataDirective")
    def reset_metadata_directive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadataDirective", []))

    @jsii.member(jsii_name="resetObjectLockLegalHold")
    def reset_object_lock_legal_hold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockLegalHold", []))

    @jsii.member(jsii_name="resetObjectLockMode")
    def reset_object_lock_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockMode", []))

    @jsii.member(jsii_name="resetObjectLockRetainUntilDate")
    def reset_object_lock_retain_until_date(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetObjectLockRetainUntilDate", []))

    @jsii.member(jsii_name="resetServerSideEncryption")
    def reset_server_side_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryption", []))

    @jsii.member(jsii_name="resetServerSideEncryptionCustomerAlgorithm")
    def reset_server_side_encryption_customer_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryptionCustomerAlgorithm", []))

    @jsii.member(jsii_name="resetServerSideEncryptionCustomerKey")
    def reset_server_side_encryption_customer_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryptionCustomerKey", []))

    @jsii.member(jsii_name="resetServerSideEncryptionCustomerKeyMd5")
    def reset_server_side_encryption_customer_key_md5(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerSideEncryptionCustomerKeyMd5", []))

    @jsii.member(jsii_name="resetSourceCustomerAlgorithm")
    def reset_source_customer_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCustomerAlgorithm", []))

    @jsii.member(jsii_name="resetSourceCustomerKey")
    def reset_source_customer_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCustomerKey", []))

    @jsii.member(jsii_name="resetSourceCustomerKeyMd5")
    def reset_source_customer_key_md5(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceCustomerKeyMd5", []))

    @jsii.member(jsii_name="resetStorageClass")
    def reset_storage_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageClass", []))

    @jsii.member(jsii_name="resetTaggingDirective")
    def reset_tagging_directive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTaggingDirective", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetWebsiteRedirect")
    def reset_website_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebsiteRedirect", []))

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
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property
    @jsii.member(jsii_name="lastModified")
    def last_modified(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModified"))

    @builtins.property
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionId"))

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="cacheControlInput")
    def cache_control_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cacheControlInput"))

    @builtins.property
    @jsii.member(jsii_name="contentDispositionInput")
    def content_disposition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentDispositionInput"))

    @builtins.property
    @jsii.member(jsii_name="contentEncodingInput")
    def content_encoding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentEncodingInput"))

    @builtins.property
    @jsii.member(jsii_name="contentLanguageInput")
    def content_language_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentLanguageInput"))

    @builtins.property
    @jsii.member(jsii_name="contentTypeInput")
    def content_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="copyIfMatchInput")
    def copy_if_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfMatchInput"))

    @builtins.property
    @jsii.member(jsii_name="copyIfModifiedSinceInput")
    def copy_if_modified_since_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfModifiedSinceInput"))

    @builtins.property
    @jsii.member(jsii_name="copyIfNoneMatchInput")
    def copy_if_none_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfNoneMatchInput"))

    @builtins.property
    @jsii.member(jsii_name="copyIfUnmodifiedSinceInput")
    def copy_if_unmodified_since_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "copyIfUnmodifiedSinceInput"))

    @builtins.property
    @jsii.member(jsii_name="expiresInput")
    def expires_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expiresInput"))

    @builtins.property
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataDirectiveInput")
    def metadata_directive_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadataDirectiveInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="objectLockLegalHoldInput")
    def object_lock_legal_hold_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockLegalHoldInput"))

    @builtins.property
    @jsii.member(jsii_name="objectLockModeInput")
    def object_lock_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockModeInput"))

    @builtins.property
    @jsii.member(jsii_name="objectLockRetainUntilDateInput")
    def object_lock_retain_until_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "objectLockRetainUntilDateInput"))

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionCustomerAlgorithmInput")
    def server_side_encryption_customer_algorithm_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionCustomerAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionCustomerKeyInput")
    def server_side_encryption_customer_key_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionCustomerKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionCustomerKeyMd5Input")
    def server_side_encryption_customer_key_md5_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionCustomerKeyMd5Input"))

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionInput")
    def server_side_encryption_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverSideEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCustomerAlgorithmInput")
    def source_customer_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCustomerAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCustomerKeyInput")
    def source_customer_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCustomerKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceCustomerKeyMd5Input")
    def source_customer_key_md5_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceCustomerKeyMd5Input"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="storageClassInput")
    def storage_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storageClassInput"))

    @builtins.property
    @jsii.member(jsii_name="taggingDirectiveInput")
    def tagging_directive_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taggingDirectiveInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="websiteRedirectInput")
    def website_redirect_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "websiteRedirectInput"))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a44dda204c025610dfba3b2afeb0df04550b134ca6d01cce9b224f3b0bc83d47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cacheControl")
    def cache_control(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cacheControl"))

    @cache_control.setter
    def cache_control(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91398fb332c00c03c00c7077800a5d5f7e87f26e1663637ccd305d89afcf9f5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cacheControl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentDisposition")
    def content_disposition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentDisposition"))

    @content_disposition.setter
    def content_disposition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d250d0f65dc35b7b54f4f988f84f7bb25012e89da8501cc6a492c1de4fbbb95d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentDisposition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentEncoding")
    def content_encoding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentEncoding"))

    @content_encoding.setter
    def content_encoding(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4066d66bce78e39483952d074ba992c183dc0217cf2d8d9878de3d3ed3cb2ca0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentEncoding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentLanguage")
    def content_language(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentLanguage"))

    @content_language.setter
    def content_language(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a35cae93e67dc7617af7fe15bb72d53d11d115324642fbd409cc293e5347f76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentLanguage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="contentType")
    def content_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentType"))

    @content_type.setter
    def content_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67210c097b3e6d0f780376cccca484a8e00d2cb43339861f1bb7f33f606d5b17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "contentType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="copyIfMatch")
    def copy_if_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfMatch"))

    @copy_if_match.setter
    def copy_if_match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0240e238bae4f7d20f1a1dc05ee5d0bd70d81870f291c1730f8d914643171dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copyIfMatch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="copyIfModifiedSince")
    def copy_if_modified_since(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfModifiedSince"))

    @copy_if_modified_since.setter
    def copy_if_modified_since(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fc923bece2021655c74c8d81eb9603b6dd640dd13903157f025541dc84b0dfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copyIfModifiedSince", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="copyIfNoneMatch")
    def copy_if_none_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfNoneMatch"))

    @copy_if_none_match.setter
    def copy_if_none_match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c926ce44b815e55e35f41fe7f99001070b0ba55d575ce0c1d6cdb9d87e89709b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copyIfNoneMatch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="copyIfUnmodifiedSince")
    def copy_if_unmodified_since(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "copyIfUnmodifiedSince"))

    @copy_if_unmodified_since.setter
    def copy_if_unmodified_since(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd997f3e0385ec502c19c0cdcbc6baba2b7923ef9423963f10d559efc8e09d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copyIfUnmodifiedSince", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expires")
    def expires(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expires"))

    @expires.setter
    def expires(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c0c254f2049b1dbccba6a5f56470ce443bb2ec3a39ba9f2c36707e3e034ec3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expires", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c68a51975809a7e6322aa10363b5049d96edaabe65a4af5ff26a5f21534249be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc727669a575dd60524ae4ac2223ca17e333393ba50bac3404c70dfb9b08aabd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a9f7a8a0cd4a5bfe4e0309f25b8a4738e6db5442732502756e6fb6abd174916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadataDirective")
    def metadata_directive(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metadataDirective"))

    @metadata_directive.setter
    def metadata_directive(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c07293dcf00a795e0a14dbd880bf18ebb1219b510f86ee7930bf772dd52bb140)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadataDirective", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="objectLockLegalHold")
    def object_lock_legal_hold(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockLegalHold"))

    @object_lock_legal_hold.setter
    def object_lock_legal_hold(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9542023b6de066ed4512383ef2b611a8dc28ce4020f82df5ceeaf9d5998a4259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "objectLockLegalHold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="objectLockMode")
    def object_lock_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockMode"))

    @object_lock_mode.setter
    def object_lock_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0cd751ef7f8663577a4b3865c01f98bc17179f82eca92994dfa75358dca441a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "objectLockMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="objectLockRetainUntilDate")
    def object_lock_retain_until_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectLockRetainUntilDate"))

    @object_lock_retain_until_date.setter
    def object_lock_retain_until_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__245589f0bc48cc2679c6faf5dc1a26c00d029be66211a6e8f38b3f462aeaf37c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "objectLockRetainUntilDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryption")
    def server_side_encryption(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryption"))

    @server_side_encryption.setter
    def server_side_encryption(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faeb5023e6e7ab17270c7a65681baaf1c51c48f6f613083cce05d583a674bed3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverSideEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionCustomerAlgorithm")
    def server_side_encryption_customer_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryptionCustomerAlgorithm"))

    @server_side_encryption_customer_algorithm.setter
    def server_side_encryption_customer_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ea565849d5dcbc4fc4c1b46227d8005f043ff86e5d073a3f88e6c2d517bb4f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverSideEncryptionCustomerAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionCustomerKey")
    def server_side_encryption_customer_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryptionCustomerKey"))

    @server_side_encryption_customer_key.setter
    def server_side_encryption_customer_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e73a2218645df26dea458c8cdcf5e4309f1168782346542f977122d9293fdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverSideEncryptionCustomerKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverSideEncryptionCustomerKeyMd5")
    def server_side_encryption_customer_key_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverSideEncryptionCustomerKeyMd5"))

    @server_side_encryption_customer_key_md5.setter
    def server_side_encryption_customer_key_md5(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc717b96914c89840e200230c904d1720150c1d1820fd0dcf2a72746401fa0bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverSideEncryptionCustomerKeyMd5", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfb3f1cbfeb7da49d79dad07771a3266327423a48b0575ce07451576341b67e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCustomerAlgorithm")
    def source_customer_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCustomerAlgorithm"))

    @source_customer_algorithm.setter
    def source_customer_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06bf56285f8f41213ceb5ee69a95ab744184c231889e3de6a4db766fe57f4468)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCustomerAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCustomerKey")
    def source_customer_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCustomerKey"))

    @source_customer_key.setter
    def source_customer_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7917106b0d87dd29b4fbfb6ff257aaa7856e0ec3ab5dcab070496c2a456fd4a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCustomerKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceCustomerKeyMd5")
    def source_customer_key_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceCustomerKeyMd5"))

    @source_customer_key_md5.setter
    def source_customer_key_md5(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de0a06391b0aef94ef04a6a947d800bc16d04a57143fc8c21548397a1d088c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceCustomerKeyMd5", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storageClass")
    def storage_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storageClass"))

    @storage_class.setter
    def storage_class(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__631833ee75fcecb95ea8b5feae4ca96efcfc3014087034e63eef0eea4435908a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storageClass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="taggingDirective")
    def tagging_directive(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "taggingDirective"))

    @tagging_directive.setter
    def tagging_directive(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d2aa6036f659f12b20f4ef375713e857558e44fd23077743df940c708398ade)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "taggingDirective", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d161a526cb877f62c76f33e4f19502613a6d938120a11d85eb82a8f0a70ae0df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="websiteRedirect")
    def website_redirect(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "websiteRedirect"))

    @website_redirect.setter
    def website_redirect(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9994555e64ac9ccfe9ac639a7bfc9f0981f19b7f3670b72f86902295d4b6baa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "websiteRedirect", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.s3ObjectCopy.S3ObjectCopyConfig",
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
        "key": "key",
        "source": "source",
        "cache_control": "cacheControl",
        "content_disposition": "contentDisposition",
        "content_encoding": "contentEncoding",
        "content_language": "contentLanguage",
        "content_type": "contentType",
        "copy_if_match": "copyIfMatch",
        "copy_if_modified_since": "copyIfModifiedSince",
        "copy_if_none_match": "copyIfNoneMatch",
        "copy_if_unmodified_since": "copyIfUnmodifiedSince",
        "expires": "expires",
        "force_destroy": "forceDestroy",
        "metadata": "metadata",
        "metadata_directive": "metadataDirective",
        "object_lock_legal_hold": "objectLockLegalHold",
        "object_lock_mode": "objectLockMode",
        "object_lock_retain_until_date": "objectLockRetainUntilDate",
        "server_side_encryption": "serverSideEncryption",
        "server_side_encryption_customer_algorithm": "serverSideEncryptionCustomerAlgorithm",
        "server_side_encryption_customer_key": "serverSideEncryptionCustomerKey",
        "server_side_encryption_customer_key_md5": "serverSideEncryptionCustomerKeyMd5",
        "source_customer_algorithm": "sourceCustomerAlgorithm",
        "source_customer_key": "sourceCustomerKey",
        "source_customer_key_md5": "sourceCustomerKeyMd5",
        "storage_class": "storageClass",
        "tagging_directive": "taggingDirective",
        "tags": "tags",
        "website_redirect": "websiteRedirect",
    },
)
class S3ObjectCopyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        key: builtins.str,
        source: builtins.str,
        cache_control: typing.Optional[builtins.str] = None,
        content_disposition: typing.Optional[builtins.str] = None,
        content_encoding: typing.Optional[builtins.str] = None,
        content_language: typing.Optional[builtins.str] = None,
        content_type: typing.Optional[builtins.str] = None,
        copy_if_match: typing.Optional[builtins.str] = None,
        copy_if_modified_since: typing.Optional[builtins.str] = None,
        copy_if_none_match: typing.Optional[builtins.str] = None,
        copy_if_unmodified_since: typing.Optional[builtins.str] = None,
        expires: typing.Optional[builtins.str] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        metadata_directive: typing.Optional[builtins.str] = None,
        object_lock_legal_hold: typing.Optional[builtins.str] = None,
        object_lock_mode: typing.Optional[builtins.str] = None,
        object_lock_retain_until_date: typing.Optional[builtins.str] = None,
        server_side_encryption: typing.Optional[builtins.str] = None,
        server_side_encryption_customer_algorithm: typing.Optional[builtins.str] = None,
        server_side_encryption_customer_key: typing.Optional[builtins.str] = None,
        server_side_encryption_customer_key_md5: typing.Optional[builtins.str] = None,
        source_customer_algorithm: typing.Optional[builtins.str] = None,
        source_customer_key: typing.Optional[builtins.str] = None,
        source_customer_key_md5: typing.Optional[builtins.str] = None,
        storage_class: typing.Optional[builtins.str] = None,
        tagging_directive: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        website_redirect: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param bucket: The name of the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#bucket S3ObjectCopy#bucket}
        :param key: The key of the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#key S3ObjectCopy#key}
        :param source: The key of the source object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source S3ObjectCopy#source}
        :param cache_control: Can be used to specify caching behavior along the request/reply chain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#cache_control S3ObjectCopy#cache_control}
        :param content_disposition: Specifies presentational information for the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_disposition S3ObjectCopy#content_disposition}
        :param content_encoding: Specifies what content encodings have been applied to the object copy and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_encoding S3ObjectCopy#content_encoding}
        :param content_language: The natural language or languages of the intended audience for the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_language S3ObjectCopy#content_language}
        :param content_type: A standard MIME type describing the format of the contents. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_type S3ObjectCopy#content_type}
        :param copy_if_match: Copies the object if its entity tag (ETag) matches the specified tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_match S3ObjectCopy#copy_if_match}
        :param copy_if_modified_since: Copies the object if it has been modified since the specified time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_modified_since S3ObjectCopy#copy_if_modified_since}
        :param copy_if_none_match: Copies the object if its entity tag (ETag) is different than the specified ETag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_none_match S3ObjectCopy#copy_if_none_match}
        :param copy_if_unmodified_since: Copies the object if it hasn't been modified since the specified time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_unmodified_since S3ObjectCopy#copy_if_unmodified_since}
        :param expires: The date and time at which the object copy is no longer cacheable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#expires S3ObjectCopy#expires}
        :param force_destroy: Specifies whether to delete the object copy even if it has a governance-type Object Copy Lock in place. You must explicitly pass a value of true for this parameter to delete the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#force_destroy S3ObjectCopy#force_destroy}
        :param metadata: A map of metadata to store with the object copy in IONOS Object Storage Object Copy Storage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#metadata S3ObjectCopy#metadata}
        :param metadata_directive: Specifies whether the metadata is copied from the source object or replaced with metadata provided in the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#metadata_directive S3ObjectCopy#metadata_directive}
        :param object_lock_legal_hold: Specifies whether a legal hold will be applied to this object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_legal_hold S3ObjectCopy#object_lock_legal_hold}
        :param object_lock_mode: Confirms that the requester knows that they will be charged for the request. Bucket owners need not specify this parameter in their requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_mode S3ObjectCopy#object_lock_mode}
        :param object_lock_retain_until_date: The date and time when you want this object copy's Object Copy Lock to expire. Must be formatted as a timestamp parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_retain_until_date S3ObjectCopy#object_lock_retain_until_date}
        :param server_side_encryption: The server-side encryption algorithm used when storing this object copy in IONOS Object Storage Object Copy Storage (AES256). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption S3ObjectCopy#server_side_encryption}
        :param server_side_encryption_customer_algorithm: Specifies the algorithm to use to when encrypting the object copy (e.g., AES256). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_algorithm S3ObjectCopy#server_side_encryption_customer_algorithm}
        :param server_side_encryption_customer_key: Specifies the 256-bit, base64-encoded encryption key to use to encrypt and decrypt your data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_key S3ObjectCopy#server_side_encryption_customer_key}
        :param server_side_encryption_customer_key_md5: Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321. IONOS Object Storage Object Copy Storage uses this header for a message integrity check to ensure that the encryption key was transmitted without error Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_key_md5 S3ObjectCopy#server_side_encryption_customer_key_md5}
        :param source_customer_algorithm: Specifies the algorithm to use to when decrypting the source object (e.g., AES256). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_algorithm S3ObjectCopy#source_customer_algorithm}
        :param source_customer_key: Specifies the 256-bit, base64-encoded encryption key to use to decrypt the source object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_key S3ObjectCopy#source_customer_key}
        :param source_customer_key_md5: Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321. IONOS Object Storage Object Copy Storage uses this header for a message integrity check to ensure that the encryption key was transmitted without error Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_key_md5 S3ObjectCopy#source_customer_key_md5}
        :param storage_class: The storage class of the object copy. Valid value is 'STANDARD'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#storage_class S3ObjectCopy#storage_class}
        :param tagging_directive: Specifies whether the object copy tag-set is copied from the source object or replaced with tag-set provided in the request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#tagging_directive S3ObjectCopy#tagging_directive}
        :param tags: The tag-set for the object copy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#tags S3ObjectCopy#tags}
        :param website_redirect: If the bucket is configured as a website, redirects requests for this object copy to another object copy in the same bucket or to an external URL. IONOS Object Storage Object Copy Storage stores the value of this header in the object copy metadata Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#website_redirect S3ObjectCopy#website_redirect}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c02ba2ba336075dfd1affceba1143cf4b06badb78a0f21bb0384eed1075a99ac)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument cache_control", value=cache_control, expected_type=type_hints["cache_control"])
            check_type(argname="argument content_disposition", value=content_disposition, expected_type=type_hints["content_disposition"])
            check_type(argname="argument content_encoding", value=content_encoding, expected_type=type_hints["content_encoding"])
            check_type(argname="argument content_language", value=content_language, expected_type=type_hints["content_language"])
            check_type(argname="argument content_type", value=content_type, expected_type=type_hints["content_type"])
            check_type(argname="argument copy_if_match", value=copy_if_match, expected_type=type_hints["copy_if_match"])
            check_type(argname="argument copy_if_modified_since", value=copy_if_modified_since, expected_type=type_hints["copy_if_modified_since"])
            check_type(argname="argument copy_if_none_match", value=copy_if_none_match, expected_type=type_hints["copy_if_none_match"])
            check_type(argname="argument copy_if_unmodified_since", value=copy_if_unmodified_since, expected_type=type_hints["copy_if_unmodified_since"])
            check_type(argname="argument expires", value=expires, expected_type=type_hints["expires"])
            check_type(argname="argument force_destroy", value=force_destroy, expected_type=type_hints["force_destroy"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument metadata_directive", value=metadata_directive, expected_type=type_hints["metadata_directive"])
            check_type(argname="argument object_lock_legal_hold", value=object_lock_legal_hold, expected_type=type_hints["object_lock_legal_hold"])
            check_type(argname="argument object_lock_mode", value=object_lock_mode, expected_type=type_hints["object_lock_mode"])
            check_type(argname="argument object_lock_retain_until_date", value=object_lock_retain_until_date, expected_type=type_hints["object_lock_retain_until_date"])
            check_type(argname="argument server_side_encryption", value=server_side_encryption, expected_type=type_hints["server_side_encryption"])
            check_type(argname="argument server_side_encryption_customer_algorithm", value=server_side_encryption_customer_algorithm, expected_type=type_hints["server_side_encryption_customer_algorithm"])
            check_type(argname="argument server_side_encryption_customer_key", value=server_side_encryption_customer_key, expected_type=type_hints["server_side_encryption_customer_key"])
            check_type(argname="argument server_side_encryption_customer_key_md5", value=server_side_encryption_customer_key_md5, expected_type=type_hints["server_side_encryption_customer_key_md5"])
            check_type(argname="argument source_customer_algorithm", value=source_customer_algorithm, expected_type=type_hints["source_customer_algorithm"])
            check_type(argname="argument source_customer_key", value=source_customer_key, expected_type=type_hints["source_customer_key"])
            check_type(argname="argument source_customer_key_md5", value=source_customer_key_md5, expected_type=type_hints["source_customer_key_md5"])
            check_type(argname="argument storage_class", value=storage_class, expected_type=type_hints["storage_class"])
            check_type(argname="argument tagging_directive", value=tagging_directive, expected_type=type_hints["tagging_directive"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument website_redirect", value=website_redirect, expected_type=type_hints["website_redirect"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "key": key,
            "source": source,
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
        if cache_control is not None:
            self._values["cache_control"] = cache_control
        if content_disposition is not None:
            self._values["content_disposition"] = content_disposition
        if content_encoding is not None:
            self._values["content_encoding"] = content_encoding
        if content_language is not None:
            self._values["content_language"] = content_language
        if content_type is not None:
            self._values["content_type"] = content_type
        if copy_if_match is not None:
            self._values["copy_if_match"] = copy_if_match
        if copy_if_modified_since is not None:
            self._values["copy_if_modified_since"] = copy_if_modified_since
        if copy_if_none_match is not None:
            self._values["copy_if_none_match"] = copy_if_none_match
        if copy_if_unmodified_since is not None:
            self._values["copy_if_unmodified_since"] = copy_if_unmodified_since
        if expires is not None:
            self._values["expires"] = expires
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if metadata is not None:
            self._values["metadata"] = metadata
        if metadata_directive is not None:
            self._values["metadata_directive"] = metadata_directive
        if object_lock_legal_hold is not None:
            self._values["object_lock_legal_hold"] = object_lock_legal_hold
        if object_lock_mode is not None:
            self._values["object_lock_mode"] = object_lock_mode
        if object_lock_retain_until_date is not None:
            self._values["object_lock_retain_until_date"] = object_lock_retain_until_date
        if server_side_encryption is not None:
            self._values["server_side_encryption"] = server_side_encryption
        if server_side_encryption_customer_algorithm is not None:
            self._values["server_side_encryption_customer_algorithm"] = server_side_encryption_customer_algorithm
        if server_side_encryption_customer_key is not None:
            self._values["server_side_encryption_customer_key"] = server_side_encryption_customer_key
        if server_side_encryption_customer_key_md5 is not None:
            self._values["server_side_encryption_customer_key_md5"] = server_side_encryption_customer_key_md5
        if source_customer_algorithm is not None:
            self._values["source_customer_algorithm"] = source_customer_algorithm
        if source_customer_key is not None:
            self._values["source_customer_key"] = source_customer_key
        if source_customer_key_md5 is not None:
            self._values["source_customer_key_md5"] = source_customer_key_md5
        if storage_class is not None:
            self._values["storage_class"] = storage_class
        if tagging_directive is not None:
            self._values["tagging_directive"] = tagging_directive
        if tags is not None:
            self._values["tags"] = tags
        if website_redirect is not None:
            self._values["website_redirect"] = website_redirect

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#bucket S3ObjectCopy#bucket}
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> builtins.str:
        '''The key of the object copy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#key S3ObjectCopy#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source(self) -> builtins.str:
        '''The key of the source object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source S3ObjectCopy#source}
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cache_control(self) -> typing.Optional[builtins.str]:
        '''Can be used to specify caching behavior along the request/reply chain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#cache_control S3ObjectCopy#cache_control}
        '''
        result = self._values.get("cache_control")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_disposition(self) -> typing.Optional[builtins.str]:
        '''Specifies presentational information for the object copy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_disposition S3ObjectCopy#content_disposition}
        '''
        result = self._values.get("content_disposition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_encoding(self) -> typing.Optional[builtins.str]:
        '''Specifies what content encodings have been applied to the object copy and thus what decoding mechanisms must be applied to obtain the media-type referenced by the Content-Type header field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_encoding S3ObjectCopy#content_encoding}
        '''
        result = self._values.get("content_encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_language(self) -> typing.Optional[builtins.str]:
        '''The natural language or languages of the intended audience for the object copy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_language S3ObjectCopy#content_language}
        '''
        result = self._values.get("content_language")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_type(self) -> typing.Optional[builtins.str]:
        '''A standard MIME type describing the format of the contents.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#content_type S3ObjectCopy#content_type}
        '''
        result = self._values.get("content_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_match(self) -> typing.Optional[builtins.str]:
        '''Copies the object if its entity tag (ETag) matches the specified tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_match S3ObjectCopy#copy_if_match}
        '''
        result = self._values.get("copy_if_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_modified_since(self) -> typing.Optional[builtins.str]:
        '''Copies the object if it has been modified since the specified time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_modified_since S3ObjectCopy#copy_if_modified_since}
        '''
        result = self._values.get("copy_if_modified_since")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_none_match(self) -> typing.Optional[builtins.str]:
        '''Copies the object if its entity tag (ETag) is different than the specified ETag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_none_match S3ObjectCopy#copy_if_none_match}
        '''
        result = self._values.get("copy_if_none_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def copy_if_unmodified_since(self) -> typing.Optional[builtins.str]:
        '''Copies the object if it hasn't been modified since the specified time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#copy_if_unmodified_since S3ObjectCopy#copy_if_unmodified_since}
        '''
        result = self._values.get("copy_if_unmodified_since")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expires(self) -> typing.Optional[builtins.str]:
        '''The date and time at which the object copy is no longer cacheable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#expires S3ObjectCopy#expires}
        '''
        result = self._values.get("expires")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to delete the object copy even if it has a governance-type Object Copy Lock in place.

        You must explicitly pass a value of true for this parameter to delete the object copy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#force_destroy S3ObjectCopy#force_destroy}
        '''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def metadata(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of metadata to store with the object copy in IONOS Object Storage Object Copy Storage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#metadata S3ObjectCopy#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def metadata_directive(self) -> typing.Optional[builtins.str]:
        '''Specifies whether the metadata is copied from the source object or replaced with metadata provided in the request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#metadata_directive S3ObjectCopy#metadata_directive}
        '''
        result = self._values.get("metadata_directive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_legal_hold(self) -> typing.Optional[builtins.str]:
        '''Specifies whether a legal hold will be applied to this object copy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_legal_hold S3ObjectCopy#object_lock_legal_hold}
        '''
        result = self._values.get("object_lock_legal_hold")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_mode(self) -> typing.Optional[builtins.str]:
        '''Confirms that the requester knows that they will be charged for the request.

        Bucket owners need not specify this parameter in their requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_mode S3ObjectCopy#object_lock_mode}
        '''
        result = self._values.get("object_lock_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_lock_retain_until_date(self) -> typing.Optional[builtins.str]:
        '''The date and time when you want this object copy's Object Copy Lock to expire.

        Must be formatted as a timestamp parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#object_lock_retain_until_date S3ObjectCopy#object_lock_retain_until_date}
        '''
        result = self._values.get("object_lock_retain_until_date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption(self) -> typing.Optional[builtins.str]:
        '''The server-side encryption algorithm used when storing this object copy in IONOS Object Storage Object Copy Storage (AES256).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption S3ObjectCopy#server_side_encryption}
        '''
        result = self._values.get("server_side_encryption")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption_customer_algorithm(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Specifies the algorithm to use to when encrypting the object copy (e.g., AES256).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_algorithm S3ObjectCopy#server_side_encryption_customer_algorithm}
        '''
        result = self._values.get("server_side_encryption_customer_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption_customer_key(self) -> typing.Optional[builtins.str]:
        '''Specifies the 256-bit, base64-encoded encryption key to use to encrypt and decrypt your data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_key S3ObjectCopy#server_side_encryption_customer_key}
        '''
        result = self._values.get("server_side_encryption_customer_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_side_encryption_customer_key_md5(self) -> typing.Optional[builtins.str]:
        '''Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321.

        IONOS Object Storage Object Copy Storage uses this header for a message integrity check  to ensure that the encryption key was transmitted without error

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#server_side_encryption_customer_key_md5 S3ObjectCopy#server_side_encryption_customer_key_md5}
        '''
        result = self._values.get("server_side_encryption_customer_key_md5")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_customer_algorithm(self) -> typing.Optional[builtins.str]:
        '''Specifies the algorithm to use to when decrypting the source object (e.g., AES256).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_algorithm S3ObjectCopy#source_customer_algorithm}
        '''
        result = self._values.get("source_customer_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_customer_key(self) -> typing.Optional[builtins.str]:
        '''Specifies the 256-bit, base64-encoded encryption key to use to decrypt the source object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_key S3ObjectCopy#source_customer_key}
        '''
        result = self._values.get("source_customer_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_customer_key_md5(self) -> typing.Optional[builtins.str]:
        '''Specifies the 128-bit MD5 digest of the encryption key according to RFC 1321.

        IONOS Object Storage Object Copy Storage uses this header for a message integrity check  to ensure that the encryption key was transmitted without error

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#source_customer_key_md5 S3ObjectCopy#source_customer_key_md5}
        '''
        result = self._values.get("source_customer_key_md5")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_class(self) -> typing.Optional[builtins.str]:
        '''The storage class of the object copy. Valid value is 'STANDARD'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#storage_class S3ObjectCopy#storage_class}
        '''
        result = self._values.get("storage_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tagging_directive(self) -> typing.Optional[builtins.str]:
        '''Specifies whether the object copy tag-set is copied from the source object or replaced with tag-set provided in the request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#tagging_directive S3ObjectCopy#tagging_directive}
        '''
        result = self._values.get("tagging_directive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The tag-set for the object copy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#tags S3ObjectCopy#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def website_redirect(self) -> typing.Optional[builtins.str]:
        '''If the bucket is configured as a website, redirects requests for this object copy to another object copy in the same bucket or to an external URL.

        IONOS Object Storage Object Copy Storage stores the value of this header in the object copy metadata

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.7.13/docs/resources/s3_object_copy#website_redirect S3ObjectCopy#website_redirect}
        '''
        result = self._values.get("website_redirect")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ObjectCopyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "S3ObjectCopy",
    "S3ObjectCopyConfig",
]

publication.publish()

def _typecheckingstub__496ab3efab151c061e3b5abf4064d4ad919526fa9ba61d633db55855693463ef(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket: builtins.str,
    key: builtins.str,
    source: builtins.str,
    cache_control: typing.Optional[builtins.str] = None,
    content_disposition: typing.Optional[builtins.str] = None,
    content_encoding: typing.Optional[builtins.str] = None,
    content_language: typing.Optional[builtins.str] = None,
    content_type: typing.Optional[builtins.str] = None,
    copy_if_match: typing.Optional[builtins.str] = None,
    copy_if_modified_since: typing.Optional[builtins.str] = None,
    copy_if_none_match: typing.Optional[builtins.str] = None,
    copy_if_unmodified_since: typing.Optional[builtins.str] = None,
    expires: typing.Optional[builtins.str] = None,
    force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    metadata_directive: typing.Optional[builtins.str] = None,
    object_lock_legal_hold: typing.Optional[builtins.str] = None,
    object_lock_mode: typing.Optional[builtins.str] = None,
    object_lock_retain_until_date: typing.Optional[builtins.str] = None,
    server_side_encryption: typing.Optional[builtins.str] = None,
    server_side_encryption_customer_algorithm: typing.Optional[builtins.str] = None,
    server_side_encryption_customer_key: typing.Optional[builtins.str] = None,
    server_side_encryption_customer_key_md5: typing.Optional[builtins.str] = None,
    source_customer_algorithm: typing.Optional[builtins.str] = None,
    source_customer_key: typing.Optional[builtins.str] = None,
    source_customer_key_md5: typing.Optional[builtins.str] = None,
    storage_class: typing.Optional[builtins.str] = None,
    tagging_directive: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    website_redirect: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__402a7a162fc6f1a6b6e39a33b7acc7db016f16460cd91380b4494503b09f160c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a44dda204c025610dfba3b2afeb0df04550b134ca6d01cce9b224f3b0bc83d47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91398fb332c00c03c00c7077800a5d5f7e87f26e1663637ccd305d89afcf9f5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d250d0f65dc35b7b54f4f988f84f7bb25012e89da8501cc6a492c1de4fbbb95d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4066d66bce78e39483952d074ba992c183dc0217cf2d8d9878de3d3ed3cb2ca0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a35cae93e67dc7617af7fe15bb72d53d11d115324642fbd409cc293e5347f76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67210c097b3e6d0f780376cccca484a8e00d2cb43339861f1bb7f33f606d5b17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0240e238bae4f7d20f1a1dc05ee5d0bd70d81870f291c1730f8d914643171dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fc923bece2021655c74c8d81eb9603b6dd640dd13903157f025541dc84b0dfd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c926ce44b815e55e35f41fe7f99001070b0ba55d575ce0c1d6cdb9d87e89709b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd997f3e0385ec502c19c0cdcbc6baba2b7923ef9423963f10d559efc8e09d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c0c254f2049b1dbccba6a5f56470ce443bb2ec3a39ba9f2c36707e3e034ec3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c68a51975809a7e6322aa10363b5049d96edaabe65a4af5ff26a5f21534249be(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc727669a575dd60524ae4ac2223ca17e333393ba50bac3404c70dfb9b08aabd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a9f7a8a0cd4a5bfe4e0309f25b8a4738e6db5442732502756e6fb6abd174916(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c07293dcf00a795e0a14dbd880bf18ebb1219b510f86ee7930bf772dd52bb140(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9542023b6de066ed4512383ef2b611a8dc28ce4020f82df5ceeaf9d5998a4259(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0cd751ef7f8663577a4b3865c01f98bc17179f82eca92994dfa75358dca441a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__245589f0bc48cc2679c6faf5dc1a26c00d029be66211a6e8f38b3f462aeaf37c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faeb5023e6e7ab17270c7a65681baaf1c51c48f6f613083cce05d583a674bed3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ea565849d5dcbc4fc4c1b46227d8005f043ff86e5d073a3f88e6c2d517bb4f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55e73a2218645df26dea458c8cdcf5e4309f1168782346542f977122d9293fdb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc717b96914c89840e200230c904d1720150c1d1820fd0dcf2a72746401fa0bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfb3f1cbfeb7da49d79dad07771a3266327423a48b0575ce07451576341b67e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06bf56285f8f41213ceb5ee69a95ab744184c231889e3de6a4db766fe57f4468(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7917106b0d87dd29b4fbfb6ff257aaa7856e0ec3ab5dcab070496c2a456fd4a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de0a06391b0aef94ef04a6a947d800bc16d04a57143fc8c21548397a1d088c1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631833ee75fcecb95ea8b5feae4ca96efcfc3014087034e63eef0eea4435908a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d2aa6036f659f12b20f4ef375713e857558e44fd23077743df940c708398ade(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d161a526cb877f62c76f33e4f19502613a6d938120a11d85eb82a8f0a70ae0df(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9994555e64ac9ccfe9ac639a7bfc9f0981f19b7f3670b72f86902295d4b6baa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c02ba2ba336075dfd1affceba1143cf4b06badb78a0f21bb0384eed1075a99ac(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bucket: builtins.str,
    key: builtins.str,
    source: builtins.str,
    cache_control: typing.Optional[builtins.str] = None,
    content_disposition: typing.Optional[builtins.str] = None,
    content_encoding: typing.Optional[builtins.str] = None,
    content_language: typing.Optional[builtins.str] = None,
    content_type: typing.Optional[builtins.str] = None,
    copy_if_match: typing.Optional[builtins.str] = None,
    copy_if_modified_since: typing.Optional[builtins.str] = None,
    copy_if_none_match: typing.Optional[builtins.str] = None,
    copy_if_unmodified_since: typing.Optional[builtins.str] = None,
    expires: typing.Optional[builtins.str] = None,
    force_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    metadata_directive: typing.Optional[builtins.str] = None,
    object_lock_legal_hold: typing.Optional[builtins.str] = None,
    object_lock_mode: typing.Optional[builtins.str] = None,
    object_lock_retain_until_date: typing.Optional[builtins.str] = None,
    server_side_encryption: typing.Optional[builtins.str] = None,
    server_side_encryption_customer_algorithm: typing.Optional[builtins.str] = None,
    server_side_encryption_customer_key: typing.Optional[builtins.str] = None,
    server_side_encryption_customer_key_md5: typing.Optional[builtins.str] = None,
    source_customer_algorithm: typing.Optional[builtins.str] = None,
    source_customer_key: typing.Optional[builtins.str] = None,
    source_customer_key_md5: typing.Optional[builtins.str] = None,
    storage_class: typing.Optional[builtins.str] = None,
    tagging_directive: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    website_redirect: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
