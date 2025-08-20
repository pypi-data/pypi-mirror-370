r'''
# `vault_pki_secret_backend_root_sign_intermediate`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_root_sign_intermediate`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate).
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


class PkiSecretBackendRootSignIntermediate(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRootSignIntermediate.PkiSecretBackendRootSignIntermediate",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate vault_pki_secret_backend_root_sign_intermediate}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        common_name: builtins.str,
        csr: builtins.str,
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
        issuer_ref: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        locality: typing.Optional[builtins.str] = None,
        max_path_length: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_after: typing.Optional[builtins.str] = None,
        not_before_duration: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[builtins.str] = None,
        permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        skid: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        use_csr_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_pss: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate vault_pki_secret_backend_root_sign_intermediate} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#backend PkiSecretBackendRootSignIntermediate#backend}
        :param common_name: CN of intermediate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#common_name PkiSecretBackendRootSignIntermediate#common_name}
        :param csr: The CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#csr PkiSecretBackendRootSignIntermediate#csr}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#alt_names PkiSecretBackendRootSignIntermediate#alt_names}
        :param country: The country. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#country PkiSecretBackendRootSignIntermediate#country}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#exclude_cn_from_sans PkiSecretBackendRootSignIntermediate#exclude_cn_from_sans}
        :param excluded_dns_domains: List of domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_dns_domains PkiSecretBackendRootSignIntermediate#excluded_dns_domains}
        :param excluded_email_addresses: List of email addresses for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_email_addresses PkiSecretBackendRootSignIntermediate#excluded_email_addresses}
        :param excluded_ip_ranges: List of IP ranges for which certificates are NOT allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_ip_ranges PkiSecretBackendRootSignIntermediate#excluded_ip_ranges}
        :param excluded_uri_domains: List of URI domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_uri_domains PkiSecretBackendRootSignIntermediate#excluded_uri_domains}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#format PkiSecretBackendRootSignIntermediate#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#id PkiSecretBackendRootSignIntermediate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ip_sans PkiSecretBackendRootSignIntermediate#ip_sans}
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#issuer_ref PkiSecretBackendRootSignIntermediate#issuer_ref}
        :param key_usage: Specify the key usages to be added to the existing set of key usages ("CRL", "CertSign") on the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#key_usage PkiSecretBackendRootSignIntermediate#key_usage}
        :param locality: The locality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#locality PkiSecretBackendRootSignIntermediate#locality}
        :param max_path_length: The maximum path length to encode in the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#max_path_length PkiSecretBackendRootSignIntermediate#max_path_length}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#namespace PkiSecretBackendRootSignIntermediate#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#not_after PkiSecretBackendRootSignIntermediate#not_after}
        :param not_before_duration: Specifies the duration by which to backdate the NotBefore property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#not_before_duration PkiSecretBackendRootSignIntermediate#not_before_duration}
        :param organization: The organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#organization PkiSecretBackendRootSignIntermediate#organization}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#other_sans PkiSecretBackendRootSignIntermediate#other_sans}
        :param ou: The organization unit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ou PkiSecretBackendRootSignIntermediate#ou}
        :param permitted_dns_domains: List of domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_dns_domains PkiSecretBackendRootSignIntermediate#permitted_dns_domains}
        :param permitted_email_addresses: List of email addresses for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_email_addresses PkiSecretBackendRootSignIntermediate#permitted_email_addresses}
        :param permitted_ip_ranges: List of IP ranges for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_ip_ranges PkiSecretBackendRootSignIntermediate#permitted_ip_ranges}
        :param permitted_uri_domains: List of URI domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_uri_domains PkiSecretBackendRootSignIntermediate#permitted_uri_domains}
        :param postal_code: The postal code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#postal_code PkiSecretBackendRootSignIntermediate#postal_code}
        :param province: The province. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#province PkiSecretBackendRootSignIntermediate#province}
        :param revoke: Revoke the certificate upon resource destruction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#revoke PkiSecretBackendRootSignIntermediate#revoke}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#signature_bits PkiSecretBackendRootSignIntermediate#signature_bits}
        :param skid: Value for the Subject Key Identifier field (RFC 5280 Section 4.2.1.2). Specified as a string in hex format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#skid PkiSecretBackendRootSignIntermediate#skid}
        :param street_address: The street address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#street_address PkiSecretBackendRootSignIntermediate#street_address}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ttl PkiSecretBackendRootSignIntermediate#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#uri_sans PkiSecretBackendRootSignIntermediate#uri_sans}
        :param use_csr_values: Preserve CSR values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#use_csr_values PkiSecretBackendRootSignIntermediate#use_csr_values}
        :param use_pss: Specifies whether or not to use PSS signatures over PKCS#1v1.5 signatures when a RSA-type issuer is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#use_pss PkiSecretBackendRootSignIntermediate#use_pss}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c871c825097ae0e9f106fc0a10e6e292f45e3d208b5fd93603ce77464c9c3f5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendRootSignIntermediateConfig(
            backend=backend,
            common_name=common_name,
            csr=csr,
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
            issuer_ref=issuer_ref,
            key_usage=key_usage,
            locality=locality,
            max_path_length=max_path_length,
            namespace=namespace,
            not_after=not_after,
            not_before_duration=not_before_duration,
            organization=organization,
            other_sans=other_sans,
            ou=ou,
            permitted_dns_domains=permitted_dns_domains,
            permitted_email_addresses=permitted_email_addresses,
            permitted_ip_ranges=permitted_ip_ranges,
            permitted_uri_domains=permitted_uri_domains,
            postal_code=postal_code,
            province=province,
            revoke=revoke,
            signature_bits=signature_bits,
            skid=skid,
            street_address=street_address,
            ttl=ttl,
            uri_sans=uri_sans,
            use_csr_values=use_csr_values,
            use_pss=use_pss,
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
        '''Generates CDKTF code for importing a PkiSecretBackendRootSignIntermediate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendRootSignIntermediate to import.
        :param import_from_id: The id of the existing PkiSecretBackendRootSignIntermediate that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendRootSignIntermediate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c46f29dcfca47d5f62ab936304e4e56200acbc422979fd46c9f0ca16aea5984)
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

    @jsii.member(jsii_name="resetIssuerRef")
    def reset_issuer_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuerRef", []))

    @jsii.member(jsii_name="resetKeyUsage")
    def reset_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyUsage", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetMaxPathLength")
    def reset_max_path_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPathLength", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNotAfter")
    def reset_not_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotAfter", []))

    @jsii.member(jsii_name="resetNotBeforeDuration")
    def reset_not_before_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotBeforeDuration", []))

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

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetRevoke")
    def reset_revoke(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevoke", []))

    @jsii.member(jsii_name="resetSignatureBits")
    def reset_signature_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureBits", []))

    @jsii.member(jsii_name="resetSkid")
    def reset_skid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkid", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetUriSans")
    def reset_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUriSans", []))

    @jsii.member(jsii_name="resetUseCsrValues")
    def reset_use_csr_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseCsrValues", []))

    @jsii.member(jsii_name="resetUsePss")
    def reset_use_pss(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsePss", []))

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
    @jsii.member(jsii_name="certificateBundle")
    def certificate_bundle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateBundle"))

    @builtins.property
    @jsii.member(jsii_name="issuingCa")
    def issuing_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuingCa"))

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
    @jsii.member(jsii_name="issuerRefInput")
    def issuer_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerRefInput"))

    @builtins.property
    @jsii.member(jsii_name="keyUsageInput")
    def key_usage_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "keyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localityInput"))

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
    @jsii.member(jsii_name="notBeforeDurationInput")
    def not_before_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notBeforeDurationInput"))

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
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provinceInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeInput")
    def revoke_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "revokeInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureBitsInput")
    def signature_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "signatureBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="skidInput")
    def skid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "skidInput"))

    @builtins.property
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streetAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="uriSansInput")
    def uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "uriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="useCsrValuesInput")
    def use_csr_values_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useCsrValuesInput"))

    @builtins.property
    @jsii.member(jsii_name="usePssInput")
    def use_pss_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePssInput"))

    @builtins.property
    @jsii.member(jsii_name="altNames")
    def alt_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "altNames"))

    @alt_names.setter
    def alt_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d17ca7b591e8549368f866015444f6ec48fbcf03c45cb448521bebccf10c3cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f699f7dec8b4c2b0cbab5a5634b50e462389fac351b2f579815f0a928a551534)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a70aaac2ac10ffe4828b5c109039a37856ad98d303918c31d7d20ae6543c4ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44fa4792a3d05b0be91b795edde4129159ced46e0cb74a38682961ef14ad2373)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "country", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="csr")
    def csr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csr"))

    @csr.setter
    def csr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c5f7fb576d587499cf35b7baef5229e20fba4e6a8cefaca8e70d544e40d434f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2ae6242055aba1200df641bf99f66f6b3d63cbfbf380865bf9d4c6ec40dc83d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeCnFromSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedDnsDomains")
    def excluded_dns_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedDnsDomains"))

    @excluded_dns_domains.setter
    def excluded_dns_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f3cc24c9638f38799970653a420cc6706a7d94d1120cac548c11dddfcb72974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedDnsDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedEmailAddresses")
    def excluded_email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedEmailAddresses"))

    @excluded_email_addresses.setter
    def excluded_email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b69079244c9d5e5a8e9d3421a51c77ce37f6e97e3679c7bcf88a22426cb7a96e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedEmailAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedIpRanges")
    def excluded_ip_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedIpRanges"))

    @excluded_ip_ranges.setter
    def excluded_ip_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1bf7f82fafac166d53bb07d3491f10d8143b5708fb3ec13c1b94b0fd22ed670)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedIpRanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludedUriDomains")
    def excluded_uri_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludedUriDomains"))

    @excluded_uri_domains.setter
    def excluded_uri_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c4adbb502e9f0778937e980053e34460d952dc33e44eea715fa0dabba177893)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludedUriDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8e86e10fd784bb024c6606c802b2105c6eb3f071dd7eb6128eae21c4e280a2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb50beb4220fcdd3585385a09167ca15a55ce1233b5171b0d93c653c1a4780d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipSans")
    def ip_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipSans"))

    @ip_sans.setter
    def ip_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fe7eeaea9157fb105cf4d21a9660e2933facc32ba5a35820ab0532de1459bce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerRef")
    def issuer_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerRef"))

    @issuer_ref.setter
    def issuer_ref(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c72a981486968078a59dfac18f79de21a8edccdb843f0979ad4327913e19c718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerRef", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyUsage")
    def key_usage(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keyUsage"))

    @key_usage.setter
    def key_usage(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0957d7b877e1c4d0c810c6af21c9f4cf3b13d7c6457e6845880852a2b51df8de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyUsage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="locality")
    def locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__424779186a1dafef663e220d0848a25c6b890911f9062bd0bc8de875ed2abdf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locality", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPathLength")
    def max_path_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPathLength"))

    @max_path_length.setter
    def max_path_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdf24542e3a71b6a3a490a778f3857968f7f91e21f23c263245155e84cc361a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPathLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__575880d128cef72dcb3ced1a261663bf9c308935984cdfd7304b41eb799f8e5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @not_after.setter
    def not_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed7724d53c6e68a9dacf570898facfda18426f2bff0aa612439a96c9494cf16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notBeforeDuration")
    def not_before_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBeforeDuration"))

    @not_before_duration.setter
    def not_before_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7269cb7d2254a36c2c8fc21b0ceca23c88830578f7e28b1aaf4f2ef11ab0185)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notBeforeDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd7902bb4cc9f69bd2f54cd249795ff1f85b9c24592a69f075d9573aa6e72727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="otherSans")
    def other_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "otherSans"))

    @other_sans.setter
    def other_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86c9db35291104130a61968f15ce51dc1b078bb5a5ce513a368f9779e57cb349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "otherSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ou")
    def ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ou"))

    @ou.setter
    def ou(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b5b4051ec2cdf223fc5001a67cf46b3f3f5d3d569687abbbca61717e5a6f19e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ou", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedDnsDomains")
    def permitted_dns_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedDnsDomains"))

    @permitted_dns_domains.setter
    def permitted_dns_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f152f7d31400c047dc8353e673d6f1f3212e6f661843e537532f5ceb4e7ab97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedDnsDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedEmailAddresses")
    def permitted_email_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedEmailAddresses"))

    @permitted_email_addresses.setter
    def permitted_email_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b56a29b623749c111e95757503e04986b2b432e17d32fbfc9bfea821abb525e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedEmailAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedIpRanges")
    def permitted_ip_ranges(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedIpRanges"))

    @permitted_ip_ranges.setter
    def permitted_ip_ranges(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f7f61081a89683a2a424a81efc6006dbd71572eaa4e0325a1d29e8b660db4d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedIpRanges", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permittedUriDomains")
    def permitted_uri_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "permittedUriDomains"))

    @permitted_uri_domains.setter
    def permitted_uri_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3670bc3edde4f8e47446c38ca3378c0784f2122bc9b7a925dcdc54d43695783)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permittedUriDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b73f9082f017056889e91853d327b70ea198628ee0f8a7e6e0b28569d3885ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postalCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="province")
    def province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "province"))

    @province.setter
    def province(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__620c14cd00b6b03df1ea5786d0a0ab5775a8a29099794966c0e9c6686c2fe794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "province", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e6fa90d3cbf5d2c9223d960df116bd0808bda9a238cd0cf63a6916020d3a8ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revoke", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureBits")
    def signature_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "signatureBits"))

    @signature_bits.setter
    def signature_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36825cc0f03f326daccd3b42acceca138372d1e4383441d93accf3565be54a29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skid")
    def skid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "skid"))

    @skid.setter
    def skid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eff01831ec116a410cb182f90b3a438bec1661bb723f0a17595950d54b090fb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebd2ab0fa4ba4ea58628591a8f103d357e574a5311458c301eb39b2bab1e256c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "streetAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__588f45ddc2075a535b815c8dd14c6e01e3c86e07832c1ba24c9575915ab63a40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3a14c8a1a684c13f21039da5de14917d65698bfedc0020ae12ea7694b4b37d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useCsrValues")
    def use_csr_values(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useCsrValues"))

    @use_csr_values.setter
    def use_csr_values(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6498f5cbaee31a3cbf3f42285ca9fdaf69773babf14a8b1997d0644abfdebe72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useCsrValues", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usePss")
    def use_pss(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usePss"))

    @use_pss.setter
    def use_pss(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__982b12a6a987577ccea79dc56d6a692eb438dacc7dcf7d9e39e4fde79e2b56a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePss", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRootSignIntermediate.PkiSecretBackendRootSignIntermediateConfig",
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
        "issuer_ref": "issuerRef",
        "key_usage": "keyUsage",
        "locality": "locality",
        "max_path_length": "maxPathLength",
        "namespace": "namespace",
        "not_after": "notAfter",
        "not_before_duration": "notBeforeDuration",
        "organization": "organization",
        "other_sans": "otherSans",
        "ou": "ou",
        "permitted_dns_domains": "permittedDnsDomains",
        "permitted_email_addresses": "permittedEmailAddresses",
        "permitted_ip_ranges": "permittedIpRanges",
        "permitted_uri_domains": "permittedUriDomains",
        "postal_code": "postalCode",
        "province": "province",
        "revoke": "revoke",
        "signature_bits": "signatureBits",
        "skid": "skid",
        "street_address": "streetAddress",
        "ttl": "ttl",
        "uri_sans": "uriSans",
        "use_csr_values": "useCsrValues",
        "use_pss": "usePss",
    },
)
class PkiSecretBackendRootSignIntermediateConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        issuer_ref: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        locality: typing.Optional[builtins.str] = None,
        max_path_length: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_after: typing.Optional[builtins.str] = None,
        not_before_duration: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[builtins.str] = None,
        permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        skid: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        use_csr_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_pss: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#backend PkiSecretBackendRootSignIntermediate#backend}
        :param common_name: CN of intermediate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#common_name PkiSecretBackendRootSignIntermediate#common_name}
        :param csr: The CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#csr PkiSecretBackendRootSignIntermediate#csr}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#alt_names PkiSecretBackendRootSignIntermediate#alt_names}
        :param country: The country. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#country PkiSecretBackendRootSignIntermediate#country}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#exclude_cn_from_sans PkiSecretBackendRootSignIntermediate#exclude_cn_from_sans}
        :param excluded_dns_domains: List of domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_dns_domains PkiSecretBackendRootSignIntermediate#excluded_dns_domains}
        :param excluded_email_addresses: List of email addresses for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_email_addresses PkiSecretBackendRootSignIntermediate#excluded_email_addresses}
        :param excluded_ip_ranges: List of IP ranges for which certificates are NOT allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_ip_ranges PkiSecretBackendRootSignIntermediate#excluded_ip_ranges}
        :param excluded_uri_domains: List of URI domains for which certificates are not allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_uri_domains PkiSecretBackendRootSignIntermediate#excluded_uri_domains}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#format PkiSecretBackendRootSignIntermediate#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#id PkiSecretBackendRootSignIntermediate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ip_sans PkiSecretBackendRootSignIntermediate#ip_sans}
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#issuer_ref PkiSecretBackendRootSignIntermediate#issuer_ref}
        :param key_usage: Specify the key usages to be added to the existing set of key usages ("CRL", "CertSign") on the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#key_usage PkiSecretBackendRootSignIntermediate#key_usage}
        :param locality: The locality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#locality PkiSecretBackendRootSignIntermediate#locality}
        :param max_path_length: The maximum path length to encode in the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#max_path_length PkiSecretBackendRootSignIntermediate#max_path_length}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#namespace PkiSecretBackendRootSignIntermediate#namespace}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#not_after PkiSecretBackendRootSignIntermediate#not_after}
        :param not_before_duration: Specifies the duration by which to backdate the NotBefore property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#not_before_duration PkiSecretBackendRootSignIntermediate#not_before_duration}
        :param organization: The organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#organization PkiSecretBackendRootSignIntermediate#organization}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#other_sans PkiSecretBackendRootSignIntermediate#other_sans}
        :param ou: The organization unit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ou PkiSecretBackendRootSignIntermediate#ou}
        :param permitted_dns_domains: List of domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_dns_domains PkiSecretBackendRootSignIntermediate#permitted_dns_domains}
        :param permitted_email_addresses: List of email addresses for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_email_addresses PkiSecretBackendRootSignIntermediate#permitted_email_addresses}
        :param permitted_ip_ranges: List of IP ranges for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_ip_ranges PkiSecretBackendRootSignIntermediate#permitted_ip_ranges}
        :param permitted_uri_domains: List of URI domains for which certificates are allowed to be issued. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_uri_domains PkiSecretBackendRootSignIntermediate#permitted_uri_domains}
        :param postal_code: The postal code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#postal_code PkiSecretBackendRootSignIntermediate#postal_code}
        :param province: The province. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#province PkiSecretBackendRootSignIntermediate#province}
        :param revoke: Revoke the certificate upon resource destruction. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#revoke PkiSecretBackendRootSignIntermediate#revoke}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#signature_bits PkiSecretBackendRootSignIntermediate#signature_bits}
        :param skid: Value for the Subject Key Identifier field (RFC 5280 Section 4.2.1.2). Specified as a string in hex format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#skid PkiSecretBackendRootSignIntermediate#skid}
        :param street_address: The street address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#street_address PkiSecretBackendRootSignIntermediate#street_address}
        :param ttl: Time to live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ttl PkiSecretBackendRootSignIntermediate#ttl}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#uri_sans PkiSecretBackendRootSignIntermediate#uri_sans}
        :param use_csr_values: Preserve CSR values. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#use_csr_values PkiSecretBackendRootSignIntermediate#use_csr_values}
        :param use_pss: Specifies whether or not to use PSS signatures over PKCS#1v1.5 signatures when a RSA-type issuer is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#use_pss PkiSecretBackendRootSignIntermediate#use_pss}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b74fb64d8e8bc53a45af93d371e6fc8866fc36f8977c7d3d41374de479b689e)
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
            check_type(argname="argument issuer_ref", value=issuer_ref, expected_type=type_hints["issuer_ref"])
            check_type(argname="argument key_usage", value=key_usage, expected_type=type_hints["key_usage"])
            check_type(argname="argument locality", value=locality, expected_type=type_hints["locality"])
            check_type(argname="argument max_path_length", value=max_path_length, expected_type=type_hints["max_path_length"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument not_after", value=not_after, expected_type=type_hints["not_after"])
            check_type(argname="argument not_before_duration", value=not_before_duration, expected_type=type_hints["not_before_duration"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
            check_type(argname="argument other_sans", value=other_sans, expected_type=type_hints["other_sans"])
            check_type(argname="argument ou", value=ou, expected_type=type_hints["ou"])
            check_type(argname="argument permitted_dns_domains", value=permitted_dns_domains, expected_type=type_hints["permitted_dns_domains"])
            check_type(argname="argument permitted_email_addresses", value=permitted_email_addresses, expected_type=type_hints["permitted_email_addresses"])
            check_type(argname="argument permitted_ip_ranges", value=permitted_ip_ranges, expected_type=type_hints["permitted_ip_ranges"])
            check_type(argname="argument permitted_uri_domains", value=permitted_uri_domains, expected_type=type_hints["permitted_uri_domains"])
            check_type(argname="argument postal_code", value=postal_code, expected_type=type_hints["postal_code"])
            check_type(argname="argument province", value=province, expected_type=type_hints["province"])
            check_type(argname="argument revoke", value=revoke, expected_type=type_hints["revoke"])
            check_type(argname="argument signature_bits", value=signature_bits, expected_type=type_hints["signature_bits"])
            check_type(argname="argument skid", value=skid, expected_type=type_hints["skid"])
            check_type(argname="argument street_address", value=street_address, expected_type=type_hints["street_address"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
            check_type(argname="argument use_csr_values", value=use_csr_values, expected_type=type_hints["use_csr_values"])
            check_type(argname="argument use_pss", value=use_pss, expected_type=type_hints["use_pss"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "common_name": common_name,
            "csr": csr,
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
        if issuer_ref is not None:
            self._values["issuer_ref"] = issuer_ref
        if key_usage is not None:
            self._values["key_usage"] = key_usage
        if locality is not None:
            self._values["locality"] = locality
        if max_path_length is not None:
            self._values["max_path_length"] = max_path_length
        if namespace is not None:
            self._values["namespace"] = namespace
        if not_after is not None:
            self._values["not_after"] = not_after
        if not_before_duration is not None:
            self._values["not_before_duration"] = not_before_duration
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
        if province is not None:
            self._values["province"] = province
        if revoke is not None:
            self._values["revoke"] = revoke
        if signature_bits is not None:
            self._values["signature_bits"] = signature_bits
        if skid is not None:
            self._values["skid"] = skid
        if street_address is not None:
            self._values["street_address"] = street_address
        if ttl is not None:
            self._values["ttl"] = ttl
        if uri_sans is not None:
            self._values["uri_sans"] = uri_sans
        if use_csr_values is not None:
            self._values["use_csr_values"] = use_csr_values
        if use_pss is not None:
            self._values["use_pss"] = use_pss

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#backend PkiSecretBackendRootSignIntermediate#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def common_name(self) -> builtins.str:
        '''CN of intermediate to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#common_name PkiSecretBackendRootSignIntermediate#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def csr(self) -> builtins.str:
        '''The CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#csr PkiSecretBackendRootSignIntermediate#csr}
        '''
        result = self._values.get("csr")
        assert result is not None, "Required property 'csr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alt_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#alt_names PkiSecretBackendRootSignIntermediate#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''The country.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#country PkiSecretBackendRootSignIntermediate#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_cn_from_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to exclude CN from SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#exclude_cn_from_sans PkiSecretBackendRootSignIntermediate#exclude_cn_from_sans}
        '''
        result = self._values.get("exclude_cn_from_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def excluded_dns_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of domains for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_dns_domains PkiSecretBackendRootSignIntermediate#excluded_dns_domains}
        '''
        result = self._values.get("excluded_dns_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of email addresses for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_email_addresses PkiSecretBackendRootSignIntermediate#excluded_email_addresses}
        '''
        result = self._values.get("excluded_email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_ip_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP ranges for which certificates are NOT allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_ip_ranges PkiSecretBackendRootSignIntermediate#excluded_ip_ranges}
        '''
        result = self._values.get("excluded_ip_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def excluded_uri_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URI domains for which certificates are not allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#excluded_uri_domains PkiSecretBackendRootSignIntermediate#excluded_uri_domains}
        '''
        result = self._values.get("excluded_uri_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format of data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#format PkiSecretBackendRootSignIntermediate#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#id PkiSecretBackendRootSignIntermediate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ip_sans PkiSecretBackendRootSignIntermediate#ip_sans}
        '''
        result = self._values.get("ip_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def issuer_ref(self) -> typing.Optional[builtins.str]:
        '''Specifies the default issuer of this request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#issuer_ref PkiSecretBackendRootSignIntermediate#issuer_ref}
        '''
        result = self._values.get("issuer_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_usage(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specify the key usages to be added to the existing set of key usages ("CRL", "CertSign") on the generated certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#key_usage PkiSecretBackendRootSignIntermediate#key_usage}
        '''
        result = self._values.get("key_usage")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''The locality.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#locality PkiSecretBackendRootSignIntermediate#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_path_length(self) -> typing.Optional[jsii.Number]:
        '''The maximum path length to encode in the generated certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#max_path_length PkiSecretBackendRootSignIntermediate#max_path_length}
        '''
        result = self._values.get("max_path_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#namespace PkiSecretBackendRootSignIntermediate#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_after(self) -> typing.Optional[builtins.str]:
        '''Set the Not After field of the certificate with specified date value.

        The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#not_after PkiSecretBackendRootSignIntermediate#not_after}
        '''
        result = self._values.get("not_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_before_duration(self) -> typing.Optional[builtins.str]:
        '''Specifies the duration by which to backdate the NotBefore property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#not_before_duration PkiSecretBackendRootSignIntermediate#not_before_duration}
        '''
        result = self._values.get("not_before_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''The organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#organization PkiSecretBackendRootSignIntermediate#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def other_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of other SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#other_sans PkiSecretBackendRootSignIntermediate#other_sans}
        '''
        result = self._values.get("other_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ou(self) -> typing.Optional[builtins.str]:
        '''The organization unit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ou PkiSecretBackendRootSignIntermediate#ou}
        '''
        result = self._values.get("ou")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permitted_dns_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of domains for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_dns_domains PkiSecretBackendRootSignIntermediate#permitted_dns_domains}
        '''
        result = self._values.get("permitted_dns_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permitted_email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of email addresses for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_email_addresses PkiSecretBackendRootSignIntermediate#permitted_email_addresses}
        '''
        result = self._values.get("permitted_email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permitted_ip_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP ranges for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_ip_ranges PkiSecretBackendRootSignIntermediate#permitted_ip_ranges}
        '''
        result = self._values.get("permitted_ip_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permitted_uri_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URI domains for which certificates are allowed to be issued.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#permitted_uri_domains PkiSecretBackendRootSignIntermediate#permitted_uri_domains}
        '''
        result = self._values.get("permitted_uri_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''The postal code.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#postal_code PkiSecretBackendRootSignIntermediate#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''The province.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#province PkiSecretBackendRootSignIntermediate#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revoke(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Revoke the certificate upon resource destruction.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#revoke PkiSecretBackendRootSignIntermediate#revoke}
        '''
        result = self._values.get("revoke")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def signature_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits to use in the signature algorithm.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#signature_bits PkiSecretBackendRootSignIntermediate#signature_bits}
        '''
        result = self._values.get("signature_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def skid(self) -> typing.Optional[builtins.str]:
        '''Value for the Subject Key Identifier field   (RFC 5280 Section 4.2.1.2). Specified as a string in hex format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#skid PkiSecretBackendRootSignIntermediate#skid}
        '''
        result = self._values.get("skid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def street_address(self) -> typing.Optional[builtins.str]:
        '''The street address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#street_address PkiSecretBackendRootSignIntermediate#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Time to live.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#ttl PkiSecretBackendRootSignIntermediate#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative URIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#uri_sans PkiSecretBackendRootSignIntermediate#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def use_csr_values(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Preserve CSR values.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#use_csr_values PkiSecretBackendRootSignIntermediate#use_csr_values}
        '''
        result = self._values.get("use_csr_values")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_pss(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether or not to use PSS signatures   over PKCS#1v1.5 signatures when a RSA-type issuer is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_root_sign_intermediate#use_pss PkiSecretBackendRootSignIntermediate#use_pss}
        '''
        result = self._values.get("use_pss")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendRootSignIntermediateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendRootSignIntermediate",
    "PkiSecretBackendRootSignIntermediateConfig",
]

publication.publish()

def _typecheckingstub__2c871c825097ae0e9f106fc0a10e6e292f45e3d208b5fd93603ce77464c9c3f5(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    common_name: builtins.str,
    csr: builtins.str,
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
    issuer_ref: typing.Optional[builtins.str] = None,
    key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    locality: typing.Optional[builtins.str] = None,
    max_path_length: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_after: typing.Optional[builtins.str] = None,
    not_before_duration: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[builtins.str] = None,
    permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    postal_code: typing.Optional[builtins.str] = None,
    province: typing.Optional[builtins.str] = None,
    revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    skid: typing.Optional[builtins.str] = None,
    street_address: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    use_csr_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_pss: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__9c46f29dcfca47d5f62ab936304e4e56200acbc422979fd46c9f0ca16aea5984(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d17ca7b591e8549368f866015444f6ec48fbcf03c45cb448521bebccf10c3cd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f699f7dec8b4c2b0cbab5a5634b50e462389fac351b2f579815f0a928a551534(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a70aaac2ac10ffe4828b5c109039a37856ad98d303918c31d7d20ae6543c4ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44fa4792a3d05b0be91b795edde4129159ced46e0cb74a38682961ef14ad2373(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c5f7fb576d587499cf35b7baef5229e20fba4e6a8cefaca8e70d544e40d434f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ae6242055aba1200df641bf99f66f6b3d63cbfbf380865bf9d4c6ec40dc83d4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f3cc24c9638f38799970653a420cc6706a7d94d1120cac548c11dddfcb72974(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b69079244c9d5e5a8e9d3421a51c77ce37f6e97e3679c7bcf88a22426cb7a96e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1bf7f82fafac166d53bb07d3491f10d8143b5708fb3ec13c1b94b0fd22ed670(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c4adbb502e9f0778937e980053e34460d952dc33e44eea715fa0dabba177893(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8e86e10fd784bb024c6606c802b2105c6eb3f071dd7eb6128eae21c4e280a2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb50beb4220fcdd3585385a09167ca15a55ce1233b5171b0d93c653c1a4780d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fe7eeaea9157fb105cf4d21a9660e2933facc32ba5a35820ab0532de1459bce(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c72a981486968078a59dfac18f79de21a8edccdb843f0979ad4327913e19c718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0957d7b877e1c4d0c810c6af21c9f4cf3b13d7c6457e6845880852a2b51df8de(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__424779186a1dafef663e220d0848a25c6b890911f9062bd0bc8de875ed2abdf8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdf24542e3a71b6a3a490a778f3857968f7f91e21f23c263245155e84cc361a5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__575880d128cef72dcb3ced1a261663bf9c308935984cdfd7304b41eb799f8e5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed7724d53c6e68a9dacf570898facfda18426f2bff0aa612439a96c9494cf16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7269cb7d2254a36c2c8fc21b0ceca23c88830578f7e28b1aaf4f2ef11ab0185(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd7902bb4cc9f69bd2f54cd249795ff1f85b9c24592a69f075d9573aa6e72727(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86c9db35291104130a61968f15ce51dc1b078bb5a5ce513a368f9779e57cb349(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b5b4051ec2cdf223fc5001a67cf46b3f3f5d3d569687abbbca61717e5a6f19e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f152f7d31400c047dc8353e673d6f1f3212e6f661843e537532f5ceb4e7ab97(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b56a29b623749c111e95757503e04986b2b432e17d32fbfc9bfea821abb525e4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f7f61081a89683a2a424a81efc6006dbd71572eaa4e0325a1d29e8b660db4d6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3670bc3edde4f8e47446c38ca3378c0784f2122bc9b7a925dcdc54d43695783(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b73f9082f017056889e91853d327b70ea198628ee0f8a7e6e0b28569d3885ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__620c14cd00b6b03df1ea5786d0a0ab5775a8a29099794966c0e9c6686c2fe794(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6fa90d3cbf5d2c9223d960df116bd0808bda9a238cd0cf63a6916020d3a8ad9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36825cc0f03f326daccd3b42acceca138372d1e4383441d93accf3565be54a29(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eff01831ec116a410cb182f90b3a438bec1661bb723f0a17595950d54b090fb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebd2ab0fa4ba4ea58628591a8f103d357e574a5311458c301eb39b2bab1e256c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__588f45ddc2075a535b815c8dd14c6e01e3c86e07832c1ba24c9575915ab63a40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3a14c8a1a684c13f21039da5de14917d65698bfedc0020ae12ea7694b4b37d9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6498f5cbaee31a3cbf3f42285ca9fdaf69773babf14a8b1997d0644abfdebe72(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__982b12a6a987577ccea79dc56d6a692eb438dacc7dcf7d9e39e4fde79e2b56a8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b74fb64d8e8bc53a45af93d371e6fc8866fc36f8977c7d3d41374de479b689e(
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
    issuer_ref: typing.Optional[builtins.str] = None,
    key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    locality: typing.Optional[builtins.str] = None,
    max_path_length: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_after: typing.Optional[builtins.str] = None,
    not_before_duration: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[builtins.str] = None,
    permitted_dns_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_ip_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    permitted_uri_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    postal_code: typing.Optional[builtins.str] = None,
    province: typing.Optional[builtins.str] = None,
    revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    skid: typing.Optional[builtins.str] = None,
    street_address: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    use_csr_values: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_pss: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
