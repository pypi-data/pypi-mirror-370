r'''
# `vault_ad_secret_backend`

Refer to the Terraform Registry for docs: [`vault_ad_secret_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend).
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


class AdSecretBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.adSecretBackend.AdSecretBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend vault_ad_secret_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        binddn: builtins.str,
        bindpass: builtins.str,
        anonymous_group_search: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backend: typing.Optional[builtins.str] = None,
        case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        certificate: typing.Optional[builtins.str] = None,
        client_tls_cert: typing.Optional[builtins.str] = None,
        client_tls_key: typing.Optional[builtins.str] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        groupattr: typing.Optional[builtins.str] = None,
        groupdn: typing.Optional[builtins.str] = None,
        groupfilter: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_rotation_tolerance: typing.Optional[jsii.Number] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        password_policy: typing.Optional[builtins.str] = None,
        request_timeout: typing.Optional[jsii.Number] = None,
        starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_max_version: typing.Optional[builtins.str] = None,
        tls_min_version: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        upndomain: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        use_pre111_group_cn_behavior: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        userattr: typing.Optional[builtins.str] = None,
        userdn: typing.Optional[builtins.str] = None,
        use_token_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend vault_ad_secret_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param binddn: Distinguished name of object to bind when performing user and group search. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#binddn AdSecretBackend#binddn}
        :param bindpass: LDAP password for searching for the user DN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#bindpass AdSecretBackend#bindpass}
        :param anonymous_group_search: Use anonymous binds when performing LDAP group searches (if true the initial credentials will still be used for the initial connection test). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#anonymous_group_search AdSecretBackend#anonymous_group_search}
        :param backend: The mount path for a backend, for example, the path given in "$ vault auth enable -path=my-ad ad". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#backend AdSecretBackend#backend}
        :param case_sensitive_names: If true, case sensitivity will be used when comparing usernames and groups for matching policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#case_sensitive_names AdSecretBackend#case_sensitive_names}
        :param certificate: CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#certificate AdSecretBackend#certificate}
        :param client_tls_cert: Client certificate to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#client_tls_cert AdSecretBackend#client_tls_cert}
        :param client_tls_key: Client certificate key to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#client_tls_key AdSecretBackend#client_tls_key}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#default_lease_ttl_seconds AdSecretBackend#default_lease_ttl_seconds}
        :param deny_null_bind: Denies an unauthenticated LDAP bind request if the user's password is empty; defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#deny_null_bind AdSecretBackend#deny_null_bind}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#description AdSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#disable_remount AdSecretBackend#disable_remount}
        :param discoverdn: Use anonymous bind to discover the bind DN of a user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#discoverdn AdSecretBackend#discoverdn}
        :param groupattr: LDAP attribute to follow on objects returned by in order to enumerate user group membership. Examples: "cn" or "memberOf", etc. Default: cn Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupattr AdSecretBackend#groupattr}
        :param groupdn: LDAP search base to use for group membership search (eg: ou=Groups,dc=example,dc=org). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupdn AdSecretBackend#groupdn}
        :param groupfilter: Go template for querying group membership of user. The template can access the following context variables: UserDN, Username Example: (&(objectClass=group)(member:1.2.840.113556.1.4.1941:={{.UserDN}})) Default: (|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}})) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupfilter AdSecretBackend#groupfilter}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#id AdSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param insecure_tls: Skip LDAP server SSL Certificate verification - insecure and not recommended for production use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#insecure_tls AdSecretBackend#insecure_tls}
        :param last_rotation_tolerance: The number of seconds after a Vault rotation where, if Active Directory shows a later rotation, it should be considered out-of-band. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#last_rotation_tolerance AdSecretBackend#last_rotation_tolerance}
        :param local: Mark the secrets engine as local-only. Local engines are not replicated or removed by replication.Tolerance duration to use when checking the last rotation time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#local AdSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#max_lease_ttl_seconds AdSecretBackend#max_lease_ttl_seconds}
        :param max_ttl: In seconds, the maximum password time-to-live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#max_ttl AdSecretBackend#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#namespace AdSecretBackend#namespace}
        :param password_policy: Name of the password policy to use to generate passwords. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#password_policy AdSecretBackend#password_policy}
        :param request_timeout: Timeout, in seconds, for the connection when making requests against the server before returning back an error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#request_timeout AdSecretBackend#request_timeout}
        :param starttls: Issue a StartTLS command after establishing unencrypted connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#starttls AdSecretBackend#starttls}
        :param tls_max_version: Maximum TLS version to use. Accepted values are 'tls10', 'tls11', 'tls12' or 'tls13'. Defaults to 'tls12'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#tls_max_version AdSecretBackend#tls_max_version}
        :param tls_min_version: Minimum TLS version to use. Accepted values are 'tls10', 'tls11', 'tls12' or 'tls13'. Defaults to 'tls12'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#tls_min_version AdSecretBackend#tls_min_version}
        :param ttl: In seconds, the default password time-to-live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#ttl AdSecretBackend#ttl}
        :param upndomain: Enables userPrincipalDomain login with [username]@UPNDomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#upndomain AdSecretBackend#upndomain}
        :param url: LDAP URL to connect to (default: ldap://127.0.0.1). Multiple URLs can be specified by concatenating them with commas; they will be tried in-order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#url AdSecretBackend#url}
        :param use_pre111_group_cn_behavior: In Vault 1.1.1 a fix for handling group CN values of different cases unfortunately introduced a regression that could cause previously defined groups to not be found due to a change in the resulting name. If set true, the pre-1.1.1 behavior for matching group CNs will be used. This is only needed in some upgrade scenarios for backwards compatibility. It is enabled by default if the config is upgraded but disabled by default on new configurations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#use_pre111_group_cn_behavior AdSecretBackend#use_pre111_group_cn_behavior}
        :param userattr: Attribute used for users (default: cn). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#userattr AdSecretBackend#userattr}
        :param userdn: LDAP domain to use for users (eg: ou=People,dc=example,dc=org). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#userdn AdSecretBackend#userdn}
        :param use_token_groups: If true, use the Active Directory tokenGroups constructed attribute of the user to find the group memberships. This will find all security groups including nested ones. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#use_token_groups AdSecretBackend#use_token_groups}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd2df9ce3069a287c5b00f4222737993b920b48d892bd18e90392c72706e643d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AdSecretBackendConfig(
            binddn=binddn,
            bindpass=bindpass,
            anonymous_group_search=anonymous_group_search,
            backend=backend,
            case_sensitive_names=case_sensitive_names,
            certificate=certificate,
            client_tls_cert=client_tls_cert,
            client_tls_key=client_tls_key,
            default_lease_ttl_seconds=default_lease_ttl_seconds,
            deny_null_bind=deny_null_bind,
            description=description,
            disable_remount=disable_remount,
            discoverdn=discoverdn,
            groupattr=groupattr,
            groupdn=groupdn,
            groupfilter=groupfilter,
            id=id,
            insecure_tls=insecure_tls,
            last_rotation_tolerance=last_rotation_tolerance,
            local=local,
            max_lease_ttl_seconds=max_lease_ttl_seconds,
            max_ttl=max_ttl,
            namespace=namespace,
            password_policy=password_policy,
            request_timeout=request_timeout,
            starttls=starttls,
            tls_max_version=tls_max_version,
            tls_min_version=tls_min_version,
            ttl=ttl,
            upndomain=upndomain,
            url=url,
            use_pre111_group_cn_behavior=use_pre111_group_cn_behavior,
            userattr=userattr,
            userdn=userdn,
            use_token_groups=use_token_groups,
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
        '''Generates CDKTF code for importing a AdSecretBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AdSecretBackend to import.
        :param import_from_id: The id of the existing AdSecretBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AdSecretBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fad5271e377fdf84d8c4350a88817b497598395db0b72d13722ff226e7b9b933)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAnonymousGroupSearch")
    def reset_anonymous_group_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnonymousGroupSearch", []))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetCaseSensitiveNames")
    def reset_case_sensitive_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaseSensitiveNames", []))

    @jsii.member(jsii_name="resetCertificate")
    def reset_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificate", []))

    @jsii.member(jsii_name="resetClientTlsCert")
    def reset_client_tls_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientTlsCert", []))

    @jsii.member(jsii_name="resetClientTlsKey")
    def reset_client_tls_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientTlsKey", []))

    @jsii.member(jsii_name="resetDefaultLeaseTtlSeconds")
    def reset_default_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultLeaseTtlSeconds", []))

    @jsii.member(jsii_name="resetDenyNullBind")
    def reset_deny_null_bind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDenyNullBind", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableRemount")
    def reset_disable_remount(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableRemount", []))

    @jsii.member(jsii_name="resetDiscoverdn")
    def reset_discoverdn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiscoverdn", []))

    @jsii.member(jsii_name="resetGroupattr")
    def reset_groupattr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupattr", []))

    @jsii.member(jsii_name="resetGroupdn")
    def reset_groupdn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupdn", []))

    @jsii.member(jsii_name="resetGroupfilter")
    def reset_groupfilter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupfilter", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInsecureTls")
    def reset_insecure_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureTls", []))

    @jsii.member(jsii_name="resetLastRotationTolerance")
    def reset_last_rotation_tolerance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastRotationTolerance", []))

    @jsii.member(jsii_name="resetLocal")
    def reset_local(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocal", []))

    @jsii.member(jsii_name="resetMaxLeaseTtlSeconds")
    def reset_max_lease_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLeaseTtlSeconds", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPasswordPolicy")
    def reset_password_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordPolicy", []))

    @jsii.member(jsii_name="resetRequestTimeout")
    def reset_request_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestTimeout", []))

    @jsii.member(jsii_name="resetStarttls")
    def reset_starttls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStarttls", []))

    @jsii.member(jsii_name="resetTlsMaxVersion")
    def reset_tls_max_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsMaxVersion", []))

    @jsii.member(jsii_name="resetTlsMinVersion")
    def reset_tls_min_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsMinVersion", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetUpndomain")
    def reset_upndomain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpndomain", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUsePre111GroupCnBehavior")
    def reset_use_pre111_group_cn_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsePre111GroupCnBehavior", []))

    @jsii.member(jsii_name="resetUserattr")
    def reset_userattr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserattr", []))

    @jsii.member(jsii_name="resetUserdn")
    def reset_userdn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserdn", []))

    @jsii.member(jsii_name="resetUseTokenGroups")
    def reset_use_token_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseTokenGroups", []))

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
    @jsii.member(jsii_name="anonymousGroupSearchInput")
    def anonymous_group_search_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "anonymousGroupSearchInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="binddnInput")
    def binddn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "binddnInput"))

    @builtins.property
    @jsii.member(jsii_name="bindpassInput")
    def bindpass_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindpassInput"))

    @builtins.property
    @jsii.member(jsii_name="caseSensitiveNamesInput")
    def case_sensitive_names_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "caseSensitiveNamesInput"))

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
    @jsii.member(jsii_name="defaultLeaseTtlSecondsInput")
    def default_lease_ttl_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultLeaseTtlSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="denyNullBindInput")
    def deny_null_bind_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "denyNullBindInput"))

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
    @jsii.member(jsii_name="discoverdnInput")
    def discoverdn_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "discoverdnInput"))

    @builtins.property
    @jsii.member(jsii_name="groupattrInput")
    def groupattr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupattrInput"))

    @builtins.property
    @jsii.member(jsii_name="groupdnInput")
    def groupdn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupdnInput"))

    @builtins.property
    @jsii.member(jsii_name="groupfilterInput")
    def groupfilter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupfilterInput"))

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
    @jsii.member(jsii_name="lastRotationToleranceInput")
    def last_rotation_tolerance_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lastRotationToleranceInput"))

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
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordPolicyInput")
    def password_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="requestTimeoutInput")
    def request_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requestTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="starttlsInput")
    def starttls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "starttlsInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsMaxVersionInput")
    def tls_max_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsMaxVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsMinVersionInput")
    def tls_min_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsMinVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="upndomainInput")
    def upndomain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "upndomainInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="usePre111GroupCnBehaviorInput")
    def use_pre111_group_cn_behavior_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usePre111GroupCnBehaviorInput"))

    @builtins.property
    @jsii.member(jsii_name="userattrInput")
    def userattr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userattrInput"))

    @builtins.property
    @jsii.member(jsii_name="userdnInput")
    def userdn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userdnInput"))

    @builtins.property
    @jsii.member(jsii_name="useTokenGroupsInput")
    def use_token_groups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useTokenGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="anonymousGroupSearch")
    def anonymous_group_search(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "anonymousGroupSearch"))

    @anonymous_group_search.setter
    def anonymous_group_search(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6277baf18e99ab764d98e859458a4f3b9b601aaea09184ac8806910ea8a16330)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anonymousGroupSearch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f0f6da18922d7553f347daedc0d3d834f01528637e7642409aa2ec07c779e1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="binddn")
    def binddn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "binddn"))

    @binddn.setter
    def binddn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__328704423a5bf09ef0a0c53729b1b13689a4925d2966c25a056940197c556e2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "binddn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindpass")
    def bindpass(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindpass"))

    @bindpass.setter
    def bindpass(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b316ca6c9ff6d91719c104f052acceab73caa0f0d05ca1200dba81a0212b0943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindpass", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caseSensitiveNames")
    def case_sensitive_names(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "caseSensitiveNames"))

    @case_sensitive_names.setter
    def case_sensitive_names(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28bc0105a0ecb6d3ef5165871b5655bc61bd171ee05c04c0be07c78b78da0856)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caseSensitiveNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c4f4530fc135296208fa0c4ee7037d4330e042eb3cca3b51c6829d348116645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTlsCert")
    def client_tls_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTlsCert"))

    @client_tls_cert.setter
    def client_tls_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d127776c89914c77f57bce9f5b002dcefaa7ea54f32ff1e27dc5907d50ef82d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTlsCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTlsKey")
    def client_tls_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTlsKey"))

    @client_tls_key.setter
    def client_tls_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e712d279d22c35ce7f49e9740666f88919137032165485098d5d4e6a55bafd56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTlsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultLeaseTtlSeconds")
    def default_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLeaseTtlSeconds"))

    @default_lease_ttl_seconds.setter
    def default_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb988a29d508bc38ca5985456f96f49f3c65fd009cc3bb8c3d3f1cd1596d9783)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="denyNullBind")
    def deny_null_bind(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "denyNullBind"))

    @deny_null_bind.setter
    def deny_null_bind(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1740c6cf8539a08fece7a3c094c47dd9076cfa72119a9eae06953069014246b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "denyNullBind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0248a42290713dcadaa64221c1ca5e07ea59faab75f49242a9401c4e83965988)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d33c66050099da813f3fd288d4f7b5b5b03f7ea4057d7ac4d4c7e8e2abd6fdcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableRemount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="discoverdn")
    def discoverdn(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "discoverdn"))

    @discoverdn.setter
    def discoverdn(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbe2b1dd1879de210151f1c83df4b86a5703454ff6cab2d8be7de209f1062cf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "discoverdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupattr")
    def groupattr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupattr"))

    @groupattr.setter
    def groupattr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09167ac52b96e42b19faa103915cc3d8427c17471f805ffcb056228d2909ccf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupattr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupdn")
    def groupdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupdn"))

    @groupdn.setter
    def groupdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e7a9c7b85961aeba23116d8a16426efd3a82f351c1db338ce7be3e7f543ebb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupfilter")
    def groupfilter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupfilter"))

    @groupfilter.setter
    def groupfilter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae13ee344cc345cc64b4a92382e12c876b697fa785fc77e731f52b14b722a5a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupfilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8af7975084033e80034326a08711e6cd4a4c11f839883206fe87cf025edbf43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__ec642e2cbf19d66636a7c72026f2cb8026005039c3ad0f579b2d70da001d6ed9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastRotationTolerance")
    def last_rotation_tolerance(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lastRotationTolerance"))

    @last_rotation_tolerance.setter
    def last_rotation_tolerance(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04e8067a19bd1abcb702d140b87d3ed0fad5d9c9d395d23b3e4adf4190e2e396)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastRotationTolerance", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__b070aa66392b6f79292156d796955be12f1ec7212556fbd7447f1f3c983f663d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLeaseTtlSeconds")
    def max_lease_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLeaseTtlSeconds"))

    @max_lease_ttl_seconds.setter
    def max_lease_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35ea0339a57d84038877c8d063242b704f553077226ebe2a9f93fec8c77d22f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLeaseTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2542ee8607652113623698c44a6ddbc515dc2f777ba16ec5d505634c829ae9ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b15abb086bbc27b63327ef545123791bf9c992ef4242bebe8dafa07460764e58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordPolicy")
    def password_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordPolicy"))

    @password_policy.setter
    def password_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60897295fd06a12bb34516d7474c025d23460ed3113c072906d27d0d6e41429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestTimeout")
    def request_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "requestTimeout"))

    @request_timeout.setter
    def request_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a735eb556e1cd15ac4d1b426ed56ea658e7a4b8c29b6f3a92d3c64ac7cd5d225)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestTimeout", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__fea1b23e28f79216a218e5ceefe22e612d69d35bfa4f35b5d4a44419db38e449)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "starttls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsMaxVersion")
    def tls_max_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsMaxVersion"))

    @tls_max_version.setter
    def tls_max_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b7185fd67dddb13a8e5b718fc209d5a518f15feda5f09a8931c134e6c47eee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsMaxVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsMinVersion")
    def tls_min_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsMinVersion"))

    @tls_min_version.setter
    def tls_min_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f2612a053eaecec75cb5ababd0f18a1e33afd091832f1020ff7d5a34d32081c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsMinVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dc6821fd5276ea29747117ce4e539a20b3b0a54b87376a1b6e61c83fd2a22f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="upndomain")
    def upndomain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "upndomain"))

    @upndomain.setter
    def upndomain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ac2079f1fdbe887094ee6d8c9e38ccd0e941b5b10303d6e7fcc450ce651340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "upndomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__649f356517da1a00f4b6168f9c13a9d6dfc7b156fe82954d66b4afc51900c1dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usePre111GroupCnBehavior")
    def use_pre111_group_cn_behavior(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usePre111GroupCnBehavior"))

    @use_pre111_group_cn_behavior.setter
    def use_pre111_group_cn_behavior(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25460fb1f6fa6934a28c0fdce6d9ece5f560312bffdf469f83c842aca0341df0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usePre111GroupCnBehavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userattr")
    def userattr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userattr"))

    @userattr.setter
    def userattr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d42df68e6d255bac05991f4c8496703f0a4e2016c259ba41a35d54cde8eb440)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userattr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userdn")
    def userdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userdn"))

    @userdn.setter
    def userdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddea5c9a4fb3e6dd0d7996e6dc7eb8e8089d307f494085dbc4f6b6119385ab9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useTokenGroups")
    def use_token_groups(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useTokenGroups"))

    @use_token_groups.setter
    def use_token_groups(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16c1e623b1cfe9ac5dca50809f8915ea1c0bc891a54d82e58c2d375db0382034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useTokenGroups", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.adSecretBackend.AdSecretBackendConfig",
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
        "anonymous_group_search": "anonymousGroupSearch",
        "backend": "backend",
        "case_sensitive_names": "caseSensitiveNames",
        "certificate": "certificate",
        "client_tls_cert": "clientTlsCert",
        "client_tls_key": "clientTlsKey",
        "default_lease_ttl_seconds": "defaultLeaseTtlSeconds",
        "deny_null_bind": "denyNullBind",
        "description": "description",
        "disable_remount": "disableRemount",
        "discoverdn": "discoverdn",
        "groupattr": "groupattr",
        "groupdn": "groupdn",
        "groupfilter": "groupfilter",
        "id": "id",
        "insecure_tls": "insecureTls",
        "last_rotation_tolerance": "lastRotationTolerance",
        "local": "local",
        "max_lease_ttl_seconds": "maxLeaseTtlSeconds",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "password_policy": "passwordPolicy",
        "request_timeout": "requestTimeout",
        "starttls": "starttls",
        "tls_max_version": "tlsMaxVersion",
        "tls_min_version": "tlsMinVersion",
        "ttl": "ttl",
        "upndomain": "upndomain",
        "url": "url",
        "use_pre111_group_cn_behavior": "usePre111GroupCnBehavior",
        "userattr": "userattr",
        "userdn": "userdn",
        "use_token_groups": "useTokenGroups",
    },
)
class AdSecretBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        anonymous_group_search: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backend: typing.Optional[builtins.str] = None,
        case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        certificate: typing.Optional[builtins.str] = None,
        client_tls_cert: typing.Optional[builtins.str] = None,
        client_tls_key: typing.Optional[builtins.str] = None,
        default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        groupattr: typing.Optional[builtins.str] = None,
        groupdn: typing.Optional[builtins.str] = None,
        groupfilter: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_rotation_tolerance: typing.Optional[jsii.Number] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        password_policy: typing.Optional[builtins.str] = None,
        request_timeout: typing.Optional[jsii.Number] = None,
        starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_max_version: typing.Optional[builtins.str] = None,
        tls_min_version: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        upndomain: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        use_pre111_group_cn_behavior: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        userattr: typing.Optional[builtins.str] = None,
        userdn: typing.Optional[builtins.str] = None,
        use_token_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param binddn: Distinguished name of object to bind when performing user and group search. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#binddn AdSecretBackend#binddn}
        :param bindpass: LDAP password for searching for the user DN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#bindpass AdSecretBackend#bindpass}
        :param anonymous_group_search: Use anonymous binds when performing LDAP group searches (if true the initial credentials will still be used for the initial connection test). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#anonymous_group_search AdSecretBackend#anonymous_group_search}
        :param backend: The mount path for a backend, for example, the path given in "$ vault auth enable -path=my-ad ad". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#backend AdSecretBackend#backend}
        :param case_sensitive_names: If true, case sensitivity will be used when comparing usernames and groups for matching policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#case_sensitive_names AdSecretBackend#case_sensitive_names}
        :param certificate: CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#certificate AdSecretBackend#certificate}
        :param client_tls_cert: Client certificate to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#client_tls_cert AdSecretBackend#client_tls_cert}
        :param client_tls_key: Client certificate key to provide to the LDAP server, must be x509 PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#client_tls_key AdSecretBackend#client_tls_key}
        :param default_lease_ttl_seconds: Default lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#default_lease_ttl_seconds AdSecretBackend#default_lease_ttl_seconds}
        :param deny_null_bind: Denies an unauthenticated LDAP bind request if the user's password is empty; defaults to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#deny_null_bind AdSecretBackend#deny_null_bind}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#description AdSecretBackend#description}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#disable_remount AdSecretBackend#disable_remount}
        :param discoverdn: Use anonymous bind to discover the bind DN of a user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#discoverdn AdSecretBackend#discoverdn}
        :param groupattr: LDAP attribute to follow on objects returned by in order to enumerate user group membership. Examples: "cn" or "memberOf", etc. Default: cn Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupattr AdSecretBackend#groupattr}
        :param groupdn: LDAP search base to use for group membership search (eg: ou=Groups,dc=example,dc=org). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupdn AdSecretBackend#groupdn}
        :param groupfilter: Go template for querying group membership of user. The template can access the following context variables: UserDN, Username Example: (&(objectClass=group)(member:1.2.840.113556.1.4.1941:={{.UserDN}})) Default: (|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}})) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupfilter AdSecretBackend#groupfilter}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#id AdSecretBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param insecure_tls: Skip LDAP server SSL Certificate verification - insecure and not recommended for production use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#insecure_tls AdSecretBackend#insecure_tls}
        :param last_rotation_tolerance: The number of seconds after a Vault rotation where, if Active Directory shows a later rotation, it should be considered out-of-band. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#last_rotation_tolerance AdSecretBackend#last_rotation_tolerance}
        :param local: Mark the secrets engine as local-only. Local engines are not replicated or removed by replication.Tolerance duration to use when checking the last rotation time. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#local AdSecretBackend#local}
        :param max_lease_ttl_seconds: Maximum possible lease duration for secrets in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#max_lease_ttl_seconds AdSecretBackend#max_lease_ttl_seconds}
        :param max_ttl: In seconds, the maximum password time-to-live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#max_ttl AdSecretBackend#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#namespace AdSecretBackend#namespace}
        :param password_policy: Name of the password policy to use to generate passwords. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#password_policy AdSecretBackend#password_policy}
        :param request_timeout: Timeout, in seconds, for the connection when making requests against the server before returning back an error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#request_timeout AdSecretBackend#request_timeout}
        :param starttls: Issue a StartTLS command after establishing unencrypted connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#starttls AdSecretBackend#starttls}
        :param tls_max_version: Maximum TLS version to use. Accepted values are 'tls10', 'tls11', 'tls12' or 'tls13'. Defaults to 'tls12'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#tls_max_version AdSecretBackend#tls_max_version}
        :param tls_min_version: Minimum TLS version to use. Accepted values are 'tls10', 'tls11', 'tls12' or 'tls13'. Defaults to 'tls12'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#tls_min_version AdSecretBackend#tls_min_version}
        :param ttl: In seconds, the default password time-to-live. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#ttl AdSecretBackend#ttl}
        :param upndomain: Enables userPrincipalDomain login with [username]@UPNDomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#upndomain AdSecretBackend#upndomain}
        :param url: LDAP URL to connect to (default: ldap://127.0.0.1). Multiple URLs can be specified by concatenating them with commas; they will be tried in-order. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#url AdSecretBackend#url}
        :param use_pre111_group_cn_behavior: In Vault 1.1.1 a fix for handling group CN values of different cases unfortunately introduced a regression that could cause previously defined groups to not be found due to a change in the resulting name. If set true, the pre-1.1.1 behavior for matching group CNs will be used. This is only needed in some upgrade scenarios for backwards compatibility. It is enabled by default if the config is upgraded but disabled by default on new configurations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#use_pre111_group_cn_behavior AdSecretBackend#use_pre111_group_cn_behavior}
        :param userattr: Attribute used for users (default: cn). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#userattr AdSecretBackend#userattr}
        :param userdn: LDAP domain to use for users (eg: ou=People,dc=example,dc=org). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#userdn AdSecretBackend#userdn}
        :param use_token_groups: If true, use the Active Directory tokenGroups constructed attribute of the user to find the group memberships. This will find all security groups including nested ones. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#use_token_groups AdSecretBackend#use_token_groups}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__552ba90156541d92ac4cfdbdd3f4a46a6448a3312558e138a9c459bc7dcd7ce7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument binddn", value=binddn, expected_type=type_hints["binddn"])
            check_type(argname="argument bindpass", value=bindpass, expected_type=type_hints["bindpass"])
            check_type(argname="argument anonymous_group_search", value=anonymous_group_search, expected_type=type_hints["anonymous_group_search"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument case_sensitive_names", value=case_sensitive_names, expected_type=type_hints["case_sensitive_names"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument client_tls_cert", value=client_tls_cert, expected_type=type_hints["client_tls_cert"])
            check_type(argname="argument client_tls_key", value=client_tls_key, expected_type=type_hints["client_tls_key"])
            check_type(argname="argument default_lease_ttl_seconds", value=default_lease_ttl_seconds, expected_type=type_hints["default_lease_ttl_seconds"])
            check_type(argname="argument deny_null_bind", value=deny_null_bind, expected_type=type_hints["deny_null_bind"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_remount", value=disable_remount, expected_type=type_hints["disable_remount"])
            check_type(argname="argument discoverdn", value=discoverdn, expected_type=type_hints["discoverdn"])
            check_type(argname="argument groupattr", value=groupattr, expected_type=type_hints["groupattr"])
            check_type(argname="argument groupdn", value=groupdn, expected_type=type_hints["groupdn"])
            check_type(argname="argument groupfilter", value=groupfilter, expected_type=type_hints["groupfilter"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument last_rotation_tolerance", value=last_rotation_tolerance, expected_type=type_hints["last_rotation_tolerance"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument max_lease_ttl_seconds", value=max_lease_ttl_seconds, expected_type=type_hints["max_lease_ttl_seconds"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument password_policy", value=password_policy, expected_type=type_hints["password_policy"])
            check_type(argname="argument request_timeout", value=request_timeout, expected_type=type_hints["request_timeout"])
            check_type(argname="argument starttls", value=starttls, expected_type=type_hints["starttls"])
            check_type(argname="argument tls_max_version", value=tls_max_version, expected_type=type_hints["tls_max_version"])
            check_type(argname="argument tls_min_version", value=tls_min_version, expected_type=type_hints["tls_min_version"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument upndomain", value=upndomain, expected_type=type_hints["upndomain"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument use_pre111_group_cn_behavior", value=use_pre111_group_cn_behavior, expected_type=type_hints["use_pre111_group_cn_behavior"])
            check_type(argname="argument userattr", value=userattr, expected_type=type_hints["userattr"])
            check_type(argname="argument userdn", value=userdn, expected_type=type_hints["userdn"])
            check_type(argname="argument use_token_groups", value=use_token_groups, expected_type=type_hints["use_token_groups"])
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
        if anonymous_group_search is not None:
            self._values["anonymous_group_search"] = anonymous_group_search
        if backend is not None:
            self._values["backend"] = backend
        if case_sensitive_names is not None:
            self._values["case_sensitive_names"] = case_sensitive_names
        if certificate is not None:
            self._values["certificate"] = certificate
        if client_tls_cert is not None:
            self._values["client_tls_cert"] = client_tls_cert
        if client_tls_key is not None:
            self._values["client_tls_key"] = client_tls_key
        if default_lease_ttl_seconds is not None:
            self._values["default_lease_ttl_seconds"] = default_lease_ttl_seconds
        if deny_null_bind is not None:
            self._values["deny_null_bind"] = deny_null_bind
        if description is not None:
            self._values["description"] = description
        if disable_remount is not None:
            self._values["disable_remount"] = disable_remount
        if discoverdn is not None:
            self._values["discoverdn"] = discoverdn
        if groupattr is not None:
            self._values["groupattr"] = groupattr
        if groupdn is not None:
            self._values["groupdn"] = groupdn
        if groupfilter is not None:
            self._values["groupfilter"] = groupfilter
        if id is not None:
            self._values["id"] = id
        if insecure_tls is not None:
            self._values["insecure_tls"] = insecure_tls
        if last_rotation_tolerance is not None:
            self._values["last_rotation_tolerance"] = last_rotation_tolerance
        if local is not None:
            self._values["local"] = local
        if max_lease_ttl_seconds is not None:
            self._values["max_lease_ttl_seconds"] = max_lease_ttl_seconds
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if password_policy is not None:
            self._values["password_policy"] = password_policy
        if request_timeout is not None:
            self._values["request_timeout"] = request_timeout
        if starttls is not None:
            self._values["starttls"] = starttls
        if tls_max_version is not None:
            self._values["tls_max_version"] = tls_max_version
        if tls_min_version is not None:
            self._values["tls_min_version"] = tls_min_version
        if ttl is not None:
            self._values["ttl"] = ttl
        if upndomain is not None:
            self._values["upndomain"] = upndomain
        if url is not None:
            self._values["url"] = url
        if use_pre111_group_cn_behavior is not None:
            self._values["use_pre111_group_cn_behavior"] = use_pre111_group_cn_behavior
        if userattr is not None:
            self._values["userattr"] = userattr
        if userdn is not None:
            self._values["userdn"] = userdn
        if use_token_groups is not None:
            self._values["use_token_groups"] = use_token_groups

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#binddn AdSecretBackend#binddn}
        '''
        result = self._values.get("binddn")
        assert result is not None, "Required property 'binddn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bindpass(self) -> builtins.str:
        '''LDAP password for searching for the user DN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#bindpass AdSecretBackend#bindpass}
        '''
        result = self._values.get("bindpass")
        assert result is not None, "Required property 'bindpass' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def anonymous_group_search(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use anonymous binds when performing LDAP group searches (if true the initial credentials will still be used for the initial connection test).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#anonymous_group_search AdSecretBackend#anonymous_group_search}
        '''
        result = self._values.get("anonymous_group_search")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''The mount path for a backend, for example, the path given in "$ vault auth enable -path=my-ad ad".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#backend AdSecretBackend#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def case_sensitive_names(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, case sensitivity will be used when comparing usernames and groups for matching policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#case_sensitive_names AdSecretBackend#case_sensitive_names}
        '''
        result = self._values.get("case_sensitive_names")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def certificate(self) -> typing.Optional[builtins.str]:
        '''CA certificate to use when verifying LDAP server certificate, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#certificate AdSecretBackend#certificate}
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_tls_cert(self) -> typing.Optional[builtins.str]:
        '''Client certificate to provide to the LDAP server, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#client_tls_cert AdSecretBackend#client_tls_cert}
        '''
        result = self._values.get("client_tls_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_tls_key(self) -> typing.Optional[builtins.str]:
        '''Client certificate key to provide to the LDAP server, must be x509 PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#client_tls_key AdSecretBackend#client_tls_key}
        '''
        result = self._values.get("client_tls_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Default lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#default_lease_ttl_seconds AdSecretBackend#default_lease_ttl_seconds}
        '''
        result = self._values.get("default_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deny_null_bind(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Denies an unauthenticated LDAP bind request if the user's password is empty; defaults to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#deny_null_bind AdSecretBackend#deny_null_bind}
        '''
        result = self._values.get("deny_null_bind")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#description AdSecretBackend#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#disable_remount AdSecretBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def discoverdn(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use anonymous bind to discover the bind DN of a user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#discoverdn AdSecretBackend#discoverdn}
        '''
        result = self._values.get("discoverdn")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def groupattr(self) -> typing.Optional[builtins.str]:
        '''LDAP attribute to follow on objects returned by  in order to enumerate user group membership.

        Examples: "cn" or "memberOf", etc. Default: cn

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupattr AdSecretBackend#groupattr}
        '''
        result = self._values.get("groupattr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groupdn(self) -> typing.Optional[builtins.str]:
        '''LDAP search base to use for group membership search (eg: ou=Groups,dc=example,dc=org).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupdn AdSecretBackend#groupdn}
        '''
        result = self._values.get("groupdn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groupfilter(self) -> typing.Optional[builtins.str]:
        '''Go template for querying group membership of user.

        The template can access the following context variables: UserDN, Username Example: (&(objectClass=group)(member:1.2.840.113556.1.4.1941:={{.UserDN}})) Default: (|(memberUid={{.Username}})(member={{.UserDN}})(uniqueMember={{.UserDN}}))

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#groupfilter AdSecretBackend#groupfilter}
        '''
        result = self._values.get("groupfilter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#id AdSecretBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Skip LDAP server SSL Certificate verification - insecure and not recommended for production use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#insecure_tls AdSecretBackend#insecure_tls}
        '''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def last_rotation_tolerance(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds after a Vault rotation where, if Active Directory shows a later rotation, it should be considered out-of-band.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#last_rotation_tolerance AdSecretBackend#last_rotation_tolerance}
        '''
        result = self._values.get("last_rotation_tolerance")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Mark the secrets engine as local-only.

        Local engines are not replicated or removed by replication.Tolerance duration to use when checking the last rotation time.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#local AdSecretBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_lease_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Maximum possible lease duration for secrets in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#max_lease_ttl_seconds AdSecretBackend#max_lease_ttl_seconds}
        '''
        result = self._values.get("max_lease_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''In seconds, the maximum password time-to-live.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#max_ttl AdSecretBackend#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#namespace AdSecretBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_policy(self) -> typing.Optional[builtins.str]:
        '''Name of the password policy to use to generate passwords.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#password_policy AdSecretBackend#password_policy}
        '''
        result = self._values.get("password_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_timeout(self) -> typing.Optional[jsii.Number]:
        '''Timeout, in seconds, for the connection when making requests against the server before returning back an error.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#request_timeout AdSecretBackend#request_timeout}
        '''
        result = self._values.get("request_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def starttls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Issue a StartTLS command after establishing unencrypted connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#starttls AdSecretBackend#starttls}
        '''
        result = self._values.get("starttls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_max_version(self) -> typing.Optional[builtins.str]:
        '''Maximum TLS version to use. Accepted values are 'tls10', 'tls11', 'tls12' or 'tls13'. Defaults to 'tls12'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#tls_max_version AdSecretBackend#tls_max_version}
        '''
        result = self._values.get("tls_max_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_min_version(self) -> typing.Optional[builtins.str]:
        '''Minimum TLS version to use. Accepted values are 'tls10', 'tls11', 'tls12' or 'tls13'. Defaults to 'tls12'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#tls_min_version AdSecretBackend#tls_min_version}
        '''
        result = self._values.get("tls_min_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''In seconds, the default password time-to-live.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#ttl AdSecretBackend#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def upndomain(self) -> typing.Optional[builtins.str]:
        '''Enables userPrincipalDomain login with [username]@UPNDomain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#upndomain AdSecretBackend#upndomain}
        '''
        result = self._values.get("upndomain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''LDAP URL to connect to (default: ldap://127.0.0.1). Multiple URLs can be specified by concatenating them with commas; they will be tried in-order.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#url AdSecretBackend#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_pre111_group_cn_behavior(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''In Vault 1.1.1 a fix for handling group CN values of different cases unfortunately introduced a regression that could cause previously defined groups to not be found due to a change in the resulting name. If set true, the pre-1.1.1 behavior for matching group CNs will be used. This is only needed in some upgrade scenarios for backwards compatibility. It is enabled by default if the config is upgraded but disabled by default on new configurations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#use_pre111_group_cn_behavior AdSecretBackend#use_pre111_group_cn_behavior}
        '''
        result = self._values.get("use_pre111_group_cn_behavior")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def userattr(self) -> typing.Optional[builtins.str]:
        '''Attribute used for users (default: cn).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#userattr AdSecretBackend#userattr}
        '''
        result = self._values.get("userattr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userdn(self) -> typing.Optional[builtins.str]:
        '''LDAP domain to use for users (eg: ou=People,dc=example,dc=org).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#userdn AdSecretBackend#userdn}
        '''
        result = self._values.get("userdn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_token_groups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, use the Active Directory tokenGroups constructed attribute of the user to find the group memberships.

        This will find all security groups including nested ones.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ad_secret_backend#use_token_groups AdSecretBackend#use_token_groups}
        '''
        result = self._values.get("use_token_groups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AdSecretBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AdSecretBackend",
    "AdSecretBackendConfig",
]

publication.publish()

def _typecheckingstub__bd2df9ce3069a287c5b00f4222737993b920b48d892bd18e90392c72706e643d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    binddn: builtins.str,
    bindpass: builtins.str,
    anonymous_group_search: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backend: typing.Optional[builtins.str] = None,
    case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    certificate: typing.Optional[builtins.str] = None,
    client_tls_cert: typing.Optional[builtins.str] = None,
    client_tls_key: typing.Optional[builtins.str] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    groupattr: typing.Optional[builtins.str] = None,
    groupdn: typing.Optional[builtins.str] = None,
    groupfilter: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_rotation_tolerance: typing.Optional[jsii.Number] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    password_policy: typing.Optional[builtins.str] = None,
    request_timeout: typing.Optional[jsii.Number] = None,
    starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_max_version: typing.Optional[builtins.str] = None,
    tls_min_version: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    upndomain: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    use_pre111_group_cn_behavior: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    userattr: typing.Optional[builtins.str] = None,
    userdn: typing.Optional[builtins.str] = None,
    use_token_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__fad5271e377fdf84d8c4350a88817b497598395db0b72d13722ff226e7b9b933(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6277baf18e99ab764d98e859458a4f3b9b601aaea09184ac8806910ea8a16330(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f0f6da18922d7553f347daedc0d3d834f01528637e7642409aa2ec07c779e1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__328704423a5bf09ef0a0c53729b1b13689a4925d2966c25a056940197c556e2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b316ca6c9ff6d91719c104f052acceab73caa0f0d05ca1200dba81a0212b0943(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28bc0105a0ecb6d3ef5165871b5655bc61bd171ee05c04c0be07c78b78da0856(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c4f4530fc135296208fa0c4ee7037d4330e042eb3cca3b51c6829d348116645(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d127776c89914c77f57bce9f5b002dcefaa7ea54f32ff1e27dc5907d50ef82d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e712d279d22c35ce7f49e9740666f88919137032165485098d5d4e6a55bafd56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb988a29d508bc38ca5985456f96f49f3c65fd009cc3bb8c3d3f1cd1596d9783(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1740c6cf8539a08fece7a3c094c47dd9076cfa72119a9eae06953069014246b8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0248a42290713dcadaa64221c1ca5e07ea59faab75f49242a9401c4e83965988(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d33c66050099da813f3fd288d4f7b5b5b03f7ea4057d7ac4d4c7e8e2abd6fdcf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbe2b1dd1879de210151f1c83df4b86a5703454ff6cab2d8be7de209f1062cf4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09167ac52b96e42b19faa103915cc3d8427c17471f805ffcb056228d2909ccf8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7a9c7b85961aeba23116d8a16426efd3a82f351c1db338ce7be3e7f543ebb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae13ee344cc345cc64b4a92382e12c876b697fa785fc77e731f52b14b722a5a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8af7975084033e80034326a08711e6cd4a4c11f839883206fe87cf025edbf43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec642e2cbf19d66636a7c72026f2cb8026005039c3ad0f579b2d70da001d6ed9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04e8067a19bd1abcb702d140b87d3ed0fad5d9c9d395d23b3e4adf4190e2e396(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b070aa66392b6f79292156d796955be12f1ec7212556fbd7447f1f3c983f663d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ea0339a57d84038877c8d063242b704f553077226ebe2a9f93fec8c77d22f7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2542ee8607652113623698c44a6ddbc515dc2f777ba16ec5d505634c829ae9ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b15abb086bbc27b63327ef545123791bf9c992ef4242bebe8dafa07460764e58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60897295fd06a12bb34516d7474c025d23460ed3113c072906d27d0d6e41429(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a735eb556e1cd15ac4d1b426ed56ea658e7a4b8c29b6f3a92d3c64ac7cd5d225(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fea1b23e28f79216a218e5ceefe22e612d69d35bfa4f35b5d4a44419db38e449(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b7185fd67dddb13a8e5b718fc209d5a518f15feda5f09a8931c134e6c47eee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f2612a053eaecec75cb5ababd0f18a1e33afd091832f1020ff7d5a34d32081c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dc6821fd5276ea29747117ce4e539a20b3b0a54b87376a1b6e61c83fd2a22f1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ac2079f1fdbe887094ee6d8c9e38ccd0e941b5b10303d6e7fcc450ce651340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__649f356517da1a00f4b6168f9c13a9d6dfc7b156fe82954d66b4afc51900c1dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25460fb1f6fa6934a28c0fdce6d9ece5f560312bffdf469f83c842aca0341df0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d42df68e6d255bac05991f4c8496703f0a4e2016c259ba41a35d54cde8eb440(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddea5c9a4fb3e6dd0d7996e6dc7eb8e8089d307f494085dbc4f6b6119385ab9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16c1e623b1cfe9ac5dca50809f8915ea1c0bc891a54d82e58c2d375db0382034(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__552ba90156541d92ac4cfdbdd3f4a46a6448a3312558e138a9c459bc7dcd7ce7(
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
    anonymous_group_search: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backend: typing.Optional[builtins.str] = None,
    case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    certificate: typing.Optional[builtins.str] = None,
    client_tls_cert: typing.Optional[builtins.str] = None,
    client_tls_key: typing.Optional[builtins.str] = None,
    default_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    groupattr: typing.Optional[builtins.str] = None,
    groupdn: typing.Optional[builtins.str] = None,
    groupfilter: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_rotation_tolerance: typing.Optional[jsii.Number] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_lease_ttl_seconds: typing.Optional[jsii.Number] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    password_policy: typing.Optional[builtins.str] = None,
    request_timeout: typing.Optional[jsii.Number] = None,
    starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_max_version: typing.Optional[builtins.str] = None,
    tls_min_version: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    upndomain: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    use_pre111_group_cn_behavior: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    userattr: typing.Optional[builtins.str] = None,
    userdn: typing.Optional[builtins.str] = None,
    use_token_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
