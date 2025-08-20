r'''
# `vault_ldap_secret_backend`

Refer to the Terraform Registry for docs: [`vault_ldap_secret_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend).
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


class LdapSecretBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.ldapSecretBackend.LdapSecretBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend vault_ldap_secret_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        binddn: builtins.str,
        bindpass: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        certificate: typing.Optional[builtins.str] = None,
        client_tls_cert: typing.Optional[builtins.str] = None,
        client_tls_key: typing.Optional[builtins.str] = None,
        connection_timeout: typing.Optional[jsii.Number] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_key: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        password_policy: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        request_timeout: typing.Optional[jsii.Number] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        schema: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_static_role_import_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        upndomain: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        userattr: typing.Optional[builtins.str] = None,
        userdn: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend vault_ldap_secret_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param binddn: Distinguished name of object to bind when performing user and group search. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#binddn LdapSecretBackend#binddn}
        :param bindpass: LDAP password for searching for the user DN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#bindpass LdapSecretBackend#bindpass}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#allowed_managed_keys LdapSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#allowed_response_headers LdapSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#audit_non_hmac_request_keys LdapSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#audit_non_hmac_response_keys LdapSecretBackend#audit_non_hmac_response_keys}
        :param certificate: CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#certificate LdapSecretBackend#certificate}
        :param client_tls_cert: Client certificate to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#client_tls_cert LdapSecretBackend#client_tls_cert}
        :param client_tls_key: Client certificate key to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#client_tls_key LdapSecretBackend#client_tls_key}
        :param connection_timeout: Timeout, in seconds, when attempting to connect to the LDAP server before trying the next URL in the configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#connection_timeout LdapSecretBackend#connection_timeout}
        :param default_lease_ttl_seconds: Default lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#default_lease_ttl_seconds LdapSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#delegated_auth_accessors LdapSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#description LdapSecretBackend#description}
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#disable_automated_rotation LdapSecretBackend#disable_automated_rotation}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#disable_remount LdapSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#external_entropy_access LdapSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#force_no_cache LdapSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#id LdapSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#identity_token_key LdapSecretBackend#identity_token_key}
        :param insecure_tls: Skip LDAP server SSL Certificate verification - insecure and not recommended for production use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#insecure_tls LdapSecretBackend#insecure_tls}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#listing_visibility LdapSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#local LdapSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#max_lease_ttl_seconds LdapSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#namespace LdapSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#options LdapSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#passthrough_request_headers LdapSecretBackend#passthrough_request_headers}
        :param password_policy: Name of the password policy to use to generate passwords. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#password_policy LdapSecretBackend#password_policy}
        :param path: The path where the LDAP secrets backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#path LdapSecretBackend#path}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#plugin_version LdapSecretBackend#plugin_version}
        :param request_timeout: Timeout, in seconds, for the connection when making requests against the server before returning back an error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#request_timeout LdapSecretBackend#request_timeout}
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_period LdapSecretBackend#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_schedule LdapSecretBackend#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_window LdapSecretBackend#rotation_window}
        :param schema: The LDAP schema to use when storing entry passwords. Valid schemas include openldap, ad, and racf. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#schema LdapSecretBackend#schema}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#seal_wrap LdapSecretBackend#seal_wrap}
        :param skip_static_role_import_rotation: Skip rotation of static role secrets on import. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#skip_static_role_import_rotation LdapSecretBackend#skip_static_role_import_rotation}
        :param starttls: Issue a StartTLS command after establishing unencrypted connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#starttls LdapSecretBackend#starttls}
        :param upndomain: Enables userPrincipalDomain login with [username]@UPNDomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#upndomain LdapSecretBackend#upndomain}
        :param url: LDAP URL to connect to (default: ldap://127.0.0.1). Multiple URLs can be specified by concatenating them with commas; they will be tried in-order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#url LdapSecretBackend#url}
        :param userattr: Attribute used for users (default: cn). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#userattr LdapSecretBackend#userattr}
        :param userdn: LDAP domain to use for users (eg: ou=People,dc=example,dc=org). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#userdn LdapSecretBackend#userdn}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3efd2b5e1813d0e339ad1f3ea85e3e0672513d49f4a8474ab0ec8d5e263bd03b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = LdapSecretBackendConfig(
            binddn=binddn,
            bindpass=bindpass,
            allowed_managed_keys=allowed_managed_keys,
            allowed_response_headers=allowed_response_headers,
            audit_non_hmac_request_keys=audit_non_hmac_request_keys,
            audit_non_hmac_response_keys=audit_non_hmac_response_keys,
            certificate=certificate,
            client_tls_cert=client_tls_cert,
            client_tls_key=client_tls_key,
            connection_timeout=connection_timeout,
            default_lease_ttl_seconds=default_lease_ttl_seconds,
            delegated_auth_accessors=delegated_auth_accessors,
            description=description,
            disable_automated_rotation=disable_automated_rotation,
            disable_remount=disable_remount,
            external_entropy_access=external_entropy_access,
            force_no_cache=force_no_cache,
            id=id,
            identity_token_key=identity_token_key,
            insecure_tls=insecure_tls,
            listing_visibility=listing_visibility,
            local=local,
            max_lease_ttl_seconds=max_lease_ttl_seconds,
            namespace=namespace,
            options=options,
            passthrough_request_headers=passthrough_request_headers,
            password_policy=password_policy,
            path=path,
            plugin_version=plugin_version,
            request_timeout=request_timeout,
            rotation_period=rotation_period,
            rotation_schedule=rotation_schedule,
            rotation_window=rotation_window,
            schema=schema,
            seal_wrap=seal_wrap,
            skip_static_role_import_rotation=skip_static_role_import_rotation,
            starttls=starttls,
            upndomain=upndomain,
            url=url,
            userattr=userattr,
            userdn=userdn,
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
        '''Generates CDKTF code for importing a LdapSecretBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LdapSecretBackend to import.
        :param import_from_id: The id of the existing LdapSecretBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LdapSecretBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__054f754ae69f1db716d7d4f273707a48052946b5f4e60e8e233eac06804df88f)
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

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetClientTlsCert")
    def reset_client_tls_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientTlsCert", []))

    @jsii.member(jsii_name="resetClientTlsKey")
    def reset_client_tls_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientTlsKey", []))

    @jsii.member(jsii_name="resetConnectionTimeout")
    def reset_connection_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionTimeout", []))

    @jsii.member(jsii_name="resetDefaultLeaseTtlSeconds")
    def reset_default_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultLeaseTtlSeconds", []))

    @jsii.member(jsii_name="resetDelegatedAuthAccessors")
    def reset_delegated_auth_accessors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelegatedAuthAccessors", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableAutomatedRotation")
    def reset_disable_automated_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAutomatedRotation", []))

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

    @jsii.member(jsii_name="resetInsecureTls")
    def reset_insecure_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureTls", []))

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

    @jsii.member(jsii_name="resetRequestTimeout")
    def reset_request_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTimeout", []))

    @jsii.member(jsii_name="resetRotationPeriod")
    def reset_rotation_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationPeriod", []))

    @jsii.member(jsii_name="resetRotationSchedule")
    def reset_rotation_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationSchedule", []))

    @jsii.member(jsii_name="resetRotationWindow")
    def reset_rotation_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationWindow", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetSealWrap")
    def reset_seal_wrap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSealWrap", []))

    @jsii.member(jsii_name="resetSkipStaticRoleImportRotation")
    def reset_skip_static_role_import_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipStaticRoleImportRotation", []))

    @jsii.member(jsii_name="resetStarttls")
    def reset_starttls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStarttls", []))

    @jsii.member(jsii_name="resetUpndomain")
    def reset_upndomain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpndomain", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUserattr")
    def reset_userattr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserattr", []))

    @jsii.member(jsii_name="resetUserdn")
    def reset_userdn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserdn", []))

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
    @jsii.member(jsii_name="binddnInput")
    def binddn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "binddnInput"))

    @builtins.property
    @jsii.member(jsii_name="bindpassInput")
    def bindpass_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindpassInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateInput"))

    @builtins.property
    @jsii.member(jsii_name="clientTlsCertInput")
    def client_tls_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientTlsCertInput"))

    @builtins.property
    @jsii.member(jsii_name="clientTlsKeyInput")
    def client_tls_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientTlsKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionTimeoutInput")
    def connection_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectionTimeoutInput"))

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
    @jsii.member(jsii_name="disableAutomatedRotationInput")
    def disable_automated_rotation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableAutomatedRotationInput"))

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
    @jsii.member(jsii_name="insecureTlsInput")
    def insecure_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureTlsInput"))

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
    @jsii.member(jsii_name="requestTimeoutInput")
    def request_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requestTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationPeriodInput")
    def rotation_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationScheduleInput")
    def rotation_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationWindowInput")
    def rotation_window_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property
    @jsii.member(jsii_name="sealWrapInput")
    def seal_wrap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sealWrapInput"))

    @builtins.property
    @jsii.member(jsii_name="skipStaticRoleImportRotationInput")
    def skip_static_role_import_rotation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipStaticRoleImportRotationInput"))

    @builtins.property
    @jsii.member(jsii_name="starttlsInput")
    def starttls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "starttlsInput"))

    @builtins.property
    @jsii.member(jsii_name="upndomainInput")
    def upndomain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "upndomainInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="userattrInput")
    def userattr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userattrInput"))

    @builtins.property
    @jsii.member(jsii_name="userdnInput")
    def userdn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userdnInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedManagedKeys")
    def allowed_managed_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedManagedKeys"))

    @allowed_managed_keys.setter
    def allowed_managed_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1991d3ee897002e54891ed0aa5d9a4d531f4796a6b305b11aebeb881008fdf64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedManagedKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedResponseHeaders")
    def allowed_response_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedResponseHeaders"))

    @allowed_response_headers.setter
    def allowed_response_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10227d40ec74fe3996e422f3cfe9c10b9915c49f6773a9f74f400e6681ac30e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedResponseHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacRequestKeys")
    def audit_non_hmac_request_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacRequestKeys"))

    @audit_non_hmac_request_keys.setter
    def audit_non_hmac_request_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d501d34e9462b63e2306b4474ad0603b2a6db8faba3a255e7b61fc90f4cab38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacRequestKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="auditNonHmacResponseKeys")
    def audit_non_hmac_response_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditNonHmacResponseKeys"))

    @audit_non_hmac_response_keys.setter
    def audit_non_hmac_response_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc2a3daff429f3eac298a21628e5e8c8c0320648fcf83f2bd7ef1f2db798c5b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditNonHmacResponseKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="binddn")
    def binddn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "binddn"))

    @binddn.setter
    def binddn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2138976a300915bd48c3af8ebf323bbe9295bc67cc0188ef0dbd93aa1a674a71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "binddn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindpass")
    def bindpass(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindpass"))

    @bindpass.setter
    def bindpass(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f64725ea16eaec4ce22ab9a0f34e326a66a58dcc7208fbbf1100adacdac18f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindpass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c59a999e6751aa98fd8bed175069d64f3901c3832eec4bb257910b9947137a9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTlsCert")
    def client_tls_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTlsCert"))

    @client_tls_cert.setter
    def client_tls_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb25f57edce9d79748cc42ba41386b04d43bf08ccdbd4ad0748e49a78d79313a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTlsCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTlsKey")
    def client_tls_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTlsKey"))

    @client_tls_key.setter
    def client_tls_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91a16c39ce8818e8c64c552cef581c740d6cda10cfd1803359b77ccd90a790af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTlsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionTimeout")
    def connection_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectionTimeout"))

    @connection_timeout.setter
    def connection_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd6b2027eab1e5377cfae0fc75f4d874574eb89b348288d05f58ad4e823da4ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSeconds")
    def default_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLeaseTtlSeconds"))

    @default_lease_ttl_seconds.setter
    def default_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20aee44e8069cd7c733f6af19512fb4e7e6125f6e5dbdc1579edc020032dcd94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delegatedAuthAccessors")
    def delegated_auth_accessors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "delegatedAuthAccessors"))

    @delegated_auth_accessors.setter
    def delegated_auth_accessors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bec68b551e60358f77b28a0970093a48361bbfa0f441ef45a3faf0bf3615bcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delegatedAuthAccessors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9488814bf674c94c6e32ff39b7ef65729db1f162c242e54f7f57c04f864ac678)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableAutomatedRotation")
    def disable_automated_rotation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableAutomatedRotation"))

    @disable_automated_rotation.setter
    def disable_automated_rotation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7135fa18037bc917b86b55855397e6f55b20316b5faa18ccbb975b1d166eb1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAutomatedRotation", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__09404b5c1b9015100b8afe8be0d2c0bc1a2babcf4d9f73a9b349b9dee5425390)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1b42b6aae4a66b45e0b0ee406dba027025d932a399fe665e827dde3ac8acbc40)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16a2f006e5673a8015eb6fce85bb09bb305fdb715cb832013fb00dfe87a2eb5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceNoCache", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ed0da9ce544aa35aabb6b656c57460a34e5c5c49a198f3f25af77836c26f425)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenKey")
    def identity_token_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityTokenKey"))

    @identity_token_key.setter
    def identity_token_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b25d999a4534e3c505da3114695febcef96a576719f52d2a6ada1adc62dff9ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureTls")
    def insecure_tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecureTls"))

    @insecure_tls.setter
    def insecure_tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a5e40b05543df36e441cc902ec64edf3ac2a0568e1698388f1ff1807a9e22c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listingVisibility")
    def listing_visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "listingVisibility"))

    @listing_visibility.setter
    def listing_visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c69db2aef6a41b007951a5d5153cda534bc89d836a0dddc357498187cacd5fa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__322a4512529c8002a5ce3e66bace783fef306c0cd14418535c605b23295d5a81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b200c0626ad7db2c58437257c14c9dbcc0f620804102046de62c07e7f3486a05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f2452c23991bea36d6627d4b34e1de2ea6f82513d7634264b32d9423dbb8990)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d61028035c3fdcb84fe4167e8af67bbaeb0525197ab0d1509b2c188fac11f5a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passthroughRequestHeaders")
    def passthrough_request_headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passthroughRequestHeaders"))

    @passthrough_request_headers.setter
    def passthrough_request_headers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a171bf9757d0457b420e29372f981e4dd4c016044064d4a4b414c380dd158026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passthroughRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordPolicy")
    def password_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordPolicy"))

    @password_policy.setter
    def password_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e871f19e87afcd982f8a639c77be9b024c1a7a0b9ae06196534d5a110950d12d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4abade05d67fea0315c99fdbc6d1997368778912cb2ea8b1624f68144929a640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginVersion")
    def plugin_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginVersion"))

    @plugin_version.setter
    def plugin_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b688d5371167a82f77f91cd11a19e02d5621667d72869506938f86da4ef3deb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestTimeout")
    def request_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requestTimeout"))

    @request_timeout.setter
    def request_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__221d1346cd595c4ad43df919c1f0883d76125d850b3211889076abe87a8e8e66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationPeriod")
    def rotation_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationPeriod"))

    @rotation_period.setter
    def rotation_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55c771184fbd42f4e9628589c2b45f02faffb5bff84c0561a50c07564be94430)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationSchedule")
    def rotation_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationSchedule"))

    @rotation_schedule.setter
    def rotation_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453f32301b8c821394f9f54ea1fdb11dedec1881307962d9771bf9243e9521ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationWindow")
    def rotation_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationWindow"))

    @rotation_window.setter
    def rotation_window(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3977c8e00c799f4d9b8accbeb1b8b7bc62b31985bfc9b1725706401d5bb21ab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationWindow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e666c92c6da867b07b8b5d199eb295b1af48b4290178cb8ea226fb25a8713ed2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "schema", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e3142fc0064d051096665a5f627931573526dff473f7e3a6dd2ef3c69e0c5c98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sealWrap", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipStaticRoleImportRotation")
    def skip_static_role_import_rotation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "skipStaticRoleImportRotation"))

    @skip_static_role_import_rotation.setter
    def skip_static_role_import_rotation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54d3d8fd821ebc5d4eb57b834113bd6b870a0195d72b3e47b69ca32e27fc0d73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipStaticRoleImportRotation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="starttls")
    def starttls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "starttls"))

    @starttls.setter
    def starttls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614d2c6d7e9cfb02e43ca89d4a38d8f5f3fa0834399bce7b56ec9ac7ecab4691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "starttls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="upndomain")
    def upndomain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "upndomain"))

    @upndomain.setter
    def upndomain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff45d0c8aca573b7f9e70d7ad2063de4a6eca448012a0c09c0bb6aad6123ef96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "upndomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d5a2894b5b79b00dafc554ee59b539d325220c9d707df81b7b6db4a912d4783)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userattr")
    def userattr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userattr"))

    @userattr.setter
    def userattr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08359748a06feda7c126ce56f0b2e25389f89eaf033eb142c557791eb9cc92c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userattr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userdn")
    def userdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userdn"))

    @userdn.setter
    def userdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e7c6963328f77644b5d2f8bce60223bf91bbca832232f2e5789227ade9fe8e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userdn", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.ldapSecretBackend.LdapSecretBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "binddn": "binddn",
        "bindpass": "bindpass",
        "allowed_managed_keys": "allowedManagedKeys",
        "allowed_response_headers": "allowedResponseHeaders",
        "audit_non_hmac_request_keys": "auditNonHmacRequestKeys",
        "audit_non_hmac_response_keys": "auditNonHmacResponseKeys",
        "certificate": "certificate",
        "client_tls_cert": "clientTlsCert",
        "client_tls_key": "clientTlsKey",
        "connection_timeout": "connectionTimeout",
        "default_lease_ttl_seconds": "defaultLeaseTtlSeconds",
        "delegated_auth_accessors": "delegatedAuthAccessors",
        "description": "description",
        "disable_automated_rotation": "disableAutomatedRotation",
        "disable_remount": "disableRemount",
        "external_entropy_access": "externalEntropyAccess",
        "force_no_cache": "forceNoCache",
        "id": "id",
        "identity_token_key": "identityTokenKey",
        "insecure_tls": "insecureTls",
        "listing_visibility": "listingVisibility",
        "local": "local",
        "max_lease_ttl_seconds": "maxLeaseTtlSeconds",
        "namespace": "namespace",
        "options": "options",
        "passthrough_request_headers": "passthroughRequestHeaders",
        "password_policy": "passwordPolicy",
        "path": "path",
        "plugin_version": "pluginVersion",
        "request_timeout": "requestTimeout",
        "rotation_period": "rotationPeriod",
        "rotation_schedule": "rotationSchedule",
        "rotation_window": "rotationWindow",
        "schema": "schema",
        "seal_wrap": "sealWrap",
        "skip_static_role_import_rotation": "skipStaticRoleImportRotation",
        "starttls": "starttls",
        "upndomain": "upndomain",
        "url": "url",
        "userattr": "userattr",
        "userdn": "userdn",
    },
)
class LdapSecretBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        binddn: builtins.str,
        bindpass: builtins.str,
        allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        certificate: typing.Optional[builtins.str] = None,
        client_tls_cert: typing.Optional[builtins.str] = None,
        client_tls_key: typing.Optional[builtins.str] = None,
        connection_timeout: typing.Optional[jsii.Number] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_key: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        listing_visibility: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        password_policy: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        plugin_version: typing.Optional[builtins.str] = None,
        request_timeout: typing.Optional[jsii.Number] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        schema: typing.Optional[builtins.str] = None,
        seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        skip_static_role_import_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        upndomain: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        userattr: typing.Optional[builtins.str] = None,
        userdn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param binddn: Distinguished name of object to bind when performing user and group search. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#binddn LdapSecretBackend#binddn}
        :param bindpass: LDAP password for searching for the user DN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#bindpass LdapSecretBackend#bindpass}
        :param allowed_managed_keys: List of managed key registry entry names that the mount in question is allowed to access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#allowed_managed_keys LdapSecretBackend#allowed_managed_keys}
        :param allowed_response_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#allowed_response_headers LdapSecretBackend#allowed_response_headers}
        :param audit_non_hmac_request_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the request data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#audit_non_hmac_request_keys LdapSecretBackend#audit_non_hmac_request_keys}
        :param audit_non_hmac_response_keys: Specifies the list of keys that will not be HMAC'd by audit devices in the response data object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#audit_non_hmac_response_keys LdapSecretBackend#audit_non_hmac_response_keys}
        :param certificate: CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#certificate LdapSecretBackend#certificate}
        :param client_tls_cert: Client certificate to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#client_tls_cert LdapSecretBackend#client_tls_cert}
        :param client_tls_key: Client certificate key to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#client_tls_key LdapSecretBackend#client_tls_key}
        :param connection_timeout: Timeout, in seconds, when attempting to connect to the LDAP server before trying the next URL in the configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#connection_timeout LdapSecretBackend#connection_timeout}
        :param default_lease_ttl_seconds: Default lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#default_lease_ttl_seconds LdapSecretBackend#default_lease_ttl_seconds}
        :param delegated_auth_accessors: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#delegated_auth_accessors LdapSecretBackend#delegated_auth_accessors}
        :param description: Human-friendly description of the mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#description LdapSecretBackend#description}
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#disable_automated_rotation LdapSecretBackend#disable_automated_rotation}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#disable_remount LdapSecretBackend#disable_remount}
        :param external_entropy_access: Enable the secrets engine to access Vault's external entropy source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#external_entropy_access LdapSecretBackend#external_entropy_access}
        :param force_no_cache: If set to true, disables caching. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#force_no_cache LdapSecretBackend#force_no_cache}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#id LdapSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_key: The key to use for signing plugin workload identity tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#identity_token_key LdapSecretBackend#identity_token_key}
        :param insecure_tls: Skip LDAP server SSL Certificate verification - insecure and not recommended for production use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#insecure_tls LdapSecretBackend#insecure_tls}
        :param listing_visibility: Specifies whether to show this mount in the UI-specific listing endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#listing_visibility LdapSecretBackend#listing_visibility}
        :param local: Local mount flag that can be explicitly set to true to enforce local mount in HA environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#local LdapSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for tokens and secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#max_lease_ttl_seconds LdapSecretBackend#max_lease_ttl_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#namespace LdapSecretBackend#namespace}
        :param options: Specifies mount type specific options that are passed to the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#options LdapSecretBackend#options}
        :param passthrough_request_headers: List of headers to allow and pass from the request to the plugin. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#passthrough_request_headers LdapSecretBackend#passthrough_request_headers}
        :param password_policy: Name of the password policy to use to generate passwords. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#password_policy LdapSecretBackend#password_policy}
        :param path: The path where the LDAP secrets backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#path LdapSecretBackend#path}
        :param plugin_version: Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#plugin_version LdapSecretBackend#plugin_version}
        :param request_timeout: Timeout, in seconds, for the connection when making requests against the server before returning back an error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#request_timeout LdapSecretBackend#request_timeout}
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_period LdapSecretBackend#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_schedule LdapSecretBackend#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_window LdapSecretBackend#rotation_window}
        :param schema: The LDAP schema to use when storing entry passwords. Valid schemas include openldap, ad, and racf. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#schema LdapSecretBackend#schema}
        :param seal_wrap: Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#seal_wrap LdapSecretBackend#seal_wrap}
        :param skip_static_role_import_rotation: Skip rotation of static role secrets on import. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#skip_static_role_import_rotation LdapSecretBackend#skip_static_role_import_rotation}
        :param starttls: Issue a StartTLS command after establishing unencrypted connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#starttls LdapSecretBackend#starttls}
        :param upndomain: Enables userPrincipalDomain login with [username]@UPNDomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#upndomain LdapSecretBackend#upndomain}
        :param url: LDAP URL to connect to (default: ldap://127.0.0.1). Multiple URLs can be specified by concatenating them with commas; they will be tried in-order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#url LdapSecretBackend#url}
        :param userattr: Attribute used for users (default: cn). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#userattr LdapSecretBackend#userattr}
        :param userdn: LDAP domain to use for users (eg: ou=People,dc=example,dc=org). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#userdn LdapSecretBackend#userdn}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd44b62dd27ea27e6843380920b77ca416beaa2bbf06011c8c46620876cab32e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument binddn", value=binddn, expected_type=type_hints["binddn"])
            check_type(argname="argument bindpass", value=bindpass, expected_type=type_hints["bindpass"])
            check_type(argname="argument allowed_managed_keys", value=allowed_managed_keys, expected_type=type_hints["allowed_managed_keys"])
            check_type(argname="argument allowed_response_headers", value=allowed_response_headers, expected_type=type_hints["allowed_response_headers"])
            check_type(argname="argument audit_non_hmac_request_keys", value=audit_non_hmac_request_keys, expected_type=type_hints["audit_non_hmac_request_keys"])
            check_type(argname="argument audit_non_hmac_response_keys", value=audit_non_hmac_response_keys, expected_type=type_hints["audit_non_hmac_response_keys"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument client_tls_cert", value=client_tls_cert, expected_type=type_hints["client_tls_cert"])
            check_type(argname="argument client_tls_key", value=client_tls_key, expected_type=type_hints["client_tls_key"])
            check_type(argname="argument connection_timeout", value=connection_timeout, expected_type=type_hints["connection_timeout"])
            check_type(argname="argument default_lease_ttl_seconds", value=default_lease_ttl_seconds, expected_type=type_hints["default_lease_ttl_seconds"])
            check_type(argname="argument delegated_auth_accessors", value=delegated_auth_accessors, expected_type=type_hints["delegated_auth_accessors"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_automated_rotation", value=disable_automated_rotation, expected_type=type_hints["disable_automated_rotation"])
            check_type(argname="argument disable_remount", value=disable_remount, expected_type=type_hints["disable_remount"])
            check_type(argname="argument external_entropy_access", value=external_entropy_access, expected_type=type_hints["external_entropy_access"])
            check_type(argname="argument force_no_cache", value=force_no_cache, expected_type=type_hints["force_no_cache"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_token_key", value=identity_token_key, expected_type=type_hints["identity_token_key"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument listing_visibility", value=listing_visibility, expected_type=type_hints["listing_visibility"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument max_lease_ttl_seconds", value=max_lease_ttl_seconds, expected_type=type_hints["max_lease_ttl_seconds"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument passthrough_request_headers", value=passthrough_request_headers, expected_type=type_hints["passthrough_request_headers"])
            check_type(argname="argument password_policy", value=password_policy, expected_type=type_hints["password_policy"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument plugin_version", value=plugin_version, expected_type=type_hints["plugin_version"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument rotation_period", value=rotation_period, expected_type=type_hints["rotation_period"])
            check_type(argname="argument rotation_schedule", value=rotation_schedule, expected_type=type_hints["rotation_schedule"])
            check_type(argname="argument rotation_window", value=rotation_window, expected_type=type_hints["rotation_window"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument seal_wrap", value=seal_wrap, expected_type=type_hints["seal_wrap"])
            check_type(argname="argument skip_static_role_import_rotation", value=skip_static_role_import_rotation, expected_type=type_hints["skip_static_role_import_rotation"])
            check_type(argname="argument starttls", value=starttls, expected_type=type_hints["starttls"])
            check_type(argname="argument upndomain", value=upndomain, expected_type=type_hints["upndomain"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument userattr", value=userattr, expected_type=type_hints["userattr"])
            check_type(argname="argument userdn", value=userdn, expected_type=type_hints["userdn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "binddn": binddn,
            "bindpass": bindpass,
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
        if certificate is not None:
            self._values["certificate"] = certificate
        if client_tls_cert is not None:
            self._values["client_tls_cert"] = client_tls_cert
        if client_tls_key is not None:
            self._values["client_tls_key"] = client_tls_key
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if default_lease_ttl_seconds is not None:
            self._values["default_lease_ttl_seconds"] = default_lease_ttl_seconds
        if delegated_auth_accessors is not None:
            self._values["delegated_auth_accessors"] = delegated_auth_accessors
        if description is not None:
            self._values["description"] = description
        if disable_automated_rotation is not None:
            self._values["disable_automated_rotation"] = disable_automated_rotation
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
        if insecure_tls is not None:
            self._values["insecure_tls"] = insecure_tls
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
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if rotation_period is not None:
            self._values["rotation_period"] = rotation_period
        if rotation_schedule is not None:
            self._values["rotation_schedule"] = rotation_schedule
        if rotation_window is not None:
            self._values["rotation_window"] = rotation_window
        if schema is not None:
            self._values["schema"] = schema
        if seal_wrap is not None:
            self._values["seal_wrap"] = seal_wrap
        if skip_static_role_import_rotation is not None:
            self._values["skip_static_role_import_rotation"] = skip_static_role_import_rotation
        if starttls is not None:
            self._values["starttls"] = starttls
        if upndomain is not None:
            self._values["upndomain"] = upndomain
        if url is not None:
            self._values["url"] = url
        if userattr is not None:
            self._values["userattr"] = userattr
        if userdn is not None:
            self._values["userdn"] = userdn

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
    def binddn(self) -> builtins.str:
        '''Distinguished name of object to bind when performing user and group search.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#binddn LdapSecretBackend#binddn}
        '''
        result = self._values.get("binddn")
        assert result is not None, "Required property 'binddn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bindpass(self) -> builtins.str:
        '''LDAP password for searching for the user DN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#bindpass LdapSecretBackend#bindpass}
        '''
        result = self._values.get("bindpass")
        assert result is not None, "Required property 'bindpass' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_managed_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of managed key registry entry names that the mount in question is allowed to access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#allowed_managed_keys LdapSecretBackend#allowed_managed_keys}
        '''
        result = self._values.get("allowed_managed_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_response_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#allowed_response_headers LdapSecretBackend#allowed_response_headers}
        '''
        result = self._values.get("allowed_response_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_request_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the request data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#audit_non_hmac_request_keys LdapSecretBackend#audit_non_hmac_request_keys}
        '''
        result = self._values.get("audit_non_hmac_request_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_non_hmac_response_keys(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the list of keys that will not be HMAC'd by audit devices in the response data object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#audit_non_hmac_response_keys LdapSecretBackend#audit_non_hmac_response_keys}
        '''
        result = self._values.get("audit_non_hmac_response_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def certificate(self) -> typing.Optional[builtins.str]:
        '''CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#certificate LdapSecretBackend#certificate}
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_tls_cert(self) -> typing.Optional[builtins.str]:
        '''Client certificate to provide to the LDAP server, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#client_tls_cert LdapSecretBackend#client_tls_cert}
        '''
        result = self._values.get("client_tls_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_tls_key(self) -> typing.Optional[builtins.str]:
        '''Client certificate key to provide to the LDAP server, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#client_tls_key LdapSecretBackend#client_tls_key}
        '''
        result = self._values.get("client_tls_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout, in seconds, when attempting to connect to the LDAP server before trying the next URL in the configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#connection_timeout LdapSecretBackend#connection_timeout}
        '''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Default lease duration for tokens and secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#default_lease_ttl_seconds LdapSecretBackend#default_lease_ttl_seconds}
        '''
        result = self._values.get("default_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delegated_auth_accessors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#delegated_auth_accessors LdapSecretBackend#delegated_auth_accessors}
        '''
        result = self._values.get("delegated_auth_accessors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#description LdapSecretBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_automated_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Stops rotation of the root credential until set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#disable_automated_rotation LdapSecretBackend#disable_automated_rotation}
        '''
        result = self._values.get("disable_automated_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#disable_remount LdapSecretBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def external_entropy_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable the secrets engine to access Vault's external entropy source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#external_entropy_access LdapSecretBackend#external_entropy_access}
        '''
        result = self._values.get("external_entropy_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def force_no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, disables caching.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#force_no_cache LdapSecretBackend#force_no_cache}
        '''
        result = self._values.get("force_no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#id LdapSecretBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_key(self) -> typing.Optional[builtins.str]:
        '''The key to use for signing plugin workload identity tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#identity_token_key LdapSecretBackend#identity_token_key}
        '''
        result = self._values.get("identity_token_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Skip LDAP server SSL Certificate verification - insecure and not recommended for production use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#insecure_tls LdapSecretBackend#insecure_tls}
        '''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def listing_visibility(self) -> typing.Optional[builtins.str]:
        '''Specifies whether to show this mount in the UI-specific listing endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#listing_visibility LdapSecretBackend#listing_visibility}
        '''
        result = self._values.get("listing_visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Local mount flag that can be explicitly set to true to enforce local mount in HA environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#local LdapSecretBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum possible lease duration for tokens and secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#max_lease_ttl_seconds LdapSecretBackend#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#namespace LdapSecretBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Specifies mount type specific options that are passed to the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#options LdapSecretBackend#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def passthrough_request_headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of headers to allow and pass from the request to the plugin.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#passthrough_request_headers LdapSecretBackend#passthrough_request_headers}
        '''
        result = self._values.get("passthrough_request_headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def password_policy(self) -> typing.Optional[builtins.str]:
        '''Name of the password policy to use to generate passwords.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#password_policy LdapSecretBackend#password_policy}
        '''
        result = self._values.get("password_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path where the LDAP secrets backend is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#path LdapSecretBackend#path}
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def plugin_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the semantic version of the plugin to use, e.g. 'v1.0.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#plugin_version LdapSecretBackend#plugin_version}
        '''
        result = self._values.get("plugin_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout, in seconds, for the connection when making requests against the server before returning back an error.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#request_timeout LdapSecretBackend#request_timeout}
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_period(self) -> typing.Optional[jsii.Number]:
        '''The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_period LdapSecretBackend#rotation_period}
        '''
        result = self._values.get("rotation_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_schedule(self) -> typing.Optional[builtins.str]:
        '''The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_schedule LdapSecretBackend#rotation_schedule}
        '''
        result = self._values.get("rotation_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_window(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered.

        Can only be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#rotation_window LdapSecretBackend#rotation_window}
        '''
        result = self._values.get("rotation_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''The LDAP schema to use when storing entry passwords. Valid schemas include openldap, ad, and racf.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#schema LdapSecretBackend#schema}
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def seal_wrap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable seal wrapping for the mount, causing values stored by the mount to be wrapped by the seal's encryption capability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#seal_wrap LdapSecretBackend#seal_wrap}
        '''
        result = self._values.get("seal_wrap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def skip_static_role_import_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Skip rotation of static role secrets on import.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#skip_static_role_import_rotation LdapSecretBackend#skip_static_role_import_rotation}
        '''
        result = self._values.get("skip_static_role_import_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def starttls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Issue a StartTLS command after establishing unencrypted connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#starttls LdapSecretBackend#starttls}
        '''
        result = self._values.get("starttls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def upndomain(self) -> typing.Optional[builtins.str]:
        '''Enables userPrincipalDomain login with [username]@UPNDomain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#upndomain LdapSecretBackend#upndomain}
        '''
        result = self._values.get("upndomain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''LDAP URL to connect to (default: ldap://127.0.0.1). Multiple URLs can be specified by concatenating them with commas; they will be tried in-order.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#url LdapSecretBackend#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userattr(self) -> typing.Optional[builtins.str]:
        '''Attribute used for users (default: cn).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#userattr LdapSecretBackend#userattr}
        '''
        result = self._values.get("userattr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userdn(self) -> typing.Optional[builtins.str]:
        '''LDAP domain to use for users (eg: ou=People,dc=example,dc=org).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend#userdn LdapSecretBackend#userdn}
        '''
        result = self._values.get("userdn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LdapSecretBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LdapSecretBackend",
    "LdapSecretBackendConfig",
]

publication.publish()

def _typecheckingstub__3efd2b5e1813d0e339ad1f3ea85e3e0672513d49f4a8474ab0ec8d5e263bd03b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    binddn: builtins.str,
    bindpass: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    certificate: typing.Optional[builtins.str] = None,
    client_tls_cert: typing.Optional[builtins.str] = None,
    client_tls_key: typing.Optional[builtins.str] = None,
    connection_timeout: typing.Optional[jsii.Number] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_key: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    password_policy: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    request_timeout: typing.Optional[jsii.Number] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    schema: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_static_role_import_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    upndomain: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    userattr: typing.Optional[builtins.str] = None,
    userdn: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__054f754ae69f1db716d7d4f273707a48052946b5f4e60e8e233eac06804df88f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1991d3ee897002e54891ed0aa5d9a4d531f4796a6b305b11aebeb881008fdf64(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10227d40ec74fe3996e422f3cfe9c10b9915c49f6773a9f74f400e6681ac30e0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d501d34e9462b63e2306b4474ad0603b2a6db8faba3a255e7b61fc90f4cab38(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc2a3daff429f3eac298a21628e5e8c8c0320648fcf83f2bd7ef1f2db798c5b0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2138976a300915bd48c3af8ebf323bbe9295bc67cc0188ef0dbd93aa1a674a71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f64725ea16eaec4ce22ab9a0f34e326a66a58dcc7208fbbf1100adacdac18f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c59a999e6751aa98fd8bed175069d64f3901c3832eec4bb257910b9947137a9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb25f57edce9d79748cc42ba41386b04d43bf08ccdbd4ad0748e49a78d79313a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a16c39ce8818e8c64c552cef581c740d6cda10cfd1803359b77ccd90a790af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd6b2027eab1e5377cfae0fc75f4d874574eb89b348288d05f58ad4e823da4ff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20aee44e8069cd7c733f6af19512fb4e7e6125f6e5dbdc1579edc020032dcd94(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bec68b551e60358f77b28a0970093a48361bbfa0f441ef45a3faf0bf3615bcf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9488814bf674c94c6e32ff39b7ef65729db1f162c242e54f7f57c04f864ac678(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7135fa18037bc917b86b55855397e6f55b20316b5faa18ccbb975b1d166eb1e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09404b5c1b9015100b8afe8be0d2c0bc1a2babcf4d9f73a9b349b9dee5425390(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b42b6aae4a66b45e0b0ee406dba027025d932a399fe665e827dde3ac8acbc40(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16a2f006e5673a8015eb6fce85bb09bb305fdb715cb832013fb00dfe87a2eb5e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ed0da9ce544aa35aabb6b656c57460a34e5c5c49a198f3f25af77836c26f425(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b25d999a4534e3c505da3114695febcef96a576719f52d2a6ada1adc62dff9ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a5e40b05543df36e441cc902ec64edf3ac2a0568e1698388f1ff1807a9e22c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c69db2aef6a41b007951a5d5153cda534bc89d836a0dddc357498187cacd5fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322a4512529c8002a5ce3e66bace783fef306c0cd14418535c605b23295d5a81(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b200c0626ad7db2c58437257c14c9dbcc0f620804102046de62c07e7f3486a05(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f2452c23991bea36d6627d4b34e1de2ea6f82513d7634264b32d9423dbb8990(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d61028035c3fdcb84fe4167e8af67bbaeb0525197ab0d1509b2c188fac11f5a2(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a171bf9757d0457b420e29372f981e4dd4c016044064d4a4b414c380dd158026(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e871f19e87afcd982f8a639c77be9b024c1a7a0b9ae06196534d5a110950d12d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4abade05d67fea0315c99fdbc6d1997368778912cb2ea8b1624f68144929a640(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b688d5371167a82f77f91cd11a19e02d5621667d72869506938f86da4ef3deb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__221d1346cd595c4ad43df919c1f0883d76125d850b3211889076abe87a8e8e66(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55c771184fbd42f4e9628589c2b45f02faffb5bff84c0561a50c07564be94430(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453f32301b8c821394f9f54ea1fdb11dedec1881307962d9771bf9243e9521ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3977c8e00c799f4d9b8accbeb1b8b7bc62b31985bfc9b1725706401d5bb21ab2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e666c92c6da867b07b8b5d199eb295b1af48b4290178cb8ea226fb25a8713ed2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3142fc0064d051096665a5f627931573526dff473f7e3a6dd2ef3c69e0c5c98(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54d3d8fd821ebc5d4eb57b834113bd6b870a0195d72b3e47b69ca32e27fc0d73(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614d2c6d7e9cfb02e43ca89d4a38d8f5f3fa0834399bce7b56ec9ac7ecab4691(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff45d0c8aca573b7f9e70d7ad2063de4a6eca448012a0c09c0bb6aad6123ef96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d5a2894b5b79b00dafc554ee59b539d325220c9d707df81b7b6db4a912d4783(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08359748a06feda7c126ce56f0b2e25389f89eaf033eb142c557791eb9cc92c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e7c6963328f77644b5d2f8bce60223bf91bbca832232f2e5789227ade9fe8e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd44b62dd27ea27e6843380920b77ca416beaa2bbf06011c8c46620876cab32e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    binddn: builtins.str,
    bindpass: builtins.str,
    allowed_managed_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_response_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_request_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_non_hmac_response_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    certificate: typing.Optional[builtins.str] = None,
    client_tls_cert: typing.Optional[builtins.str] = None,
    client_tls_key: typing.Optional[builtins.str] = None,
    connection_timeout: typing.Optional[jsii.Number] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    delegated_auth_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_entropy_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    force_no_cache: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_key: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    listing_visibility: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    passthrough_request_headers: typing.Optional[typing.Sequence[builtins.str]] = None,
    password_policy: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    plugin_version: typing.Optional[builtins.str] = None,
    request_timeout: typing.Optional[jsii.Number] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    schema: typing.Optional[builtins.str] = None,
    seal_wrap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    skip_static_role_import_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    upndomain: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    userattr: typing.Optional[builtins.str] = None,
    userdn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
