r'''
# `vault_cert_auth_backend_role`

Refer to the Terraform Registry for docs: [`vault_cert_auth_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role).
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


class CertAuthBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.certAuthBackendRole.CertAuthBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role vault_cert_auth_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        certificate: builtins.str,
        name: builtins.str,
        allowed_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        backend: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        ocsp_ca_certificates: typing.Optional[builtins.str] = None,
        ocsp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_fail_open: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_query_all_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_servers_override: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role vault_cert_auth_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#certificate CertAuthBackendRole#certificate}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#name CertAuthBackendRole#name}.
        :param allowed_common_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_common_names CertAuthBackendRole#allowed_common_names}.
        :param allowed_dns_sans: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_dns_sans CertAuthBackendRole#allowed_dns_sans}.
        :param allowed_email_sans: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_email_sans CertAuthBackendRole#allowed_email_sans}.
        :param allowed_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_names CertAuthBackendRole#allowed_names}.
        :param allowed_organizational_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_organizational_units CertAuthBackendRole#allowed_organizational_units}.
        :param allowed_uri_sans: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_uri_sans CertAuthBackendRole#allowed_uri_sans}.
        :param backend: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#backend CertAuthBackendRole#backend}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#display_name CertAuthBackendRole#display_name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#id CertAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#namespace CertAuthBackendRole#namespace}
        :param ocsp_ca_certificates: Any additional CA certificates needed to verify OCSP responses. Provided as base64 encoded PEM data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_ca_certificates CertAuthBackendRole#ocsp_ca_certificates}
        :param ocsp_enabled: If enabled, validate certificates' revocation status using OCSP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_enabled CertAuthBackendRole#ocsp_enabled}
        :param ocsp_fail_open: If true and an OCSP response cannot be fetched or is of an unknown status, the login will proceed as if the certificate has not been revoked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_fail_open CertAuthBackendRole#ocsp_fail_open}
        :param ocsp_query_all_servers: If set to true, rather than accepting the first successful OCSP response, query all servers and consider the certificate valid only if all servers agree. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_query_all_servers CertAuthBackendRole#ocsp_query_all_servers}
        :param ocsp_servers_override: A comma-separated list of OCSP server addresses. If unset, the OCSP server is determined from the AuthorityInformationAccess extension on the certificate being inspected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_servers_override CertAuthBackendRole#ocsp_servers_override}
        :param required_extensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#required_extensions CertAuthBackendRole#required_extensions}.
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_bound_cidrs CertAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_explicit_max_ttl CertAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_max_ttl CertAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_no_default_policy CertAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_num_uses CertAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_period CertAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_policies CertAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_ttl CertAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_type CertAuthBackendRole#token_type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f740e98e3e8bfb1cf72bd0cc64b18b244a97aea1dde90a8dafde4b27e46193d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CertAuthBackendRoleConfig(
            certificate=certificate,
            name=name,
            allowed_common_names=allowed_common_names,
            allowed_dns_sans=allowed_dns_sans,
            allowed_email_sans=allowed_email_sans,
            allowed_names=allowed_names,
            allowed_organizational_units=allowed_organizational_units,
            allowed_uri_sans=allowed_uri_sans,
            backend=backend,
            display_name=display_name,
            id=id,
            namespace=namespace,
            ocsp_ca_certificates=ocsp_ca_certificates,
            ocsp_enabled=ocsp_enabled,
            ocsp_fail_open=ocsp_fail_open,
            ocsp_query_all_servers=ocsp_query_all_servers,
            ocsp_servers_override=ocsp_servers_override,
            required_extensions=required_extensions,
            token_bound_cidrs=token_bound_cidrs,
            token_explicit_max_ttl=token_explicit_max_ttl,
            token_max_ttl=token_max_ttl,
            token_no_default_policy=token_no_default_policy,
            token_num_uses=token_num_uses,
            token_period=token_period,
            token_policies=token_policies,
            token_ttl=token_ttl,
            token_type=token_type,
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
        '''Generates CDKTF code for importing a CertAuthBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CertAuthBackendRole to import.
        :param import_from_id: The id of the existing CertAuthBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CertAuthBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1aefd65491d3fa8ca469e67666ae22c1add6b7c78d40ff596adaf04c0a6c267b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedCommonNames")
    def reset_allowed_common_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedCommonNames", []))

    @jsii.member(jsii_name="resetAllowedDnsSans")
    def reset_allowed_dns_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDnsSans", []))

    @jsii.member(jsii_name="resetAllowedEmailSans")
    def reset_allowed_email_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedEmailSans", []))

    @jsii.member(jsii_name="resetAllowedNames")
    def reset_allowed_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedNames", []))

    @jsii.member(jsii_name="resetAllowedOrganizationalUnits")
    def reset_allowed_organizational_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedOrganizationalUnits", []))

    @jsii.member(jsii_name="resetAllowedUriSans")
    def reset_allowed_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUriSans", []))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOcspCaCertificates")
    def reset_ocsp_ca_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspCaCertificates", []))

    @jsii.member(jsii_name="resetOcspEnabled")
    def reset_ocsp_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspEnabled", []))

    @jsii.member(jsii_name="resetOcspFailOpen")
    def reset_ocsp_fail_open(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspFailOpen", []))

    @jsii.member(jsii_name="resetOcspQueryAllServers")
    def reset_ocsp_query_all_servers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspQueryAllServers", []))

    @jsii.member(jsii_name="resetOcspServersOverride")
    def reset_ocsp_servers_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspServersOverride", []))

    @jsii.member(jsii_name="resetRequiredExtensions")
    def reset_required_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredExtensions", []))

    @jsii.member(jsii_name="resetTokenBoundCidrs")
    def reset_token_bound_cidrs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenBoundCidrs", []))

    @jsii.member(jsii_name="resetTokenExplicitMaxTtl")
    def reset_token_explicit_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenExplicitMaxTtl", []))

    @jsii.member(jsii_name="resetTokenMaxTtl")
    def reset_token_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenMaxTtl", []))

    @jsii.member(jsii_name="resetTokenNoDefaultPolicy")
    def reset_token_no_default_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenNoDefaultPolicy", []))

    @jsii.member(jsii_name="resetTokenNumUses")
    def reset_token_num_uses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenNumUses", []))

    @jsii.member(jsii_name="resetTokenPeriod")
    def reset_token_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenPeriod", []))

    @jsii.member(jsii_name="resetTokenPolicies")
    def reset_token_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenPolicies", []))

    @jsii.member(jsii_name="resetTokenTtl")
    def reset_token_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenTtl", []))

    @jsii.member(jsii_name="resetTokenType")
    def reset_token_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenType", []))

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
    @jsii.member(jsii_name="allowedCommonNamesInput")
    def allowed_common_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedCommonNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDnsSansInput")
    def allowed_dns_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedDnsSansInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedEmailSansInput")
    def allowed_email_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedEmailSansInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedNamesInput")
    def allowed_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedOrganizationalUnitsInput")
    def allowed_organizational_units_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedOrganizationalUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUriSansInput")
    def allowed_uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspCaCertificatesInput")
    def ocsp_ca_certificates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ocspCaCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspEnabledInput")
    def ocsp_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ocspEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspFailOpenInput")
    def ocsp_fail_open_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ocspFailOpenInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspQueryAllServersInput")
    def ocsp_query_all_servers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ocspQueryAllServersInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspServersOverrideInput")
    def ocsp_servers_override_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ocspServersOverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredExtensionsInput")
    def required_extensions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "requiredExtensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenBoundCidrsInput")
    def token_bound_cidrs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tokenBoundCidrsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenExplicitMaxTtlInput")
    def token_explicit_max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenExplicitMaxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtlInput")
    def token_max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenMaxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenNoDefaultPolicyInput")
    def token_no_default_policy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tokenNoDefaultPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenNumUsesInput")
    def token_num_uses_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenNumUsesInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenPeriodInput")
    def token_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenPoliciesInput")
    def token_policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tokenPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenTtlInput")
    def token_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenTypeInput")
    def token_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedCommonNames")
    def allowed_common_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedCommonNames"))

    @allowed_common_names.setter
    def allowed_common_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d1c93d000ed6b72c7d3d8bed68ae99fa832bec2f39e9a4abcc6b792c3e24bc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedCommonNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedDnsSans")
    def allowed_dns_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedDnsSans"))

    @allowed_dns_sans.setter
    def allowed_dns_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b7f5ece7321e0f284eb4d5ff0eb02fa18a3060fabafd61a280b1da1686e3a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDnsSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedEmailSans")
    def allowed_email_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedEmailSans"))

    @allowed_email_sans.setter
    def allowed_email_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3383d9bc67af3888142864295f30b7f4a9c2d4c5c53c8e118a5c7999df532daf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedEmailSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedNames")
    def allowed_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedNames"))

    @allowed_names.setter
    def allowed_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b247b46554d086b9ffcbac786e7b072d3d818e21545ffc93991abd1a7e8cec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedOrganizationalUnits")
    def allowed_organizational_units(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedOrganizationalUnits"))

    @allowed_organizational_units.setter
    def allowed_organizational_units(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2942209978e0d5548bc05a6e38054f163a1babec407306f9bef2b535df85605)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedOrganizationalUnits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedUriSans")
    def allowed_uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUriSans"))

    @allowed_uri_sans.setter
    def allowed_uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cb8f7a4755389e8253e76ad5d7c80656baf8aeff77053be45118f8a19a06589)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUriSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6eb8017153f5a8a8706d982a1cf8cd0f0443d40bffb5765b37a47faa27fb3687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e941800fb5f78aafeae76369819961bc7787af0ace7e4501fd3b9bd12f648cdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64653d7be60f9f6c34edcbe244fb5d964d83f5706a667932b3eac861b691c988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__873b664a489404bbf07fe8088320081a021aca739d2cd3b4cc5e3f77a4a495d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__659c4676ce75505c6f29075203b39976fd688c3e8f82986847012977f277d395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c53a0a6f5295b8afe4b8b675ceb51d9f522778d809ed29ff14c555dbd22d883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspCaCertificates")
    def ocsp_ca_certificates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ocspCaCertificates"))

    @ocsp_ca_certificates.setter
    def ocsp_ca_certificates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21c00a68a3fea96861ffb7a517f667d626a480627e5602f42b60c032d4493d67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspCaCertificates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspEnabled")
    def ocsp_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ocspEnabled"))

    @ocsp_enabled.setter
    def ocsp_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5185d5ef3427f0cf5fc633e664938959e35527a997c6d12805d48c464902c92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspFailOpen")
    def ocsp_fail_open(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ocspFailOpen"))

    @ocsp_fail_open.setter
    def ocsp_fail_open(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b89c6a7a528b4b100c27877aeba1a134282e6bdaa40a560418e746a4a29eb9cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspFailOpen", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspQueryAllServers")
    def ocsp_query_all_servers(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ocspQueryAllServers"))

    @ocsp_query_all_servers.setter
    def ocsp_query_all_servers(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39c454c2b8c1865427f3fc9f245900eb38834ca269b6c1895c5914d9683ca034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspQueryAllServers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspServersOverride")
    def ocsp_servers_override(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ocspServersOverride"))

    @ocsp_servers_override.setter
    def ocsp_servers_override(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c84f01fa1739b20111747f7e8c32fe08d87010a041a96b9059842463a4cf727e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspServersOverride", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredExtensions")
    def required_extensions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "requiredExtensions"))

    @required_extensions.setter
    def required_extensions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cdebb8c29186c42ca221af36c874184f8dda79e744059faded5810b37f2ce1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredExtensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenBoundCidrs")
    def token_bound_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenBoundCidrs"))

    @token_bound_cidrs.setter
    def token_bound_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__794be8932f3578cfa047c27e0f994d702f5bfd36dc8dd2ae05d96859d38ee54b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenBoundCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenExplicitMaxTtl")
    def token_explicit_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenExplicitMaxTtl"))

    @token_explicit_max_ttl.setter
    def token_explicit_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06c51c8a9cd1994a1e1334ac9ca005ecac1203fa3f558dda9159c3d2a2f587bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenExplicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtl")
    def token_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenMaxTtl"))

    @token_max_ttl.setter
    def token_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3478986c8d9d82cd83d79a16824aac617a174112827777477e2e6097b37bf5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNoDefaultPolicy")
    def token_no_default_policy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tokenNoDefaultPolicy"))

    @token_no_default_policy.setter
    def token_no_default_policy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa474c12a792ee4e7f29ffc0b9291b919f9360213aa7f86aa530898e858d3873)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNoDefaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNumUses")
    def token_num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenNumUses"))

    @token_num_uses.setter
    def token_num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__303e79c5a0cbbc968fe4fadc1fd55280fe8fa03d60cb90c79fe73fa7b1495bc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNumUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPeriod")
    def token_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenPeriod"))

    @token_period.setter
    def token_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4562e70dc659b822747995d98787c43805606fa30dbd86eaccb5fedf2ed3fbfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPolicies")
    def token_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenPolicies"))

    @token_policies.setter
    def token_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ea350883ef05ab27c0e086ffa8c81d5fcf39e6129ce436678b2d3e4a45dd050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenTtl")
    def token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenTtl"))

    @token_ttl.setter
    def token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1a2ee90d3c306a6e83c54ec0f6e8bd52bb3d5e31736bb5b8092112e77cc8681)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenType")
    def token_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenType"))

    @token_type.setter
    def token_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b5df6157ed857a423f7aec8672998816a1f061ab8a54c9c612a396c56f7df6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenType", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.certAuthBackendRole.CertAuthBackendRoleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "certificate": "certificate",
        "name": "name",
        "allowed_common_names": "allowedCommonNames",
        "allowed_dns_sans": "allowedDnsSans",
        "allowed_email_sans": "allowedEmailSans",
        "allowed_names": "allowedNames",
        "allowed_organizational_units": "allowedOrganizationalUnits",
        "allowed_uri_sans": "allowedUriSans",
        "backend": "backend",
        "display_name": "displayName",
        "id": "id",
        "namespace": "namespace",
        "ocsp_ca_certificates": "ocspCaCertificates",
        "ocsp_enabled": "ocspEnabled",
        "ocsp_fail_open": "ocspFailOpen",
        "ocsp_query_all_servers": "ocspQueryAllServers",
        "ocsp_servers_override": "ocspServersOverride",
        "required_extensions": "requiredExtensions",
        "token_bound_cidrs": "tokenBoundCidrs",
        "token_explicit_max_ttl": "tokenExplicitMaxTtl",
        "token_max_ttl": "tokenMaxTtl",
        "token_no_default_policy": "tokenNoDefaultPolicy",
        "token_num_uses": "tokenNumUses",
        "token_period": "tokenPeriod",
        "token_policies": "tokenPolicies",
        "token_ttl": "tokenTtl",
        "token_type": "tokenType",
    },
)
class CertAuthBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        certificate: builtins.str,
        name: builtins.str,
        allowed_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        backend: typing.Optional[builtins.str] = None,
        display_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        ocsp_ca_certificates: typing.Optional[builtins.str] = None,
        ocsp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_fail_open: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_query_all_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_servers_override: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#certificate CertAuthBackendRole#certificate}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#name CertAuthBackendRole#name}.
        :param allowed_common_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_common_names CertAuthBackendRole#allowed_common_names}.
        :param allowed_dns_sans: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_dns_sans CertAuthBackendRole#allowed_dns_sans}.
        :param allowed_email_sans: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_email_sans CertAuthBackendRole#allowed_email_sans}.
        :param allowed_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_names CertAuthBackendRole#allowed_names}.
        :param allowed_organizational_units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_organizational_units CertAuthBackendRole#allowed_organizational_units}.
        :param allowed_uri_sans: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_uri_sans CertAuthBackendRole#allowed_uri_sans}.
        :param backend: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#backend CertAuthBackendRole#backend}.
        :param display_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#display_name CertAuthBackendRole#display_name}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#id CertAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#namespace CertAuthBackendRole#namespace}
        :param ocsp_ca_certificates: Any additional CA certificates needed to verify OCSP responses. Provided as base64 encoded PEM data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_ca_certificates CertAuthBackendRole#ocsp_ca_certificates}
        :param ocsp_enabled: If enabled, validate certificates' revocation status using OCSP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_enabled CertAuthBackendRole#ocsp_enabled}
        :param ocsp_fail_open: If true and an OCSP response cannot be fetched or is of an unknown status, the login will proceed as if the certificate has not been revoked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_fail_open CertAuthBackendRole#ocsp_fail_open}
        :param ocsp_query_all_servers: If set to true, rather than accepting the first successful OCSP response, query all servers and consider the certificate valid only if all servers agree. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_query_all_servers CertAuthBackendRole#ocsp_query_all_servers}
        :param ocsp_servers_override: A comma-separated list of OCSP server addresses. If unset, the OCSP server is determined from the AuthorityInformationAccess extension on the certificate being inspected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_servers_override CertAuthBackendRole#ocsp_servers_override}
        :param required_extensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#required_extensions CertAuthBackendRole#required_extensions}.
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_bound_cidrs CertAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_explicit_max_ttl CertAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_max_ttl CertAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_no_default_policy CertAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_num_uses CertAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_period CertAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_policies CertAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_ttl CertAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_type CertAuthBackendRole#token_type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3615ea055c5a0ef60b6758a48def2ea8b32c8afe38dc73a75471cb834e41aef9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allowed_common_names", value=allowed_common_names, expected_type=type_hints["allowed_common_names"])
            check_type(argname="argument allowed_dns_sans", value=allowed_dns_sans, expected_type=type_hints["allowed_dns_sans"])
            check_type(argname="argument allowed_email_sans", value=allowed_email_sans, expected_type=type_hints["allowed_email_sans"])
            check_type(argname="argument allowed_names", value=allowed_names, expected_type=type_hints["allowed_names"])
            check_type(argname="argument allowed_organizational_units", value=allowed_organizational_units, expected_type=type_hints["allowed_organizational_units"])
            check_type(argname="argument allowed_uri_sans", value=allowed_uri_sans, expected_type=type_hints["allowed_uri_sans"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument ocsp_ca_certificates", value=ocsp_ca_certificates, expected_type=type_hints["ocsp_ca_certificates"])
            check_type(argname="argument ocsp_enabled", value=ocsp_enabled, expected_type=type_hints["ocsp_enabled"])
            check_type(argname="argument ocsp_fail_open", value=ocsp_fail_open, expected_type=type_hints["ocsp_fail_open"])
            check_type(argname="argument ocsp_query_all_servers", value=ocsp_query_all_servers, expected_type=type_hints["ocsp_query_all_servers"])
            check_type(argname="argument ocsp_servers_override", value=ocsp_servers_override, expected_type=type_hints["ocsp_servers_override"])
            check_type(argname="argument required_extensions", value=required_extensions, expected_type=type_hints["required_extensions"])
            check_type(argname="argument token_bound_cidrs", value=token_bound_cidrs, expected_type=type_hints["token_bound_cidrs"])
            check_type(argname="argument token_explicit_max_ttl", value=token_explicit_max_ttl, expected_type=type_hints["token_explicit_max_ttl"])
            check_type(argname="argument token_max_ttl", value=token_max_ttl, expected_type=type_hints["token_max_ttl"])
            check_type(argname="argument token_no_default_policy", value=token_no_default_policy, expected_type=type_hints["token_no_default_policy"])
            check_type(argname="argument token_num_uses", value=token_num_uses, expected_type=type_hints["token_num_uses"])
            check_type(argname="argument token_period", value=token_period, expected_type=type_hints["token_period"])
            check_type(argname="argument token_policies", value=token_policies, expected_type=type_hints["token_policies"])
            check_type(argname="argument token_ttl", value=token_ttl, expected_type=type_hints["token_ttl"])
            check_type(argname="argument token_type", value=token_type, expected_type=type_hints["token_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "certificate": certificate,
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
        if allowed_common_names is not None:
            self._values["allowed_common_names"] = allowed_common_names
        if allowed_dns_sans is not None:
            self._values["allowed_dns_sans"] = allowed_dns_sans
        if allowed_email_sans is not None:
            self._values["allowed_email_sans"] = allowed_email_sans
        if allowed_names is not None:
            self._values["allowed_names"] = allowed_names
        if allowed_organizational_units is not None:
            self._values["allowed_organizational_units"] = allowed_organizational_units
        if allowed_uri_sans is not None:
            self._values["allowed_uri_sans"] = allowed_uri_sans
        if backend is not None:
            self._values["backend"] = backend
        if display_name is not None:
            self._values["display_name"] = display_name
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if ocsp_ca_certificates is not None:
            self._values["ocsp_ca_certificates"] = ocsp_ca_certificates
        if ocsp_enabled is not None:
            self._values["ocsp_enabled"] = ocsp_enabled
        if ocsp_fail_open is not None:
            self._values["ocsp_fail_open"] = ocsp_fail_open
        if ocsp_query_all_servers is not None:
            self._values["ocsp_query_all_servers"] = ocsp_query_all_servers
        if ocsp_servers_override is not None:
            self._values["ocsp_servers_override"] = ocsp_servers_override
        if required_extensions is not None:
            self._values["required_extensions"] = required_extensions
        if token_bound_cidrs is not None:
            self._values["token_bound_cidrs"] = token_bound_cidrs
        if token_explicit_max_ttl is not None:
            self._values["token_explicit_max_ttl"] = token_explicit_max_ttl
        if token_max_ttl is not None:
            self._values["token_max_ttl"] = token_max_ttl
        if token_no_default_policy is not None:
            self._values["token_no_default_policy"] = token_no_default_policy
        if token_num_uses is not None:
            self._values["token_num_uses"] = token_num_uses
        if token_period is not None:
            self._values["token_period"] = token_period
        if token_policies is not None:
            self._values["token_policies"] = token_policies
        if token_ttl is not None:
            self._values["token_ttl"] = token_ttl
        if token_type is not None:
            self._values["token_type"] = token_type

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
    def certificate(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#certificate CertAuthBackendRole#certificate}.'''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#name CertAuthBackendRole#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_common_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_common_names CertAuthBackendRole#allowed_common_names}.'''
        result = self._values.get("allowed_common_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_dns_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_dns_sans CertAuthBackendRole#allowed_dns_sans}.'''
        result = self._values.get("allowed_dns_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_email_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_email_sans CertAuthBackendRole#allowed_email_sans}.'''
        result = self._values.get("allowed_email_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_names CertAuthBackendRole#allowed_names}.'''
        result = self._values.get("allowed_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_organizational_units(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_organizational_units CertAuthBackendRole#allowed_organizational_units}.'''
        result = self._values.get("allowed_organizational_units")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#allowed_uri_sans CertAuthBackendRole#allowed_uri_sans}.'''
        result = self._values.get("allowed_uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#backend CertAuthBackendRole#backend}.'''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#display_name CertAuthBackendRole#display_name}.'''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#id CertAuthBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#namespace CertAuthBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ocsp_ca_certificates(self) -> typing.Optional[builtins.str]:
        '''Any additional CA certificates needed to verify OCSP responses. Provided as base64 encoded PEM data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_ca_certificates CertAuthBackendRole#ocsp_ca_certificates}
        '''
        result = self._values.get("ocsp_ca_certificates")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ocsp_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If enabled, validate certificates' revocation status using OCSP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_enabled CertAuthBackendRole#ocsp_enabled}
        '''
        result = self._values.get("ocsp_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ocsp_fail_open(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true and an OCSP response cannot be fetched or is of an unknown status, the login will proceed as if the certificate has not been revoked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_fail_open CertAuthBackendRole#ocsp_fail_open}
        '''
        result = self._values.get("ocsp_fail_open")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ocsp_query_all_servers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, rather than accepting the first successful OCSP response, query all servers and consider the certificate valid only if all servers agree.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_query_all_servers CertAuthBackendRole#ocsp_query_all_servers}
        '''
        result = self._values.get("ocsp_query_all_servers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ocsp_servers_override(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated list of OCSP server addresses.

        If unset, the OCSP server is determined from the AuthorityInformationAccess extension on the certificate being inspected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#ocsp_servers_override CertAuthBackendRole#ocsp_servers_override}
        '''
        result = self._values.get("ocsp_servers_override")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def required_extensions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#required_extensions CertAuthBackendRole#required_extensions}.'''
        result = self._values.get("required_extensions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_bound_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the blocks of IP addresses which are allowed to use the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_bound_cidrs CertAuthBackendRole#token_bound_cidrs}
        '''
        result = self._values.get("token_bound_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_explicit_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Explicit Maximum TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_explicit_max_ttl CertAuthBackendRole#token_explicit_max_ttl}
        '''
        result = self._values.get("token_explicit_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''The maximum lifetime of the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_max_ttl CertAuthBackendRole#token_max_ttl}
        '''
        result = self._values.get("token_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_no_default_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the 'default' policy will not automatically be added to generated tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_no_default_policy CertAuthBackendRole#token_no_default_policy}
        '''
        result = self._values.get("token_no_default_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_num_uses(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times a token may be used, a value of zero means unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_num_uses CertAuthBackendRole#token_num_uses}
        '''
        result = self._values.get("token_num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_period(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_period CertAuthBackendRole#token_period}
        '''
        result = self._values.get("token_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Generated Token's Policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_policies CertAuthBackendRole#token_policies}
        '''
        result = self._values.get("token_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The initial ttl of the token to generate in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_ttl CertAuthBackendRole#token_ttl}
        '''
        result = self._values.get("token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_type(self) -> typing.Optional[builtins.str]:
        '''The type of token to generate, service or batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/cert_auth_backend_role#token_type CertAuthBackendRole#token_type}
        '''
        result = self._values.get("token_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertAuthBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CertAuthBackendRole",
    "CertAuthBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__0f740e98e3e8bfb1cf72bd0cc64b18b244a97aea1dde90a8dafde4b27e46193d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    certificate: builtins.str,
    name: builtins.str,
    allowed_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    backend: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    ocsp_ca_certificates: typing.Optional[builtins.str] = None,
    ocsp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_fail_open: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_query_all_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_servers_override: typing.Optional[typing.Sequence[builtins.str]] = None,
    required_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__1aefd65491d3fa8ca469e67666ae22c1add6b7c78d40ff596adaf04c0a6c267b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1c93d000ed6b72c7d3d8bed68ae99fa832bec2f39e9a4abcc6b792c3e24bc1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b7f5ece7321e0f284eb4d5ff0eb02fa18a3060fabafd61a280b1da1686e3a4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3383d9bc67af3888142864295f30b7f4a9c2d4c5c53c8e118a5c7999df532daf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b247b46554d086b9ffcbac786e7b072d3d818e21545ffc93991abd1a7e8cec(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2942209978e0d5548bc05a6e38054f163a1babec407306f9bef2b535df85605(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cb8f7a4755389e8253e76ad5d7c80656baf8aeff77053be45118f8a19a06589(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6eb8017153f5a8a8706d982a1cf8cd0f0443d40bffb5765b37a47faa27fb3687(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e941800fb5f78aafeae76369819961bc7787af0ace7e4501fd3b9bd12f648cdf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64653d7be60f9f6c34edcbe244fb5d964d83f5706a667932b3eac861b691c988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__873b664a489404bbf07fe8088320081a021aca739d2cd3b4cc5e3f77a4a495d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__659c4676ce75505c6f29075203b39976fd688c3e8f82986847012977f277d395(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c53a0a6f5295b8afe4b8b675ceb51d9f522778d809ed29ff14c555dbd22d883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21c00a68a3fea96861ffb7a517f667d626a480627e5602f42b60c032d4493d67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5185d5ef3427f0cf5fc633e664938959e35527a997c6d12805d48c464902c92(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b89c6a7a528b4b100c27877aeba1a134282e6bdaa40a560418e746a4a29eb9cf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39c454c2b8c1865427f3fc9f245900eb38834ca269b6c1895c5914d9683ca034(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c84f01fa1739b20111747f7e8c32fe08d87010a041a96b9059842463a4cf727e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cdebb8c29186c42ca221af36c874184f8dda79e744059faded5810b37f2ce1e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794be8932f3578cfa047c27e0f994d702f5bfd36dc8dd2ae05d96859d38ee54b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06c51c8a9cd1994a1e1334ac9ca005ecac1203fa3f558dda9159c3d2a2f587bb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3478986c8d9d82cd83d79a16824aac617a174112827777477e2e6097b37bf5f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa474c12a792ee4e7f29ffc0b9291b919f9360213aa7f86aa530898e858d3873(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__303e79c5a0cbbc968fe4fadc1fd55280fe8fa03d60cb90c79fe73fa7b1495bc8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4562e70dc659b822747995d98787c43805606fa30dbd86eaccb5fedf2ed3fbfb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ea350883ef05ab27c0e086ffa8c81d5fcf39e6129ce436678b2d3e4a45dd050(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1a2ee90d3c306a6e83c54ec0f6e8bd52bb3d5e31736bb5b8092112e77cc8681(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b5df6157ed857a423f7aec8672998816a1f061ab8a54c9c612a396c56f7df6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3615ea055c5a0ef60b6758a48def2ea8b32c8afe38dc73a75471cb834e41aef9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    certificate: builtins.str,
    name: builtins.str,
    allowed_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    backend: typing.Optional[builtins.str] = None,
    display_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    ocsp_ca_certificates: typing.Optional[builtins.str] = None,
    ocsp_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_fail_open: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_query_all_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_servers_override: typing.Optional[typing.Sequence[builtins.str]] = None,
    required_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
