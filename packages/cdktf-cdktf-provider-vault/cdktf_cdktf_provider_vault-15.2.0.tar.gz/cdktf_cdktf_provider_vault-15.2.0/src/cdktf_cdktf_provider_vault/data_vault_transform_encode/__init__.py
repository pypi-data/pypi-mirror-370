r'''
# `data_vault_transform_encode`

Refer to the Terraform Registry for docs: [`data_vault_transform_encode`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode).
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


class DataVaultTransformEncode(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultTransformEncode.DataVaultTransformEncode",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode vault_transform_encode}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        path: builtins.str,
        role_name: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        encoded_value: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        transformation: typing.Optional[builtins.str] = None,
        tweak: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode vault_transform_encode} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param path: Path to backend from which to retrieve data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#path DataVaultTransformEncode#path}
        :param role_name: The name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#role_name DataVaultTransformEncode#role_name}
        :param batch_input: Specifies a list of items to be encoded in a single batch. If this parameter is set, the parameters 'value', 'transformation' and 'tweak' will be ignored. Each batch item within the list can specify these parameters instead. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#batch_input DataVaultTransformEncode#batch_input}
        :param batch_results: The result of encoding batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#batch_results DataVaultTransformEncode#batch_results}
        :param encoded_value: The result of encoding a value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#encoded_value DataVaultTransformEncode#encoded_value}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#id DataVaultTransformEncode#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#namespace DataVaultTransformEncode#namespace}
        :param transformation: The transformation to perform. If no value is provided and the role contains a single transformation, this value will be inferred from the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#transformation DataVaultTransformEncode#transformation}
        :param tweak: The tweak value to use. Only applicable for FPE transformations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#tweak DataVaultTransformEncode#tweak}
        :param value: The value in which to encode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#value DataVaultTransformEncode#value}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32741ff0f40905f2e91ebfdbdbded327699cdb3a597c26b616cb17ab8aca9ebc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultTransformEncodeConfig(
            path=path,
            role_name=role_name,
            batch_input=batch_input,
            batch_results=batch_results,
            encoded_value=encoded_value,
            id=id,
            namespace=namespace,
            transformation=transformation,
            tweak=tweak,
            value=value,
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
        '''Generates CDKTF code for importing a DataVaultTransformEncode resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultTransformEncode to import.
        :param import_from_id: The id of the existing DataVaultTransformEncode that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultTransformEncode to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__913283f84d3a4b6cb0607fdd732675ea71c4801542287bb768e03b6898831e9a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBatchInput")
    def reset_batch_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchInput", []))

    @jsii.member(jsii_name="resetBatchResults")
    def reset_batch_results(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchResults", []))

    @jsii.member(jsii_name="resetEncodedValue")
    def reset_encoded_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncodedValue", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetTransformation")
    def reset_transformation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransformation", []))

    @jsii.member(jsii_name="resetTweak")
    def reset_tweak(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTweak", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

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
    @jsii.member(jsii_name="batchInputInput")
    def batch_input_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], jsii.get(self, "batchInputInput"))

    @builtins.property
    @jsii.member(jsii_name="batchResultsInput")
    def batch_results_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], jsii.get(self, "batchResultsInput"))

    @builtins.property
    @jsii.member(jsii_name="encodedValueInput")
    def encoded_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodedValueInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="transformationInput")
    def transformation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "transformationInput"))

    @builtins.property
    @jsii.member(jsii_name="tweakInput")
    def tweak_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tweakInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="batchInput")
    def batch_input(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "batchInput"))

    @batch_input.setter
    def batch_input(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5f2a86b9626eceb921101ca2ca241c16e4dd6ea60a5677fd03ea5ebc9b6aa8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchInput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchResults")
    def batch_results(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "batchResults"))

    @batch_results.setter
    def batch_results(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eda829b15e663eee2f32d1720324aca907d2b2f94508dc2471115794624557d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchResults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encodedValue")
    def encoded_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encodedValue"))

    @encoded_value.setter
    def encoded_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e02ab5474edefa2a0c335d4c6fff16d068303278ae34413920e61171c45f00e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encodedValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3805c3e7759c93440ec2ce57310fd59461b2e9762b4e5a85ac5a6bee51a8915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38cac33366f3c967cba8c52f04d4aa180e7a90d33802f4727cb9163eed97f5c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9de8dcd0d1cf0cd47997c76ecd70d391626d13470719755ee3e87a49641ec14d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0012d2dca9a36e92853b85a6ae0afffe755ccd30a4fae022dad528727b98beb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="transformation")
    def transformation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "transformation"))

    @transformation.setter
    def transformation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__597f7184ed675cf355e2d7b1311349c7a848bffeb82593bff5ab38108cbc4cab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "transformation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tweak")
    def tweak(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tweak"))

    @tweak.setter
    def tweak(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b4bae472c7692fbe70174796607eb391a44d1194d367d62252cdf0393d5815b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tweak", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d1ab805210cc4b1fa924caed7b35c1ee2affd7d454b22c503243395e3152b95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultTransformEncode.DataVaultTransformEncodeConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "path": "path",
        "role_name": "roleName",
        "batch_input": "batchInput",
        "batch_results": "batchResults",
        "encoded_value": "encodedValue",
        "id": "id",
        "namespace": "namespace",
        "transformation": "transformation",
        "tweak": "tweak",
        "value": "value",
    },
)
class DataVaultTransformEncodeConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        path: builtins.str,
        role_name: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        encoded_value: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        transformation: typing.Optional[builtins.str] = None,
        tweak: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param path: Path to backend from which to retrieve data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#path DataVaultTransformEncode#path}
        :param role_name: The name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#role_name DataVaultTransformEncode#role_name}
        :param batch_input: Specifies a list of items to be encoded in a single batch. If this parameter is set, the parameters 'value', 'transformation' and 'tweak' will be ignored. Each batch item within the list can specify these parameters instead. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#batch_input DataVaultTransformEncode#batch_input}
        :param batch_results: The result of encoding batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#batch_results DataVaultTransformEncode#batch_results}
        :param encoded_value: The result of encoding a value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#encoded_value DataVaultTransformEncode#encoded_value}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#id DataVaultTransformEncode#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#namespace DataVaultTransformEncode#namespace}
        :param transformation: The transformation to perform. If no value is provided and the role contains a single transformation, this value will be inferred from the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#transformation DataVaultTransformEncode#transformation}
        :param tweak: The tweak value to use. Only applicable for FPE transformations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#tweak DataVaultTransformEncode#tweak}
        :param value: The value in which to encode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#value DataVaultTransformEncode#value}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65f0f5ef00268a8b948a81bbd59873e599c6e112b2d03cd207eba9163f044ab7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument batch_input", value=batch_input, expected_type=type_hints["batch_input"])
            check_type(argname="argument batch_results", value=batch_results, expected_type=type_hints["batch_results"])
            check_type(argname="argument encoded_value", value=encoded_value, expected_type=type_hints["encoded_value"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument transformation", value=transformation, expected_type=type_hints["transformation"])
            check_type(argname="argument tweak", value=tweak, expected_type=type_hints["tweak"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
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
        if batch_input is not None:
            self._values["batch_input"] = batch_input
        if batch_results is not None:
            self._values["batch_results"] = batch_results
        if encoded_value is not None:
            self._values["encoded_value"] = encoded_value
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if transformation is not None:
            self._values["transformation"] = transformation
        if tweak is not None:
            self._values["tweak"] = tweak
        if value is not None:
            self._values["value"] = value

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
    def path(self) -> builtins.str:
        '''Path to backend from which to retrieve data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#path DataVaultTransformEncode#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> builtins.str:
        '''The name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#role_name DataVaultTransformEncode#role_name}
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def batch_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''Specifies a list of items to be encoded in a single batch.

        If this parameter is set, the parameters 'value', 'transformation' and 'tweak' will be ignored. Each batch item within the list can specify these parameters instead.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#batch_input DataVaultTransformEncode#batch_input}
        '''
        result = self._values.get("batch_input")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def batch_results(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''The result of encoding batch_input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#batch_results DataVaultTransformEncode#batch_results}
        '''
        result = self._values.get("batch_results")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def encoded_value(self) -> typing.Optional[builtins.str]:
        '''The result of encoding a value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#encoded_value DataVaultTransformEncode#encoded_value}
        '''
        result = self._values.get("encoded_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#id DataVaultTransformEncode#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#namespace DataVaultTransformEncode#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transformation(self) -> typing.Optional[builtins.str]:
        '''The transformation to perform.

        If no value is provided and the role contains a single transformation, this value will be inferred from the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#transformation DataVaultTransformEncode#transformation}
        '''
        result = self._values.get("transformation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tweak(self) -> typing.Optional[builtins.str]:
        '''The tweak value to use. Only applicable for FPE transformations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#tweak DataVaultTransformEncode#tweak}
        '''
        result = self._values.get("tweak")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''The value in which to encode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transform_encode#value DataVaultTransformEncode#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultTransformEncodeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVaultTransformEncode",
    "DataVaultTransformEncodeConfig",
]

publication.publish()

def _typecheckingstub__32741ff0f40905f2e91ebfdbdbded327699cdb3a597c26b616cb17ab8aca9ebc(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    path: builtins.str,
    role_name: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    encoded_value: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    transformation: typing.Optional[builtins.str] = None,
    tweak: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__913283f84d3a4b6cb0607fdd732675ea71c4801542287bb768e03b6898831e9a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5f2a86b9626eceb921101ca2ca241c16e4dd6ea60a5677fd03ea5ebc9b6aa8e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eda829b15e663eee2f32d1720324aca907d2b2f94508dc2471115794624557d2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e02ab5474edefa2a0c335d4c6fff16d068303278ae34413920e61171c45f00e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3805c3e7759c93440ec2ce57310fd59461b2e9762b4e5a85ac5a6bee51a8915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38cac33366f3c967cba8c52f04d4aa180e7a90d33802f4727cb9163eed97f5c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de8dcd0d1cf0cd47997c76ecd70d391626d13470719755ee3e87a49641ec14d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0012d2dca9a36e92853b85a6ae0afffe755ccd30a4fae022dad528727b98beb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__597f7184ed675cf355e2d7b1311349c7a848bffeb82593bff5ab38108cbc4cab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b4bae472c7692fbe70174796607eb391a44d1194d367d62252cdf0393d5815b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d1ab805210cc4b1fa924caed7b35c1ee2affd7d454b22c503243395e3152b95(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65f0f5ef00268a8b948a81bbd59873e599c6e112b2d03cd207eba9163f044ab7(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    path: builtins.str,
    role_name: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    encoded_value: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    transformation: typing.Optional[builtins.str] = None,
    tweak: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
