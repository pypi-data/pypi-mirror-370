r'''
# `vault_pki_secret_backend_role`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role).
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


class PkiSecretBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRole.PkiSecretBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role vault_pki_secret_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        name: builtins.str,
        allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_serial_numbers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_uri_sans_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_glob_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_ip_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_localhost: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_wildcard_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        basic_constraints_valid_for_non_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cn_validations: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        country: typing.Optional[typing.Sequence[builtins.str]] = None,
        email_protection_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ext_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        ext_key_usage_oids: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_lease: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer_ref: typing.Optional[builtins.str] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_type: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        locality: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        no_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_store_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        not_after: typing.Optional[builtins.str] = None,
        not_before_duration: typing.Optional[builtins.str] = None,
        organization: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy_identifier: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PkiSecretBackendRolePolicyIdentifier", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        postal_code: typing.Optional[typing.Sequence[builtins.str]] = None,
        province: typing.Optional[typing.Sequence[builtins.str]] = None,
        require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        serial_number_source: typing.Optional[builtins.str] = None,
        server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[builtins.str] = None,
        use_csr_common_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_csr_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_pss: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role vault_pki_secret_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The path of the PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#backend PkiSecretBackendRole#backend}
        :param name: Unique name for the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#name PkiSecretBackendRole#name}
        :param allow_any_name: Flag to allow any name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_any_name PkiSecretBackendRole#allow_any_name}
        :param allow_bare_domains: Flag to allow certificates matching the actual domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_bare_domains PkiSecretBackendRole#allow_bare_domains}
        :param allowed_domains: The domains of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_domains PkiSecretBackendRole#allowed_domains}
        :param allowed_domains_template: Flag to indicate that ``allowed_domains`` specifies a template expression (e.g. {{identity.entity.aliases..name}}). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_domains_template PkiSecretBackendRole#allowed_domains_template}
        :param allowed_other_sans: Defines allowed custom SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_other_sans PkiSecretBackendRole#allowed_other_sans}
        :param allowed_serial_numbers: Defines allowed Subject serial numbers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_serial_numbers PkiSecretBackendRole#allowed_serial_numbers}
        :param allowed_uri_sans: Defines allowed URI SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_uri_sans PkiSecretBackendRole#allowed_uri_sans}
        :param allowed_uri_sans_template: Flag to indicate that ``allowed_uri_sans`` specifies a template expression (e.g. {{identity.entity.aliases..name}}). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_uri_sans_template PkiSecretBackendRole#allowed_uri_sans_template}
        :param allowed_user_ids: The allowed User ID's. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_user_ids PkiSecretBackendRole#allowed_user_ids}
        :param allow_glob_domains: Flag to allow names containing glob patterns. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_glob_domains PkiSecretBackendRole#allow_glob_domains}
        :param allow_ip_sans: Flag to allow IP SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_ip_sans PkiSecretBackendRole#allow_ip_sans}
        :param allow_localhost: Flag to allow certificates for localhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_localhost PkiSecretBackendRole#allow_localhost}
        :param allow_subdomains: Flag to allow certificates matching subdomains. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_subdomains PkiSecretBackendRole#allow_subdomains}
        :param allow_wildcard_certificates: Flag to allow wildcard certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_wildcard_certificates PkiSecretBackendRole#allow_wildcard_certificates}
        :param basic_constraints_valid_for_non_ca: Flag to mark basic constraints valid when issuing non-CA certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#basic_constraints_valid_for_non_ca PkiSecretBackendRole#basic_constraints_valid_for_non_ca}
        :param client_flag: Flag to specify certificates for client use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#client_flag PkiSecretBackendRole#client_flag}
        :param cn_validations: Specify validations to run on the Common Name field of the certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#cn_validations PkiSecretBackendRole#cn_validations}
        :param code_signing_flag: Flag to specify certificates for code signing use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#code_signing_flag PkiSecretBackendRole#code_signing_flag}
        :param country: The country of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#country PkiSecretBackendRole#country}
        :param email_protection_flag: Flag to specify certificates for email protection use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#email_protection_flag PkiSecretBackendRole#email_protection_flag}
        :param enforce_hostnames: Flag to allow only valid host names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#enforce_hostnames PkiSecretBackendRole#enforce_hostnames}
        :param ext_key_usage: Specify the allowed extended key usage constraint on issued certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ext_key_usage PkiSecretBackendRole#ext_key_usage}
        :param ext_key_usage_oids: A list of extended key usage OIDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ext_key_usage_oids PkiSecretBackendRole#ext_key_usage_oids}
        :param generate_lease: Flag to generate leases with certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#generate_lease PkiSecretBackendRole#generate_lease}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#id PkiSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#issuer_ref PkiSecretBackendRole#issuer_ref}
        :param key_bits: The number of bits of generated keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_bits PkiSecretBackendRole#key_bits}
        :param key_type: The generated key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_type PkiSecretBackendRole#key_type}
        :param key_usage: Specify the allowed key usage constraint on issued certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_usage PkiSecretBackendRole#key_usage}
        :param locality: The locality of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#locality PkiSecretBackendRole#locality}
        :param max_ttl: The maximum TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#max_ttl PkiSecretBackendRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#namespace PkiSecretBackendRole#namespace}
        :param no_store: Flag to not store certificates in the storage backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#no_store PkiSecretBackendRole#no_store}
        :param no_store_metadata: Allows metadata to be stored keyed on the certificate's serial number. The field is independent of no_store, allowing metadata storage regardless of whether certificates are stored. If true, metadata is not stored and an error is returned if the metadata field is specified on issuance APIs Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#no_store_metadata PkiSecretBackendRole#no_store_metadata}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#not_after PkiSecretBackendRole#not_after}
        :param not_before_duration: Specifies the duration by which to backdate the NotBefore property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#not_before_duration PkiSecretBackendRole#not_before_duration}
        :param organization: The organization of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#organization PkiSecretBackendRole#organization}
        :param ou: The organization unit of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ou PkiSecretBackendRole#ou}
        :param policy_identifier: policy_identifier block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#policy_identifier PkiSecretBackendRole#policy_identifier}
        :param policy_identifiers: Specify the list of allowed policies OIDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#policy_identifiers PkiSecretBackendRole#policy_identifiers}
        :param postal_code: The postal code of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#postal_code PkiSecretBackendRole#postal_code}
        :param province: The province of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#province PkiSecretBackendRole#province}
        :param require_cn: Flag to force CN usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#require_cn PkiSecretBackendRole#require_cn}
        :param serial_number_source: Specifies the source of the subject serial number. Valid values are json-csr (default) or json. When set to json-csr, the subject serial number is taken from the serial_number parameter and falls back to the serial number in the CSR. When set to json, the subject serial number is taken from the serial_number parameter but will ignore any value in the CSR. For backwards compatibility an empty value for this field will default to the json-csr behavior. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#serial_number_source PkiSecretBackendRole#serial_number_source}
        :param server_flag: Flag to specify certificates for server use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#server_flag PkiSecretBackendRole#server_flag}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#signature_bits PkiSecretBackendRole#signature_bits}
        :param street_address: The street address of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#street_address PkiSecretBackendRole#street_address}
        :param ttl: The TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ttl PkiSecretBackendRole#ttl}
        :param use_csr_common_name: Flag to use the CN in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_csr_common_name PkiSecretBackendRole#use_csr_common_name}
        :param use_csr_sans: Flag to use the SANs in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_csr_sans PkiSecretBackendRole#use_csr_sans}
        :param use_pss: Specifies whether or not to use PSS signatures over PKCS#1v1.5 signatures when a RSA-type issuer is used. Ignored for ECDSA/Ed25519 issuers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_pss PkiSecretBackendRole#use_pss}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dde302e3509ad6d6820978bc921b8731a84a5acab3e090045db11e5049c9c62)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendRoleConfig(
            backend=backend,
            name=name,
            allow_any_name=allow_any_name,
            allow_bare_domains=allow_bare_domains,
            allowed_domains=allowed_domains,
            allowed_domains_template=allowed_domains_template,
            allowed_other_sans=allowed_other_sans,
            allowed_serial_numbers=allowed_serial_numbers,
            allowed_uri_sans=allowed_uri_sans,
            allowed_uri_sans_template=allowed_uri_sans_template,
            allowed_user_ids=allowed_user_ids,
            allow_glob_domains=allow_glob_domains,
            allow_ip_sans=allow_ip_sans,
            allow_localhost=allow_localhost,
            allow_subdomains=allow_subdomains,
            allow_wildcard_certificates=allow_wildcard_certificates,
            basic_constraints_valid_for_non_ca=basic_constraints_valid_for_non_ca,
            client_flag=client_flag,
            cn_validations=cn_validations,
            code_signing_flag=code_signing_flag,
            country=country,
            email_protection_flag=email_protection_flag,
            enforce_hostnames=enforce_hostnames,
            ext_key_usage=ext_key_usage,
            ext_key_usage_oids=ext_key_usage_oids,
            generate_lease=generate_lease,
            id=id,
            issuer_ref=issuer_ref,
            key_bits=key_bits,
            key_type=key_type,
            key_usage=key_usage,
            locality=locality,
            max_ttl=max_ttl,
            namespace=namespace,
            no_store=no_store,
            no_store_metadata=no_store_metadata,
            not_after=not_after,
            not_before_duration=not_before_duration,
            organization=organization,
            ou=ou,
            policy_identifier=policy_identifier,
            policy_identifiers=policy_identifiers,
            postal_code=postal_code,
            province=province,
            require_cn=require_cn,
            serial_number_source=serial_number_source,
            server_flag=server_flag,
            signature_bits=signature_bits,
            street_address=street_address,
            ttl=ttl,
            use_csr_common_name=use_csr_common_name,
            use_csr_sans=use_csr_sans,
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
        '''Generates CDKTF code for importing a PkiSecretBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendRole to import.
        :param import_from_id: The id of the existing PkiSecretBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfccb371d8d5c1673e87c4809146e4edbcbbe7eb96752d9d2e5999ca7bf8b769)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putPolicyIdentifier")
    def put_policy_identifier(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PkiSecretBackendRolePolicyIdentifier", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3e4ae93979768f420af02eed90070ba97fa1aec10dd16d86ee07650b4972de3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyIdentifier", [value]))

    @jsii.member(jsii_name="resetAllowAnyName")
    def reset_allow_any_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAnyName", []))

    @jsii.member(jsii_name="resetAllowBareDomains")
    def reset_allow_bare_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowBareDomains", []))

    @jsii.member(jsii_name="resetAllowedDomains")
    def reset_allowed_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDomains", []))

    @jsii.member(jsii_name="resetAllowedDomainsTemplate")
    def reset_allowed_domains_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDomainsTemplate", []))

    @jsii.member(jsii_name="resetAllowedOtherSans")
    def reset_allowed_other_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOtherSans", []))

    @jsii.member(jsii_name="resetAllowedSerialNumbers")
    def reset_allowed_serial_numbers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedSerialNumbers", []))

    @jsii.member(jsii_name="resetAllowedUriSans")
    def reset_allowed_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUriSans", []))

    @jsii.member(jsii_name="resetAllowedUriSansTemplate")
    def reset_allowed_uri_sans_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUriSansTemplate", []))

    @jsii.member(jsii_name="resetAllowedUserIds")
    def reset_allowed_user_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUserIds", []))

    @jsii.member(jsii_name="resetAllowGlobDomains")
    def reset_allow_glob_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowGlobDomains", []))

    @jsii.member(jsii_name="resetAllowIpSans")
    def reset_allow_ip_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowIpSans", []))

    @jsii.member(jsii_name="resetAllowLocalhost")
    def reset_allow_localhost(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowLocalhost", []))

    @jsii.member(jsii_name="resetAllowSubdomains")
    def reset_allow_subdomains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSubdomains", []))

    @jsii.member(jsii_name="resetAllowWildcardCertificates")
    def reset_allow_wildcard_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowWildcardCertificates", []))

    @jsii.member(jsii_name="resetBasicConstraintsValidForNonCa")
    def reset_basic_constraints_valid_for_non_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasicConstraintsValidForNonCa", []))

    @jsii.member(jsii_name="resetClientFlag")
    def reset_client_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientFlag", []))

    @jsii.member(jsii_name="resetCnValidations")
    def reset_cn_validations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCnValidations", []))

    @jsii.member(jsii_name="resetCodeSigningFlag")
    def reset_code_signing_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCodeSigningFlag", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetEmailProtectionFlag")
    def reset_email_protection_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailProtectionFlag", []))

    @jsii.member(jsii_name="resetEnforceHostnames")
    def reset_enforce_hostnames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnforceHostnames", []))

    @jsii.member(jsii_name="resetExtKeyUsage")
    def reset_ext_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtKeyUsage", []))

    @jsii.member(jsii_name="resetExtKeyUsageOids")
    def reset_ext_key_usage_oids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtKeyUsageOids", []))

    @jsii.member(jsii_name="resetGenerateLease")
    def reset_generate_lease(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateLease", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIssuerRef")
    def reset_issuer_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuerRef", []))

    @jsii.member(jsii_name="resetKeyBits")
    def reset_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyBits", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetKeyUsage")
    def reset_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyUsage", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNoStore")
    def reset_no_store(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoStore", []))

    @jsii.member(jsii_name="resetNoStoreMetadata")
    def reset_no_store_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoStoreMetadata", []))

    @jsii.member(jsii_name="resetNotAfter")
    def reset_not_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotAfter", []))

    @jsii.member(jsii_name="resetNotBeforeDuration")
    def reset_not_before_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotBeforeDuration", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetOu")
    def reset_ou(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOu", []))

    @jsii.member(jsii_name="resetPolicyIdentifier")
    def reset_policy_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyIdentifier", []))

    @jsii.member(jsii_name="resetPolicyIdentifiers")
    def reset_policy_identifiers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyIdentifiers", []))

    @jsii.member(jsii_name="resetPostalCode")
    def reset_postal_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostalCode", []))

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetRequireCn")
    def reset_require_cn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequireCn", []))

    @jsii.member(jsii_name="resetSerialNumberSource")
    def reset_serial_number_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSerialNumberSource", []))

    @jsii.member(jsii_name="resetServerFlag")
    def reset_server_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerFlag", []))

    @jsii.member(jsii_name="resetSignatureBits")
    def reset_signature_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureBits", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetUseCsrCommonName")
    def reset_use_csr_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseCsrCommonName", []))

    @jsii.member(jsii_name="resetUseCsrSans")
    def reset_use_csr_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseCsrSans", []))

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
    @jsii.member(jsii_name="policyIdentifier")
    def policy_identifier(self) -> "PkiSecretBackendRolePolicyIdentifierList":
        return typing.cast("PkiSecretBackendRolePolicyIdentifierList", jsii.get(self, "policyIdentifier"))

    @builtins.property
    @jsii.member(jsii_name="allowAnyNameInput")
    def allow_any_name_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAnyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="allowBareDomainsInput")
    def allow_bare_domains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowBareDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsInput")
    def allowed_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsTemplateInput")
    def allowed_domains_template_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowedDomainsTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedOtherSansInput")
    def allowed_other_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOtherSansInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedSerialNumbersInput")
    def allowed_serial_numbers_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedSerialNumbersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUriSansInput")
    def allowed_uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUriSansTemplateInput")
    def allowed_uri_sans_template_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowedUriSansTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUserIdsInput")
    def allowed_user_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUserIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowGlobDomainsInput")
    def allow_glob_domains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowGlobDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowIpSansInput")
    def allow_ip_sans_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowIpSansInput"))

    @builtins.property
    @jsii.member(jsii_name="allowLocalhostInput")
    def allow_localhost_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowLocalhostInput"))

    @builtins.property
    @jsii.member(jsii_name="allowSubdomainsInput")
    def allow_subdomains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowSubdomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowWildcardCertificatesInput")
    def allow_wildcard_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowWildcardCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="basicConstraintsValidForNonCaInput")
    def basic_constraints_valid_for_non_ca_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "basicConstraintsValidForNonCaInput"))

    @builtins.property
    @jsii.member(jsii_name="clientFlagInput")
    def client_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clientFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="cnValidationsInput")
    def cn_validations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cnValidationsInput"))

    @builtins.property
    @jsii.member(jsii_name="codeSigningFlagInput")
    def code_signing_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "codeSigningFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "countryInput"))

    @builtins.property
    @jsii.member(jsii_name="emailProtectionFlagInput")
    def email_protection_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "emailProtectionFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="enforceHostnamesInput")
    def enforce_hostnames_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enforceHostnamesInput"))

    @builtins.property
    @jsii.member(jsii_name="extKeyUsageInput")
    def ext_key_usage_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "extKeyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="extKeyUsageOidsInput")
    def ext_key_usage_oids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "extKeyUsageOidsInput"))

    @builtins.property
    @jsii.member(jsii_name="generateLeaseInput")
    def generate_lease_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "generateLeaseInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerRefInput")
    def issuer_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerRefInput"))

    @builtins.property
    @jsii.member(jsii_name="keyBitsInput")
    def key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="keyUsageInput")
    def key_usage_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "keyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "localityInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="noStoreInput")
    def no_store_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noStoreInput"))

    @builtins.property
    @jsii.member(jsii_name="noStoreMetadataInput")
    def no_store_metadata_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noStoreMetadataInput"))

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
    def organization_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "organizationInput"))

    @builtins.property
    @jsii.member(jsii_name="ouInput")
    def ou_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ouInput"))

    @builtins.property
    @jsii.member(jsii_name="policyIdentifierInput")
    def policy_identifier_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendRolePolicyIdentifier"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendRolePolicyIdentifier"]]], jsii.get(self, "policyIdentifierInput"))

    @builtins.property
    @jsii.member(jsii_name="policyIdentifiersInput")
    def policy_identifiers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "policyIdentifiersInput"))

    @builtins.property
    @jsii.member(jsii_name="postalCodeInput")
    def postal_code_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "postalCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "provinceInput"))

    @builtins.property
    @jsii.member(jsii_name="requireCnInput")
    def require_cn_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requireCnInput"))

    @builtins.property
    @jsii.member(jsii_name="serialNumberSourceInput")
    def serial_number_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serialNumberSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="serverFlagInput")
    def server_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serverFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureBitsInput")
    def signature_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "signatureBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "streetAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="useCsrCommonNameInput")
    def use_csr_common_name_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useCsrCommonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="useCsrSansInput")
    def use_csr_sans_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useCsrSansInput"))

    @builtins.property
    @jsii.member(jsii_name="usePssInput")
    def use_pss_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePssInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAnyName")
    def allow_any_name(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAnyName"))

    @allow_any_name.setter
    def allow_any_name(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e52faef2c0fb3c0d6cdbf5c054e334799a1c7d3b69272499821ab7f168b7176)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAnyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowBareDomains")
    def allow_bare_domains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowBareDomains"))

    @allow_bare_domains.setter
    def allow_bare_domains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4702407aa7f85a09489a1dc850ce9c74d16eb88a65b7f3c3bafa6dd187cb537)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowBareDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedDomains")
    def allowed_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedDomains"))

    @allowed_domains.setter
    def allowed_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__879d9d584ec7a94bfd819fe1e5988356afc25cd42c7c363264d15fd09a09ed81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsTemplate")
    def allowed_domains_template(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowedDomainsTemplate"))

    @allowed_domains_template.setter
    def allowed_domains_template(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fe5618998119f32e0f4b63e1c752f4c7a1e64a120bdeb7eef070d083de5f3af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDomainsTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedOtherSans")
    def allowed_other_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOtherSans"))

    @allowed_other_sans.setter
    def allowed_other_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7106c19b217aa463447da8164ec97ce7e3c0ba90bf5e8b25d4adf904f11fd521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOtherSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedSerialNumbers")
    def allowed_serial_numbers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedSerialNumbers"))

    @allowed_serial_numbers.setter
    def allowed_serial_numbers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db76a1856525340c790a815078719d5e7473c066390b3080dba20ffa4153d3f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedSerialNumbers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedUriSans")
    def allowed_uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUriSans"))

    @allowed_uri_sans.setter
    def allowed_uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__438bba11178b2c2db58bd2d05df9d261f6d6f660f3fbf86733b6300e76240a70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUriSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedUriSansTemplate")
    def allowed_uri_sans_template(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowedUriSansTemplate"))

    @allowed_uri_sans_template.setter
    def allowed_uri_sans_template(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7a51cefd25a81260e714a9045b2bd6b9dceb12cae09e14b8a47817bd1da9ee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUriSansTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedUserIds")
    def allowed_user_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUserIds"))

    @allowed_user_ids.setter
    def allowed_user_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c2a3b3669296d6a05b64b2c9f6ccd86cdba528acd4936c1d329d068556763f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUserIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowGlobDomains")
    def allow_glob_domains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowGlobDomains"))

    @allow_glob_domains.setter
    def allow_glob_domains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b97f3ba64abccc27a36eae4cae25f3aff3a848c2902cca9a7953de9ffc51705)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowGlobDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowIpSans")
    def allow_ip_sans(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowIpSans"))

    @allow_ip_sans.setter
    def allow_ip_sans(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af99b2b25da83b8bd5d7982aab2d36389e57b7b7b1fb731f06e60ed88af57fe6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowIpSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowLocalhost")
    def allow_localhost(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowLocalhost"))

    @allow_localhost.setter
    def allow_localhost(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c66f51793d35c0a7baa730e25cc1eb1f9636a6d99b76640a829cfabdbf083cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowLocalhost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowSubdomains")
    def allow_subdomains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowSubdomains"))

    @allow_subdomains.setter
    def allow_subdomains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__130ac8a492f2f51d4ae235a6fac015d14b5d27556f572b04ea1770289de0398d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowSubdomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowWildcardCertificates")
    def allow_wildcard_certificates(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowWildcardCertificates"))

    @allow_wildcard_certificates.setter
    def allow_wildcard_certificates(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cb9bedbcab58bd868a0e550ab0305a867a73be77c866840efc4ba2f212455a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowWildcardCertificates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__968aaa780b19cab60f0de55c86a0cc227228fd9ca715193a5cd38a90cfa86d3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="basicConstraintsValidForNonCa")
    def basic_constraints_valid_for_non_ca(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "basicConstraintsValidForNonCa"))

    @basic_constraints_valid_for_non_ca.setter
    def basic_constraints_valid_for_non_ca(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c3aa0b3b9fcf16c176034c0cb60f9f1f691333e310b1f5ac106ebd6f8fa09f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "basicConstraintsValidForNonCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientFlag")
    def client_flag(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "clientFlag"))

    @client_flag.setter
    def client_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784b2f830bd83e1d1a46f51e20bdaf86fc6cb781522e7ece6d13ed1ac68ce3e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientFlag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cnValidations")
    def cn_validations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cnValidations"))

    @cn_validations.setter
    def cn_validations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0687a7b983c44e59142e6327928f1cae5c68a7a5f95b1a5b3996161922f202a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cnValidations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="codeSigningFlag")
    def code_signing_flag(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "codeSigningFlag"))

    @code_signing_flag.setter
    def code_signing_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d0f06a0145d2f0e59d9fce6538a31deb760380422a38c4efabcfa78a89d2d4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "codeSigningFlag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="country")
    def country(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "country"))

    @country.setter
    def country(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59761cac6990930240849d730c26652a6d80d0fc61c85649cab6d76732da62fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "country", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailProtectionFlag")
    def email_protection_flag(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "emailProtectionFlag"))

    @email_protection_flag.setter
    def email_protection_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2a01ed64d41a9906ea137076eb72f51da3e8532a4fbc4d9582c5dbaeef5fa63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailProtectionFlag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enforceHostnames")
    def enforce_hostnames(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enforceHostnames"))

    @enforce_hostnames.setter
    def enforce_hostnames(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b6f0ea385a64a2192e3022e1d82a29cbb668b5092bebab34eee232f4276f51c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enforceHostnames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extKeyUsage")
    def ext_key_usage(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extKeyUsage"))

    @ext_key_usage.setter
    def ext_key_usage(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a0d07e8fa90de8e28fa8e9697c0d2e8e433c6c1402d52ccfd2e41e9882f9004)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extKeyUsage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extKeyUsageOids")
    def ext_key_usage_oids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extKeyUsageOids"))

    @ext_key_usage_oids.setter
    def ext_key_usage_oids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97681f2e6994519baea510bb2d9227bc4a20914117afa66cd5becf30b7c38a0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extKeyUsageOids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="generateLease")
    def generate_lease(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "generateLease"))

    @generate_lease.setter
    def generate_lease(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aacb08e4491256ad48ecb20e5fd72c7054da99f11b17f6ba88360c57902a35b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateLease", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551bfaf03a79dca97e47a54d907e6a173dd410dd5a0705d249603a387326adba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerRef")
    def issuer_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerRef"))

    @issuer_ref.setter
    def issuer_ref(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f8260548e17d9ddb6bedb9d4cd76043197174217a55771d4018e379962289d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerRef", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyBits")
    def key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyBits"))

    @key_bits.setter
    def key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adbdc19d4ab8ceadf103e8d59bdf239e0c3a323901e17b2f3a00a6610133ccff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d9fa6a288f185d2a7648e37a1fd7226e72db0426c54895d437143c08753a360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyUsage")
    def key_usage(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keyUsage"))

    @key_usage.setter
    def key_usage(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__410eb31c1c97c71fc32570135527754ceff99be3eae8889797e8ef25b761d30f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyUsage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="locality")
    def locality(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0821731d9978755f452fbdd8a675f485e5b692f3c38f9a0f65c5f7906915a78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locality", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51af240a71f27344ebc7e078ca2ff6ff96a12ee7f0f78ba1c96e20b4917ddfcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__713e6e11f8222e5922411c56b258cc841e0efa57926fb57920912d018b9c4c1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b0b19fffc717ea582c3d1181472329d2049b48a28f160a9201f318b590cce62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noStore")
    def no_store(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noStore"))

    @no_store.setter
    def no_store(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae46b1b9c2ae6bff895e7e7bbefc9235de5805ce83529206c0f815d55cca9284)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noStoreMetadata")
    def no_store_metadata(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noStoreMetadata"))

    @no_store_metadata.setter
    def no_store_metadata(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8189b749eca85402f4fa14b2bb538694d167b705bae7e34b73af77c97c5fd1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noStoreMetadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @not_after.setter
    def not_after(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce4aba887d0fb1b234b9b59b4414db412a1b100fac63bd12200e7bb76b9f931f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notBeforeDuration")
    def not_before_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBeforeDuration"))

    @not_before_duration.setter
    def not_before_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fef4cd4c5dded4f906186c80d68cd025cf7789b3ab35543bdd2bb2d7da02d734)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notBeforeDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e03ad59197dde825f0a341cd6888cbde48817264c582e21629eeb35ca7938a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ou")
    def ou(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ou"))

    @ou.setter
    def ou(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d61e811590d8cbd3694391c2a2a683be2a59ff2939cfaf642c5221211f0a14d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ou", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policyIdentifiers")
    def policy_identifiers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "policyIdentifiers"))

    @policy_identifiers.setter
    def policy_identifiers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42dce68f47db94385457bf4249f1889ee72495405d764c745efd5426f87e5f75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyIdentifiers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee5a08db369fd112177b91615f01f979c3a9a7b3d5613a3b7f6b3b7a17be9cdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postalCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="province")
    def province(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "province"))

    @province.setter
    def province(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__512d57f011d1ad8a9204e299ff0e28397b9cf77dad630a91b44870a0f2882c37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "province", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requireCn")
    def require_cn(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requireCn"))

    @require_cn.setter
    def require_cn(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48a50505f5610ce8facd05eae09994e46a043d362ab575710932eace3b9ffdf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requireCn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serialNumberSource")
    def serial_number_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumberSource"))

    @serial_number_source.setter
    def serial_number_source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb89fa4f0ae17b974de4d4700e8bf1ec1897a88960b9a8147c6d5cdff337ec80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serialNumberSource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverFlag")
    def server_flag(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serverFlag"))

    @server_flag.setter
    def server_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cac3c652465c69245665c901db7d51de0efde8c3f3bdfc6c80cf75e84da68d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverFlag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureBits")
    def signature_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "signatureBits"))

    @signature_bits.setter
    def signature_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__900f86b96be311bc4ba9fde30dc118ec8db91e45c482aa2f008aa3d7795d3d18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0292635cf0053e0c5c9f3e9732fa2ead906afbbed556081fa19e9fd7e635100)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "streetAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b1f673f6c5e90e944bb063aa259034047385278b09851902f445d1ef781b786)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useCsrCommonName")
    def use_csr_common_name(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useCsrCommonName"))

    @use_csr_common_name.setter
    def use_csr_common_name(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05cd4adab5413ba4f08c35ce17a8b2b1e5c0acf4427e045b6ab6b830988f8d28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useCsrCommonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useCsrSans")
    def use_csr_sans(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useCsrSans"))

    @use_csr_sans.setter
    def use_csr_sans(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a80f3488053df8bddace5b3e904c773a83fca87659bb463cd5a068e53e570c5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useCsrSans", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__f54b1a72acc4b1bfa9dcf3e7ca3e2d4f5d3b1a45cc8bfced846bd7b6388c61e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePss", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRole.PkiSecretBackendRoleConfig",
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
        "name": "name",
        "allow_any_name": "allowAnyName",
        "allow_bare_domains": "allowBareDomains",
        "allowed_domains": "allowedDomains",
        "allowed_domains_template": "allowedDomainsTemplate",
        "allowed_other_sans": "allowedOtherSans",
        "allowed_serial_numbers": "allowedSerialNumbers",
        "allowed_uri_sans": "allowedUriSans",
        "allowed_uri_sans_template": "allowedUriSansTemplate",
        "allowed_user_ids": "allowedUserIds",
        "allow_glob_domains": "allowGlobDomains",
        "allow_ip_sans": "allowIpSans",
        "allow_localhost": "allowLocalhost",
        "allow_subdomains": "allowSubdomains",
        "allow_wildcard_certificates": "allowWildcardCertificates",
        "basic_constraints_valid_for_non_ca": "basicConstraintsValidForNonCa",
        "client_flag": "clientFlag",
        "cn_validations": "cnValidations",
        "code_signing_flag": "codeSigningFlag",
        "country": "country",
        "email_protection_flag": "emailProtectionFlag",
        "enforce_hostnames": "enforceHostnames",
        "ext_key_usage": "extKeyUsage",
        "ext_key_usage_oids": "extKeyUsageOids",
        "generate_lease": "generateLease",
        "id": "id",
        "issuer_ref": "issuerRef",
        "key_bits": "keyBits",
        "key_type": "keyType",
        "key_usage": "keyUsage",
        "locality": "locality",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "no_store": "noStore",
        "no_store_metadata": "noStoreMetadata",
        "not_after": "notAfter",
        "not_before_duration": "notBeforeDuration",
        "organization": "organization",
        "ou": "ou",
        "policy_identifier": "policyIdentifier",
        "policy_identifiers": "policyIdentifiers",
        "postal_code": "postalCode",
        "province": "province",
        "require_cn": "requireCn",
        "serial_number_source": "serialNumberSource",
        "server_flag": "serverFlag",
        "signature_bits": "signatureBits",
        "street_address": "streetAddress",
        "ttl": "ttl",
        "use_csr_common_name": "useCsrCommonName",
        "use_csr_sans": "useCsrSans",
        "use_pss": "usePss",
    },
)
class PkiSecretBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_serial_numbers: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_uri_sans_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_glob_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_ip_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_localhost: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_wildcard_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        basic_constraints_valid_for_non_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cn_validations: typing.Optional[typing.Sequence[builtins.str]] = None,
        code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        country: typing.Optional[typing.Sequence[builtins.str]] = None,
        email_protection_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ext_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        ext_key_usage_oids: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_lease: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer_ref: typing.Optional[builtins.str] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_type: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        locality: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        no_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_store_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        not_after: typing.Optional[builtins.str] = None,
        not_before_duration: typing.Optional[builtins.str] = None,
        organization: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[typing.Sequence[builtins.str]] = None,
        policy_identifier: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PkiSecretBackendRolePolicyIdentifier", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
        postal_code: typing.Optional[typing.Sequence[builtins.str]] = None,
        province: typing.Optional[typing.Sequence[builtins.str]] = None,
        require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        serial_number_source: typing.Optional[builtins.str] = None,
        server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[builtins.str] = None,
        use_csr_common_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_csr_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param backend: The path of the PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#backend PkiSecretBackendRole#backend}
        :param name: Unique name for the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#name PkiSecretBackendRole#name}
        :param allow_any_name: Flag to allow any name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_any_name PkiSecretBackendRole#allow_any_name}
        :param allow_bare_domains: Flag to allow certificates matching the actual domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_bare_domains PkiSecretBackendRole#allow_bare_domains}
        :param allowed_domains: The domains of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_domains PkiSecretBackendRole#allowed_domains}
        :param allowed_domains_template: Flag to indicate that ``allowed_domains`` specifies a template expression (e.g. {{identity.entity.aliases..name}}). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_domains_template PkiSecretBackendRole#allowed_domains_template}
        :param allowed_other_sans: Defines allowed custom SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_other_sans PkiSecretBackendRole#allowed_other_sans}
        :param allowed_serial_numbers: Defines allowed Subject serial numbers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_serial_numbers PkiSecretBackendRole#allowed_serial_numbers}
        :param allowed_uri_sans: Defines allowed URI SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_uri_sans PkiSecretBackendRole#allowed_uri_sans}
        :param allowed_uri_sans_template: Flag to indicate that ``allowed_uri_sans`` specifies a template expression (e.g. {{identity.entity.aliases..name}}). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_uri_sans_template PkiSecretBackendRole#allowed_uri_sans_template}
        :param allowed_user_ids: The allowed User ID's. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_user_ids PkiSecretBackendRole#allowed_user_ids}
        :param allow_glob_domains: Flag to allow names containing glob patterns. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_glob_domains PkiSecretBackendRole#allow_glob_domains}
        :param allow_ip_sans: Flag to allow IP SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_ip_sans PkiSecretBackendRole#allow_ip_sans}
        :param allow_localhost: Flag to allow certificates for localhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_localhost PkiSecretBackendRole#allow_localhost}
        :param allow_subdomains: Flag to allow certificates matching subdomains. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_subdomains PkiSecretBackendRole#allow_subdomains}
        :param allow_wildcard_certificates: Flag to allow wildcard certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_wildcard_certificates PkiSecretBackendRole#allow_wildcard_certificates}
        :param basic_constraints_valid_for_non_ca: Flag to mark basic constraints valid when issuing non-CA certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#basic_constraints_valid_for_non_ca PkiSecretBackendRole#basic_constraints_valid_for_non_ca}
        :param client_flag: Flag to specify certificates for client use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#client_flag PkiSecretBackendRole#client_flag}
        :param cn_validations: Specify validations to run on the Common Name field of the certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#cn_validations PkiSecretBackendRole#cn_validations}
        :param code_signing_flag: Flag to specify certificates for code signing use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#code_signing_flag PkiSecretBackendRole#code_signing_flag}
        :param country: The country of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#country PkiSecretBackendRole#country}
        :param email_protection_flag: Flag to specify certificates for email protection use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#email_protection_flag PkiSecretBackendRole#email_protection_flag}
        :param enforce_hostnames: Flag to allow only valid host names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#enforce_hostnames PkiSecretBackendRole#enforce_hostnames}
        :param ext_key_usage: Specify the allowed extended key usage constraint on issued certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ext_key_usage PkiSecretBackendRole#ext_key_usage}
        :param ext_key_usage_oids: A list of extended key usage OIDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ext_key_usage_oids PkiSecretBackendRole#ext_key_usage_oids}
        :param generate_lease: Flag to generate leases with certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#generate_lease PkiSecretBackendRole#generate_lease}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#id PkiSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer_ref: Specifies the default issuer of this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#issuer_ref PkiSecretBackendRole#issuer_ref}
        :param key_bits: The number of bits of generated keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_bits PkiSecretBackendRole#key_bits}
        :param key_type: The generated key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_type PkiSecretBackendRole#key_type}
        :param key_usage: Specify the allowed key usage constraint on issued certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_usage PkiSecretBackendRole#key_usage}
        :param locality: The locality of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#locality PkiSecretBackendRole#locality}
        :param max_ttl: The maximum TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#max_ttl PkiSecretBackendRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#namespace PkiSecretBackendRole#namespace}
        :param no_store: Flag to not store certificates in the storage backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#no_store PkiSecretBackendRole#no_store}
        :param no_store_metadata: Allows metadata to be stored keyed on the certificate's serial number. The field is independent of no_store, allowing metadata storage regardless of whether certificates are stored. If true, metadata is not stored and an error is returned if the metadata field is specified on issuance APIs Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#no_store_metadata PkiSecretBackendRole#no_store_metadata}
        :param not_after: Set the Not After field of the certificate with specified date value. The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#not_after PkiSecretBackendRole#not_after}
        :param not_before_duration: Specifies the duration by which to backdate the NotBefore property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#not_before_duration PkiSecretBackendRole#not_before_duration}
        :param organization: The organization of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#organization PkiSecretBackendRole#organization}
        :param ou: The organization unit of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ou PkiSecretBackendRole#ou}
        :param policy_identifier: policy_identifier block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#policy_identifier PkiSecretBackendRole#policy_identifier}
        :param policy_identifiers: Specify the list of allowed policies OIDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#policy_identifiers PkiSecretBackendRole#policy_identifiers}
        :param postal_code: The postal code of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#postal_code PkiSecretBackendRole#postal_code}
        :param province: The province of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#province PkiSecretBackendRole#province}
        :param require_cn: Flag to force CN usage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#require_cn PkiSecretBackendRole#require_cn}
        :param serial_number_source: Specifies the source of the subject serial number. Valid values are json-csr (default) or json. When set to json-csr, the subject serial number is taken from the serial_number parameter and falls back to the serial number in the CSR. When set to json, the subject serial number is taken from the serial_number parameter but will ignore any value in the CSR. For backwards compatibility an empty value for this field will default to the json-csr behavior. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#serial_number_source PkiSecretBackendRole#serial_number_source}
        :param server_flag: Flag to specify certificates for server use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#server_flag PkiSecretBackendRole#server_flag}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#signature_bits PkiSecretBackendRole#signature_bits}
        :param street_address: The street address of generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#street_address PkiSecretBackendRole#street_address}
        :param ttl: The TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ttl PkiSecretBackendRole#ttl}
        :param use_csr_common_name: Flag to use the CN in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_csr_common_name PkiSecretBackendRole#use_csr_common_name}
        :param use_csr_sans: Flag to use the SANs in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_csr_sans PkiSecretBackendRole#use_csr_sans}
        :param use_pss: Specifies whether or not to use PSS signatures over PKCS#1v1.5 signatures when a RSA-type issuer is used. Ignored for ECDSA/Ed25519 issuers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_pss PkiSecretBackendRole#use_pss}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f90b513ba952320bbcd9e85cdd7d19e3a338e9de625d64cf41cb16550c9abab)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allow_any_name", value=allow_any_name, expected_type=type_hints["allow_any_name"])
            check_type(argname="argument allow_bare_domains", value=allow_bare_domains, expected_type=type_hints["allow_bare_domains"])
            check_type(argname="argument allowed_domains", value=allowed_domains, expected_type=type_hints["allowed_domains"])
            check_type(argname="argument allowed_domains_template", value=allowed_domains_template, expected_type=type_hints["allowed_domains_template"])
            check_type(argname="argument allowed_other_sans", value=allowed_other_sans, expected_type=type_hints["allowed_other_sans"])
            check_type(argname="argument allowed_serial_numbers", value=allowed_serial_numbers, expected_type=type_hints["allowed_serial_numbers"])
            check_type(argname="argument allowed_uri_sans", value=allowed_uri_sans, expected_type=type_hints["allowed_uri_sans"])
            check_type(argname="argument allowed_uri_sans_template", value=allowed_uri_sans_template, expected_type=type_hints["allowed_uri_sans_template"])
            check_type(argname="argument allowed_user_ids", value=allowed_user_ids, expected_type=type_hints["allowed_user_ids"])
            check_type(argname="argument allow_glob_domains", value=allow_glob_domains, expected_type=type_hints["allow_glob_domains"])
            check_type(argname="argument allow_ip_sans", value=allow_ip_sans, expected_type=type_hints["allow_ip_sans"])
            check_type(argname="argument allow_localhost", value=allow_localhost, expected_type=type_hints["allow_localhost"])
            check_type(argname="argument allow_subdomains", value=allow_subdomains, expected_type=type_hints["allow_subdomains"])
            check_type(argname="argument allow_wildcard_certificates", value=allow_wildcard_certificates, expected_type=type_hints["allow_wildcard_certificates"])
            check_type(argname="argument basic_constraints_valid_for_non_ca", value=basic_constraints_valid_for_non_ca, expected_type=type_hints["basic_constraints_valid_for_non_ca"])
            check_type(argname="argument client_flag", value=client_flag, expected_type=type_hints["client_flag"])
            check_type(argname="argument cn_validations", value=cn_validations, expected_type=type_hints["cn_validations"])
            check_type(argname="argument code_signing_flag", value=code_signing_flag, expected_type=type_hints["code_signing_flag"])
            check_type(argname="argument country", value=country, expected_type=type_hints["country"])
            check_type(argname="argument email_protection_flag", value=email_protection_flag, expected_type=type_hints["email_protection_flag"])
            check_type(argname="argument enforce_hostnames", value=enforce_hostnames, expected_type=type_hints["enforce_hostnames"])
            check_type(argname="argument ext_key_usage", value=ext_key_usage, expected_type=type_hints["ext_key_usage"])
            check_type(argname="argument ext_key_usage_oids", value=ext_key_usage_oids, expected_type=type_hints["ext_key_usage_oids"])
            check_type(argname="argument generate_lease", value=generate_lease, expected_type=type_hints["generate_lease"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issuer_ref", value=issuer_ref, expected_type=type_hints["issuer_ref"])
            check_type(argname="argument key_bits", value=key_bits, expected_type=type_hints["key_bits"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument key_usage", value=key_usage, expected_type=type_hints["key_usage"])
            check_type(argname="argument locality", value=locality, expected_type=type_hints["locality"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument no_store", value=no_store, expected_type=type_hints["no_store"])
            check_type(argname="argument no_store_metadata", value=no_store_metadata, expected_type=type_hints["no_store_metadata"])
            check_type(argname="argument not_after", value=not_after, expected_type=type_hints["not_after"])
            check_type(argname="argument not_before_duration", value=not_before_duration, expected_type=type_hints["not_before_duration"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
            check_type(argname="argument ou", value=ou, expected_type=type_hints["ou"])
            check_type(argname="argument policy_identifier", value=policy_identifier, expected_type=type_hints["policy_identifier"])
            check_type(argname="argument policy_identifiers", value=policy_identifiers, expected_type=type_hints["policy_identifiers"])
            check_type(argname="argument postal_code", value=postal_code, expected_type=type_hints["postal_code"])
            check_type(argname="argument province", value=province, expected_type=type_hints["province"])
            check_type(argname="argument require_cn", value=require_cn, expected_type=type_hints["require_cn"])
            check_type(argname="argument serial_number_source", value=serial_number_source, expected_type=type_hints["serial_number_source"])
            check_type(argname="argument server_flag", value=server_flag, expected_type=type_hints["server_flag"])
            check_type(argname="argument signature_bits", value=signature_bits, expected_type=type_hints["signature_bits"])
            check_type(argname="argument street_address", value=street_address, expected_type=type_hints["street_address"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument use_csr_common_name", value=use_csr_common_name, expected_type=type_hints["use_csr_common_name"])
            check_type(argname="argument use_csr_sans", value=use_csr_sans, expected_type=type_hints["use_csr_sans"])
            check_type(argname="argument use_pss", value=use_pss, expected_type=type_hints["use_pss"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
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
        if allow_any_name is not None:
            self._values["allow_any_name"] = allow_any_name
        if allow_bare_domains is not None:
            self._values["allow_bare_domains"] = allow_bare_domains
        if allowed_domains is not None:
            self._values["allowed_domains"] = allowed_domains
        if allowed_domains_template is not None:
            self._values["allowed_domains_template"] = allowed_domains_template
        if allowed_other_sans is not None:
            self._values["allowed_other_sans"] = allowed_other_sans
        if allowed_serial_numbers is not None:
            self._values["allowed_serial_numbers"] = allowed_serial_numbers
        if allowed_uri_sans is not None:
            self._values["allowed_uri_sans"] = allowed_uri_sans
        if allowed_uri_sans_template is not None:
            self._values["allowed_uri_sans_template"] = allowed_uri_sans_template
        if allowed_user_ids is not None:
            self._values["allowed_user_ids"] = allowed_user_ids
        if allow_glob_domains is not None:
            self._values["allow_glob_domains"] = allow_glob_domains
        if allow_ip_sans is not None:
            self._values["allow_ip_sans"] = allow_ip_sans
        if allow_localhost is not None:
            self._values["allow_localhost"] = allow_localhost
        if allow_subdomains is not None:
            self._values["allow_subdomains"] = allow_subdomains
        if allow_wildcard_certificates is not None:
            self._values["allow_wildcard_certificates"] = allow_wildcard_certificates
        if basic_constraints_valid_for_non_ca is not None:
            self._values["basic_constraints_valid_for_non_ca"] = basic_constraints_valid_for_non_ca
        if client_flag is not None:
            self._values["client_flag"] = client_flag
        if cn_validations is not None:
            self._values["cn_validations"] = cn_validations
        if code_signing_flag is not None:
            self._values["code_signing_flag"] = code_signing_flag
        if country is not None:
            self._values["country"] = country
        if email_protection_flag is not None:
            self._values["email_protection_flag"] = email_protection_flag
        if enforce_hostnames is not None:
            self._values["enforce_hostnames"] = enforce_hostnames
        if ext_key_usage is not None:
            self._values["ext_key_usage"] = ext_key_usage
        if ext_key_usage_oids is not None:
            self._values["ext_key_usage_oids"] = ext_key_usage_oids
        if generate_lease is not None:
            self._values["generate_lease"] = generate_lease
        if id is not None:
            self._values["id"] = id
        if issuer_ref is not None:
            self._values["issuer_ref"] = issuer_ref
        if key_bits is not None:
            self._values["key_bits"] = key_bits
        if key_type is not None:
            self._values["key_type"] = key_type
        if key_usage is not None:
            self._values["key_usage"] = key_usage
        if locality is not None:
            self._values["locality"] = locality
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if no_store is not None:
            self._values["no_store"] = no_store
        if no_store_metadata is not None:
            self._values["no_store_metadata"] = no_store_metadata
        if not_after is not None:
            self._values["not_after"] = not_after
        if not_before_duration is not None:
            self._values["not_before_duration"] = not_before_duration
        if organization is not None:
            self._values["organization"] = organization
        if ou is not None:
            self._values["ou"] = ou
        if policy_identifier is not None:
            self._values["policy_identifier"] = policy_identifier
        if policy_identifiers is not None:
            self._values["policy_identifiers"] = policy_identifiers
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if province is not None:
            self._values["province"] = province
        if require_cn is not None:
            self._values["require_cn"] = require_cn
        if serial_number_source is not None:
            self._values["serial_number_source"] = serial_number_source
        if server_flag is not None:
            self._values["server_flag"] = server_flag
        if signature_bits is not None:
            self._values["signature_bits"] = signature_bits
        if street_address is not None:
            self._values["street_address"] = street_address
        if ttl is not None:
            self._values["ttl"] = ttl
        if use_csr_common_name is not None:
            self._values["use_csr_common_name"] = use_csr_common_name
        if use_csr_sans is not None:
            self._values["use_csr_sans"] = use_csr_sans
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
        '''The path of the PKI secret backend the resource belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#backend PkiSecretBackendRole#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Unique name for the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#name PkiSecretBackendRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_any_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow any name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_any_name PkiSecretBackendRole#allow_any_name}
        '''
        result = self._values.get("allow_any_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_bare_domains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow certificates matching the actual domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_bare_domains PkiSecretBackendRole#allow_bare_domains}
        '''
        result = self._values.get("allow_bare_domains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The domains of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_domains PkiSecretBackendRole#allowed_domains}
        '''
        result = self._values.get("allowed_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_domains_template(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to indicate that ``allowed_domains`` specifies a template expression (e.g. {{identity.entity.aliases..name}}).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_domains_template PkiSecretBackendRole#allowed_domains_template}
        '''
        result = self._values.get("allowed_domains_template")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_other_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Defines allowed custom SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_other_sans PkiSecretBackendRole#allowed_other_sans}
        '''
        result = self._values.get("allowed_other_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_serial_numbers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Defines allowed Subject serial numbers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_serial_numbers PkiSecretBackendRole#allowed_serial_numbers}
        '''
        result = self._values.get("allowed_serial_numbers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Defines allowed URI SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_uri_sans PkiSecretBackendRole#allowed_uri_sans}
        '''
        result = self._values.get("allowed_uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_uri_sans_template(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to indicate that ``allowed_uri_sans`` specifies a template expression (e.g. {{identity.entity.aliases..name}}).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_uri_sans_template PkiSecretBackendRole#allowed_uri_sans_template}
        '''
        result = self._values.get("allowed_uri_sans_template")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_user_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The allowed User ID's.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allowed_user_ids PkiSecretBackendRole#allowed_user_ids}
        '''
        result = self._values.get("allowed_user_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_glob_domains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow names containing glob patterns.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_glob_domains PkiSecretBackendRole#allow_glob_domains}
        '''
        result = self._values.get("allow_glob_domains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_ip_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow IP SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_ip_sans PkiSecretBackendRole#allow_ip_sans}
        '''
        result = self._values.get("allow_ip_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_localhost(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow certificates for localhost.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_localhost PkiSecretBackendRole#allow_localhost}
        '''
        result = self._values.get("allow_localhost")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_subdomains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow certificates matching subdomains.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_subdomains PkiSecretBackendRole#allow_subdomains}
        '''
        result = self._values.get("allow_subdomains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_wildcard_certificates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow wildcard certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#allow_wildcard_certificates PkiSecretBackendRole#allow_wildcard_certificates}
        '''
        result = self._values.get("allow_wildcard_certificates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def basic_constraints_valid_for_non_ca(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to mark basic constraints valid when issuing non-CA certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#basic_constraints_valid_for_non_ca PkiSecretBackendRole#basic_constraints_valid_for_non_ca}
        '''
        result = self._values.get("basic_constraints_valid_for_non_ca")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def client_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify certificates for client use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#client_flag PkiSecretBackendRole#client_flag}
        '''
        result = self._values.get("client_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cn_validations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specify validations to run on the Common Name field of the certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#cn_validations PkiSecretBackendRole#cn_validations}
        '''
        result = self._values.get("cn_validations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def code_signing_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify certificates for code signing use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#code_signing_flag PkiSecretBackendRole#code_signing_flag}
        '''
        result = self._values.get("code_signing_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def country(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The country of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#country PkiSecretBackendRole#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def email_protection_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify certificates for email protection use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#email_protection_flag PkiSecretBackendRole#email_protection_flag}
        '''
        result = self._values.get("email_protection_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enforce_hostnames(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow only valid host names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#enforce_hostnames PkiSecretBackendRole#enforce_hostnames}
        '''
        result = self._values.get("enforce_hostnames")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ext_key_usage(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specify the allowed extended key usage constraint on issued certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ext_key_usage PkiSecretBackendRole#ext_key_usage}
        '''
        result = self._values.get("ext_key_usage")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ext_key_usage_oids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of extended key usage OIDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ext_key_usage_oids PkiSecretBackendRole#ext_key_usage_oids}
        '''
        result = self._values.get("ext_key_usage_oids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def generate_lease(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to generate leases with certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#generate_lease PkiSecretBackendRole#generate_lease}
        '''
        result = self._values.get("generate_lease")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#id PkiSecretBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issuer_ref(self) -> typing.Optional[builtins.str]:
        '''Specifies the default issuer of this request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#issuer_ref PkiSecretBackendRole#issuer_ref}
        '''
        result = self._values.get("issuer_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits of generated keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_bits PkiSecretBackendRole#key_bits}
        '''
        result = self._values.get("key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''The generated key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_type PkiSecretBackendRole#key_type}
        '''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_usage(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specify the allowed key usage constraint on issued certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#key_usage PkiSecretBackendRole#key_usage}
        '''
        result = self._values.get("key_usage")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def locality(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The locality of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#locality PkiSecretBackendRole#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[builtins.str]:
        '''The maximum TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#max_ttl PkiSecretBackendRole#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#namespace PkiSecretBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_store(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to not store certificates in the storage backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#no_store PkiSecretBackendRole#no_store}
        '''
        result = self._values.get("no_store")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def no_store_metadata(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allows metadata to be stored keyed on the certificate's serial number.

        The field is independent of no_store, allowing metadata storage regardless of whether certificates are stored. If true, metadata is not stored and an error is returned if the metadata field is specified on issuance APIs

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#no_store_metadata PkiSecretBackendRole#no_store_metadata}
        '''
        result = self._values.get("no_store_metadata")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def not_after(self) -> typing.Optional[builtins.str]:
        '''Set the Not After field of the certificate with specified date value.

        The value format should be given in UTC format YYYY-MM-ddTHH:MM:SSZ. Supports the Y10K end date for IEEE 802.1AR-2018 standard devices, 9999-12-31T23:59:59Z.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#not_after PkiSecretBackendRole#not_after}
        '''
        result = self._values.get("not_after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_before_duration(self) -> typing.Optional[builtins.str]:
        '''Specifies the duration by which to backdate the NotBefore property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#not_before_duration PkiSecretBackendRole#not_before_duration}
        '''
        result = self._values.get("not_before_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The organization of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#organization PkiSecretBackendRole#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ou(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The organization unit of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ou PkiSecretBackendRole#ou}
        '''
        result = self._values.get("ou")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def policy_identifier(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendRolePolicyIdentifier"]]]:
        '''policy_identifier block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#policy_identifier PkiSecretBackendRole#policy_identifier}
        '''
        result = self._values.get("policy_identifier")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendRolePolicyIdentifier"]]], result)

    @builtins.property
    def policy_identifiers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specify the list of allowed policies OIDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#policy_identifiers PkiSecretBackendRole#policy_identifiers}
        '''
        result = self._values.get("policy_identifiers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The postal code of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#postal_code PkiSecretBackendRole#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def province(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The province of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#province PkiSecretBackendRole#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def require_cn(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to force CN usage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#require_cn PkiSecretBackendRole#require_cn}
        '''
        result = self._values.get("require_cn")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def serial_number_source(self) -> typing.Optional[builtins.str]:
        '''Specifies the source of the subject serial number.

        Valid values are json-csr (default) or json. When set to json-csr, the subject serial number is taken from the serial_number parameter and falls back to the serial number in the CSR. When set to json, the subject serial number is taken from the serial_number parameter but will ignore any value in the CSR. For backwards compatibility an empty value for this field will default to the json-csr behavior.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#serial_number_source PkiSecretBackendRole#serial_number_source}
        '''
        result = self._values.get("serial_number_source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to specify certificates for server use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#server_flag PkiSecretBackendRole#server_flag}
        '''
        result = self._values.get("server_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def signature_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits to use in the signature algorithm.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#signature_bits PkiSecretBackendRole#signature_bits}
        '''
        result = self._values.get("signature_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def street_address(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The street address of generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#street_address PkiSecretBackendRole#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''The TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#ttl PkiSecretBackendRole#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_csr_common_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to use the CN in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_csr_common_name PkiSecretBackendRole#use_csr_common_name}
        '''
        result = self._values.get("use_csr_common_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_csr_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to use the SANs in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_csr_sans PkiSecretBackendRole#use_csr_sans}
        '''
        result = self._values.get("use_csr_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_pss(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether or not to use PSS signatures over PKCS#1v1.5 signatures when a RSA-type issuer is used. Ignored for ECDSA/Ed25519 issuers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#use_pss PkiSecretBackendRole#use_pss}
        '''
        result = self._values.get("use_pss")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRole.PkiSecretBackendRolePolicyIdentifier",
    jsii_struct_bases=[],
    name_mapping={"oid": "oid", "cps": "cps", "notice": "notice"},
)
class PkiSecretBackendRolePolicyIdentifier:
    def __init__(
        self,
        *,
        oid: builtins.str,
        cps: typing.Optional[builtins.str] = None,
        notice: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param oid: OID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#oid PkiSecretBackendRole#oid}
        :param cps: Optional CPS URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#cps PkiSecretBackendRole#cps}
        :param notice: Optional notice. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#notice PkiSecretBackendRole#notice}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c664c9980dbe4099be81cb2f782b2f9333d8a0c4f218049bd1160aee63efa1af)
            check_type(argname="argument oid", value=oid, expected_type=type_hints["oid"])
            check_type(argname="argument cps", value=cps, expected_type=type_hints["cps"])
            check_type(argname="argument notice", value=notice, expected_type=type_hints["notice"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "oid": oid,
        }
        if cps is not None:
            self._values["cps"] = cps
        if notice is not None:
            self._values["notice"] = notice

    @builtins.property
    def oid(self) -> builtins.str:
        '''OID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#oid PkiSecretBackendRole#oid}
        '''
        result = self._values.get("oid")
        assert result is not None, "Required property 'oid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cps(self) -> typing.Optional[builtins.str]:
        '''Optional CPS URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#cps PkiSecretBackendRole#cps}
        '''
        result = self._values.get("cps")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notice(self) -> typing.Optional[builtins.str]:
        '''Optional notice.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_role#notice PkiSecretBackendRole#notice}
        '''
        result = self._values.get("notice")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendRolePolicyIdentifier(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PkiSecretBackendRolePolicyIdentifierList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRole.PkiSecretBackendRolePolicyIdentifierList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a1d319daa55d22532f93094de67dff3c86815e92e6d1ef3bb1f79d6501f0c407)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "PkiSecretBackendRolePolicyIdentifierOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f561729282a2e90cca07987153828651fc9fc64c7382d3835aa8629baf49450)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PkiSecretBackendRolePolicyIdentifierOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03fef8c3e8cc97475554ad90d89f1d727fb7ca890152ce53960659597874f056)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f498c9c4406d5d9904f9ccaa3ca8213bf5738e75665e7a7d96a7813a993a6382)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e171417ffd242c8533dc9498e00c2ad77a50b737fcf18afa3e142392a9294390)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendRolePolicyIdentifier]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendRolePolicyIdentifier]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendRolePolicyIdentifier]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f2ed3cbb9db55802e4f336233b32ac47fa504ca260b5f5563c3c3fb8034c0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PkiSecretBackendRolePolicyIdentifierOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendRole.PkiSecretBackendRolePolicyIdentifierOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb3cf89944b514b0adc334bb435cbce1986a1890db348040cc1684144f22f13c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCps")
    def reset_cps(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCps", []))

    @jsii.member(jsii_name="resetNotice")
    def reset_notice(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotice", []))

    @builtins.property
    @jsii.member(jsii_name="cpsInput")
    def cps_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpsInput"))

    @builtins.property
    @jsii.member(jsii_name="noticeInput")
    def notice_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "noticeInput"))

    @builtins.property
    @jsii.member(jsii_name="oidInput")
    def oid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidInput"))

    @builtins.property
    @jsii.member(jsii_name="cps")
    def cps(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cps"))

    @cps.setter
    def cps(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e2ef5694a775b48049622e5a233b2bc9a81bfc4b9112384913699ef28a18b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notice")
    def notice(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notice"))

    @notice.setter
    def notice(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b165b0ce760073ec8f33ebdaf25b938859a3468d959b9d859b4ab51be36d8c45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notice", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oid")
    def oid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oid"))

    @oid.setter
    def oid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16209db57b51ea53e668e2da96b5cbe99a7cd2752168b09af48ca2938ecea0d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendRolePolicyIdentifier]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendRolePolicyIdentifier]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendRolePolicyIdentifier]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1de6babfe7f798bb8aefdda6caba8562b127dd87062f1b87b52e8e1211cdb7ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PkiSecretBackendRole",
    "PkiSecretBackendRoleConfig",
    "PkiSecretBackendRolePolicyIdentifier",
    "PkiSecretBackendRolePolicyIdentifierList",
    "PkiSecretBackendRolePolicyIdentifierOutputReference",
]

publication.publish()

def _typecheckingstub__1dde302e3509ad6d6820978bc921b8731a84a5acab3e090045db11e5049c9c62(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    name: builtins.str,
    allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_serial_numbers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_uri_sans_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_glob_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_ip_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_localhost: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_wildcard_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    basic_constraints_valid_for_non_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cn_validations: typing.Optional[typing.Sequence[builtins.str]] = None,
    code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    country: typing.Optional[typing.Sequence[builtins.str]] = None,
    email_protection_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ext_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    ext_key_usage_oids: typing.Optional[typing.Sequence[builtins.str]] = None,
    generate_lease: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer_ref: typing.Optional[builtins.str] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_type: typing.Optional[builtins.str] = None,
    key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    locality: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    no_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    no_store_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    not_after: typing.Optional[builtins.str] = None,
    not_before_duration: typing.Optional[builtins.str] = None,
    organization: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[typing.Sequence[builtins.str]] = None,
    policy_identifier: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PkiSecretBackendRolePolicyIdentifier, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    postal_code: typing.Optional[typing.Sequence[builtins.str]] = None,
    province: typing.Optional[typing.Sequence[builtins.str]] = None,
    require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    serial_number_source: typing.Optional[builtins.str] = None,
    server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[builtins.str] = None,
    use_csr_common_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_csr_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__dfccb371d8d5c1673e87c4809146e4edbcbbe7eb96752d9d2e5999ca7bf8b769(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3e4ae93979768f420af02eed90070ba97fa1aec10dd16d86ee07650b4972de3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PkiSecretBackendRolePolicyIdentifier, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e52faef2c0fb3c0d6cdbf5c054e334799a1c7d3b69272499821ab7f168b7176(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4702407aa7f85a09489a1dc850ce9c74d16eb88a65b7f3c3bafa6dd187cb537(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879d9d584ec7a94bfd819fe1e5988356afc25cd42c7c363264d15fd09a09ed81(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fe5618998119f32e0f4b63e1c752f4c7a1e64a120bdeb7eef070d083de5f3af(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7106c19b217aa463447da8164ec97ce7e3c0ba90bf5e8b25d4adf904f11fd521(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db76a1856525340c790a815078719d5e7473c066390b3080dba20ffa4153d3f6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__438bba11178b2c2db58bd2d05df9d261f6d6f660f3fbf86733b6300e76240a70(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7a51cefd25a81260e714a9045b2bd6b9dceb12cae09e14b8a47817bd1da9ee1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c2a3b3669296d6a05b64b2c9f6ccd86cdba528acd4936c1d329d068556763f6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b97f3ba64abccc27a36eae4cae25f3aff3a848c2902cca9a7953de9ffc51705(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af99b2b25da83b8bd5d7982aab2d36389e57b7b7b1fb731f06e60ed88af57fe6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c66f51793d35c0a7baa730e25cc1eb1f9636a6d99b76640a829cfabdbf083cd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__130ac8a492f2f51d4ae235a6fac015d14b5d27556f572b04ea1770289de0398d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cb9bedbcab58bd868a0e550ab0305a867a73be77c866840efc4ba2f212455a2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__968aaa780b19cab60f0de55c86a0cc227228fd9ca715193a5cd38a90cfa86d3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c3aa0b3b9fcf16c176034c0cb60f9f1f691333e310b1f5ac106ebd6f8fa09f5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784b2f830bd83e1d1a46f51e20bdaf86fc6cb781522e7ece6d13ed1ac68ce3e7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0687a7b983c44e59142e6327928f1cae5c68a7a5f95b1a5b3996161922f202a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d0f06a0145d2f0e59d9fce6538a31deb760380422a38c4efabcfa78a89d2d4b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59761cac6990930240849d730c26652a6d80d0fc61c85649cab6d76732da62fb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2a01ed64d41a9906ea137076eb72f51da3e8532a4fbc4d9582c5dbaeef5fa63(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b6f0ea385a64a2192e3022e1d82a29cbb668b5092bebab34eee232f4276f51c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a0d07e8fa90de8e28fa8e9697c0d2e8e433c6c1402d52ccfd2e41e9882f9004(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97681f2e6994519baea510bb2d9227bc4a20914117afa66cd5becf30b7c38a0d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aacb08e4491256ad48ecb20e5fd72c7054da99f11b17f6ba88360c57902a35b2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551bfaf03a79dca97e47a54d907e6a173dd410dd5a0705d249603a387326adba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f8260548e17d9ddb6bedb9d4cd76043197174217a55771d4018e379962289d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adbdc19d4ab8ceadf103e8d59bdf239e0c3a323901e17b2f3a00a6610133ccff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d9fa6a288f185d2a7648e37a1fd7226e72db0426c54895d437143c08753a360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__410eb31c1c97c71fc32570135527754ceff99be3eae8889797e8ef25b761d30f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0821731d9978755f452fbdd8a675f485e5b692f3c38f9a0f65c5f7906915a78(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51af240a71f27344ebc7e078ca2ff6ff96a12ee7f0f78ba1c96e20b4917ddfcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__713e6e11f8222e5922411c56b258cc841e0efa57926fb57920912d018b9c4c1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b0b19fffc717ea582c3d1181472329d2049b48a28f160a9201f318b590cce62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae46b1b9c2ae6bff895e7e7bbefc9235de5805ce83529206c0f815d55cca9284(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8189b749eca85402f4fa14b2bb538694d167b705bae7e34b73af77c97c5fd1a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce4aba887d0fb1b234b9b59b4414db412a1b100fac63bd12200e7bb76b9f931f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fef4cd4c5dded4f906186c80d68cd025cf7789b3ab35543bdd2bb2d7da02d734(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e03ad59197dde825f0a341cd6888cbde48817264c582e21629eeb35ca7938a5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d61e811590d8cbd3694391c2a2a683be2a59ff2939cfaf642c5221211f0a14d0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42dce68f47db94385457bf4249f1889ee72495405d764c745efd5426f87e5f75(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee5a08db369fd112177b91615f01f979c3a9a7b3d5613a3b7f6b3b7a17be9cdf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__512d57f011d1ad8a9204e299ff0e28397b9cf77dad630a91b44870a0f2882c37(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48a50505f5610ce8facd05eae09994e46a043d362ab575710932eace3b9ffdf4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb89fa4f0ae17b974de4d4700e8bf1ec1897a88960b9a8147c6d5cdff337ec80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cac3c652465c69245665c901db7d51de0efde8c3f3bdfc6c80cf75e84da68d2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__900f86b96be311bc4ba9fde30dc118ec8db91e45c482aa2f008aa3d7795d3d18(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0292635cf0053e0c5c9f3e9732fa2ead906afbbed556081fa19e9fd7e635100(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b1f673f6c5e90e944bb063aa259034047385278b09851902f445d1ef781b786(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05cd4adab5413ba4f08c35ce17a8b2b1e5c0acf4427e045b6ab6b830988f8d28(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a80f3488053df8bddace5b3e904c773a83fca87659bb463cd5a068e53e570c5f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f54b1a72acc4b1bfa9dcf3e7ca3e2d4f5d3b1a45cc8bfced846bd7b6388c61e2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f90b513ba952320bbcd9e85cdd7d19e3a338e9de625d64cf41cb16550c9abab(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    name: builtins.str,
    allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_serial_numbers: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_uri_sans_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_user_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_glob_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_ip_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_localhost: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_wildcard_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    basic_constraints_valid_for_non_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cn_validations: typing.Optional[typing.Sequence[builtins.str]] = None,
    code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    country: typing.Optional[typing.Sequence[builtins.str]] = None,
    email_protection_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ext_key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    ext_key_usage_oids: typing.Optional[typing.Sequence[builtins.str]] = None,
    generate_lease: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer_ref: typing.Optional[builtins.str] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_type: typing.Optional[builtins.str] = None,
    key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    locality: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    no_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    no_store_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    not_after: typing.Optional[builtins.str] = None,
    not_before_duration: typing.Optional[builtins.str] = None,
    organization: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[typing.Sequence[builtins.str]] = None,
    policy_identifier: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PkiSecretBackendRolePolicyIdentifier, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_identifiers: typing.Optional[typing.Sequence[builtins.str]] = None,
    postal_code: typing.Optional[typing.Sequence[builtins.str]] = None,
    province: typing.Optional[typing.Sequence[builtins.str]] = None,
    require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    serial_number_source: typing.Optional[builtins.str] = None,
    server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[builtins.str] = None,
    use_csr_common_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_csr_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_pss: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c664c9980dbe4099be81cb2f782b2f9333d8a0c4f218049bd1160aee63efa1af(
    *,
    oid: builtins.str,
    cps: typing.Optional[builtins.str] = None,
    notice: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1d319daa55d22532f93094de67dff3c86815e92e6d1ef3bb1f79d6501f0c407(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f561729282a2e90cca07987153828651fc9fc64c7382d3835aa8629baf49450(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03fef8c3e8cc97475554ad90d89f1d727fb7ca890152ce53960659597874f056(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f498c9c4406d5d9904f9ccaa3ca8213bf5738e75665e7a7d96a7813a993a6382(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e171417ffd242c8533dc9498e00c2ad77a50b737fcf18afa3e142392a9294390(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f2ed3cbb9db55802e4f336233b32ac47fa504ca260b5f5563c3c3fb8034c0b9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendRolePolicyIdentifier]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb3cf89944b514b0adc334bb435cbce1986a1890db348040cc1684144f22f13c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e2ef5694a775b48049622e5a233b2bc9a81bfc4b9112384913699ef28a18b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b165b0ce760073ec8f33ebdaf25b938859a3468d959b9d859b4ab51be36d8c45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16209db57b51ea53e668e2da96b5cbe99a7cd2752168b09af48ca2938ecea0d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1de6babfe7f798bb8aefdda6caba8562b127dd87062f1b87b52e8e1211cdb7ae(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendRolePolicyIdentifier]],
) -> None:
    """Type checking stubs"""
    pass
