r'''
# `vault_terraform_cloud_secret_backend`

Refer to the Terraform Registry for docs: [`vault_terraform_cloud_secret_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend).
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


class TerraformCloudSecretBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.terraformCloudSecretBackend.TerraformCloudSecretBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend vault_terraform_cloud_secret_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        address: typing.Optional[builtins.str] = None,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        backend: typing.Optional[builtins.str] = None,
        base_path: typing.Optional[builtins.str] = None,
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
        plugin_version: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend vault_terraform_cloud_secret_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address: Specifies the address of the Terraform Cloud instance, provided as "host:port" like "127.0.0.1:8500". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#address TerraformCloudSecretBackend#address}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#allowed_managed_keys TerraformCloudSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#allowed_response_headers TerraformCloudSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#audit_non_hmac_request_keys TerraformCloudSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#audit_non_hmac_response_keys TerraformCloudSecretBackend#audit_non_hmac_response_keys}
        :param backend: Unique name of the Vault Terraform Cloud mount to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#backend TerraformCloudSecretBackend#backend}
        :param base_path: Specifies the base path for the Terraform Cloud or Enterprise API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#base_path TerraformCloudSecretBackend#base_path}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#default_lease_ttl_seconds TerraformCloudSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#delegated_auth_accessors TerraformCloudSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#description TerraformCloudSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#disable_remount TerraformCloudSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#external_entropy_access TerraformCloudSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#force_no_cache TerraformCloudSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#id TerraformCloudSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#identity_token_key TerraformCloudSecretBackend#identity_token_key}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#listing_visibility TerraformCloudSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#local TerraformCloudSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#max_lease_ttl_seconds TerraformCloudSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#namespace TerraformCloudSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#options TerraformCloudSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#passthrough_request_headers TerraformCloudSecretBackend#passthrough_request_headers}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#plugin_version TerraformCloudSecretBackend#plugin_version}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#seal_wrap TerraformCloudSecretBackend#seal_wrap}
        :param token: Specifies the Terraform Cloud access token to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#token TerraformCloudSecretBackend#token}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb670bb1f83988527548ff49a106effe5ff981293679ca808168c3595244ab5e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TerraformCloudSecretBackendConfig(
            address=address,
            allowed_managed_keys=allowed_managed_keys,
            allowed_response_headers=allowed_response_headers,
            audit_non_hmac_request_keys=audit_non_hmac_request_keys,
            audit_non_hmac_response_keys=audit_non_hmac_response_keys,
            backend=backend,
            base_path=base_path,
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
            plugin_version=plugin_version,
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
        '''Generates CDKTF code for importing a TerraformCloudSecretBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TerraformCloudSecretBackend to import.
        :param import_from_id: The id of the existing TerraformCloudSecretBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TerraformCloudSecretBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb0f2a72d52268d35608634bc64b82005da25ecce6f78804786d9de9c2f4f092)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAddress")
    def reset_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddress", []))

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

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetBasePath")
    def reset_base_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBasePath", []))

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

    @jsii.member(jsii_name="resetPluginVersion")
    def reset_plugin_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginVersion", []))

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
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="basePathInput")
    def base_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "basePathInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f70600bfa486e11e6537a71481f301ddd3f39acfc66dab182265b9716cef587c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedManagedKeys")
    def allowed_managed_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedManagedKeys"))

    @allowed_managed_keys.setter
    def allowed_managed_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dbec364644d5d3ce5d184c6503cc37d3c9b9b51010cf4dcb559c5477a705b31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedManagedKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeaders")
    def allowed_response_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedResponseHeaders"))

    @allowed_response_headers.setter
    def allowed_response_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0d5af28a9a652af588bd6e69ea347b0cbc23bb5d268ec6898d44f7da71281d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedResponseHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeys")
    def audit_non_hmac_request_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacRequestKeys"))

    @audit_non_hmac_request_keys.setter
    def audit_non_hmac_request_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c762736ee0bde802095063e9ddb18f9b17f27ada1c70bb22b775b84787bdae9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacRequestKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeys")
    def audit_non_hmac_response_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacResponseKeys"))

    @audit_non_hmac_response_keys.setter
    def audit_non_hmac_response_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fa0e5027a3b0a99afe3c076d0d05e9d0b1ffec1adbf748e3d4d5db2ce988e2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacResponseKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a747a5b09b773f055b70be3dc4c4e08d194860115cf746979e2f738c7f74b36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="basePath")
    def base_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "basePath"))

    @base_path.setter
    def base_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bc2e772123d6bf78f59792f496f2a7772eee8d01aa1d98976a18daf2d0d45bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "basePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSeconds")
    def default_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLeaseTtlSeconds"))

    @default_lease_ttl_seconds.setter
    def default_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e4e384b7efe69bdb1c11053f9aac4210561eaf6a622fdfbde0dd4c019ffb61c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegatedAuthAccessors")
    def delegated_auth_accessors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "delegatedAuthAccessors"))

    @delegated_auth_accessors.setter
    def delegated_auth_accessors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c30f86f03071d57219f6838bc40266cfaa8514ffe95ae1aa34ed073e3d6f1fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegatedAuthAccessors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbd4a0f5ef289d7126301db9f5d60745a4888af166e39951d809172a540a6a38)
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
            type_hints = typing.get_type_hints(_typecheckingstub__febbd61ce8bc62bfe1a6cc1c14977369ebfe25f51e3ad8c024bbf759c8ad9076)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dda273f3689a5b38a89c73c1ecafa47b6c244a26b7ca9f1e915ef1ce8a1203bb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__60da534fac7a4205fff27faefeb67bbba6cc1e64ef3d310d1c08a6ba6df8e4da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceNoCache", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__465a79de5fc1db0bb63cef3044c9b837a98ef513f382320a3e63e10c98930ea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenKey")
    def identity_token_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityTokenKey"))

    @identity_token_key.setter
    def identity_token_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb688bd0447261844c8fd58af82a90e89a03962ffb30d2886c5ec3ee9bc1ef4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listingVisibility")
    def listing_visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listingVisibility"))

    @listing_visibility.setter
    def listing_visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5028f850cffca8da3074a2ff75748ec2464705d087bfedc5002d40824c3d7dd4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__98ba1fcf6a955cf8aac4eb705afd39028d648f4a2bdc0f024eed932fd7248fb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ced2cf030956df58b4575c7fb7c6d0028693610ad2b2ade08965f19f5596458)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a012285f59e8f539cd75ed0615b27fd50f76a23f8f9faefeab0aab2f1d2c6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76b8f50bf099fefb5869f674e3e90a9067e0e52eacbf4d34af048baefa98ee2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeaders")
    def passthrough_request_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passthroughRequestHeaders"))

    @passthrough_request_headers.setter
    def passthrough_request_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2447a04d15cb65344336b8bbbff44068e0eaeca0325c9a97fa26b242409f8014)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passthroughRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginVersion")
    def plugin_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginVersion"))

    @plugin_version.setter
    def plugin_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4179e0dc11d5cb636a7408aa16ed229bd6033691b4b4000a20cb75dca9f41544)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6dff1f39ae9fd5758ed27495567cd2c0a5c745afb4a6e49fe2ed28a859607d8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sealWrap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @token.setter
    def token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12b266a38b9943cb4de23c68dc171b7e5d55db6d61a7711f88663b39c2f0aa88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.terraformCloudSecretBackend.TerraformCloudSecretBackendConfig",
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
        "backend": "backend",
        "base_path": "basePath",
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
        "plugin_version": "pluginVersion",
        "seal_wrap": "sealWrap",
        "token": "token",
    },
)
class TerraformCloudSecretBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        address: typing.Optional[builtins.str] = None,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        backend: typing.Optional[builtins.str] = None,
        base_path: typing.Optional[builtins.str] = None,
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
        plugin_version: typing.Optional[builtins.str] = None,
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
        :param address: Specifies the address of the Terraform Cloud instance, provided as "host:port" like "127.0.0.1:8500". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#address TerraformCloudSecretBackend#address}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#allowed_managed_keys TerraformCloudSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#allowed_response_headers TerraformCloudSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#audit_non_hmac_request_keys TerraformCloudSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#audit_non_hmac_response_keys TerraformCloudSecretBackend#audit_non_hmac_response_keys}
        :param backend: Unique name of the Vault Terraform Cloud mount to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#backend TerraformCloudSecretBackend#backend}
        :param base_path: Specifies the base path for the Terraform Cloud or Enterprise API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#base_path TerraformCloudSecretBackend#base_path}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#default_lease_ttl_seconds TerraformCloudSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#delegated_auth_accessors TerraformCloudSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#description TerraformCloudSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#disable_remount TerraformCloudSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#external_entropy_access TerraformCloudSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#force_no_cache TerraformCloudSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#id TerraformCloudSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#identity_token_key TerraformCloudSecretBackend#identity_token_key}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#listing_visibility TerraformCloudSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#local TerraformCloudSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#max_lease_ttl_seconds TerraformCloudSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#namespace TerraformCloudSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#options TerraformCloudSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#passthrough_request_headers TerraformCloudSecretBackend#passthrough_request_headers}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#plugin_version TerraformCloudSecretBackend#plugin_version}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#seal_wrap TerraformCloudSecretBackend#seal_wrap}
        :param token: Specifies the Terraform Cloud access token to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#token TerraformCloudSecretBackend#token}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36a8112f1eca6e51965cbe139d6f14784859b643b7981771a1ebafa49cd8bed9)
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
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument base_path", value=base_path, expected_type=type_hints["base_path"])
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
            check_type(argname="argument plugin_version", value=plugin_version, expected_type=type_hints["plugin_version"])
            check_type(argname="argument seal_wrap", value=seal_wrap, expected_type=type_hints["seal_wrap"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
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
        if address is not None:
            self._values["address"] = address
        if allowed_managed_keys is not None:
            self._values["allowed_managed_keys"] = allowed_managed_keys
        if allowed_response_headers is not None:
            self._values["allowed_response_headers"] = allowed_response_headers
        if audit_non_hmac_request_keys is not None:
            self._values["audit_non_hmac_request_keys"] = audit_non_hmac_request_keys
        if audit_non_hmac_response_keys is not None:
            self._values["audit_non_hmac_response_keys"] = audit_non_hmac_response_keys
        if backend is not None:
            self._values["backend"] = backend
        if base_path is not None:
            self._values["base_path"] = base_path
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
        if plugin_version is not None:
            self._values["plugin_version"] = plugin_version
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
    def address(self) -> typing.Optional[builtins.str]:
        '''Specifies the address of the Terraform Cloud instance, provided as "host:port" like "127.0.0.1:8500".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#address TerraformCloudSecretBackend#address}
        '''
        result = self._values.get("address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_managed_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of managed key registry entry names that the mount in question is allowed to access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#allowed_managed_keys TerraformCloudSecretBackend#allowed_managed_keys}
        '''
        result = self._values.get("allowed_managed_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_response_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#allowed_response_headers TerraformCloudSecretBackend#allowed_response_headers}
        '''
        result = self._values.get("allowed_response_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_request_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the request data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#audit_non_hmac_request_keys TerraformCloudSecretBackend#audit_non_hmac_request_keys}
        '''
        result = self._values.get("audit_non_hmac_request_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_response_keys(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the response data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#audit_non_hmac_response_keys TerraformCloudSecretBackend#audit_non_hmac_response_keys}
        '''
        result = self._values.get("audit_non_hmac_response_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the Vault Terraform Cloud mount to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#backend TerraformCloudSecretBackend#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_path(self) -> typing.Optional[builtins.str]:
        '''Specifies the base path for the Terraform Cloud or Enterprise API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#base_path TerraformCloudSecretBackend#base_path}
        '''
        result = self._values.get("base_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Default lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#default_lease_ttl_seconds TerraformCloudSecretBackend#default_lease_ttl_seconds}
        '''
        result = self._values.get("default_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delegated_auth_accessors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#delegated_auth_accessors TerraformCloudSecretBackend#delegated_auth_accessors}
        '''
        result = self._values.get("delegated_auth_accessors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#description TerraformCloudSecretBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#disable_remount TerraformCloudSecretBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def external_entropy_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the secrets engine to access Vault's external entropy source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#external_entropy_access TerraformCloudSecretBackend#external_entropy_access}
        '''
        result = self._values.get("external_entropy_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def force_no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, disables caching.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#force_no_cache TerraformCloudSecretBackend#force_no_cache}
        '''
        result = self._values.get("force_no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#id TerraformCloudSecretBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_key(self) -> typing.Optional[builtins.str]:
        '''The key to use for signing plugin workload identity tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#identity_token_key TerraformCloudSecretBackend#identity_token_key}
        '''
        result = self._values.get("identity_token_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def listing_visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies whether to show this mount in the UI-specific listing endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#listing_visibility TerraformCloudSecretBackend#listing_visibility}
        '''
        result = self._values.get("listing_visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Local mount flag that can be explicitly set to true to enforce local mount in HA environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#local TerraformCloudSecretBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum possible lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#max_lease_ttl_seconds TerraformCloudSecretBackend#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#namespace TerraformCloudSecretBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies mount type specific options that are passed to the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#options TerraformCloudSecretBackend#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def passthrough_request_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#passthrough_request_headers TerraformCloudSecretBackend#passthrough_request_headers}
        '''
        result = self._values.get("passthrough_request_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def plugin_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#plugin_version TerraformCloudSecretBackend#plugin_version}
        '''
        result = self._values.get("plugin_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seal_wrap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#seal_wrap TerraformCloudSecretBackend#seal_wrap}
        '''
        result = self._values.get("seal_wrap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Specifies the Terraform Cloud access token to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_backend#token TerraformCloudSecretBackend#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TerraformCloudSecretBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TerraformCloudSecretBackend",
    "TerraformCloudSecretBackendConfig",
]

publication.publish()

def _typecheckingstub__cb670bb1f83988527548ff49a106effe5ff981293679ca808168c3595244ab5e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    address: typing.Optional[builtins.str] = None,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    backend: typing.Optional[builtins.str] = None,
    base_path: typing.Optional[builtins.str] = None,
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
    plugin_version: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__eb0f2a72d52268d35608634bc64b82005da25ecce6f78804786d9de9c2f4f092(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f70600bfa486e11e6537a71481f301ddd3f39acfc66dab182265b9716cef587c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dbec364644d5d3ce5d184c6503cc37d3c9b9b51010cf4dcb559c5477a705b31(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0d5af28a9a652af588bd6e69ea347b0cbc23bb5d268ec6898d44f7da71281d3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c762736ee0bde802095063e9ddb18f9b17f27ada1c70bb22b775b84787bdae9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fa0e5027a3b0a99afe3c076d0d05e9d0b1ffec1adbf748e3d4d5db2ce988e2e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a747a5b09b773f055b70be3dc4c4e08d194860115cf746979e2f738c7f74b36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bc2e772123d6bf78f59792f496f2a7772eee8d01aa1d98976a18daf2d0d45bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e4e384b7efe69bdb1c11053f9aac4210561eaf6a622fdfbde0dd4c019ffb61c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c30f86f03071d57219f6838bc40266cfaa8514ffe95ae1aa34ed073e3d6f1fa(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbd4a0f5ef289d7126301db9f5d60745a4888af166e39951d809172a540a6a38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__febbd61ce8bc62bfe1a6cc1c14977369ebfe25f51e3ad8c024bbf759c8ad9076(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda273f3689a5b38a89c73c1ecafa47b6c244a26b7ca9f1e915ef1ce8a1203bb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60da534fac7a4205fff27faefeb67bbba6cc1e64ef3d310d1c08a6ba6df8e4da(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__465a79de5fc1db0bb63cef3044c9b837a98ef513f382320a3e63e10c98930ea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb688bd0447261844c8fd58af82a90e89a03962ffb30d2886c5ec3ee9bc1ef4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5028f850cffca8da3074a2ff75748ec2464705d087bfedc5002d40824c3d7dd4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98ba1fcf6a955cf8aac4eb705afd39028d648f4a2bdc0f024eed932fd7248fb1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ced2cf030956df58b4575c7fb7c6d0028693610ad2b2ade08965f19f5596458(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a012285f59e8f539cd75ed0615b27fd50f76a23f8f9faefeab0aab2f1d2c6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76b8f50bf099fefb5869f674e3e90a9067e0e52eacbf4d34af048baefa98ee2f(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2447a04d15cb65344336b8bbbff44068e0eaeca0325c9a97fa26b242409f8014(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4179e0dc11d5cb636a7408aa16ed229bd6033691b4b4000a20cb75dca9f41544(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dff1f39ae9fd5758ed27495567cd2c0a5c745afb4a6e49fe2ed28a859607d8c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12b266a38b9943cb4de23c68dc171b7e5d55db6d61a7711f88663b39c2f0aa88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a8112f1eca6e51965cbe139d6f14784859b643b7981771a1ebafa49cd8bed9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    address: typing.Optional[builtins.str] = None,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    backend: typing.Optional[builtins.str] = None,
    base_path: typing.Optional[builtins.str] = None,
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
    plugin_version: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
