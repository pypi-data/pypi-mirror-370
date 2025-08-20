r'''
# `vault_azure_auth_backend_role`

Refer to the Terraform Registry for docs: [`vault_azure_auth_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role).
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


class AzureAuthBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.azureAuthBackendRole.AzureAuthBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role vault_azure_auth_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        role: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        bound_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_scale_sets: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_service_principal_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_subscription_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role vault_azure_auth_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#role AzureAuthBackendRole#role}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#backend AzureAuthBackendRole#backend}
        :param bound_group_ids: The list of group ids that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_group_ids AzureAuthBackendRole#bound_group_ids}
        :param bound_locations: The list of locations that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_locations AzureAuthBackendRole#bound_locations}
        :param bound_resource_groups: The list of resource groups that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_resource_groups AzureAuthBackendRole#bound_resource_groups}
        :param bound_scale_sets: The list of scale set names that the login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_scale_sets AzureAuthBackendRole#bound_scale_sets}
        :param bound_service_principal_ids: The list of Service Principal IDs that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_service_principal_ids AzureAuthBackendRole#bound_service_principal_ids}
        :param bound_subscription_ids: The list of subscription IDs that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_subscription_ids AzureAuthBackendRole#bound_subscription_ids}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#id AzureAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#namespace AzureAuthBackendRole#namespace}
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_bound_cidrs AzureAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_explicit_max_ttl AzureAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_max_ttl AzureAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_no_default_policy AzureAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_num_uses AzureAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_period AzureAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_policies AzureAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_ttl AzureAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_type AzureAuthBackendRole#token_type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec166bc6aca30993e18b9ee7b4c337d7564e599ac15a469bdf36390daebb721)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AzureAuthBackendRoleConfig(
            role=role,
            backend=backend,
            bound_group_ids=bound_group_ids,
            bound_locations=bound_locations,
            bound_resource_groups=bound_resource_groups,
            bound_scale_sets=bound_scale_sets,
            bound_service_principal_ids=bound_service_principal_ids,
            bound_subscription_ids=bound_subscription_ids,
            id=id,
            namespace=namespace,
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
        '''Generates CDKTF code for importing a AzureAuthBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AzureAuthBackendRole to import.
        :param import_from_id: The id of the existing AzureAuthBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AzureAuthBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfb0d99855e5974f54f68f32b7c5e965272d6cabf8ed5254908802ea52b66b0b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetBoundGroupIds")
    def reset_bound_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundGroupIds", []))

    @jsii.member(jsii_name="resetBoundLocations")
    def reset_bound_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundLocations", []))

    @jsii.member(jsii_name="resetBoundResourceGroups")
    def reset_bound_resource_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceGroups", []))

    @jsii.member(jsii_name="resetBoundScaleSets")
    def reset_bound_scale_sets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundScaleSets", []))

    @jsii.member(jsii_name="resetBoundServicePrincipalIds")
    def reset_bound_service_principal_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundServicePrincipalIds", []))

    @jsii.member(jsii_name="resetBoundSubscriptionIds")
    def reset_bound_subscription_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSubscriptionIds", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

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
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="boundGroupIdsInput")
    def bound_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundGroupIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundLocationsInput")
    def bound_locations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceGroupsInput")
    def bound_resource_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundScaleSetsInput")
    def bound_scale_sets_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundScaleSetsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundServicePrincipalIdsInput")
    def bound_service_principal_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundServicePrincipalIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSubscriptionIdsInput")
    def bound_subscription_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundSubscriptionIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

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
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d4e1e40e651291c988ace17a09bb9b630f1d270cd23d3d1ee06e7cbb6b74836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundGroupIds")
    def bound_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundGroupIds"))

    @bound_group_ids.setter
    def bound_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__446e8785192c7f138049180373737ca44ba85a421b5daf9e1513e2b54925625a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundGroupIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundLocations")
    def bound_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundLocations"))

    @bound_locations.setter
    def bound_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020898514a12f489fa41a89c0d972a2fdcee245d2ee44095e79379955fc80f60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundLocations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundResourceGroups")
    def bound_resource_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceGroups"))

    @bound_resource_groups.setter
    def bound_resource_groups(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51f9364bcdcaaf0e754902ed2a50c91ce106e459fd8a0e66070b95a4aa59d3f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceGroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundScaleSets")
    def bound_scale_sets(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundScaleSets"))

    @bound_scale_sets.setter
    def bound_scale_sets(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8262f02c0bbdc8454dfcc17a7fea43c47a93c99360e122a1c684e70bae7b22f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundScaleSets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundServicePrincipalIds")
    def bound_service_principal_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundServicePrincipalIds"))

    @bound_service_principal_ids.setter
    def bound_service_principal_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87dee7d4d42503fbcbe52150c2e983af87dc39b9c5a02613142eeb95075d9299)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundServicePrincipalIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundSubscriptionIds")
    def bound_subscription_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundSubscriptionIds"))

    @bound_subscription_ids.setter
    def bound_subscription_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14602bfc07dc84161f2b227ed292ccfb882b4470b3aacd557d7057b2eb7228ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSubscriptionIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a3227a4845dfd54f5ff184772248f4a33347627b11eeb6fc8fdebed658ea6c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34a1901ff395720232872fe7b332b29618487f83ac0da7cd7cb7d81df3852f0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac8caed60d258dc18546002eb74071e3180371d37a219ecb1519cc0afcc3cca8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenBoundCidrs")
    def token_bound_cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenBoundCidrs"))

    @token_bound_cidrs.setter
    def token_bound_cidrs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6761fa3539659c61a48f87e15a6de98ffa4148c5c821e21cc56eb82438dac9c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenBoundCidrs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenExplicitMaxTtl")
    def token_explicit_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenExplicitMaxTtl"))

    @token_explicit_max_ttl.setter
    def token_explicit_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c41d74cfdcb35b4c2303e50043ad5dccd01849d8647eb1d323c4a363fba915bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenExplicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtl")
    def token_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenMaxTtl"))

    @token_max_ttl.setter
    def token_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c91faa350222b55f2652995d16f46fa30f9c0c525993bb9e7b6451eb43b82b1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__02479fbf5096793ff3f87e0fcc03b608f1ca5bab62aac37a8b141644ec1bb54e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNoDefaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNumUses")
    def token_num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenNumUses"))

    @token_num_uses.setter
    def token_num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb280a3e7993fcd23c7b93c12237cdae97461d1a85a9e69a2cef37392275f95d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNumUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPeriod")
    def token_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenPeriod"))

    @token_period.setter
    def token_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f47ed40d7175e8586250e2f2d0be3447ffd493e1b7e7779fb4ff4f15f9d055d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenPolicies")
    def token_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenPolicies"))

    @token_policies.setter
    def token_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3296a6e987f632f8e79a299aea84fe3981376849d65112faf9ac1192ec1dae02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenTtl")
    def token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenTtl"))

    @token_ttl.setter
    def token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b35737ef4cf908127fc29b1f07c8a8e0eb00bdcf6768224db559ef6dc3f41231)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenType")
    def token_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenType"))

    @token_type.setter
    def token_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca3df681ba2a96eac4d4b05d616bd68b82ade107f64d70e70d375af131ea183)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenType", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.azureAuthBackendRole.AzureAuthBackendRoleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "role": "role",
        "backend": "backend",
        "bound_group_ids": "boundGroupIds",
        "bound_locations": "boundLocations",
        "bound_resource_groups": "boundResourceGroups",
        "bound_scale_sets": "boundScaleSets",
        "bound_service_principal_ids": "boundServicePrincipalIds",
        "bound_subscription_ids": "boundSubscriptionIds",
        "id": "id",
        "namespace": "namespace",
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
class AzureAuthBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        role: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        bound_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_scale_sets: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_service_principal_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_subscription_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
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
        :param role: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#role AzureAuthBackendRole#role}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#backend AzureAuthBackendRole#backend}
        :param bound_group_ids: The list of group ids that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_group_ids AzureAuthBackendRole#bound_group_ids}
        :param bound_locations: The list of locations that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_locations AzureAuthBackendRole#bound_locations}
        :param bound_resource_groups: The list of resource groups that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_resource_groups AzureAuthBackendRole#bound_resource_groups}
        :param bound_scale_sets: The list of scale set names that the login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_scale_sets AzureAuthBackendRole#bound_scale_sets}
        :param bound_service_principal_ids: The list of Service Principal IDs that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_service_principal_ids AzureAuthBackendRole#bound_service_principal_ids}
        :param bound_subscription_ids: The list of subscription IDs that login is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_subscription_ids AzureAuthBackendRole#bound_subscription_ids}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#id AzureAuthBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#namespace AzureAuthBackendRole#namespace}
        :param token_bound_cidrs: Specifies the blocks of IP addresses which are allowed to use the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_bound_cidrs AzureAuthBackendRole#token_bound_cidrs}
        :param token_explicit_max_ttl: Generated Token's Explicit Maximum TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_explicit_max_ttl AzureAuthBackendRole#token_explicit_max_ttl}
        :param token_max_ttl: The maximum lifetime of the generated token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_max_ttl AzureAuthBackendRole#token_max_ttl}
        :param token_no_default_policy: If true, the 'default' policy will not automatically be added to generated tokens. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_no_default_policy AzureAuthBackendRole#token_no_default_policy}
        :param token_num_uses: The maximum number of times a token may be used, a value of zero means unlimited. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_num_uses AzureAuthBackendRole#token_num_uses}
        :param token_period: Generated Token's Period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_period AzureAuthBackendRole#token_period}
        :param token_policies: Generated Token's Policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_policies AzureAuthBackendRole#token_policies}
        :param token_ttl: The initial ttl of the token to generate in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_ttl AzureAuthBackendRole#token_ttl}
        :param token_type: The type of token to generate, service or batch. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_type AzureAuthBackendRole#token_type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b60a00ba10ee980ad50f720a9dd43ccc0e11c90790701c2b4af37ff7743b5753)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument bound_group_ids", value=bound_group_ids, expected_type=type_hints["bound_group_ids"])
            check_type(argname="argument bound_locations", value=bound_locations, expected_type=type_hints["bound_locations"])
            check_type(argname="argument bound_resource_groups", value=bound_resource_groups, expected_type=type_hints["bound_resource_groups"])
            check_type(argname="argument bound_scale_sets", value=bound_scale_sets, expected_type=type_hints["bound_scale_sets"])
            check_type(argname="argument bound_service_principal_ids", value=bound_service_principal_ids, expected_type=type_hints["bound_service_principal_ids"])
            check_type(argname="argument bound_subscription_ids", value=bound_subscription_ids, expected_type=type_hints["bound_subscription_ids"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
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
            "role": role,
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
        if backend is not None:
            self._values["backend"] = backend
        if bound_group_ids is not None:
            self._values["bound_group_ids"] = bound_group_ids
        if bound_locations is not None:
            self._values["bound_locations"] = bound_locations
        if bound_resource_groups is not None:
            self._values["bound_resource_groups"] = bound_resource_groups
        if bound_scale_sets is not None:
            self._values["bound_scale_sets"] = bound_scale_sets
        if bound_service_principal_ids is not None:
            self._values["bound_service_principal_ids"] = bound_service_principal_ids
        if bound_subscription_ids is not None:
            self._values["bound_subscription_ids"] = bound_subscription_ids
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
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
    def role(self) -> builtins.str:
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#role AzureAuthBackendRole#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the auth backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#backend AzureAuthBackendRole#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bound_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of group ids that login is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_group_ids AzureAuthBackendRole#bound_group_ids}
        '''
        result = self._values.get("bound_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_locations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of locations that login is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_locations AzureAuthBackendRole#bound_locations}
        '''
        result = self._values.get("bound_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of resource groups that login is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_resource_groups AzureAuthBackendRole#bound_resource_groups}
        '''
        result = self._values.get("bound_resource_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_scale_sets(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of scale set names that the login is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_scale_sets AzureAuthBackendRole#bound_scale_sets}
        '''
        result = self._values.get("bound_scale_sets")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_service_principal_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of Service Principal IDs that login is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_service_principal_ids AzureAuthBackendRole#bound_service_principal_ids}
        '''
        result = self._values.get("bound_service_principal_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_subscription_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of subscription IDs that login is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#bound_subscription_ids AzureAuthBackendRole#bound_subscription_ids}
        '''
        result = self._values.get("bound_subscription_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#id AzureAuthBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#namespace AzureAuthBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_bound_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specifies the blocks of IP addresses which are allowed to use the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_bound_cidrs AzureAuthBackendRole#token_bound_cidrs}
        '''
        result = self._values.get("token_bound_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_explicit_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Explicit Maximum TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_explicit_max_ttl AzureAuthBackendRole#token_explicit_max_ttl}
        '''
        result = self._values.get("token_explicit_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''The maximum lifetime of the generated token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_max_ttl AzureAuthBackendRole#token_max_ttl}
        '''
        result = self._values.get("token_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_no_default_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the 'default' policy will not automatically be added to generated tokens.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_no_default_policy AzureAuthBackendRole#token_no_default_policy}
        '''
        result = self._values.get("token_no_default_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def token_num_uses(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times a token may be used, a value of zero means unlimited.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_num_uses AzureAuthBackendRole#token_num_uses}
        '''
        result = self._values.get("token_num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_period(self) -> typing.Optional[jsii.Number]:
        '''Generated Token's Period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_period AzureAuthBackendRole#token_period}
        '''
        result = self._values.get("token_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Generated Token's Policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_policies AzureAuthBackendRole#token_policies}
        '''
        result = self._values.get("token_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The initial ttl of the token to generate in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_ttl AzureAuthBackendRole#token_ttl}
        '''
        result = self._values.get("token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_type(self) -> typing.Optional[builtins.str]:
        '''The type of token to generate, service or batch.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_auth_backend_role#token_type AzureAuthBackendRole#token_type}
        '''
        result = self._values.get("token_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AzureAuthBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AzureAuthBackendRole",
    "AzureAuthBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__aec166bc6aca30993e18b9ee7b4c337d7564e599ac15a469bdf36390daebb721(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    role: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    bound_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_scale_sets: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_service_principal_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_subscription_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__bfb0d99855e5974f54f68f32b7c5e965272d6cabf8ed5254908802ea52b66b0b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d4e1e40e651291c988ace17a09bb9b630f1d270cd23d3d1ee06e7cbb6b74836(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__446e8785192c7f138049180373737ca44ba85a421b5daf9e1513e2b54925625a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020898514a12f489fa41a89c0d972a2fdcee245d2ee44095e79379955fc80f60(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51f9364bcdcaaf0e754902ed2a50c91ce106e459fd8a0e66070b95a4aa59d3f7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8262f02c0bbdc8454dfcc17a7fea43c47a93c99360e122a1c684e70bae7b22f8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87dee7d4d42503fbcbe52150c2e983af87dc39b9c5a02613142eeb95075d9299(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14602bfc07dc84161f2b227ed292ccfb882b4470b3aacd557d7057b2eb7228ed(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a3227a4845dfd54f5ff184772248f4a33347627b11eeb6fc8fdebed658ea6c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a1901ff395720232872fe7b332b29618487f83ac0da7cd7cb7d81df3852f0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac8caed60d258dc18546002eb74071e3180371d37a219ecb1519cc0afcc3cca8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6761fa3539659c61a48f87e15a6de98ffa4148c5c821e21cc56eb82438dac9c7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c41d74cfdcb35b4c2303e50043ad5dccd01849d8647eb1d323c4a363fba915bb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c91faa350222b55f2652995d16f46fa30f9c0c525993bb9e7b6451eb43b82b1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02479fbf5096793ff3f87e0fcc03b608f1ca5bab62aac37a8b141644ec1bb54e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb280a3e7993fcd23c7b93c12237cdae97461d1a85a9e69a2cef37392275f95d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f47ed40d7175e8586250e2f2d0be3447ffd493e1b7e7779fb4ff4f15f9d055d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3296a6e987f632f8e79a299aea84fe3981376849d65112faf9ac1192ec1dae02(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35737ef4cf908127fc29b1f07c8a8e0eb00bdcf6768224db559ef6dc3f41231(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca3df681ba2a96eac4d4b05d616bd68b82ade107f64d70e70d375af131ea183(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60a00ba10ee980ad50f720a9dd43ccc0e11c90790701c2b4af37ff7743b5753(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    role: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    bound_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_scale_sets: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_service_principal_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_subscription_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
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
