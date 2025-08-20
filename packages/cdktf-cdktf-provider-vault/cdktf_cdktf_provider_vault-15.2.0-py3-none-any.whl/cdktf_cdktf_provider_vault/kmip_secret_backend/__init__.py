r'''
# `vault_kmip_secret_backend`

Refer to the Terraform Registry for docs: [`vault_kmip_secret_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend).
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


class KmipSecretBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.kmipSecretBackend.KmipSecretBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend vault_kmip_secret_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        path: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        default_tls_client_key_bits: typing.Optional[jsii.Number] = None,
        default_tls_client_key_type: typing.Optional[builtins.str] = None,
        default_tls_client_ttl: typing.Optional[jsii.Number] = None,
        delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_key: typing.Optional[builtins.str] = None,
        listen_addrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        server_hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
        server_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_ca_key_bits: typing.Optional[jsii.Number] = None,
        tls_ca_key_type: typing.Optional[builtins.str] = None,
        tls_min_version: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend vault_kmip_secret_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param path: Path where KMIP secret backend will be mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#path KmipSecretBackend#path}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#allowed_managed_keys KmipSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#allowed_response_headers KmipSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#audit_non_hmac_request_keys KmipSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#audit_non_hmac_response_keys KmipSecretBackend#audit_non_hmac_response_keys}
        :param default_lease_ttl_seconds: Default lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_lease_ttl_seconds KmipSecretBackend#default_lease_ttl_seconds}
        :param default_tls_client_key_bits: Client certificate key bits, valid values depend on key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_key_bits KmipSecretBackend#default_tls_client_key_bits}
        :param default_tls_client_key_type: Client certificate key type, rsa or ec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_key_type KmipSecretBackend#default_tls_client_key_type}
        :param default_tls_client_ttl: Client certificate TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_ttl KmipSecretBackend#default_tls_client_ttl}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#delegated_auth_accessors KmipSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#description KmipSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#disable_remount KmipSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#external_entropy_access KmipSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#force_no_cache KmipSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#id KmipSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#identity_token_key KmipSecretBackend#identity_token_key}
        :param listen_addrs: Addresses the KMIP server should listen on (host:port). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#listen_addrs KmipSecretBackend#listen_addrs}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#listing_visibility KmipSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#local KmipSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#max_lease_ttl_seconds KmipSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#namespace KmipSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#options KmipSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#passthrough_request_headers KmipSecretBackend#passthrough_request_headers}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#plugin_version KmipSecretBackend#plugin_version}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#seal_wrap KmipSecretBackend#seal_wrap}
        :param server_hostnames: Hostnames to include in the server's TLS certificate as SAN DNS names. The first will be used as the common name (CN) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#server_hostnames KmipSecretBackend#server_hostnames}
        :param server_ips: IPs to include in the server's TLS certificate as SAN IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#server_ips KmipSecretBackend#server_ips}
        :param tls_ca_key_bits: CA key bits, valid values depend on key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_ca_key_bits KmipSecretBackend#tls_ca_key_bits}
        :param tls_ca_key_type: CA key type, rsa or ec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_ca_key_type KmipSecretBackend#tls_ca_key_type}
        :param tls_min_version: Minimum TLS version to accept. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_min_version KmipSecretBackend#tls_min_version}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f1cd19672cd534fbe2c663ed130e68e1e5d6c4c568f62919c3e110aa1cc1c1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = KmipSecretBackendConfig(
            path=path,
            allowed_managed_keys=allowed_managed_keys,
            allowed_response_headers=allowed_response_headers,
            audit_non_hmac_request_keys=audit_non_hmac_request_keys,
            audit_non_hmac_response_keys=audit_non_hmac_response_keys,
            default_lease_ttl_seconds=default_lease_ttl_seconds,
            default_tls_client_key_bits=default_tls_client_key_bits,
            default_tls_client_key_type=default_tls_client_key_type,
            default_tls_client_ttl=default_tls_client_ttl,
            delegated_auth_accessors=delegated_auth_accessors,
            description=description,
            disable_remount=disable_remount,
            external_entropy_access=external_entropy_access,
            force_no_cache=force_no_cache,
            id=id,
            identity_token_key=identity_token_key,
            listen_addrs=listen_addrs,
            listing_visibility=listing_visibility,
            local=local,
            max_lease_ttl_seconds=max_lease_ttl_seconds,
            namespace=namespace,
            options=options,
            passthrough_request_headers=passthrough_request_headers,
            plugin_version=plugin_version,
            seal_wrap=seal_wrap,
            server_hostnames=server_hostnames,
            server_ips=server_ips,
            tls_ca_key_bits=tls_ca_key_bits,
            tls_ca_key_type=tls_ca_key_type,
            tls_min_version=tls_min_version,
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
        '''Generates CDKTF code for importing a KmipSecretBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KmipSecretBackend to import.
        :param import_from_id: The id of the existing KmipSecretBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KmipSecretBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2be6d29abb3c5fdbb99d17ceeae9a3665321d75a62f7ac7b62b30767fa989cb4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedManagedKeys")
    def reset_allowed_managed_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedManagedKeys", []))

    @jsii.member(jsii_name="resetAllowedResponseHeaders")
    def reset_allowed_response_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedResponseHeaders", []))

    @jsii.member(jsii_name="resetAuditNonHmacRequestKeys")
    def reset_audit_non_hmac_request_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditNonHmacRequestKeys", []))

    @jsii.member(jsii_name="resetAuditNonHmacResponseKeys")
    def reset_audit_non_hmac_response_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditNonHmacResponseKeys", []))

    @jsii.member(jsii_name="resetDefaultLeaseTtlSeconds")
    def reset_default_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultLeaseTtlSeconds", []))

    @jsii.member(jsii_name="resetDefaultTlsClientKeyBits")
    def reset_default_tls_client_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTlsClientKeyBits", []))

    @jsii.member(jsii_name="resetDefaultTlsClientKeyType")
    def reset_default_tls_client_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTlsClientKeyType", []))

    @jsii.member(jsii_name="resetDefaultTlsClientTtl")
    def reset_default_tls_client_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTlsClientTtl", []))

    @jsii.member(jsii_name="resetDelegatedAuthAccessors")
    def reset_delegated_auth_accessors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelegatedAuthAccessors", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableRemount")
    def reset_disable_remount(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableRemount", []))

    @jsii.member(jsii_name="resetExternalEntropyAccess")
    def reset_external_entropy_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalEntropyAccess", []))

    @jsii.member(jsii_name="resetForceNoCache")
    def reset_force_no_cache(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceNoCache", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentityTokenKey")
    def reset_identity_token_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityTokenKey", []))

    @jsii.member(jsii_name="resetListenAddrs")
    def reset_listen_addrs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetListenAddrs", []))

    @jsii.member(jsii_name="resetListingVisibility")
    def reset_listing_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetListingVisibility", []))

    @jsii.member(jsii_name="resetLocal")
    def reset_local(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocal", []))

    @jsii.member(jsii_name="resetMaxLeaseTtlSeconds")
    def reset_max_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLeaseTtlSeconds", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="resetPassthroughRequestHeaders")
    def reset_passthrough_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassthroughRequestHeaders", []))

    @jsii.member(jsii_name="resetPluginVersion")
    def reset_plugin_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginVersion", []))

    @jsii.member(jsii_name="resetSealWrap")
    def reset_seal_wrap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSealWrap", []))

    @jsii.member(jsii_name="resetServerHostnames")
    def reset_server_hostnames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerHostnames", []))

    @jsii.member(jsii_name="resetServerIps")
    def reset_server_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerIps", []))

    @jsii.member(jsii_name="resetTlsCaKeyBits")
    def reset_tls_ca_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCaKeyBits", []))

    @jsii.member(jsii_name="resetTlsCaKeyType")
    def reset_tls_ca_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCaKeyType", []))

    @jsii.member(jsii_name="resetTlsMinVersion")
    def reset_tls_min_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsMinVersion", []))

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
    @jsii.member(jsii_name="allowedManagedKeysInput")
    def allowed_managed_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedManagedKeysInput"))

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
    @jsii.member(jsii_name="defaultLeaseTtlSecondsInput")
    def default_lease_ttl_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultLeaseTtlSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTlsClientKeyBitsInput")
    def default_tls_client_key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultTlsClientKeyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTlsClientKeyTypeInput")
    def default_tls_client_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultTlsClientKeyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTlsClientTtlInput")
    def default_tls_client_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultTlsClientTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="delegatedAuthAccessorsInput")
    def delegated_auth_accessors_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "delegatedAuthAccessorsInput"))

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
    @jsii.member(jsii_name="externalEntropyAccessInput")
    def external_entropy_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "externalEntropyAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="forceNoCacheInput")
    def force_no_cache_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceNoCacheInput"))

    @builtins.property
    @jsii.member(jsii_name="identityTokenKeyInput")
    def identity_token_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityTokenKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="listenAddrsInput")
    def listen_addrs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "listenAddrsInput"))

    @builtins.property
    @jsii.member(jsii_name="listingVisibilityInput")
    def listing_visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "listingVisibilityInput"))

    @builtins.property
    @jsii.member(jsii_name="localInput")
    def local_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "localInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSecondsInput")
    def max_lease_ttl_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLeaseTtlSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "optionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeadersInput")
    def passthrough_request_headers_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "passthroughRequestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="pluginVersionInput")
    def plugin_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="sealWrapInput")
    def seal_wrap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sealWrapInput"))

    @builtins.property
    @jsii.member(jsii_name="serverHostnamesInput")
    def server_hostnames_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serverHostnamesInput"))

    @builtins.property
    @jsii.member(jsii_name="serverIpsInput")
    def server_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serverIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaKeyBitsInput")
    def tls_ca_key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tlsCaKeyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaKeyTypeInput")
    def tls_ca_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCaKeyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsMinVersionInput")
    def tls_min_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsMinVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedManagedKeys")
    def allowed_managed_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedManagedKeys"))

    @allowed_managed_keys.setter
    def allowed_managed_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4241f906fc47f0364ec7d1c3641f6fbe4e396b0445c1eab1e65a2eede7b4f65c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedManagedKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeaders")
    def allowed_response_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedResponseHeaders"))

    @allowed_response_headers.setter
    def allowed_response_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff65aceda13bf257944ae0498e05793860b69b0af6fbef50b98bd149d2188988)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedResponseHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeys")
    def audit_non_hmac_request_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacRequestKeys"))

    @audit_non_hmac_request_keys.setter
    def audit_non_hmac_request_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53bae35dec58c4f3deeb9bdf238857014d192777ed5f4e978069e12367dffa73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacRequestKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeys")
    def audit_non_hmac_response_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacResponseKeys"))

    @audit_non_hmac_response_keys.setter
    def audit_non_hmac_response_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9ec8bf7b9799429c6f6d354202e2f5864f222fec2c0c081f49e2cb46ece030c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacResponseKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSeconds")
    def default_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLeaseTtlSeconds"))

    @default_lease_ttl_seconds.setter
    def default_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__694abed9aec8f8902ac9a03cfa9d68eab317afd8906feb5c50db0f307bcc075d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTlsClientKeyBits")
    def default_tls_client_key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultTlsClientKeyBits"))

    @default_tls_client_key_bits.setter
    def default_tls_client_key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dff036ec0e20f47ced6d93934d2695f57bb84ffe13dba2f77dd12a034c5e9575)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTlsClientKeyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTlsClientKeyType")
    def default_tls_client_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultTlsClientKeyType"))

    @default_tls_client_key_type.setter
    def default_tls_client_key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af475a60885b969dc7818778d02584a49ac8df3769cb397f08f05b958b198d03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTlsClientKeyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTlsClientTtl")
    def default_tls_client_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultTlsClientTtl"))

    @default_tls_client_ttl.setter
    def default_tls_client_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__592440d62d6abc4d0741e4f443374a8f978071dcfbc09c6e6ed216407b7ffedc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTlsClientTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegatedAuthAccessors")
    def delegated_auth_accessors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "delegatedAuthAccessors"))

    @delegated_auth_accessors.setter
    def delegated_auth_accessors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50ff39257596d6c16fe3349e121a0815d82b575134b03299b0b4869f5dcb710f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegatedAuthAccessors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1aad70a890ce92193a8d0dd82270135b005aa50d110ec911725cb1e2f9ce0a7c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__061f6428de2b6323d842ab63f4bf34032300720309654debdc8bbb1c8e14a330)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableRemount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalEntropyAccess")
    def external_entropy_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "externalEntropyAccess"))

    @external_entropy_access.setter
    def external_entropy_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7638c92cce2df6ccccdff6ac38be3ae73bf4d6c591c2ea19e5d5fc1a7e3756)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalEntropyAccess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="forceNoCache")
    def force_no_cache(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceNoCache"))

    @force_no_cache.setter
    def force_no_cache(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb54906b190af033fafd4f31322f37a9b2ff9cc1c6e578f76a99bb4ece8e0c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceNoCache", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c3e1e6638e19b4dd9087d975abc54dcae9ab350aec66cd781a17a7a741eee40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenKey")
    def identity_token_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityTokenKey"))

    @identity_token_key.setter
    def identity_token_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23cecf29ee60ecc0666504ec0b86a17d7310b408e84b9927707c71994ea9332b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listenAddrs")
    def listen_addrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "listenAddrs"))

    @listen_addrs.setter
    def listen_addrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f22684210561bbaca2855f6a2913b2d7332243b969520c8d909612b8338a4c2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "listenAddrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listingVisibility")
    def listing_visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listingVisibility"))

    @listing_visibility.setter
    def listing_visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f4aa2d48505eda367b01d28f3e503c9eab24ed7d35d3023ebf7f403988b3f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "listingVisibility", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__cddc35069f3b2ebb74931d2764fcf34c17e05355f523c3ccd78d40a315ec39f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77e1dc02cc891c8a86dc39acc15496742e947b4a52998c7c24ac90ce25d493f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7f4695c59a222065aae0f8ba8c17ec94234710390935f73fc527a143fa85e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85fd91cfc577ea2276d2d011f2d5af31c008d7f830ef1f2b2d8e1bde0dd015dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeaders")
    def passthrough_request_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passthroughRequestHeaders"))

    @passthrough_request_headers.setter
    def passthrough_request_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7f4b0955d428fd8e0a4dbefb885966fdce7a13212c668db321f5db09f64bd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passthroughRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04690898e76823e1a2645ff4bc73a3a3a4556cd41dbb60fe6e55602b6e07bf7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginVersion")
    def plugin_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginVersion"))

    @plugin_version.setter
    def plugin_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca5fad19b42f80b6480089191c4afe879e3a7f87a490deafdeb73021ba9399bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sealWrap")
    def seal_wrap(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sealWrap"))

    @seal_wrap.setter
    def seal_wrap(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a79a965c8f87f95211c7b04a11077e156302897feb1d7c108660094402d22067)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sealWrap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverHostnames")
    def server_hostnames(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "serverHostnames"))

    @server_hostnames.setter
    def server_hostnames(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efcb587161a3888d3997c532570e424b364c2086a4480280111d2b82ce6bbec6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverHostnames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverIps")
    def server_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "serverIps"))

    @server_ips.setter
    def server_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f167cb974e7b56937e43212d06c98cd1de0821e56110ab45b7293e4a4caf42e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverIps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCaKeyBits")
    def tls_ca_key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tlsCaKeyBits"))

    @tls_ca_key_bits.setter
    def tls_ca_key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bf82afbd0f3e999b9880afda66f157a57517c73fa9fef397ea675b34f428096)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCaKeyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCaKeyType")
    def tls_ca_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCaKeyType"))

    @tls_ca_key_type.setter
    def tls_ca_key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__218ea8dde21b19b2e69337e4e68e63e6d893113a43604b7d79bd4d0a71b81fad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCaKeyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsMinVersion")
    def tls_min_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsMinVersion"))

    @tls_min_version.setter
    def tls_min_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__679c4c97a02ed58c9dda44f60a57e4ece99e827e7882728d694f235aa53efdac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsMinVersion", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.kmipSecretBackend.KmipSecretBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "path": "path",
        "allowed_managed_keys": "allowedManagedKeys",
        "allowed_response_headers": "allowedResponseHeaders",
        "audit_non_hmac_request_keys": "auditNonHmacRequestKeys",
        "audit_non_hmac_response_keys": "auditNonHmacResponseKeys",
        "default_lease_ttl_seconds": "defaultLeaseTtlSeconds",
        "default_tls_client_key_bits": "defaultTlsClientKeyBits",
        "default_tls_client_key_type": "defaultTlsClientKeyType",
        "default_tls_client_ttl": "defaultTlsClientTtl",
        "delegated_auth_accessors": "delegatedAuthAccessors",
        "description": "description",
        "disable_remount": "disableRemount",
        "external_entropy_access": "externalEntropyAccess",
        "force_no_cache": "forceNoCache",
        "id": "id",
        "identity_token_key": "identityTokenKey",
        "listen_addrs": "listenAddrs",
        "listing_visibility": "listingVisibility",
        "local": "local",
        "max_lease_ttl_seconds": "maxLeaseTtlSeconds",
        "namespace": "namespace",
        "options": "options",
        "passthrough_request_headers": "passthroughRequestHeaders",
        "plugin_version": "pluginVersion",
        "seal_wrap": "sealWrap",
        "server_hostnames": "serverHostnames",
        "server_ips": "serverIps",
        "tls_ca_key_bits": "tlsCaKeyBits",
        "tls_ca_key_type": "tlsCaKeyType",
        "tls_min_version": "tlsMinVersion",
    },
)
class KmipSecretBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        path: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        default_tls_client_key_bits: typing.Optional[jsii.Number] = None,
        default_tls_client_key_type: typing.Optional[builtins.str] = None,
        default_tls_client_ttl: typing.Optional[jsii.Number] = None,
        delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_key: typing.Optional[builtins.str] = None,
        listen_addrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        server_hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
        server_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_ca_key_bits: typing.Optional[jsii.Number] = None,
        tls_ca_key_type: typing.Optional[builtins.str] = None,
        tls_min_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param path: Path where KMIP secret backend will be mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#path KmipSecretBackend#path}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#allowed_managed_keys KmipSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#allowed_response_headers KmipSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#audit_non_hmac_request_keys KmipSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#audit_non_hmac_response_keys KmipSecretBackend#audit_non_hmac_response_keys}
        :param default_lease_ttl_seconds: Default lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_lease_ttl_seconds KmipSecretBackend#default_lease_ttl_seconds}
        :param default_tls_client_key_bits: Client certificate key bits, valid values depend on key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_key_bits KmipSecretBackend#default_tls_client_key_bits}
        :param default_tls_client_key_type: Client certificate key type, rsa or ec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_key_type KmipSecretBackend#default_tls_client_key_type}
        :param default_tls_client_ttl: Client certificate TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_ttl KmipSecretBackend#default_tls_client_ttl}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#delegated_auth_accessors KmipSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#description KmipSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#disable_remount KmipSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#external_entropy_access KmipSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#force_no_cache KmipSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#id KmipSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#identity_token_key KmipSecretBackend#identity_token_key}
        :param listen_addrs: Addresses the KMIP server should listen on (host:port). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#listen_addrs KmipSecretBackend#listen_addrs}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#listing_visibility KmipSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#local KmipSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#max_lease_ttl_seconds KmipSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#namespace KmipSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#options KmipSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#passthrough_request_headers KmipSecretBackend#passthrough_request_headers}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#plugin_version KmipSecretBackend#plugin_version}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#seal_wrap KmipSecretBackend#seal_wrap}
        :param server_hostnames: Hostnames to include in the server's TLS certificate as SAN DNS names. The first will be used as the common name (CN) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#server_hostnames KmipSecretBackend#server_hostnames}
        :param server_ips: IPs to include in the server's TLS certificate as SAN IP addresses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#server_ips KmipSecretBackend#server_ips}
        :param tls_ca_key_bits: CA key bits, valid values depend on key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_ca_key_bits KmipSecretBackend#tls_ca_key_bits}
        :param tls_ca_key_type: CA key type, rsa or ec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_ca_key_type KmipSecretBackend#tls_ca_key_type}
        :param tls_min_version: Minimum TLS version to accept. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_min_version KmipSecretBackend#tls_min_version}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2661d7f66687c235e6528187932cf3e5adda35eee7fafa4f220c49762126919)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument allowed_managed_keys", value=allowed_managed_keys, expected_type=type_hints["allowed_managed_keys"])
            check_type(argname="argument allowed_response_headers", value=allowed_response_headers, expected_type=type_hints["allowed_response_headers"])
            check_type(argname="argument audit_non_hmac_request_keys", value=audit_non_hmac_request_keys, expected_type=type_hints["audit_non_hmac_request_keys"])
            check_type(argname="argument audit_non_hmac_response_keys", value=audit_non_hmac_response_keys, expected_type=type_hints["audit_non_hmac_response_keys"])
            check_type(argname="argument default_lease_ttl_seconds", value=default_lease_ttl_seconds, expected_type=type_hints["default_lease_ttl_seconds"])
            check_type(argname="argument default_tls_client_key_bits", value=default_tls_client_key_bits, expected_type=type_hints["default_tls_client_key_bits"])
            check_type(argname="argument default_tls_client_key_type", value=default_tls_client_key_type, expected_type=type_hints["default_tls_client_key_type"])
            check_type(argname="argument default_tls_client_ttl", value=default_tls_client_ttl, expected_type=type_hints["default_tls_client_ttl"])
            check_type(argname="argument delegated_auth_accessors", value=delegated_auth_accessors, expected_type=type_hints["delegated_auth_accessors"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_remount", value=disable_remount, expected_type=type_hints["disable_remount"])
            check_type(argname="argument external_entropy_access", value=external_entropy_access, expected_type=type_hints["external_entropy_access"])
            check_type(argname="argument force_no_cache", value=force_no_cache, expected_type=type_hints["force_no_cache"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_token_key", value=identity_token_key, expected_type=type_hints["identity_token_key"])
            check_type(argname="argument listen_addrs", value=listen_addrs, expected_type=type_hints["listen_addrs"])
            check_type(argname="argument listing_visibility", value=listing_visibility, expected_type=type_hints["listing_visibility"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument max_lease_ttl_seconds", value=max_lease_ttl_seconds, expected_type=type_hints["max_lease_ttl_seconds"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument passthrough_request_headers", value=passthrough_request_headers, expected_type=type_hints["passthrough_request_headers"])
            check_type(argname="argument plugin_version", value=plugin_version, expected_type=type_hints["plugin_version"])
            check_type(argname="argument seal_wrap", value=seal_wrap, expected_type=type_hints["seal_wrap"])
            check_type(argname="argument server_hostnames", value=server_hostnames, expected_type=type_hints["server_hostnames"])
            check_type(argname="argument server_ips", value=server_ips, expected_type=type_hints["server_ips"])
            check_type(argname="argument tls_ca_key_bits", value=tls_ca_key_bits, expected_type=type_hints["tls_ca_key_bits"])
            check_type(argname="argument tls_ca_key_type", value=tls_ca_key_type, expected_type=type_hints["tls_ca_key_type"])
            check_type(argname="argument tls_min_version", value=tls_min_version, expected_type=type_hints["tls_min_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
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
        if allowed_managed_keys is not None:
            self._values["allowed_managed_keys"] = allowed_managed_keys
        if allowed_response_headers is not None:
            self._values["allowed_response_headers"] = allowed_response_headers
        if audit_non_hmac_request_keys is not None:
            self._values["audit_non_hmac_request_keys"] = audit_non_hmac_request_keys
        if audit_non_hmac_response_keys is not None:
            self._values["audit_non_hmac_response_keys"] = audit_non_hmac_response_keys
        if default_lease_ttl_seconds is not None:
            self._values["default_lease_ttl_seconds"] = default_lease_ttl_seconds
        if default_tls_client_key_bits is not None:
            self._values["default_tls_client_key_bits"] = default_tls_client_key_bits
        if default_tls_client_key_type is not None:
            self._values["default_tls_client_key_type"] = default_tls_client_key_type
        if default_tls_client_ttl is not None:
            self._values["default_tls_client_ttl"] = default_tls_client_ttl
        if delegated_auth_accessors is not None:
            self._values["delegated_auth_accessors"] = delegated_auth_accessors
        if description is not None:
            self._values["description"] = description
        if disable_remount is not None:
            self._values["disable_remount"] = disable_remount
        if external_entropy_access is not None:
            self._values["external_entropy_access"] = external_entropy_access
        if force_no_cache is not None:
            self._values["force_no_cache"] = force_no_cache
        if id is not None:
            self._values["id"] = id
        if identity_token_key is not None:
            self._values["identity_token_key"] = identity_token_key
        if listen_addrs is not None:
            self._values["listen_addrs"] = listen_addrs
        if listing_visibility is not None:
            self._values["listing_visibility"] = listing_visibility
        if local is not None:
            self._values["local"] = local
        if max_lease_ttl_seconds is not None:
            self._values["max_lease_ttl_seconds"] = max_lease_ttl_seconds
        if namespace is not None:
            self._values["namespace"] = namespace
        if options is not None:
            self._values["options"] = options
        if passthrough_request_headers is not None:
            self._values["passthrough_request_headers"] = passthrough_request_headers
        if plugin_version is not None:
            self._values["plugin_version"] = plugin_version
        if seal_wrap is not None:
            self._values["seal_wrap"] = seal_wrap
        if server_hostnames is not None:
            self._values["server_hostnames"] = server_hostnames
        if server_ips is not None:
            self._values["server_ips"] = server_ips
        if tls_ca_key_bits is not None:
            self._values["tls_ca_key_bits"] = tls_ca_key_bits
        if tls_ca_key_type is not None:
            self._values["tls_ca_key_type"] = tls_ca_key_type
        if tls_min_version is not None:
            self._values["tls_min_version"] = tls_min_version

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
    def path(self) -> builtins.str:
        '''Path where KMIP secret backend will be mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#path KmipSecretBackend#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_managed_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of managed key registry entry names that the mount in question is allowed to access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#allowed_managed_keys KmipSecretBackend#allowed_managed_keys}
        '''
        result = self._values.get("allowed_managed_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_response_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#allowed_response_headers KmipSecretBackend#allowed_response_headers}
        '''
        result = self._values.get("allowed_response_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_request_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the request data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#audit_non_hmac_request_keys KmipSecretBackend#audit_non_hmac_request_keys}
        '''
        result = self._values.get("audit_non_hmac_request_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_response_keys(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the response data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#audit_non_hmac_response_keys KmipSecretBackend#audit_non_hmac_response_keys}
        '''
        result = self._values.get("audit_non_hmac_response_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Default lease duration for tokens and secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_lease_ttl_seconds KmipSecretBackend#default_lease_ttl_seconds}
        '''
        result = self._values.get("default_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_tls_client_key_bits(self) -> typing.Optional[jsii.Number]:
        '''Client certificate key bits, valid values depend on key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_key_bits KmipSecretBackend#default_tls_client_key_bits}
        '''
        result = self._values.get("default_tls_client_key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_tls_client_key_type(self) -> typing.Optional[builtins.str]:
        '''Client certificate key type, rsa or ec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_key_type KmipSecretBackend#default_tls_client_key_type}
        '''
        result = self._values.get("default_tls_client_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_tls_client_ttl(self) -> typing.Optional[jsii.Number]:
        '''Client certificate TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#default_tls_client_ttl KmipSecretBackend#default_tls_client_ttl}
        '''
        result = self._values.get("default_tls_client_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delegated_auth_accessors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#delegated_auth_accessors KmipSecretBackend#delegated_auth_accessors}
        '''
        result = self._values.get("delegated_auth_accessors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#description KmipSecretBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#disable_remount KmipSecretBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def external_entropy_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the secrets engine to access Vault's external entropy source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#external_entropy_access KmipSecretBackend#external_entropy_access}
        '''
        result = self._values.get("external_entropy_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def force_no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, disables caching.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#force_no_cache KmipSecretBackend#force_no_cache}
        '''
        result = self._values.get("force_no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#id KmipSecretBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_key(self) -> typing.Optional[builtins.str]:
        '''The key to use for signing plugin workload identity tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#identity_token_key KmipSecretBackend#identity_token_key}
        '''
        result = self._values.get("identity_token_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def listen_addrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Addresses the KMIP server should listen on (host:port).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#listen_addrs KmipSecretBackend#listen_addrs}
        '''
        result = self._values.get("listen_addrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def listing_visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies whether to show this mount in the UI-specific listing endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#listing_visibility KmipSecretBackend#listing_visibility}
        '''
        result = self._values.get("listing_visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Local mount flag that can be explicitly set to true to enforce local mount in HA environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#local KmipSecretBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum possible lease duration for tokens and secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#max_lease_ttl_seconds KmipSecretBackend#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#namespace KmipSecretBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies mount type specific options that are passed to the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#options KmipSecretBackend#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def passthrough_request_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#passthrough_request_headers KmipSecretBackend#passthrough_request_headers}
        '''
        result = self._values.get("passthrough_request_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def plugin_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#plugin_version KmipSecretBackend#plugin_version}
        '''
        result = self._values.get("plugin_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seal_wrap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#seal_wrap KmipSecretBackend#seal_wrap}
        '''
        result = self._values.get("seal_wrap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def server_hostnames(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Hostnames to include in the server's TLS certificate as SAN DNS names.

        The first will be used as the common name (CN)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#server_hostnames KmipSecretBackend#server_hostnames}
        '''
        result = self._values.get("server_hostnames")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def server_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IPs to include in the server's TLS certificate as SAN IP addresses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#server_ips KmipSecretBackend#server_ips}
        '''
        result = self._values.get("server_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tls_ca_key_bits(self) -> typing.Optional[jsii.Number]:
        '''CA key bits, valid values depend on key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_ca_key_bits KmipSecretBackend#tls_ca_key_bits}
        '''
        result = self._values.get("tls_ca_key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_ca_key_type(self) -> typing.Optional[builtins.str]:
        '''CA key type, rsa or ec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_ca_key_type KmipSecretBackend#tls_ca_key_type}
        '''
        result = self._values.get("tls_ca_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_min_version(self) -> typing.Optional[builtins.str]:
        '''Minimum TLS version to accept.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_backend#tls_min_version KmipSecretBackend#tls_min_version}
        '''
        result = self._values.get("tls_min_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KmipSecretBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KmipSecretBackend",
    "KmipSecretBackendConfig",
]

publication.publish()

def _typecheckingstub__d0f1cd19672cd534fbe2c663ed130e68e1e5d6c4c568f62919c3e110aa1cc1c1(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    path: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    default_tls_client_key_bits: typing.Optional[jsii.Number] = None,
    default_tls_client_key_type: typing.Optional[builtins.str] = None,
    default_tls_client_ttl: typing.Optional[jsii.Number] = None,
    delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_key: typing.Optional[builtins.str] = None,
    listen_addrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    server_hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
    server_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    tls_ca_key_bits: typing.Optional[jsii.Number] = None,
    tls_ca_key_type: typing.Optional[builtins.str] = None,
    tls_min_version: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__2be6d29abb3c5fdbb99d17ceeae9a3665321d75a62f7ac7b62b30767fa989cb4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4241f906fc47f0364ec7d1c3641f6fbe4e396b0445c1eab1e65a2eede7b4f65c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff65aceda13bf257944ae0498e05793860b69b0af6fbef50b98bd149d2188988(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53bae35dec58c4f3deeb9bdf238857014d192777ed5f4e978069e12367dffa73(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9ec8bf7b9799429c6f6d354202e2f5864f222fec2c0c081f49e2cb46ece030c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__694abed9aec8f8902ac9a03cfa9d68eab317afd8906feb5c50db0f307bcc075d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dff036ec0e20f47ced6d93934d2695f57bb84ffe13dba2f77dd12a034c5e9575(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af475a60885b969dc7818778d02584a49ac8df3769cb397f08f05b958b198d03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__592440d62d6abc4d0741e4f443374a8f978071dcfbc09c6e6ed216407b7ffedc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50ff39257596d6c16fe3349e121a0815d82b575134b03299b0b4869f5dcb710f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1aad70a890ce92193a8d0dd82270135b005aa50d110ec911725cb1e2f9ce0a7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__061f6428de2b6323d842ab63f4bf34032300720309654debdc8bbb1c8e14a330(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7638c92cce2df6ccccdff6ac38be3ae73bf4d6c591c2ea19e5d5fc1a7e3756(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb54906b190af033fafd4f31322f37a9b2ff9cc1c6e578f76a99bb4ece8e0c1c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c3e1e6638e19b4dd9087d975abc54dcae9ab350aec66cd781a17a7a741eee40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23cecf29ee60ecc0666504ec0b86a17d7310b408e84b9927707c71994ea9332b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f22684210561bbaca2855f6a2913b2d7332243b969520c8d909612b8338a4c2e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f4aa2d48505eda367b01d28f3e503c9eab24ed7d35d3023ebf7f403988b3f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cddc35069f3b2ebb74931d2764fcf34c17e05355f523c3ccd78d40a315ec39f6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77e1dc02cc891c8a86dc39acc15496742e947b4a52998c7c24ac90ce25d493f9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7f4695c59a222065aae0f8ba8c17ec94234710390935f73fc527a143fa85e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85fd91cfc577ea2276d2d011f2d5af31c008d7f830ef1f2b2d8e1bde0dd015dc(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7f4b0955d428fd8e0a4dbefb885966fdce7a13212c668db321f5db09f64bd9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04690898e76823e1a2645ff4bc73a3a3a4556cd41dbb60fe6e55602b6e07bf7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca5fad19b42f80b6480089191c4afe879e3a7f87a490deafdeb73021ba9399bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a79a965c8f87f95211c7b04a11077e156302897feb1d7c108660094402d22067(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efcb587161a3888d3997c532570e424b364c2086a4480280111d2b82ce6bbec6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f167cb974e7b56937e43212d06c98cd1de0821e56110ab45b7293e4a4caf42e9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bf82afbd0f3e999b9880afda66f157a57517c73fa9fef397ea675b34f428096(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__218ea8dde21b19b2e69337e4e68e63e6d893113a43604b7d79bd4d0a71b81fad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679c4c97a02ed58c9dda44f60a57e4ece99e827e7882728d694f235aa53efdac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2661d7f66687c235e6528187932cf3e5adda35eee7fafa4f220c49762126919(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    path: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    default_tls_client_key_bits: typing.Optional[jsii.Number] = None,
    default_tls_client_key_type: typing.Optional[builtins.str] = None,
    default_tls_client_ttl: typing.Optional[jsii.Number] = None,
    delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_key: typing.Optional[builtins.str] = None,
    listen_addrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    server_hostnames: typing.Optional[typing.Sequence[builtins.str]] = None,
    server_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    tls_ca_key_bits: typing.Optional[jsii.Number] = None,
    tls_ca_key_type: typing.Optional[builtins.str] = None,
    tls_min_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
