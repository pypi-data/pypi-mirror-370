r'''
# `vault_jwt_auth_backend_role`

Refer to the Terraform Registry for docs: [`vault_jwt_auth_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role).
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


class JwtAuthBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.jwtAuthBackendRole.JwtAuthBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role vault_jwt_auth_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        role_name: builtins.str,
        user_claim: builtins.str,
        allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        backend: typing.Optional[builtins.str] = None,
        bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_claims: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bound_claims_type: typing.Optional[builtins.str] = None,
        bound_subject: typing.Optional[builtins.str] = None,
        claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        clock_skew_leeway: typing.Optional[jsii.Number] = None,
        disable_bound_claims_parsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiration_leeway: typing.Optional[jsii.Number] = None,
        groups_claim: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_age: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_before_leeway: typing.Optional[jsii.Number] = None,
        oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        role_type: typing.Optional[builtins.str] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
        user_claim_json_pointer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        verbose_oidc_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role vault_jwt_auth_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#role_name JwtAuthBackendRole#role_name}
        :param user_claim: The claim to use to uniquely identify the user; this will be used as the name for the Identity entity alias created due to a successful login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#user_claim JwtAuthBackendRole#user_claim}
        :param allowed_redirect_uris: The list of allowed values for redirect_uri during OIDC logins. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#allowed_redirect_uris JwtAuthBackendRole#allowed_redirect_uris}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#backend JwtAuthBackendRole#backend}
        :param bound_audiences: List of aud claims to match against. Any match is sufficient. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_audiences JwtAuthBackendRole#bound_audiences}
        :param bound_claims: Map of claims/values to match against. The expected value may be a single string or a comma-separated string list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_claims JwtAuthBackendRole#bound_claims}
        :param bound_claims_type: How to interpret values in the claims/values map: can be either "string" (exact match) or "glob" (wildcard match). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_claims_type JwtAuthBackendRole#bound_claims_type}
        :param bound_subject: If set, requires that the sub claim matches this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_subject JwtAuthBackendRole#bound_subject}
        :param claim_mappings: Map of claims (keys) to be copied to specified metadata fields (values). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#claim_mappings JwtAuthBackendRole#claim_mappings}
        :param clock_skew_leeway: The amount of leeway to add to all claims to account for clock skew, in seconds. Defaults to 60 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#clock_skew_leeway JwtAuthBackendRole#clock_skew_leeway}
        :param disable_bound_claims_parsing: Disable bound claim value parsing. Useful when values contain commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#disable_bound_claims_parsing JwtAuthBackendRole#disable_bound_claims_parsing}
        :param expiration_leeway: The amount of leeway to add to expiration (exp) claims to account for clock skew, in seconds. Defaults to 150 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#expiration_leeway JwtAuthBackendRole#expiration_leeway}
        :param groups_claim: The claim to use to uniquely identify the set of groups to which the user belongs; this will be used as the names for the Identity group aliases created due to a successful login. The claim value must be a list of strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#groups_claim JwtAuthBackendRole#groups_claim}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#id JwtAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_age: Specifies the allowable elapsed time in seconds since the last time the user was actively authenticated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#max_age JwtAuthBackendRole#max_age}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#namespace JwtAuthBackendRole#namespace}
        :param not_before_leeway: The amount of leeway to add to not before (nbf) claims to account for clock skew, in seconds. Defaults to 150 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#not_before_leeway JwtAuthBackendRole#not_before_leeway}
        :param oidc_scopes: List of OIDC scopes to be used with an OIDC role. The standard scope "openid" is automatically included and need not be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#oidc_scopes JwtAuthBackendRole#oidc_scopes}
        :param role_type: Type of role, either "oidc" (default) or "jwt". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#role_type JwtAuthBackendRole#role_type}
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_bound_cidrs JwtAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_explicit_max_ttl JwtAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_max_ttl JwtAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_no_default_policy JwtAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_num_uses JwtAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_period JwtAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_policies JwtAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_ttl JwtAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_type JwtAuthBackendRole#token_type}
        :param user_claim_json_pointer: Specifies if the user_claim value uses JSON pointer syntax for referencing claims. By default, the user_claim value will not use JSON pointer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#user_claim_json_pointer JwtAuthBackendRole#user_claim_json_pointer}
        :param verbose_oidc_logging: Log received OIDC tokens and claims when debug-level logging is active. Not recommended in production since sensitive information may be present in OIDC responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#verbose_oidc_logging JwtAuthBackendRole#verbose_oidc_logging}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e42435fc4e09ef809949b47750e457559fc156d2bac3436d8aa0b11ec8f19610)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = JwtAuthBackendRoleConfig(
            role_name=role_name,
            user_claim=user_claim,
            allowed_redirect_uris=allowed_redirect_uris,
            backend=backend,
            bound_audiences=bound_audiences,
            bound_claims=bound_claims,
            bound_claims_type=bound_claims_type,
            bound_subject=bound_subject,
            claim_mappings=claim_mappings,
            clock_skew_leeway=clock_skew_leeway,
            disable_bound_claims_parsing=disable_bound_claims_parsing,
            expiration_leeway=expiration_leeway,
            groups_claim=groups_claim,
            id=id,
            max_age=max_age,
            namespace=namespace,
            not_before_leeway=not_before_leeway,
            oidc_scopes=oidc_scopes,
            role_type=role_type,
            token_bound_cidrs=token_bound_cidrs,
            token_explicit_max_ttl=token_explicit_max_ttl,
            token_max_ttl=token_max_ttl,
            token_no_default_policy=token_no_default_policy,
            token_num_uses=token_num_uses,
            token_period=token_period,
            token_policies=token_policies,
            token_ttl=token_ttl,
            token_type=token_type,
            user_claim_json_pointer=user_claim_json_pointer,
            verbose_oidc_logging=verbose_oidc_logging,
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
        '''Generates CDKTF code for importing a JwtAuthBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the JwtAuthBackendRole to import.
        :param import_from_id: The id of the existing JwtAuthBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the JwtAuthBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce44aafd40249dc625fb957e99077abcad97969e44505e65e6d2df077f8af608)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedRedirectUris")
    def reset_allowed_redirect_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedRedirectUris", []))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetBoundAudiences")
    def reset_bound_audiences(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundAudiences", []))

    @jsii.member(jsii_name="resetBoundClaims")
    def reset_bound_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundClaims", []))

    @jsii.member(jsii_name="resetBoundClaimsType")
    def reset_bound_claims_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundClaimsType", []))

    @jsii.member(jsii_name="resetBoundSubject")
    def reset_bound_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSubject", []))

    @jsii.member(jsii_name="resetClaimMappings")
    def reset_claim_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClaimMappings", []))

    @jsii.member(jsii_name="resetClockSkewLeeway")
    def reset_clock_skew_leeway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClockSkewLeeway", []))

    @jsii.member(jsii_name="resetDisableBoundClaimsParsing")
    def reset_disable_bound_claims_parsing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableBoundClaimsParsing", []))

    @jsii.member(jsii_name="resetExpirationLeeway")
    def reset_expiration_leeway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationLeeway", []))

    @jsii.member(jsii_name="resetGroupsClaim")
    def reset_groups_claim(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupsClaim", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxAge")
    def reset_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAge", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNotBeforeLeeway")
    def reset_not_before_leeway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotBeforeLeeway", []))

    @jsii.member(jsii_name="resetOidcScopes")
    def reset_oidc_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcScopes", []))

    @jsii.member(jsii_name="resetRoleType")
    def reset_role_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleType", []))

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

    @jsii.member(jsii_name="resetUserClaimJsonPointer")
    def reset_user_claim_json_pointer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserClaimJsonPointer", []))

    @jsii.member(jsii_name="resetVerboseOidcLogging")
    def reset_verbose_oidc_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerboseOidcLogging", []))

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
    @jsii.member(jsii_name="allowedRedirectUrisInput")
    def allowed_redirect_uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedRedirectUrisInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="boundAudiencesInput")
    def bound_audiences_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundAudiencesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundClaimsInput")
    def bound_claims_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "boundClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundClaimsTypeInput")
    def bound_claims_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "boundClaimsTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSubjectInput")
    def bound_subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "boundSubjectInput"))

    @builtins.property
    @jsii.member(jsii_name="claimMappingsInput")
    def claim_mappings_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "claimMappingsInput"))

    @builtins.property
    @jsii.member(jsii_name="clockSkewLeewayInput")
    def clock_skew_leeway_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clockSkewLeewayInput"))

    @builtins.property
    @jsii.member(jsii_name="disableBoundClaimsParsingInput")
    def disable_bound_claims_parsing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableBoundClaimsParsingInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationLeewayInput")
    def expiration_leeway_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expirationLeewayInput"))

    @builtins.property
    @jsii.member(jsii_name="groupsClaimInput")
    def groups_claim_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupsClaimInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAgeInput")
    def max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="notBeforeLeewayInput")
    def not_before_leeway_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "notBeforeLeewayInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcScopesInput")
    def oidc_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "oidcScopesInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="roleTypeInput")
    def role_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleTypeInput"))

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
    @jsii.member(jsii_name="userClaimInput")
    def user_claim_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userClaimInput"))

    @builtins.property
    @jsii.member(jsii_name="userClaimJsonPointerInput")
    def user_claim_json_pointer_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "userClaimJsonPointerInput"))

    @builtins.property
    @jsii.member(jsii_name="verboseOidcLoggingInput")
    def verbose_oidc_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "verboseOidcLoggingInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedRedirectUris")
    def allowed_redirect_uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedRedirectUris"))

    @allowed_redirect_uris.setter
    def allowed_redirect_uris(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a2080573c1f47b1f141c2c97f3dce33a8a2ea2a646cf3b567a24bc2e4e75b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedRedirectUris", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2543102c50df1e1c81d53f4a60cb0913769039d4a9b8f578e088f0fa11f3fb12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundAudiences")
    def bound_audiences(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundAudiences"))

    @bound_audiences.setter
    def bound_audiences(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a040f7a990992b3a5727142bab769056e1ab854ae9571b43c2bdb43818ded6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundAudiences", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundClaims")
    def bound_claims(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "boundClaims"))

    @bound_claims.setter
    def bound_claims(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93236b64e008e1b23a2ef28237140252c9f8d4482d93a6c3b87dafba819319ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundClaims", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundClaimsType")
    def bound_claims_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "boundClaimsType"))

    @bound_claims_type.setter
    def bound_claims_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fb20983002fdd87d50e296ebd309c45e177a1074a9d40f9e02afcc52b1423af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundClaimsType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundSubject")
    def bound_subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "boundSubject"))

    @bound_subject.setter
    def bound_subject(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__394801c2e809dbb0461e052ff4d42337bc55eda28fbbebaefb35262dd6ef9b64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSubject", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimMappings")
    def claim_mappings(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "claimMappings"))

    @claim_mappings.setter
    def claim_mappings(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7f25756fa41c8faec019f904a596a313056f232deedf318d2acf668616a763)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimMappings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clockSkewLeeway")
    def clock_skew_leeway(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clockSkewLeeway"))

    @clock_skew_leeway.setter
    def clock_skew_leeway(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64435529d52b9db87f299a8bdffa31203af5cde42c68fc7e4c4a2d00c5182963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clockSkewLeeway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableBoundClaimsParsing")
    def disable_bound_claims_parsing(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableBoundClaimsParsing"))

    @disable_bound_claims_parsing.setter
    def disable_bound_claims_parsing(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__874645d8e7715e3eb9d301580507d0710f5bd0f8c415a39427f88e92e2806bb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableBoundClaimsParsing", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expirationLeeway")
    def expiration_leeway(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expirationLeeway"))

    @expiration_leeway.setter
    def expiration_leeway(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e4e2a2218dd1d116a8d357dc2c987f50e78a559e8505db2afd359e5df1f5fa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationLeeway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupsClaim")
    def groups_claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupsClaim"))

    @groups_claim.setter
    def groups_claim(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ec2eff9e661800f030dc11900653afb3ab1c642234b9d0689ac1f5c7fa6dafb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupsClaim", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e84bd856fcb4688e6b4d2a084bf44931a7c2855258def7af0dabcb131024e04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAge")
    def max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAge"))

    @max_age.setter
    def max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06299276cc0a2a04660c30a5aae6d4f6cb2a995b8291304f704a34f095a6b2d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__371d44c153a2ee66481f4bd1192b3cda94d56314f4d32603c748661f64e034e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notBeforeLeeway")
    def not_before_leeway(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "notBeforeLeeway"))

    @not_before_leeway.setter
    def not_before_leeway(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f740b7a6a4542f9e4d96be927c043e17737f8cd75c7b8a7bf6cc69d0fbee69c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notBeforeLeeway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcScopes")
    def oidc_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "oidcScopes"))

    @oidc_scopes.setter
    def oidc_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8052d1eedef4f2d018ddab4a551d21cb3c84df109074dc8f6dd002678fca1cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcScopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c92a286057790c0105804e4233930592be4fb90be44d07d7ebda6ec0083e4bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleType")
    def role_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleType"))

    @role_type.setter
    def role_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6940588dc09191dfc8d674055a77fd2ea5b7f8e137d1dc29f7d9f0cd428cc6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenBoundCidrs")
    def token_bound_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenBoundCidrs"))

    @token_bound_cidrs.setter
    def token_bound_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62ed495fa47833bb676760b44e9af662c13cd85b4255009952c4448b5d8c8ebf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenBoundCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenExplicitMaxTtl")
    def token_explicit_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenExplicitMaxTtl"))

    @token_explicit_max_ttl.setter
    def token_explicit_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb321a4aee27134fea6f2c707d432fdac1564cfc3082c9f252a14043974537bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenExplicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtl")
    def token_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenMaxTtl"))

    @token_max_ttl.setter
    def token_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2532a07e4583375a396061f6ef2ca555cca1fc1dd8ba6f6064c6a37e1be97bab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__abadd1efa7ff7f263097267f085040aceb2437f31b29d3e72b14c264892683b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNoDefaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNumUses")
    def token_num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenNumUses"))

    @token_num_uses.setter
    def token_num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ba51a3b4a8b84fc6fc8b048fbf5fa90e5a1d07fb58d5bd1d37e40e153ae5329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNumUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPeriod")
    def token_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenPeriod"))

    @token_period.setter
    def token_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b63ded186a793c98c4b61607f2f00563f6334e79c0b02eda6cf4faee22fc4757)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPolicies")
    def token_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenPolicies"))

    @token_policies.setter
    def token_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e23abad51e73ec588cc004f24506679614037e0d3a724fa217b92b768ad832)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenTtl")
    def token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenTtl"))

    @token_ttl.setter
    def token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32b77b51fc828ccc62d1248a909dcbcc89b9d5d5fc9198459163a79ea69e5ac5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenType")
    def token_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenType"))

    @token_type.setter
    def token_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__948b92d8ae17dcc5d4e006e0265b7b1800059e65766c564aa08ba747d2edd28e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userClaim")
    def user_claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userClaim"))

    @user_claim.setter
    def user_claim(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e76c139b326b319e38ac82e5f59009acd1fa030cbacb1b6c2a06bf9012325fa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userClaim", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userClaimJsonPointer")
    def user_claim_json_pointer(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "userClaimJsonPointer"))

    @user_claim_json_pointer.setter
    def user_claim_json_pointer(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62334b8cdaece3680d3fcaf054f2107eef8e08045e04ce8b09dfa0c651001935)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userClaimJsonPointer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="verboseOidcLogging")
    def verbose_oidc_logging(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "verboseOidcLogging"))

    @verbose_oidc_logging.setter
    def verbose_oidc_logging(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee199b1e0624baa352594910100f6b5a89e8beaf4006ff5c136c3cf13e210cfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verboseOidcLogging", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.jwtAuthBackendRole.JwtAuthBackendRoleConfig",
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
        "user_claim": "userClaim",
        "allowed_redirect_uris": "allowedRedirectUris",
        "backend": "backend",
        "bound_audiences": "boundAudiences",
        "bound_claims": "boundClaims",
        "bound_claims_type": "boundClaimsType",
        "bound_subject": "boundSubject",
        "claim_mappings": "claimMappings",
        "clock_skew_leeway": "clockSkewLeeway",
        "disable_bound_claims_parsing": "disableBoundClaimsParsing",
        "expiration_leeway": "expirationLeeway",
        "groups_claim": "groupsClaim",
        "id": "id",
        "max_age": "maxAge",
        "namespace": "namespace",
        "not_before_leeway": "notBeforeLeeway",
        "oidc_scopes": "oidcScopes",
        "role_type": "roleType",
        "token_bound_cidrs": "tokenBoundCidrs",
        "token_explicit_max_ttl": "tokenExplicitMaxTtl",
        "token_max_ttl": "tokenMaxTtl",
        "token_no_default_policy": "tokenNoDefaultPolicy",
        "token_num_uses": "tokenNumUses",
        "token_period": "tokenPeriod",
        "token_policies": "tokenPolicies",
        "token_ttl": "tokenTtl",
        "token_type": "tokenType",
        "user_claim_json_pointer": "userClaimJsonPointer",
        "verbose_oidc_logging": "verboseOidcLogging",
    },
)
class JwtAuthBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        user_claim: builtins.str,
        allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        backend: typing.Optional[builtins.str] = None,
        bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_claims: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        bound_claims_type: typing.Optional[builtins.str] = None,
        bound_subject: typing.Optional[builtins.str] = None,
        claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        clock_skew_leeway: typing.Optional[jsii.Number] = None,
        disable_bound_claims_parsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiration_leeway: typing.Optional[jsii.Number] = None,
        groups_claim: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_age: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        not_before_leeway: typing.Optional[jsii.Number] = None,
        oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        role_type: typing.Optional[builtins.str] = None,
        token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        token_num_uses: typing.Optional[jsii.Number] = None,
        token_period: typing.Optional[jsii.Number] = None,
        token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_ttl: typing.Optional[jsii.Number] = None,
        token_type: typing.Optional[builtins.str] = None,
        user_claim_json_pointer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        verbose_oidc_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#role_name JwtAuthBackendRole#role_name}
        :param user_claim: The claim to use to uniquely identify the user; this will be used as the name for the Identity entity alias created due to a successful login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#user_claim JwtAuthBackendRole#user_claim}
        :param allowed_redirect_uris: The list of allowed values for redirect_uri during OIDC logins. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#allowed_redirect_uris JwtAuthBackendRole#allowed_redirect_uris}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#backend JwtAuthBackendRole#backend}
        :param bound_audiences: List of aud claims to match against. Any match is sufficient. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_audiences JwtAuthBackendRole#bound_audiences}
        :param bound_claims: Map of claims/values to match against. The expected value may be a single string or a comma-separated string list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_claims JwtAuthBackendRole#bound_claims}
        :param bound_claims_type: How to interpret values in the claims/values map: can be either "string" (exact match) or "glob" (wildcard match). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_claims_type JwtAuthBackendRole#bound_claims_type}
        :param bound_subject: If set, requires that the sub claim matches this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_subject JwtAuthBackendRole#bound_subject}
        :param claim_mappings: Map of claims (keys) to be copied to specified metadata fields (values). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#claim_mappings JwtAuthBackendRole#claim_mappings}
        :param clock_skew_leeway: The amount of leeway to add to all claims to account for clock skew, in seconds. Defaults to 60 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#clock_skew_leeway JwtAuthBackendRole#clock_skew_leeway}
        :param disable_bound_claims_parsing: Disable bound claim value parsing. Useful when values contain commas. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#disable_bound_claims_parsing JwtAuthBackendRole#disable_bound_claims_parsing}
        :param expiration_leeway: The amount of leeway to add to expiration (exp) claims to account for clock skew, in seconds. Defaults to 150 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#expiration_leeway JwtAuthBackendRole#expiration_leeway}
        :param groups_claim: The claim to use to uniquely identify the set of groups to which the user belongs; this will be used as the names for the Identity group aliases created due to a successful login. The claim value must be a list of strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#groups_claim JwtAuthBackendRole#groups_claim}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#id JwtAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_age: Specifies the allowable elapsed time in seconds since the last time the user was actively authenticated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#max_age JwtAuthBackendRole#max_age}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#namespace JwtAuthBackendRole#namespace}
        :param not_before_leeway: The amount of leeway to add to not before (nbf) claims to account for clock skew, in seconds. Defaults to 150 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#not_before_leeway JwtAuthBackendRole#not_before_leeway}
        :param oidc_scopes: List of OIDC scopes to be used with an OIDC role. The standard scope "openid" is automatically included and need not be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#oidc_scopes JwtAuthBackendRole#oidc_scopes}
        :param role_type: Type of role, either "oidc" (default) or "jwt". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#role_type JwtAuthBackendRole#role_type}
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_bound_cidrs JwtAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_explicit_max_ttl JwtAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_max_ttl JwtAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_no_default_policy JwtAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_num_uses JwtAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_period JwtAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_policies JwtAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_ttl JwtAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_type JwtAuthBackendRole#token_type}
        :param user_claim_json_pointer: Specifies if the user_claim value uses JSON pointer syntax for referencing claims. By default, the user_claim value will not use JSON pointer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#user_claim_json_pointer JwtAuthBackendRole#user_claim_json_pointer}
        :param verbose_oidc_logging: Log received OIDC tokens and claims when debug-level logging is active. Not recommended in production since sensitive information may be present in OIDC responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#verbose_oidc_logging JwtAuthBackendRole#verbose_oidc_logging}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed5d7adf85af741502b13d2755290ba1cdff0452496de22a45f4863f538d6331)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument user_claim", value=user_claim, expected_type=type_hints["user_claim"])
            check_type(argname="argument allowed_redirect_uris", value=allowed_redirect_uris, expected_type=type_hints["allowed_redirect_uris"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument bound_audiences", value=bound_audiences, expected_type=type_hints["bound_audiences"])
            check_type(argname="argument bound_claims", value=bound_claims, expected_type=type_hints["bound_claims"])
            check_type(argname="argument bound_claims_type", value=bound_claims_type, expected_type=type_hints["bound_claims_type"])
            check_type(argname="argument bound_subject", value=bound_subject, expected_type=type_hints["bound_subject"])
            check_type(argname="argument claim_mappings", value=claim_mappings, expected_type=type_hints["claim_mappings"])
            check_type(argname="argument clock_skew_leeway", value=clock_skew_leeway, expected_type=type_hints["clock_skew_leeway"])
            check_type(argname="argument disable_bound_claims_parsing", value=disable_bound_claims_parsing, expected_type=type_hints["disable_bound_claims_parsing"])
            check_type(argname="argument expiration_leeway", value=expiration_leeway, expected_type=type_hints["expiration_leeway"])
            check_type(argname="argument groups_claim", value=groups_claim, expected_type=type_hints["groups_claim"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_age", value=max_age, expected_type=type_hints["max_age"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument not_before_leeway", value=not_before_leeway, expected_type=type_hints["not_before_leeway"])
            check_type(argname="argument oidc_scopes", value=oidc_scopes, expected_type=type_hints["oidc_scopes"])
            check_type(argname="argument role_type", value=role_type, expected_type=type_hints["role_type"])
            check_type(argname="argument token_bound_cidrs", value=token_bound_cidrs, expected_type=type_hints["token_bound_cidrs"])
            check_type(argname="argument token_explicit_max_ttl", value=token_explicit_max_ttl, expected_type=type_hints["token_explicit_max_ttl"])
            check_type(argname="argument token_max_ttl", value=token_max_ttl, expected_type=type_hints["token_max_ttl"])
            check_type(argname="argument token_no_default_policy", value=token_no_default_policy, expected_type=type_hints["token_no_default_policy"])
            check_type(argname="argument token_num_uses", value=token_num_uses, expected_type=type_hints["token_num_uses"])
            check_type(argname="argument token_period", value=token_period, expected_type=type_hints["token_period"])
            check_type(argname="argument token_policies", value=token_policies, expected_type=type_hints["token_policies"])
            check_type(argname="argument token_ttl", value=token_ttl, expected_type=type_hints["token_ttl"])
            check_type(argname="argument token_type", value=token_type, expected_type=type_hints["token_type"])
            check_type(argname="argument user_claim_json_pointer", value=user_claim_json_pointer, expected_type=type_hints["user_claim_json_pointer"])
            check_type(argname="argument verbose_oidc_logging", value=verbose_oidc_logging, expected_type=type_hints["verbose_oidc_logging"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_name": role_name,
            "user_claim": user_claim,
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
        if allowed_redirect_uris is not None:
            self._values["allowed_redirect_uris"] = allowed_redirect_uris
        if backend is not None:
            self._values["backend"] = backend
        if bound_audiences is not None:
            self._values["bound_audiences"] = bound_audiences
        if bound_claims is not None:
            self._values["bound_claims"] = bound_claims
        if bound_claims_type is not None:
            self._values["bound_claims_type"] = bound_claims_type
        if bound_subject is not None:
            self._values["bound_subject"] = bound_subject
        if claim_mappings is not None:
            self._values["claim_mappings"] = claim_mappings
        if clock_skew_leeway is not None:
            self._values["clock_skew_leeway"] = clock_skew_leeway
        if disable_bound_claims_parsing is not None:
            self._values["disable_bound_claims_parsing"] = disable_bound_claims_parsing
        if expiration_leeway is not None:
            self._values["expiration_leeway"] = expiration_leeway
        if groups_claim is not None:
            self._values["groups_claim"] = groups_claim
        if id is not None:
            self._values["id"] = id
        if max_age is not None:
            self._values["max_age"] = max_age
        if namespace is not None:
            self._values["namespace"] = namespace
        if not_before_leeway is not None:
            self._values["not_before_leeway"] = not_before_leeway
        if oidc_scopes is not None:
            self._values["oidc_scopes"] = oidc_scopes
        if role_type is not None:
            self._values["role_type"] = role_type
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
        if user_claim_json_pointer is not None:
            self._values["user_claim_json_pointer"] = user_claim_json_pointer
        if verbose_oidc_logging is not None:
            self._values["verbose_oidc_logging"] = verbose_oidc_logging

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#role_name JwtAuthBackendRole#role_name}
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_claim(self) -> builtins.str:
        '''The claim to use to uniquely identify the user;

        this will be used as the name for the Identity entity alias created due to a successful login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#user_claim JwtAuthBackendRole#user_claim}
        '''
        result = self._values.get("user_claim")
        assert result is not None, "Required property 'user_claim' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_redirect_uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of allowed values for redirect_uri during OIDC logins.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#allowed_redirect_uris JwtAuthBackendRole#allowed_redirect_uris}
        '''
        result = self._values.get("allowed_redirect_uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the auth backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#backend JwtAuthBackendRole#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bound_audiences(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of aud claims to match against. Any match is sufficient.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_audiences JwtAuthBackendRole#bound_audiences}
        '''
        result = self._values.get("bound_audiences")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_claims(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Map of claims/values to match against. The expected value may be a single string or a comma-separated string list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_claims JwtAuthBackendRole#bound_claims}
        '''
        result = self._values.get("bound_claims")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def bound_claims_type(self) -> typing.Optional[builtins.str]:
        '''How to interpret values in the claims/values map: can be either "string" (exact match) or "glob" (wildcard match).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_claims_type JwtAuthBackendRole#bound_claims_type}
        '''
        result = self._values.get("bound_claims_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bound_subject(self) -> typing.Optional[builtins.str]:
        '''If set, requires that the sub claim matches this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#bound_subject JwtAuthBackendRole#bound_subject}
        '''
        result = self._values.get("bound_subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def claim_mappings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Map of claims (keys) to be copied to specified metadata fields (values).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#claim_mappings JwtAuthBackendRole#claim_mappings}
        '''
        result = self._values.get("claim_mappings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def clock_skew_leeway(self) -> typing.Optional[jsii.Number]:
        '''The amount of leeway to add to all claims to account for clock skew, in seconds.

        Defaults to 60 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#clock_skew_leeway JwtAuthBackendRole#clock_skew_leeway}
        '''
        result = self._values.get("clock_skew_leeway")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disable_bound_claims_parsing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable bound claim value parsing. Useful when values contain commas.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#disable_bound_claims_parsing JwtAuthBackendRole#disable_bound_claims_parsing}
        '''
        result = self._values.get("disable_bound_claims_parsing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def expiration_leeway(self) -> typing.Optional[jsii.Number]:
        '''The amount of leeway to add to expiration (exp) claims to account for clock skew, in seconds.

        Defaults to 150 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#expiration_leeway JwtAuthBackendRole#expiration_leeway}
        '''
        result = self._values.get("expiration_leeway")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def groups_claim(self) -> typing.Optional[builtins.str]:
        '''The claim to use to uniquely identify the set of groups to which the user belongs;

        this will be used as the names for the Identity group aliases created due to a successful login. The claim value must be a list of strings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#groups_claim JwtAuthBackendRole#groups_claim}
        '''
        result = self._values.get("groups_claim")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#id JwtAuthBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_age(self) -> typing.Optional[jsii.Number]:
        '''Specifies the allowable elapsed time in seconds since the last time the user was actively authenticated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#max_age JwtAuthBackendRole#max_age}
        '''
        result = self._values.get("max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#namespace JwtAuthBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_before_leeway(self) -> typing.Optional[jsii.Number]:
        '''The amount of leeway to add to not before (nbf) claims to account for clock skew, in seconds.

        Defaults to 150 seconds if set to 0 and can be disabled if set to -1. Only applicable with 'jwt' roles.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#not_before_leeway JwtAuthBackendRole#not_before_leeway}
        '''
        result = self._values.get("not_before_leeway")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def oidc_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of OIDC scopes to be used with an OIDC role.

        The standard scope "openid" is automatically included and need not be specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#oidc_scopes JwtAuthBackendRole#oidc_scopes}
        '''
        result = self._values.get("oidc_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def role_type(self) -> typing.Optional[builtins.str]:
        '''Type of role, either "oidc" (default) or "jwt".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#role_type JwtAuthBackendRole#role_type}
        '''
        result = self._values.get("role_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_bound_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the blocks of IP addresses which are allowed to use the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_bound_cidrs JwtAuthBackendRole#token_bound_cidrs}
        '''
        result = self._values.get("token_bound_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_explicit_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Explicit Maximum TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_explicit_max_ttl JwtAuthBackendRole#token_explicit_max_ttl}
        '''
        result = self._values.get("token_explicit_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''The maximum lifetime of the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_max_ttl JwtAuthBackendRole#token_max_ttl}
        '''
        result = self._values.get("token_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_no_default_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the 'default' policy will not automatically be added to generated tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_no_default_policy JwtAuthBackendRole#token_no_default_policy}
        '''
        result = self._values.get("token_no_default_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_num_uses(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times a token may be used, a value of zero means unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_num_uses JwtAuthBackendRole#token_num_uses}
        '''
        result = self._values.get("token_num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_period(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_period JwtAuthBackendRole#token_period}
        '''
        result = self._values.get("token_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Generated Token's Policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_policies JwtAuthBackendRole#token_policies}
        '''
        result = self._values.get("token_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The initial ttl of the token to generate in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_ttl JwtAuthBackendRole#token_ttl}
        '''
        result = self._values.get("token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_type(self) -> typing.Optional[builtins.str]:
        '''The type of token to generate, service or batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#token_type JwtAuthBackendRole#token_type}
        '''
        result = self._values.get("token_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_claim_json_pointer(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if the user_claim value uses JSON pointer syntax for referencing claims.

        By default, the user_claim value will not use JSON pointer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#user_claim_json_pointer JwtAuthBackendRole#user_claim_json_pointer}
        '''
        result = self._values.get("user_claim_json_pointer")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def verbose_oidc_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Log received OIDC tokens and claims when debug-level logging is active.

        Not recommended in production since sensitive information may be present in OIDC responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/jwt_auth_backend_role#verbose_oidc_logging JwtAuthBackendRole#verbose_oidc_logging}
        '''
        result = self._values.get("verbose_oidc_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JwtAuthBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "JwtAuthBackendRole",
    "JwtAuthBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__e42435fc4e09ef809949b47750e457559fc156d2bac3436d8aa0b11ec8f19610(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    role_name: builtins.str,
    user_claim: builtins.str,
    allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    backend: typing.Optional[builtins.str] = None,
    bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_claims: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    bound_claims_type: typing.Optional[builtins.str] = None,
    bound_subject: typing.Optional[builtins.str] = None,
    claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    clock_skew_leeway: typing.Optional[jsii.Number] = None,
    disable_bound_claims_parsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiration_leeway: typing.Optional[jsii.Number] = None,
    groups_claim: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_age: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_before_leeway: typing.Optional[jsii.Number] = None,
    oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    role_type: typing.Optional[builtins.str] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
    user_claim_json_pointer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    verbose_oidc_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__ce44aafd40249dc625fb957e99077abcad97969e44505e65e6d2df077f8af608(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a2080573c1f47b1f141c2c97f3dce33a8a2ea2a646cf3b567a24bc2e4e75b0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2543102c50df1e1c81d53f4a60cb0913769039d4a9b8f578e088f0fa11f3fb12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a040f7a990992b3a5727142bab769056e1ab854ae9571b43c2bdb43818ded6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93236b64e008e1b23a2ef28237140252c9f8d4482d93a6c3b87dafba819319ac(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fb20983002fdd87d50e296ebd309c45e177a1074a9d40f9e02afcc52b1423af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__394801c2e809dbb0461e052ff4d42337bc55eda28fbbebaefb35262dd6ef9b64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7f25756fa41c8faec019f904a596a313056f232deedf318d2acf668616a763(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64435529d52b9db87f299a8bdffa31203af5cde42c68fc7e4c4a2d00c5182963(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__874645d8e7715e3eb9d301580507d0710f5bd0f8c415a39427f88e92e2806bb2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e4e2a2218dd1d116a8d357dc2c987f50e78a559e8505db2afd359e5df1f5fa9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ec2eff9e661800f030dc11900653afb3ab1c642234b9d0689ac1f5c7fa6dafb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e84bd856fcb4688e6b4d2a084bf44931a7c2855258def7af0dabcb131024e04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06299276cc0a2a04660c30a5aae6d4f6cb2a995b8291304f704a34f095a6b2d3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__371d44c153a2ee66481f4bd1192b3cda94d56314f4d32603c748661f64e034e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f740b7a6a4542f9e4d96be927c043e17737f8cd75c7b8a7bf6cc69d0fbee69c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8052d1eedef4f2d018ddab4a551d21cb3c84df109074dc8f6dd002678fca1cde(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c92a286057790c0105804e4233930592be4fb90be44d07d7ebda6ec0083e4bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6940588dc09191dfc8d674055a77fd2ea5b7f8e137d1dc29f7d9f0cd428cc6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62ed495fa47833bb676760b44e9af662c13cd85b4255009952c4448b5d8c8ebf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb321a4aee27134fea6f2c707d432fdac1564cfc3082c9f252a14043974537bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2532a07e4583375a396061f6ef2ca555cca1fc1dd8ba6f6064c6a37e1be97bab(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abadd1efa7ff7f263097267f085040aceb2437f31b29d3e72b14c264892683b0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ba51a3b4a8b84fc6fc8b048fbf5fa90e5a1d07fb58d5bd1d37e40e153ae5329(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b63ded186a793c98c4b61607f2f00563f6334e79c0b02eda6cf4faee22fc4757(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4e23abad51e73ec588cc004f24506679614037e0d3a724fa217b92b768ad832(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b77b51fc828ccc62d1248a909dcbcc89b9d5d5fc9198459163a79ea69e5ac5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__948b92d8ae17dcc5d4e006e0265b7b1800059e65766c564aa08ba747d2edd28e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76c139b326b319e38ac82e5f59009acd1fa030cbacb1b6c2a06bf9012325fa1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62334b8cdaece3680d3fcaf054f2107eef8e08045e04ce8b09dfa0c651001935(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee199b1e0624baa352594910100f6b5a89e8beaf4006ff5c136c3cf13e210cfd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed5d7adf85af741502b13d2755290ba1cdff0452496de22a45f4863f538d6331(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    role_name: builtins.str,
    user_claim: builtins.str,
    allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    backend: typing.Optional[builtins.str] = None,
    bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_claims: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    bound_claims_type: typing.Optional[builtins.str] = None,
    bound_subject: typing.Optional[builtins.str] = None,
    claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    clock_skew_leeway: typing.Optional[jsii.Number] = None,
    disable_bound_claims_parsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiration_leeway: typing.Optional[jsii.Number] = None,
    groups_claim: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_age: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    not_before_leeway: typing.Optional[jsii.Number] = None,
    oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    role_type: typing.Optional[builtins.str] = None,
    token_bound_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_explicit_max_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
    token_no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    token_num_uses: typing.Optional[jsii.Number] = None,
    token_period: typing.Optional[jsii.Number] = None,
    token_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_ttl: typing.Optional[jsii.Number] = None,
    token_type: typing.Optional[builtins.str] = None,
    user_claim_json_pointer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    verbose_oidc_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
