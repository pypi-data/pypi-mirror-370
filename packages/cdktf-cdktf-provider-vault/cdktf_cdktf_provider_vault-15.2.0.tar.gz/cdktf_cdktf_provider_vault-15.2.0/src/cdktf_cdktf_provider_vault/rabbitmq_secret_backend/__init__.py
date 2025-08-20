r'''
# `vault_rabbitmq_secret_backend`

Refer to the Terraform Registry for docs: [`vault_rabbitmq_secret_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend).
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


class RabbitmqSecretBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackend.RabbitmqSecretBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend vault_rabbitmq_secret_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        connection_uri: builtins.str,
        password: builtins.str,
        username: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        password_policy: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username_template: typing.Optional[builtins.str] = None,
        verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend vault_rabbitmq_secret_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection_uri: Specifies the RabbitMQ connection URI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#connection_uri RabbitmqSecretBackend#connection_uri}
        :param password: Specifies the RabbitMQ management administrator password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#password RabbitmqSecretBackend#password}
        :param username: Specifies the RabbitMQ management administrator username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#username RabbitmqSecretBackend#username}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#allowed_managed_keys RabbitmqSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#allowed_response_headers RabbitmqSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#audit_non_hmac_request_keys RabbitmqSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#audit_non_hmac_response_keys RabbitmqSecretBackend#audit_non_hmac_response_keys}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#default_lease_ttl_seconds RabbitmqSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#delegated_auth_accessors RabbitmqSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#description RabbitmqSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#disable_remount RabbitmqSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#external_entropy_access RabbitmqSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#force_no_cache RabbitmqSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#id RabbitmqSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#identity_token_key RabbitmqSecretBackend#identity_token_key}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#listing_visibility RabbitmqSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#local RabbitmqSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#max_lease_ttl_seconds RabbitmqSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#namespace RabbitmqSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#options RabbitmqSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#passthrough_request_headers RabbitmqSecretBackend#passthrough_request_headers}
        :param password_policy: Specifies a password policy to use when creating dynamic credentials. Defaults to generating an alphanumeric password if not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#password_policy RabbitmqSecretBackend#password_policy}
        :param path: The path of the RabbitMQ Secret Backend where the connection should be configured. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#path RabbitmqSecretBackend#path}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#plugin_version RabbitmqSecretBackend#plugin_version}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#seal_wrap RabbitmqSecretBackend#seal_wrap}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#username_template RabbitmqSecretBackend#username_template}
        :param verify_connection: Specifies whether to verify connection URI, username, and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#verify_connection RabbitmqSecretBackend#verify_connection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7694b35845630769ef012c18bda42f5bf2c62149c50fc23ad49a765eb09a7c54)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RabbitmqSecretBackendConfig(
            connection_uri=connection_uri,
            password=password,
            username=username,
            allowed_managed_keys=allowed_managed_keys,
            allowed_response_headers=allowed_response_headers,
            audit_non_hmac_request_keys=audit_non_hmac_request_keys,
            audit_non_hmac_response_keys=audit_non_hmac_response_keys,
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
            password_policy=password_policy,
            path=path,
            plugin_version=plugin_version,
            seal_wrap=seal_wrap,
            username_template=username_template,
            verify_connection=verify_connection,
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
        '''Generates CDKTF code for importing a RabbitmqSecretBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RabbitmqSecretBackend to import.
        :param import_from_id: The id of the existing RabbitmqSecretBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RabbitmqSecretBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__362bbcf89360e02864264feb73fbe0d1df89ddae26f0a281ef1a9d23a77df95e)
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

    @jsii.member(jsii_name="resetPasswordPolicy")
    def reset_password_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordPolicy", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetPluginVersion")
    def reset_plugin_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginVersion", []))

    @jsii.member(jsii_name="resetSealWrap")
    def reset_seal_wrap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSealWrap", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @jsii.member(jsii_name="resetVerifyConnection")
    def reset_verify_connection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyConnection", []))

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
    @jsii.member(jsii_name="connectionUriInput")
    def connection_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUriInput"))

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
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordPolicyInput")
    def password_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordPolicyInput"))

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
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="verifyConnectionInput")
    def verify_connection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "verifyConnectionInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedManagedKeys")
    def allowed_managed_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedManagedKeys"))

    @allowed_managed_keys.setter
    def allowed_managed_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c15951118a25c5b8d4d4586716888c73adf489fc1a46d3eacf38d593e1b8d521)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedManagedKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeaders")
    def allowed_response_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedResponseHeaders"))

    @allowed_response_headers.setter
    def allowed_response_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5ee53b98eb4b90cce3460efe2792fcd4693644a8dcf3b3c93578a75fedc93e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedResponseHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeys")
    def audit_non_hmac_request_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacRequestKeys"))

    @audit_non_hmac_request_keys.setter
    def audit_non_hmac_request_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f426b08c6496e3bac72741eabb7bdd971ad6ad88ab54ce8ab0c2474ecd20bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacRequestKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeys")
    def audit_non_hmac_response_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacResponseKeys"))

    @audit_non_hmac_response_keys.setter
    def audit_non_hmac_response_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b20832b10724c2fe5de92b093f1275dd0a15b64e0a8d4c455b02fec4e7376a6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacResponseKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionUri")
    def connection_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUri"))

    @connection_uri.setter
    def connection_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__811b329ff91ecc45d839771a1ddd3408752c7586ed320d27327f6158925b5407)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSeconds")
    def default_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLeaseTtlSeconds"))

    @default_lease_ttl_seconds.setter
    def default_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cadbf8ab530d69a3e80747a487896632a8ed804252344d2b5f4a3c9721febd4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegatedAuthAccessors")
    def delegated_auth_accessors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "delegatedAuthAccessors"))

    @delegated_auth_accessors.setter
    def delegated_auth_accessors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6540ae1ea0a359e0ec95847f7ea58d691f300af4022e1528705a04d5edb3a8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegatedAuthAccessors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62f5e77a2f4d730c01bf988dd14623887386031ba822fafa621fa65fc6f6f74d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffe966fb6b555110762cae11788134f50051fb4a433df9e1f114f635945df1d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ef362cd8a0fcfed39fb2d41a1157d6ed0dabad354745e1b469412794b12da88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cec6e9167f410dfe375bb0163ec4a1c6818752a60a132422d30337170352f0cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceNoCache", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e024c513b6b309449fa7058340f6db6c13051820151bc2a55ca7f9c2fd4606a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenKey")
    def identity_token_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityTokenKey"))

    @identity_token_key.setter
    def identity_token_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ab4262e4df1e08922ba900b30c7398e63d549a8c259a1047350cccc229bbd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listingVisibility")
    def listing_visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listingVisibility"))

    @listing_visibility.setter
    def listing_visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f618e072834f3575ae5acc8e6ad2f2ac6a616b54c46499eb5eb5e0acedfb9e95)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9e14dede2c27926259c7359d19a1ab402b8271ff0dc70d98c7dddd93a7cff84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c727114329c2a9a58e420213b1067d90623988ec81a49a21510af47d3e70c7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c94d0327da801d41c5232d0d1d6bd50345d2106f740b929dea81aad64d206aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92622f0a986ced39517378259d3e753fe0cb6edfd912ac01a7da012a394d4565)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeaders")
    def passthrough_request_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passthroughRequestHeaders"))

    @passthrough_request_headers.setter
    def passthrough_request_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c7afefeaeade9e77d579987b9f69250b927629c5d6482760d79db2305f33140)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passthroughRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1e0fda514e088215e0d8d864df2cb2f784875bbcbb7eb0d84f0b8bfc6452d30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordPolicy")
    def password_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordPolicy"))

    @password_policy.setter
    def password_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ae251f0bca49de7a050c85a4f382b2930eea1ac8450ca44fd53a98ffec7ce81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9cfcd273d3f4cc4722cd98788cc1f92590a3fefb947fbf6e8c7b843d4acfa8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginVersion")
    def plugin_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginVersion"))

    @plugin_version.setter
    def plugin_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754abe51139faa62b061c121032b19d60696ccd2f57888a2e2c4dff245336b7c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8fee6a450ed21a0e8632fddc33185941dbbef9d09251929eca6b374ad5b9c0d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sealWrap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bb884f2817c7707c05165b9cc3e530af9f4cf04a5448d3a910791dc8443f513)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4af7044d65aa3c1e4019277edab7c1fc101f318db4e9e5a11345993ab18f9c35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="verifyConnection")
    def verify_connection(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "verifyConnection"))

    @verify_connection.setter
    def verify_connection(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d1f2580b4f513368af66cd0c568c6bd6c555fa0044d4cdf27b09a696c7781b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verifyConnection", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackend.RabbitmqSecretBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "connection_uri": "connectionUri",
        "password": "password",
        "username": "username",
        "allowed_managed_keys": "allowedManagedKeys",
        "allowed_response_headers": "allowedResponseHeaders",
        "audit_non_hmac_request_keys": "auditNonHmacRequestKeys",
        "audit_non_hmac_response_keys": "auditNonHmacResponseKeys",
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
        "password_policy": "passwordPolicy",
        "path": "path",
        "plugin_version": "pluginVersion",
        "seal_wrap": "sealWrap",
        "username_template": "usernameTemplate",
        "verify_connection": "verifyConnection",
    },
)
class RabbitmqSecretBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        connection_uri: builtins.str,
        password: builtins.str,
        username: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        password_policy: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username_template: typing.Optional[builtins.str] = None,
        verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param connection_uri: Specifies the RabbitMQ connection URI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#connection_uri RabbitmqSecretBackend#connection_uri}
        :param password: Specifies the RabbitMQ management administrator password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#password RabbitmqSecretBackend#password}
        :param username: Specifies the RabbitMQ management administrator username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#username RabbitmqSecretBackend#username}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#allowed_managed_keys RabbitmqSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#allowed_response_headers RabbitmqSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#audit_non_hmac_request_keys RabbitmqSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#audit_non_hmac_response_keys RabbitmqSecretBackend#audit_non_hmac_response_keys}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#default_lease_ttl_seconds RabbitmqSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#delegated_auth_accessors RabbitmqSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#description RabbitmqSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#disable_remount RabbitmqSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#external_entropy_access RabbitmqSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#force_no_cache RabbitmqSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#id RabbitmqSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#identity_token_key RabbitmqSecretBackend#identity_token_key}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#listing_visibility RabbitmqSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#local RabbitmqSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#max_lease_ttl_seconds RabbitmqSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#namespace RabbitmqSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#options RabbitmqSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#passthrough_request_headers RabbitmqSecretBackend#passthrough_request_headers}
        :param password_policy: Specifies a password policy to use when creating dynamic credentials. Defaults to generating an alphanumeric password if not set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#password_policy RabbitmqSecretBackend#password_policy}
        :param path: The path of the RabbitMQ Secret Backend where the connection should be configured. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#path RabbitmqSecretBackend#path}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#plugin_version RabbitmqSecretBackend#plugin_version}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#seal_wrap RabbitmqSecretBackend#seal_wrap}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#username_template RabbitmqSecretBackend#username_template}
        :param verify_connection: Specifies whether to verify connection URI, username, and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#verify_connection RabbitmqSecretBackend#verify_connection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fbb87d707417ad5ec8dbb0d73e5ba0df02d3c02d6d1970fea268806192ed1d7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument connection_uri", value=connection_uri, expected_type=type_hints["connection_uri"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument allowed_managed_keys", value=allowed_managed_keys, expected_type=type_hints["allowed_managed_keys"])
            check_type(argname="argument allowed_response_headers", value=allowed_response_headers, expected_type=type_hints["allowed_response_headers"])
            check_type(argname="argument audit_non_hmac_request_keys", value=audit_non_hmac_request_keys, expected_type=type_hints["audit_non_hmac_request_keys"])
            check_type(argname="argument audit_non_hmac_response_keys", value=audit_non_hmac_response_keys, expected_type=type_hints["audit_non_hmac_response_keys"])
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
            check_type(argname="argument password_policy", value=password_policy, expected_type=type_hints["password_policy"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument plugin_version", value=plugin_version, expected_type=type_hints["plugin_version"])
            check_type(argname="argument seal_wrap", value=seal_wrap, expected_type=type_hints["seal_wrap"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
            check_type(argname="argument verify_connection", value=verify_connection, expected_type=type_hints["verify_connection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_uri": connection_uri,
            "password": password,
            "username": username,
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
        if password_policy is not None:
            self._values["password_policy"] = password_policy
        if path is not None:
            self._values["path"] = path
        if plugin_version is not None:
            self._values["plugin_version"] = plugin_version
        if seal_wrap is not None:
            self._values["seal_wrap"] = seal_wrap
        if username_template is not None:
            self._values["username_template"] = username_template
        if verify_connection is not None:
            self._values["verify_connection"] = verify_connection

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
    def connection_uri(self) -> builtins.str:
        '''Specifies the RabbitMQ connection URI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#connection_uri RabbitmqSecretBackend#connection_uri}
        '''
        result = self._values.get("connection_uri")
        assert result is not None, "Required property 'connection_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Specifies the RabbitMQ management administrator password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#password RabbitmqSecretBackend#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Specifies the RabbitMQ management administrator username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#username RabbitmqSecretBackend#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_managed_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of managed key registry entry names that the mount in question is allowed to access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#allowed_managed_keys RabbitmqSecretBackend#allowed_managed_keys}
        '''
        result = self._values.get("allowed_managed_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_response_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#allowed_response_headers RabbitmqSecretBackend#allowed_response_headers}
        '''
        result = self._values.get("allowed_response_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_request_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the request data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#audit_non_hmac_request_keys RabbitmqSecretBackend#audit_non_hmac_request_keys}
        '''
        result = self._values.get("audit_non_hmac_request_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_response_keys(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the response data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#audit_non_hmac_response_keys RabbitmqSecretBackend#audit_non_hmac_response_keys}
        '''
        result = self._values.get("audit_non_hmac_response_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Default lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#default_lease_ttl_seconds RabbitmqSecretBackend#default_lease_ttl_seconds}
        '''
        result = self._values.get("default_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delegated_auth_accessors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#delegated_auth_accessors RabbitmqSecretBackend#delegated_auth_accessors}
        '''
        result = self._values.get("delegated_auth_accessors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#description RabbitmqSecretBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#disable_remount RabbitmqSecretBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def external_entropy_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the secrets engine to access Vault's external entropy source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#external_entropy_access RabbitmqSecretBackend#external_entropy_access}
        '''
        result = self._values.get("external_entropy_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def force_no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, disables caching.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#force_no_cache RabbitmqSecretBackend#force_no_cache}
        '''
        result = self._values.get("force_no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#id RabbitmqSecretBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_key(self) -> typing.Optional[builtins.str]:
        '''The key to use for signing plugin workload identity tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#identity_token_key RabbitmqSecretBackend#identity_token_key}
        '''
        result = self._values.get("identity_token_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def listing_visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies whether to show this mount in the UI-specific listing endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#listing_visibility RabbitmqSecretBackend#listing_visibility}
        '''
        result = self._values.get("listing_visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Local mount flag that can be explicitly set to true to enforce local mount in HA environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#local RabbitmqSecretBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum possible lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#max_lease_ttl_seconds RabbitmqSecretBackend#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#namespace RabbitmqSecretBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies mount type specific options that are passed to the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#options RabbitmqSecretBackend#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def passthrough_request_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#passthrough_request_headers RabbitmqSecretBackend#passthrough_request_headers}
        '''
        result = self._values.get("passthrough_request_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def password_policy(self) -> typing.Optional[builtins.str]:
        '''Specifies a password policy to use when creating dynamic credentials. Defaults to generating an alphanumeric password if not set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#password_policy RabbitmqSecretBackend#password_policy}
        '''
        result = self._values.get("password_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path of the RabbitMQ Secret Backend where the connection should be configured.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#path RabbitmqSecretBackend#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugin_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#plugin_version RabbitmqSecretBackend#plugin_version}
        '''
        result = self._values.get("plugin_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seal_wrap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#seal_wrap RabbitmqSecretBackend#seal_wrap}
        '''
        result = self._values.get("seal_wrap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how dynamic usernames are generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#username_template RabbitmqSecretBackend#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_connection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to verify connection URI, username, and password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend#verify_connection RabbitmqSecretBackend#verify_connection}
        '''
        result = self._values.get("verify_connection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RabbitmqSecretBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RabbitmqSecretBackend",
    "RabbitmqSecretBackendConfig",
]

publication.publish()

def _typecheckingstub__7694b35845630769ef012c18bda42f5bf2c62149c50fc23ad49a765eb09a7c54(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    connection_uri: builtins.str,
    password: builtins.str,
    username: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
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
    password_policy: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username_template: typing.Optional[builtins.str] = None,
    verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__362bbcf89360e02864264feb73fbe0d1df89ddae26f0a281ef1a9d23a77df95e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c15951118a25c5b8d4d4586716888c73adf489fc1a46d3eacf38d593e1b8d521(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5ee53b98eb4b90cce3460efe2792fcd4693644a8dcf3b3c93578a75fedc93e3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f426b08c6496e3bac72741eabb7bdd971ad6ad88ab54ce8ab0c2474ecd20bd8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b20832b10724c2fe5de92b093f1275dd0a15b64e0a8d4c455b02fec4e7376a6f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__811b329ff91ecc45d839771a1ddd3408752c7586ed320d27327f6158925b5407(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cadbf8ab530d69a3e80747a487896632a8ed804252344d2b5f4a3c9721febd4c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6540ae1ea0a359e0ec95847f7ea58d691f300af4022e1528705a04d5edb3a8e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62f5e77a2f4d730c01bf988dd14623887386031ba822fafa621fa65fc6f6f74d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffe966fb6b555110762cae11788134f50051fb4a433df9e1f114f635945df1d7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ef362cd8a0fcfed39fb2d41a1157d6ed0dabad354745e1b469412794b12da88(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cec6e9167f410dfe375bb0163ec4a1c6818752a60a132422d30337170352f0cc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e024c513b6b309449fa7058340f6db6c13051820151bc2a55ca7f9c2fd4606a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ab4262e4df1e08922ba900b30c7398e63d549a8c259a1047350cccc229bbd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f618e072834f3575ae5acc8e6ad2f2ac6a616b54c46499eb5eb5e0acedfb9e95(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9e14dede2c27926259c7359d19a1ab402b8271ff0dc70d98c7dddd93a7cff84(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c727114329c2a9a58e420213b1067d90623988ec81a49a21510af47d3e70c7e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c94d0327da801d41c5232d0d1d6bd50345d2106f740b929dea81aad64d206aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92622f0a986ced39517378259d3e753fe0cb6edfd912ac01a7da012a394d4565(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c7afefeaeade9e77d579987b9f69250b927629c5d6482760d79db2305f33140(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1e0fda514e088215e0d8d864df2cb2f784875bbcbb7eb0d84f0b8bfc6452d30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ae251f0bca49de7a050c85a4f382b2930eea1ac8450ca44fd53a98ffec7ce81(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9cfcd273d3f4cc4722cd98788cc1f92590a3fefb947fbf6e8c7b843d4acfa8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754abe51139faa62b061c121032b19d60696ccd2f57888a2e2c4dff245336b7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fee6a450ed21a0e8632fddc33185941dbbef9d09251929eca6b374ad5b9c0d2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bb884f2817c7707c05165b9cc3e530af9f4cf04a5448d3a910791dc8443f513(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4af7044d65aa3c1e4019277edab7c1fc101f318db4e9e5a11345993ab18f9c35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d1f2580b4f513368af66cd0c568c6bd6c555fa0044d4cdf27b09a696c7781b1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fbb87d707417ad5ec8dbb0d73e5ba0df02d3c02d6d1970fea268806192ed1d7(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    connection_uri: builtins.str,
    password: builtins.str,
    username: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
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
    password_policy: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username_template: typing.Optional[builtins.str] = None,
    verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
