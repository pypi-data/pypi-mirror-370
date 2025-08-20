r'''
# `vault_identity_mfa_login_enforcement`

Refer to the Terraform Registry for docs: [`vault_identity_mfa_login_enforcement`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement).
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


class IdentityMfaLoginEnforcement(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.identityMfaLoginEnforcement.IdentityMfaLoginEnforcement",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement vault_identity_mfa_login_enforcement}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        mfa_method_ids: typing.Sequence[builtins.str],
        name: builtins.str,
        auth_method_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        auth_method_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_entity_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        identity_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement vault_identity_mfa_login_enforcement} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param mfa_method_ids: Set of MFA method UUIDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#mfa_method_ids IdentityMfaLoginEnforcement#mfa_method_ids}
        :param name: Login enforcement name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#name IdentityMfaLoginEnforcement#name}
        :param auth_method_accessors: Set of auth method accessor IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#auth_method_accessors IdentityMfaLoginEnforcement#auth_method_accessors}
        :param auth_method_types: Set of auth method types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#auth_method_types IdentityMfaLoginEnforcement#auth_method_types}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#id IdentityMfaLoginEnforcement#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_entity_ids: Set of identity entity IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#identity_entity_ids IdentityMfaLoginEnforcement#identity_entity_ids}
        :param identity_group_ids: Set of identity group IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#identity_group_ids IdentityMfaLoginEnforcement#identity_group_ids}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#namespace IdentityMfaLoginEnforcement#namespace}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad9a5c7758cfeacae5ddf8bccc43a71ad565d9cb1926dfcfa52733805a22c44f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = IdentityMfaLoginEnforcementConfig(
            mfa_method_ids=mfa_method_ids,
            name=name,
            auth_method_accessors=auth_method_accessors,
            auth_method_types=auth_method_types,
            id=id,
            identity_entity_ids=identity_entity_ids,
            identity_group_ids=identity_group_ids,
            namespace=namespace,
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
        '''Generates CDKTF code for importing a IdentityMfaLoginEnforcement resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the IdentityMfaLoginEnforcement to import.
        :param import_from_id: The id of the existing IdentityMfaLoginEnforcement that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the IdentityMfaLoginEnforcement to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0e6e68ed5cc4123e0138d92dbc4816bb5bb0c01f98c6edd559c7d3e0a2e39ba)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAuthMethodAccessors")
    def reset_auth_method_accessors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethodAccessors", []))

    @jsii.member(jsii_name="resetAuthMethodTypes")
    def reset_auth_method_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethodTypes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentityEntityIds")
    def reset_identity_entity_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityEntityIds", []))

    @jsii.member(jsii_name="resetIdentityGroupIds")
    def reset_identity_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityGroupIds", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

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
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="namespacePath")
    def namespace_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespacePath"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="authMethodAccessorsInput")
    def auth_method_accessors_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authMethodAccessorsInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodTypesInput")
    def auth_method_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authMethodTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="identityEntityIdsInput")
    def identity_entity_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "identityEntityIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="identityGroupIdsInput")
    def identity_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "identityGroupIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mfaMethodIdsInput")
    def mfa_method_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mfaMethodIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodAccessors")
    def auth_method_accessors(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authMethodAccessors"))

    @auth_method_accessors.setter
    def auth_method_accessors(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c790ecb443625ac06ba28a7effb62276540744e2c252acbd09fe8a048b4749fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethodAccessors", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authMethodTypes")
    def auth_method_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authMethodTypes"))

    @auth_method_types.setter
    def auth_method_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a097c91ab884fe4d1bda303a27f74c01b460f8ae70e98d9c2b065a9878c45dbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethodTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a0b8b2bc566cedeb18bfb1f55e51304aa83b0c3bdd67f69103cff5c58ae0b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityEntityIds")
    def identity_entity_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "identityEntityIds"))

    @identity_entity_ids.setter
    def identity_entity_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66952c1619cca26cba7392d473a2cc4f539684bdec94930e5a56437541c204e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityEntityIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityGroupIds")
    def identity_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "identityGroupIds"))

    @identity_group_ids.setter
    def identity_group_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e90dcbd0a867cd78d89d5de64f63919f8068ce77185920323d43a5d93586f384)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityGroupIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mfaMethodIds")
    def mfa_method_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mfaMethodIds"))

    @mfa_method_ids.setter
    def mfa_method_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcb783f028f334d554f3c02243cd776e7d7792e6d5b5312be111de350741b836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mfaMethodIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f317f485babfe4cd2528bf0d50e7c173ea66e54afb7b1e0f53f6a947860f1cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6140a13e21786d23e46da16bb533dc9d041c5eaa321fc5f67afb04553b091ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.identityMfaLoginEnforcement.IdentityMfaLoginEnforcementConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "mfa_method_ids": "mfaMethodIds",
        "name": "name",
        "auth_method_accessors": "authMethodAccessors",
        "auth_method_types": "authMethodTypes",
        "id": "id",
        "identity_entity_ids": "identityEntityIds",
        "identity_group_ids": "identityGroupIds",
        "namespace": "namespace",
    },
)
class IdentityMfaLoginEnforcementConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        mfa_method_ids: typing.Sequence[builtins.str],
        name: builtins.str,
        auth_method_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
        auth_method_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_entity_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        identity_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param mfa_method_ids: Set of MFA method UUIDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#mfa_method_ids IdentityMfaLoginEnforcement#mfa_method_ids}
        :param name: Login enforcement name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#name IdentityMfaLoginEnforcement#name}
        :param auth_method_accessors: Set of auth method accessor IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#auth_method_accessors IdentityMfaLoginEnforcement#auth_method_accessors}
        :param auth_method_types: Set of auth method types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#auth_method_types IdentityMfaLoginEnforcement#auth_method_types}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#id IdentityMfaLoginEnforcement#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_entity_ids: Set of identity entity IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#identity_entity_ids IdentityMfaLoginEnforcement#identity_entity_ids}
        :param identity_group_ids: Set of identity group IDs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#identity_group_ids IdentityMfaLoginEnforcement#identity_group_ids}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#namespace IdentityMfaLoginEnforcement#namespace}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ff18d9622c29d5112dec946da30c3cb25b168bad362de7e3fb64a31917a1d35)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument mfa_method_ids", value=mfa_method_ids, expected_type=type_hints["mfa_method_ids"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auth_method_accessors", value=auth_method_accessors, expected_type=type_hints["auth_method_accessors"])
            check_type(argname="argument auth_method_types", value=auth_method_types, expected_type=type_hints["auth_method_types"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_entity_ids", value=identity_entity_ids, expected_type=type_hints["identity_entity_ids"])
            check_type(argname="argument identity_group_ids", value=identity_group_ids, expected_type=type_hints["identity_group_ids"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mfa_method_ids": mfa_method_ids,
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
        if auth_method_accessors is not None:
            self._values["auth_method_accessors"] = auth_method_accessors
        if auth_method_types is not None:
            self._values["auth_method_types"] = auth_method_types
        if id is not None:
            self._values["id"] = id
        if identity_entity_ids is not None:
            self._values["identity_entity_ids"] = identity_entity_ids
        if identity_group_ids is not None:
            self._values["identity_group_ids"] = identity_group_ids
        if namespace is not None:
            self._values["namespace"] = namespace

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
    def mfa_method_ids(self) -> typing.List[builtins.str]:
        '''Set of MFA method UUIDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#mfa_method_ids IdentityMfaLoginEnforcement#mfa_method_ids}
        '''
        result = self._values.get("mfa_method_ids")
        assert result is not None, "Required property 'mfa_method_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Login enforcement name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#name IdentityMfaLoginEnforcement#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_method_accessors(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of auth method accessor IDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#auth_method_accessors IdentityMfaLoginEnforcement#auth_method_accessors}
        '''
        result = self._values.get("auth_method_accessors")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auth_method_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of auth method types.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#auth_method_types IdentityMfaLoginEnforcement#auth_method_types}
        '''
        result = self._values.get("auth_method_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#id IdentityMfaLoginEnforcement#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_entity_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of identity entity IDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#identity_entity_ids IdentityMfaLoginEnforcement#identity_entity_ids}
        '''
        result = self._values.get("identity_entity_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def identity_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of identity group IDs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#identity_group_ids IdentityMfaLoginEnforcement#identity_group_ids}
        '''
        result = self._values.get("identity_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_mfa_login_enforcement#namespace IdentityMfaLoginEnforcement#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityMfaLoginEnforcementConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IdentityMfaLoginEnforcement",
    "IdentityMfaLoginEnforcementConfig",
]

publication.publish()

def _typecheckingstub__ad9a5c7758cfeacae5ddf8bccc43a71ad565d9cb1926dfcfa52733805a22c44f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    mfa_method_ids: typing.Sequence[builtins.str],
    name: builtins.str,
    auth_method_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    auth_method_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_entity_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    identity_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__c0e6e68ed5cc4123e0138d92dbc4816bb5bb0c01f98c6edd559c7d3e0a2e39ba(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c790ecb443625ac06ba28a7effb62276540744e2c252acbd09fe8a048b4749fc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a097c91ab884fe4d1bda303a27f74c01b460f8ae70e98d9c2b065a9878c45dbd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a0b8b2bc566cedeb18bfb1f55e51304aa83b0c3bdd67f69103cff5c58ae0b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66952c1619cca26cba7392d473a2cc4f539684bdec94930e5a56437541c204e9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e90dcbd0a867cd78d89d5de64f63919f8068ce77185920323d43a5d93586f384(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcb783f028f334d554f3c02243cd776e7d7792e6d5b5312be111de350741b836(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f317f485babfe4cd2528bf0d50e7c173ea66e54afb7b1e0f53f6a947860f1cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6140a13e21786d23e46da16bb533dc9d041c5eaa321fc5f67afb04553b091ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ff18d9622c29d5112dec946da30c3cb25b168bad362de7e3fb64a31917a1d35(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mfa_method_ids: typing.Sequence[builtins.str],
    name: builtins.str,
    auth_method_accessors: typing.Optional[typing.Sequence[builtins.str]] = None,
    auth_method_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_entity_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    identity_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
