r'''
# `data_vault_identity_entity`

Refer to the Terraform Registry for docs: [`data_vault_identity_entity`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity).
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


class DataVaultIdentityEntity(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultIdentityEntity.DataVaultIdentityEntity",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity vault_identity_entity}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        alias_id: typing.Optional[builtins.str] = None,
        alias_mount_accessor: typing.Optional[builtins.str] = None,
        alias_name: typing.Optional[builtins.str] = None,
        entity_id: typing.Optional[builtins.str] = None,
        entity_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity vault_identity_entity} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias_id: ID of the alias. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_id DataVaultIdentityEntity#alias_id}
        :param alias_mount_accessor: Accessor of the mount to which the alias belongs to. This should be supplied in conjunction with ``alias_name``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_mount_accessor DataVaultIdentityEntity#alias_mount_accessor}
        :param alias_name: Name of the alias. This should be supplied in conjunction with ``alias_mount_accessor``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_name DataVaultIdentityEntity#alias_name}
        :param entity_id: ID of the entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#entity_id DataVaultIdentityEntity#entity_id}
        :param entity_name: Name of the entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#entity_name DataVaultIdentityEntity#entity_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#id DataVaultIdentityEntity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#namespace DataVaultIdentityEntity#namespace}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad0423d523da09cfdd7ed47215e578dae0fc96fa03ea752c0766f634985a03a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultIdentityEntityConfig(
            alias_id=alias_id,
            alias_mount_accessor=alias_mount_accessor,
            alias_name=alias_name,
            entity_id=entity_id,
            entity_name=entity_name,
            id=id,
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
        '''Generates CDKTF code for importing a DataVaultIdentityEntity resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultIdentityEntity to import.
        :param import_from_id: The id of the existing DataVaultIdentityEntity that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultIdentityEntity to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e4d365b01fe43dd5cf55d24970766baf9918fd95acccae45825e04f4077023d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAliasId")
    def reset_alias_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasId", []))

    @jsii.member(jsii_name="resetAliasMountAccessor")
    def reset_alias_mount_accessor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasMountAccessor", []))

    @jsii.member(jsii_name="resetAliasName")
    def reset_alias_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliasName", []))

    @jsii.member(jsii_name="resetEntityId")
    def reset_entity_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityId", []))

    @jsii.member(jsii_name="resetEntityName")
    def reset_entity_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntityName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> "DataVaultIdentityEntityAliasesList":
        return typing.cast("DataVaultIdentityEntityAliasesList", jsii.get(self, "aliases"))

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property
    @jsii.member(jsii_name="dataJson")
    def data_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataJson"))

    @builtins.property
    @jsii.member(jsii_name="directGroupIds")
    def direct_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "directGroupIds"))

    @builtins.property
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "disabled"))

    @builtins.property
    @jsii.member(jsii_name="groupIds")
    def group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groupIds"))

    @builtins.property
    @jsii.member(jsii_name="inheritedGroupIds")
    def inherited_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "inheritedGroupIds"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdateTime")
    def last_update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdateTime"))

    @builtins.property
    @jsii.member(jsii_name="mergedEntityIds")
    def merged_entity_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mergedEntityIds"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="namespaceId")
    def namespace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespaceId"))

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="aliasIdInput")
    def alias_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasIdInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasMountAccessorInput")
    def alias_mount_accessor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasMountAccessorInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasNameInput")
    def alias_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entityIdInput")
    def entity_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityIdInput"))

    @builtins.property
    @jsii.member(jsii_name="entityNameInput")
    def entity_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entityNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasId")
    def alias_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aliasId"))

    @alias_id.setter
    def alias_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b4aa2b9e9b969c1b293cc9aea7923d63a90fabb2d788f5d406fb9d9295e27b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aliasId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aliasMountAccessor")
    def alias_mount_accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aliasMountAccessor"))

    @alias_mount_accessor.setter
    def alias_mount_accessor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43af89751c39cfc4df0689a46080bb1917442cfa0a321db6072de5f45968d286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aliasMountAccessor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="aliasName")
    def alias_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aliasName"))

    @alias_name.setter
    def alias_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__249bb7e5136f552e8836e66ac577902ae58f89948d9a7d4bd95037f6025ddb1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aliasName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entityId")
    def entity_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityId"))

    @entity_id.setter
    def entity_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7595a012eb7309f6cda813f98f5dbaf754b5f3e20a51c1023dc3e7ffb9989179)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entityName")
    def entity_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entityName"))

    @entity_name.setter
    def entity_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90fba64d571fa02427b02ad7901866fceaf73eb25968a334e986debf1aa8fbc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entityName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68948a52c54396fddfbb52cbd643d2e3a390d4a807e9052abdd23a910929885a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fba5c58443a5ce6f2690141dd2034332ad796c3615a151aaf09dd80cd7dcfe33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultIdentityEntity.DataVaultIdentityEntityAliases",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataVaultIdentityEntityAliases:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultIdentityEntityAliases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataVaultIdentityEntityAliasesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultIdentityEntity.DataVaultIdentityEntityAliasesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__796668aabb85bdb98459430f2e2375035d1330cb1a12e6a7f57e8694c4d16758)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataVaultIdentityEntityAliasesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c1652196dc51a50dd9498dfb83052189de342aa12c396efd58641b0ba4ed8ee)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataVaultIdentityEntityAliasesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7a10e4375e1f6112c42b99ca3651fb856d2fb6c51814c7705a9e0fc82be6ee0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__77fcc9f31a4a372e08fe26b7826207fd57ce07df157084a08429481a17041793)
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
            type_hints = typing.get_type_hints(_typecheckingstub__14f92b5a88835c2cd0dbae0fa948f5f0baab1cf307548e4717a29d4a23d4ccfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataVaultIdentityEntityAliasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultIdentityEntity.DataVaultIdentityEntityAliasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__98fb52103a19d866e2b8f995b5adfc6b9403e9de4afde54c5f819a020beb7489)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="canonicalId")
    def canonical_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "canonicalId"))

    @builtins.property
    @jsii.member(jsii_name="creationTime")
    def creation_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationTime"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdateTime")
    def last_update_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdateTime"))

    @builtins.property
    @jsii.member(jsii_name="mergedFromCanonicalIds")
    def merged_from_canonical_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mergedFromCanonicalIds"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="mountAccessor")
    def mount_accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountAccessor"))

    @builtins.property
    @jsii.member(jsii_name="mountPath")
    def mount_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountPath"))

    @builtins.property
    @jsii.member(jsii_name="mountType")
    def mount_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountType"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataVaultIdentityEntityAliases]:
        return typing.cast(typing.Optional[DataVaultIdentityEntityAliases], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataVaultIdentityEntityAliases],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89f49768481700ac4bc4004a0c9ccc777d38db1b4eab06bf5099a385cad5448d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultIdentityEntity.DataVaultIdentityEntityConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "alias_id": "aliasId",
        "alias_mount_accessor": "aliasMountAccessor",
        "alias_name": "aliasName",
        "entity_id": "entityId",
        "entity_name": "entityName",
        "id": "id",
        "namespace": "namespace",
    },
)
class DataVaultIdentityEntityConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        alias_id: typing.Optional[builtins.str] = None,
        alias_mount_accessor: typing.Optional[builtins.str] = None,
        alias_name: typing.Optional[builtins.str] = None,
        entity_id: typing.Optional[builtins.str] = None,
        entity_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
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
        :param alias_id: ID of the alias. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_id DataVaultIdentityEntity#alias_id}
        :param alias_mount_accessor: Accessor of the mount to which the alias belongs to. This should be supplied in conjunction with ``alias_name``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_mount_accessor DataVaultIdentityEntity#alias_mount_accessor}
        :param alias_name: Name of the alias. This should be supplied in conjunction with ``alias_mount_accessor``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_name DataVaultIdentityEntity#alias_name}
        :param entity_id: ID of the entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#entity_id DataVaultIdentityEntity#entity_id}
        :param entity_name: Name of the entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#entity_name DataVaultIdentityEntity#entity_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#id DataVaultIdentityEntity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#namespace DataVaultIdentityEntity#namespace}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8727549547ec6386b18df4ca01c48f1946aa1faf8d04a19d48a4cc76a3a0ae05)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument alias_id", value=alias_id, expected_type=type_hints["alias_id"])
            check_type(argname="argument alias_mount_accessor", value=alias_mount_accessor, expected_type=type_hints["alias_mount_accessor"])
            check_type(argname="argument alias_name", value=alias_name, expected_type=type_hints["alias_name"])
            check_type(argname="argument entity_id", value=entity_id, expected_type=type_hints["entity_id"])
            check_type(argname="argument entity_name", value=entity_name, expected_type=type_hints["entity_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
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
        if alias_id is not None:
            self._values["alias_id"] = alias_id
        if alias_mount_accessor is not None:
            self._values["alias_mount_accessor"] = alias_mount_accessor
        if alias_name is not None:
            self._values["alias_name"] = alias_name
        if entity_id is not None:
            self._values["entity_id"] = entity_id
        if entity_name is not None:
            self._values["entity_name"] = entity_name
        if id is not None:
            self._values["id"] = id
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
    def alias_id(self) -> typing.Optional[builtins.str]:
        '''ID of the alias.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_id DataVaultIdentityEntity#alias_id}
        '''
        result = self._values.get("alias_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias_mount_accessor(self) -> typing.Optional[builtins.str]:
        '''Accessor of the mount to which the alias belongs to. This should be supplied in conjunction with ``alias_name``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_mount_accessor DataVaultIdentityEntity#alias_mount_accessor}
        '''
        result = self._values.get("alias_mount_accessor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias_name(self) -> typing.Optional[builtins.str]:
        '''Name of the alias. This should be supplied in conjunction with ``alias_mount_accessor``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#alias_name DataVaultIdentityEntity#alias_name}
        '''
        result = self._values.get("alias_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entity_id(self) -> typing.Optional[builtins.str]:
        '''ID of the entity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#entity_id DataVaultIdentityEntity#entity_id}
        '''
        result = self._values.get("entity_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entity_name(self) -> typing.Optional[builtins.str]:
        '''Name of the entity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#entity_name DataVaultIdentityEntity#entity_name}
        '''
        result = self._values.get("entity_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#id DataVaultIdentityEntity#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/identity_entity#namespace DataVaultIdentityEntity#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultIdentityEntityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVaultIdentityEntity",
    "DataVaultIdentityEntityAliases",
    "DataVaultIdentityEntityAliasesList",
    "DataVaultIdentityEntityAliasesOutputReference",
    "DataVaultIdentityEntityConfig",
]

publication.publish()

def _typecheckingstub__ad0423d523da09cfdd7ed47215e578dae0fc96fa03ea752c0766f634985a03a3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    alias_id: typing.Optional[builtins.str] = None,
    alias_mount_accessor: typing.Optional[builtins.str] = None,
    alias_name: typing.Optional[builtins.str] = None,
    entity_id: typing.Optional[builtins.str] = None,
    entity_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__4e4d365b01fe43dd5cf55d24970766baf9918fd95acccae45825e04f4077023d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b4aa2b9e9b969c1b293cc9aea7923d63a90fabb2d788f5d406fb9d9295e27b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43af89751c39cfc4df0689a46080bb1917442cfa0a321db6072de5f45968d286(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__249bb7e5136f552e8836e66ac577902ae58f89948d9a7d4bd95037f6025ddb1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7595a012eb7309f6cda813f98f5dbaf754b5f3e20a51c1023dc3e7ffb9989179(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90fba64d571fa02427b02ad7901866fceaf73eb25968a334e986debf1aa8fbc7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68948a52c54396fddfbb52cbd643d2e3a390d4a807e9052abdd23a910929885a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fba5c58443a5ce6f2690141dd2034332ad796c3615a151aaf09dd80cd7dcfe33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__796668aabb85bdb98459430f2e2375035d1330cb1a12e6a7f57e8694c4d16758(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c1652196dc51a50dd9498dfb83052189de342aa12c396efd58641b0ba4ed8ee(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a10e4375e1f6112c42b99ca3651fb856d2fb6c51814c7705a9e0fc82be6ee0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77fcc9f31a4a372e08fe26b7826207fd57ce07df157084a08429481a17041793(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f92b5a88835c2cd0dbae0fa948f5f0baab1cf307548e4717a29d4a23d4ccfb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98fb52103a19d866e2b8f995b5adfc6b9403e9de4afde54c5f819a020beb7489(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89f49768481700ac4bc4004a0c9ccc777d38db1b4eab06bf5099a385cad5448d(
    value: typing.Optional[DataVaultIdentityEntityAliases],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8727549547ec6386b18df4ca01c48f1946aa1faf8d04a19d48a4cc76a3a0ae05(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    alias_id: typing.Optional[builtins.str] = None,
    alias_mount_accessor: typing.Optional[builtins.str] = None,
    alias_name: typing.Optional[builtins.str] = None,
    entity_id: typing.Optional[builtins.str] = None,
    entity_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
