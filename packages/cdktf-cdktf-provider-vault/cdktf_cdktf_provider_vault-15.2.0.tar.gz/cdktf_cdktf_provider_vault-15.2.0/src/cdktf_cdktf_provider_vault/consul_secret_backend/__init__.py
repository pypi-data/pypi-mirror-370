r'''
# `vault_consul_secret_backend`

Refer to the Terraform Registry for docs: [`vault_consul_secret_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend).
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


class ConsulSecretBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.consulSecretBackend.ConsulSecretBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend vault_consul_secret_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        address: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ca_cert: typing.Optional[builtins.str] = None,
        client_cert: typing.Optional[builtins.str] = None,
        client_key: typing.Optional[builtins.str] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_key: typing.Optional[builtins.str] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        path: typing.Optional[builtins.str] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        scheme: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend vault_consul_secret_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address: Specifies the address of the Consul instance, provided as "host:port" like "127.0.0.1:8500". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#address ConsulSecretBackend#address}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#allowed_managed_keys ConsulSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#allowed_response_headers ConsulSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#audit_non_hmac_request_keys ConsulSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#audit_non_hmac_response_keys ConsulSecretBackend#audit_non_hmac_response_keys}
        :param bootstrap: Denotes a backend resource that is used to bootstrap the Consul ACL system. Only one resource may be used to bootstrap. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#bootstrap ConsulSecretBackend#bootstrap}
        :param ca_cert: CA certificate to use when verifying Consul server certificate, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#ca_cert ConsulSecretBackend#ca_cert}
        :param client_cert: Client certificate used for Consul's TLS communication, must be x509 PEM encoded and if this is set you need to also set client_key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#client_cert ConsulSecretBackend#client_cert}
        :param client_key: Client key used for Consul's TLS communication, must be x509 PEM encoded and if this is set you need to also set client_cert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#client_key ConsulSecretBackend#client_key}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#default_lease_ttl_seconds ConsulSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#delegated_auth_accessors ConsulSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#description ConsulSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#disable_remount ConsulSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#external_entropy_access ConsulSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#force_no_cache ConsulSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#id ConsulSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#identity_token_key ConsulSecretBackend#identity_token_key}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#listing_visibility ConsulSecretBackend#listing_visibility}
        :param local: Specifies if the secret backend is local only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#local ConsulSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#max_lease_ttl_seconds ConsulSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#namespace ConsulSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#options ConsulSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#passthrough_request_headers ConsulSecretBackend#passthrough_request_headers}
        :param path: Unique name of the Vault Consul mount to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#path ConsulSecretBackend#path}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#plugin_version ConsulSecretBackend#plugin_version}
        :param scheme: Specifies the URL scheme to use. Defaults to "http". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#scheme ConsulSecretBackend#scheme}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#seal_wrap ConsulSecretBackend#seal_wrap}
        :param token: Specifies the Consul token to use when managing or issuing new tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#token ConsulSecretBackend#token}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bffc533c52221f17e5cc370c949c189e7908d198f59e03a6106e3aa84d1e1e34)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConsulSecretBackendConfig(
            address=address,
            allowed_managed_keys=allowed_managed_keys,
            allowed_response_headers=allowed_response_headers,
            audit_non_hmac_request_keys=audit_non_hmac_request_keys,
            audit_non_hmac_response_keys=audit_non_hmac_response_keys,
            bootstrap=bootstrap,
            ca_cert=ca_cert,
            client_cert=client_cert,
            client_key=client_key,
            default_lease_ttl_seconds=default_lease_ttl_seconds,
            delegated_auth_accessors=delegated_auth_accessors,
            description=description,
            disable_remount=disable_remount,
            external_entropy_access=external_entropy_access,
            force_no_cache=force_no_cache,
            id=id,
            identity_token_key=identity_token_key,
            listing_visibility=listing_visibility,
            local=local,
            max_lease_ttl_seconds=max_lease_ttl_seconds,
            namespace=namespace,
            options=options,
            passthrough_request_headers=passthrough_request_headers,
            path=path,
            plugin_version=plugin_version,
            scheme=scheme,
            seal_wrap=seal_wrap,
            token=token,
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
        '''Generates CDKTF code for importing a ConsulSecretBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConsulSecretBackend to import.
        :param import_from_id: The id of the existing ConsulSecretBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConsulSecretBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04ef69a69ee61d8934a4929e3a54d6a5f872010db01d0d7140c412216e67b7c2)
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

    @jsii.member(jsii_name="resetBootstrap")
    def reset_bootstrap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootstrap", []))

    @jsii.member(jsii_name="resetCaCert")
    def reset_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCert", []))

    @jsii.member(jsii_name="resetClientCert")
    def reset_client_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientCert", []))

    @jsii.member(jsii_name="resetClientKey")
    def reset_client_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientKey", []))

    @jsii.member(jsii_name="resetDefaultLeaseTtlSeconds")
    def reset_default_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultLeaseTtlSeconds", []))

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

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetPluginVersion")
    def reset_plugin_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginVersion", []))

    @jsii.member(jsii_name="resetScheme")
    def reset_scheme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheme", []))

    @jsii.member(jsii_name="resetSealWrap")
    def reset_seal_wrap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSealWrap", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

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
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

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
    @jsii.member(jsii_name="bootstrapInput")
    def bootstrap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "bootstrapInput"))

    @builtins.property
    @jsii.member(jsii_name="caCertInput")
    def ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertInput"))

    @builtins.property
    @jsii.member(jsii_name="clientCertInput")
    def client_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientCertInput"))

    @builtins.property
    @jsii.member(jsii_name="clientKeyInput")
    def client_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSecondsInput")
    def default_lease_ttl_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultLeaseTtlSecondsInput"))

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
    @jsii.member(jsii_name="schemeInput")
    def scheme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemeInput"))

    @builtins.property
    @jsii.member(jsii_name="sealWrapInput")
    def seal_wrap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sealWrapInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236d1a0816262d493adb125e9de08e12946a614947e0b79a5bdf7089145757da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedManagedKeys")
    def allowed_managed_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedManagedKeys"))

    @allowed_managed_keys.setter
    def allowed_managed_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dbe9d542f68b0b6f4652dd1bc41d49b8cea6583aa928493418bdaa4aed5d3f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedManagedKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeaders")
    def allowed_response_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedResponseHeaders"))

    @allowed_response_headers.setter
    def allowed_response_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f56e6d94a5448195665cbac2249d6756515e924dac3d7b19cee13deaa0d2272a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedResponseHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeys")
    def audit_non_hmac_request_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacRequestKeys"))

    @audit_non_hmac_request_keys.setter
    def audit_non_hmac_request_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__446b216888db400371472aafd215f0164956e6e3a75d4ea26f556f251ff15a68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacRequestKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeys")
    def audit_non_hmac_response_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacResponseKeys"))

    @audit_non_hmac_response_keys.setter
    def audit_non_hmac_response_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90f60b984a5e9fdf33dd6147a221971420199bde9800777c15f968b20f78c3ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacResponseKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bootstrap")
    def bootstrap(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "bootstrap"))

    @bootstrap.setter
    def bootstrap(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2006bc9726aade910c8799c1d57c527c95276a07bc4a01dc184f1287ff12ea5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootstrap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caCert")
    def ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCert"))

    @ca_cert.setter
    def ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d5e57238a3ff0f796e51cc561e40de103ddfb2c90dc618d0e75740dc9eaa64a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientCert")
    def client_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientCert"))

    @client_cert.setter
    def client_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb5571cbaa515068089125f2ffd5bb47c06665a032a8b499536047941e21dbff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientKey")
    def client_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientKey"))

    @client_key.setter
    def client_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80bf06eedd1d1ac44fb68791577de8f44942c1763b2122c65d83b8dc89ec5130)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSeconds")
    def default_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLeaseTtlSeconds"))

    @default_lease_ttl_seconds.setter
    def default_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07db92eda8d69cff8fa1ac21e02a5e78c94aa61795b85f18e0715412e22a88cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegatedAuthAccessors")
    def delegated_auth_accessors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "delegatedAuthAccessors"))

    @delegated_auth_accessors.setter
    def delegated_auth_accessors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fdcc500932fba5d9efce541fd80245737faf8a3df69ce9ef868123f5859fc05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegatedAuthAccessors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90e9806569a4d979780ebf745f5bcfc162aeaf95eda73430b0fc12cb62371d7f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__59fccc15beaa6022a413051f86cd85a401aa28c33bef3c63fd5611278583c621)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c3d3087d511685c1fa7e751e8a14fd6e4ba47b040b3b848a7b1ca2c7cfc8f18)
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
            type_hints = typing.get_type_hints(_typecheckingstub__53b95633c403b53a8620f37141e57a2e5b27e40fd1ad7366057cbcca52327c30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceNoCache", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7996bd3fd35290e686631d4a4a76bf1f2df1e59743400a3ab3088acb689d00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenKey")
    def identity_token_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityTokenKey"))

    @identity_token_key.setter
    def identity_token_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0877a2fa729ca1fc6be78cb551f2a22d6d5b6685719c030850c544dd8b990ef2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listingVisibility")
    def listing_visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listingVisibility"))

    @listing_visibility.setter
    def listing_visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398b032d992620f2cf5c6b3ed06738c97a9fbec69aa9763cf672741a763ffce8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8b5a9351f7eb3cff5b542d8a37fe1912f51101a4b8aee454b285cf0954425af7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__636e88a0e1d00d0b50d20c31681e84be9bde8b6b4983f1b1ab0900f6007c5a80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b86d61254a25e63a9588338ed51510bfefb3090936fbe130272259d17c082941)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1eab3cf309c1bf1a6d8dc07b8fa3b5c9dc189713070db88aecf630a26389e98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeaders")
    def passthrough_request_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passthroughRequestHeaders"))

    @passthrough_request_headers.setter
    def passthrough_request_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37edc68cd93814d6b8004634aa9e0d6f538bfd4800b8cc797d85707860650f0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passthroughRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8275a33c12bf5cd49f0aa2262f351e09ce64d593df764f71b58ea922ebcc7e92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginVersion")
    def plugin_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginVersion"))

    @plugin_version.setter
    def plugin_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb28df3471d9cb6ec7f7cd8be68cff797dc08229eba525d7e1334b2b03743a1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scheme")
    def scheme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scheme"))

    @scheme.setter
    def scheme(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__377f549a9b3ff35fb3104e22ad98098e15fd0f446df0a0d4a06b1d2351d9e172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheme", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e620976f39304e618493a4b8db3c1156b4744376ed596624bef26e955424c2a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sealWrap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__866ea16e0c6d36f07d6e5b5cbbb7e097b6974da7cb941e6909ebd9807e978e81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.consulSecretBackend.ConsulSecretBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "address": "address",
        "allowed_managed_keys": "allowedManagedKeys",
        "allowed_response_headers": "allowedResponseHeaders",
        "audit_non_hmac_request_keys": "auditNonHmacRequestKeys",
        "audit_non_hmac_response_keys": "auditNonHmacResponseKeys",
        "bootstrap": "bootstrap",
        "ca_cert": "caCert",
        "client_cert": "clientCert",
        "client_key": "clientKey",
        "default_lease_ttl_seconds": "defaultLeaseTtlSeconds",
        "delegated_auth_accessors": "delegatedAuthAccessors",
        "description": "description",
        "disable_remount": "disableRemount",
        "external_entropy_access": "externalEntropyAccess",
        "force_no_cache": "forceNoCache",
        "id": "id",
        "identity_token_key": "identityTokenKey",
        "listing_visibility": "listingVisibility",
        "local": "local",
        "max_lease_ttl_seconds": "maxLeaseTtlSeconds",
        "namespace": "namespace",
        "options": "options",
        "passthrough_request_headers": "passthroughRequestHeaders",
        "path": "path",
        "plugin_version": "pluginVersion",
        "scheme": "scheme",
        "seal_wrap": "sealWrap",
        "token": "token",
    },
)
class ConsulSecretBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        address: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        bootstrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ca_cert: typing.Optional[builtins.str] = None,
        client_cert: typing.Optional[builtins.str] = None,
        client_key: typing.Optional[builtins.str] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_key: typing.Optional[builtins.str] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        path: typing.Optional[builtins.str] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        scheme: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param address: Specifies the address of the Consul instance, provided as "host:port" like "127.0.0.1:8500". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#address ConsulSecretBackend#address}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#allowed_managed_keys ConsulSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#allowed_response_headers ConsulSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#audit_non_hmac_request_keys ConsulSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#audit_non_hmac_response_keys ConsulSecretBackend#audit_non_hmac_response_keys}
        :param bootstrap: Denotes a backend resource that is used to bootstrap the Consul ACL system. Only one resource may be used to bootstrap. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#bootstrap ConsulSecretBackend#bootstrap}
        :param ca_cert: CA certificate to use when verifying Consul server certificate, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#ca_cert ConsulSecretBackend#ca_cert}
        :param client_cert: Client certificate used for Consul's TLS communication, must be x509 PEM encoded and if this is set you need to also set client_key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#client_cert ConsulSecretBackend#client_cert}
        :param client_key: Client key used for Consul's TLS communication, must be x509 PEM encoded and if this is set you need to also set client_cert. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#client_key ConsulSecretBackend#client_key}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#default_lease_ttl_seconds ConsulSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#delegated_auth_accessors ConsulSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#description ConsulSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#disable_remount ConsulSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#external_entropy_access ConsulSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#force_no_cache ConsulSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#id ConsulSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#identity_token_key ConsulSecretBackend#identity_token_key}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#listing_visibility ConsulSecretBackend#listing_visibility}
        :param local: Specifies if the secret backend is local only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#local ConsulSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#max_lease_ttl_seconds ConsulSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#namespace ConsulSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#options ConsulSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#passthrough_request_headers ConsulSecretBackend#passthrough_request_headers}
        :param path: Unique name of the Vault Consul mount to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#path ConsulSecretBackend#path}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#plugin_version ConsulSecretBackend#plugin_version}
        :param scheme: Specifies the URL scheme to use. Defaults to "http". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#scheme ConsulSecretBackend#scheme}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#seal_wrap ConsulSecretBackend#seal_wrap}
        :param token: Specifies the Consul token to use when managing or issuing new tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#token ConsulSecretBackend#token}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c12ca3a9a0612ec8a74980d12e4452f716b542426bbfc8ba51c53dbc67fa9a6)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument allowed_managed_keys", value=allowed_managed_keys, expected_type=type_hints["allowed_managed_keys"])
            check_type(argname="argument allowed_response_headers", value=allowed_response_headers, expected_type=type_hints["allowed_response_headers"])
            check_type(argname="argument audit_non_hmac_request_keys", value=audit_non_hmac_request_keys, expected_type=type_hints["audit_non_hmac_request_keys"])
            check_type(argname="argument audit_non_hmac_response_keys", value=audit_non_hmac_response_keys, expected_type=type_hints["audit_non_hmac_response_keys"])
            check_type(argname="argument bootstrap", value=bootstrap, expected_type=type_hints["bootstrap"])
            check_type(argname="argument ca_cert", value=ca_cert, expected_type=type_hints["ca_cert"])
            check_type(argname="argument client_cert", value=client_cert, expected_type=type_hints["client_cert"])
            check_type(argname="argument client_key", value=client_key, expected_type=type_hints["client_key"])
            check_type(argname="argument default_lease_ttl_seconds", value=default_lease_ttl_seconds, expected_type=type_hints["default_lease_ttl_seconds"])
            check_type(argname="argument delegated_auth_accessors", value=delegated_auth_accessors, expected_type=type_hints["delegated_auth_accessors"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_remount", value=disable_remount, expected_type=type_hints["disable_remount"])
            check_type(argname="argument external_entropy_access", value=external_entropy_access, expected_type=type_hints["external_entropy_access"])
            check_type(argname="argument force_no_cache", value=force_no_cache, expected_type=type_hints["force_no_cache"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_token_key", value=identity_token_key, expected_type=type_hints["identity_token_key"])
            check_type(argname="argument listing_visibility", value=listing_visibility, expected_type=type_hints["listing_visibility"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument max_lease_ttl_seconds", value=max_lease_ttl_seconds, expected_type=type_hints["max_lease_ttl_seconds"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument passthrough_request_headers", value=passthrough_request_headers, expected_type=type_hints["passthrough_request_headers"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument plugin_version", value=plugin_version, expected_type=type_hints["plugin_version"])
            check_type(argname="argument scheme", value=scheme, expected_type=type_hints["scheme"])
            check_type(argname="argument seal_wrap", value=seal_wrap, expected_type=type_hints["seal_wrap"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
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
        if bootstrap is not None:
            self._values["bootstrap"] = bootstrap
        if ca_cert is not None:
            self._values["ca_cert"] = ca_cert
        if client_cert is not None:
            self._values["client_cert"] = client_cert
        if client_key is not None:
            self._values["client_key"] = client_key
        if default_lease_ttl_seconds is not None:
            self._values["default_lease_ttl_seconds"] = default_lease_ttl_seconds
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
        if path is not None:
            self._values["path"] = path
        if plugin_version is not None:
            self._values["plugin_version"] = plugin_version
        if scheme is not None:
            self._values["scheme"] = scheme
        if seal_wrap is not None:
            self._values["seal_wrap"] = seal_wrap
        if token is not None:
            self._values["token"] = token

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
    def address(self) -> builtins.str:
        '''Specifies the address of the Consul instance, provided as "host:port" like "127.0.0.1:8500".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#address ConsulSecretBackend#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_managed_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of managed key registry entry names that the mount in question is allowed to access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#allowed_managed_keys ConsulSecretBackend#allowed_managed_keys}
        '''
        result = self._values.get("allowed_managed_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_response_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#allowed_response_headers ConsulSecretBackend#allowed_response_headers}
        '''
        result = self._values.get("allowed_response_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_request_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the request data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#audit_non_hmac_request_keys ConsulSecretBackend#audit_non_hmac_request_keys}
        '''
        result = self._values.get("audit_non_hmac_request_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_response_keys(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the response data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#audit_non_hmac_response_keys ConsulSecretBackend#audit_non_hmac_response_keys}
        '''
        result = self._values.get("audit_non_hmac_response_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bootstrap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Denotes a backend resource that is used to bootstrap the Consul ACL system.

        Only one resource may be used to bootstrap.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#bootstrap ConsulSecretBackend#bootstrap}
        '''
        result = self._values.get("bootstrap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ca_cert(self) -> typing.Optional[builtins.str]:
        '''CA certificate to use when verifying Consul server certificate, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#ca_cert ConsulSecretBackend#ca_cert}
        '''
        result = self._values.get("ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_cert(self) -> typing.Optional[builtins.str]:
        '''Client certificate used for Consul's TLS communication, must be x509 PEM encoded and if this is set you need to also set client_key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#client_cert ConsulSecretBackend#client_cert}
        '''
        result = self._values.get("client_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_key(self) -> typing.Optional[builtins.str]:
        '''Client key used for Consul's TLS communication, must be x509 PEM encoded and if this is set you need to also set client_cert.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#client_key ConsulSecretBackend#client_key}
        '''
        result = self._values.get("client_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Default lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#default_lease_ttl_seconds ConsulSecretBackend#default_lease_ttl_seconds}
        '''
        result = self._values.get("default_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delegated_auth_accessors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#delegated_auth_accessors ConsulSecretBackend#delegated_auth_accessors}
        '''
        result = self._values.get("delegated_auth_accessors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#description ConsulSecretBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#disable_remount ConsulSecretBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def external_entropy_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the secrets engine to access Vault's external entropy source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#external_entropy_access ConsulSecretBackend#external_entropy_access}
        '''
        result = self._values.get("external_entropy_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def force_no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, disables caching.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#force_no_cache ConsulSecretBackend#force_no_cache}
        '''
        result = self._values.get("force_no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#id ConsulSecretBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_key(self) -> typing.Optional[builtins.str]:
        '''The key to use for signing plugin workload identity tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#identity_token_key ConsulSecretBackend#identity_token_key}
        '''
        result = self._values.get("identity_token_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def listing_visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies whether to show this mount in the UI-specific listing endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#listing_visibility ConsulSecretBackend#listing_visibility}
        '''
        result = self._values.get("listing_visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if the secret backend is local only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#local ConsulSecretBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum possible lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#max_lease_ttl_seconds ConsulSecretBackend#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#namespace ConsulSecretBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies mount type specific options that are passed to the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#options ConsulSecretBackend#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def passthrough_request_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#passthrough_request_headers ConsulSecretBackend#passthrough_request_headers}
        '''
        result = self._values.get("passthrough_request_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Unique name of the Vault Consul mount to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#path ConsulSecretBackend#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugin_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#plugin_version ConsulSecretBackend#plugin_version}
        '''
        result = self._values.get("plugin_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheme(self) -> typing.Optional[builtins.str]:
        '''Specifies the URL scheme to use. Defaults to "http".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#scheme ConsulSecretBackend#scheme}
        '''
        result = self._values.get("scheme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seal_wrap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#seal_wrap ConsulSecretBackend#seal_wrap}
        '''
        result = self._values.get("seal_wrap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Specifies the Consul token to use when managing or issuing new tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend#token ConsulSecretBackend#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConsulSecretBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ConsulSecretBackend",
    "ConsulSecretBackendConfig",
]

publication.publish()

def _typecheckingstub__bffc533c52221f17e5cc370c949c189e7908d198f59e03a6106e3aa84d1e1e34(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    address: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ca_cert: typing.Optional[builtins.str] = None,
    client_cert: typing.Optional[builtins.str] = None,
    client_key: typing.Optional[builtins.str] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_key: typing.Optional[builtins.str] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    path: typing.Optional[builtins.str] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    scheme: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__04ef69a69ee61d8934a4929e3a54d6a5f872010db01d0d7140c412216e67b7c2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__236d1a0816262d493adb125e9de08e12946a614947e0b79a5bdf7089145757da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dbe9d542f68b0b6f4652dd1bc41d49b8cea6583aa928493418bdaa4aed5d3f7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f56e6d94a5448195665cbac2249d6756515e924dac3d7b19cee13deaa0d2272a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__446b216888db400371472aafd215f0164956e6e3a75d4ea26f556f251ff15a68(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90f60b984a5e9fdf33dd6147a221971420199bde9800777c15f968b20f78c3ec(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2006bc9726aade910c8799c1d57c527c95276a07bc4a01dc184f1287ff12ea5b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d5e57238a3ff0f796e51cc561e40de103ddfb2c90dc618d0e75740dc9eaa64a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb5571cbaa515068089125f2ffd5bb47c06665a032a8b499536047941e21dbff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80bf06eedd1d1ac44fb68791577de8f44942c1763b2122c65d83b8dc89ec5130(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07db92eda8d69cff8fa1ac21e02a5e78c94aa61795b85f18e0715412e22a88cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fdcc500932fba5d9efce541fd80245737faf8a3df69ce9ef868123f5859fc05(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90e9806569a4d979780ebf745f5bcfc162aeaf95eda73430b0fc12cb62371d7f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59fccc15beaa6022a413051f86cd85a401aa28c33bef3c63fd5611278583c621(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c3d3087d511685c1fa7e751e8a14fd6e4ba47b040b3b848a7b1ca2c7cfc8f18(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53b95633c403b53a8620f37141e57a2e5b27e40fd1ad7366057cbcca52327c30(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7996bd3fd35290e686631d4a4a76bf1f2df1e59743400a3ab3088acb689d00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0877a2fa729ca1fc6be78cb551f2a22d6d5b6685719c030850c544dd8b990ef2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398b032d992620f2cf5c6b3ed06738c97a9fbec69aa9763cf672741a763ffce8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b5a9351f7eb3cff5b542d8a37fe1912f51101a4b8aee454b285cf0954425af7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__636e88a0e1d00d0b50d20c31681e84be9bde8b6b4983f1b1ab0900f6007c5a80(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b86d61254a25e63a9588338ed51510bfefb3090936fbe130272259d17c082941(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1eab3cf309c1bf1a6d8dc07b8fa3b5c9dc189713070db88aecf630a26389e98(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37edc68cd93814d6b8004634aa9e0d6f538bfd4800b8cc797d85707860650f0f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8275a33c12bf5cd49f0aa2262f351e09ce64d593df764f71b58ea922ebcc7e92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb28df3471d9cb6ec7f7cd8be68cff797dc08229eba525d7e1334b2b03743a1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__377f549a9b3ff35fb3104e22ad98098e15fd0f446df0a0d4a06b1d2351d9e172(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e620976f39304e618493a4b8db3c1156b4744376ed596624bef26e955424c2a3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__866ea16e0c6d36f07d6e5b5cbbb7e097b6974da7cb941e6909ebd9807e978e81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c12ca3a9a0612ec8a74980d12e4452f716b542426bbfc8ba51c53dbc67fa9a6(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    address: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    bootstrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ca_cert: typing.Optional[builtins.str] = None,
    client_cert: typing.Optional[builtins.str] = None,
    client_key: typing.Optional[builtins.str] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_key: typing.Optional[builtins.str] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    path: typing.Optional[builtins.str] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    scheme: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
