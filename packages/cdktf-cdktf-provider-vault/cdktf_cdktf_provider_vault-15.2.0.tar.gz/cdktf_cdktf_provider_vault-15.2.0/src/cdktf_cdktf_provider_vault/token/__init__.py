r'''
# `vault_token`

Refer to the Terraform Registry for docs: [`vault_token`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token).
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


class Token(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.token.Token",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token vault_token}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        display_name: typing.Optional[builtins.str] = None,
        explicit_max_ttl: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_parent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        num_uses: typing.Optional[jsii.Number] = None,
        period: typing.Optional[builtins.str] = None,
        policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        renew_increment: typing.Optional[jsii.Number] = None,
        renew_min_lease: typing.Optional[jsii.Number] = None,
        role_name: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
        wrapping_ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token vault_token} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param display_name: The display name of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#display_name Token#display_name}
        :param explicit_max_ttl: The explicit max TTL of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#explicit_max_ttl Token#explicit_max_ttl}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#id Token#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metadata: Metadata to be associated with the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#metadata Token#metadata}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#namespace Token#namespace}
        :param no_default_policy: Flag to disable the default policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#no_default_policy Token#no_default_policy}
        :param no_parent: Flag to create a token without parent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#no_parent Token#no_parent}
        :param num_uses: The number of allowed uses of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#num_uses Token#num_uses}
        :param period: The period of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#period Token#period}
        :param policies: List of policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#policies Token#policies}
        :param renewable: Flag to allow the token to be renewed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renewable Token#renewable}
        :param renew_increment: The renew increment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renew_increment Token#renew_increment}
        :param renew_min_lease: The minimum lease to renew token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renew_min_lease Token#renew_min_lease}
        :param role_name: The token role name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#role_name Token#role_name}
        :param ttl: The TTL period of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#ttl Token#ttl}
        :param wrapping_ttl: The TTL period of the wrapped token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#wrapping_ttl Token#wrapping_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79bbcdf1c788a57a162b669c1dc161d86e837ced7bd9a95cf82a8a650f7a1816)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TokenConfig(
            display_name=display_name,
            explicit_max_ttl=explicit_max_ttl,
            id=id,
            metadata=metadata,
            namespace=namespace,
            no_default_policy=no_default_policy,
            no_parent=no_parent,
            num_uses=num_uses,
            period=period,
            policies=policies,
            renewable=renewable,
            renew_increment=renew_increment,
            renew_min_lease=renew_min_lease,
            role_name=role_name,
            ttl=ttl,
            wrapping_ttl=wrapping_ttl,
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
        '''Generates CDKTF code for importing a Token resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Token to import.
        :param import_from_id: The id of the existing Token that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Token to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a2b4fe05eb7de53c5c9d83d9f014525d5fc43fe5f16e1d5b57c9330fa3e1dd3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDisplayName")
    def reset_display_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisplayName", []))

    @jsii.member(jsii_name="resetExplicitMaxTtl")
    def reset_explicit_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExplicitMaxTtl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNoDefaultPolicy")
    def reset_no_default_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoDefaultPolicy", []))

    @jsii.member(jsii_name="resetNoParent")
    def reset_no_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoParent", []))

    @jsii.member(jsii_name="resetNumUses")
    def reset_num_uses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumUses", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetPolicies")
    def reset_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicies", []))

    @jsii.member(jsii_name="resetRenewable")
    def reset_renewable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenewable", []))

    @jsii.member(jsii_name="resetRenewIncrement")
    def reset_renew_increment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenewIncrement", []))

    @jsii.member(jsii_name="resetRenewMinLease")
    def reset_renew_min_lease(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRenewMinLease", []))

    @jsii.member(jsii_name="resetRoleName")
    def reset_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleName", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetWrappingTtl")
    def reset_wrapping_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWrappingTtl", []))

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
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientToken"))

    @builtins.property
    @jsii.member(jsii_name="leaseDuration")
    def lease_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "leaseDuration"))

    @builtins.property
    @jsii.member(jsii_name="leaseStarted")
    def lease_started(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "leaseStarted"))

    @builtins.property
    @jsii.member(jsii_name="wrappedToken")
    def wrapped_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wrappedToken"))

    @builtins.property
    @jsii.member(jsii_name="wrappingAccessor")
    def wrapping_accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wrappingAccessor"))

    @builtins.property
    @jsii.member(jsii_name="displayNameInput")
    def display_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "displayNameInput"))

    @builtins.property
    @jsii.member(jsii_name="explicitMaxTtlInput")
    def explicit_max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "explicitMaxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="noDefaultPolicyInput")
    def no_default_policy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noDefaultPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="noParentInput")
    def no_parent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noParentInput"))

    @builtins.property
    @jsii.member(jsii_name="numUsesInput")
    def num_uses_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numUsesInput"))

    @builtins.property
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "periodInput"))

    @builtins.property
    @jsii.member(jsii_name="policiesInput")
    def policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "policiesInput"))

    @builtins.property
    @jsii.member(jsii_name="renewableInput")
    def renewable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "renewableInput"))

    @builtins.property
    @jsii.member(jsii_name="renewIncrementInput")
    def renew_increment_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "renewIncrementInput"))

    @builtins.property
    @jsii.member(jsii_name="renewMinLeaseInput")
    def renew_min_lease_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "renewMinLeaseInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="wrappingTtlInput")
    def wrapping_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wrappingTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @display_name.setter
    def display_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d0c1438a789c8a3552e8b61d34b35d7ab05c93f56c3d8eced021e3fa51344e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "displayName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="explicitMaxTtl")
    def explicit_max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "explicitMaxTtl"))

    @explicit_max_ttl.setter
    def explicit_max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd629f1c9bfbd8d1880a520440011994fc6496b95a2feeb1e67d053451915b31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "explicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7226eee4c03f2952da448a7108efea4317059b06ca589c34547c5cb7a7fd049b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37757388b9f814597867bb14523a801816e9452327d8d8f93e2d76d767102de9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3fa5fb58f525e4d2f5adf3aea8769ca679c6ff98f5d68e6d21f8c0252383c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noDefaultPolicy")
    def no_default_policy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noDefaultPolicy"))

    @no_default_policy.setter
    def no_default_policy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4551e381a33fd82e9e90db8508c328c9264b8d03e12030623c726354f757de0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noDefaultPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noParent")
    def no_parent(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noParent"))

    @no_parent.setter
    def no_parent(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1907b2d22877ff891ed23b95ad8f9d78f17a9b6316f141f9e820410b01b27f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noParent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numUses")
    def num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numUses"))

    @num_uses.setter
    def num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d890420efc5296443cd8bac980c63c69105552090fce652ef744a6e84eaac63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "period"))

    @period.setter
    def period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c78ff6153b20f9378a0d5b34081de57d8c02bf0f63aba0d74f1302b6676271c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "policies"))

    @policies.setter
    def policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__768cdb809e2bddb7c915244763ac9a87f482d59e4a7ff2511de0ffd5b47c4979)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policies", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__fac9ab1b43d15ab487908c653e8e067d233b4f29be78990ce69ba9e20c5edca5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewIncrement")
    def renew_increment(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "renewIncrement"))

    @renew_increment.setter
    def renew_increment(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82673a59f238f7af77ccd65e2c1724fc1493c8d5e832cdd114af43d2e84962b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewIncrement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="renewMinLease")
    def renew_min_lease(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "renewMinLease"))

    @renew_min_lease.setter
    def renew_min_lease(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3822aaed2c4cd8d6896024eafa58dd05d664a22f2c32192f0b347086593471f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "renewMinLease", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84989ea7a52d149553bce0bd0e88093e17cae72df00dc52c85834bf2568730dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d8474c0a54344d3ee31e23d53b9ca67115d0ef40bd3a1685a7a0f5e7d2196f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrappingTtl")
    def wrapping_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wrappingTtl"))

    @wrapping_ttl.setter
    def wrapping_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06ff01cc004e67efac8905fc6f022bdbe005c35ab2162bfefd22dfb6913b2574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrappingTtl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.token.TokenConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "display_name": "displayName",
        "explicit_max_ttl": "explicitMaxTtl",
        "id": "id",
        "metadata": "metadata",
        "namespace": "namespace",
        "no_default_policy": "noDefaultPolicy",
        "no_parent": "noParent",
        "num_uses": "numUses",
        "period": "period",
        "policies": "policies",
        "renewable": "renewable",
        "renew_increment": "renewIncrement",
        "renew_min_lease": "renewMinLease",
        "role_name": "roleName",
        "ttl": "ttl",
        "wrapping_ttl": "wrappingTtl",
    },
)
class TokenConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        display_name: typing.Optional[builtins.str] = None,
        explicit_max_ttl: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        no_parent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        num_uses: typing.Optional[jsii.Number] = None,
        period: typing.Optional[builtins.str] = None,
        policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        renew_increment: typing.Optional[jsii.Number] = None,
        renew_min_lease: typing.Optional[jsii.Number] = None,
        role_name: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
        wrapping_ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param display_name: The display name of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#display_name Token#display_name}
        :param explicit_max_ttl: The explicit max TTL of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#explicit_max_ttl Token#explicit_max_ttl}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#id Token#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metadata: Metadata to be associated with the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#metadata Token#metadata}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#namespace Token#namespace}
        :param no_default_policy: Flag to disable the default policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#no_default_policy Token#no_default_policy}
        :param no_parent: Flag to create a token without parent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#no_parent Token#no_parent}
        :param num_uses: The number of allowed uses of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#num_uses Token#num_uses}
        :param period: The period of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#period Token#period}
        :param policies: List of policies. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#policies Token#policies}
        :param renewable: Flag to allow the token to be renewed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renewable Token#renewable}
        :param renew_increment: The renew increment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renew_increment Token#renew_increment}
        :param renew_min_lease: The minimum lease to renew token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renew_min_lease Token#renew_min_lease}
        :param role_name: The token role name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#role_name Token#role_name}
        :param ttl: The TTL period of the token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#ttl Token#ttl}
        :param wrapping_ttl: The TTL period of the wrapped token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#wrapping_ttl Token#wrapping_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c2ae7a93427084daecdc64f74d8598342bda3e16215fd3154cd4e9d5b4e9e84)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument explicit_max_ttl", value=explicit_max_ttl, expected_type=type_hints["explicit_max_ttl"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument no_default_policy", value=no_default_policy, expected_type=type_hints["no_default_policy"])
            check_type(argname="argument no_parent", value=no_parent, expected_type=type_hints["no_parent"])
            check_type(argname="argument num_uses", value=num_uses, expected_type=type_hints["num_uses"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument policies", value=policies, expected_type=type_hints["policies"])
            check_type(argname="argument renewable", value=renewable, expected_type=type_hints["renewable"])
            check_type(argname="argument renew_increment", value=renew_increment, expected_type=type_hints["renew_increment"])
            check_type(argname="argument renew_min_lease", value=renew_min_lease, expected_type=type_hints["renew_min_lease"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument wrapping_ttl", value=wrapping_ttl, expected_type=type_hints["wrapping_ttl"])
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
        if display_name is not None:
            self._values["display_name"] = display_name
        if explicit_max_ttl is not None:
            self._values["explicit_max_ttl"] = explicit_max_ttl
        if id is not None:
            self._values["id"] = id
        if metadata is not None:
            self._values["metadata"] = metadata
        if namespace is not None:
            self._values["namespace"] = namespace
        if no_default_policy is not None:
            self._values["no_default_policy"] = no_default_policy
        if no_parent is not None:
            self._values["no_parent"] = no_parent
        if num_uses is not None:
            self._values["num_uses"] = num_uses
        if period is not None:
            self._values["period"] = period
        if policies is not None:
            self._values["policies"] = policies
        if renewable is not None:
            self._values["renewable"] = renewable
        if renew_increment is not None:
            self._values["renew_increment"] = renew_increment
        if renew_min_lease is not None:
            self._values["renew_min_lease"] = renew_min_lease
        if role_name is not None:
            self._values["role_name"] = role_name
        if ttl is not None:
            self._values["ttl"] = ttl
        if wrapping_ttl is not None:
            self._values["wrapping_ttl"] = wrapping_ttl

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
    def display_name(self) -> typing.Optional[builtins.str]:
        '''The display name of the token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#display_name Token#display_name}
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def explicit_max_ttl(self) -> typing.Optional[builtins.str]:
        '''The explicit max TTL of the token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#explicit_max_ttl Token#explicit_max_ttl}
        '''
        result = self._values.get("explicit_max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#id Token#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Metadata to be associated with the token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#metadata Token#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#namespace Token#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_default_policy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to disable the default policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#no_default_policy Token#no_default_policy}
        '''
        result = self._values.get("no_default_policy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def no_parent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to create a token without parent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#no_parent Token#no_parent}
        '''
        result = self._values.get("no_parent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def num_uses(self) -> typing.Optional[jsii.Number]:
        '''The number of allowed uses of the token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#num_uses Token#num_uses}
        '''
        result = self._values.get("num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def period(self) -> typing.Optional[builtins.str]:
        '''The period of the token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#period Token#period}
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of policies.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#policies Token#policies}
        '''
        result = self._values.get("policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def renewable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to allow the token to be renewed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renewable Token#renewable}
        '''
        result = self._values.get("renewable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def renew_increment(self) -> typing.Optional[jsii.Number]:
        '''The renew increment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renew_increment Token#renew_increment}
        '''
        result = self._values.get("renew_increment")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def renew_min_lease(self) -> typing.Optional[jsii.Number]:
        '''The minimum lease to renew token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#renew_min_lease Token#renew_min_lease}
        '''
        result = self._values.get("renew_min_lease")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The token role name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#role_name Token#role_name}
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''The TTL period of the token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#ttl Token#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wrapping_ttl(self) -> typing.Optional[builtins.str]:
        '''The TTL period of the wrapped token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/token#wrapping_ttl Token#wrapping_ttl}
        '''
        result = self._values.get("wrapping_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TokenConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Token",
    "TokenConfig",
]

publication.publish()

def _typecheckingstub__79bbcdf1c788a57a162b669c1dc161d86e837ced7bd9a95cf82a8a650f7a1816(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    display_name: typing.Optional[builtins.str] = None,
    explicit_max_ttl: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    no_parent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    num_uses: typing.Optional[jsii.Number] = None,
    period: typing.Optional[builtins.str] = None,
    policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    renew_increment: typing.Optional[jsii.Number] = None,
    renew_min_lease: typing.Optional[jsii.Number] = None,
    role_name: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
    wrapping_ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6a2b4fe05eb7de53c5c9d83d9f014525d5fc43fe5f16e1d5b57c9330fa3e1dd3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d0c1438a789c8a3552e8b61d34b35d7ab05c93f56c3d8eced021e3fa51344e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd629f1c9bfbd8d1880a520440011994fc6496b95a2feeb1e67d053451915b31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7226eee4c03f2952da448a7108efea4317059b06ca589c34547c5cb7a7fd049b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37757388b9f814597867bb14523a801816e9452327d8d8f93e2d76d767102de9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3fa5fb58f525e4d2f5adf3aea8769ca679c6ff98f5d68e6d21f8c0252383c7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4551e381a33fd82e9e90db8508c328c9264b8d03e12030623c726354f757de0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1907b2d22877ff891ed23b95ad8f9d78f17a9b6316f141f9e820410b01b27f7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d890420efc5296443cd8bac980c63c69105552090fce652ef744a6e84eaac63(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c78ff6153b20f9378a0d5b34081de57d8c02bf0f63aba0d74f1302b6676271c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__768cdb809e2bddb7c915244763ac9a87f482d59e4a7ff2511de0ffd5b47c4979(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fac9ab1b43d15ab487908c653e8e067d233b4f29be78990ce69ba9e20c5edca5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82673a59f238f7af77ccd65e2c1724fc1493c8d5e832cdd114af43d2e84962b3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3822aaed2c4cd8d6896024eafa58dd05d664a22f2c32192f0b347086593471f7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84989ea7a52d149553bce0bd0e88093e17cae72df00dc52c85834bf2568730dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d8474c0a54344d3ee31e23d53b9ca67115d0ef40bd3a1685a7a0f5e7d2196f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06ff01cc004e67efac8905fc6f022bdbe005c35ab2162bfefd22dfb6913b2574(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c2ae7a93427084daecdc64f74d8598342bda3e16215fd3154cd4e9d5b4e9e84(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    display_name: typing.Optional[builtins.str] = None,
    explicit_max_ttl: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    metadata: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
    no_default_policy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    no_parent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    num_uses: typing.Optional[jsii.Number] = None,
    period: typing.Optional[builtins.str] = None,
    policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    renewable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    renew_increment: typing.Optional[jsii.Number] = None,
    renew_min_lease: typing.Optional[jsii.Number] = None,
    role_name: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
    wrapping_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
