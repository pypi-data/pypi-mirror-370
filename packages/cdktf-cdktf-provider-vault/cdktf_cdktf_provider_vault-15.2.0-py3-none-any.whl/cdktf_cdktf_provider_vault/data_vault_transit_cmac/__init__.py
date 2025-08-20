r'''
# `data_vault_transit_cmac`

Refer to the Terraform Registry for docs: [`data_vault_transit_cmac`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac).
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


class DataVaultTransitCmac(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultTransitCmac.DataVaultTransitCmac",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac vault_transit_cmac}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        path: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        cmac: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input: typing.Optional[builtins.str] = None,
        key_version: typing.Optional[jsii.Number] = None,
        mac_length: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        url_mac_length: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac vault_transit_cmac} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the CMAC key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#name DataVaultTransitCmac#name}
        :param path: The Transit secret backend the key belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#path DataVaultTransitCmac#path}
        :param batch_input: Specifies a list of items for processing. When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#batch_input DataVaultTransitCmac#batch_input}
        :param batch_results: The results returned from Vault if using batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#batch_results DataVaultTransitCmac#batch_results}
        :param cmac: The CMAC returned from Vault if using input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#cmac DataVaultTransitCmac#cmac}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#id DataVaultTransitCmac#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input: Specifies the base64 encoded input data. One of input or batch_input must be supplied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#input DataVaultTransitCmac#input}
        :param key_version: The version of the key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#key_version DataVaultTransitCmac#key_version}
        :param mac_length: Specifies the MAC length to use (POST body parameter). The mac_length cannot be larger than the cipher's block size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#mac_length DataVaultTransitCmac#mac_length}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#namespace DataVaultTransitCmac#namespace}
        :param url_mac_length: Specifies the MAC length to use (URL parameter). If provided, this value overrides mac_length. The url_mac_length cannot be larger than the cipher's block size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#url_mac_length DataVaultTransitCmac#url_mac_length}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__160a1076a417291e8ff7c5402f71431dcf614804fb2f28852807d7a95df9c67a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultTransitCmacConfig(
            name=name,
            path=path,
            batch_input=batch_input,
            batch_results=batch_results,
            cmac=cmac,
            id=id,
            input=input,
            key_version=key_version,
            mac_length=mac_length,
            namespace=namespace,
            url_mac_length=url_mac_length,
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
        '''Generates CDKTF code for importing a DataVaultTransitCmac resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultTransitCmac to import.
        :param import_from_id: The id of the existing DataVaultTransitCmac that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultTransitCmac to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c847ac8608ac41c4faf3da9b34b4fbc8f7bb0c72ac6b15174954ba2b9332cf95)
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

    @jsii.member(jsii_name="resetCmac")
    def reset_cmac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCmac", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInput")
    def reset_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInput", []))

    @jsii.member(jsii_name="resetKeyVersion")
    def reset_key_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyVersion", []))

    @jsii.member(jsii_name="resetMacLength")
    def reset_mac_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMacLength", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetUrlMacLength")
    def reset_url_mac_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrlMacLength", []))

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
    @jsii.member(jsii_name="cmacInput")
    def cmac_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cmacInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="keyVersionInput")
    def key_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="macLengthInput")
    def mac_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "macLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="urlMacLengthInput")
    def url_mac_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "urlMacLengthInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__8eb84962c1544c9f33dcfe1579893ee5a94cbcaf52ab0a0b6b52a2d746c31307)
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
            type_hints = typing.get_type_hints(_typecheckingstub__91e07bbd5a1e90b7df04ea8dafcf75230384882547229a23751c77c06c84e06a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchResults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cmac")
    def cmac(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cmac"))

    @cmac.setter
    def cmac(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae2f993778ae71d9ebb20ca383ad805367914b2d4a5749e1cd39819ab0e2f5ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cmac", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a84a715fa2fc51cfc5360278a1aff4fa8cedf9b9acc8f7e1650c3e7e5702395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "input"))

    @input.setter
    def input(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13dad607f5b7fc9de381c9bfbb9a07303ecf404f7094fb2d97afd2a101c172cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "input", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyVersion")
    def key_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyVersion"))

    @key_version.setter
    def key_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac010d54e64f6c885b5583a0b32833af0ae7282cd4a24ee49b5989557c0a1d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="macLength")
    def mac_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "macLength"))

    @mac_length.setter
    def mac_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21d088fc45a86ff22d23b9bca461d99e1473bef07cb55005953bf6dcab6d11a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "macLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c7221a82a88da7a55804c3e1aa2e9afa6701cb41d7e7502ef9c60f8fb22f452)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50b9fc5a2fde647a6eb6d81eca2f7055e34f6bd5a9a6657c77567c3578901d60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db110f0c9f88a312faeb60240a28c20819a8052d6df63c5e5a93512dfb5f8023)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlMacLength")
    def url_mac_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "urlMacLength"))

    @url_mac_length.setter
    def url_mac_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ec303f48bac76dd15a196d99bda599a0b94a7ba43bc875069d3a2acd6d12727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlMacLength", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultTransitCmac.DataVaultTransitCmacConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "path": "path",
        "batch_input": "batchInput",
        "batch_results": "batchResults",
        "cmac": "cmac",
        "id": "id",
        "input": "input",
        "key_version": "keyVersion",
        "mac_length": "macLength",
        "namespace": "namespace",
        "url_mac_length": "urlMacLength",
    },
)
class DataVaultTransitCmacConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        path: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        cmac: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input: typing.Optional[builtins.str] = None,
        key_version: typing.Optional[jsii.Number] = None,
        mac_length: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        url_mac_length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Name of the CMAC key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#name DataVaultTransitCmac#name}
        :param path: The Transit secret backend the key belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#path DataVaultTransitCmac#path}
        :param batch_input: Specifies a list of items for processing. When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#batch_input DataVaultTransitCmac#batch_input}
        :param batch_results: The results returned from Vault if using batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#batch_results DataVaultTransitCmac#batch_results}
        :param cmac: The CMAC returned from Vault if using input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#cmac DataVaultTransitCmac#cmac}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#id DataVaultTransitCmac#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input: Specifies the base64 encoded input data. One of input or batch_input must be supplied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#input DataVaultTransitCmac#input}
        :param key_version: The version of the key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#key_version DataVaultTransitCmac#key_version}
        :param mac_length: Specifies the MAC length to use (POST body parameter). The mac_length cannot be larger than the cipher's block size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#mac_length DataVaultTransitCmac#mac_length}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#namespace DataVaultTransitCmac#namespace}
        :param url_mac_length: Specifies the MAC length to use (URL parameter). If provided, this value overrides mac_length. The url_mac_length cannot be larger than the cipher's block size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#url_mac_length DataVaultTransitCmac#url_mac_length}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da8e4044177be41b9a49384cbb184a144e0f2068441d10f5f73d44e13f31f245)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument batch_input", value=batch_input, expected_type=type_hints["batch_input"])
            check_type(argname="argument batch_results", value=batch_results, expected_type=type_hints["batch_results"])
            check_type(argname="argument cmac", value=cmac, expected_type=type_hints["cmac"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument key_version", value=key_version, expected_type=type_hints["key_version"])
            check_type(argname="argument mac_length", value=mac_length, expected_type=type_hints["mac_length"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument url_mac_length", value=url_mac_length, expected_type=type_hints["url_mac_length"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "path": path,
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
        if cmac is not None:
            self._values["cmac"] = cmac
        if id is not None:
            self._values["id"] = id
        if input is not None:
            self._values["input"] = input
        if key_version is not None:
            self._values["key_version"] = key_version
        if mac_length is not None:
            self._values["mac_length"] = mac_length
        if namespace is not None:
            self._values["namespace"] = namespace
        if url_mac_length is not None:
            self._values["url_mac_length"] = url_mac_length

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
    def name(self) -> builtins.str:
        '''Name of the CMAC key to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#name DataVaultTransitCmac#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''The Transit secret backend the key belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#path DataVaultTransitCmac#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def batch_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''Specifies a list of items for processing.

        When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#batch_input DataVaultTransitCmac#batch_input}
        '''
        result = self._values.get("batch_input")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def batch_results(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''The results returned from Vault if using batch_input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#batch_results DataVaultTransitCmac#batch_results}
        '''
        result = self._values.get("batch_results")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def cmac(self) -> typing.Optional[builtins.str]:
        '''The CMAC returned from Vault if using input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#cmac DataVaultTransitCmac#cmac}
        '''
        result = self._values.get("cmac")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#id DataVaultTransitCmac#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input(self) -> typing.Optional[builtins.str]:
        '''Specifies the base64 encoded input data. One of input or batch_input must be supplied.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#input DataVaultTransitCmac#input}
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_version(self) -> typing.Optional[jsii.Number]:
        '''The version of the key to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#key_version DataVaultTransitCmac#key_version}
        '''
        result = self._values.get("key_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mac_length(self) -> typing.Optional[jsii.Number]:
        '''Specifies the MAC length to use (POST body parameter). The mac_length cannot be larger than the cipher's block size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#mac_length DataVaultTransitCmac#mac_length}
        '''
        result = self._values.get("mac_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#namespace DataVaultTransitCmac#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url_mac_length(self) -> typing.Optional[jsii.Number]:
        '''Specifies the MAC length to use (URL parameter).

        If provided, this value overrides mac_length. The url_mac_length cannot be larger than the cipher's block size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_cmac#url_mac_length DataVaultTransitCmac#url_mac_length}
        '''
        result = self._values.get("url_mac_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultTransitCmacConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVaultTransitCmac",
    "DataVaultTransitCmacConfig",
]

publication.publish()

def _typecheckingstub__160a1076a417291e8ff7c5402f71431dcf614804fb2f28852807d7a95df9c67a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    path: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    cmac: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    input: typing.Optional[builtins.str] = None,
    key_version: typing.Optional[jsii.Number] = None,
    mac_length: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    url_mac_length: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__c847ac8608ac41c4faf3da9b34b4fbc8f7bb0c72ac6b15174954ba2b9332cf95(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eb84962c1544c9f33dcfe1579893ee5a94cbcaf52ab0a0b6b52a2d746c31307(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e07bbd5a1e90b7df04ea8dafcf75230384882547229a23751c77c06c84e06a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae2f993778ae71d9ebb20ca383ad805367914b2d4a5749e1cd39819ab0e2f5ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a84a715fa2fc51cfc5360278a1aff4fa8cedf9b9acc8f7e1650c3e7e5702395(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13dad607f5b7fc9de381c9bfbb9a07303ecf404f7094fb2d97afd2a101c172cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac010d54e64f6c885b5583a0b32833af0ae7282cd4a24ee49b5989557c0a1d58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21d088fc45a86ff22d23b9bca461d99e1473bef07cb55005953bf6dcab6d11a9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c7221a82a88da7a55804c3e1aa2e9afa6701cb41d7e7502ef9c60f8fb22f452(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50b9fc5a2fde647a6eb6d81eca2f7055e34f6bd5a9a6657c77567c3578901d60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db110f0c9f88a312faeb60240a28c20819a8052d6df63c5e5a93512dfb5f8023(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ec303f48bac76dd15a196d99bda599a0b94a7ba43bc875069d3a2acd6d12727(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da8e4044177be41b9a49384cbb184a144e0f2068441d10f5f73d44e13f31f245(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    path: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    cmac: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    input: typing.Optional[builtins.str] = None,
    key_version: typing.Optional[jsii.Number] = None,
    mac_length: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    url_mac_length: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
