r'''
# `vault_pki_secret_backend_sign`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_sign`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign).
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


class PkiSecretBackendSign(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendSign.PkiSecretBackendSign",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign vault_pki_secret_backend_sign}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        common_name: builtins.str,
        csr: builtins.str,
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
        ttl: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign vault_pki_secret_backend_sign} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#backend PkiSecretBackendSign#backend}
        :param common_name: CN of intermediate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#common_name PkiSecretBackendSign#common_name}
        :param csr: The CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#csr PkiSecretBackendSign#csr}
        :param name: Name of the role to create the certificate against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#name PkiSecretBackendSign#name}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#alt_names PkiSecretBackendSign#alt_names}
        :param auto_renew: If enabled, a new certificate will be generated if the expiration is within min_seconds_remaining. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#auto_renew PkiSecretBackendSign#auto_renew}
        :param cert_metadata: A base 64 encoded value or an empty string to associate with the certificate's serial number. The role's no_store_metadata must be set to false, otherwise an error is returned when specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#cert_metadata PkiSecretBackendSign#cert_metadata}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#exclude_cn_from_sans PkiSecretBackendSign#exclude_cn_from_sans}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#format PkiSecretBackendSign#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#id PkiSecretBackendSign#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#ip_sans PkiSecretBackendSign#ip_sans}
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#issuer_ref PkiSecretBackendSign#issuer_ref}
        :param min_seconds_remaining: Generate a new certificate when the expiration is within this number of seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#min_seconds_remaining PkiSecretBackendSign#min_seconds_remaining}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#namespace PkiSecretBackendSign#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#not_after PkiSecretBackendSign#not_after}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#other_sans PkiSecretBackendSign#other_sans}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#ttl PkiSecretBackendSign#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#uri_sans PkiSecretBackendSign#uri_sans}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b41af669c3ca7e76924b5c5648cc4f62509f360ccc4e3ff1be53677afb47554)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendSignConfig(
            backend=backend,
            common_name=common_name,
            csr=csr,
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
            ttl=ttl,
            uri_sans=uri_sans,
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
        '''Generates CDKTF code for importing a PkiSecretBackendSign resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendSign to import.
        :param import_from_id: The id of the existing PkiSecretBackendSign that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendSign to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bfadb60b5fd628618283aee52132735fa292cb205a00d52405ac47ffd07001a)
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

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetUriSans")
    def reset_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUriSans", []))

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
    def ca_chain(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "caChain"))

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
    @jsii.member(jsii_name="csrInput")
    def csr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "csrInput"))

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
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="uriSansInput")
    def uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "uriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="altNames")
    def alt_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "altNames"))

    @alt_names.setter
    def alt_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__537f7b1bd98be981fb1b9d8ccbb0495bde864af7035aa458df3e6f1bd418cedf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4d1dcecd21edc8c4d290b2f978903f1f5ed3b8327d68e1c3563c177361e4941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRenew", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00e7460487ceeab305d478573f42d7d9971d118f8d7d456289e2010406c9a0b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certMetadata")
    def cert_metadata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certMetadata"))

    @cert_metadata.setter
    def cert_metadata(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c77167c9333d43b8534b533cf2a1657cc7b9aac10d8bc7e2c7d774383f223cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certMetadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3930a3031168e1674272de46f917624348eb443b5de5d7238f506bca9b64ad8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="csr")
    def csr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csr"))

    @csr.setter
    def csr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d380abb8a29c5f199c2c778b3534fb0ab9d6bf4cf3f7795b30e5b3e15127dad4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "csr", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__23581e99be7d6880243a465374929d58bcdfe1ce12d4d166f6e264e919d37d42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeCnFromSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__826178722e2336555d7f4a108ebfa8c919a84d194f5b582fd86dc494af395ab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83d6f3af20eff9dc79cf4c9f996bb6d9e81df64b8b12b265f417555b792250dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipSans")
    def ip_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipSans"))

    @ip_sans.setter
    def ip_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b7220ceba268fc2374ce0c1a25212205b4616b63b4f149e04a24915e7baca07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerRef")
    def issuer_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerRef"))

    @issuer_ref.setter
    def issuer_ref(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21b78600a3ce1e555db77377df3a5262b60a7ba1b68e57c19ea71a5b4eedbf5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerRef", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minSecondsRemaining")
    def min_seconds_remaining(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSecondsRemaining"))

    @min_seconds_remaining.setter
    def min_seconds_remaining(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fc4169f7b1c042724d41ba87312ac5a6b2b92d06304992cfc4502489bfe7f1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minSecondsRemaining", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69ff32c6e88fa152b8ee3c2b4c774a50546a936d44026c394ef3ac177e817344)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2011df7709dc7960f4c9e2cb994e131f84ac4b0ca81dda0446d865badde35e20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @not_after.setter
    def not_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5b6df6041a875f6c4a4bed23cb056fb9a55cdb36eff0474c81185a62c6c17b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="otherSans")
    def other_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "otherSans"))

    @other_sans.setter
    def other_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da08f7167a520d53d0177ec00e4254d28a96346ebe08f3b94079c2a3a112fb24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "otherSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c06bb5ab6e390d64fe5d2002c590d5ce028b17e8ebdc7e8808db39d53288195)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fd9ed3d69943da01e0b7d06135570938e81a0f098faf21e1edc595cff4471db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendSign.PkiSecretBackendSignConfig",
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
        "csr": "csr",
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
        "ttl": "ttl",
        "uri_sans": "uriSans",
    },
)
class PkiSecretBackendSignConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        csr: builtins.str,
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
        ttl: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#backend PkiSecretBackendSign#backend}
        :param common_name: CN of intermediate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#common_name PkiSecretBackendSign#common_name}
        :param csr: The CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#csr PkiSecretBackendSign#csr}
        :param name: Name of the role to create the certificate against. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#name PkiSecretBackendSign#name}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#alt_names PkiSecretBackendSign#alt_names}
        :param auto_renew: If enabled, a new certificate will be generated if the expiration is within min_seconds_remaining. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#auto_renew PkiSecretBackendSign#auto_renew}
        :param cert_metadata: A base 64 encoded value or an empty string to associate with the certificate's serial number. The role's no_store_metadata must be set to false, otherwise an error is returned when specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#cert_metadata PkiSecretBackendSign#cert_metadata}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#exclude_cn_from_sans PkiSecretBackendSign#exclude_cn_from_sans}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#format PkiSecretBackendSign#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#id PkiSecretBackendSign#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#ip_sans PkiSecretBackendSign#ip_sans}
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#issuer_ref PkiSecretBackendSign#issuer_ref}
        :param min_seconds_remaining: Generate a new certificate when the expiration is within this number of seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#min_seconds_remaining PkiSecretBackendSign#min_seconds_remaining}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#namespace PkiSecretBackendSign#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#not_after PkiSecretBackendSign#not_after}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#other_sans PkiSecretBackendSign#other_sans}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#ttl PkiSecretBackendSign#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#uri_sans PkiSecretBackendSign#uri_sans}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d75e2885e6c0b8a6c90ea4f5e1f555269347c311526fc898e9e65f35c44c7308)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument csr", value=csr, expected_type=type_hints["csr"])
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
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "common_name": common_name,
            "csr": csr,
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
        if ttl is not None:
            self._values["ttl"] = ttl
        if uri_sans is not None:
            self._values["uri_sans"] = uri_sans

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#backend PkiSecretBackendSign#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def common_name(self) -> builtins.str:
        '''CN of intermediate to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#common_name PkiSecretBackendSign#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def csr(self) -> builtins.str:
        '''The CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#csr PkiSecretBackendSign#csr}
        '''
        result = self._values.get("csr")
        assert result is not None, "Required property 'csr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the role to create the certificate against.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#name PkiSecretBackendSign#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alt_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#alt_names PkiSecretBackendSign#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auto_renew(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If enabled, a new certificate will be generated if the expiration is within min_seconds_remaining.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#auto_renew PkiSecretBackendSign#auto_renew}
        '''
        result = self._values.get("auto_renew")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cert_metadata(self) -> typing.Optional[builtins.str]:
        '''A base 64 encoded value or an empty string to associate with the certificate's serial number.

        The role's no_store_metadata must be set to false, otherwise an error is returned when specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#cert_metadata PkiSecretBackendSign#cert_metadata}
        '''
        result = self._values.get("cert_metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_cn_from_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to exclude CN from SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#exclude_cn_from_sans PkiSecretBackendSign#exclude_cn_from_sans}
        '''
        result = self._values.get("exclude_cn_from_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format of data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#format PkiSecretBackendSign#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#id PkiSecretBackendSign#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#ip_sans PkiSecretBackendSign#ip_sans}
        '''
        result = self._values.get("ip_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def issuer_ref(self) -> typing.Optional[builtins.str]:
        '''Specifies the default issuer of this request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#issuer_ref PkiSecretBackendSign#issuer_ref}
        '''
        result = self._values.get("issuer_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_seconds_remaining(self) -> typing.Optional[jsii.Number]:
        '''Generate a new certificate when the expiration is within this number of seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#min_seconds_remaining PkiSecretBackendSign#min_seconds_remaining}
        '''
        result = self._values.get("min_seconds_remaining")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#namespace PkiSecretBackendSign#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_after(self) -> typing.Optional[builtins.str]:
        '''Set the Not After field of the certificate with specified date value.

        The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#not_after PkiSecretBackendSign#not_after}
        '''
        result = self._values.get("not_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def other_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of other SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#other_sans PkiSecretBackendSign#other_sans}
        '''
        result = self._values.get("other_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Time to live.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#ttl PkiSecretBackendSign#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative URIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_sign#uri_sans PkiSecretBackendSign#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendSignConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendSign",
    "PkiSecretBackendSignConfig",
]

publication.publish()

def _typecheckingstub__8b41af669c3ca7e76924b5c5648cc4f62509f360ccc4e3ff1be53677afb47554(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    common_name: builtins.str,
    csr: builtins.str,
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
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__5bfadb60b5fd628618283aee52132735fa292cb205a00d52405ac47ffd07001a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__537f7b1bd98be981fb1b9d8ccbb0495bde864af7035aa458df3e6f1bd418cedf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4d1dcecd21edc8c4d290b2f978903f1f5ed3b8327d68e1c3563c177361e4941(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00e7460487ceeab305d478573f42d7d9971d118f8d7d456289e2010406c9a0b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c77167c9333d43b8534b533cf2a1657cc7b9aac10d8bc7e2c7d774383f223cde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3930a3031168e1674272de46f917624348eb443b5de5d7238f506bca9b64ad8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d380abb8a29c5f199c2c778b3534fb0ab9d6bf4cf3f7795b30e5b3e15127dad4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23581e99be7d6880243a465374929d58bcdfe1ce12d4d166f6e264e919d37d42(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__826178722e2336555d7f4a108ebfa8c919a84d194f5b582fd86dc494af395ab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83d6f3af20eff9dc79cf4c9f996bb6d9e81df64b8b12b265f417555b792250dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b7220ceba268fc2374ce0c1a25212205b4616b63b4f149e04a24915e7baca07(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21b78600a3ce1e555db77377df3a5262b60a7ba1b68e57c19ea71a5b4eedbf5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fc4169f7b1c042724d41ba87312ac5a6b2b92d06304992cfc4502489bfe7f1f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69ff32c6e88fa152b8ee3c2b4c774a50546a936d44026c394ef3ac177e817344(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2011df7709dc7960f4c9e2cb994e131f84ac4b0ca81dda0446d865badde35e20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5b6df6041a875f6c4a4bed23cb056fb9a55cdb36eff0474c81185a62c6c17b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da08f7167a520d53d0177ec00e4254d28a96346ebe08f3b94079c2a3a112fb24(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c06bb5ab6e390d64fe5d2002c590d5ce028b17e8ebdc7e8808db39d53288195(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fd9ed3d69943da01e0b7d06135570938e81a0f098faf21e1edc595cff4471db(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d75e2885e6c0b8a6c90ea4f5e1f555269347c311526fc898e9e65f35c44c7308(
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
    csr: builtins.str,
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
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
