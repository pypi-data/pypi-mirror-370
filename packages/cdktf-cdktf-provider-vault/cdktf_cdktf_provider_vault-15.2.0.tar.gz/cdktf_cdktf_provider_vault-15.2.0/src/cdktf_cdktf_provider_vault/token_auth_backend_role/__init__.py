r'''
# `vault_token_auth_backend_role`

Refer to the Terraform Registry for docs: [`vault_token_auth_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role).
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


class TokenAuthBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.tokenAuthBackendRole.TokenAuthBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role vault_token_auth_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        role_name: builtins.str,
        allowed_entity_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
        disallowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        disallowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        orphan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        path_suffix: typing.Optional[builtins.str] = None,
        renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role vault_token_auth_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#role_name TokenAuthBackendRole#role_name}
        :param allowed_entity_aliases: Set of allowed entity aliases for this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_entity_aliases TokenAuthBackendRole#allowed_entity_aliases}
        :param allowed_policies: List of allowed policies for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_policies TokenAuthBackendRole#allowed_policies}
        :param allowed_policies_glob: Set of allowed policies with glob match for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_policies_glob TokenAuthBackendRole#allowed_policies_glob}
        :param disallowed_policies: List of disallowed policies for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#disallowed_policies TokenAuthBackendRole#disallowed_policies}
        :param disallowed_policies_glob: Set of disallowed policies with glob match for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#disallowed_policies_glob TokenAuthBackendRole#disallowed_policies_glob}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#id TokenAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#namespace TokenAuthBackendRole#namespace}
        :param orphan: If true, tokens created against this policy will be orphan tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#orphan TokenAuthBackendRole#orphan}
        :param path_suffix: Tokens created against this role will have the given suffix as part of their path in addition to the role name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#path_suffix TokenAuthBackendRole#path_suffix}
        :param renewable: Whether to disable the ability of the token to be renewed past its initial TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#renewable TokenAuthBackendRole#renewable}
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_bound_cidrs TokenAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_explicit_max_ttl TokenAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_max_ttl TokenAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_no_default_policy TokenAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_num_uses TokenAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_period TokenAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_policies TokenAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_ttl TokenAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_type TokenAuthBackendRole#token_type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c11e4307c02dc0db58adfce516305b46bf9a50995abcdcfb28779b586b1cc1e4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TokenAuthBackendRoleConfig(
            role_name=role_name,
            allowed_entity_aliases=allowed_entity_aliases,
            allowed_policies=allowed_policies,
            allowed_policies_glob=allowed_policies_glob,
            disallowed_policies=disallowed_policies,
            disallowed_policies_glob=disallowed_policies_glob,
            id=id,
            namespace=namespace,
            orphan=orphan,
            path_suffix=path_suffix,
            renewable=renewable,
            token_bound_cidrs=token_bound_cidrs,
            token_explicit_max_ttl=token_explicit_max_ttl,
            token_max_ttl=token_max_ttl,
            token_no_default_policy=token_no_default_policy,
            token_num_uses=token_num_uses,
            token_period=token_period,
            token_policies=token_policies,
            token_ttl=token_ttl,
            token_type=token_type,
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
        '''Generates CDKTF code for importing a TokenAuthBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TokenAuthBackendRole to import.
        :param import_from_id: The id of the existing TokenAuthBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TokenAuthBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3828f0765a7d119162edfae72950bc160503e5dac0ecc039cf5c3abc3d9ec88e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedEntityAliases")
    def reset_allowed_entity_aliases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedEntityAliases", []))

    @jsii.member(jsii_name="resetAllowedPolicies")
    def reset_allowed_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedPolicies", []))

    @jsii.member(jsii_name="resetAllowedPoliciesGlob")
    def reset_allowed_policies_glob(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedPoliciesGlob", []))

    @jsii.member(jsii_name="resetDisallowedPolicies")
    def reset_disallowed_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisallowedPolicies", []))

    @jsii.member(jsii_name="resetDisallowedPoliciesGlob")
    def reset_disallowed_policies_glob(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisallowedPoliciesGlob", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOrphan")
    def reset_orphan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrphan", []))

    @jsii.member(jsii_name="resetPathSuffix")
    def reset_path_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathSuffix", []))

    @jsii.member(jsii_name="resetRenewable")
    def reset_renewable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenewable", []))

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
    @jsii.member(jsii_name="allowedEntityAliasesInput")
    def allowed_entity_aliases_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedEntityAliasesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedPoliciesGlobInput")
    def allowed_policies_glob_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedPoliciesGlobInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedPoliciesInput")
    def allowed_policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="disallowedPoliciesGlobInput")
    def disallowed_policies_glob_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "disallowedPoliciesGlobInput"))

    @builtins.property
    @jsii.member(jsii_name="disallowedPoliciesInput")
    def disallowed_policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "disallowedPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="orphanInput")
    def orphan_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "orphanInput"))

    @builtins.property
    @jsii.member(jsii_name="pathSuffixInput")
    def path_suffix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="renewableInput")
    def renewable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "renewableInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

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
    @jsii.member(jsii_name="allowedEntityAliases")
    def allowed_entity_aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedEntityAliases"))

    @allowed_entity_aliases.setter
    def allowed_entity_aliases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__161de41fed83aad05b6f4df566cdf35b11fb4bab7db05e1f7322033defd5e9d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedEntityAliases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedPolicies")
    def allowed_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedPolicies"))

    @allowed_policies.setter
    def allowed_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__463bba10c7795b272d9996b3f40d98a7070a996738780e6e658c33abab6580cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedPoliciesGlob")
    def allowed_policies_glob(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedPoliciesGlob"))

    @allowed_policies_glob.setter
    def allowed_policies_glob(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d02989843daad9624a95f1f6ada681931fd671fd766c0acb10338d9a1923d209)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedPoliciesGlob", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disallowedPolicies")
    def disallowed_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "disallowedPolicies"))

    @disallowed_policies.setter
    def disallowed_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efe69972f5741170875f47c1b2e8b056554a6810bfcba98009ca3b81b64fc224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disallowedPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disallowedPoliciesGlob")
    def disallowed_policies_glob(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "disallowedPoliciesGlob"))

    @disallowed_policies_glob.setter
    def disallowed_policies_glob(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__516109f703af99b499967efeea38afed7524f989b835972ef86031dc0b38c8f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disallowedPoliciesGlob", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b6cf9d07ffbc62f6fb38b3938005f6e8c11b3bd5cd5c432462927eb9737a6d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3902c38d4a88ea2f6548f62b0f48558830b9ad8d7ec7be4564f47ef898cd6cf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="orphan")
    def orphan(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "orphan"))

    @orphan.setter
    def orphan(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a20ad52cb7dbfdf2e2149c52a39d98ced669bb69d6bbcab40fe98b2519b301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "orphan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathSuffix")
    def path_suffix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathSuffix"))

    @path_suffix.setter
    def path_suffix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb5f3dbaa5ba0fb2a9798e703cccddea571a8268b6d4c7c4607c49844a60d529)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathSuffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewable")
    def renewable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "renewable"))

    @renewable.setter
    def renewable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8fa0b9d9e8bc7a5626750867d5491529ce34814e9b4d565687718c0c3abf78a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36bd2f07dde8afecd4c506ef85da58f09a77c4399c642f58a6a3d62a1d099b16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenBoundCidrs")
    def token_bound_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenBoundCidrs"))

    @token_bound_cidrs.setter
    def token_bound_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaa922bd0cf195a6f32ffb24c1bd031664f22d51e0a11ca071a5501d9e298d4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenBoundCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenExplicitMaxTtl")
    def token_explicit_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenExplicitMaxTtl"))

    @token_explicit_max_ttl.setter
    def token_explicit_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c15ccbd2a19c8405cd9d78e571f477cf58111d6172779028f98e4b5fc3a4d5e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenExplicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtl")
    def token_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenMaxTtl"))

    @token_max_ttl.setter
    def token_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1e201f9f756ff6c84e9218b96440264be15ae64648fbdc3068f7be86cd7cbdb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b46372b5023c5f93b04dab1217b57d77087e260eeac2a9aeb9a4eb4d7697c3ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNoDefaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNumUses")
    def token_num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenNumUses"))

    @token_num_uses.setter
    def token_num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4137fc7850ed7d1ffc3dd05cbd9c9a58dc2eaa05ac03241d1eb0c901e336d4da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNumUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPeriod")
    def token_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenPeriod"))

    @token_period.setter
    def token_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7e13fe0b2d219d5edcec9db88a02ee8e75a8e225169382d6d6371c18129c432)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPolicies")
    def token_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenPolicies"))

    @token_policies.setter
    def token_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b7d786ae6591218753dbc84cc8008a43ed173b59629a5e52354fba804bd1473)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenTtl")
    def token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenTtl"))

    @token_ttl.setter
    def token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__803fe8305b844c17aab23d0eda60d0673267ae374704a9988b3ce6ea0a606215)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenType")
    def token_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenType"))

    @token_type.setter
    def token_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b686d18d6f8edb749dbb503f805d487e080a6bc1d61d1dbf6eb367fde69de4db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenType", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.tokenAuthBackendRole.TokenAuthBackendRoleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "role_name": "roleName",
        "allowed_entity_aliases": "allowedEntityAliases",
        "allowed_policies": "allowedPolicies",
        "allowed_policies_glob": "allowedPoliciesGlob",
        "disallowed_policies": "disallowedPolicies",
        "disallowed_policies_glob": "disallowedPoliciesGlob",
        "id": "id",
        "namespace": "namespace",
        "orphan": "orphan",
        "path_suffix": "pathSuffix",
        "renewable": "renewable",
        "token_bound_cidrs": "tokenBoundCidrs",
        "token_explicit_max_ttl": "tokenExplicitMaxTtl",
        "token_max_ttl": "tokenMaxTtl",
        "token_no_default_policy": "tokenNoDefaultPolicy",
        "token_num_uses": "tokenNumUses",
        "token_period": "tokenPeriod",
        "token_policies": "tokenPolicies",
        "token_ttl": "tokenTtl",
        "token_type": "tokenType",
    },
)
class TokenAuthBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        role_name: builtins.str,
        allowed_entity_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
        disallowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        disallowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        orphan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        path_suffix: typing.Optional[builtins.str] = None,
        renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#role_name TokenAuthBackendRole#role_name}
        :param allowed_entity_aliases: Set of allowed entity aliases for this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_entity_aliases TokenAuthBackendRole#allowed_entity_aliases}
        :param allowed_policies: List of allowed policies for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_policies TokenAuthBackendRole#allowed_policies}
        :param allowed_policies_glob: Set of allowed policies with glob match for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_policies_glob TokenAuthBackendRole#allowed_policies_glob}
        :param disallowed_policies: List of disallowed policies for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#disallowed_policies TokenAuthBackendRole#disallowed_policies}
        :param disallowed_policies_glob: Set of disallowed policies with glob match for given role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#disallowed_policies_glob TokenAuthBackendRole#disallowed_policies_glob}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#id TokenAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#namespace TokenAuthBackendRole#namespace}
        :param orphan: If true, tokens created against this policy will be orphan tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#orphan TokenAuthBackendRole#orphan}
        :param path_suffix: Tokens created against this role will have the given suffix as part of their path in addition to the role name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#path_suffix TokenAuthBackendRole#path_suffix}
        :param renewable: Whether to disable the ability of the token to be renewed past its initial TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#renewable TokenAuthBackendRole#renewable}
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_bound_cidrs TokenAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_explicit_max_ttl TokenAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_max_ttl TokenAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_no_default_policy TokenAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_num_uses TokenAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_period TokenAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_policies TokenAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_ttl TokenAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_type TokenAuthBackendRole#token_type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73bafb7ef5f28be9c93355b2ad6810b31e084ac24d073c6d64991c62a0fed382)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument allowed_entity_aliases", value=allowed_entity_aliases, expected_type=type_hints["allowed_entity_aliases"])
            check_type(argname="argument allowed_policies", value=allowed_policies, expected_type=type_hints["allowed_policies"])
            check_type(argname="argument allowed_policies_glob", value=allowed_policies_glob, expected_type=type_hints["allowed_policies_glob"])
            check_type(argname="argument disallowed_policies", value=disallowed_policies, expected_type=type_hints["disallowed_policies"])
            check_type(argname="argument disallowed_policies_glob", value=disallowed_policies_glob, expected_type=type_hints["disallowed_policies_glob"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument orphan", value=orphan, expected_type=type_hints["orphan"])
            check_type(argname="argument path_suffix", value=path_suffix, expected_type=type_hints["path_suffix"])
            check_type(argname="argument renewable", value=renewable, expected_type=type_hints["renewable"])
            check_type(argname="argument token_bound_cidrs", value=token_bound_cidrs, expected_type=type_hints["token_bound_cidrs"])
            check_type(argname="argument token_explicit_max_ttl", value=token_explicit_max_ttl, expected_type=type_hints["token_explicit_max_ttl"])
            check_type(argname="argument token_max_ttl", value=token_max_ttl, expected_type=type_hints["token_max_ttl"])
            check_type(argname="argument token_no_default_policy", value=token_no_default_policy, expected_type=type_hints["token_no_default_policy"])
            check_type(argname="argument token_num_uses", value=token_num_uses, expected_type=type_hints["token_num_uses"])
            check_type(argname="argument token_period", value=token_period, expected_type=type_hints["token_period"])
            check_type(argname="argument token_policies", value=token_policies, expected_type=type_hints["token_policies"])
            check_type(argname="argument token_ttl", value=token_ttl, expected_type=type_hints["token_ttl"])
            check_type(argname="argument token_type", value=token_type, expected_type=type_hints["token_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_name": role_name,
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
        if allowed_entity_aliases is not None:
            self._values["allowed_entity_aliases"] = allowed_entity_aliases
        if allowed_policies is not None:
            self._values["allowed_policies"] = allowed_policies
        if allowed_policies_glob is not None:
            self._values["allowed_policies_glob"] = allowed_policies_glob
        if disallowed_policies is not None:
            self._values["disallowed_policies"] = disallowed_policies
        if disallowed_policies_glob is not None:
            self._values["disallowed_policies_glob"] = disallowed_policies_glob
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if orphan is not None:
            self._values["orphan"] = orphan
        if path_suffix is not None:
            self._values["path_suffix"] = path_suffix
        if renewable is not None:
            self._values["renewable"] = renewable
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
    def role_name(self) -> builtins.str:
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#role_name TokenAuthBackendRole#role_name}
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_entity_aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of allowed entity aliases for this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_entity_aliases TokenAuthBackendRole#allowed_entity_aliases}
        '''
        result = self._values.get("allowed_entity_aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of allowed policies for given role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_policies TokenAuthBackendRole#allowed_policies}
        '''
        result = self._values.get("allowed_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_policies_glob(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of allowed policies with glob match for given role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#allowed_policies_glob TokenAuthBackendRole#allowed_policies_glob}
        '''
        result = self._values.get("allowed_policies_glob")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disallowed_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of disallowed policies for given role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#disallowed_policies TokenAuthBackendRole#disallowed_policies}
        '''
        result = self._values.get("disallowed_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def disallowed_policies_glob(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of disallowed policies with glob match for given role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#disallowed_policies_glob TokenAuthBackendRole#disallowed_policies_glob}
        '''
        result = self._values.get("disallowed_policies_glob")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#id TokenAuthBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#namespace TokenAuthBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def orphan(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, tokens created against this policy will be orphan tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#orphan TokenAuthBackendRole#orphan}
        '''
        result = self._values.get("orphan")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def path_suffix(self) -> typing.Optional[builtins.str]:
        '''Tokens created against this role will have the given suffix as part of their path in addition to the role name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#path_suffix TokenAuthBackendRole#path_suffix}
        '''
        result = self._values.get("path_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def renewable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to disable the ability of the token to be renewed past its initial TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#renewable TokenAuthBackendRole#renewable}
        '''
        result = self._values.get("renewable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_bound_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the blocks of IP addresses which are allowed to use the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_bound_cidrs TokenAuthBackendRole#token_bound_cidrs}
        '''
        result = self._values.get("token_bound_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_explicit_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Explicit Maximum TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_explicit_max_ttl TokenAuthBackendRole#token_explicit_max_ttl}
        '''
        result = self._values.get("token_explicit_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''The maximum lifetime of the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_max_ttl TokenAuthBackendRole#token_max_ttl}
        '''
        result = self._values.get("token_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_no_default_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the 'default' policy will not automatically be added to generated tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_no_default_policy TokenAuthBackendRole#token_no_default_policy}
        '''
        result = self._values.get("token_no_default_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_num_uses(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times a token may be used, a value of zero means unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_num_uses TokenAuthBackendRole#token_num_uses}
        '''
        result = self._values.get("token_num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_period(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_period TokenAuthBackendRole#token_period}
        '''
        result = self._values.get("token_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Generated Token's Policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_policies TokenAuthBackendRole#token_policies}
        '''
        result = self._values.get("token_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The initial ttl of the token to generate in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_ttl TokenAuthBackendRole#token_ttl}
        '''
        result = self._values.get("token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_type(self) -> typing.Optional[builtins.str]:
        '''The type of token to generate, service or batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token_auth_backend_role#token_type TokenAuthBackendRole#token_type}
        '''
        result = self._values.get("token_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TokenAuthBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TokenAuthBackendRole",
    "TokenAuthBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__c11e4307c02dc0db58adfce516305b46bf9a50995abcdcfb28779b586b1cc1e4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    role_name: builtins.str,
    allowed_entity_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
    disallowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    disallowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    orphan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    path_suffix: typing.Optional[builtins.str] = None,
    renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__3828f0765a7d119162edfae72950bc160503e5dac0ecc039cf5c3abc3d9ec88e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__161de41fed83aad05b6f4df566cdf35b11fb4bab7db05e1f7322033defd5e9d9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__463bba10c7795b272d9996b3f40d98a7070a996738780e6e658c33abab6580cb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d02989843daad9624a95f1f6ada681931fd671fd766c0acb10338d9a1923d209(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efe69972f5741170875f47c1b2e8b056554a6810bfcba98009ca3b81b64fc224(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__516109f703af99b499967efeea38afed7524f989b835972ef86031dc0b38c8f0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6cf9d07ffbc62f6fb38b3938005f6e8c11b3bd5cd5c432462927eb9737a6d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3902c38d4a88ea2f6548f62b0f48558830b9ad8d7ec7be4564f47ef898cd6cf1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a20ad52cb7dbfdf2e2149c52a39d98ced669bb69d6bbcab40fe98b2519b301(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb5f3dbaa5ba0fb2a9798e703cccddea571a8268b6d4c7c4607c49844a60d529(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8fa0b9d9e8bc7a5626750867d5491529ce34814e9b4d565687718c0c3abf78a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36bd2f07dde8afecd4c506ef85da58f09a77c4399c642f58a6a3d62a1d099b16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaa922bd0cf195a6f32ffb24c1bd031664f22d51e0a11ca071a5501d9e298d4c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c15ccbd2a19c8405cd9d78e571f477cf58111d6172779028f98e4b5fc3a4d5e7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1e201f9f756ff6c84e9218b96440264be15ae64648fbdc3068f7be86cd7cbdb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46372b5023c5f93b04dab1217b57d77087e260eeac2a9aeb9a4eb4d7697c3ba(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4137fc7850ed7d1ffc3dd05cbd9c9a58dc2eaa05ac03241d1eb0c901e336d4da(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7e13fe0b2d219d5edcec9db88a02ee8e75a8e225169382d6d6371c18129c432(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b7d786ae6591218753dbc84cc8008a43ed173b59629a5e52354fba804bd1473(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__803fe8305b844c17aab23d0eda60d0673267ae374704a9988b3ce6ea0a606215(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b686d18d6f8edb749dbb503f805d487e080a6bc1d61d1dbf6eb367fde69de4db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73bafb7ef5f28be9c93355b2ad6810b31e084ac24d073c6d64991c62a0fed382(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    role_name: builtins.str,
    allowed_entity_aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
    disallowed_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    disallowed_policies_glob: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    orphan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    path_suffix: typing.Optional[builtins.str] = None,
    renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
