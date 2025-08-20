r'''
# `vault_pki_secret_backend_root_cert`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_root_cert`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert).
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


class PkiSecretBackendRootCert(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRootCert.PkiSecretBackendRootCert",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert vault_pki_secret_backend_root_cert}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        common_name: builtins.str,
        type: builtins.str,
        alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        country: typing.Optional[builtins.str] = None,
        exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        excluded_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        issuer_name: typing.Optional[builtins.str] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_ref: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        managed_key_id: typing.Optional[builtins.str] = None,
        managed_key_name: typing.Optional[builtins.str] = None,
        max_path_length: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_after: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[builtins.str] = None,
        permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        postal_code: typing.Optional[builtins.str] = None,
        private_key_format: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        street_address: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert vault_pki_secret_backend_root_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#backend PkiSecretBackendRootCert#backend}
        :param common_name: CN of root to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#common_name PkiSecretBackendRootCert#common_name}
        :param type: Type of root to create. Must be either "existing", "exported", "internal" or "kms". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#type PkiSecretBackendRootCert#type}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#alt_names PkiSecretBackendRootCert#alt_names}
        :param country: The country. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#country PkiSecretBackendRootCert#country}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#exclude_cn_from_sans PkiSecretBackendRootCert#exclude_cn_from_sans}
        :param excluded_dns_domains: List of domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_dns_domains PkiSecretBackendRootCert#excluded_dns_domains}
        :param excluded_email_addresses: List of email addresses for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_email_addresses PkiSecretBackendRootCert#excluded_email_addresses}
        :param excluded_ip_ranges: List of IP ranges for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_ip_ranges PkiSecretBackendRootCert#excluded_ip_ranges}
        :param excluded_uri_domains: List of URI domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_uri_domains PkiSecretBackendRootCert#excluded_uri_domains}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#format PkiSecretBackendRootCert#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#id PkiSecretBackendRootCert#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ip_sans PkiSecretBackendRootCert#ip_sans}
        :param issuer_name: Provides a name to the specified issuer. The name must be unique across all issuers and not be the reserved value 'default'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#issuer_name PkiSecretBackendRootCert#issuer_name}
        :param key_bits: The number of bits to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_bits PkiSecretBackendRootCert#key_bits}
        :param key_name: When a new key is created with this request, optionally specifies the name for this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_name PkiSecretBackendRootCert#key_name}
        :param key_ref: Specifies the key to use for generating this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_ref PkiSecretBackendRootCert#key_ref}
        :param key_type: The desired key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_type PkiSecretBackendRootCert#key_type}
        :param locality: The locality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#locality PkiSecretBackendRootCert#locality}
        :param managed_key_id: The ID of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#managed_key_id PkiSecretBackendRootCert#managed_key_id}
        :param managed_key_name: The name of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#managed_key_name PkiSecretBackendRootCert#managed_key_name}
        :param max_path_length: The maximum path length to encode in the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#max_path_length PkiSecretBackendRootCert#max_path_length}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#namespace PkiSecretBackendRootCert#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#not_after PkiSecretBackendRootCert#not_after}
        :param organization: The organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#organization PkiSecretBackendRootCert#organization}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#other_sans PkiSecretBackendRootCert#other_sans}
        :param ou: The organization unit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ou PkiSecretBackendRootCert#ou}
        :param permitted_dns_domains: List of domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_dns_domains PkiSecretBackendRootCert#permitted_dns_domains}
        :param permitted_email_addresses: List of email addresses for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_email_addresses PkiSecretBackendRootCert#permitted_email_addresses}
        :param permitted_ip_ranges: List of IP ranges for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_ip_ranges PkiSecretBackendRootCert#permitted_ip_ranges}
        :param permitted_uri_domains: List of URI domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_uri_domains PkiSecretBackendRootCert#permitted_uri_domains}
        :param postal_code: The postal code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#postal_code PkiSecretBackendRootCert#postal_code}
        :param private_key_format: The private key format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#private_key_format PkiSecretBackendRootCert#private_key_format}
        :param province: The province. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#province PkiSecretBackendRootCert#province}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#signature_bits PkiSecretBackendRootCert#signature_bits}
        :param street_address: The street address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#street_address PkiSecretBackendRootCert#street_address}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ttl PkiSecretBackendRootCert#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#uri_sans PkiSecretBackendRootCert#uri_sans}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7711bd6d6b2f8bdd134b0c86e9ee2df29818a46cf540ac0c9c87e498e72f92e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendRootCertConfig(
            backend=backend,
            common_name=common_name,
            type=type,
            alt_names=alt_names,
            country=country,
            exclude_cn_from_sans=exclude_cn_from_sans,
            excluded_dns_domains=excluded_dns_domains,
            excluded_email_addresses=excluded_email_addresses,
            excluded_ip_ranges=excluded_ip_ranges,
            excluded_uri_domains=excluded_uri_domains,
            format=format,
            id=id,
            ip_sans=ip_sans,
            issuer_name=issuer_name,
            key_bits=key_bits,
            key_name=key_name,
            key_ref=key_ref,
            key_type=key_type,
            locality=locality,
            managed_key_id=managed_key_id,
            managed_key_name=managed_key_name,
            max_path_length=max_path_length,
            namespace=namespace,
            not_after=not_after,
            organization=organization,
            other_sans=other_sans,
            ou=ou,
            permitted_dns_domains=permitted_dns_domains,
            permitted_email_addresses=permitted_email_addresses,
            permitted_ip_ranges=permitted_ip_ranges,
            permitted_uri_domains=permitted_uri_domains,
            postal_code=postal_code,
            private_key_format=private_key_format,
            province=province,
            signature_bits=signature_bits,
            street_address=street_address,
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
        '''Generates CDKTF code for importing a PkiSecretBackendRootCert resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendRootCert to import.
        :param import_from_id: The id of the existing PkiSecretBackendRootCert that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendRootCert to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba3afc76a90e12fe3678185629046b9e973b46a4ed88a9071ec0008da368f9d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAltNames")
    def reset_alt_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAltNames", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetExcludeCnFromSans")
    def reset_exclude_cn_from_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeCnFromSans", []))

    @jsii.member(jsii_name="resetExcludedDnsDomains")
    def reset_excluded_dns_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedDnsDomains", []))

    @jsii.member(jsii_name="resetExcludedEmailAddresses")
    def reset_excluded_email_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedEmailAddresses", []))

    @jsii.member(jsii_name="resetExcludedIpRanges")
    def reset_excluded_ip_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedIpRanges", []))

    @jsii.member(jsii_name="resetExcludedUriDomains")
    def reset_excluded_uri_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludedUriDomains", []))

    @jsii.member(jsii_name="resetFormat")
    def reset_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormat", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpSans")
    def reset_ip_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpSans", []))

    @jsii.member(jsii_name="resetIssuerName")
    def reset_issuer_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuerName", []))

    @jsii.member(jsii_name="resetKeyBits")
    def reset_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyBits", []))

    @jsii.member(jsii_name="resetKeyName")
    def reset_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyName", []))

    @jsii.member(jsii_name="resetKeyRef")
    def reset_key_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyRef", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetManagedKeyId")
    def reset_managed_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedKeyId", []))

    @jsii.member(jsii_name="resetManagedKeyName")
    def reset_managed_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedKeyName", []))

    @jsii.member(jsii_name="resetMaxPathLength")
    def reset_max_path_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPathLength", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNotAfter")
    def reset_not_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotAfter", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetOtherSans")
    def reset_other_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOtherSans", []))

    @jsii.member(jsii_name="resetOu")
    def reset_ou(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOu", []))

    @jsii.member(jsii_name="resetPermittedDnsDomains")
    def reset_permitted_dns_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermittedDnsDomains", []))

    @jsii.member(jsii_name="resetPermittedEmailAddresses")
    def reset_permitted_email_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermittedEmailAddresses", []))

    @jsii.member(jsii_name="resetPermittedIpRanges")
    def reset_permitted_ip_ranges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermittedIpRanges", []))

    @jsii.member(jsii_name="resetPermittedUriDomains")
    def reset_permitted_uri_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermittedUriDomains", []))

    @jsii.member(jsii_name="resetPostalCode")
    def reset_postal_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostalCode", []))

    @jsii.member(jsii_name="resetPrivateKeyFormat")
    def reset_private_key_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyFormat", []))

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetSignatureBits")
    def reset_signature_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureBits", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

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
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @builtins.property
    @jsii.member(jsii_name="issuerId")
    def issuer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerId"))

    @builtins.property
    @jsii.member(jsii_name="issuingCa")
    def issuing_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuingCa"))

    @builtins.property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @builtins.property
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @builtins.property
    @jsii.member(jsii_name="altNamesInput")
    def alt_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "altNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeCnFromSansInput")
    def exclude_cn_from_sans_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeCnFromSansInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedDnsDomainsInput")
    def excluded_dns_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedDnsDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedEmailAddressesInput")
    def excluded_email_addresses_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedEmailAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedIpRangesInput")
    def excluded_ip_ranges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedIpRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="excludedUriDomainsInput")
    def excluded_uri_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludedUriDomainsInput"))

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
    @jsii.member(jsii_name="issuerNameInput")
    def issuer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="keyBitsInput")
    def key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyNameInput")
    def key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="keyRefInput")
    def key_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyRefInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localityInput"))

    @builtins.property
    @jsii.member(jsii_name="managedKeyIdInput")
    def managed_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="managedKeyNameInput")
    def managed_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPathLengthInput")
    def max_path_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPathLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="notAfterInput")
    def not_after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property
    @jsii.member(jsii_name="otherSansInput")
    def other_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "otherSansInput"))

    @builtins.property
    @jsii.member(jsii_name="ouInput")
    def ou_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ouInput"))

    @builtins.property
    @jsii.member(jsii_name="permittedDnsDomainsInput")
    def permitted_dns_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "permittedDnsDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="permittedEmailAddressesInput")
    def permitted_email_addresses_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "permittedEmailAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="permittedIpRangesInput")
    def permitted_ip_ranges_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "permittedIpRangesInput"))

    @builtins.property
    @jsii.member(jsii_name="permittedUriDomainsInput")
    def permitted_uri_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "permittedUriDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="postalCodeInput")
    def postal_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postalCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyFormatInput")
    def private_key_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provinceInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureBitsInput")
    def signature_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "signatureBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streetAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__17653c42aceadf7901bb3ed3d6f81fbb580877e4649338a3df65131257ebcaa6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__370f4d6b8a5ea2cae17476d20a19098488ecc82fc96f5424197b9e591ed74873)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b729fcef07bbf0ce3381c30f9bc4524c3f9f4554434320f8daa6c43eef213063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a81411fbb7cdc429494aedb48c9b71d5a0fa4ae68c1c29a3d48afdc9e4a7acc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "country", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__5f18a5e3d5d32196d26829d741506777f721c5534b8f603a52b34e0aaa213b6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeCnFromSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedDnsDomains")
    def excluded_dns_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedDnsDomains"))

    @excluded_dns_domains.setter
    def excluded_dns_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__808e8f67fd7c80724a921a40a3e807a8d44388a1b6ee965ef7dc3b07fe176948)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedDnsDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedEmailAddresses")
    def excluded_email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedEmailAddresses"))

    @excluded_email_addresses.setter
    def excluded_email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91a2c00589e9404457b7c477bf417219a6fbe1be01c7ad812d66e02766086767)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedEmailAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedIpRanges")
    def excluded_ip_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedIpRanges"))

    @excluded_ip_ranges.setter
    def excluded_ip_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0981150f774af6f6cf377a3860c5feddb6cf3aad4df97f7a68eea5a2f08e360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedIpRanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedUriDomains")
    def excluded_uri_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedUriDomains"))

    @excluded_uri_domains.setter
    def excluded_uri_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50d8baa3bb4d126562eeb00076fbfc43c1d9d562214628702b333847b6222caf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedUriDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d9baa7b9aceb5d38af7d42cc1a04400b1400bbd17b0aafc8f5ceb14ebeae633)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ca1a78abd92e87dc31df72a621ec6e5a60a3d14b6ae69a9153310395434a942)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipSans")
    def ip_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipSans"))

    @ip_sans.setter
    def ip_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9604a1e07399f6e84b396c3e4cf00267f897dfd80061a35d4547c719408487a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerName")
    def issuer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerName"))

    @issuer_name.setter
    def issuer_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36f9efc0216138c04c73b87386bc0d1697f30cab92cdd6154bda285a08295080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyBits")
    def key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyBits"))

    @key_bits.setter
    def key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d300717c691910c32c3d139960e9ff543a558e11842919da7dea05d84a51da9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyName")
    def key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyName"))

    @key_name.setter
    def key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b88f7a19e320d5d383372c32bf569f9bbeff9819d59cc3c4b76d32982a9467ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyRef")
    def key_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyRef"))

    @key_ref.setter
    def key_ref(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__396daa92090a4add7c39a8f1f0e9510560aae04e819d10f469de74a626c82e3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyRef", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d8069beda62513aee17ffdf27b99adce475f8ba3c5a1193a26dc357ec631a3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="locality")
    def locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55b7b8743d3a9fd8f452721c40bfaa16fae4733d3fbd9e6bd29a33e25b52502c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locality", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedKeyId")
    def managed_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedKeyId"))

    @managed_key_id.setter
    def managed_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a50accf936b6d3257c001e65e2e000dd977bcc8044aa551086891d5d0d469aba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedKeyName")
    def managed_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedKeyName"))

    @managed_key_name.setter
    def managed_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ee6fdfbe66eeada057154e27ed35834e1c2e9f5e00485d6a1519b97d00bfd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedKeyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPathLength")
    def max_path_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPathLength"))

    @max_path_length.setter
    def max_path_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2559868a4d4c7f9d9868e3a02a0b49b0025ee201df769bf06b73c228aae78197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPathLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee1c133d495cfd445c36b2bc00d8431d4bdefb6736e442a52a342aabac995ae2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @not_after.setter
    def not_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52b4f882e86cc7926e807a9320710b43536ef2ed0ac7a87eeccf860867472795)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80aa9360873fdcf9814547d1c50a83a8ffe53ec030ca65b74fb58dc0512ce340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="otherSans")
    def other_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "otherSans"))

    @other_sans.setter
    def other_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d283988fb50ee306d991fb376ac4a6e3a6eb3798d3fc49b593154161e75f8052)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "otherSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ou")
    def ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ou"))

    @ou.setter
    def ou(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__788cf0db4a2a3a7dd9ca36012387da69750abc9b30fb0a187b325849b65c989c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ou", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedDnsDomains")
    def permitted_dns_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedDnsDomains"))

    @permitted_dns_domains.setter
    def permitted_dns_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1c295d07019914cbf50bfde0fce70224bd8fd9da5c958276a5d0d129777012e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedDnsDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedEmailAddresses")
    def permitted_email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedEmailAddresses"))

    @permitted_email_addresses.setter
    def permitted_email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62407f80543ba013370e85d4e4114a27a7054298ac26ddcfceb9d5dddeace169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedEmailAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedIpRanges")
    def permitted_ip_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedIpRanges"))

    @permitted_ip_ranges.setter
    def permitted_ip_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34cfaeb3867d06af7ec4069c1601c13445ca98cdca21218878181c142d6ef7f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedIpRanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedUriDomains")
    def permitted_uri_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedUriDomains"))

    @permitted_uri_domains.setter
    def permitted_uri_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__194cd982696c62da9529dee22eb6f468ce780592711875e50ab8aa26742e58d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedUriDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab6841bf9414dde1f520e595577e265799c68ffa202e137118f56df161de7a65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postalCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyFormat")
    def private_key_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyFormat"))

    @private_key_format.setter
    def private_key_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb51eb91a4d3758d10f7ae4f10191a194315e50397947e06b00264088fc54dc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="province")
    def province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "province"))

    @province.setter
    def province(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3b7d22111b35987e36495c82f1ff9e953c75aa7db4f55ca01f926835dca17f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "province", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureBits")
    def signature_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "signatureBits"))

    @signature_bits.setter
    def signature_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e12e0304065f99a72712a1242cf40911c9dbd5eeae2384e22364e57c1884c68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d304fa2e3547824a199dc392d0e873863ec72d97844273c23b111ed55dc15c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "streetAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dafbe7f72bf0bfa091da8c37636d1a246f0d68530e4c0d1ff61a0e1c01f4d3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fbc0b9ff5a219f044a9b2ab237e1d728abc0221e7940b1a2164f8325a220975)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__052e2d65bd91fad46a5a24f03d1c7ec4f865a057a799170ef698b036df09fcf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRootCert.PkiSecretBackendRootCertConfig",
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
        "type": "type",
        "alt_names": "altNames",
        "country": "country",
        "exclude_cn_from_sans": "excludeCnFromSans",
        "excluded_dns_domains": "excludedDnsDomains",
        "excluded_email_addresses": "excludedEmailAddresses",
        "excluded_ip_ranges": "excludedIpRanges",
        "excluded_uri_domains": "excludedUriDomains",
        "format": "format",
        "id": "id",
        "ip_sans": "ipSans",
        "issuer_name": "issuerName",
        "key_bits": "keyBits",
        "key_name": "keyName",
        "key_ref": "keyRef",
        "key_type": "keyType",
        "locality": "locality",
        "managed_key_id": "managedKeyId",
        "managed_key_name": "managedKeyName",
        "max_path_length": "maxPathLength",
        "namespace": "namespace",
        "not_after": "notAfter",
        "organization": "organization",
        "other_sans": "otherSans",
        "ou": "ou",
        "permitted_dns_domains": "permittedDnsDomains",
        "permitted_email_addresses": "permittedEmailAddresses",
        "permitted_ip_ranges": "permittedIpRanges",
        "permitted_uri_domains": "permittedUriDomains",
        "postal_code": "postalCode",
        "private_key_format": "privateKeyFormat",
        "province": "province",
        "signature_bits": "signatureBits",
        "street_address": "streetAddress",
        "ttl": "ttl",
        "uri_sans": "uriSans",
    },
)
class PkiSecretBackendRootCertConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        type: builtins.str,
        alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        country: typing.Optional[builtins.str] = None,
        exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        excluded_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        excluded_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        issuer_name: typing.Optional[builtins.str] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_ref: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        managed_key_id: typing.Optional[builtins.str] = None,
        managed_key_name: typing.Optional[builtins.str] = None,
        max_path_length: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_after: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[builtins.str] = None,
        permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        postal_code: typing.Optional[builtins.str] = None,
        private_key_format: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        street_address: typing.Optional[builtins.str] = None,
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
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#backend PkiSecretBackendRootCert#backend}
        :param common_name: CN of root to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#common_name PkiSecretBackendRootCert#common_name}
        :param type: Type of root to create. Must be either "existing", "exported", "internal" or "kms". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#type PkiSecretBackendRootCert#type}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#alt_names PkiSecretBackendRootCert#alt_names}
        :param country: The country. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#country PkiSecretBackendRootCert#country}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#exclude_cn_from_sans PkiSecretBackendRootCert#exclude_cn_from_sans}
        :param excluded_dns_domains: List of domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_dns_domains PkiSecretBackendRootCert#excluded_dns_domains}
        :param excluded_email_addresses: List of email addresses for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_email_addresses PkiSecretBackendRootCert#excluded_email_addresses}
        :param excluded_ip_ranges: List of IP ranges for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_ip_ranges PkiSecretBackendRootCert#excluded_ip_ranges}
        :param excluded_uri_domains: List of URI domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_uri_domains PkiSecretBackendRootCert#excluded_uri_domains}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#format PkiSecretBackendRootCert#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#id PkiSecretBackendRootCert#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ip_sans PkiSecretBackendRootCert#ip_sans}
        :param issuer_name: Provides a name to the specified issuer. The name must be unique across all issuers and not be the reserved value 'default'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#issuer_name PkiSecretBackendRootCert#issuer_name}
        :param key_bits: The number of bits to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_bits PkiSecretBackendRootCert#key_bits}
        :param key_name: When a new key is created with this request, optionally specifies the name for this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_name PkiSecretBackendRootCert#key_name}
        :param key_ref: Specifies the key to use for generating this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_ref PkiSecretBackendRootCert#key_ref}
        :param key_type: The desired key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_type PkiSecretBackendRootCert#key_type}
        :param locality: The locality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#locality PkiSecretBackendRootCert#locality}
        :param managed_key_id: The ID of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#managed_key_id PkiSecretBackendRootCert#managed_key_id}
        :param managed_key_name: The name of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#managed_key_name PkiSecretBackendRootCert#managed_key_name}
        :param max_path_length: The maximum path length to encode in the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#max_path_length PkiSecretBackendRootCert#max_path_length}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#namespace PkiSecretBackendRootCert#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#not_after PkiSecretBackendRootCert#not_after}
        :param organization: The organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#organization PkiSecretBackendRootCert#organization}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#other_sans PkiSecretBackendRootCert#other_sans}
        :param ou: The organization unit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ou PkiSecretBackendRootCert#ou}
        :param permitted_dns_domains: List of domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_dns_domains PkiSecretBackendRootCert#permitted_dns_domains}
        :param permitted_email_addresses: List of email addresses for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_email_addresses PkiSecretBackendRootCert#permitted_email_addresses}
        :param permitted_ip_ranges: List of IP ranges for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_ip_ranges PkiSecretBackendRootCert#permitted_ip_ranges}
        :param permitted_uri_domains: List of URI domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_uri_domains PkiSecretBackendRootCert#permitted_uri_domains}
        :param postal_code: The postal code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#postal_code PkiSecretBackendRootCert#postal_code}
        :param private_key_format: The private key format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#private_key_format PkiSecretBackendRootCert#private_key_format}
        :param province: The province. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#province PkiSecretBackendRootCert#province}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#signature_bits PkiSecretBackendRootCert#signature_bits}
        :param street_address: The street address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#street_address PkiSecretBackendRootCert#street_address}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ttl PkiSecretBackendRootCert#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#uri_sans PkiSecretBackendRootCert#uri_sans}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3a028bd2c0f9a3bad24a0637e08c77cb762ca7d322377cdb54d266daa055682)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument alt_names", value=alt_names, expected_type=type_hints["alt_names"])
            check_type(argname="argument country", value=country, expected_type=type_hints["country"])
            check_type(argname="argument exclude_cn_from_sans", value=exclude_cn_from_sans, expected_type=type_hints["exclude_cn_from_sans"])
            check_type(argname="argument excluded_dns_domains", value=excluded_dns_domains, expected_type=type_hints["excluded_dns_domains"])
            check_type(argname="argument excluded_email_addresses", value=excluded_email_addresses, expected_type=type_hints["excluded_email_addresses"])
            check_type(argname="argument excluded_ip_ranges", value=excluded_ip_ranges, expected_type=type_hints["excluded_ip_ranges"])
            check_type(argname="argument excluded_uri_domains", value=excluded_uri_domains, expected_type=type_hints["excluded_uri_domains"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_sans", value=ip_sans, expected_type=type_hints["ip_sans"])
            check_type(argname="argument issuer_name", value=issuer_name, expected_type=type_hints["issuer_name"])
            check_type(argname="argument key_bits", value=key_bits, expected_type=type_hints["key_bits"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument key_ref", value=key_ref, expected_type=type_hints["key_ref"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument locality", value=locality, expected_type=type_hints["locality"])
            check_type(argname="argument managed_key_id", value=managed_key_id, expected_type=type_hints["managed_key_id"])
            check_type(argname="argument managed_key_name", value=managed_key_name, expected_type=type_hints["managed_key_name"])
            check_type(argname="argument max_path_length", value=max_path_length, expected_type=type_hints["max_path_length"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument not_after", value=not_after, expected_type=type_hints["not_after"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
            check_type(argname="argument other_sans", value=other_sans, expected_type=type_hints["other_sans"])
            check_type(argname="argument ou", value=ou, expected_type=type_hints["ou"])
            check_type(argname="argument permitted_dns_domains", value=permitted_dns_domains, expected_type=type_hints["permitted_dns_domains"])
            check_type(argname="argument permitted_email_addresses", value=permitted_email_addresses, expected_type=type_hints["permitted_email_addresses"])
            check_type(argname="argument permitted_ip_ranges", value=permitted_ip_ranges, expected_type=type_hints["permitted_ip_ranges"])
            check_type(argname="argument permitted_uri_domains", value=permitted_uri_domains, expected_type=type_hints["permitted_uri_domains"])
            check_type(argname="argument postal_code", value=postal_code, expected_type=type_hints["postal_code"])
            check_type(argname="argument private_key_format", value=private_key_format, expected_type=type_hints["private_key_format"])
            check_type(argname="argument province", value=province, expected_type=type_hints["province"])
            check_type(argname="argument signature_bits", value=signature_bits, expected_type=type_hints["signature_bits"])
            check_type(argname="argument street_address", value=street_address, expected_type=type_hints["street_address"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "common_name": common_name,
            "type": type,
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
        if country is not None:
            self._values["country"] = country
        if exclude_cn_from_sans is not None:
            self._values["exclude_cn_from_sans"] = exclude_cn_from_sans
        if excluded_dns_domains is not None:
            self._values["excluded_dns_domains"] = excluded_dns_domains
        if excluded_email_addresses is not None:
            self._values["excluded_email_addresses"] = excluded_email_addresses
        if excluded_ip_ranges is not None:
            self._values["excluded_ip_ranges"] = excluded_ip_ranges
        if excluded_uri_domains is not None:
            self._values["excluded_uri_domains"] = excluded_uri_domains
        if format is not None:
            self._values["format"] = format
        if id is not None:
            self._values["id"] = id
        if ip_sans is not None:
            self._values["ip_sans"] = ip_sans
        if issuer_name is not None:
            self._values["issuer_name"] = issuer_name
        if key_bits is not None:
            self._values["key_bits"] = key_bits
        if key_name is not None:
            self._values["key_name"] = key_name
        if key_ref is not None:
            self._values["key_ref"] = key_ref
        if key_type is not None:
            self._values["key_type"] = key_type
        if locality is not None:
            self._values["locality"] = locality
        if managed_key_id is not None:
            self._values["managed_key_id"] = managed_key_id
        if managed_key_name is not None:
            self._values["managed_key_name"] = managed_key_name
        if max_path_length is not None:
            self._values["max_path_length"] = max_path_length
        if namespace is not None:
            self._values["namespace"] = namespace
        if not_after is not None:
            self._values["not_after"] = not_after
        if organization is not None:
            self._values["organization"] = organization
        if other_sans is not None:
            self._values["other_sans"] = other_sans
        if ou is not None:
            self._values["ou"] = ou
        if permitted_dns_domains is not None:
            self._values["permitted_dns_domains"] = permitted_dns_domains
        if permitted_email_addresses is not None:
            self._values["permitted_email_addresses"] = permitted_email_addresses
        if permitted_ip_ranges is not None:
            self._values["permitted_ip_ranges"] = permitted_ip_ranges
        if permitted_uri_domains is not None:
            self._values["permitted_uri_domains"] = permitted_uri_domains
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if private_key_format is not None:
            self._values["private_key_format"] = private_key_format
        if province is not None:
            self._values["province"] = province
        if signature_bits is not None:
            self._values["signature_bits"] = signature_bits
        if street_address is not None:
            self._values["street_address"] = street_address
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#backend PkiSecretBackendRootCert#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def common_name(self) -> builtins.str:
        '''CN of root to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#common_name PkiSecretBackendRootCert#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Type of root to create. Must be either "existing", "exported", "internal" or "kms".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#type PkiSecretBackendRootCert#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alt_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#alt_names PkiSecretBackendRootCert#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''The country.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#country PkiSecretBackendRootCert#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_cn_from_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to exclude CN from SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#exclude_cn_from_sans PkiSecretBackendRootCert#exclude_cn_from_sans}
        '''
        result = self._values.get("exclude_cn_from_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def excluded_dns_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of domains for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_dns_domains PkiSecretBackendRootCert#excluded_dns_domains}
        '''
        result = self._values.get("excluded_dns_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of email addresses for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_email_addresses PkiSecretBackendRootCert#excluded_email_addresses}
        '''
        result = self._values.get("excluded_email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_ip_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP ranges for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_ip_ranges PkiSecretBackendRootCert#excluded_ip_ranges}
        '''
        result = self._values.get("excluded_ip_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_uri_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URI domains for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#excluded_uri_domains PkiSecretBackendRootCert#excluded_uri_domains}
        '''
        result = self._values.get("excluded_uri_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format of data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#format PkiSecretBackendRootCert#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#id PkiSecretBackendRootCert#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ip_sans PkiSecretBackendRootCert#ip_sans}
        '''
        result = self._values.get("ip_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def issuer_name(self) -> typing.Optional[builtins.str]:
        '''Provides a name to the specified issuer.

        The name must be unique across all issuers and not be the reserved value 'default'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#issuer_name PkiSecretBackendRootCert#issuer_name}
        '''
        result = self._values.get("issuer_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_bits PkiSecretBackendRootCert#key_bits}
        '''
        result = self._values.get("key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''When a new key is created with this request, optionally specifies the name for this.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_name PkiSecretBackendRootCert#key_name}
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_ref(self) -> typing.Optional[builtins.str]:
        '''Specifies the key to use for generating this request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_ref PkiSecretBackendRootCert#key_ref}
        '''
        result = self._values.get("key_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''The desired key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#key_type PkiSecretBackendRootCert#key_type}
        '''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''The locality.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#locality PkiSecretBackendRootCert#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_key_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the previously configured managed key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#managed_key_id PkiSecretBackendRootCert#managed_key_id}
        '''
        result = self._values.get("managed_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_key_name(self) -> typing.Optional[builtins.str]:
        '''The name of the previously configured managed key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#managed_key_name PkiSecretBackendRootCert#managed_key_name}
        '''
        result = self._values.get("managed_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_path_length(self) -> typing.Optional[jsii.Number]:
        '''The maximum path length to encode in the generated certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#max_path_length PkiSecretBackendRootCert#max_path_length}
        '''
        result = self._values.get("max_path_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#namespace PkiSecretBackendRootCert#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_after(self) -> typing.Optional[builtins.str]:
        '''Set the Not After field of the certificate with specified date value.

        The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#not_after PkiSecretBackendRootCert#not_after}
        '''
        result = self._values.get("not_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''The organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#organization PkiSecretBackendRootCert#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def other_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of other SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#other_sans PkiSecretBackendRootCert#other_sans}
        '''
        result = self._values.get("other_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ou(self) -> typing.Optional[builtins.str]:
        '''The organization unit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ou PkiSecretBackendRootCert#ou}
        '''
        result = self._values.get("ou")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permitted_dns_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of domains for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_dns_domains PkiSecretBackendRootCert#permitted_dns_domains}
        '''
        result = self._values.get("permitted_dns_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permitted_email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of email addresses for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_email_addresses PkiSecretBackendRootCert#permitted_email_addresses}
        '''
        result = self._values.get("permitted_email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permitted_ip_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP ranges for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_ip_ranges PkiSecretBackendRootCert#permitted_ip_ranges}
        '''
        result = self._values.get("permitted_ip_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permitted_uri_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URI domains for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#permitted_uri_domains PkiSecretBackendRootCert#permitted_uri_domains}
        '''
        result = self._values.get("permitted_uri_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''The postal code.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#postal_code PkiSecretBackendRootCert#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_format(self) -> typing.Optional[builtins.str]:
        '''The private key format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#private_key_format PkiSecretBackendRootCert#private_key_format}
        '''
        result = self._values.get("private_key_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''The province.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#province PkiSecretBackendRootCert#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits to use in the signature algorithm.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#signature_bits PkiSecretBackendRootCert#signature_bits}
        '''
        result = self._values.get("signature_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def street_address(self) -> typing.Optional[builtins.str]:
        '''The street address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#street_address PkiSecretBackendRootCert#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Time to live.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#ttl PkiSecretBackendRootCert#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative URIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_cert#uri_sans PkiSecretBackendRootCert#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendRootCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendRootCert",
    "PkiSecretBackendRootCertConfig",
]

publication.publish()

def _typecheckingstub__7711bd6d6b2f8bdd134b0c86e9ee2df29818a46cf540ac0c9c87e498e72f92e8(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    common_name: builtins.str,
    type: builtins.str,
    alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    country: typing.Optional[builtins.str] = None,
    exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    excluded_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    issuer_name: typing.Optional[builtins.str] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_ref: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    locality: typing.Optional[builtins.str] = None,
    managed_key_id: typing.Optional[builtins.str] = None,
    managed_key_name: typing.Optional[builtins.str] = None,
    max_path_length: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_after: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[builtins.str] = None,
    permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    postal_code: typing.Optional[builtins.str] = None,
    private_key_format: typing.Optional[builtins.str] = None,
    province: typing.Optional[builtins.str] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    street_address: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__ba3afc76a90e12fe3678185629046b9e973b46a4ed88a9071ec0008da368f9d5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17653c42aceadf7901bb3ed3d6f81fbb580877e4649338a3df65131257ebcaa6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__370f4d6b8a5ea2cae17476d20a19098488ecc82fc96f5424197b9e591ed74873(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b729fcef07bbf0ce3381c30f9bc4524c3f9f4554434320f8daa6c43eef213063(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a81411fbb7cdc429494aedb48c9b71d5a0fa4ae68c1c29a3d48afdc9e4a7acc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f18a5e3d5d32196d26829d741506777f721c5534b8f603a52b34e0aaa213b6d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__808e8f67fd7c80724a921a40a3e807a8d44388a1b6ee965ef7dc3b07fe176948(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a2c00589e9404457b7c477bf417219a6fbe1be01c7ad812d66e02766086767(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0981150f774af6f6cf377a3860c5feddb6cf3aad4df97f7a68eea5a2f08e360(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50d8baa3bb4d126562eeb00076fbfc43c1d9d562214628702b333847b6222caf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d9baa7b9aceb5d38af7d42cc1a04400b1400bbd17b0aafc8f5ceb14ebeae633(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ca1a78abd92e87dc31df72a621ec6e5a60a3d14b6ae69a9153310395434a942(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9604a1e07399f6e84b396c3e4cf00267f897dfd80061a35d4547c719408487a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36f9efc0216138c04c73b87386bc0d1697f30cab92cdd6154bda285a08295080(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d300717c691910c32c3d139960e9ff543a558e11842919da7dea05d84a51da9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b88f7a19e320d5d383372c32bf569f9bbeff9819d59cc3c4b76d32982a9467ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__396daa92090a4add7c39a8f1f0e9510560aae04e819d10f469de74a626c82e3a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d8069beda62513aee17ffdf27b99adce475f8ba3c5a1193a26dc357ec631a3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55b7b8743d3a9fd8f452721c40bfaa16fae4733d3fbd9e6bd29a33e25b52502c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a50accf936b6d3257c001e65e2e000dd977bcc8044aa551086891d5d0d469aba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ee6fdfbe66eeada057154e27ed35834e1c2e9f5e00485d6a1519b97d00bfd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2559868a4d4c7f9d9868e3a02a0b49b0025ee201df769bf06b73c228aae78197(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee1c133d495cfd445c36b2bc00d8431d4bdefb6736e442a52a342aabac995ae2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b4f882e86cc7926e807a9320710b43536ef2ed0ac7a87eeccf860867472795(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80aa9360873fdcf9814547d1c50a83a8ffe53ec030ca65b74fb58dc0512ce340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d283988fb50ee306d991fb376ac4a6e3a6eb3798d3fc49b593154161e75f8052(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__788cf0db4a2a3a7dd9ca36012387da69750abc9b30fb0a187b325849b65c989c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1c295d07019914cbf50bfde0fce70224bd8fd9da5c958276a5d0d129777012e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62407f80543ba013370e85d4e4114a27a7054298ac26ddcfceb9d5dddeace169(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34cfaeb3867d06af7ec4069c1601c13445ca98cdca21218878181c142d6ef7f6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__194cd982696c62da9529dee22eb6f468ce780592711875e50ab8aa26742e58d9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab6841bf9414dde1f520e595577e265799c68ffa202e137118f56df161de7a65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb51eb91a4d3758d10f7ae4f10191a194315e50397947e06b00264088fc54dc6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3b7d22111b35987e36495c82f1ff9e953c75aa7db4f55ca01f926835dca17f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e12e0304065f99a72712a1242cf40911c9dbd5eeae2384e22364e57c1884c68(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d304fa2e3547824a199dc392d0e873863ec72d97844273c23b111ed55dc15c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dafbe7f72bf0bfa091da8c37636d1a246f0d68530e4c0d1ff61a0e1c01f4d3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fbc0b9ff5a219f044a9b2ab237e1d728abc0221e7940b1a2164f8325a220975(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__052e2d65bd91fad46a5a24f03d1c7ec4f865a057a799170ef698b036df09fcf4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3a028bd2c0f9a3bad24a0637e08c77cb762ca7d322377cdb54d266daa055682(
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
    type: builtins.str,
    alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    country: typing.Optional[builtins.str] = None,
    exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    excluded_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    excluded_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    issuer_name: typing.Optional[builtins.str] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_ref: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    locality: typing.Optional[builtins.str] = None,
    managed_key_id: typing.Optional[builtins.str] = None,
    managed_key_name: typing.Optional[builtins.str] = None,
    max_path_length: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_after: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[builtins.str] = None,
    permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    postal_code: typing.Optional[builtins.str] = None,
    private_key_format: typing.Optional[builtins.str] = None,
    province: typing.Optional[builtins.str] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    street_address: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
