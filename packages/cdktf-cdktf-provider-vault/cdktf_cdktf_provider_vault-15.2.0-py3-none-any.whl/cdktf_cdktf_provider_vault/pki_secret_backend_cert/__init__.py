r'''
# `vault_pki_secret_backend_cert`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_cert`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert).
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


class PkiSecretBackendCert(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendCert.PkiSecretBackendCert",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert vault_pki_secret_backend_cert}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        common_name: builtins.str,
        name: builtins.str,
        alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cert_metadata: typing.Optional[builtins.str] = None,
        exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        issuer_ref: typing.Optional[builtins.str] = None,
        min_seconds_remaining: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_after: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        private_key_format: typing.Optional[builtins.str] = None,
        revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        revoke_with_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ttl: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert vault_pki_secret_backend_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#backend PkiSecretBackendCert#backend}
        :param common_name: CN of the certificate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#common_name PkiSecretBackendCert#common_name}
        :param name: Name of the role to create the certificate against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#name PkiSecretBackendCert#name}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#alt_names PkiSecretBackendCert#alt_names}
        :param auto_renew: If enabled, a new certificate will be generated if the expiration is within min_seconds_remaining. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#auto_renew PkiSecretBackendCert#auto_renew}
        :param cert_metadata: A base 64 encoded value or an empty string to associate with the certificate's serial number. The role's no_store_metadata must be set to false, otherwise an error is returned when specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#cert_metadata PkiSecretBackendCert#cert_metadata}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#exclude_cn_from_sans PkiSecretBackendCert#exclude_cn_from_sans}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#format PkiSecretBackendCert#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#id PkiSecretBackendCert#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#ip_sans PkiSecretBackendCert#ip_sans}
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#issuer_ref PkiSecretBackendCert#issuer_ref}
        :param min_seconds_remaining: Generate a new certificate when the expiration is within this number of seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#min_seconds_remaining PkiSecretBackendCert#min_seconds_remaining}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#namespace PkiSecretBackendCert#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#not_after PkiSecretBackendCert#not_after}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#other_sans PkiSecretBackendCert#other_sans}
        :param private_key_format: The private key format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#private_key_format PkiSecretBackendCert#private_key_format}
        :param revoke: Revoke the certificate upon resource destruction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#revoke PkiSecretBackendCert#revoke}
        :param revoke_with_key: Revoke the certificate with private key method upon resource destruction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#revoke_with_key PkiSecretBackendCert#revoke_with_key}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#ttl PkiSecretBackendCert#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#uri_sans PkiSecretBackendCert#uri_sans}
        :param user_ids: List of Subject User IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#user_ids PkiSecretBackendCert#user_ids}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2815269061eeda8bf3c431336f698cf2014e24418495f89676610aa4853c2e51)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendCertConfig(
            backend=backend,
            common_name=common_name,
            name=name,
            alt_names=alt_names,
            auto_renew=auto_renew,
            cert_metadata=cert_metadata,
            exclude_cn_from_sans=exclude_cn_from_sans,
            format=format,
            id=id,
            ip_sans=ip_sans,
            issuer_ref=issuer_ref,
            min_seconds_remaining=min_seconds_remaining,
            namespace=namespace,
            not_after=not_after,
            other_sans=other_sans,
            private_key_format=private_key_format,
            revoke=revoke,
            revoke_with_key=revoke_with_key,
            ttl=ttl,
            uri_sans=uri_sans,
            user_ids=user_ids,
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
        '''Generates CDKTF code for importing a PkiSecretBackendCert resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendCert to import.
        :param import_from_id: The id of the existing PkiSecretBackendCert that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendCert to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7044ef7d3343aa35a050228938264200945c67e79a555f8269eed7be4654de44)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAltNames")
    def reset_alt_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAltNames", []))

    @jsii.member(jsii_name="resetAutoRenew")
    def reset_auto_renew(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRenew", []))

    @jsii.member(jsii_name="resetCertMetadata")
    def reset_cert_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertMetadata", []))

    @jsii.member(jsii_name="resetExcludeCnFromSans")
    def reset_exclude_cn_from_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeCnFromSans", []))

    @jsii.member(jsii_name="resetFormat")
    def reset_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormat", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpSans")
    def reset_ip_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpSans", []))

    @jsii.member(jsii_name="resetIssuerRef")
    def reset_issuer_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuerRef", []))

    @jsii.member(jsii_name="resetMinSecondsRemaining")
    def reset_min_seconds_remaining(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinSecondsRemaining", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNotAfter")
    def reset_not_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotAfter", []))

    @jsii.member(jsii_name="resetOtherSans")
    def reset_other_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOtherSans", []))

    @jsii.member(jsii_name="resetPrivateKeyFormat")
    def reset_private_key_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyFormat", []))

    @jsii.member(jsii_name="resetRevoke")
    def reset_revoke(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevoke", []))

    @jsii.member(jsii_name="resetRevokeWithKey")
    def reset_revoke_with_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevokeWithKey", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetUriSans")
    def reset_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUriSans", []))

    @jsii.member(jsii_name="resetUserIds")
    def reset_user_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserIds", []))

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
    @jsii.member(jsii_name="caChain")
    def ca_chain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caChain"))

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="expiration")
    def expiration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expiration"))

    @builtins.property
    @jsii.member(jsii_name="issuingCa")
    def issuing_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuingCa"))

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyType")
    def private_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyType"))

    @builtins.property
    @jsii.member(jsii_name="renewPending")
    def renew_pending(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "renewPending"))

    @builtins.property
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @builtins.property
    @jsii.member(jsii_name="altNamesInput")
    def alt_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "altNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRenewInput")
    def auto_renew_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoRenewInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="certMetadataInput")
    def cert_metadata_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certMetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeCnFromSansInput")
    def exclude_cn_from_sans_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeCnFromSansInput"))

    @builtins.property
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipSansInput")
    def ip_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipSansInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerRefInput")
    def issuer_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerRefInput"))

    @builtins.property
    @jsii.member(jsii_name="minSecondsRemainingInput")
    def min_seconds_remaining_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minSecondsRemainingInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="notAfterInput")
    def not_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="otherSansInput")
    def other_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "otherSansInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyFormatInput")
    def private_key_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeInput")
    def revoke_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "revokeInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeWithKeyInput")
    def revoke_with_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "revokeWithKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="uriSansInput")
    def uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "uriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="userIdsInput")
    def user_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="altNames")
    def alt_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "altNames"))

    @alt_names.setter
    def alt_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c18413ae5b8c0972dd9cf45ebbc57ea90fa018acd19a36bc68e46aa8c088bfa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoRenew")
    def auto_renew(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoRenew"))

    @auto_renew.setter
    def auto_renew(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed90d5386f8077498f21c5222e351718514d3279b4dd7dd09674b447a7c5ffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRenew", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12cdd31db7cb3a4bb82decf29d05dfbd6401cc754d97655cd9acfcde18660c64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certMetadata")
    def cert_metadata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certMetadata"))

    @cert_metadata.setter
    def cert_metadata(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa4d0616b768ce36a2c4cf16469d89fce531d8bf1a848191bf014c03008888b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certMetadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cbeec2b9a8101027855e88806cc51128b62c8eb25559fe2f4b8c1a66196a347)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeCnFromSans")
    def exclude_cn_from_sans(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludeCnFromSans"))

    @exclude_cn_from_sans.setter
    def exclude_cn_from_sans(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3079ccf56580b3950f0d060879e2f066bdd42831eb7a1baaeb632de0493a5c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeCnFromSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e66b3ca096d0ca8799207d1599614acc0b490a5624fb42df62f01ab497231be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e6aa3f7ffb625dafaf87d1ce1de59d4e3a3855aba5634564f04b12ab3637389)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipSans")
    def ip_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipSans"))

    @ip_sans.setter
    def ip_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c851d6d94fc39d3c5a595a06b0605752959e7f5be57d52e9ae6e901c12079f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerRef")
    def issuer_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerRef"))

    @issuer_ref.setter
    def issuer_ref(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4656e8d4163db8064e3057eb908e0c459c593247c82aba3a64f803e2ee833e76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerRef", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minSecondsRemaining")
    def min_seconds_remaining(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSecondsRemaining"))

    @min_seconds_remaining.setter
    def min_seconds_remaining(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6643acba4726f816f5f626fa899abb15eddf30d870d06f50bf9ce61271157074)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minSecondsRemaining", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c55e00ffb9850d505d405766a19eb9fdef38a5a8116752e2afc6a6f3e5c6c1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e841dfb6ab95b4825733d31042fabca0208d4fe36f52431aad23de90f79e5bab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @not_after.setter
    def not_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__867cd63cca4e31b395ca2f11bbb46fd0df6caedcd1385e46a7a78f24f2d415cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="otherSans")
    def other_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "otherSans"))

    @other_sans.setter
    def other_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e32e5de5a93739574f8cd548cce1039907bb9aafb7848d54b4b38cf92c0a3318)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "otherSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyFormat")
    def private_key_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyFormat"))

    @private_key_format.setter
    def private_key_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28e3b9d9c0d407a32df54d0c9f7cb1095aec22e5cb3d58a8f43eca8c3dac024)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="revoke")
    def revoke(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "revoke"))

    @revoke.setter
    def revoke(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4f2d7d22d79bba3495bfdec1667e30e8ff6454bff04a5043554b26f6ae33792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revoke", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="revokeWithKey")
    def revoke_with_key(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "revokeWithKey"))

    @revoke_with_key.setter
    def revoke_with_key(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6b9d2f591208e8df369bd4466bc5c24e273d0c63d4c2e2cf45ae003556d0bbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokeWithKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f43836d54249ac7b74e82e31d129263710cfd9b91a3f4e40159bd64328e361e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fcdd0f2267a3575c45fc297fa7d9fe69b8ee5cac1921c1d3d4b0145b4119b01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userIds")
    def user_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userIds"))

    @user_ids.setter
    def user_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc0251928beef60e9608ab209294f30e60a55b794acf58cc9cfc741e21a99ade)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userIds", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendCert.PkiSecretBackendCertConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "backend": "backend",
        "common_name": "commonName",
        "name": "name",
        "alt_names": "altNames",
        "auto_renew": "autoRenew",
        "cert_metadata": "certMetadata",
        "exclude_cn_from_sans": "excludeCnFromSans",
        "format": "format",
        "id": "id",
        "ip_sans": "ipSans",
        "issuer_ref": "issuerRef",
        "min_seconds_remaining": "minSecondsRemaining",
        "namespace": "namespace",
        "not_after": "notAfter",
        "other_sans": "otherSans",
        "private_key_format": "privateKeyFormat",
        "revoke": "revoke",
        "revoke_with_key": "revokeWithKey",
        "ttl": "ttl",
        "uri_sans": "uriSans",
        "user_ids": "userIds",
    },
)
class PkiSecretBackendCertConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: builtins.str,
        common_name: builtins.str,
        name: builtins.str,
        alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cert_metadata: typing.Optional[builtins.str] = None,
        exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        issuer_ref: typing.Optional[builtins.str] = None,
        min_seconds_remaining: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_after: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        private_key_format: typing.Optional[builtins.str] = None,
        revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        revoke_with_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ttl: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#backend PkiSecretBackendCert#backend}
        :param common_name: CN of the certificate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#common_name PkiSecretBackendCert#common_name}
        :param name: Name of the role to create the certificate against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#name PkiSecretBackendCert#name}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#alt_names PkiSecretBackendCert#alt_names}
        :param auto_renew: If enabled, a new certificate will be generated if the expiration is within min_seconds_remaining. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#auto_renew PkiSecretBackendCert#auto_renew}
        :param cert_metadata: A base 64 encoded value or an empty string to associate with the certificate's serial number. The role's no_store_metadata must be set to false, otherwise an error is returned when specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#cert_metadata PkiSecretBackendCert#cert_metadata}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#exclude_cn_from_sans PkiSecretBackendCert#exclude_cn_from_sans}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#format PkiSecretBackendCert#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#id PkiSecretBackendCert#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#ip_sans PkiSecretBackendCert#ip_sans}
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#issuer_ref PkiSecretBackendCert#issuer_ref}
        :param min_seconds_remaining: Generate a new certificate when the expiration is within this number of seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#min_seconds_remaining PkiSecretBackendCert#min_seconds_remaining}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#namespace PkiSecretBackendCert#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#not_after PkiSecretBackendCert#not_after}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#other_sans PkiSecretBackendCert#other_sans}
        :param private_key_format: The private key format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#private_key_format PkiSecretBackendCert#private_key_format}
        :param revoke: Revoke the certificate upon resource destruction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#revoke PkiSecretBackendCert#revoke}
        :param revoke_with_key: Revoke the certificate with private key method upon resource destruction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#revoke_with_key PkiSecretBackendCert#revoke_with_key}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#ttl PkiSecretBackendCert#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#uri_sans PkiSecretBackendCert#uri_sans}
        :param user_ids: List of Subject User IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#user_ids PkiSecretBackendCert#user_ids}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b16af1485ca0d51b93e10a6315754926daceab71676db3030f807a4169b36732)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alt_names", value=alt_names, expected_type=type_hints["alt_names"])
            check_type(argname="argument auto_renew", value=auto_renew, expected_type=type_hints["auto_renew"])
            check_type(argname="argument cert_metadata", value=cert_metadata, expected_type=type_hints["cert_metadata"])
            check_type(argname="argument exclude_cn_from_sans", value=exclude_cn_from_sans, expected_type=type_hints["exclude_cn_from_sans"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_sans", value=ip_sans, expected_type=type_hints["ip_sans"])
            check_type(argname="argument issuer_ref", value=issuer_ref, expected_type=type_hints["issuer_ref"])
            check_type(argname="argument min_seconds_remaining", value=min_seconds_remaining, expected_type=type_hints["min_seconds_remaining"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument not_after", value=not_after, expected_type=type_hints["not_after"])
            check_type(argname="argument other_sans", value=other_sans, expected_type=type_hints["other_sans"])
            check_type(argname="argument private_key_format", value=private_key_format, expected_type=type_hints["private_key_format"])
            check_type(argname="argument revoke", value=revoke, expected_type=type_hints["revoke"])
            check_type(argname="argument revoke_with_key", value=revoke_with_key, expected_type=type_hints["revoke_with_key"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
            check_type(argname="argument user_ids", value=user_ids, expected_type=type_hints["user_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "common_name": common_name,
            "name": name,
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
        if alt_names is not None:
            self._values["alt_names"] = alt_names
        if auto_renew is not None:
            self._values["auto_renew"] = auto_renew
        if cert_metadata is not None:
            self._values["cert_metadata"] = cert_metadata
        if exclude_cn_from_sans is not None:
            self._values["exclude_cn_from_sans"] = exclude_cn_from_sans
        if format is not None:
            self._values["format"] = format
        if id is not None:
            self._values["id"] = id
        if ip_sans is not None:
            self._values["ip_sans"] = ip_sans
        if issuer_ref is not None:
            self._values["issuer_ref"] = issuer_ref
        if min_seconds_remaining is not None:
            self._values["min_seconds_remaining"] = min_seconds_remaining
        if namespace is not None:
            self._values["namespace"] = namespace
        if not_after is not None:
            self._values["not_after"] = not_after
        if other_sans is not None:
            self._values["other_sans"] = other_sans
        if private_key_format is not None:
            self._values["private_key_format"] = private_key_format
        if revoke is not None:
            self._values["revoke"] = revoke
        if revoke_with_key is not None:
            self._values["revoke_with_key"] = revoke_with_key
        if ttl is not None:
            self._values["ttl"] = ttl
        if uri_sans is not None:
            self._values["uri_sans"] = uri_sans
        if user_ids is not None:
            self._values["user_ids"] = user_ids

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
    def backend(self) -> builtins.str:
        '''The PKI secret backend the resource belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#backend PkiSecretBackendCert#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def common_name(self) -> builtins.str:
        '''CN of the certificate to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#common_name PkiSecretBackendCert#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the role to create the certificate against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#name PkiSecretBackendCert#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alt_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#alt_names PkiSecretBackendCert#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auto_renew(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If enabled, a new certificate will be generated if the expiration is within min_seconds_remaining.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#auto_renew PkiSecretBackendCert#auto_renew}
        '''
        result = self._values.get("auto_renew")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cert_metadata(self) -> typing.Optional[builtins.str]:
        '''A base 64 encoded value or an empty string to associate with the certificate's serial number.

        The role's no_store_metadata must be set to false, otherwise an error is returned when specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#cert_metadata PkiSecretBackendCert#cert_metadata}
        '''
        result = self._values.get("cert_metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_cn_from_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to exclude CN from SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#exclude_cn_from_sans PkiSecretBackendCert#exclude_cn_from_sans}
        '''
        result = self._values.get("exclude_cn_from_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format of data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#format PkiSecretBackendCert#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#id PkiSecretBackendCert#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#ip_sans PkiSecretBackendCert#ip_sans}
        '''
        result = self._values.get("ip_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def issuer_ref(self) -> typing.Optional[builtins.str]:
        '''Specifies the default issuer of this request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#issuer_ref PkiSecretBackendCert#issuer_ref}
        '''
        result = self._values.get("issuer_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_seconds_remaining(self) -> typing.Optional[jsii.Number]:
        '''Generate a new certificate when the expiration is within this number of seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#min_seconds_remaining PkiSecretBackendCert#min_seconds_remaining}
        '''
        result = self._values.get("min_seconds_remaining")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#namespace PkiSecretBackendCert#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_after(self) -> typing.Optional[builtins.str]:
        '''Set the Not After field of the certificate with specified date value.

        The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#not_after PkiSecretBackendCert#not_after}
        '''
        result = self._values.get("not_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def other_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of other SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#other_sans PkiSecretBackendCert#other_sans}
        '''
        result = self._values.get("other_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def private_key_format(self) -> typing.Optional[builtins.str]:
        '''The private key format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#private_key_format PkiSecretBackendCert#private_key_format}
        '''
        result = self._values.get("private_key_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revoke(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Revoke the certificate upon resource destruction.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#revoke PkiSecretBackendCert#revoke}
        '''
        result = self._values.get("revoke")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def revoke_with_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Revoke the certificate with private key method upon resource destruction.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#revoke_with_key PkiSecretBackendCert#revoke_with_key}
        '''
        result = self._values.get("revoke_with_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Time to live.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#ttl PkiSecretBackendCert#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative URIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#uri_sans PkiSecretBackendCert#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Subject User IDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_cert#user_ids PkiSecretBackendCert#user_ids}
        '''
        result = self._values.get("user_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendCert",
    "PkiSecretBackendCertConfig",
]

publication.publish()

def _typecheckingstub__2815269061eeda8bf3c431336f698cf2014e24418495f89676610aa4853c2e51(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    common_name: builtins.str,
    name: builtins.str,
    alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cert_metadata: typing.Optional[builtins.str] = None,
    exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    issuer_ref: typing.Optional[builtins.str] = None,
    min_seconds_remaining: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_after: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    private_key_format: typing.Optional[builtins.str] = None,
    revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    revoke_with_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__7044ef7d3343aa35a050228938264200945c67e79a555f8269eed7be4654de44(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c18413ae5b8c0972dd9cf45ebbc57ea90fa018acd19a36bc68e46aa8c088bfa8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed90d5386f8077498f21c5222e351718514d3279b4dd7dd09674b447a7c5ffd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12cdd31db7cb3a4bb82decf29d05dfbd6401cc754d97655cd9acfcde18660c64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa4d0616b768ce36a2c4cf16469d89fce531d8bf1a848191bf014c03008888b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cbeec2b9a8101027855e88806cc51128b62c8eb25559fe2f4b8c1a66196a347(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3079ccf56580b3950f0d060879e2f066bdd42831eb7a1baaeb632de0493a5c4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e66b3ca096d0ca8799207d1599614acc0b490a5624fb42df62f01ab497231be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e6aa3f7ffb625dafaf87d1ce1de59d4e3a3855aba5634564f04b12ab3637389(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c851d6d94fc39d3c5a595a06b0605752959e7f5be57d52e9ae6e901c12079f2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4656e8d4163db8064e3057eb908e0c459c593247c82aba3a64f803e2ee833e76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6643acba4726f816f5f626fa899abb15eddf30d870d06f50bf9ce61271157074(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c55e00ffb9850d505d405766a19eb9fdef38a5a8116752e2afc6a6f3e5c6c1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e841dfb6ab95b4825733d31042fabca0208d4fe36f52431aad23de90f79e5bab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__867cd63cca4e31b395ca2f11bbb46fd0df6caedcd1385e46a7a78f24f2d415cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e32e5de5a93739574f8cd548cce1039907bb9aafb7848d54b4b38cf92c0a3318(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28e3b9d9c0d407a32df54d0c9f7cb1095aec22e5cb3d58a8f43eca8c3dac024(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f2d7d22d79bba3495bfdec1667e30e8ff6454bff04a5043554b26f6ae33792(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6b9d2f591208e8df369bd4466bc5c24e273d0c63d4c2e2cf45ae003556d0bbf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f43836d54249ac7b74e82e31d129263710cfd9b91a3f4e40159bd64328e361e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fcdd0f2267a3575c45fc297fa7d9fe69b8ee5cac1921c1d3d4b0145b4119b01(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc0251928beef60e9608ab209294f30e60a55b794acf58cc9cfc741e21a99ade(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b16af1485ca0d51b93e10a6315754926daceab71676db3030f807a4169b36732(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    common_name: builtins.str,
    name: builtins.str,
    alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cert_metadata: typing.Optional[builtins.str] = None,
    exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    issuer_ref: typing.Optional[builtins.str] = None,
    min_seconds_remaining: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_after: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    private_key_format: typing.Optional[builtins.str] = None,
    revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    revoke_with_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
