r'''
# `provider`

Refer to the Terraform Registry for docs: [`vault`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs).
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


class VaultProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.provider.VaultProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs vault}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        add_address_to_env: typing.Optional[builtins.str] = None,
        address: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        auth_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_aws: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginAws", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_azure: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginAzure", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_cert: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginCert", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginGcp", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginJwt", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_kerberos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginKerberos", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_oci: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginOci", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_oidc: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginOidc", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_radius: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginRadius", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_token_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginTokenFile", typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_userpass: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderAuthLoginUserpass", typing.Dict[builtins.str, typing.Any]]]]] = None,
        ca_cert_dir: typing.Optional[builtins.str] = None,
        ca_cert_file: typing.Optional[builtins.str] = None,
        client_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderClientAuth", typing.Dict[builtins.str, typing.Any]]]]] = None,
        headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        max_retries_ccc: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        set_namespace_from_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_child_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_get_vault_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_server_name: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
        token_name: typing.Optional[builtins.str] = None,
        vault_version_override: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs vault} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param add_address_to_env: If true, adds the value of the ``address`` argument to the Terraform process environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#add_address_to_env VaultProvider#add_address_to_env}
        :param address: URL of the root of the target Vault server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#address VaultProvider#address}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#alias VaultProvider#alias}
        :param auth_login: auth_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login VaultProvider#auth_login}
        :param auth_login_aws: auth_login_aws block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_aws VaultProvider#auth_login_aws}
        :param auth_login_azure: auth_login_azure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_azure VaultProvider#auth_login_azure}
        :param auth_login_cert: auth_login_cert block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_cert VaultProvider#auth_login_cert}
        :param auth_login_gcp: auth_login_gcp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_gcp VaultProvider#auth_login_gcp}
        :param auth_login_jwt: auth_login_jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_jwt VaultProvider#auth_login_jwt}
        :param auth_login_kerberos: auth_login_kerberos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_kerberos VaultProvider#auth_login_kerberos}
        :param auth_login_oci: auth_login_oci block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_oci VaultProvider#auth_login_oci}
        :param auth_login_oidc: auth_login_oidc block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_oidc VaultProvider#auth_login_oidc}
        :param auth_login_radius: auth_login_radius block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_radius VaultProvider#auth_login_radius}
        :param auth_login_token_file: auth_login_token_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_token_file VaultProvider#auth_login_token_file}
        :param auth_login_userpass: auth_login_userpass block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_userpass VaultProvider#auth_login_userpass}
        :param ca_cert_dir: Path to directory containing CA certificate files to validate the server's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#ca_cert_dir VaultProvider#ca_cert_dir}
        :param ca_cert_file: Path to a CA certificate file to validate the server's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#ca_cert_file VaultProvider#ca_cert_file}
        :param client_auth: client_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#client_auth VaultProvider#client_auth}
        :param headers: headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#headers VaultProvider#headers}
        :param max_lease_ttl_seconds: Maximum TTL for secret leases requested by this provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_lease_ttl_seconds VaultProvider#max_lease_ttl_seconds}
        :param max_retries: Maximum number of retries when a 5xx error code is encountered. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_retries VaultProvider#max_retries}
        :param max_retries_ccc: Maximum number of retries for Client Controlled Consistency related operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_retries_ccc VaultProvider#max_retries_ccc}
        :param namespace: The namespace to use. Available only for Vault Enterprise. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param set_namespace_from_token: In the case where the Vault token is for a specific namespace and the provider namespace is not configured, use the token namespace as the root namespace for all resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#set_namespace_from_token VaultProvider#set_namespace_from_token}
        :param skip_child_token: Set this to true to prevent the creation of ephemeral child token used by this provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_child_token VaultProvider#skip_child_token}
        :param skip_get_vault_version: Skip the dynamic fetching of the Vault server version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_get_vault_version VaultProvider#skip_get_vault_version}
        :param skip_tls_verify: Set this to true only if the target Vault server is an insecure development instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_tls_verify VaultProvider#skip_tls_verify}
        :param tls_server_name: Name to use as the SNI host when connecting via TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#tls_server_name VaultProvider#tls_server_name}
        :param token: Token to use to authenticate to Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token VaultProvider#token}
        :param token_name: Token name to use for creating the Vault child token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token_name VaultProvider#token_name}
        :param vault_version_override: Override the Vault server version, which is normally determined dynamically from the target Vault server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vault_version_override VaultProvider#vault_version_override}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d3c7755e0fde79055ed6fd229756ea8b5a53b6f39ddece5c78a6f8aa048bd71)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = VaultProviderConfig(
            add_address_to_env=add_address_to_env,
            address=address,
            alias=alias,
            auth_login=auth_login,
            auth_login_aws=auth_login_aws,
            auth_login_azure=auth_login_azure,
            auth_login_cert=auth_login_cert,
            auth_login_gcp=auth_login_gcp,
            auth_login_jwt=auth_login_jwt,
            auth_login_kerberos=auth_login_kerberos,
            auth_login_oci=auth_login_oci,
            auth_login_oidc=auth_login_oidc,
            auth_login_radius=auth_login_radius,
            auth_login_token_file=auth_login_token_file,
            auth_login_userpass=auth_login_userpass,
            ca_cert_dir=ca_cert_dir,
            ca_cert_file=ca_cert_file,
            client_auth=client_auth,
            headers=headers,
            max_lease_ttl_seconds=max_lease_ttl_seconds,
            max_retries=max_retries,
            max_retries_ccc=max_retries_ccc,
            namespace=namespace,
            set_namespace_from_token=set_namespace_from_token,
            skip_child_token=skip_child_token,
            skip_get_vault_version=skip_get_vault_version,
            skip_tls_verify=skip_tls_verify,
            tls_server_name=tls_server_name,
            token=token,
            token_name=token_name,
            vault_version_override=vault_version_override,
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
        '''Generates CDKTF code for importing a VaultProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VaultProvider to import.
        :param import_from_id: The id of the existing VaultProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VaultProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2f847af62d1b6879b1baf2ae724aaa29af8d6ffea0b5148d93337cc391f0cce)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAddAddressToEnv")
    def reset_add_address_to_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddAddressToEnv", []))

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAuthLogin")
    def reset_auth_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLogin", []))

    @jsii.member(jsii_name="resetAuthLoginAws")
    def reset_auth_login_aws(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginAws", []))

    @jsii.member(jsii_name="resetAuthLoginAzure")
    def reset_auth_login_azure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginAzure", []))

    @jsii.member(jsii_name="resetAuthLoginCert")
    def reset_auth_login_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginCert", []))

    @jsii.member(jsii_name="resetAuthLoginGcp")
    def reset_auth_login_gcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginGcp", []))

    @jsii.member(jsii_name="resetAuthLoginJwt")
    def reset_auth_login_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginJwt", []))

    @jsii.member(jsii_name="resetAuthLoginKerberos")
    def reset_auth_login_kerberos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginKerberos", []))

    @jsii.member(jsii_name="resetAuthLoginOci")
    def reset_auth_login_oci(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginOci", []))

    @jsii.member(jsii_name="resetAuthLoginOidc")
    def reset_auth_login_oidc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginOidc", []))

    @jsii.member(jsii_name="resetAuthLoginRadius")
    def reset_auth_login_radius(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginRadius", []))

    @jsii.member(jsii_name="resetAuthLoginTokenFile")
    def reset_auth_login_token_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginTokenFile", []))

    @jsii.member(jsii_name="resetAuthLoginUserpass")
    def reset_auth_login_userpass(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthLoginUserpass", []))

    @jsii.member(jsii_name="resetCaCertDir")
    def reset_ca_cert_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCertDir", []))

    @jsii.member(jsii_name="resetCaCertFile")
    def reset_ca_cert_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCertFile", []))

    @jsii.member(jsii_name="resetClientAuth")
    def reset_client_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientAuth", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetMaxLeaseTtlSeconds")
    def reset_max_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLeaseTtlSeconds", []))

    @jsii.member(jsii_name="resetMaxRetries")
    def reset_max_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetries", []))

    @jsii.member(jsii_name="resetMaxRetriesCcc")
    def reset_max_retries_ccc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetriesCcc", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetSetNamespaceFromToken")
    def reset_set_namespace_from_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetNamespaceFromToken", []))

    @jsii.member(jsii_name="resetSkipChildToken")
    def reset_skip_child_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipChildToken", []))

    @jsii.member(jsii_name="resetSkipGetVaultVersion")
    def reset_skip_get_vault_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipGetVaultVersion", []))

    @jsii.member(jsii_name="resetSkipTlsVerify")
    def reset_skip_tls_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipTlsVerify", []))

    @jsii.member(jsii_name="resetTlsServerName")
    def reset_tls_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsServerName", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="resetTokenName")
    def reset_token_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenName", []))

    @jsii.member(jsii_name="resetVaultVersionOverride")
    def reset_vault_version_override(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVaultVersionOverride", []))

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
    @jsii.member(jsii_name="addAddressToEnvInput")
    def add_address_to_env_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addAddressToEnvInput"))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginAwsInput")
    def auth_login_aws_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAws"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAws"]]], jsii.get(self, "authLoginAwsInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginAzureInput")
    def auth_login_azure_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAzure"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAzure"]]], jsii.get(self, "authLoginAzureInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginCertInput")
    def auth_login_cert_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginCert"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginCert"]]], jsii.get(self, "authLoginCertInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginGcpInput")
    def auth_login_gcp_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginGcp"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginGcp"]]], jsii.get(self, "authLoginGcpInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginInput")
    def auth_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLogin"]]], jsii.get(self, "authLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginJwtInput")
    def auth_login_jwt_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginJwt"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginJwt"]]], jsii.get(self, "authLoginJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginKerberosInput")
    def auth_login_kerberos_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginKerberos"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginKerberos"]]], jsii.get(self, "authLoginKerberosInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginOciInput")
    def auth_login_oci_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOci"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOci"]]], jsii.get(self, "authLoginOciInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginOidcInput")
    def auth_login_oidc_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOidc"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOidc"]]], jsii.get(self, "authLoginOidcInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginRadiusInput")
    def auth_login_radius_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginRadius"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginRadius"]]], jsii.get(self, "authLoginRadiusInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginTokenFileInput")
    def auth_login_token_file_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginTokenFile"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginTokenFile"]]], jsii.get(self, "authLoginTokenFileInput"))

    @builtins.property
    @jsii.member(jsii_name="authLoginUserpassInput")
    def auth_login_userpass_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginUserpass"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginUserpass"]]], jsii.get(self, "authLoginUserpassInput"))

    @builtins.property
    @jsii.member(jsii_name="caCertDirInput")
    def ca_cert_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertDirInput"))

    @builtins.property
    @jsii.member(jsii_name="caCertFileInput")
    def ca_cert_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertFileInput"))

    @builtins.property
    @jsii.member(jsii_name="clientAuthInput")
    def client_auth_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderClientAuth"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderClientAuth"]]], jsii.get(self, "clientAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]], jsii.get(self, "headersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSecondsInput")
    def max_lease_ttl_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLeaseTtlSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRetriesCccInput")
    def max_retries_ccc_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetriesCccInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRetriesInput")
    def max_retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetriesInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="setNamespaceFromTokenInput")
    def set_namespace_from_token_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "setNamespaceFromTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="skipChildTokenInput")
    def skip_child_token_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipChildTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="skipGetVaultVersionInput")
    def skip_get_vault_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipGetVaultVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="skipTlsVerifyInput")
    def skip_tls_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipTlsVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsServerNameInput")
    def tls_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenNameInput")
    def token_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenNameInput"))

    @builtins.property
    @jsii.member(jsii_name="vaultVersionOverrideInput")
    def vault_version_override_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vaultVersionOverrideInput"))

    @builtins.property
    @jsii.member(jsii_name="addAddressToEnv")
    def add_address_to_env(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addAddressToEnv"))

    @add_address_to_env.setter
    def add_address_to_env(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb4a024728085b21255b331b8cafb8e1f4e13b34c08ff46feb6f5dbc02e20d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addAddressToEnv", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "address"))

    @address.setter
    def address(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41cbe18f6e51e6d8b40bbedc765a2e86e5bb13ea0f800a8fef9e304e727a8ba3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45d1349f9c546f3c4217603090328a263290cd8ab6820f11c9bdb25e1af3c657)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLogin")
    def auth_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLogin"]]], jsii.get(self, "authLogin"))

    @auth_login.setter
    def auth_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa3b4bef01072b48310ed5081591961b76db438cd005fb22a6e5bd301da63f68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLogin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginAws")
    def auth_login_aws(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAws"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAws"]]], jsii.get(self, "authLoginAws"))

    @auth_login_aws.setter
    def auth_login_aws(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAws"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e01b7937c68afbbebdc5e4845d39215b1aa84d4e2c813c59965b3a2475a30b1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginAws", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginAzure")
    def auth_login_azure(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAzure"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAzure"]]], jsii.get(self, "authLoginAzure"))

    @auth_login_azure.setter
    def auth_login_azure(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginAzure"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18ef03027fb974ac6f55af2c7641e0e261c4673c77a213d2bcc93e505e858e74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginAzure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginCert")
    def auth_login_cert(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginCert"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginCert"]]], jsii.get(self, "authLoginCert"))

    @auth_login_cert.setter
    def auth_login_cert(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginCert"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4be5c26ab33f5e79b2e51cf8e61b794beca04649e5c1597d6d2855f487895dbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginGcp")
    def auth_login_gcp(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginGcp"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginGcp"]]], jsii.get(self, "authLoginGcp"))

    @auth_login_gcp.setter
    def auth_login_gcp(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginGcp"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c94fb99f53120eb6da4e1e0ecd0173ee6bdd1ff9e2a74ba3a363175db27b4f89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginGcp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginJwt")
    def auth_login_jwt(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginJwt"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginJwt"]]], jsii.get(self, "authLoginJwt"))

    @auth_login_jwt.setter
    def auth_login_jwt(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginJwt"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__997fabe98b5ffbb86d64e7573c8ee796e165db66b7dee91d83391857ca80a054)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginJwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginKerberos")
    def auth_login_kerberos(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginKerberos"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginKerberos"]]], jsii.get(self, "authLoginKerberos"))

    @auth_login_kerberos.setter
    def auth_login_kerberos(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginKerberos"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a45afc5ac62a1484b28a72948aa0fcd52e9cbacf3c5630052bb46666e9d61306)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginKerberos", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginOci")
    def auth_login_oci(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOci"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOci"]]], jsii.get(self, "authLoginOci"))

    @auth_login_oci.setter
    def auth_login_oci(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOci"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__886110d602f20627d559e66441cd42afb7b59a3ee4c56928234ffe6e206f9701)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginOci", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginOidc")
    def auth_login_oidc(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOidc"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOidc"]]], jsii.get(self, "authLoginOidc"))

    @auth_login_oidc.setter
    def auth_login_oidc(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginOidc"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7872bc318f6ab77f55cc3681f9813a0b70597c43fa614d3330d2c80e3ccf045a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginOidc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginRadius")
    def auth_login_radius(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginRadius"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginRadius"]]], jsii.get(self, "authLoginRadius"))

    @auth_login_radius.setter
    def auth_login_radius(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginRadius"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae5550453911cabc56f1684a61b1f21144dddbb85cf1e312da541d0174eb3f16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginRadius", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginTokenFile")
    def auth_login_token_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginTokenFile"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginTokenFile"]]], jsii.get(self, "authLoginTokenFile"))

    @auth_login_token_file.setter
    def auth_login_token_file(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginTokenFile"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__699e969dbd9a15f496067c7fe2d4c08390454817e20b35aeccb9629ae2da9e51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginTokenFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authLoginUserpass")
    def auth_login_userpass(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginUserpass"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginUserpass"]]], jsii.get(self, "authLoginUserpass"))

    @auth_login_userpass.setter
    def auth_login_userpass(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderAuthLoginUserpass"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2f5510c57a792b65d8dc32646efc325e4079f8a492c9f445ab300d57469ff89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authLoginUserpass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caCertDir")
    def ca_cert_dir(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertDir"))

    @ca_cert_dir.setter
    def ca_cert_dir(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__522200e98126128d2c7d4c381bcdb2938d69ddcba32af12bd6f3fa6c5bd19f7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCertDir", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caCertFile")
    def ca_cert_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertFile"))

    @ca_cert_file.setter
    def ca_cert_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b276bfb2bacd0dbb98594a074408c82b252f6dda0a9870f0edaa81fce84ee73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCertFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientAuth")
    def client_auth(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderClientAuth"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderClientAuth"]]], jsii.get(self, "clientAuth"))

    @client_auth.setter
    def client_auth(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderClientAuth"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3153e1a79f3137c81a654219243493834f4e56a925bc2b5c59f3bf37fa7b8c2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientAuth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]], jsii.get(self, "headers"))

    @headers.setter
    def headers(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23e64473656495402772f98e6441593ad80315f3d21b4aad7203dd523d83a0e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2ff33e88c42dad7875706ead3cfe13fafeb2eae2a15332a6227af9b9d5304c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__114c5a84bc2c5488ec705ac38a408983c71793fe385c7be3ed2f854c40ae6cbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRetries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRetriesCcc")
    def max_retries_ccc(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetriesCcc"))

    @max_retries_ccc.setter
    def max_retries_ccc(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d43981df1423abbf193b7f4e6d459e5a6a3f53cd37660b734f5aa8043918fa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRetriesCcc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f9e92148b8fb37166a68b23f41f8149cfcdf38ed1e8423788ac6eca583771a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="setNamespaceFromToken")
    def set_namespace_from_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "setNamespaceFromToken"))

    @set_namespace_from_token.setter
    def set_namespace_from_token(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b31299d9596a8f32cdd8c2b904f59340a14fa26108020661e207dc8dcf198511)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "setNamespaceFromToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipChildToken")
    def skip_child_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipChildToken"))

    @skip_child_token.setter
    def skip_child_token(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__332b58f12460d09d8770d392a9ce89c31d109cc902fc8139572e98bb79c9611e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipChildToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipGetVaultVersion")
    def skip_get_vault_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipGetVaultVersion"))

    @skip_get_vault_version.setter
    def skip_get_vault_version(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__944cf481030f71c4fcbdac1c9159b65303da1b160d1f32a23d313eeeab9a67f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipGetVaultVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipTlsVerify")
    def skip_tls_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipTlsVerify"))

    @skip_tls_verify.setter
    def skip_tls_verify(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f16ce43552bf5072718892b805101a1b21398268f2e37b9c74224a168539ae41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipTlsVerify", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsServerName")
    def tls_server_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsServerName"))

    @tls_server_name.setter
    def tls_server_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d5ae9ee18b2cfcd1e8befefa3e7cc66a682f9d07113a99211e6afd3fed2dfc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsServerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b6e89fd3b39aebbd35b1dbcc1de240487d702092e217f1d641b46b6293eb12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenName")
    def token_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenName"))

    @token_name.setter
    def token_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e85ea1ce47ab55931d04ed6c1761b741750495eb8ca12d81defb2e16d1bc0d77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vaultVersionOverride")
    def vault_version_override(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vaultVersionOverride"))

    @vault_version_override.setter
    def vault_version_override(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1c85a439e07f3126b010213d5939012f6245f03f58d610d62907875fae573ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vaultVersionOverride", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLogin",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "method": "method",
        "namespace": "namespace",
        "parameters": "parameters",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLogin:
    def __init__(
        self,
        *,
        path: builtins.str,
        method: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#path VaultProvider#path}.
        :param method: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#method VaultProvider#method}.
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#parameters VaultProvider#parameters}.
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c19f09d9e472aea8e30d6203066570211571447e723703ee35f611f7877979)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument method", value=method, expected_type=type_hints["method"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }
        if method is not None:
            self._values["method"] = method
        if namespace is not None:
            self._values["namespace"] = namespace
        if parameters is not None:
            self._values["parameters"] = parameters
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#path VaultProvider#path}.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#method VaultProvider#method}.'''
        result = self._values.get("method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#parameters VaultProvider#parameters}.'''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginAws",
    jsii_struct_bases=[],
    name_mapping={
        "role": "role",
        "aws_access_key_id": "awsAccessKeyId",
        "aws_iam_endpoint": "awsIamEndpoint",
        "aws_profile": "awsProfile",
        "aws_region": "awsRegion",
        "aws_role_arn": "awsRoleArn",
        "aws_role_session_name": "awsRoleSessionName",
        "aws_secret_access_key": "awsSecretAccessKey",
        "aws_session_token": "awsSessionToken",
        "aws_shared_credentials_file": "awsSharedCredentialsFile",
        "aws_sts_endpoint": "awsStsEndpoint",
        "aws_web_identity_token_file": "awsWebIdentityTokenFile",
        "header_value": "headerValue",
        "mount": "mount",
        "namespace": "namespace",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginAws:
    def __init__(
        self,
        *,
        role: builtins.str,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_iam_endpoint: typing.Optional[builtins.str] = None,
        aws_profile: typing.Optional[builtins.str] = None,
        aws_region: typing.Optional[builtins.str] = None,
        aws_role_arn: typing.Optional[builtins.str] = None,
        aws_role_session_name: typing.Optional[builtins.str] = None,
        aws_secret_access_key: typing.Optional[builtins.str] = None,
        aws_session_token: typing.Optional[builtins.str] = None,
        aws_shared_credentials_file: typing.Optional[builtins.str] = None,
        aws_sts_endpoint: typing.Optional[builtins.str] = None,
        aws_web_identity_token_file: typing.Optional[builtins.str] = None,
        header_value: typing.Optional[builtins.str] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param role: The Vault role to use when logging into Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        :param aws_access_key_id: The AWS access key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_access_key_id VaultProvider#aws_access_key_id}
        :param aws_iam_endpoint: The IAM endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_iam_endpoint VaultProvider#aws_iam_endpoint}
        :param aws_profile: The name of the AWS profile. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_profile VaultProvider#aws_profile}
        :param aws_region: The AWS region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_region VaultProvider#aws_region}
        :param aws_role_arn: The ARN of the AWS Role to assume.Used during STS AssumeRole. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_role_arn VaultProvider#aws_role_arn}
        :param aws_role_session_name: Specifies the name to attach to the AWS role session. Used during STS AssumeRole. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_role_session_name VaultProvider#aws_role_session_name}
        :param aws_secret_access_key: The AWS secret access key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_secret_access_key VaultProvider#aws_secret_access_key}
        :param aws_session_token: The AWS session token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_session_token VaultProvider#aws_session_token}
        :param aws_shared_credentials_file: Path to the AWS shared credentials file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_shared_credentials_file VaultProvider#aws_shared_credentials_file}
        :param aws_sts_endpoint: The STS endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_sts_endpoint VaultProvider#aws_sts_endpoint}
        :param aws_web_identity_token_file: Path to the file containing an OAuth 2.0 access token or OpenID Connect ID token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_web_identity_token_file VaultProvider#aws_web_identity_token_file}
        :param header_value: The Vault header value to include in the STS signing request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#header_value VaultProvider#header_value}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ece9a1d2a35d54d96b651ade05abce634f093e879b38831306976b08d1de9f5)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument aws_access_key_id", value=aws_access_key_id, expected_type=type_hints["aws_access_key_id"])
            check_type(argname="argument aws_iam_endpoint", value=aws_iam_endpoint, expected_type=type_hints["aws_iam_endpoint"])
            check_type(argname="argument aws_profile", value=aws_profile, expected_type=type_hints["aws_profile"])
            check_type(argname="argument aws_region", value=aws_region, expected_type=type_hints["aws_region"])
            check_type(argname="argument aws_role_arn", value=aws_role_arn, expected_type=type_hints["aws_role_arn"])
            check_type(argname="argument aws_role_session_name", value=aws_role_session_name, expected_type=type_hints["aws_role_session_name"])
            check_type(argname="argument aws_secret_access_key", value=aws_secret_access_key, expected_type=type_hints["aws_secret_access_key"])
            check_type(argname="argument aws_session_token", value=aws_session_token, expected_type=type_hints["aws_session_token"])
            check_type(argname="argument aws_shared_credentials_file", value=aws_shared_credentials_file, expected_type=type_hints["aws_shared_credentials_file"])
            check_type(argname="argument aws_sts_endpoint", value=aws_sts_endpoint, expected_type=type_hints["aws_sts_endpoint"])
            check_type(argname="argument aws_web_identity_token_file", value=aws_web_identity_token_file, expected_type=type_hints["aws_web_identity_token_file"])
            check_type(argname="argument header_value", value=header_value, expected_type=type_hints["header_value"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }
        if aws_access_key_id is not None:
            self._values["aws_access_key_id"] = aws_access_key_id
        if aws_iam_endpoint is not None:
            self._values["aws_iam_endpoint"] = aws_iam_endpoint
        if aws_profile is not None:
            self._values["aws_profile"] = aws_profile
        if aws_region is not None:
            self._values["aws_region"] = aws_region
        if aws_role_arn is not None:
            self._values["aws_role_arn"] = aws_role_arn
        if aws_role_session_name is not None:
            self._values["aws_role_session_name"] = aws_role_session_name
        if aws_secret_access_key is not None:
            self._values["aws_secret_access_key"] = aws_secret_access_key
        if aws_session_token is not None:
            self._values["aws_session_token"] = aws_session_token
        if aws_shared_credentials_file is not None:
            self._values["aws_shared_credentials_file"] = aws_shared_credentials_file
        if aws_sts_endpoint is not None:
            self._values["aws_sts_endpoint"] = aws_sts_endpoint
        if aws_web_identity_token_file is not None:
            self._values["aws_web_identity_token_file"] = aws_web_identity_token_file
        if header_value is not None:
            self._values["header_value"] = header_value
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def role(self) -> builtins.str:
        '''The Vault role to use when logging into Vault.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_access_key_id(self) -> typing.Optional[builtins.str]:
        '''The AWS access key ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_access_key_id VaultProvider#aws_access_key_id}
        '''
        result = self._values.get("aws_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_iam_endpoint(self) -> typing.Optional[builtins.str]:
        '''The IAM endpoint URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_iam_endpoint VaultProvider#aws_iam_endpoint}
        '''
        result = self._values.get("aws_iam_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_profile(self) -> typing.Optional[builtins.str]:
        '''The name of the AWS profile.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_profile VaultProvider#aws_profile}
        '''
        result = self._values.get("aws_profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_region(self) -> typing.Optional[builtins.str]:
        '''The AWS region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_region VaultProvider#aws_region}
        '''
        result = self._values.get("aws_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_role_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of the AWS Role to assume.Used during STS AssumeRole.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_role_arn VaultProvider#aws_role_arn}
        '''
        result = self._values.get("aws_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_role_session_name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name to attach to the AWS role session. Used during STS AssumeRole.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_role_session_name VaultProvider#aws_role_session_name}
        '''
        result = self._values.get("aws_role_session_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''The AWS secret access key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_secret_access_key VaultProvider#aws_secret_access_key}
        '''
        result = self._values.get("aws_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_session_token(self) -> typing.Optional[builtins.str]:
        '''The AWS session token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_session_token VaultProvider#aws_session_token}
        '''
        result = self._values.get("aws_session_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_shared_credentials_file(self) -> typing.Optional[builtins.str]:
        '''Path to the AWS shared credentials file.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_shared_credentials_file VaultProvider#aws_shared_credentials_file}
        '''
        result = self._values.get("aws_shared_credentials_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_sts_endpoint(self) -> typing.Optional[builtins.str]:
        '''The STS endpoint URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_sts_endpoint VaultProvider#aws_sts_endpoint}
        '''
        result = self._values.get("aws_sts_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_web_identity_token_file(self) -> typing.Optional[builtins.str]:
        '''Path to the file containing an OAuth 2.0 access token or OpenID Connect ID token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#aws_web_identity_token_file VaultProvider#aws_web_identity_token_file}
        '''
        result = self._values.get("aws_web_identity_token_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def header_value(self) -> typing.Optional[builtins.str]:
        '''The Vault header value to include in the STS signing request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#header_value VaultProvider#header_value}
        '''
        result = self._values.get("header_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginAws(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginAzure",
    jsii_struct_bases=[],
    name_mapping={
        "resource_group_name": "resourceGroupName",
        "role": "role",
        "subscription_id": "subscriptionId",
        "client_id": "clientId",
        "jwt": "jwt",
        "mount": "mount",
        "namespace": "namespace",
        "scope": "scope",
        "tenant_id": "tenantId",
        "use_root_namespace": "useRootNamespace",
        "vm_name": "vmName",
        "vmss_name": "vmssName",
    },
)
class VaultProviderAuthLoginAzure:
    def __init__(
        self,
        *,
        resource_group_name: builtins.str,
        role: builtins.str,
        subscription_id: builtins.str,
        client_id: typing.Optional[builtins.str] = None,
        jwt: typing.Optional[builtins.str] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        scope: typing.Optional[builtins.str] = None,
        tenant_id: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vm_name: typing.Optional[builtins.str] = None,
        vmss_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param resource_group_name: The resource group for the machine that generated the MSI token. This information can be obtained through instance metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#resource_group_name VaultProvider#resource_group_name}
        :param role: Name of the login role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        :param subscription_id: The subscription ID for the machine that generated the MSI token. This information can be obtained through instance metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#subscription_id VaultProvider#subscription_id}
        :param client_id: The identity's client ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#client_id VaultProvider#client_id}
        :param jwt: A signed JSON Web Token. If not specified on will be created automatically. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#jwt VaultProvider#jwt}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param scope: The scopes to include in the token request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#scope VaultProvider#scope}
        :param tenant_id: Provides the tenant ID to use in a multi-tenant authentication scenario. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#tenant_id VaultProvider#tenant_id}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        :param vm_name: The virtual machine name for the machine that generated the MSI token. This information can be obtained through instance metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vm_name VaultProvider#vm_name}
        :param vmss_name: The virtual machine scale set name for the machine that generated the MSI token. This information can be obtained through instance metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vmss_name VaultProvider#vmss_name}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc40d0d1824f71b146a70b1472b75e8585e69db50d35a92105b98844ef7aa6d4)
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
            check_type(argname="argument vm_name", value=vm_name, expected_type=type_hints["vm_name"])
            check_type(argname="argument vmss_name", value=vmss_name, expected_type=type_hints["vmss_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "resource_group_name": resource_group_name,
            "role": role,
            "subscription_id": subscription_id,
        }
        if client_id is not None:
            self._values["client_id"] = client_id
        if jwt is not None:
            self._values["jwt"] = jwt
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if scope is not None:
            self._values["scope"] = scope
        if tenant_id is not None:
            self._values["tenant_id"] = tenant_id
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace
        if vm_name is not None:
            self._values["vm_name"] = vm_name
        if vmss_name is not None:
            self._values["vmss_name"] = vmss_name

    @builtins.property
    def resource_group_name(self) -> builtins.str:
        '''The resource group for the machine that generated the MSI token. This information can be obtained through instance metadata.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#resource_group_name VaultProvider#resource_group_name}
        '''
        result = self._values.get("resource_group_name")
        assert result is not None, "Required property 'resource_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Name of the login role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscription_id(self) -> builtins.str:
        '''The subscription ID for the machine that generated the MSI token. This information can be obtained through instance metadata.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#subscription_id VaultProvider#subscription_id}
        '''
        result = self._values.get("subscription_id")
        assert result is not None, "Required property 'subscription_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''The identity's client ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#client_id VaultProvider#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt(self) -> typing.Optional[builtins.str]:
        '''A signed JSON Web Token. If not specified on will be created automatically.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#jwt VaultProvider#jwt}
        '''
        result = self._values.get("jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''The scopes to include in the token request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#scope VaultProvider#scope}
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tenant_id(self) -> typing.Optional[builtins.str]:
        '''Provides the tenant ID to use in a multi-tenant authentication scenario.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#tenant_id VaultProvider#tenant_id}
        '''
        result = self._values.get("tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vm_name(self) -> typing.Optional[builtins.str]:
        '''The virtual machine name for the machine that generated the MSI token.

        This information can be obtained through instance metadata.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vm_name VaultProvider#vm_name}
        '''
        result = self._values.get("vm_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vmss_name(self) -> typing.Optional[builtins.str]:
        '''The virtual machine scale set name for the machine that generated the MSI token.

        This information can be obtained through instance metadata.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vmss_name VaultProvider#vmss_name}
        '''
        result = self._values.get("vmss_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginAzure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginCert",
    jsii_struct_bases=[],
    name_mapping={
        "cert_file": "certFile",
        "key_file": "keyFile",
        "mount": "mount",
        "name": "name",
        "namespace": "namespace",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginCert:
    def __init__(
        self,
        *,
        cert_file: builtins.str,
        key_file: builtins.str,
        mount: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param cert_file: Path to a file containing the client certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#cert_file VaultProvider#cert_file}
        :param key_file: Path to a file containing the private key that the certificate was issued for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#key_file VaultProvider#key_file}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param name: Name of the certificate's role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#name VaultProvider#name}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c039eecad26b3ec09227319c3843e9308ab85f552580791121c55bc6c51de866)
            check_type(argname="argument cert_file", value=cert_file, expected_type=type_hints["cert_file"])
            check_type(argname="argument key_file", value=key_file, expected_type=type_hints["key_file"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cert_file": cert_file,
            "key_file": key_file,
        }
        if mount is not None:
            self._values["mount"] = mount
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def cert_file(self) -> builtins.str:
        '''Path to a file containing the client certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#cert_file VaultProvider#cert_file}
        '''
        result = self._values.get("cert_file")
        assert result is not None, "Required property 'cert_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_file(self) -> builtins.str:
        '''Path to a file containing the private key that the certificate was issued for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#key_file VaultProvider#key_file}
        '''
        result = self._values.get("key_file")
        assert result is not None, "Required property 'key_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the certificate's role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#name VaultProvider#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginCert(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginGcp",
    jsii_struct_bases=[],
    name_mapping={
        "role": "role",
        "credentials": "credentials",
        "jwt": "jwt",
        "mount": "mount",
        "namespace": "namespace",
        "service_account": "serviceAccount",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginGcp:
    def __init__(
        self,
        *,
        role: builtins.str,
        credentials: typing.Optional[builtins.str] = None,
        jwt: typing.Optional[builtins.str] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        service_account: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param role: Name of the login role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        :param credentials: Path to the Google Cloud credentials file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#credentials VaultProvider#credentials}
        :param jwt: A signed JSON Web Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#jwt VaultProvider#jwt}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param service_account: IAM service account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#service_account VaultProvider#service_account}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c7c18be60af67dad8d5cbf84683b0e37ced5a2fea8e2418632c85323a41fdf9)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument credentials", value=credentials, expected_type=type_hints["credentials"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument service_account", value=service_account, expected_type=type_hints["service_account"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }
        if credentials is not None:
            self._values["credentials"] = credentials
        if jwt is not None:
            self._values["jwt"] = jwt
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if service_account is not None:
            self._values["service_account"] = service_account
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def role(self) -> builtins.str:
        '''Name of the login role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def credentials(self) -> typing.Optional[builtins.str]:
        '''Path to the Google Cloud credentials file.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#credentials VaultProvider#credentials}
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt(self) -> typing.Optional[builtins.str]:
        '''A signed JSON Web Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#jwt VaultProvider#jwt}
        '''
        result = self._values.get("jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_account(self) -> typing.Optional[builtins.str]:
        '''IAM service account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#service_account VaultProvider#service_account}
        '''
        result = self._values.get("service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginGcp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginJwt",
    jsii_struct_bases=[],
    name_mapping={
        "role": "role",
        "jwt": "jwt",
        "mount": "mount",
        "namespace": "namespace",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginJwt:
    def __init__(
        self,
        *,
        role: builtins.str,
        jwt: typing.Optional[builtins.str] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param role: Name of the login role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        :param jwt: A signed JSON Web Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#jwt VaultProvider#jwt}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee6ccc900ddbe0f7d1faadec5007c4a96f152d7bb55599b155410ff93400151f)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }
        if jwt is not None:
            self._values["jwt"] = jwt
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def role(self) -> builtins.str:
        '''Name of the login role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def jwt(self) -> typing.Optional[builtins.str]:
        '''A signed JSON Web Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#jwt VaultProvider#jwt}
        '''
        result = self._values.get("jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginJwt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginKerberos",
    jsii_struct_bases=[],
    name_mapping={
        "disable_fast_negotiation": "disableFastNegotiation",
        "keytab_path": "keytabPath",
        "krb5_conf_path": "krb5ConfPath",
        "mount": "mount",
        "namespace": "namespace",
        "realm": "realm",
        "remove_instance_name": "removeInstanceName",
        "service": "service",
        "token": "token",
        "username": "username",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginKerberos:
    def __init__(
        self,
        *,
        disable_fast_negotiation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        keytab_path: typing.Optional[builtins.str] = None,
        krb5_conf_path: typing.Optional[builtins.str] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        realm: typing.Optional[builtins.str] = None,
        remove_instance_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param disable_fast_negotiation: Disable the Kerberos FAST negotiation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#disable_fast_negotiation VaultProvider#disable_fast_negotiation}
        :param keytab_path: The Kerberos keytab file containing the entry of the login entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#keytab_path VaultProvider#keytab_path}
        :param krb5_conf_path: A valid Kerberos configuration file e.g. /etc/krb5.conf. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#krb5conf_path VaultProvider#krb5conf_path}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param realm: The Kerberos server's authoritative authentication domain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#realm VaultProvider#realm}
        :param remove_instance_name: Strip the host from the username found in the keytab. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#remove_instance_name VaultProvider#remove_instance_name}
        :param service: The service principle name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#service VaultProvider#service}
        :param token: Simple and Protected GSSAPI Negotiation Mechanism (SPNEGO) token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token VaultProvider#token}
        :param username: The username to login into Kerberos with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#username VaultProvider#username}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f58ea360b321e9ec2b16fce1926ebf1ae883c0ff43ea4c1df84da702c892a37c)
            check_type(argname="argument disable_fast_negotiation", value=disable_fast_negotiation, expected_type=type_hints["disable_fast_negotiation"])
            check_type(argname="argument keytab_path", value=keytab_path, expected_type=type_hints["keytab_path"])
            check_type(argname="argument krb5_conf_path", value=krb5_conf_path, expected_type=type_hints["krb5_conf_path"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument realm", value=realm, expected_type=type_hints["realm"])
            check_type(argname="argument remove_instance_name", value=remove_instance_name, expected_type=type_hints["remove_instance_name"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if disable_fast_negotiation is not None:
            self._values["disable_fast_negotiation"] = disable_fast_negotiation
        if keytab_path is not None:
            self._values["keytab_path"] = keytab_path
        if krb5_conf_path is not None:
            self._values["krb5_conf_path"] = krb5_conf_path
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if realm is not None:
            self._values["realm"] = realm
        if remove_instance_name is not None:
            self._values["remove_instance_name"] = remove_instance_name
        if service is not None:
            self._values["service"] = service
        if token is not None:
            self._values["token"] = token
        if username is not None:
            self._values["username"] = username
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def disable_fast_negotiation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable the Kerberos FAST negotiation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#disable_fast_negotiation VaultProvider#disable_fast_negotiation}
        '''
        result = self._values.get("disable_fast_negotiation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def keytab_path(self) -> typing.Optional[builtins.str]:
        '''The Kerberos keytab file containing the entry of the login entity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#keytab_path VaultProvider#keytab_path}
        '''
        result = self._values.get("keytab_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def krb5_conf_path(self) -> typing.Optional[builtins.str]:
        '''A valid Kerberos configuration file e.g. /etc/krb5.conf.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#krb5conf_path VaultProvider#krb5conf_path}
        '''
        result = self._values.get("krb5_conf_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def realm(self) -> typing.Optional[builtins.str]:
        '''The Kerberos server's authoritative authentication domain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#realm VaultProvider#realm}
        '''
        result = self._values.get("realm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remove_instance_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Strip the host from the username found in the keytab.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#remove_instance_name VaultProvider#remove_instance_name}
        '''
        result = self._values.get("remove_instance_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        '''The service principle name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#service VaultProvider#service}
        '''
        result = self._values.get("service")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Simple and Protected GSSAPI Negotiation Mechanism (SPNEGO) token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token VaultProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The username to login into Kerberos with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#username VaultProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginKerberos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginOci",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "role": "role",
        "mount": "mount",
        "namespace": "namespace",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginOci:
    def __init__(
        self,
        *,
        auth_type: builtins.str,
        role: builtins.str,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param auth_type: Authentication type to use when getting OCI credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_type VaultProvider#auth_type}
        :param role: Name of the login role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5497c2614f448da8b7652258c676a58fd4cf986247ab6d6e837387b4fbeadbfe)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_type": auth_type,
            "role": role,
        }
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def auth_type(self) -> builtins.str:
        '''Authentication type to use when getting OCI credentials.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_type VaultProvider#auth_type}
        '''
        result = self._values.get("auth_type")
        assert result is not None, "Required property 'auth_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Name of the login role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginOci(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginOidc",
    jsii_struct_bases=[],
    name_mapping={
        "role": "role",
        "callback_address": "callbackAddress",
        "callback_listener_address": "callbackListenerAddress",
        "mount": "mount",
        "namespace": "namespace",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginOidc:
    def __init__(
        self,
        *,
        role: builtins.str,
        callback_address: typing.Optional[builtins.str] = None,
        callback_listener_address: typing.Optional[builtins.str] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param role: Name of the login role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        :param callback_address: The callback address. Must be a valid URI without the path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#callback_address VaultProvider#callback_address}
        :param callback_listener_address: The callback listener's address. Must be a valid URI without the path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#callback_listener_address VaultProvider#callback_listener_address}
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9353dd7c223c1a13f5a1faf380f9516b82893e76b15790f799530ca385bb5d66)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument callback_address", value=callback_address, expected_type=type_hints["callback_address"])
            check_type(argname="argument callback_listener_address", value=callback_listener_address, expected_type=type_hints["callback_listener_address"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
        }
        if callback_address is not None:
            self._values["callback_address"] = callback_address
        if callback_listener_address is not None:
            self._values["callback_listener_address"] = callback_listener_address
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def role(self) -> builtins.str:
        '''Name of the login role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#role VaultProvider#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def callback_address(self) -> typing.Optional[builtins.str]:
        '''The callback address. Must be a valid URI without the path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#callback_address VaultProvider#callback_address}
        '''
        result = self._values.get("callback_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def callback_listener_address(self) -> typing.Optional[builtins.str]:
        '''The callback listener's address. Must be a valid URI without the path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#callback_listener_address VaultProvider#callback_listener_address}
        '''
        result = self._values.get("callback_listener_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginOidc(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginRadius",
    jsii_struct_bases=[],
    name_mapping={
        "mount": "mount",
        "namespace": "namespace",
        "password": "password",
        "username": "username",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginRadius:
    def __init__(
        self,
        *,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param password: The Radius password for username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#password VaultProvider#password}
        :param username: The Radius username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#username VaultProvider#username}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__135a164d2d92c902189afc88159510347c4f57d0e0538d143c53fa6b144bf2e3)
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The Radius password for username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#password VaultProvider#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The Radius username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#username VaultProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginRadius(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginTokenFile",
    jsii_struct_bases=[],
    name_mapping={
        "filename": "filename",
        "namespace": "namespace",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginTokenFile:
    def __init__(
        self,
        *,
        filename: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param filename: The name of a file containing a single line that is a valid Vault token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#filename VaultProvider#filename}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5691bcafe5aaa85dd9adf362eefb3fceefd24c2688f7a0dbaa2989fb3e67f4bc)
            check_type(argname="argument filename", value=filename, expected_type=type_hints["filename"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if filename is not None:
            self._values["filename"] = filename
        if namespace is not None:
            self._values["namespace"] = namespace
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def filename(self) -> typing.Optional[builtins.str]:
        '''The name of a file containing a single line that is a valid Vault token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#filename VaultProvider#filename}
        '''
        result = self._values.get("filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginTokenFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderAuthLoginUserpass",
    jsii_struct_bases=[],
    name_mapping={
        "mount": "mount",
        "namespace": "namespace",
        "password": "password",
        "password_file": "passwordFile",
        "username": "username",
        "use_root_namespace": "useRootNamespace",
    },
)
class VaultProviderAuthLoginUserpass:
    def __init__(
        self,
        *,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        password_file: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param mount: The path where the authentication engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        :param namespace: The authentication engine's namespace. Conflicts with use_root_namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param password: Login with password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#password VaultProvider#password}
        :param password_file: Login with password from a file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#password_file VaultProvider#password_file}
        :param username: Login with username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#username VaultProvider#username}
        :param use_root_namespace: Authenticate to the root Vault namespace. Conflicts with namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b78f4b8b677c0df722dc2b1711633a8be8bd6d656fda2a9c851883763b1a305f)
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_file", value=password_file, expected_type=type_hints["password_file"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument use_root_namespace", value=use_root_namespace, expected_type=type_hints["use_root_namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if password is not None:
            self._values["password"] = password
        if password_file is not None:
            self._values["password_file"] = password_file
        if username is not None:
            self._values["username"] = username
        if use_root_namespace is not None:
            self._values["use_root_namespace"] = use_root_namespace

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the authentication engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#mount VaultProvider#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The authentication engine's namespace. Conflicts with use_root_namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Login with password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#password VaultProvider#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_file(self) -> typing.Optional[builtins.str]:
        '''Login with password from a file.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#password_file VaultProvider#password_file}
        '''
        result = self._values.get("password_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Login with username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#username VaultProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_root_namespace(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Authenticate to the root Vault namespace. Conflicts with namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#use_root_namespace VaultProvider#use_root_namespace}
        '''
        result = self._values.get("use_root_namespace")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderAuthLoginUserpass(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderClientAuth",
    jsii_struct_bases=[],
    name_mapping={"cert_file": "certFile", "key_file": "keyFile"},
)
class VaultProviderClientAuth:
    def __init__(self, *, cert_file: builtins.str, key_file: builtins.str) -> None:
        '''
        :param cert_file: Path to a file containing the client certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#cert_file VaultProvider#cert_file}
        :param key_file: Path to a file containing the private key that the certificate was issued for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#key_file VaultProvider#key_file}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cc551af7d258036fefb3a353aea1cecff794544b3ca345dba023c845087c7f2)
            check_type(argname="argument cert_file", value=cert_file, expected_type=type_hints["cert_file"])
            check_type(argname="argument key_file", value=key_file, expected_type=type_hints["key_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cert_file": cert_file,
            "key_file": key_file,
        }

    @builtins.property
    def cert_file(self) -> builtins.str:
        '''Path to a file containing the client certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#cert_file VaultProvider#cert_file}
        '''
        result = self._values.get("cert_file")
        assert result is not None, "Required property 'cert_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_file(self) -> builtins.str:
        '''Path to a file containing the private key that the certificate was issued for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#key_file VaultProvider#key_file}
        '''
        result = self._values.get("key_file")
        assert result is not None, "Required property 'key_file' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderClientAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "add_address_to_env": "addAddressToEnv",
        "address": "address",
        "alias": "alias",
        "auth_login": "authLogin",
        "auth_login_aws": "authLoginAws",
        "auth_login_azure": "authLoginAzure",
        "auth_login_cert": "authLoginCert",
        "auth_login_gcp": "authLoginGcp",
        "auth_login_jwt": "authLoginJwt",
        "auth_login_kerberos": "authLoginKerberos",
        "auth_login_oci": "authLoginOci",
        "auth_login_oidc": "authLoginOidc",
        "auth_login_radius": "authLoginRadius",
        "auth_login_token_file": "authLoginTokenFile",
        "auth_login_userpass": "authLoginUserpass",
        "ca_cert_dir": "caCertDir",
        "ca_cert_file": "caCertFile",
        "client_auth": "clientAuth",
        "headers": "headers",
        "max_lease_ttl_seconds": "maxLeaseTtlSeconds",
        "max_retries": "maxRetries",
        "max_retries_ccc": "maxRetriesCcc",
        "namespace": "namespace",
        "set_namespace_from_token": "setNamespaceFromToken",
        "skip_child_token": "skipChildToken",
        "skip_get_vault_version": "skipGetVaultVersion",
        "skip_tls_verify": "skipTlsVerify",
        "tls_server_name": "tlsServerName",
        "token": "token",
        "token_name": "tokenName",
        "vault_version_override": "vaultVersionOverride",
    },
)
class VaultProviderConfig:
    def __init__(
        self,
        *,
        add_address_to_env: typing.Optional[builtins.str] = None,
        address: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        auth_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_aws: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginAws, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_azure: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginAzure, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_cert: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginCert, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginGcp, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginJwt, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_kerberos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginKerberos, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_oci: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginOci, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_oidc: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginOidc, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_radius: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginRadius, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_token_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginTokenFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
        auth_login_userpass: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginUserpass, typing.Dict[builtins.str, typing.Any]]]]] = None,
        ca_cert_dir: typing.Optional[builtins.str] = None,
        ca_cert_file: typing.Optional[builtins.str] = None,
        client_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderClientAuth, typing.Dict[builtins.str, typing.Any]]]]] = None,
        headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VaultProviderHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        max_retries_ccc: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        set_namespace_from_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_child_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_get_vault_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_server_name: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
        token_name: typing.Optional[builtins.str] = None,
        vault_version_override: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param add_address_to_env: If true, adds the value of the ``address`` argument to the Terraform process environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#add_address_to_env VaultProvider#add_address_to_env}
        :param address: URL of the root of the target Vault server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#address VaultProvider#address}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#alias VaultProvider#alias}
        :param auth_login: auth_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login VaultProvider#auth_login}
        :param auth_login_aws: auth_login_aws block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_aws VaultProvider#auth_login_aws}
        :param auth_login_azure: auth_login_azure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_azure VaultProvider#auth_login_azure}
        :param auth_login_cert: auth_login_cert block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_cert VaultProvider#auth_login_cert}
        :param auth_login_gcp: auth_login_gcp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_gcp VaultProvider#auth_login_gcp}
        :param auth_login_jwt: auth_login_jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_jwt VaultProvider#auth_login_jwt}
        :param auth_login_kerberos: auth_login_kerberos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_kerberos VaultProvider#auth_login_kerberos}
        :param auth_login_oci: auth_login_oci block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_oci VaultProvider#auth_login_oci}
        :param auth_login_oidc: auth_login_oidc block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_oidc VaultProvider#auth_login_oidc}
        :param auth_login_radius: auth_login_radius block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_radius VaultProvider#auth_login_radius}
        :param auth_login_token_file: auth_login_token_file block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_token_file VaultProvider#auth_login_token_file}
        :param auth_login_userpass: auth_login_userpass block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_userpass VaultProvider#auth_login_userpass}
        :param ca_cert_dir: Path to directory containing CA certificate files to validate the server's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#ca_cert_dir VaultProvider#ca_cert_dir}
        :param ca_cert_file: Path to a CA certificate file to validate the server's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#ca_cert_file VaultProvider#ca_cert_file}
        :param client_auth: client_auth block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#client_auth VaultProvider#client_auth}
        :param headers: headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#headers VaultProvider#headers}
        :param max_lease_ttl_seconds: Maximum TTL for secret leases requested by this provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_lease_ttl_seconds VaultProvider#max_lease_ttl_seconds}
        :param max_retries: Maximum number of retries when a 5xx error code is encountered. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_retries VaultProvider#max_retries}
        :param max_retries_ccc: Maximum number of retries for Client Controlled Consistency related operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_retries_ccc VaultProvider#max_retries_ccc}
        :param namespace: The namespace to use. Available only for Vault Enterprise. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        :param set_namespace_from_token: In the case where the Vault token is for a specific namespace and the provider namespace is not configured, use the token namespace as the root namespace for all resources. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#set_namespace_from_token VaultProvider#set_namespace_from_token}
        :param skip_child_token: Set this to true to prevent the creation of ephemeral child token used by this provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_child_token VaultProvider#skip_child_token}
        :param skip_get_vault_version: Skip the dynamic fetching of the Vault server version. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_get_vault_version VaultProvider#skip_get_vault_version}
        :param skip_tls_verify: Set this to true only if the target Vault server is an insecure development instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_tls_verify VaultProvider#skip_tls_verify}
        :param tls_server_name: Name to use as the SNI host when connecting via TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#tls_server_name VaultProvider#tls_server_name}
        :param token: Token to use to authenticate to Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token VaultProvider#token}
        :param token_name: Token name to use for creating the Vault child token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token_name VaultProvider#token_name}
        :param vault_version_override: Override the Vault server version, which is normally determined dynamically from the target Vault server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vault_version_override VaultProvider#vault_version_override}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bf39c1744dc4dabda4c7cdeb1837822362f4198efac16be7cac3074cf6961b3)
            check_type(argname="argument add_address_to_env", value=add_address_to_env, expected_type=type_hints["add_address_to_env"])
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument auth_login", value=auth_login, expected_type=type_hints["auth_login"])
            check_type(argname="argument auth_login_aws", value=auth_login_aws, expected_type=type_hints["auth_login_aws"])
            check_type(argname="argument auth_login_azure", value=auth_login_azure, expected_type=type_hints["auth_login_azure"])
            check_type(argname="argument auth_login_cert", value=auth_login_cert, expected_type=type_hints["auth_login_cert"])
            check_type(argname="argument auth_login_gcp", value=auth_login_gcp, expected_type=type_hints["auth_login_gcp"])
            check_type(argname="argument auth_login_jwt", value=auth_login_jwt, expected_type=type_hints["auth_login_jwt"])
            check_type(argname="argument auth_login_kerberos", value=auth_login_kerberos, expected_type=type_hints["auth_login_kerberos"])
            check_type(argname="argument auth_login_oci", value=auth_login_oci, expected_type=type_hints["auth_login_oci"])
            check_type(argname="argument auth_login_oidc", value=auth_login_oidc, expected_type=type_hints["auth_login_oidc"])
            check_type(argname="argument auth_login_radius", value=auth_login_radius, expected_type=type_hints["auth_login_radius"])
            check_type(argname="argument auth_login_token_file", value=auth_login_token_file, expected_type=type_hints["auth_login_token_file"])
            check_type(argname="argument auth_login_userpass", value=auth_login_userpass, expected_type=type_hints["auth_login_userpass"])
            check_type(argname="argument ca_cert_dir", value=ca_cert_dir, expected_type=type_hints["ca_cert_dir"])
            check_type(argname="argument ca_cert_file", value=ca_cert_file, expected_type=type_hints["ca_cert_file"])
            check_type(argname="argument client_auth", value=client_auth, expected_type=type_hints["client_auth"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument max_lease_ttl_seconds", value=max_lease_ttl_seconds, expected_type=type_hints["max_lease_ttl_seconds"])
            check_type(argname="argument max_retries", value=max_retries, expected_type=type_hints["max_retries"])
            check_type(argname="argument max_retries_ccc", value=max_retries_ccc, expected_type=type_hints["max_retries_ccc"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument set_namespace_from_token", value=set_namespace_from_token, expected_type=type_hints["set_namespace_from_token"])
            check_type(argname="argument skip_child_token", value=skip_child_token, expected_type=type_hints["skip_child_token"])
            check_type(argname="argument skip_get_vault_version", value=skip_get_vault_version, expected_type=type_hints["skip_get_vault_version"])
            check_type(argname="argument skip_tls_verify", value=skip_tls_verify, expected_type=type_hints["skip_tls_verify"])
            check_type(argname="argument tls_server_name", value=tls_server_name, expected_type=type_hints["tls_server_name"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
            check_type(argname="argument token_name", value=token_name, expected_type=type_hints["token_name"])
            check_type(argname="argument vault_version_override", value=vault_version_override, expected_type=type_hints["vault_version_override"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if add_address_to_env is not None:
            self._values["add_address_to_env"] = add_address_to_env
        if address is not None:
            self._values["address"] = address
        if alias is not None:
            self._values["alias"] = alias
        if auth_login is not None:
            self._values["auth_login"] = auth_login
        if auth_login_aws is not None:
            self._values["auth_login_aws"] = auth_login_aws
        if auth_login_azure is not None:
            self._values["auth_login_azure"] = auth_login_azure
        if auth_login_cert is not None:
            self._values["auth_login_cert"] = auth_login_cert
        if auth_login_gcp is not None:
            self._values["auth_login_gcp"] = auth_login_gcp
        if auth_login_jwt is not None:
            self._values["auth_login_jwt"] = auth_login_jwt
        if auth_login_kerberos is not None:
            self._values["auth_login_kerberos"] = auth_login_kerberos
        if auth_login_oci is not None:
            self._values["auth_login_oci"] = auth_login_oci
        if auth_login_oidc is not None:
            self._values["auth_login_oidc"] = auth_login_oidc
        if auth_login_radius is not None:
            self._values["auth_login_radius"] = auth_login_radius
        if auth_login_token_file is not None:
            self._values["auth_login_token_file"] = auth_login_token_file
        if auth_login_userpass is not None:
            self._values["auth_login_userpass"] = auth_login_userpass
        if ca_cert_dir is not None:
            self._values["ca_cert_dir"] = ca_cert_dir
        if ca_cert_file is not None:
            self._values["ca_cert_file"] = ca_cert_file
        if client_auth is not None:
            self._values["client_auth"] = client_auth
        if headers is not None:
            self._values["headers"] = headers
        if max_lease_ttl_seconds is not None:
            self._values["max_lease_ttl_seconds"] = max_lease_ttl_seconds
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if max_retries_ccc is not None:
            self._values["max_retries_ccc"] = max_retries_ccc
        if namespace is not None:
            self._values["namespace"] = namespace
        if set_namespace_from_token is not None:
            self._values["set_namespace_from_token"] = set_namespace_from_token
        if skip_child_token is not None:
            self._values["skip_child_token"] = skip_child_token
        if skip_get_vault_version is not None:
            self._values["skip_get_vault_version"] = skip_get_vault_version
        if skip_tls_verify is not None:
            self._values["skip_tls_verify"] = skip_tls_verify
        if tls_server_name is not None:
            self._values["tls_server_name"] = tls_server_name
        if token is not None:
            self._values["token"] = token
        if token_name is not None:
            self._values["token_name"] = token_name
        if vault_version_override is not None:
            self._values["vault_version_override"] = vault_version_override

    @builtins.property
    def add_address_to_env(self) -> typing.Optional[builtins.str]:
        '''If true, adds the value of the ``address`` argument to the Terraform process environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#add_address_to_env VaultProvider#add_address_to_env}
        '''
        result = self._values.get("add_address_to_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def address(self) -> typing.Optional[builtins.str]:
        '''URL of the root of the target Vault server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#address VaultProvider#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#alias VaultProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLogin]]]:
        '''auth_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login VaultProvider#auth_login}
        '''
        result = self._values.get("auth_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLogin]]], result)

    @builtins.property
    def auth_login_aws(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginAws]]]:
        '''auth_login_aws block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_aws VaultProvider#auth_login_aws}
        '''
        result = self._values.get("auth_login_aws")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginAws]]], result)

    @builtins.property
    def auth_login_azure(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginAzure]]]:
        '''auth_login_azure block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_azure VaultProvider#auth_login_azure}
        '''
        result = self._values.get("auth_login_azure")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginAzure]]], result)

    @builtins.property
    def auth_login_cert(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginCert]]]:
        '''auth_login_cert block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_cert VaultProvider#auth_login_cert}
        '''
        result = self._values.get("auth_login_cert")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginCert]]], result)

    @builtins.property
    def auth_login_gcp(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginGcp]]]:
        '''auth_login_gcp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_gcp VaultProvider#auth_login_gcp}
        '''
        result = self._values.get("auth_login_gcp")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginGcp]]], result)

    @builtins.property
    def auth_login_jwt(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginJwt]]]:
        '''auth_login_jwt block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_jwt VaultProvider#auth_login_jwt}
        '''
        result = self._values.get("auth_login_jwt")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginJwt]]], result)

    @builtins.property
    def auth_login_kerberos(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginKerberos]]]:
        '''auth_login_kerberos block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_kerberos VaultProvider#auth_login_kerberos}
        '''
        result = self._values.get("auth_login_kerberos")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginKerberos]]], result)

    @builtins.property
    def auth_login_oci(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginOci]]]:
        '''auth_login_oci block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_oci VaultProvider#auth_login_oci}
        '''
        result = self._values.get("auth_login_oci")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginOci]]], result)

    @builtins.property
    def auth_login_oidc(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginOidc]]]:
        '''auth_login_oidc block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_oidc VaultProvider#auth_login_oidc}
        '''
        result = self._values.get("auth_login_oidc")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginOidc]]], result)

    @builtins.property
    def auth_login_radius(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginRadius]]]:
        '''auth_login_radius block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_radius VaultProvider#auth_login_radius}
        '''
        result = self._values.get("auth_login_radius")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginRadius]]], result)

    @builtins.property
    def auth_login_token_file(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginTokenFile]]]:
        '''auth_login_token_file block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_token_file VaultProvider#auth_login_token_file}
        '''
        result = self._values.get("auth_login_token_file")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginTokenFile]]], result)

    @builtins.property
    def auth_login_userpass(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginUserpass]]]:
        '''auth_login_userpass block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#auth_login_userpass VaultProvider#auth_login_userpass}
        '''
        result = self._values.get("auth_login_userpass")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginUserpass]]], result)

    @builtins.property
    def ca_cert_dir(self) -> typing.Optional[builtins.str]:
        '''Path to directory containing CA certificate files to validate the server's certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#ca_cert_dir VaultProvider#ca_cert_dir}
        '''
        result = self._values.get("ca_cert_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_cert_file(self) -> typing.Optional[builtins.str]:
        '''Path to a CA certificate file to validate the server's certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#ca_cert_file VaultProvider#ca_cert_file}
        '''
        result = self._values.get("ca_cert_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_auth(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderClientAuth]]]:
        '''client_auth block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#client_auth VaultProvider#client_auth}
        '''
        result = self._values.get("client_auth")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderClientAuth]]], result)

    @builtins.property
    def headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]]:
        '''headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#headers VaultProvider#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VaultProviderHeaders"]]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum TTL for secret leases requested by this provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_lease_ttl_seconds VaultProvider#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of retries when a 5xx error code is encountered.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_retries VaultProvider#max_retries}
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries_ccc(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of retries for Client Controlled Consistency related operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#max_retries_ccc VaultProvider#max_retries_ccc}
        '''
        result = self._values.get("max_retries_ccc")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The namespace to use. Available only for Vault Enterprise.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#namespace VaultProvider#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def set_namespace_from_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''In the case where the Vault token is for a specific namespace and the provider namespace is not configured, use the token namespace as the root namespace for all resources.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#set_namespace_from_token VaultProvider#set_namespace_from_token}
        '''
        result = self._values.get("set_namespace_from_token")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def skip_child_token(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set this to true to prevent the creation of ephemeral child token used by this provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_child_token VaultProvider#skip_child_token}
        '''
        result = self._values.get("skip_child_token")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def skip_get_vault_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Skip the dynamic fetching of the Vault server version.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_get_vault_version VaultProvider#skip_get_vault_version}
        '''
        result = self._values.get("skip_get_vault_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def skip_tls_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set this to true only if the target Vault server is an insecure development instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#skip_tls_verify VaultProvider#skip_tls_verify}
        '''
        result = self._values.get("skip_tls_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_server_name(self) -> typing.Optional[builtins.str]:
        '''Name to use as the SNI host when connecting via TLS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#tls_server_name VaultProvider#tls_server_name}
        '''
        result = self._values.get("tls_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Token to use to authenticate to Vault.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token VaultProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_name(self) -> typing.Optional[builtins.str]:
        '''Token name to use for creating the Vault child token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#token_name VaultProvider#token_name}
        '''
        result = self._values.get("token_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vault_version_override(self) -> typing.Optional[builtins.str]:
        '''Override the Vault server version, which is normally determined dynamically from the target Vault server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#vault_version_override VaultProvider#vault_version_override}
        '''
        result = self._values.get("vault_version_override")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.provider.VaultProviderHeaders",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class VaultProviderHeaders:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: The header name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#name VaultProvider#name}
        :param value: The header value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#value VaultProvider#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e7844df4f93b164b9a2c1c52b36e03baa237fadb18fe25ad14a1519ddefddf8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The header name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#name VaultProvider#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The header value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs#value VaultProvider#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProviderHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "VaultProvider",
    "VaultProviderAuthLogin",
    "VaultProviderAuthLoginAws",
    "VaultProviderAuthLoginAzure",
    "VaultProviderAuthLoginCert",
    "VaultProviderAuthLoginGcp",
    "VaultProviderAuthLoginJwt",
    "VaultProviderAuthLoginKerberos",
    "VaultProviderAuthLoginOci",
    "VaultProviderAuthLoginOidc",
    "VaultProviderAuthLoginRadius",
    "VaultProviderAuthLoginTokenFile",
    "VaultProviderAuthLoginUserpass",
    "VaultProviderClientAuth",
    "VaultProviderConfig",
    "VaultProviderHeaders",
]

publication.publish()

def _typecheckingstub__7d3c7755e0fde79055ed6fd229756ea8b5a53b6f39ddece5c78a6f8aa048bd71(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    add_address_to_env: typing.Optional[builtins.str] = None,
    address: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    auth_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_aws: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginAws, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_azure: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginAzure, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_cert: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginCert, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginGcp, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginJwt, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_kerberos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginKerberos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_oci: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginOci, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_oidc: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginOidc, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_radius: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginRadius, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_token_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginTokenFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_userpass: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginUserpass, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ca_cert_dir: typing.Optional[builtins.str] = None,
    ca_cert_file: typing.Optional[builtins.str] = None,
    client_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderClientAuth, typing.Dict[builtins.str, typing.Any]]]]] = None,
    headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    max_retries_ccc: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    set_namespace_from_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_child_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_get_vault_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_server_name: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
    token_name: typing.Optional[builtins.str] = None,
    vault_version_override: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2f847af62d1b6879b1baf2ae724aaa29af8d6ffea0b5148d93337cc391f0cce(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb4a024728085b21255b331b8cafb8e1f4e13b34c08ff46feb6f5dbc02e20d6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41cbe18f6e51e6d8b40bbedc765a2e86e5bb13ea0f800a8fef9e304e727a8ba3(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45d1349f9c546f3c4217603090328a263290cd8ab6820f11c9bdb25e1af3c657(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa3b4bef01072b48310ed5081591961b76db438cd005fb22a6e5bd301da63f68(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e01b7937c68afbbebdc5e4845d39215b1aa84d4e2c813c59965b3a2475a30b1f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginAws]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18ef03027fb974ac6f55af2c7641e0e261c4673c77a213d2bcc93e505e858e74(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginAzure]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4be5c26ab33f5e79b2e51cf8e61b794beca04649e5c1597d6d2855f487895dbe(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginCert]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c94fb99f53120eb6da4e1e0ecd0173ee6bdd1ff9e2a74ba3a363175db27b4f89(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginGcp]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__997fabe98b5ffbb86d64e7573c8ee796e165db66b7dee91d83391857ca80a054(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginJwt]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a45afc5ac62a1484b28a72948aa0fcd52e9cbacf3c5630052bb46666e9d61306(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginKerberos]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__886110d602f20627d559e66441cd42afb7b59a3ee4c56928234ffe6e206f9701(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginOci]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7872bc318f6ab77f55cc3681f9813a0b70597c43fa614d3330d2c80e3ccf045a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginOidc]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae5550453911cabc56f1684a61b1f21144dddbb85cf1e312da541d0174eb3f16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginRadius]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__699e969dbd9a15f496067c7fe2d4c08390454817e20b35aeccb9629ae2da9e51(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginTokenFile]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f5510c57a792b65d8dc32646efc325e4079f8a492c9f445ab300d57469ff89(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderAuthLoginUserpass]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__522200e98126128d2c7d4c381bcdb2938d69ddcba32af12bd6f3fa6c5bd19f7d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b276bfb2bacd0dbb98594a074408c82b252f6dda0a9870f0edaa81fce84ee73(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3153e1a79f3137c81a654219243493834f4e56a925bc2b5c59f3bf37fa7b8c2a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderClientAuth]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23e64473656495402772f98e6441593ad80315f3d21b4aad7203dd523d83a0e1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VaultProviderHeaders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2ff33e88c42dad7875706ead3cfe13fafeb2eae2a15332a6227af9b9d5304c0(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__114c5a84bc2c5488ec705ac38a408983c71793fe385c7be3ed2f854c40ae6cbf(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d43981df1423abbf193b7f4e6d459e5a6a3f53cd37660b734f5aa8043918fa4(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f9e92148b8fb37166a68b23f41f8149cfcdf38ed1e8423788ac6eca583771a2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b31299d9596a8f32cdd8c2b904f59340a14fa26108020661e207dc8dcf198511(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__332b58f12460d09d8770d392a9ce89c31d109cc902fc8139572e98bb79c9611e(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944cf481030f71c4fcbdac1c9159b65303da1b160d1f32a23d313eeeab9a67f1(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f16ce43552bf5072718892b805101a1b21398268f2e37b9c74224a168539ae41(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d5ae9ee18b2cfcd1e8befefa3e7cc66a682f9d07113a99211e6afd3fed2dfc1(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89b6e89fd3b39aebbd35b1dbcc1de240487d702092e217f1d641b46b6293eb12(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e85ea1ce47ab55931d04ed6c1761b741750495eb8ca12d81defb2e16d1bc0d77(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1c85a439e07f3126b010213d5939012f6245f03f58d610d62907875fae573ec(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c19f09d9e472aea8e30d6203066570211571447e723703ee35f611f7877979(
    *,
    path: builtins.str,
    method: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ece9a1d2a35d54d96b651ade05abce634f093e879b38831306976b08d1de9f5(
    *,
    role: builtins.str,
    aws_access_key_id: typing.Optional[builtins.str] = None,
    aws_iam_endpoint: typing.Optional[builtins.str] = None,
    aws_profile: typing.Optional[builtins.str] = None,
    aws_region: typing.Optional[builtins.str] = None,
    aws_role_arn: typing.Optional[builtins.str] = None,
    aws_role_session_name: typing.Optional[builtins.str] = None,
    aws_secret_access_key: typing.Optional[builtins.str] = None,
    aws_session_token: typing.Optional[builtins.str] = None,
    aws_shared_credentials_file: typing.Optional[builtins.str] = None,
    aws_sts_endpoint: typing.Optional[builtins.str] = None,
    aws_web_identity_token_file: typing.Optional[builtins.str] = None,
    header_value: typing.Optional[builtins.str] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc40d0d1824f71b146a70b1472b75e8585e69db50d35a92105b98844ef7aa6d4(
    *,
    resource_group_name: builtins.str,
    role: builtins.str,
    subscription_id: builtins.str,
    client_id: typing.Optional[builtins.str] = None,
    jwt: typing.Optional[builtins.str] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    scope: typing.Optional[builtins.str] = None,
    tenant_id: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vm_name: typing.Optional[builtins.str] = None,
    vmss_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c039eecad26b3ec09227319c3843e9308ab85f552580791121c55bc6c51de866(
    *,
    cert_file: builtins.str,
    key_file: builtins.str,
    mount: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c7c18be60af67dad8d5cbf84683b0e37ced5a2fea8e2418632c85323a41fdf9(
    *,
    role: builtins.str,
    credentials: typing.Optional[builtins.str] = None,
    jwt: typing.Optional[builtins.str] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    service_account: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee6ccc900ddbe0f7d1faadec5007c4a96f152d7bb55599b155410ff93400151f(
    *,
    role: builtins.str,
    jwt: typing.Optional[builtins.str] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f58ea360b321e9ec2b16fce1926ebf1ae883c0ff43ea4c1df84da702c892a37c(
    *,
    disable_fast_negotiation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    keytab_path: typing.Optional[builtins.str] = None,
    krb5_conf_path: typing.Optional[builtins.str] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    realm: typing.Optional[builtins.str] = None,
    remove_instance_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5497c2614f448da8b7652258c676a58fd4cf986247ab6d6e837387b4fbeadbfe(
    *,
    auth_type: builtins.str,
    role: builtins.str,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9353dd7c223c1a13f5a1faf380f9516b82893e76b15790f799530ca385bb5d66(
    *,
    role: builtins.str,
    callback_address: typing.Optional[builtins.str] = None,
    callback_listener_address: typing.Optional[builtins.str] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__135a164d2d92c902189afc88159510347c4f57d0e0538d143c53fa6b144bf2e3(
    *,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5691bcafe5aaa85dd9adf362eefb3fceefd24c2688f7a0dbaa2989fb3e67f4bc(
    *,
    filename: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b78f4b8b677c0df722dc2b1711633a8be8bd6d656fda2a9c851883763b1a305f(
    *,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    password_file: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    use_root_namespace: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cc551af7d258036fefb3a353aea1cecff794544b3ca345dba023c845087c7f2(
    *,
    cert_file: builtins.str,
    key_file: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bf39c1744dc4dabda4c7cdeb1837822362f4198efac16be7cac3074cf6961b3(
    *,
    add_address_to_env: typing.Optional[builtins.str] = None,
    address: typing.Optional[builtins.str] = None,
    alias: typing.Optional[builtins.str] = None,
    auth_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_aws: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginAws, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_azure: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginAzure, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_cert: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginCert, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginGcp, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_jwt: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginJwt, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_kerberos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginKerberos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_oci: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginOci, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_oidc: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginOidc, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_radius: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginRadius, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_token_file: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginTokenFile, typing.Dict[builtins.str, typing.Any]]]]] = None,
    auth_login_userpass: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderAuthLoginUserpass, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ca_cert_dir: typing.Optional[builtins.str] = None,
    ca_cert_file: typing.Optional[builtins.str] = None,
    client_auth: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderClientAuth, typing.Dict[builtins.str, typing.Any]]]]] = None,
    headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VaultProviderHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    max_retries_ccc: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    set_namespace_from_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_child_token: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_get_vault_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_tls_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_server_name: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
    token_name: typing.Optional[builtins.str] = None,
    vault_version_override: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e7844df4f93b164b9a2c1c52b36e03baa237fadb18fe25ad14a1519ddefddf8(
    *,
    name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
