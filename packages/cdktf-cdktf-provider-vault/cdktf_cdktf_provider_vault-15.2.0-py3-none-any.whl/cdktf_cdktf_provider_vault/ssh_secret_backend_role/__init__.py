r'''
# `vault_ssh_secret_backend_role`

Refer to the Terraform Registry for docs: [`vault_ssh_secret_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role).
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


class SshSecretBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.sshSecretBackendRole.SshSecretBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role vault_ssh_secret_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        key_type: builtins.str,
        name: builtins.str,
        algorithm_signer: typing.Optional[builtins.str] = None,
        allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_critical_options: typing.Optional[builtins.str] = None,
        allowed_domains: typing.Optional[builtins.str] = None,
        allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_extensions: typing.Optional[builtins.str] = None,
        allowed_user_key_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SshSecretBackendRoleAllowedUserKeyConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_users: typing.Optional[builtins.str] = None,
        allowed_users_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_empty_principals: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_host_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_user_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_user_key_ids: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cidr_list: typing.Optional[builtins.str] = None,
        default_critical_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        default_extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        default_user: typing.Optional[builtins.str] = None,
        default_user_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        key_id_format: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_before_duration: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role vault_ssh_secret_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#backend SshSecretBackendRole#backend}.
        :param key_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#key_type SshSecretBackendRole#key_type}.
        :param name: Unique name for the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#name SshSecretBackendRole#name}
        :param algorithm_signer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#algorithm_signer SshSecretBackendRole#algorithm_signer}.
        :param allow_bare_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_bare_domains SshSecretBackendRole#allow_bare_domains}.
        :param allowed_critical_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_critical_options SshSecretBackendRole#allowed_critical_options}.
        :param allowed_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_domains SshSecretBackendRole#allowed_domains}.
        :param allowed_domains_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_domains_template SshSecretBackendRole#allowed_domains_template}.
        :param allowed_extensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_extensions SshSecretBackendRole#allowed_extensions}.
        :param allowed_user_key_config: allowed_user_key_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_user_key_config SshSecretBackendRole#allowed_user_key_config}
        :param allowed_users: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_users SshSecretBackendRole#allowed_users}.
        :param allowed_users_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_users_template SshSecretBackendRole#allowed_users_template}.
        :param allow_empty_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_empty_principals SshSecretBackendRole#allow_empty_principals}.
        :param allow_host_certificates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_host_certificates SshSecretBackendRole#allow_host_certificates}.
        :param allow_subdomains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_subdomains SshSecretBackendRole#allow_subdomains}.
        :param allow_user_certificates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_user_certificates SshSecretBackendRole#allow_user_certificates}.
        :param allow_user_key_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_user_key_ids SshSecretBackendRole#allow_user_key_ids}.
        :param cidr_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#cidr_list SshSecretBackendRole#cidr_list}.
        :param default_critical_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_critical_options SshSecretBackendRole#default_critical_options}.
        :param default_extensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_extensions SshSecretBackendRole#default_extensions}.
        :param default_user: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_user SshSecretBackendRole#default_user}.
        :param default_user_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_user_template SshSecretBackendRole#default_user_template}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#id SshSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_id_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#key_id_format SshSecretBackendRole#key_id_format}.
        :param max_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#max_ttl SshSecretBackendRole#max_ttl}.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#namespace SshSecretBackendRole#namespace}
        :param not_before_duration: Specifies the duration by which to backdate the ValidAfter property. Uses duration format strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#not_before_duration SshSecretBackendRole#not_before_duration}
        :param ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#ttl SshSecretBackendRole#ttl}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ced88bf68784d756a74fcad715b6403dfbf36b8dd8da0b478c5e012d0c4229a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SshSecretBackendRoleConfig(
            backend=backend,
            key_type=key_type,
            name=name,
            algorithm_signer=algorithm_signer,
            allow_bare_domains=allow_bare_domains,
            allowed_critical_options=allowed_critical_options,
            allowed_domains=allowed_domains,
            allowed_domains_template=allowed_domains_template,
            allowed_extensions=allowed_extensions,
            allowed_user_key_config=allowed_user_key_config,
            allowed_users=allowed_users,
            allowed_users_template=allowed_users_template,
            allow_empty_principals=allow_empty_principals,
            allow_host_certificates=allow_host_certificates,
            allow_subdomains=allow_subdomains,
            allow_user_certificates=allow_user_certificates,
            allow_user_key_ids=allow_user_key_ids,
            cidr_list=cidr_list,
            default_critical_options=default_critical_options,
            default_extensions=default_extensions,
            default_user=default_user,
            default_user_template=default_user_template,
            id=id,
            key_id_format=key_id_format,
            max_ttl=max_ttl,
            namespace=namespace,
            not_before_duration=not_before_duration,
            ttl=ttl,
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
        '''Generates CDKTF code for importing a SshSecretBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SshSecretBackendRole to import.
        :param import_from_id: The id of the existing SshSecretBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SshSecretBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35bd6b612bdd6f55bc33f92cb68c032873d708c579af8a988041c9778dea6804)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAllowedUserKeyConfig")
    def put_allowed_user_key_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["SshSecretBackendRoleAllowedUserKeyConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a1cb76a3cb9c1ff358c2532bf07d95acdcc456202ce620ba679b7ec48ce0874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedUserKeyConfig", [value]))

    @jsii.member(jsii_name="resetAlgorithmSigner")
    def reset_algorithm_signer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithmSigner", []))

    @jsii.member(jsii_name="resetAllowBareDomains")
    def reset_allow_bare_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowBareDomains", []))

    @jsii.member(jsii_name="resetAllowedCriticalOptions")
    def reset_allowed_critical_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedCriticalOptions", []))

    @jsii.member(jsii_name="resetAllowedDomains")
    def reset_allowed_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDomains", []))

    @jsii.member(jsii_name="resetAllowedDomainsTemplate")
    def reset_allowed_domains_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDomainsTemplate", []))

    @jsii.member(jsii_name="resetAllowedExtensions")
    def reset_allowed_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedExtensions", []))

    @jsii.member(jsii_name="resetAllowedUserKeyConfig")
    def reset_allowed_user_key_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUserKeyConfig", []))

    @jsii.member(jsii_name="resetAllowedUsers")
    def reset_allowed_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUsers", []))

    @jsii.member(jsii_name="resetAllowedUsersTemplate")
    def reset_allowed_users_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUsersTemplate", []))

    @jsii.member(jsii_name="resetAllowEmptyPrincipals")
    def reset_allow_empty_principals(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowEmptyPrincipals", []))

    @jsii.member(jsii_name="resetAllowHostCertificates")
    def reset_allow_host_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowHostCertificates", []))

    @jsii.member(jsii_name="resetAllowSubdomains")
    def reset_allow_subdomains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSubdomains", []))

    @jsii.member(jsii_name="resetAllowUserCertificates")
    def reset_allow_user_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUserCertificates", []))

    @jsii.member(jsii_name="resetAllowUserKeyIds")
    def reset_allow_user_key_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowUserKeyIds", []))

    @jsii.member(jsii_name="resetCidrList")
    def reset_cidr_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCidrList", []))

    @jsii.member(jsii_name="resetDefaultCriticalOptions")
    def reset_default_critical_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultCriticalOptions", []))

    @jsii.member(jsii_name="resetDefaultExtensions")
    def reset_default_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultExtensions", []))

    @jsii.member(jsii_name="resetDefaultUser")
    def reset_default_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultUser", []))

    @jsii.member(jsii_name="resetDefaultUserTemplate")
    def reset_default_user_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultUserTemplate", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyIdFormat")
    def reset_key_id_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyIdFormat", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNotBeforeDuration")
    def reset_not_before_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotBeforeDuration", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="allowedUserKeyConfig")
    def allowed_user_key_config(self) -> "SshSecretBackendRoleAllowedUserKeyConfigList":
        return typing.cast("SshSecretBackendRoleAllowedUserKeyConfigList", jsii.get(self, "allowedUserKeyConfig"))

    @builtins.property
    @jsii.member(jsii_name="algorithmSignerInput")
    def algorithm_signer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmSignerInput"))

    @builtins.property
    @jsii.member(jsii_name="allowBareDomainsInput")
    def allow_bare_domains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowBareDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedCriticalOptionsInput")
    def allowed_critical_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedCriticalOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsInput")
    def allowed_domains_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsTemplateInput")
    def allowed_domains_template_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowedDomainsTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedExtensionsInput")
    def allowed_extensions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedExtensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUserKeyConfigInput")
    def allowed_user_key_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SshSecretBackendRoleAllowedUserKeyConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["SshSecretBackendRoleAllowedUserKeyConfig"]]], jsii.get(self, "allowedUserKeyConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUsersInput")
    def allowed_users_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedUsersInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUsersTemplateInput")
    def allowed_users_template_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowedUsersTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="allowEmptyPrincipalsInput")
    def allow_empty_principals_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowEmptyPrincipalsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowHostCertificatesInput")
    def allow_host_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowHostCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowSubdomainsInput")
    def allow_subdomains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowSubdomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowUserCertificatesInput")
    def allow_user_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUserCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowUserKeyIdsInput")
    def allow_user_key_ids_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowUserKeyIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="cidrListInput")
    def cidr_list_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cidrListInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultCriticalOptionsInput")
    def default_critical_options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "defaultCriticalOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultExtensionsInput")
    def default_extensions_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "defaultExtensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultUserInput")
    def default_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultUserInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultUserTemplateInput")
    def default_user_template_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "defaultUserTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyIdFormatInput")
    def key_id_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="notBeforeDurationInput")
    def not_before_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notBeforeDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithmSigner")
    def algorithm_signer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithmSigner"))

    @algorithm_signer.setter
    def algorithm_signer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__045e474b97256a4c803f20110667655464973f7b73b2b72de11356974aba1f26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithmSigner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowBareDomains")
    def allow_bare_domains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowBareDomains"))

    @allow_bare_domains.setter
    def allow_bare_domains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e0bd9e7d2f899c243c32ab9308098c90fce13538f6bb2309d1a61813e7b7c85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowBareDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedCriticalOptions")
    def allowed_critical_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedCriticalOptions"))

    @allowed_critical_options.setter
    def allowed_critical_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e116b84be64fc27fcb2d3e5234abd8c53c3a611055a6afc437ffb1c84e63767)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedCriticalOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedDomains")
    def allowed_domains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedDomains"))

    @allowed_domains.setter
    def allowed_domains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81b8175c2e21a96b809209bf2ef0f6cc9ec96b59a0bb0af57c5670aacf3655a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsTemplate")
    def allowed_domains_template(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowedDomainsTemplate"))

    @allowed_domains_template.setter
    def allowed_domains_template(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6e35fc2e5d0567540a0c7518599c0ad2840435ce29a90bac2b237e2fa89a3b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDomainsTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedExtensions")
    def allowed_extensions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedExtensions"))

    @allowed_extensions.setter
    def allowed_extensions(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dab1e4883f73dfadc1ff76238f624955af7f674c46b89d1273fc987a0b156f48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedExtensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedUsers")
    def allowed_users(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedUsers"))

    @allowed_users.setter
    def allowed_users(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d59793a34d0af4bac5264e821825be34605512d114f710eeeaf24c3a00e1b42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUsers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedUsersTemplate")
    def allowed_users_template(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowedUsersTemplate"))

    @allowed_users_template.setter
    def allowed_users_template(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8026bcac79f7f443bbe773885052ca515a5e0a8cdd3122e031ccc2eb7d5c27bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUsersTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowEmptyPrincipals")
    def allow_empty_principals(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowEmptyPrincipals"))

    @allow_empty_principals.setter
    def allow_empty_principals(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754c20429a3b46712a202c998cd14dc812b810ed993bf2ca689c7973a6da754e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowEmptyPrincipals", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowHostCertificates")
    def allow_host_certificates(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowHostCertificates"))

    @allow_host_certificates.setter
    def allow_host_certificates(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9461459f9983a9356ac5823864974090ba5b4163035e4e7a5353524b534dd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowHostCertificates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowSubdomains")
    def allow_subdomains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowSubdomains"))

    @allow_subdomains.setter
    def allow_subdomains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__380ee19bcbf9724e7613371e6401ee8283745b3e56edef61335a53eb508bdac4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowSubdomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowUserCertificates")
    def allow_user_certificates(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowUserCertificates"))

    @allow_user_certificates.setter
    def allow_user_certificates(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__950ccb720da8ebd8cdb527e5c6f6b4f16e6331cc743d10390aaab0e266c469d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUserCertificates", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowUserKeyIds")
    def allow_user_key_ids(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowUserKeyIds"))

    @allow_user_key_ids.setter
    def allow_user_key_ids(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91097e2a3b316b15b3774d8cfe529483521eff2b84968d45a2ec9b269f81f30c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowUserKeyIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d215028cb12f1fda669d2c790a6a6e8ea18a584767f23e8169987c24ebfae00d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cidrList")
    def cidr_list(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cidrList"))

    @cidr_list.setter
    def cidr_list(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca95aa84be2317a2c8153f260f4e1551dae19216039c7eec416fd5db49fc0da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidrList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultCriticalOptions")
    def default_critical_options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "defaultCriticalOptions"))

    @default_critical_options.setter
    def default_critical_options(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c46a8b0c4a7fa1c529c85e37e3278cb3ec4d588db689c6b1b9c51327c93339b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultCriticalOptions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultExtensions")
    def default_extensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "defaultExtensions"))

    @default_extensions.setter
    def default_extensions(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7800f5d212be38299bb84f253cb323d65ee18cfaf391e6738a8b58f84f376e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultExtensions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultUser")
    def default_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultUser"))

    @default_user.setter
    def default_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__304a9c5db7e3bd1fe14bf8d0e4db2c77e5b3295d0a411a2ca4a110f7664c0933)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultUser", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultUserTemplate")
    def default_user_template(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "defaultUserTemplate"))

    @default_user_template.setter
    def default_user_template(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c641ca51d0f29581f38b0db0de38e34a51699fe2fddf3fb1870987c51033a86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultUserTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__971245d7310af4ae082fde1d503c585687c86d61a19385bc3970362a0b4de7fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyIdFormat")
    def key_id_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyIdFormat"))

    @key_id_format.setter
    def key_id_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52be35765eb81f659fed273268910bcb72ad0fa575b23cf905cacdb1b5948552)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyIdFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e70353de2a88634f4945559ea90269cd23247aef1f5739ea1a49c964836340)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdd9b3fede80c409cebd6588572bce86632bb389901a1b32dff0869b62f5cfb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cae3e7b0f078fe29d7c20d9bf56848698675725ff6d4164b238c43876b42d8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b71412e3c88ced9f630085f473b20356f5f3dd2f6ddb7b33cc048e56bdf3c08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notBeforeDuration")
    def not_before_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBeforeDuration"))

    @not_before_duration.setter
    def not_before_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__819cd6e64afd67602b45fa55b6271701a0fef0212407615dfb70f9c91bfb8413)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notBeforeDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84ae399c7307e95912a27f8bd72fcf0a983c6bd491a5d4b115381095aacf7e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.sshSecretBackendRole.SshSecretBackendRoleAllowedUserKeyConfig",
    jsii_struct_bases=[],
    name_mapping={"lengths": "lengths", "type": "type"},
)
class SshSecretBackendRoleAllowedUserKeyConfig:
    def __init__(
        self,
        *,
        lengths: typing.Sequence[jsii.Number],
        type: builtins.str,
    ) -> None:
        '''
        :param lengths: List of allowed key lengths, vault-1.10 and above. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#lengths SshSecretBackendRole#lengths}
        :param type: Key type, choices: rsa, ecdsa, ec, dsa, ed25519, ssh-rsa, ssh-dss, ssh-ed25519, ecdsa-sha2-nistp256, ecdsa-sha2-nistp384, ecdsa-sha2-nistp521. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#type SshSecretBackendRole#type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a20480b6592cbc25ddbbe0b241dd087657a8f98da88928537430fc6502905f96)
            check_type(argname="argument lengths", value=lengths, expected_type=type_hints["lengths"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lengths": lengths,
            "type": type,
        }

    @builtins.property
    def lengths(self) -> typing.List[jsii.Number]:
        '''List of allowed key lengths, vault-1.10 and above.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#lengths SshSecretBackendRole#lengths}
        '''
        result = self._values.get("lengths")
        assert result is not None, "Required property 'lengths' is missing"
        return typing.cast(typing.List[jsii.Number], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Key type, choices: rsa, ecdsa, ec, dsa, ed25519, ssh-rsa, ssh-dss, ssh-ed25519, ecdsa-sha2-nistp256, ecdsa-sha2-nistp384, ecdsa-sha2-nistp521.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#type SshSecretBackendRole#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SshSecretBackendRoleAllowedUserKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SshSecretBackendRoleAllowedUserKeyConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.sshSecretBackendRole.SshSecretBackendRoleAllowedUserKeyConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__972666618294defc46c989459fa22873dcb28f6c26af2b93daf9073ecc2d4197)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "SshSecretBackendRoleAllowedUserKeyConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a35aa91b425c1f75896f5e8a8f020cd90e691a2e9bd273badc255f4381602d69)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("SshSecretBackendRoleAllowedUserKeyConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__062c76529f09d392a79bd5c5e5a93d5eadd444543cb5fba22e4e146f6e857057)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e65709a2d058fab64c5ddce38b678fcc9a38d02cc40b1e917240535f613459d1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c13fbc5c8b0e8632bfd2eeec6cb5e4ecdc5a4db203639d143ee1ebce9ab9804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SshSecretBackendRoleAllowedUserKeyConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SshSecretBackendRoleAllowedUserKeyConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SshSecretBackendRoleAllowedUserKeyConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b854de1d024cdb981ff750892b8f78b7794a0e675ca4b2997a7370598fb03678)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class SshSecretBackendRoleAllowedUserKeyConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.sshSecretBackendRole.SshSecretBackendRoleAllowedUserKeyConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c1d20cd597a8834bb21253eae5d7ed6d46bf3e24e04aad9f0a44ab0360e336a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="lengthsInput")
    def lengths_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "lengthsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="lengths")
    def lengths(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "lengths"))

    @lengths.setter
    def lengths(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d44050be820525c0bba926b98eb2c74d0243ba564d4ecab7b601ddf3eb507f6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lengths", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb62a8d59da5b4382fc111f9f31994df088b4b6e04dd2a094fa824e25e58cf13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SshSecretBackendRoleAllowedUserKeyConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SshSecretBackendRoleAllowedUserKeyConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SshSecretBackendRoleAllowedUserKeyConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51cb5dc67f79c27be423ff9f5664a4e27ba54aaa1c5e99e279276f0e184a4155)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.sshSecretBackendRole.SshSecretBackendRoleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "backend": "backend",
        "key_type": "keyType",
        "name": "name",
        "algorithm_signer": "algorithmSigner",
        "allow_bare_domains": "allowBareDomains",
        "allowed_critical_options": "allowedCriticalOptions",
        "allowed_domains": "allowedDomains",
        "allowed_domains_template": "allowedDomainsTemplate",
        "allowed_extensions": "allowedExtensions",
        "allowed_user_key_config": "allowedUserKeyConfig",
        "allowed_users": "allowedUsers",
        "allowed_users_template": "allowedUsersTemplate",
        "allow_empty_principals": "allowEmptyPrincipals",
        "allow_host_certificates": "allowHostCertificates",
        "allow_subdomains": "allowSubdomains",
        "allow_user_certificates": "allowUserCertificates",
        "allow_user_key_ids": "allowUserKeyIds",
        "cidr_list": "cidrList",
        "default_critical_options": "defaultCriticalOptions",
        "default_extensions": "defaultExtensions",
        "default_user": "defaultUser",
        "default_user_template": "defaultUserTemplate",
        "id": "id",
        "key_id_format": "keyIdFormat",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "not_before_duration": "notBeforeDuration",
        "ttl": "ttl",
    },
)
class SshSecretBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: builtins.str,
        key_type: builtins.str,
        name: builtins.str,
        algorithm_signer: typing.Optional[builtins.str] = None,
        allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_critical_options: typing.Optional[builtins.str] = None,
        allowed_domains: typing.Optional[builtins.str] = None,
        allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_extensions: typing.Optional[builtins.str] = None,
        allowed_user_key_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SshSecretBackendRoleAllowedUserKeyConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
        allowed_users: typing.Optional[builtins.str] = None,
        allowed_users_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_empty_principals: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_host_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_user_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_user_key_ids: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cidr_list: typing.Optional[builtins.str] = None,
        default_critical_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        default_extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        default_user: typing.Optional[builtins.str] = None,
        default_user_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        key_id_format: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_before_duration: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#backend SshSecretBackendRole#backend}.
        :param key_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#key_type SshSecretBackendRole#key_type}.
        :param name: Unique name for the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#name SshSecretBackendRole#name}
        :param algorithm_signer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#algorithm_signer SshSecretBackendRole#algorithm_signer}.
        :param allow_bare_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_bare_domains SshSecretBackendRole#allow_bare_domains}.
        :param allowed_critical_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_critical_options SshSecretBackendRole#allowed_critical_options}.
        :param allowed_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_domains SshSecretBackendRole#allowed_domains}.
        :param allowed_domains_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_domains_template SshSecretBackendRole#allowed_domains_template}.
        :param allowed_extensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_extensions SshSecretBackendRole#allowed_extensions}.
        :param allowed_user_key_config: allowed_user_key_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_user_key_config SshSecretBackendRole#allowed_user_key_config}
        :param allowed_users: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_users SshSecretBackendRole#allowed_users}.
        :param allowed_users_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_users_template SshSecretBackendRole#allowed_users_template}.
        :param allow_empty_principals: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_empty_principals SshSecretBackendRole#allow_empty_principals}.
        :param allow_host_certificates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_host_certificates SshSecretBackendRole#allow_host_certificates}.
        :param allow_subdomains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_subdomains SshSecretBackendRole#allow_subdomains}.
        :param allow_user_certificates: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_user_certificates SshSecretBackendRole#allow_user_certificates}.
        :param allow_user_key_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_user_key_ids SshSecretBackendRole#allow_user_key_ids}.
        :param cidr_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#cidr_list SshSecretBackendRole#cidr_list}.
        :param default_critical_options: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_critical_options SshSecretBackendRole#default_critical_options}.
        :param default_extensions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_extensions SshSecretBackendRole#default_extensions}.
        :param default_user: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_user SshSecretBackendRole#default_user}.
        :param default_user_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_user_template SshSecretBackendRole#default_user_template}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#id SshSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_id_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#key_id_format SshSecretBackendRole#key_id_format}.
        :param max_ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#max_ttl SshSecretBackendRole#max_ttl}.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#namespace SshSecretBackendRole#namespace}
        :param not_before_duration: Specifies the duration by which to backdate the ValidAfter property. Uses duration format strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#not_before_duration SshSecretBackendRole#not_before_duration}
        :param ttl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#ttl SshSecretBackendRole#ttl}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da1526537ffae42c40b816625649f1731b0295630b34629a604dde72602f4f94)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument algorithm_signer", value=algorithm_signer, expected_type=type_hints["algorithm_signer"])
            check_type(argname="argument allow_bare_domains", value=allow_bare_domains, expected_type=type_hints["allow_bare_domains"])
            check_type(argname="argument allowed_critical_options", value=allowed_critical_options, expected_type=type_hints["allowed_critical_options"])
            check_type(argname="argument allowed_domains", value=allowed_domains, expected_type=type_hints["allowed_domains"])
            check_type(argname="argument allowed_domains_template", value=allowed_domains_template, expected_type=type_hints["allowed_domains_template"])
            check_type(argname="argument allowed_extensions", value=allowed_extensions, expected_type=type_hints["allowed_extensions"])
            check_type(argname="argument allowed_user_key_config", value=allowed_user_key_config, expected_type=type_hints["allowed_user_key_config"])
            check_type(argname="argument allowed_users", value=allowed_users, expected_type=type_hints["allowed_users"])
            check_type(argname="argument allowed_users_template", value=allowed_users_template, expected_type=type_hints["allowed_users_template"])
            check_type(argname="argument allow_empty_principals", value=allow_empty_principals, expected_type=type_hints["allow_empty_principals"])
            check_type(argname="argument allow_host_certificates", value=allow_host_certificates, expected_type=type_hints["allow_host_certificates"])
            check_type(argname="argument allow_subdomains", value=allow_subdomains, expected_type=type_hints["allow_subdomains"])
            check_type(argname="argument allow_user_certificates", value=allow_user_certificates, expected_type=type_hints["allow_user_certificates"])
            check_type(argname="argument allow_user_key_ids", value=allow_user_key_ids, expected_type=type_hints["allow_user_key_ids"])
            check_type(argname="argument cidr_list", value=cidr_list, expected_type=type_hints["cidr_list"])
            check_type(argname="argument default_critical_options", value=default_critical_options, expected_type=type_hints["default_critical_options"])
            check_type(argname="argument default_extensions", value=default_extensions, expected_type=type_hints["default_extensions"])
            check_type(argname="argument default_user", value=default_user, expected_type=type_hints["default_user"])
            check_type(argname="argument default_user_template", value=default_user_template, expected_type=type_hints["default_user_template"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_id_format", value=key_id_format, expected_type=type_hints["key_id_format"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument not_before_duration", value=not_before_duration, expected_type=type_hints["not_before_duration"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "key_type": key_type,
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
        if algorithm_signer is not None:
            self._values["algorithm_signer"] = algorithm_signer
        if allow_bare_domains is not None:
            self._values["allow_bare_domains"] = allow_bare_domains
        if allowed_critical_options is not None:
            self._values["allowed_critical_options"] = allowed_critical_options
        if allowed_domains is not None:
            self._values["allowed_domains"] = allowed_domains
        if allowed_domains_template is not None:
            self._values["allowed_domains_template"] = allowed_domains_template
        if allowed_extensions is not None:
            self._values["allowed_extensions"] = allowed_extensions
        if allowed_user_key_config is not None:
            self._values["allowed_user_key_config"] = allowed_user_key_config
        if allowed_users is not None:
            self._values["allowed_users"] = allowed_users
        if allowed_users_template is not None:
            self._values["allowed_users_template"] = allowed_users_template
        if allow_empty_principals is not None:
            self._values["allow_empty_principals"] = allow_empty_principals
        if allow_host_certificates is not None:
            self._values["allow_host_certificates"] = allow_host_certificates
        if allow_subdomains is not None:
            self._values["allow_subdomains"] = allow_subdomains
        if allow_user_certificates is not None:
            self._values["allow_user_certificates"] = allow_user_certificates
        if allow_user_key_ids is not None:
            self._values["allow_user_key_ids"] = allow_user_key_ids
        if cidr_list is not None:
            self._values["cidr_list"] = cidr_list
        if default_critical_options is not None:
            self._values["default_critical_options"] = default_critical_options
        if default_extensions is not None:
            self._values["default_extensions"] = default_extensions
        if default_user is not None:
            self._values["default_user"] = default_user
        if default_user_template is not None:
            self._values["default_user_template"] = default_user_template
        if id is not None:
            self._values["id"] = id
        if key_id_format is not None:
            self._values["key_id_format"] = key_id_format
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if not_before_duration is not None:
            self._values["not_before_duration"] = not_before_duration
        if ttl is not None:
            self._values["ttl"] = ttl

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
    def backend(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#backend SshSecretBackendRole#backend}.'''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#key_type SshSecretBackendRole#key_type}.'''
        result = self._values.get("key_type")
        assert result is not None, "Required property 'key_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Unique name for the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#name SshSecretBackendRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def algorithm_signer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#algorithm_signer SshSecretBackendRole#algorithm_signer}.'''
        result = self._values.get("algorithm_signer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allow_bare_domains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_bare_domains SshSecretBackendRole#allow_bare_domains}.'''
        result = self._values.get("allow_bare_domains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_critical_options(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_critical_options SshSecretBackendRole#allowed_critical_options}.'''
        result = self._values.get("allowed_critical_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_domains(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_domains SshSecretBackendRole#allowed_domains}.'''
        result = self._values.get("allowed_domains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_domains_template(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_domains_template SshSecretBackendRole#allowed_domains_template}.'''
        result = self._values.get("allowed_domains_template")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_extensions(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_extensions SshSecretBackendRole#allowed_extensions}.'''
        result = self._values.get("allowed_extensions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_user_key_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SshSecretBackendRoleAllowedUserKeyConfig]]]:
        '''allowed_user_key_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_user_key_config SshSecretBackendRole#allowed_user_key_config}
        '''
        result = self._values.get("allowed_user_key_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SshSecretBackendRoleAllowedUserKeyConfig]]], result)

    @builtins.property
    def allowed_users(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_users SshSecretBackendRole#allowed_users}.'''
        result = self._values.get("allowed_users")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_users_template(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allowed_users_template SshSecretBackendRole#allowed_users_template}.'''
        result = self._values.get("allowed_users_template")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_empty_principals(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_empty_principals SshSecretBackendRole#allow_empty_principals}.'''
        result = self._values.get("allow_empty_principals")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_host_certificates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_host_certificates SshSecretBackendRole#allow_host_certificates}.'''
        result = self._values.get("allow_host_certificates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_subdomains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_subdomains SshSecretBackendRole#allow_subdomains}.'''
        result = self._values.get("allow_subdomains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_user_certificates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_user_certificates SshSecretBackendRole#allow_user_certificates}.'''
        result = self._values.get("allow_user_certificates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_user_key_ids(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#allow_user_key_ids SshSecretBackendRole#allow_user_key_ids}.'''
        result = self._values.get("allow_user_key_ids")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cidr_list(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#cidr_list SshSecretBackendRole#cidr_list}.'''
        result = self._values.get("cidr_list")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_critical_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_critical_options SshSecretBackendRole#default_critical_options}.'''
        result = self._values.get("default_critical_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def default_extensions(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_extensions SshSecretBackendRole#default_extensions}.'''
        result = self._values.get("default_extensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def default_user(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_user SshSecretBackendRole#default_user}.'''
        result = self._values.get("default_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_user_template(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#default_user_template SshSecretBackendRole#default_user_template}.'''
        result = self._values.get("default_user_template")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#id SshSecretBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_id_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#key_id_format SshSecretBackendRole#key_id_format}.'''
        result = self._values.get("key_id_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#max_ttl SshSecretBackendRole#max_ttl}.'''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#namespace SshSecretBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_before_duration(self) -> typing.Optional[builtins.str]:
        '''Specifies the duration by which to backdate the ValidAfter property. Uses duration format strings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#not_before_duration SshSecretBackendRole#not_before_duration}
        '''
        result = self._values.get("not_before_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_role#ttl SshSecretBackendRole#ttl}.'''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SshSecretBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SshSecretBackendRole",
    "SshSecretBackendRoleAllowedUserKeyConfig",
    "SshSecretBackendRoleAllowedUserKeyConfigList",
    "SshSecretBackendRoleAllowedUserKeyConfigOutputReference",
    "SshSecretBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__0ced88bf68784d756a74fcad715b6403dfbf36b8dd8da0b478c5e012d0c4229a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    key_type: builtins.str,
    name: builtins.str,
    algorithm_signer: typing.Optional[builtins.str] = None,
    allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_critical_options: typing.Optional[builtins.str] = None,
    allowed_domains: typing.Optional[builtins.str] = None,
    allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_extensions: typing.Optional[builtins.str] = None,
    allowed_user_key_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SshSecretBackendRoleAllowedUserKeyConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_users: typing.Optional[builtins.str] = None,
    allowed_users_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_empty_principals: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_host_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_user_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_user_key_ids: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cidr_list: typing.Optional[builtins.str] = None,
    default_critical_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    default_extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    default_user: typing.Optional[builtins.str] = None,
    default_user_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    key_id_format: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_before_duration: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__35bd6b612bdd6f55bc33f92cb68c032873d708c579af8a988041c9778dea6804(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a1cb76a3cb9c1ff358c2532bf07d95acdcc456202ce620ba679b7ec48ce0874(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SshSecretBackendRoleAllowedUserKeyConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__045e474b97256a4c803f20110667655464973f7b73b2b72de11356974aba1f26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e0bd9e7d2f899c243c32ab9308098c90fce13538f6bb2309d1a61813e7b7c85(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e116b84be64fc27fcb2d3e5234abd8c53c3a611055a6afc437ffb1c84e63767(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81b8175c2e21a96b809209bf2ef0f6cc9ec96b59a0bb0af57c5670aacf3655a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6e35fc2e5d0567540a0c7518599c0ad2840435ce29a90bac2b237e2fa89a3b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab1e4883f73dfadc1ff76238f624955af7f674c46b89d1273fc987a0b156f48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d59793a34d0af4bac5264e821825be34605512d114f710eeeaf24c3a00e1b42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8026bcac79f7f443bbe773885052ca515a5e0a8cdd3122e031ccc2eb7d5c27bf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754c20429a3b46712a202c998cd14dc812b810ed993bf2ca689c7973a6da754e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9461459f9983a9356ac5823864974090ba5b4163035e4e7a5353524b534dd8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__380ee19bcbf9724e7613371e6401ee8283745b3e56edef61335a53eb508bdac4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__950ccb720da8ebd8cdb527e5c6f6b4f16e6331cc743d10390aaab0e266c469d3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91097e2a3b316b15b3774d8cfe529483521eff2b84968d45a2ec9b269f81f30c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d215028cb12f1fda669d2c790a6a6e8ea18a584767f23e8169987c24ebfae00d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca95aa84be2317a2c8153f260f4e1551dae19216039c7eec416fd5db49fc0da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c46a8b0c4a7fa1c529c85e37e3278cb3ec4d588db689c6b1b9c51327c93339b1(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7800f5d212be38299bb84f253cb323d65ee18cfaf391e6738a8b58f84f376e1(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__304a9c5db7e3bd1fe14bf8d0e4db2c77e5b3295d0a411a2ca4a110f7664c0933(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c641ca51d0f29581f38b0db0de38e34a51699fe2fddf3fb1870987c51033a86(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971245d7310af4ae082fde1d503c585687c86d61a19385bc3970362a0b4de7fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52be35765eb81f659fed273268910bcb72ad0fa575b23cf905cacdb1b5948552(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e70353de2a88634f4945559ea90269cd23247aef1f5739ea1a49c964836340(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdd9b3fede80c409cebd6588572bce86632bb389901a1b32dff0869b62f5cfb8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cae3e7b0f078fe29d7c20d9bf56848698675725ff6d4164b238c43876b42d8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b71412e3c88ced9f630085f473b20356f5f3dd2f6ddb7b33cc048e56bdf3c08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__819cd6e64afd67602b45fa55b6271701a0fef0212407615dfb70f9c91bfb8413(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84ae399c7307e95912a27f8bd72fcf0a983c6bd491a5d4b115381095aacf7e55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a20480b6592cbc25ddbbe0b241dd087657a8f98da88928537430fc6502905f96(
    *,
    lengths: typing.Sequence[jsii.Number],
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__972666618294defc46c989459fa22873dcb28f6c26af2b93daf9073ecc2d4197(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a35aa91b425c1f75896f5e8a8f020cd90e691a2e9bd273badc255f4381602d69(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__062c76529f09d392a79bd5c5e5a93d5eadd444543cb5fba22e4e146f6e857057(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e65709a2d058fab64c5ddce38b678fcc9a38d02cc40b1e917240535f613459d1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c13fbc5c8b0e8632bfd2eeec6cb5e4ecdc5a4db203639d143ee1ebce9ab9804(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b854de1d024cdb981ff750892b8f78b7794a0e675ca4b2997a7370598fb03678(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[SshSecretBackendRoleAllowedUserKeyConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c1d20cd597a8834bb21253eae5d7ed6d46bf3e24e04aad9f0a44ab0360e336a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d44050be820525c0bba926b98eb2c74d0243ba564d4ecab7b601ddf3eb507f6f(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb62a8d59da5b4382fc111f9f31994df088b4b6e04dd2a094fa824e25e58cf13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51cb5dc67f79c27be423ff9f5664a4e27ba54aaa1c5e99e279276f0e184a4155(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, SshSecretBackendRoleAllowedUserKeyConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da1526537ffae42c40b816625649f1731b0295630b34629a604dde72602f4f94(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    key_type: builtins.str,
    name: builtins.str,
    algorithm_signer: typing.Optional[builtins.str] = None,
    allow_bare_domains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_critical_options: typing.Optional[builtins.str] = None,
    allowed_domains: typing.Optional[builtins.str] = None,
    allowed_domains_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_extensions: typing.Optional[builtins.str] = None,
    allowed_user_key_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[SshSecretBackendRoleAllowedUserKeyConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_users: typing.Optional[builtins.str] = None,
    allowed_users_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_empty_principals: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_host_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_user_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_user_key_ids: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cidr_list: typing.Optional[builtins.str] = None,
    default_critical_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    default_extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    default_user: typing.Optional[builtins.str] = None,
    default_user_template: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    key_id_format: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_before_duration: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
