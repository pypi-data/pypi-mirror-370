r'''
# `vault_ldap_auth_backend`

Refer to the Terraform Registry for docs: [`vault_ldap_auth_backend`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend).
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


class LdapAuthBackend(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.ldapAuthBackend.LdapAuthBackend",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend vault_ldap_auth_backend}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        url: builtins.str,
        binddn: typing.Optional[builtins.str] = None,
        bindpass: typing.Optional[builtins.str] = None,
        case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        certificate: typing.Optional[builtins.str] = None,
        client_tls_cert: typing.Optional[builtins.str] = None,
        client_tls_key: typing.Optional[builtins.str] = None,
        connection_timeout: typing.Optional[jsii.Number] = None,
        deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        groupattr: typing.Optional[builtins.str] = None,
        groupdn: typing.Optional[builtins.str] = None,
        groupfilter: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_page_size: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_max_version: typing.Optional[builtins.str] = None,
        tls_min_version: typing.Optional[builtins.str] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
        upndomain: typing.Optional[builtins.str] = None,
        userattr: typing.Optional[builtins.str] = None,
        userdn: typing.Optional[builtins.str] = None,
        userfilter: typing.Optional[builtins.str] = None,
        username_as_alias: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_token_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend vault_ldap_auth_backend} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#url LdapAuthBackend#url}.
        :param binddn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#binddn LdapAuthBackend#binddn}.
        :param bindpass: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#bindpass LdapAuthBackend#bindpass}.
        :param case_sensitive_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#case_sensitive_names LdapAuthBackend#case_sensitive_names}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#certificate LdapAuthBackend#certificate}.
        :param client_tls_cert: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#client_tls_cert LdapAuthBackend#client_tls_cert}.
        :param client_tls_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#client_tls_key LdapAuthBackend#client_tls_key}.
        :param connection_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#connection_timeout LdapAuthBackend#connection_timeout}.
        :param deny_null_bind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#deny_null_bind LdapAuthBackend#deny_null_bind}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#description LdapAuthBackend#description}.
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#disable_automated_rotation LdapAuthBackend#disable_automated_rotation}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#disable_remount LdapAuthBackend#disable_remount}
        :param discoverdn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#discoverdn LdapAuthBackend#discoverdn}.
        :param groupattr: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupattr LdapAuthBackend#groupattr}.
        :param groupdn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupdn LdapAuthBackend#groupdn}.
        :param groupfilter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupfilter LdapAuthBackend#groupfilter}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#id LdapAuthBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param insecure_tls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#insecure_tls LdapAuthBackend#insecure_tls}.
        :param local: Specifies if the auth method is local only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#local LdapAuthBackend#local}
        :param max_page_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#max_page_size LdapAuthBackend#max_page_size}.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#namespace LdapAuthBackend#namespace}
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#path LdapAuthBackend#path}.
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_period LdapAuthBackend#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_schedule LdapAuthBackend#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_window LdapAuthBackend#rotation_window}
        :param starttls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#starttls LdapAuthBackend#starttls}.
        :param tls_max_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#tls_max_version LdapAuthBackend#tls_max_version}.
        :param tls_min_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#tls_min_version LdapAuthBackend#tls_min_version}.
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_bound_cidrs LdapAuthBackend#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_explicit_max_ttl LdapAuthBackend#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_max_ttl LdapAuthBackend#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_no_default_policy LdapAuthBackend#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_num_uses LdapAuthBackend#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_period LdapAuthBackend#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_policies LdapAuthBackend#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_ttl LdapAuthBackend#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_type LdapAuthBackend#token_type}
        :param upndomain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#upndomain LdapAuthBackend#upndomain}.
        :param userattr: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userattr LdapAuthBackend#userattr}.
        :param userdn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userdn LdapAuthBackend#userdn}.
        :param userfilter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userfilter LdapAuthBackend#userfilter}.
        :param username_as_alias: Force the auth method to use the username passed by the user as the alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#username_as_alias LdapAuthBackend#username_as_alias}
        :param use_token_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#use_token_groups LdapAuthBackend#use_token_groups}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a612673267da58e0983ae26d9e157f12ea35bc4392a1520213eaf5f3d7b9376)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = LdapAuthBackendConfig(
            url=url,
            binddn=binddn,
            bindpass=bindpass,
            case_sensitive_names=case_sensitive_names,
            certificate=certificate,
            client_tls_cert=client_tls_cert,
            client_tls_key=client_tls_key,
            connection_timeout=connection_timeout,
            deny_null_bind=deny_null_bind,
            description=description,
            disable_automated_rotation=disable_automated_rotation,
            disable_remount=disable_remount,
            discoverdn=discoverdn,
            groupattr=groupattr,
            groupdn=groupdn,
            groupfilter=groupfilter,
            id=id,
            insecure_tls=insecure_tls,
            local=local,
            max_page_size=max_page_size,
            namespace=namespace,
            path=path,
            rotation_period=rotation_period,
            rotation_schedule=rotation_schedule,
            rotation_window=rotation_window,
            starttls=starttls,
            tls_max_version=tls_max_version,
            tls_min_version=tls_min_version,
            token_bound_cidrs=token_bound_cidrs,
            token_explicit_max_ttl=token_explicit_max_ttl,
            token_max_ttl=token_max_ttl,
            token_no_default_policy=token_no_default_policy,
            token_num_uses=token_num_uses,
            token_period=token_period,
            token_policies=token_policies,
            token_ttl=token_ttl,
            token_type=token_type,
            upndomain=upndomain,
            userattr=userattr,
            userdn=userdn,
            userfilter=userfilter,
            username_as_alias=username_as_alias,
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
        '''Generates CDKTF code for importing a LdapAuthBackend resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LdapAuthBackend to import.
        :param import_from_id: The id of the existing LdapAuthBackend that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LdapAuthBackend to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6be3b6d915ff534f5e5b2045212ade7e718fad2abee62280b25dc98ab82222d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBinddn")
    def reset_binddn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBinddn", []))

    @jsii.member(jsii_name="resetBindpass")
    def reset_bindpass(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBindpass", []))

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

    @jsii.member(jsii_name="resetConnectionTimeout")
    def reset_connection_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionTimeout", []))

    @jsii.member(jsii_name="resetDenyNullBind")
    def reset_deny_null_bind(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDenyNullBind", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDisableAutomatedRotation")
    def reset_disable_automated_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAutomatedRotation", []))

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

    @jsii.member(jsii_name="resetLocal")
    def reset_local(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocal", []))

    @jsii.member(jsii_name="resetMaxPageSize")
    def reset_max_page_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPageSize", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetRotationPeriod")
    def reset_rotation_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationPeriod", []))

    @jsii.member(jsii_name="resetRotationSchedule")
    def reset_rotation_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationSchedule", []))

    @jsii.member(jsii_name="resetRotationWindow")
    def reset_rotation_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationWindow", []))

    @jsii.member(jsii_name="resetStarttls")
    def reset_starttls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStarttls", []))

    @jsii.member(jsii_name="resetTlsMaxVersion")
    def reset_tls_max_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsMaxVersion", []))

    @jsii.member(jsii_name="resetTlsMinVersion")
    def reset_tls_min_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsMinVersion", []))

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

    @jsii.member(jsii_name="resetUpndomain")
    def reset_upndomain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpndomain", []))

    @jsii.member(jsii_name="resetUserattr")
    def reset_userattr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserattr", []))

    @jsii.member(jsii_name="resetUserdn")
    def reset_userdn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserdn", []))

    @jsii.member(jsii_name="resetUserfilter")
    def reset_userfilter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserfilter", []))

    @jsii.member(jsii_name="resetUsernameAsAlias")
    def reset_username_as_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameAsAlias", []))

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
    @jsii.member(jsii_name="accessor")
    def accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessor"))

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
    @jsii.member(jsii_name="connectionTimeoutInput")
    def connection_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectionTimeoutInput"))

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
    @jsii.member(jsii_name="localInput")
    def local_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "localInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPageSizeInput")
    def max_page_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPageSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

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
    @jsii.member(jsii_name="userfilterInput")
    def userfilter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userfilterInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameAsAliasInput")
    def username_as_alias_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "usernameAsAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="useTokenGroupsInput")
    def use_token_groups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useTokenGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="binddn")
    def binddn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "binddn"))

    @binddn.setter
    def binddn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e93055c1d2e6c5118bc1f6a4df2641cf9cb4abe0a984493dc74f58fbcdedf7db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "binddn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindpass")
    def bindpass(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindpass"))

    @bindpass.setter
    def bindpass(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef510a9242088f894c1ec1952646066e5c2132b270ff605597df1ac3c09e7cb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c7f01dfa54afcf9d910ee4243ac57e1e07503efaaecb936f6995f4460ee0865)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caseSensitiveNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificate"))

    @certificate.setter
    def certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e2f99f0507f688b7ec5e25dca193371f76f28022f35a2088ce23423969975a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTlsCert")
    def client_tls_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTlsCert"))

    @client_tls_cert.setter
    def client_tls_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd7d8d30a8eb8eac72cebe464afd6f7c5751eee7c0d59def5a700e50025ee7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTlsCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientTlsKey")
    def client_tls_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientTlsKey"))

    @client_tls_key.setter
    def client_tls_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2fbbb64188c938486024f9278195a88ca96758b2ed40c04b15d12c8dd041d2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientTlsKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionTimeout")
    def connection_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectionTimeout"))

    @connection_timeout.setter
    def connection_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a48d4e45458d7e90db45b9d9591a7a8decba4d1f87873aa6934f736d1f5cf4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionTimeout", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e4ebeb54aecc054bc41ec0016e25825618a06e1212e05becc05498f0fae978c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "denyNullBind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9facf239ed05d82f4af5f9aeb10f82c9098e3e140f5c8d149fbfbbbc91a5b606)
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
            type_hints = typing.get_type_hints(_typecheckingstub__36467a86e3e999f43345e4c7c00ea74707736fb58298b7d62bf90972fa0913df)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e47f01de34a7c90fe8b2c56a3e3763a6c2fc2e4d0e73ce142b676a56e3fd7b4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e84d029344e3d8deb8632b394d9429201cb77e65df528c131ec0c782cc6fb11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "discoverdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupattr")
    def groupattr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupattr"))

    @groupattr.setter
    def groupattr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187cf57576ab6a599efa91091cb3fd4b7fedcc3b7fbaf57805e04a7ec92d9301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupattr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupdn")
    def groupdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupdn"))

    @groupdn.setter
    def groupdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a35e7fbe545b448ae9da8cb88041aa7404dd1dd6fb6d56421ea9850da5501995)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupfilter")
    def groupfilter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupfilter"))

    @groupfilter.setter
    def groupfilter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a5329f611b182ecb4f785156bf8dea9e22a61ce93d2e82031e9100498f15bab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupfilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87b8176f32ebb58de39a9015160d74d19c57007739d2383668af94df52874b0f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__81d2cbf8ef2d7a6aa633d0c5eacb49b5f07cc39ca34c660e751e4884fdac8c41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__b434480f8b73111bda3fc4cf837b5fd1cd00ab140172f2f4e644ca6358e5c5a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPageSize")
    def max_page_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPageSize"))

    @max_page_size.setter
    def max_page_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__773de9ff50db0622cf5dcdd12be85598de57687665861f5bf32357c92251876a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPageSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b17d3e69fc2b78add5dd8c75c6843f1bf4eabd99c9c7348250891060c7a1d71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e0655a4e0b333faf630fe4e93efa6664aa19e1719f8a1a3642724489e8479b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationPeriod")
    def rotation_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationPeriod"))

    @rotation_period.setter
    def rotation_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9969b9c8658ac741d4921a2e31dc84c2c03553e8f18676f4142dad69ab27296b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationSchedule")
    def rotation_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationSchedule"))

    @rotation_schedule.setter
    def rotation_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a35d50dd57a60f36792e5a7beef5a205233b9bacf75ec700f203b0ca48dbe545)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationWindow")
    def rotation_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationWindow"))

    @rotation_window.setter
    def rotation_window(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3439f57a7851509d750fdf2b2b1a1e0cea8a258450c6c674a28e5f2a3e7892a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationWindow", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e9cfd51073a9e4c2422ef1ebeefab2bdc20c765b3d51a83560d649b7f45128ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "starttls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsMaxVersion")
    def tls_max_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsMaxVersion"))

    @tls_max_version.setter
    def tls_max_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8409a49aef77db5baf67b37964898f336e8c3b3d7a6d755d31e993e356d356b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsMaxVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsMinVersion")
    def tls_min_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsMinVersion"))

    @tls_min_version.setter
    def tls_min_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88df194a6b69e666bad7a8581daa429c1b4b3b4fb7951b388129c69cdfc1bd7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsMinVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenBoundCidrs")
    def token_bound_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenBoundCidrs"))

    @token_bound_cidrs.setter
    def token_bound_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__036a5228922a1f1323fed2fcfbf31b19b3a0ba932f539f173677384ab6210f56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenBoundCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenExplicitMaxTtl")
    def token_explicit_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenExplicitMaxTtl"))

    @token_explicit_max_ttl.setter
    def token_explicit_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7721bbfcd12f9c0c564254b761020d6dc6353ab9dba683ed27174a4d6585f9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenExplicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtl")
    def token_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenMaxTtl"))

    @token_max_ttl.setter
    def token_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8813e27a0a309c62361d82c80bcf395fbd32ba347adb07ec7c5059ca5d52cc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a88da75192ccb8179509d9c84f6b1840f06a5b7afebc3cbd3c39fb86e2c0c27e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNoDefaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNumUses")
    def token_num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenNumUses"))

    @token_num_uses.setter
    def token_num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56c2f54e4daa2b01329735455e33e71f1335b2856e7cee868b03f03718b9a61d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNumUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPeriod")
    def token_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenPeriod"))

    @token_period.setter
    def token_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__322754212e722140f8bdca21385f33ffc274df9ed067d0ddbea253f0396b0f7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPolicies")
    def token_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenPolicies"))

    @token_policies.setter
    def token_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__addd15f899b7228f5deabf2438a6220c2a9d0478645bb557b036682df5b46349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenTtl")
    def token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenTtl"))

    @token_ttl.setter
    def token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09095ab39d618c7e916ef86bae54bc3cfcdf5b36e25d2c190ca3b18e461a3e31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenType")
    def token_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenType"))

    @token_type.setter
    def token_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3e02b67eb652b570c0fa763f887517d3e45a76daa2104fac56de833b1ec67dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="upndomain")
    def upndomain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "upndomain"))

    @upndomain.setter
    def upndomain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a509fb0183c2ff008bf6b7115ff6135af5483d431d34a3fcfc8dfcd7e4b52ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "upndomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea1222c78da72f429739b08c6ee8c5db2a90f09efe46c41b97ff3703cb64b95c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userattr")
    def userattr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userattr"))

    @userattr.setter
    def userattr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__652ef4a66b6b54f1804a2dcce50681e1588a086093c00d6f62b3845b1aa2c63b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userattr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userdn")
    def userdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userdn"))

    @userdn.setter
    def userdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__164a9ebc2b060c0790bcb389b7eb55385994bbc7eb0406d34d4c33f95f9c793e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userfilter")
    def userfilter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userfilter"))

    @userfilter.setter
    def userfilter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a6e4cc0e2779124c966e198049a26ef64abc5dc1ee5fa0b127add337eb423a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userfilter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameAsAlias")
    def username_as_alias(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "usernameAsAlias"))

    @username_as_alias.setter
    def username_as_alias(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d9f10996ec9e830811da9934b7fe2a54a33dd003365897f9fe839d7724b2860)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameAsAlias", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__838fc6f04d9bca7c8cb6c7f34964f3c140c64b2f2773a2b0960cbdd2ee9780c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useTokenGroups", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.ldapAuthBackend.LdapAuthBackendConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "url": "url",
        "binddn": "binddn",
        "bindpass": "bindpass",
        "case_sensitive_names": "caseSensitiveNames",
        "certificate": "certificate",
        "client_tls_cert": "clientTlsCert",
        "client_tls_key": "clientTlsKey",
        "connection_timeout": "connectionTimeout",
        "deny_null_bind": "denyNullBind",
        "description": "description",
        "disable_automated_rotation": "disableAutomatedRotation",
        "disable_remount": "disableRemount",
        "discoverdn": "discoverdn",
        "groupattr": "groupattr",
        "groupdn": "groupdn",
        "groupfilter": "groupfilter",
        "id": "id",
        "insecure_tls": "insecureTls",
        "local": "local",
        "max_page_size": "maxPageSize",
        "namespace": "namespace",
        "path": "path",
        "rotation_period": "rotationPeriod",
        "rotation_schedule": "rotationSchedule",
        "rotation_window": "rotationWindow",
        "starttls": "starttls",
        "tls_max_version": "tlsMaxVersion",
        "tls_min_version": "tlsMinVersion",
        "token_bound_cidrs": "tokenBoundCidrs",
        "token_explicit_max_ttl": "tokenExplicitMaxTtl",
        "token_max_ttl": "tokenMaxTtl",
        "token_no_default_policy": "tokenNoDefaultPolicy",
        "token_num_uses": "tokenNumUses",
        "token_period": "tokenPeriod",
        "token_policies": "tokenPolicies",
        "token_ttl": "tokenTtl",
        "token_type": "tokenType",
        "upndomain": "upndomain",
        "userattr": "userattr",
        "userdn": "userdn",
        "userfilter": "userfilter",
        "username_as_alias": "usernameAsAlias",
        "use_token_groups": "useTokenGroups",
    },
)
class LdapAuthBackendConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        url: builtins.str,
        binddn: typing.Optional[builtins.str] = None,
        bindpass: typing.Optional[builtins.str] = None,
        case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        certificate: typing.Optional[builtins.str] = None,
        client_tls_cert: typing.Optional[builtins.str] = None,
        client_tls_key: typing.Optional[builtins.str] = None,
        connection_timeout: typing.Optional[jsii.Number] = None,
        deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        groupattr: typing.Optional[builtins.str] = None,
        groupdn: typing.Optional[builtins.str] = None,
        groupfilter: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_page_size: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_max_version: typing.Optional[builtins.str] = None,
        tls_min_version: typing.Optional[builtins.str] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
        upndomain: typing.Optional[builtins.str] = None,
        userattr: typing.Optional[builtins.str] = None,
        userdn: typing.Optional[builtins.str] = None,
        userfilter: typing.Optional[builtins.str] = None,
        username_as_alias: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#url LdapAuthBackend#url}.
        :param binddn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#binddn LdapAuthBackend#binddn}.
        :param bindpass: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#bindpass LdapAuthBackend#bindpass}.
        :param case_sensitive_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#case_sensitive_names LdapAuthBackend#case_sensitive_names}.
        :param certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#certificate LdapAuthBackend#certificate}.
        :param client_tls_cert: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#client_tls_cert LdapAuthBackend#client_tls_cert}.
        :param client_tls_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#client_tls_key LdapAuthBackend#client_tls_key}.
        :param connection_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#connection_timeout LdapAuthBackend#connection_timeout}.
        :param deny_null_bind: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#deny_null_bind LdapAuthBackend#deny_null_bind}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#description LdapAuthBackend#description}.
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#disable_automated_rotation LdapAuthBackend#disable_automated_rotation}
        :param disable_remount: If set, opts out of mount migration on path updates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#disable_remount LdapAuthBackend#disable_remount}
        :param discoverdn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#discoverdn LdapAuthBackend#discoverdn}.
        :param groupattr: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupattr LdapAuthBackend#groupattr}.
        :param groupdn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupdn LdapAuthBackend#groupdn}.
        :param groupfilter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupfilter LdapAuthBackend#groupfilter}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#id LdapAuthBackend#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param insecure_tls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#insecure_tls LdapAuthBackend#insecure_tls}.
        :param local: Specifies if the auth method is local only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#local LdapAuthBackend#local}
        :param max_page_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#max_page_size LdapAuthBackend#max_page_size}.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#namespace LdapAuthBackend#namespace}
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#path LdapAuthBackend#path}.
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_period LdapAuthBackend#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_schedule LdapAuthBackend#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_window LdapAuthBackend#rotation_window}
        :param starttls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#starttls LdapAuthBackend#starttls}.
        :param tls_max_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#tls_max_version LdapAuthBackend#tls_max_version}.
        :param tls_min_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#tls_min_version LdapAuthBackend#tls_min_version}.
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_bound_cidrs LdapAuthBackend#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_explicit_max_ttl LdapAuthBackend#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_max_ttl LdapAuthBackend#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_no_default_policy LdapAuthBackend#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_num_uses LdapAuthBackend#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_period LdapAuthBackend#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_policies LdapAuthBackend#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_ttl LdapAuthBackend#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_type LdapAuthBackend#token_type}
        :param upndomain: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#upndomain LdapAuthBackend#upndomain}.
        :param userattr: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userattr LdapAuthBackend#userattr}.
        :param userdn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userdn LdapAuthBackend#userdn}.
        :param userfilter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userfilter LdapAuthBackend#userfilter}.
        :param username_as_alias: Force the auth method to use the username passed by the user as the alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#username_as_alias LdapAuthBackend#username_as_alias}
        :param use_token_groups: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#use_token_groups LdapAuthBackend#use_token_groups}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f737301359075057545e7a29eb796fac7fe8b5140f4deaf6f7863b2f6f98896)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument binddn", value=binddn, expected_type=type_hints["binddn"])
            check_type(argname="argument bindpass", value=bindpass, expected_type=type_hints["bindpass"])
            check_type(argname="argument case_sensitive_names", value=case_sensitive_names, expected_type=type_hints["case_sensitive_names"])
            check_type(argname="argument certificate", value=certificate, expected_type=type_hints["certificate"])
            check_type(argname="argument client_tls_cert", value=client_tls_cert, expected_type=type_hints["client_tls_cert"])
            check_type(argname="argument client_tls_key", value=client_tls_key, expected_type=type_hints["client_tls_key"])
            check_type(argname="argument connection_timeout", value=connection_timeout, expected_type=type_hints["connection_timeout"])
            check_type(argname="argument deny_null_bind", value=deny_null_bind, expected_type=type_hints["deny_null_bind"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument disable_automated_rotation", value=disable_automated_rotation, expected_type=type_hints["disable_automated_rotation"])
            check_type(argname="argument disable_remount", value=disable_remount, expected_type=type_hints["disable_remount"])
            check_type(argname="argument discoverdn", value=discoverdn, expected_type=type_hints["discoverdn"])
            check_type(argname="argument groupattr", value=groupattr, expected_type=type_hints["groupattr"])
            check_type(argname="argument groupdn", value=groupdn, expected_type=type_hints["groupdn"])
            check_type(argname="argument groupfilter", value=groupfilter, expected_type=type_hints["groupfilter"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument max_page_size", value=max_page_size, expected_type=type_hints["max_page_size"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument rotation_period", value=rotation_period, expected_type=type_hints["rotation_period"])
            check_type(argname="argument rotation_schedule", value=rotation_schedule, expected_type=type_hints["rotation_schedule"])
            check_type(argname="argument rotation_window", value=rotation_window, expected_type=type_hints["rotation_window"])
            check_type(argname="argument starttls", value=starttls, expected_type=type_hints["starttls"])
            check_type(argname="argument tls_max_version", value=tls_max_version, expected_type=type_hints["tls_max_version"])
            check_type(argname="argument tls_min_version", value=tls_min_version, expected_type=type_hints["tls_min_version"])
            check_type(argname="argument token_bound_cidrs", value=token_bound_cidrs, expected_type=type_hints["token_bound_cidrs"])
            check_type(argname="argument token_explicit_max_ttl", value=token_explicit_max_ttl, expected_type=type_hints["token_explicit_max_ttl"])
            check_type(argname="argument token_max_ttl", value=token_max_ttl, expected_type=type_hints["token_max_ttl"])
            check_type(argname="argument token_no_default_policy", value=token_no_default_policy, expected_type=type_hints["token_no_default_policy"])
            check_type(argname="argument token_num_uses", value=token_num_uses, expected_type=type_hints["token_num_uses"])
            check_type(argname="argument token_period", value=token_period, expected_type=type_hints["token_period"])
            check_type(argname="argument token_policies", value=token_policies, expected_type=type_hints["token_policies"])
            check_type(argname="argument token_ttl", value=token_ttl, expected_type=type_hints["token_ttl"])
            check_type(argname="argument token_type", value=token_type, expected_type=type_hints["token_type"])
            check_type(argname="argument upndomain", value=upndomain, expected_type=type_hints["upndomain"])
            check_type(argname="argument userattr", value=userattr, expected_type=type_hints["userattr"])
            check_type(argname="argument userdn", value=userdn, expected_type=type_hints["userdn"])
            check_type(argname="argument userfilter", value=userfilter, expected_type=type_hints["userfilter"])
            check_type(argname="argument username_as_alias", value=username_as_alias, expected_type=type_hints["username_as_alias"])
            check_type(argname="argument use_token_groups", value=use_token_groups, expected_type=type_hints["use_token_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
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
        if binddn is not None:
            self._values["binddn"] = binddn
        if bindpass is not None:
            self._values["bindpass"] = bindpass
        if case_sensitive_names is not None:
            self._values["case_sensitive_names"] = case_sensitive_names
        if certificate is not None:
            self._values["certificate"] = certificate
        if client_tls_cert is not None:
            self._values["client_tls_cert"] = client_tls_cert
        if client_tls_key is not None:
            self._values["client_tls_key"] = client_tls_key
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if deny_null_bind is not None:
            self._values["deny_null_bind"] = deny_null_bind
        if description is not None:
            self._values["description"] = description
        if disable_automated_rotation is not None:
            self._values["disable_automated_rotation"] = disable_automated_rotation
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
        if local is not None:
            self._values["local"] = local
        if max_page_size is not None:
            self._values["max_page_size"] = max_page_size
        if namespace is not None:
            self._values["namespace"] = namespace
        if path is not None:
            self._values["path"] = path
        if rotation_period is not None:
            self._values["rotation_period"] = rotation_period
        if rotation_schedule is not None:
            self._values["rotation_schedule"] = rotation_schedule
        if rotation_window is not None:
            self._values["rotation_window"] = rotation_window
        if starttls is not None:
            self._values["starttls"] = starttls
        if tls_max_version is not None:
            self._values["tls_max_version"] = tls_max_version
        if tls_min_version is not None:
            self._values["tls_min_version"] = tls_min_version
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
        if upndomain is not None:
            self._values["upndomain"] = upndomain
        if userattr is not None:
            self._values["userattr"] = userattr
        if userdn is not None:
            self._values["userdn"] = userdn
        if userfilter is not None:
            self._values["userfilter"] = userfilter
        if username_as_alias is not None:
            self._values["username_as_alias"] = username_as_alias
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
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#url LdapAuthBackend#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def binddn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#binddn LdapAuthBackend#binddn}.'''
        result = self._values.get("binddn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bindpass(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#bindpass LdapAuthBackend#bindpass}.'''
        result = self._values.get("bindpass")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def case_sensitive_names(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#case_sensitive_names LdapAuthBackend#case_sensitive_names}.'''
        result = self._values.get("case_sensitive_names")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def certificate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#certificate LdapAuthBackend#certificate}.'''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_tls_cert(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#client_tls_cert LdapAuthBackend#client_tls_cert}.'''
        result = self._values.get("client_tls_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_tls_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#client_tls_key LdapAuthBackend#client_tls_key}.'''
        result = self._values.get("client_tls_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#connection_timeout LdapAuthBackend#connection_timeout}.'''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deny_null_bind(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#deny_null_bind LdapAuthBackend#deny_null_bind}.'''
        result = self._values.get("deny_null_bind")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#description LdapAuthBackend#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_automated_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Stops rotation of the root credential until set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#disable_automated_rotation LdapAuthBackend#disable_automated_rotation}
        '''
        result = self._values.get("disable_automated_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_remount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, opts out of mount migration on path updates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#disable_remount LdapAuthBackend#disable_remount}
        '''
        result = self._values.get("disable_remount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def discoverdn(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#discoverdn LdapAuthBackend#discoverdn}.'''
        result = self._values.get("discoverdn")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def groupattr(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupattr LdapAuthBackend#groupattr}.'''
        result = self._values.get("groupattr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groupdn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupdn LdapAuthBackend#groupdn}.'''
        result = self._values.get("groupdn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groupfilter(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#groupfilter LdapAuthBackend#groupfilter}.'''
        result = self._values.get("groupfilter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#id LdapAuthBackend#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#insecure_tls LdapAuthBackend#insecure_tls}.'''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if the auth method is local only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#local LdapAuthBackend#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_page_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#max_page_size LdapAuthBackend#max_page_size}.'''
        result = self._values.get("max_page_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#namespace LdapAuthBackend#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#path LdapAuthBackend#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_period(self) -> typing.Optional[jsii.Number]:
        '''The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_period LdapAuthBackend#rotation_period}
        '''
        result = self._values.get("rotation_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_schedule(self) -> typing.Optional[builtins.str]:
        '''The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_schedule LdapAuthBackend#rotation_schedule}
        '''
        result = self._values.get("rotation_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_window(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered.

        Can only be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#rotation_window LdapAuthBackend#rotation_window}
        '''
        result = self._values.get("rotation_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def starttls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#starttls LdapAuthBackend#starttls}.'''
        result = self._values.get("starttls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_max_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#tls_max_version LdapAuthBackend#tls_max_version}.'''
        result = self._values.get("tls_max_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_min_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#tls_min_version LdapAuthBackend#tls_min_version}.'''
        result = self._values.get("tls_min_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_bound_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the blocks of IP addresses which are allowed to use the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_bound_cidrs LdapAuthBackend#token_bound_cidrs}
        '''
        result = self._values.get("token_bound_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_explicit_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Explicit Maximum TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_explicit_max_ttl LdapAuthBackend#token_explicit_max_ttl}
        '''
        result = self._values.get("token_explicit_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''The maximum lifetime of the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_max_ttl LdapAuthBackend#token_max_ttl}
        '''
        result = self._values.get("token_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_no_default_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the 'default' policy will not automatically be added to generated tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_no_default_policy LdapAuthBackend#token_no_default_policy}
        '''
        result = self._values.get("token_no_default_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_num_uses(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times a token may be used, a value of zero means unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_num_uses LdapAuthBackend#token_num_uses}
        '''
        result = self._values.get("token_num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_period(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_period LdapAuthBackend#token_period}
        '''
        result = self._values.get("token_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Generated Token's Policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_policies LdapAuthBackend#token_policies}
        '''
        result = self._values.get("token_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The initial ttl of the token to generate in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_ttl LdapAuthBackend#token_ttl}
        '''
        result = self._values.get("token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_type(self) -> typing.Optional[builtins.str]:
        '''The type of token to generate, service or batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#token_type LdapAuthBackend#token_type}
        '''
        result = self._values.get("token_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upndomain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#upndomain LdapAuthBackend#upndomain}.'''
        result = self._values.get("upndomain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userattr(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userattr LdapAuthBackend#userattr}.'''
        result = self._values.get("userattr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userdn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userdn LdapAuthBackend#userdn}.'''
        result = self._values.get("userdn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userfilter(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#userfilter LdapAuthBackend#userfilter}.'''
        result = self._values.get("userfilter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_as_alias(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Force the auth method to use the username passed by the user as the alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#username_as_alias LdapAuthBackend#username_as_alias}
        '''
        result = self._values.get("username_as_alias")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_token_groups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_auth_backend#use_token_groups LdapAuthBackend#use_token_groups}.'''
        result = self._values.get("use_token_groups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LdapAuthBackendConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LdapAuthBackend",
    "LdapAuthBackendConfig",
]

publication.publish()

def _typecheckingstub__7a612673267da58e0983ae26d9e157f12ea35bc4392a1520213eaf5f3d7b9376(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    url: builtins.str,
    binddn: typing.Optional[builtins.str] = None,
    bindpass: typing.Optional[builtins.str] = None,
    case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    certificate: typing.Optional[builtins.str] = None,
    client_tls_cert: typing.Optional[builtins.str] = None,
    client_tls_key: typing.Optional[builtins.str] = None,
    connection_timeout: typing.Optional[jsii.Number] = None,
    deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    groupattr: typing.Optional[builtins.str] = None,
    groupdn: typing.Optional[builtins.str] = None,
    groupfilter: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_page_size: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_max_version: typing.Optional[builtins.str] = None,
    tls_min_version: typing.Optional[builtins.str] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
    upndomain: typing.Optional[builtins.str] = None,
    userattr: typing.Optional[builtins.str] = None,
    userdn: typing.Optional[builtins.str] = None,
    userfilter: typing.Optional[builtins.str] = None,
    username_as_alias: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__6be3b6d915ff534f5e5b2045212ade7e718fad2abee62280b25dc98ab82222d5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e93055c1d2e6c5118bc1f6a4df2641cf9cb4abe0a984493dc74f58fbcdedf7db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef510a9242088f894c1ec1952646066e5c2132b270ff605597df1ac3c09e7cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c7f01dfa54afcf9d910ee4243ac57e1e07503efaaecb936f6995f4460ee0865(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e2f99f0507f688b7ec5e25dca193371f76f28022f35a2088ce23423969975a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd7d8d30a8eb8eac72cebe464afd6f7c5751eee7c0d59def5a700e50025ee7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2fbbb64188c938486024f9278195a88ca96758b2ed40c04b15d12c8dd041d2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a48d4e45458d7e90db45b9d9591a7a8decba4d1f87873aa6934f736d1f5cf4d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4ebeb54aecc054bc41ec0016e25825618a06e1212e05becc05498f0fae978c0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9facf239ed05d82f4af5f9aeb10f82c9098e3e140f5c8d149fbfbbbc91a5b606(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36467a86e3e999f43345e4c7c00ea74707736fb58298b7d62bf90972fa0913df(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e47f01de34a7c90fe8b2c56a3e3763a6c2fc2e4d0e73ce142b676a56e3fd7b4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e84d029344e3d8deb8632b394d9429201cb77e65df528c131ec0c782cc6fb11(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187cf57576ab6a599efa91091cb3fd4b7fedcc3b7fbaf57805e04a7ec92d9301(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a35e7fbe545b448ae9da8cb88041aa7404dd1dd6fb6d56421ea9850da5501995(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a5329f611b182ecb4f785156bf8dea9e22a61ce93d2e82031e9100498f15bab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87b8176f32ebb58de39a9015160d74d19c57007739d2383668af94df52874b0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81d2cbf8ef2d7a6aa633d0c5eacb49b5f07cc39ca34c660e751e4884fdac8c41(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b434480f8b73111bda3fc4cf837b5fd1cd00ab140172f2f4e644ca6358e5c5a4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__773de9ff50db0622cf5dcdd12be85598de57687665861f5bf32357c92251876a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b17d3e69fc2b78add5dd8c75c6843f1bf4eabd99c9c7348250891060c7a1d71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e0655a4e0b333faf630fe4e93efa6664aa19e1719f8a1a3642724489e8479b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9969b9c8658ac741d4921a2e31dc84c2c03553e8f18676f4142dad69ab27296b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a35d50dd57a60f36792e5a7beef5a205233b9bacf75ec700f203b0ca48dbe545(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3439f57a7851509d750fdf2b2b1a1e0cea8a258450c6c674a28e5f2a3e7892a6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9cfd51073a9e4c2422ef1ebeefab2bdc20c765b3d51a83560d649b7f45128ac(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8409a49aef77db5baf67b37964898f336e8c3b3d7a6d755d31e993e356d356b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88df194a6b69e666bad7a8581daa429c1b4b3b4fb7951b388129c69cdfc1bd7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__036a5228922a1f1323fed2fcfbf31b19b3a0ba932f539f173677384ab6210f56(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7721bbfcd12f9c0c564254b761020d6dc6353ab9dba683ed27174a4d6585f9e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8813e27a0a309c62361d82c80bcf395fbd32ba347adb07ec7c5059ca5d52cc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88da75192ccb8179509d9c84f6b1840f06a5b7afebc3cbd3c39fb86e2c0c27e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56c2f54e4daa2b01329735455e33e71f1335b2856e7cee868b03f03718b9a61d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322754212e722140f8bdca21385f33ffc274df9ed067d0ddbea253f0396b0f7a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__addd15f899b7228f5deabf2438a6220c2a9d0478645bb557b036682df5b46349(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09095ab39d618c7e916ef86bae54bc3cfcdf5b36e25d2c190ca3b18e461a3e31(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3e02b67eb652b570c0fa763f887517d3e45a76daa2104fac56de833b1ec67dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a509fb0183c2ff008bf6b7115ff6135af5483d431d34a3fcfc8dfcd7e4b52ad9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1222c78da72f429739b08c6ee8c5db2a90f09efe46c41b97ff3703cb64b95c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__652ef4a66b6b54f1804a2dcce50681e1588a086093c00d6f62b3845b1aa2c63b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__164a9ebc2b060c0790bcb389b7eb55385994bbc7eb0406d34d4c33f95f9c793e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a6e4cc0e2779124c966e198049a26ef64abc5dc1ee5fa0b127add337eb423a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d9f10996ec9e830811da9934b7fe2a54a33dd003365897f9fe839d7724b2860(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__838fc6f04d9bca7c8cb6c7f34964f3c140c64b2f2773a2b0960cbdd2ee9780c9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f737301359075057545e7a29eb796fac7fe8b5140f4deaf6f7863b2f6f98896(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    url: builtins.str,
    binddn: typing.Optional[builtins.str] = None,
    bindpass: typing.Optional[builtins.str] = None,
    case_sensitive_names: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    certificate: typing.Optional[builtins.str] = None,
    client_tls_cert: typing.Optional[builtins.str] = None,
    client_tls_key: typing.Optional[builtins.str] = None,
    connection_timeout: typing.Optional[jsii.Number] = None,
    deny_null_bind: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_remount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    discoverdn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    groupattr: typing.Optional[builtins.str] = None,
    groupdn: typing.Optional[builtins.str] = None,
    groupfilter: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_page_size: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    starttls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_max_version: typing.Optional[builtins.str] = None,
    tls_min_version: typing.Optional[builtins.str] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
    upndomain: typing.Optional[builtins.str] = None,
    userattr: typing.Optional[builtins.str] = None,
    userdn: typing.Optional[builtins.str] = None,
    userfilter: typing.Optional[builtins.str] = None,
    username_as_alias: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_token_groups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
