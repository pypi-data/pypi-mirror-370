r'''
# `vault_jwt_auth_backend`

Refer to the Terraform Registry for docs: [`vault_jwt_auth_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend).
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


class JwtAuthBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.jwtAuthBackend.JwtAuthBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend vault_jwt_auth_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        bound_issuer: typing.Optional[builtins.str] = None,
        default_role: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        jwks_ca_pem: typing.Optional[builtins.str] = None,
        jwks_pairs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        jwks_url: typing.Optional[builtins.str] = None,
        jwt_supported_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
        jwt_validation_pubkeys: typing.Optional[typing.Sequence[builtins.str]] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        namespace: typing.Optional[builtins.str] = None,
        namespace_in_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oidc_client_id: typing.Optional[builtins.str] = None,
        oidc_client_secret: typing.Optional[builtins.str] = None,
        oidc_discovery_ca_pem: typing.Optional[builtins.str] = None,
        oidc_discovery_url: typing.Optional[builtins.str] = None,
        oidc_response_mode: typing.Optional[builtins.str] = None,
        oidc_response_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        path: typing.Optional[builtins.str] = None,
        provider_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tune: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["JwtAuthBackendTune", typing.Dict[builtins.str, typing.Any]]]]] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend vault_jwt_auth_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bound_issuer: The value against which to match the iss claim in a JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#bound_issuer JwtAuthBackend#bound_issuer}
        :param default_role: The default role to use if none is provided during login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#default_role JwtAuthBackend#default_role}
        :param description: The description of the auth backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#description JwtAuthBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#disable_remount JwtAuthBackend#disable_remount}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#id JwtAuthBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwks_ca_pem: The CA certificate or chain of certificates, in PEM format, to use to validate connections to the JWKS URL. If not set, system certificates are used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_ca_pem JwtAuthBackend#jwks_ca_pem}
        :param jwks_pairs: List of JWKS URL and optional CA certificate pairs. Cannot be used with 'jwks_url' or 'jwks_ca_pem'. Requires Vault 1.16+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_pairs JwtAuthBackend#jwks_pairs}
        :param jwks_url: JWKS URL to use to authenticate signatures. Cannot be used with 'oidc_discovery_url' or 'jwt_validation_pubkeys'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_url JwtAuthBackend#jwks_url}
        :param jwt_supported_algs: A list of supported signing algorithms. Defaults to [RS256]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwt_supported_algs JwtAuthBackend#jwt_supported_algs}
        :param jwt_validation_pubkeys: A list of PEM-encoded public keys to use to authenticate signatures locally. Cannot be used with 'jwks_url' or 'oidc_discovery_url'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwt_validation_pubkeys JwtAuthBackend#jwt_validation_pubkeys}
        :param local: Specifies if the auth method is local only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#local JwtAuthBackend#local}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#namespace JwtAuthBackend#namespace}
        :param namespace_in_state: Pass namespace in the OIDC state parameter instead of as a separate query parameter. With this setting, the allowed redirect URL(s) in Vault and on the provider side should not contain a namespace query parameter. This means only one redirect URL entry needs to be maintained on the OIDC provider side for all vault namespaces that will be authenticating against it. Defaults to true for new configs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#namespace_in_state JwtAuthBackend#namespace_in_state}
        :param oidc_client_id: Client ID used for OIDC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_client_id JwtAuthBackend#oidc_client_id}
        :param oidc_client_secret: Client Secret used for OIDC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_client_secret JwtAuthBackend#oidc_client_secret}
        :param oidc_discovery_ca_pem: The CA certificate or chain of certificates, in PEM format, to use to validate connections to the OIDC Discovery URL. If not set, system certificates are used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_discovery_ca_pem JwtAuthBackend#oidc_discovery_ca_pem}
        :param oidc_discovery_url: The OIDC Discovery URL, without any .well-known component (base path). Cannot be used with 'jwks_url' or 'jwt_validation_pubkeys'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_discovery_url JwtAuthBackend#oidc_discovery_url}
        :param oidc_response_mode: The response mode to be used in the OAuth2 request. Allowed values are 'query' and 'form_post'. Defaults to 'query'. If using Vault namespaces, and oidc_response_mode is 'form_post', then 'namespace_in_state' should be set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_response_mode JwtAuthBackend#oidc_response_mode}
        :param oidc_response_types: The response types to request. Allowed values are 'code' and 'id_token'. Defaults to 'code'. Note: 'id_token' may only be used if 'oidc_response_mode' is set to 'form_post'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_response_types JwtAuthBackend#oidc_response_types}
        :param path: path to mount the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#path JwtAuthBackend#path}
        :param provider_config: Provider specific handling configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#provider_config JwtAuthBackend#provider_config}
        :param tune: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#tune JwtAuthBackend#tune}.
        :param type: Type of backend. Can be either 'jwt' or 'oidc'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#type JwtAuthBackend#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__737b8648abee4ff850210f2823a65fe9f3d654c840a7374acdd513f1c1213eb1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = JwtAuthBackendConfig(
            bound_issuer=bound_issuer,
            default_role=default_role,
            description=description,
            disable_remount=disable_remount,
            id=id,
            jwks_ca_pem=jwks_ca_pem,
            jwks_pairs=jwks_pairs,
            jwks_url=jwks_url,
            jwt_supported_algs=jwt_supported_algs,
            jwt_validation_pubkeys=jwt_validation_pubkeys,
            local=local,
            namespace=namespace,
            namespace_in_state=namespace_in_state,
            oidc_client_id=oidc_client_id,
            oidc_client_secret=oidc_client_secret,
            oidc_discovery_ca_pem=oidc_discovery_ca_pem,
            oidc_discovery_url=oidc_discovery_url,
            oidc_response_mode=oidc_response_mode,
            oidc_response_types=oidc_response_types,
            path=path,
            provider_config=provider_config,
            tune=tune,
            type=type,
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
        '''Generates CDKTF code for importing a JwtAuthBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the JwtAuthBackend to import.
        :param import_from_id: The id of the existing JwtAuthBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the JwtAuthBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03759e9224d2b1b133bd53a1ecaa0dbcc671e1f7cdda236e9d26251a482f1b5e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putTune")
    def put_tune(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["JwtAuthBackendTune", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8d2c8e3b76fa7fd02d83a718a999e906cf6f9f4ee54dd8b0ec92a0f3e5a90f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTune", [value]))

    @jsii.member(jsii_name="resetBoundIssuer")
    def reset_bound_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIssuer", []))

    @jsii.member(jsii_name="resetDefaultRole")
    def reset_default_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRole", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableRemount")
    def reset_disable_remount(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableRemount", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwksCaPem")
    def reset_jwks_ca_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksCaPem", []))

    @jsii.member(jsii_name="resetJwksPairs")
    def reset_jwks_pairs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksPairs", []))

    @jsii.member(jsii_name="resetJwksUrl")
    def reset_jwks_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksUrl", []))

    @jsii.member(jsii_name="resetJwtSupportedAlgs")
    def reset_jwt_supported_algs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtSupportedAlgs", []))

    @jsii.member(jsii_name="resetJwtValidationPubkeys")
    def reset_jwt_validation_pubkeys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtValidationPubkeys", []))

    @jsii.member(jsii_name="resetLocal")
    def reset_local(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocal", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNamespaceInState")
    def reset_namespace_in_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespaceInState", []))

    @jsii.member(jsii_name="resetOidcClientId")
    def reset_oidc_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcClientId", []))

    @jsii.member(jsii_name="resetOidcClientSecret")
    def reset_oidc_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcClientSecret", []))

    @jsii.member(jsii_name="resetOidcDiscoveryCaPem")
    def reset_oidc_discovery_ca_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcDiscoveryCaPem", []))

    @jsii.member(jsii_name="resetOidcDiscoveryUrl")
    def reset_oidc_discovery_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcDiscoveryUrl", []))

    @jsii.member(jsii_name="resetOidcResponseMode")
    def reset_oidc_response_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcResponseMode", []))

    @jsii.member(jsii_name="resetOidcResponseTypes")
    def reset_oidc_response_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcResponseTypes", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetProviderConfig")
    def reset_provider_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderConfig", []))

    @jsii.member(jsii_name="resetTune")
    def reset_tune(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTune", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="accessor")
    def accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessor"))

    @builtins.property
    @jsii.member(jsii_name="tune")
    def tune(self) -> "JwtAuthBackendTuneList":
        return typing.cast("JwtAuthBackendTuneList", jsii.get(self, "tune"))

    @builtins.property
    @jsii.member(jsii_name="boundIssuerInput")
    def bound_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "boundIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultRoleInput")
    def default_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="disableRemountInput")
    def disable_remount_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableRemountInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksCaPemInput")
    def jwks_ca_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksCaPemInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksPairsInput")
    def jwks_pairs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], jsii.get(self, "jwksPairsInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksUrlInput")
    def jwks_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtSupportedAlgsInput")
    def jwt_supported_algs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jwtSupportedAlgsInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtValidationPubkeysInput")
    def jwt_validation_pubkeys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jwtValidationPubkeysInput"))

    @builtins.property
    @jsii.member(jsii_name="localInput")
    def local_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "localInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInStateInput")
    def namespace_in_state_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "namespaceInStateInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcClientIdInput")
    def oidc_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcClientSecretInput")
    def oidc_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcDiscoveryCaPemInput")
    def oidc_discovery_ca_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcDiscoveryCaPemInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcDiscoveryUrlInput")
    def oidc_discovery_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcDiscoveryUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcResponseModeInput")
    def oidc_response_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcResponseModeInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcResponseTypesInput")
    def oidc_response_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "oidcResponseTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="providerConfigInput")
    def provider_config_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "providerConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="tuneInput")
    def tune_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["JwtAuthBackendTune"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["JwtAuthBackendTune"]]], jsii.get(self, "tuneInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIssuer")
    def bound_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "boundIssuer"))

    @bound_issuer.setter
    def bound_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcb4459a2f1e081f276ca3f9fd05f710d4c3c3f65990d1008716c4ace097e741)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIssuer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultRole")
    def default_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRole"))

    @default_role.setter
    def default_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09aa0d15b11708c275d698487420e958175219f04175890ba109f5d71efb3c2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25eb738bcc128047bdd52b670ecbe6cb9a6600224fb39658f7ec64e8c41d24ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableRemount")
    def disable_remount(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableRemount"))

    @disable_remount.setter
    def disable_remount(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__842f21ff7436a6323327d9d7918fdbcfb51429f5c0c870181bcd3c5231cd5fab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableRemount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3307ace947d82f3129b7aa5fdfbcdb53e738631330a51586e5871a91c209d13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwksCaPem")
    def jwks_ca_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksCaPem"))

    @jwks_ca_pem.setter
    def jwks_ca_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28e35ac54c3ab1d6e562143bac740810d53b970a4c21b6bd12a67fda340e7db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksCaPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwksPairs")
    def jwks_pairs(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "jwksPairs"))

    @jwks_pairs.setter
    def jwks_pairs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__976a697c03804db217922d87ae74d6da58f9a742f8070b22f3159f0c757b7cf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksPairs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwksUrl")
    def jwks_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksUrl"))

    @jwks_url.setter
    def jwks_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__200edaefa2b856b8213f4043ae533454cbba173e772072cd2c84742b7e3fddc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwtSupportedAlgs")
    def jwt_supported_algs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jwtSupportedAlgs"))

    @jwt_supported_algs.setter
    def jwt_supported_algs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e2f299c4ee368b112523d4a6d7b94154e49f2e1a67ac923d5ac75da49ce9a97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtSupportedAlgs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwtValidationPubkeys")
    def jwt_validation_pubkeys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jwtValidationPubkeys"))

    @jwt_validation_pubkeys.setter
    def jwt_validation_pubkeys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8678c709a3bfc64a5b72b26568a2d1c53911487e86e207b7b6a1258e0090e37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtValidationPubkeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="local")
    def local(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "local"))

    @local.setter
    def local(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08fe588ee4ad59925119125aabce34dc26317f5fe9112269d5b913b2acf94691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2e26988cc569bb0e63358066b35b7c9a692614dfed32a27c5dd0021f8adf47d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespaceInState")
    def namespace_in_state(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "namespaceInState"))

    @namespace_in_state.setter
    def namespace_in_state(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1a2e1ce56b53647cf5a7ead3ad7ff147ddd165c0c9a01fe33dd6e89c57eea0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespaceInState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcClientId")
    def oidc_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcClientId"))

    @oidc_client_id.setter
    def oidc_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e931fb3152c46d132e8109e6f8c1dd80ad96d4b0bb915997bb218be07a6d39c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcClientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcClientSecret")
    def oidc_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcClientSecret"))

    @oidc_client_secret.setter
    def oidc_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f59fb6be0ecc6ea5aa209c67290efd729309d4175a3a00956187b9833d84ad7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcDiscoveryCaPem")
    def oidc_discovery_ca_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcDiscoveryCaPem"))

    @oidc_discovery_ca_pem.setter
    def oidc_discovery_ca_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cee03174d4c3e4f566365a904f8a0581e1cdff6a3f9f0b3f12548b138cbcc4a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcDiscoveryCaPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcDiscoveryUrl")
    def oidc_discovery_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcDiscoveryUrl"))

    @oidc_discovery_url.setter
    def oidc_discovery_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__326cde6e3a65e033d83695c41c6cb0817cf2c93742f551aceff5c04baa5a2e03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcDiscoveryUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcResponseMode")
    def oidc_response_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcResponseMode"))

    @oidc_response_mode.setter
    def oidc_response_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34dc8cba8d63b29240cd8d0fca37fe48d92d911808fee19ec6014cd7bdaa59c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcResponseMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcResponseTypes")
    def oidc_response_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "oidcResponseTypes"))

    @oidc_response_types.setter
    def oidc_response_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7abe5ad35a4ae59be717cbccc99de7c4ecc12a18b84a275c0b18086d23398896)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcResponseTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e384bc14fba76ab9f3acf2018d02c5263160e90511b0d9642cddf16e5ef080dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerConfig")
    def provider_config(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "providerConfig"))

    @provider_config.setter
    def provider_config(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__815fea5651c99925a9e006e557789785935bcd6c0ab176591d060fdc26cdbc09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerConfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10e3480631db0801fb18dd0b57eea2b5a01400841db18582170b12fa0376b454)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.jwtAuthBackend.JwtAuthBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "bound_issuer": "boundIssuer",
        "default_role": "defaultRole",
        "description": "description",
        "disable_remount": "disableRemount",
        "id": "id",
        "jwks_ca_pem": "jwksCaPem",
        "jwks_pairs": "jwksPairs",
        "jwks_url": "jwksUrl",
        "jwt_supported_algs": "jwtSupportedAlgs",
        "jwt_validation_pubkeys": "jwtValidationPubkeys",
        "local": "local",
        "namespace": "namespace",
        "namespace_in_state": "namespaceInState",
        "oidc_client_id": "oidcClientId",
        "oidc_client_secret": "oidcClientSecret",
        "oidc_discovery_ca_pem": "oidcDiscoveryCaPem",
        "oidc_discovery_url": "oidcDiscoveryUrl",
        "oidc_response_mode": "oidcResponseMode",
        "oidc_response_types": "oidcResponseTypes",
        "path": "path",
        "provider_config": "providerConfig",
        "tune": "tune",
        "type": "type",
    },
)
class JwtAuthBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        bound_issuer: typing.Optional[builtins.str] = None,
        default_role: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        jwks_ca_pem: typing.Optional[builtins.str] = None,
        jwks_pairs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        jwks_url: typing.Optional[builtins.str] = None,
        jwt_supported_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
        jwt_validation_pubkeys: typing.Optional[typing.Sequence[builtins.str]] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        namespace: typing.Optional[builtins.str] = None,
        namespace_in_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oidc_client_id: typing.Optional[builtins.str] = None,
        oidc_client_secret: typing.Optional[builtins.str] = None,
        oidc_discovery_ca_pem: typing.Optional[builtins.str] = None,
        oidc_discovery_url: typing.Optional[builtins.str] = None,
        oidc_response_mode: typing.Optional[builtins.str] = None,
        oidc_response_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        path: typing.Optional[builtins.str] = None,
        provider_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tune: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["JwtAuthBackendTune", typing.Dict[builtins.str, typing.Any]]]]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param bound_issuer: The value against which to match the iss claim in a JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#bound_issuer JwtAuthBackend#bound_issuer}
        :param default_role: The default role to use if none is provided during login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#default_role JwtAuthBackend#default_role}
        :param description: The description of the auth backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#description JwtAuthBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#disable_remount JwtAuthBackend#disable_remount}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#id JwtAuthBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwks_ca_pem: The CA certificate or chain of certificates, in PEM format, to use to validate connections to the JWKS URL. If not set, system certificates are used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_ca_pem JwtAuthBackend#jwks_ca_pem}
        :param jwks_pairs: List of JWKS URL and optional CA certificate pairs. Cannot be used with 'jwks_url' or 'jwks_ca_pem'. Requires Vault 1.16+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_pairs JwtAuthBackend#jwks_pairs}
        :param jwks_url: JWKS URL to use to authenticate signatures. Cannot be used with 'oidc_discovery_url' or 'jwt_validation_pubkeys'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_url JwtAuthBackend#jwks_url}
        :param jwt_supported_algs: A list of supported signing algorithms. Defaults to [RS256]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwt_supported_algs JwtAuthBackend#jwt_supported_algs}
        :param jwt_validation_pubkeys: A list of PEM-encoded public keys to use to authenticate signatures locally. Cannot be used with 'jwks_url' or 'oidc_discovery_url'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwt_validation_pubkeys JwtAuthBackend#jwt_validation_pubkeys}
        :param local: Specifies if the auth method is local only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#local JwtAuthBackend#local}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#namespace JwtAuthBackend#namespace}
        :param namespace_in_state: Pass namespace in the OIDC state parameter instead of as a separate query parameter. With this setting, the allowed redirect URL(s) in Vault and on the provider side should not contain a namespace query parameter. This means only one redirect URL entry needs to be maintained on the OIDC provider side for all vault namespaces that will be authenticating against it. Defaults to true for new configs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#namespace_in_state JwtAuthBackend#namespace_in_state}
        :param oidc_client_id: Client ID used for OIDC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_client_id JwtAuthBackend#oidc_client_id}
        :param oidc_client_secret: Client Secret used for OIDC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_client_secret JwtAuthBackend#oidc_client_secret}
        :param oidc_discovery_ca_pem: The CA certificate or chain of certificates, in PEM format, to use to validate connections to the OIDC Discovery URL. If not set, system certificates are used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_discovery_ca_pem JwtAuthBackend#oidc_discovery_ca_pem}
        :param oidc_discovery_url: The OIDC Discovery URL, without any .well-known component (base path). Cannot be used with 'jwks_url' or 'jwt_validation_pubkeys'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_discovery_url JwtAuthBackend#oidc_discovery_url}
        :param oidc_response_mode: The response mode to be used in the OAuth2 request. Allowed values are 'query' and 'form_post'. Defaults to 'query'. If using Vault namespaces, and oidc_response_mode is 'form_post', then 'namespace_in_state' should be set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_response_mode JwtAuthBackend#oidc_response_mode}
        :param oidc_response_types: The response types to request. Allowed values are 'code' and 'id_token'. Defaults to 'code'. Note: 'id_token' may only be used if 'oidc_response_mode' is set to 'form_post'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_response_types JwtAuthBackend#oidc_response_types}
        :param path: path to mount the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#path JwtAuthBackend#path}
        :param provider_config: Provider specific handling configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#provider_config JwtAuthBackend#provider_config}
        :param tune: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#tune JwtAuthBackend#tune}.
        :param type: Type of backend. Can be either 'jwt' or 'oidc'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#type JwtAuthBackend#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0ca3a9a25ad6d31b97f95d3222e7f066583af77e393e4fa16c547be9a98a6f9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument bound_issuer", value=bound_issuer, expected_type=type_hints["bound_issuer"])
            check_type(argname="argument default_role", value=default_role, expected_type=type_hints["default_role"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_remount", value=disable_remount, expected_type=type_hints["disable_remount"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwks_ca_pem", value=jwks_ca_pem, expected_type=type_hints["jwks_ca_pem"])
            check_type(argname="argument jwks_pairs", value=jwks_pairs, expected_type=type_hints["jwks_pairs"])
            check_type(argname="argument jwks_url", value=jwks_url, expected_type=type_hints["jwks_url"])
            check_type(argname="argument jwt_supported_algs", value=jwt_supported_algs, expected_type=type_hints["jwt_supported_algs"])
            check_type(argname="argument jwt_validation_pubkeys", value=jwt_validation_pubkeys, expected_type=type_hints["jwt_validation_pubkeys"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument namespace_in_state", value=namespace_in_state, expected_type=type_hints["namespace_in_state"])
            check_type(argname="argument oidc_client_id", value=oidc_client_id, expected_type=type_hints["oidc_client_id"])
            check_type(argname="argument oidc_client_secret", value=oidc_client_secret, expected_type=type_hints["oidc_client_secret"])
            check_type(argname="argument oidc_discovery_ca_pem", value=oidc_discovery_ca_pem, expected_type=type_hints["oidc_discovery_ca_pem"])
            check_type(argname="argument oidc_discovery_url", value=oidc_discovery_url, expected_type=type_hints["oidc_discovery_url"])
            check_type(argname="argument oidc_response_mode", value=oidc_response_mode, expected_type=type_hints["oidc_response_mode"])
            check_type(argname="argument oidc_response_types", value=oidc_response_types, expected_type=type_hints["oidc_response_types"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument provider_config", value=provider_config, expected_type=type_hints["provider_config"])
            check_type(argname="argument tune", value=tune, expected_type=type_hints["tune"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if bound_issuer is not None:
            self._values["bound_issuer"] = bound_issuer
        if default_role is not None:
            self._values["default_role"] = default_role
        if description is not None:
            self._values["description"] = description
        if disable_remount is not None:
            self._values["disable_remount"] = disable_remount
        if id is not None:
            self._values["id"] = id
        if jwks_ca_pem is not None:
            self._values["jwks_ca_pem"] = jwks_ca_pem
        if jwks_pairs is not None:
            self._values["jwks_pairs"] = jwks_pairs
        if jwks_url is not None:
            self._values["jwks_url"] = jwks_url
        if jwt_supported_algs is not None:
            self._values["jwt_supported_algs"] = jwt_supported_algs
        if jwt_validation_pubkeys is not None:
            self._values["jwt_validation_pubkeys"] = jwt_validation_pubkeys
        if local is not None:
            self._values["local"] = local
        if namespace is not None:
            self._values["namespace"] = namespace
        if namespace_in_state is not None:
            self._values["namespace_in_state"] = namespace_in_state
        if oidc_client_id is not None:
            self._values["oidc_client_id"] = oidc_client_id
        if oidc_client_secret is not None:
            self._values["oidc_client_secret"] = oidc_client_secret
        if oidc_discovery_ca_pem is not None:
            self._values["oidc_discovery_ca_pem"] = oidc_discovery_ca_pem
        if oidc_discovery_url is not None:
            self._values["oidc_discovery_url"] = oidc_discovery_url
        if oidc_response_mode is not None:
            self._values["oidc_response_mode"] = oidc_response_mode
        if oidc_response_types is not None:
            self._values["oidc_response_types"] = oidc_response_types
        if path is not None:
            self._values["path"] = path
        if provider_config is not None:
            self._values["provider_config"] = provider_config
        if tune is not None:
            self._values["tune"] = tune
        if type is not None:
            self._values["type"] = type

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
    def bound_issuer(self) -> typing.Optional[builtins.str]:
        '''The value against which to match the iss claim in a JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#bound_issuer JwtAuthBackend#bound_issuer}
        '''
        result = self._values.get("bound_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_role(self) -> typing.Optional[builtins.str]:
        '''The default role to use if none is provided during login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#default_role JwtAuthBackend#default_role}
        '''
        result = self._values.get("default_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the auth backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#description JwtAuthBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#disable_remount JwtAuthBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#id JwtAuthBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_ca_pem(self) -> typing.Optional[builtins.str]:
        '''The CA certificate or chain of certificates, in PEM format, to use to validate connections to the JWKS URL.

        If not set, system certificates are used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_ca_pem JwtAuthBackend#jwks_ca_pem}
        '''
        result = self._values.get("jwks_ca_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_pairs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''List of JWKS URL and optional CA certificate pairs. Cannot be used with 'jwks_url' or 'jwks_ca_pem'. Requires Vault 1.16+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_pairs JwtAuthBackend#jwks_pairs}
        '''
        result = self._values.get("jwks_pairs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def jwks_url(self) -> typing.Optional[builtins.str]:
        '''JWKS URL to use to authenticate signatures. Cannot be used with 'oidc_discovery_url' or 'jwt_validation_pubkeys'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwks_url JwtAuthBackend#jwks_url}
        '''
        result = self._values.get("jwks_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_supported_algs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of supported signing algorithms. Defaults to [RS256].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwt_supported_algs JwtAuthBackend#jwt_supported_algs}
        '''
        result = self._values.get("jwt_supported_algs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def jwt_validation_pubkeys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of PEM-encoded public keys to use to authenticate signatures locally.

        Cannot be used with 'jwks_url' or 'oidc_discovery_url'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#jwt_validation_pubkeys JwtAuthBackend#jwt_validation_pubkeys}
        '''
        result = self._values.get("jwt_validation_pubkeys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if the auth method is local only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#local JwtAuthBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#namespace JwtAuthBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace_in_state(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Pass namespace in the OIDC state parameter instead of as a separate query parameter.

        With this setting, the allowed redirect URL(s) in Vault and on the provider side should not contain a namespace query parameter. This means only one redirect URL entry needs to be maintained on the OIDC provider side for all vault namespaces that will be authenticating against it. Defaults to true for new configs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#namespace_in_state JwtAuthBackend#namespace_in_state}
        '''
        result = self._values.get("namespace_in_state")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def oidc_client_id(self) -> typing.Optional[builtins.str]:
        '''Client ID used for OIDC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_client_id JwtAuthBackend#oidc_client_id}
        '''
        result = self._values.get("oidc_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_client_secret(self) -> typing.Optional[builtins.str]:
        '''Client Secret used for OIDC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_client_secret JwtAuthBackend#oidc_client_secret}
        '''
        result = self._values.get("oidc_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_discovery_ca_pem(self) -> typing.Optional[builtins.str]:
        '''The CA certificate or chain of certificates, in PEM format, to use to validate connections to the OIDC Discovery URL.

        If not set, system certificates are used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_discovery_ca_pem JwtAuthBackend#oidc_discovery_ca_pem}
        '''
        result = self._values.get("oidc_discovery_ca_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_discovery_url(self) -> typing.Optional[builtins.str]:
        '''The OIDC Discovery URL, without any .well-known component (base path). Cannot be used with 'jwks_url' or 'jwt_validation_pubkeys'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_discovery_url JwtAuthBackend#oidc_discovery_url}
        '''
        result = self._values.get("oidc_discovery_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_response_mode(self) -> typing.Optional[builtins.str]:
        '''The response mode to be used in the OAuth2 request.

        Allowed values are 'query' and 'form_post'. Defaults to 'query'. If using Vault namespaces, and oidc_response_mode is 'form_post', then 'namespace_in_state' should be set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_response_mode JwtAuthBackend#oidc_response_mode}
        '''
        result = self._values.get("oidc_response_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_response_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The response types to request.

        Allowed values are 'code' and 'id_token'. Defaults to 'code'. Note: 'id_token' may only be used if 'oidc_response_mode' is set to 'form_post'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#oidc_response_types JwtAuthBackend#oidc_response_types}
        '''
        result = self._values.get("oidc_response_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''path to mount the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#path JwtAuthBackend#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_config(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Provider specific handling configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#provider_config JwtAuthBackend#provider_config}
        '''
        result = self._values.get("provider_config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tune(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["JwtAuthBackendTune"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#tune JwtAuthBackend#tune}.'''
        result = self._values.get("tune")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["JwtAuthBackendTune"]]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Type of backend. Can be either 'jwt' or 'oidc'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#type JwtAuthBackend#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JwtAuthBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.jwtAuthBackend.JwtAuthBackendTune",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_response_headers": "allowedResponseHeaders",
        "audit_non_hmac_request_keys": "auditNonHmacRequestKeys",
        "audit_non_hmac_response_keys": "auditNonHmacResponseKeys",
        "default_lease_ttl": "defaultLeaseTtl",
        "listing_visibility": "listingVisibility",
        "max_lease_ttl": "maxLeaseTtl",
        "passthrough_request_headers": "passthroughRequestHeaders",
        "token_type": "tokenType",
    },
)
class JwtAuthBackendTune:
    def __init__(
        self,
        *,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_lease_ttl: typing.Optional[builtins.str] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        max_lease_ttl: typing.Optional[builtins.str] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param allowed_response_headers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#allowed_response_headers JwtAuthBackend#allowed_response_headers}.
        :param audit_non_hmac_request_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#audit_non_hmac_request_keys JwtAuthBackend#audit_non_hmac_request_keys}.
        :param audit_non_hmac_response_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#audit_non_hmac_response_keys JwtAuthBackend#audit_non_hmac_response_keys}.
        :param default_lease_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#default_lease_ttl JwtAuthBackend#default_lease_ttl}.
        :param listing_visibility: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#listing_visibility JwtAuthBackend#listing_visibility}.
        :param max_lease_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#max_lease_ttl JwtAuthBackend#max_lease_ttl}.
        :param passthrough_request_headers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#passthrough_request_headers JwtAuthBackend#passthrough_request_headers}.
        :param token_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#token_type JwtAuthBackend#token_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cc80b1b1eb1f84c0b92f07d05c4c988c4c103258307ee22d88928e504152dd4)
            check_type(argname="argument allowed_response_headers", value=allowed_response_headers, expected_type=type_hints["allowed_response_headers"])
            check_type(argname="argument audit_non_hmac_request_keys", value=audit_non_hmac_request_keys, expected_type=type_hints["audit_non_hmac_request_keys"])
            check_type(argname="argument audit_non_hmac_response_keys", value=audit_non_hmac_response_keys, expected_type=type_hints["audit_non_hmac_response_keys"])
            check_type(argname="argument default_lease_ttl", value=default_lease_ttl, expected_type=type_hints["default_lease_ttl"])
            check_type(argname="argument listing_visibility", value=listing_visibility, expected_type=type_hints["listing_visibility"])
            check_type(argname="argument max_lease_ttl", value=max_lease_ttl, expected_type=type_hints["max_lease_ttl"])
            check_type(argname="argument passthrough_request_headers", value=passthrough_request_headers, expected_type=type_hints["passthrough_request_headers"])
            check_type(argname="argument token_type", value=token_type, expected_type=type_hints["token_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_response_headers is not None:
            self._values["allowed_response_headers"] = allowed_response_headers
        if audit_non_hmac_request_keys is not None:
            self._values["audit_non_hmac_request_keys"] = audit_non_hmac_request_keys
        if audit_non_hmac_response_keys is not None:
            self._values["audit_non_hmac_response_keys"] = audit_non_hmac_response_keys
        if default_lease_ttl is not None:
            self._values["default_lease_ttl"] = default_lease_ttl
        if listing_visibility is not None:
            self._values["listing_visibility"] = listing_visibility
        if max_lease_ttl is not None:
            self._values["max_lease_ttl"] = max_lease_ttl
        if passthrough_request_headers is not None:
            self._values["passthrough_request_headers"] = passthrough_request_headers
        if token_type is not None:
            self._values["token_type"] = token_type

    @builtins.property
    def allowed_response_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#allowed_response_headers JwtAuthBackend#allowed_response_headers}.'''
        result = self._values.get("allowed_response_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_request_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#audit_non_hmac_request_keys JwtAuthBackend#audit_non_hmac_request_keys}.'''
        result = self._values.get("audit_non_hmac_request_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_response_keys(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#audit_non_hmac_response_keys JwtAuthBackend#audit_non_hmac_response_keys}.'''
        result = self._values.get("audit_non_hmac_response_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_lease_ttl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#default_lease_ttl JwtAuthBackend#default_lease_ttl}.'''
        result = self._values.get("default_lease_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def listing_visibility(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#listing_visibility JwtAuthBackend#listing_visibility}.'''
        result = self._values.get("listing_visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_lease_ttl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#max_lease_ttl JwtAuthBackend#max_lease_ttl}.'''
        result = self._values.get("max_lease_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passthrough_request_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#passthrough_request_headers JwtAuthBackend#passthrough_request_headers}.'''
        result = self._values.get("passthrough_request_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend#token_type JwtAuthBackend#token_type}.'''
        result = self._values.get("token_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JwtAuthBackendTune(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class JwtAuthBackendTuneList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.jwtAuthBackend.JwtAuthBackendTuneList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__446fb1a1206adde9a19543ba76dbb1af319ae636e851fd83789408148e0eec58)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "JwtAuthBackendTuneOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc5cc564eb096cf6186e622b981b0d672e4c45c0bf8b6f859021060fda0a4f5e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("JwtAuthBackendTuneOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d21bcfb5cc0a2f4fac0ea77b38cea04408c84c7e31370b7a8ae81a8c3ac3c31)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3939561fdbed64631194dcf2f7883f9199c41b17a156b5e1b8cb0c1a2953bbae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a61962f57b2cb422df63b42c20b90b67047a5c9c529d1ae9a34059ac31868d7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[JwtAuthBackendTune]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[JwtAuthBackendTune]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[JwtAuthBackendTune]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6f45202156438f19b79379d9f7a88e14432f74b74b5cc7e42ac1a13db6ee9e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class JwtAuthBackendTuneOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.jwtAuthBackend.JwtAuthBackendTuneOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7083547beda2f434b949b7655e0493c8c939afd4bbb6bfe36cea6da6787430c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAllowedResponseHeaders")
    def reset_allowed_response_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedResponseHeaders", []))

    @jsii.member(jsii_name="resetAuditNonHmacRequestKeys")
    def reset_audit_non_hmac_request_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditNonHmacRequestKeys", []))

    @jsii.member(jsii_name="resetAuditNonHmacResponseKeys")
    def reset_audit_non_hmac_response_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditNonHmacResponseKeys", []))

    @jsii.member(jsii_name="resetDefaultLeaseTtl")
    def reset_default_lease_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultLeaseTtl", []))

    @jsii.member(jsii_name="resetListingVisibility")
    def reset_listing_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetListingVisibility", []))

    @jsii.member(jsii_name="resetMaxLeaseTtl")
    def reset_max_lease_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLeaseTtl", []))

    @jsii.member(jsii_name="resetPassthroughRequestHeaders")
    def reset_passthrough_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassthroughRequestHeaders", []))

    @jsii.member(jsii_name="resetTokenType")
    def reset_token_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenType", []))

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeadersInput")
    def allowed_response_headers_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedResponseHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeysInput")
    def audit_non_hmac_request_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "auditNonHmacRequestKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeysInput")
    def audit_non_hmac_response_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "auditNonHmacResponseKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlInput")
    def default_lease_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultLeaseTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="listingVisibilityInput")
    def listing_visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "listingVisibilityInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlInput")
    def max_lease_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxLeaseTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeadersInput")
    def passthrough_request_headers_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "passthroughRequestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenTypeInput")
    def token_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeaders")
    def allowed_response_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedResponseHeaders"))

    @allowed_response_headers.setter
    def allowed_response_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8c04302991f90c437fc8c643cd708e75b6be86f671c540ffc56242601c684af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedResponseHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeys")
    def audit_non_hmac_request_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacRequestKeys"))

    @audit_non_hmac_request_keys.setter
    def audit_non_hmac_request_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0a5e20cd115b25169e9b9ceda7a8ecd8b6657ae47dac978d202951b388cc8cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacRequestKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeys")
    def audit_non_hmac_response_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacResponseKeys"))

    @audit_non_hmac_response_keys.setter
    def audit_non_hmac_response_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef00d625da63af832f199c93757d31a106840632567e3000aa42b2bc4b303987)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacResponseKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtl")
    def default_lease_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultLeaseTtl"))

    @default_lease_ttl.setter
    def default_lease_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1809c7ee2c325243903a6e809cd105bac18f3e95713dd20dc491604cd9502a0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listingVisibility")
    def listing_visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listingVisibility"))

    @listing_visibility.setter
    def listing_visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__818161e82cfe698a33375580264ae4cf457f6b483c1222970042f8da6b608017)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "listingVisibility", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtl")
    def max_lease_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxLeaseTtl"))

    @max_lease_ttl.setter
    def max_lease_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e87fdcc844e6989a07f8a7327e513a34051a4964255c540ae48ca0d509bc6618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeaders")
    def passthrough_request_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passthroughRequestHeaders"))

    @passthrough_request_headers.setter
    def passthrough_request_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cbfc3710587218389737d0f1b7e460bf85b8c0974914c96c0499362911057f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passthroughRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenType")
    def token_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenType"))

    @token_type.setter
    def token_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68321bbe1529f43663743f51518be297bde37e07c116c3b9e574786dbc28d778)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, JwtAuthBackendTune]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, JwtAuthBackendTune]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, JwtAuthBackendTune]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cf0d7cf61699f958e0c409ba6ad9f7bbdca14c91f2a235fb382acdebff3c632)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "JwtAuthBackend",
    "JwtAuthBackendConfig",
    "JwtAuthBackendTune",
    "JwtAuthBackendTuneList",
    "JwtAuthBackendTuneOutputReference",
]

publication.publish()

def _typecheckingstub__737b8648abee4ff850210f2823a65fe9f3d654c840a7374acdd513f1c1213eb1(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    bound_issuer: typing.Optional[builtins.str] = None,
    default_role: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    jwks_ca_pem: typing.Optional[builtins.str] = None,
    jwks_pairs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    jwks_url: typing.Optional[builtins.str] = None,
    jwt_supported_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
    jwt_validation_pubkeys: typing.Optional[typing.Sequence[builtins.str]] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    namespace: typing.Optional[builtins.str] = None,
    namespace_in_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oidc_client_id: typing.Optional[builtins.str] = None,
    oidc_client_secret: typing.Optional[builtins.str] = None,
    oidc_discovery_ca_pem: typing.Optional[builtins.str] = None,
    oidc_discovery_url: typing.Optional[builtins.str] = None,
    oidc_response_mode: typing.Optional[builtins.str] = None,
    oidc_response_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    path: typing.Optional[builtins.str] = None,
    provider_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    tune: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[JwtAuthBackendTune, typing.Dict[builtins.str, typing.Any]]]]] = None,
    type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__03759e9224d2b1b133bd53a1ecaa0dbcc671e1f7cdda236e9d26251a482f1b5e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d2c8e3b76fa7fd02d83a718a999e906cf6f9f4ee54dd8b0ec92a0f3e5a90f7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[JwtAuthBackendTune, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb4459a2f1e081f276ca3f9fd05f710d4c3c3f65990d1008716c4ace097e741(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09aa0d15b11708c275d698487420e958175219f04175890ba109f5d71efb3c2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25eb738bcc128047bdd52b670ecbe6cb9a6600224fb39658f7ec64e8c41d24ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__842f21ff7436a6323327d9d7918fdbcfb51429f5c0c870181bcd3c5231cd5fab(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3307ace947d82f3129b7aa5fdfbcdb53e738631330a51586e5871a91c209d13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28e35ac54c3ab1d6e562143bac740810d53b970a4c21b6bd12a67fda340e7db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__976a697c03804db217922d87ae74d6da58f9a742f8070b22f3159f0c757b7cf0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__200edaefa2b856b8213f4043ae533454cbba173e772072cd2c84742b7e3fddc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e2f299c4ee368b112523d4a6d7b94154e49f2e1a67ac923d5ac75da49ce9a97(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8678c709a3bfc64a5b72b26568a2d1c53911487e86e207b7b6a1258e0090e37(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08fe588ee4ad59925119125aabce34dc26317f5fe9112269d5b913b2acf94691(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e26988cc569bb0e63358066b35b7c9a692614dfed32a27c5dd0021f8adf47d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1a2e1ce56b53647cf5a7ead3ad7ff147ddd165c0c9a01fe33dd6e89c57eea0a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e931fb3152c46d132e8109e6f8c1dd80ad96d4b0bb915997bb218be07a6d39c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f59fb6be0ecc6ea5aa209c67290efd729309d4175a3a00956187b9833d84ad7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cee03174d4c3e4f566365a904f8a0581e1cdff6a3f9f0b3f12548b138cbcc4a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__326cde6e3a65e033d83695c41c6cb0817cf2c93742f551aceff5c04baa5a2e03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34dc8cba8d63b29240cd8d0fca37fe48d92d911808fee19ec6014cd7bdaa59c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7abe5ad35a4ae59be717cbccc99de7c4ecc12a18b84a275c0b18086d23398896(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e384bc14fba76ab9f3acf2018d02c5263160e90511b0d9642cddf16e5ef080dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__815fea5651c99925a9e006e557789785935bcd6c0ab176591d060fdc26cdbc09(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10e3480631db0801fb18dd0b57eea2b5a01400841db18582170b12fa0376b454(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0ca3a9a25ad6d31b97f95d3222e7f066583af77e393e4fa16c547be9a98a6f9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bound_issuer: typing.Optional[builtins.str] = None,
    default_role: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    jwks_ca_pem: typing.Optional[builtins.str] = None,
    jwks_pairs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    jwks_url: typing.Optional[builtins.str] = None,
    jwt_supported_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
    jwt_validation_pubkeys: typing.Optional[typing.Sequence[builtins.str]] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    namespace: typing.Optional[builtins.str] = None,
    namespace_in_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oidc_client_id: typing.Optional[builtins.str] = None,
    oidc_client_secret: typing.Optional[builtins.str] = None,
    oidc_discovery_ca_pem: typing.Optional[builtins.str] = None,
    oidc_discovery_url: typing.Optional[builtins.str] = None,
    oidc_response_mode: typing.Optional[builtins.str] = None,
    oidc_response_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    path: typing.Optional[builtins.str] = None,
    provider_config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    tune: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[JwtAuthBackendTune, typing.Dict[builtins.str, typing.Any]]]]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cc80b1b1eb1f84c0b92f07d05c4c988c4c103258307ee22d88928e504152dd4(
    *,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_lease_ttl: typing.Optional[builtins.str] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    max_lease_ttl: typing.Optional[builtins.str] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__446fb1a1206adde9a19543ba76dbb1af319ae636e851fd83789408148e0eec58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc5cc564eb096cf6186e622b981b0d672e4c45c0bf8b6f859021060fda0a4f5e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d21bcfb5cc0a2f4fac0ea77b38cea04408c84c7e31370b7a8ae81a8c3ac3c31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3939561fdbed64631194dcf2f7883f9199c41b17a156b5e1b8cb0c1a2953bbae(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a61962f57b2cb422df63b42c20b90b67047a5c9c529d1ae9a34059ac31868d7c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6f45202156438f19b79379d9f7a88e14432f74b74b5cc7e42ac1a13db6ee9e4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[JwtAuthBackendTune]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7083547beda2f434b949b7655e0493c8c939afd4bbb6bfe36cea6da6787430c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c04302991f90c437fc8c643cd708e75b6be86f671c540ffc56242601c684af(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a5e20cd115b25169e9b9ceda7a8ecd8b6657ae47dac978d202951b388cc8cd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef00d625da63af832f199c93757d31a106840632567e3000aa42b2bc4b303987(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1809c7ee2c325243903a6e809cd105bac18f3e95713dd20dc491604cd9502a0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__818161e82cfe698a33375580264ae4cf457f6b483c1222970042f8da6b608017(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e87fdcc844e6989a07f8a7327e513a34051a4964255c540ae48ca0d509bc6618(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cbfc3710587218389737d0f1b7e460bf85b8c0974914c96c0499362911057f9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68321bbe1529f43663743f51518be297bde37e07c116c3b9e574786dbc28d778(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf0d7cf61699f958e0c409ba6ad9f7bbdca14c91f2a235fb382acdebff3c632(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, JwtAuthBackendTune]],
) -> None:
    """Type checking stubs"""
    pass
