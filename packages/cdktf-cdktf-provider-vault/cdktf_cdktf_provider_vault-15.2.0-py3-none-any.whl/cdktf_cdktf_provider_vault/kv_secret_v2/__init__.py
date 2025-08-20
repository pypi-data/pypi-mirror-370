r'''
# `vault_kv_secret_v2`

Refer to the Terraform Registry for docs: [`vault_kv_secret_v2`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2).
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


class KvSecretV2(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.kvSecretV2.KvSecretV2",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2 vault_kv_secret_v2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        mount: builtins.str,
        name: builtins.str,
        cas: typing.Optional[jsii.Number] = None,
        custom_metadata: typing.Optional[typing.Union["KvSecretV2CustomMetadata", typing.Dict[builtins.str, typing.Any]]] = None,
        data_json: typing.Optional[builtins.str] = None,
        data_json_wo: typing.Optional[builtins.str] = None,
        data_json_wo_version: typing.Optional[jsii.Number] = None,
        delete_all_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_read: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2 vault_kv_secret_v2} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param mount: Path where KV-V2 engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#mount KvSecretV2#mount}
        :param name: Full name of the secret. For a nested secret, the name is the nested path excluding the mount and data prefix. For example, for a secret at 'kvv2/data/foo/bar/baz', the name is 'foo/bar/baz' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#name KvSecretV2#name}
        :param cas: This flag is required if cas_required is set to true on either the secret or the engine's config. In order for a write to be successful, cas must be set to the current version of the secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#cas KvSecretV2#cas}
        :param custom_metadata: custom_metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#custom_metadata KvSecretV2#custom_metadata}
        :param data_json: JSON-encoded secret data to write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json KvSecretV2#data_json}
        :param data_json_wo: Write-Only JSON-encoded secret data to write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json_wo KvSecretV2#data_json_wo}
        :param data_json_wo_version: Version counter for write-only secret data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json_wo_version KvSecretV2#data_json_wo_version}
        :param delete_all_versions: If set to true, permanently deletes all versions for the specified key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#delete_all_versions KvSecretV2#delete_all_versions}
        :param disable_read: If set to true, disables reading secret from Vault; note: drift won't be detected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#disable_read KvSecretV2#disable_read}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#id KvSecretV2#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#namespace KvSecretV2#namespace}
        :param options: An object that holds option settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#options KvSecretV2#options}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32c83490a8ab3a1748099ae27f254f1d3736311e94cb7238bf63e03f46a19ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = KvSecretV2Config(
            mount=mount,
            name=name,
            cas=cas,
            custom_metadata=custom_metadata,
            data_json=data_json,
            data_json_wo=data_json_wo,
            data_json_wo_version=data_json_wo_version,
            delete_all_versions=delete_all_versions,
            disable_read=disable_read,
            id=id,
            namespace=namespace,
            options=options,
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
        '''Generates CDKTF code for importing a KvSecretV2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KvSecretV2 to import.
        :param import_from_id: The id of the existing KvSecretV2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KvSecretV2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784a271b49b1e61272b316bc3e25a5242c4cd1d5339fa83606a85d6d4c065784)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCustomMetadata")
    def put_custom_metadata(
        self,
        *,
        cas_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        delete_version_after: typing.Optional[jsii.Number] = None,
        max_versions: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cas_required: If true, all keys will require the cas parameter to be set on all write requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#cas_required KvSecretV2#cas_required}
        :param data: A map of arbitrary string to string valued user-provided metadata meant to describe the secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data KvSecretV2#data}
        :param delete_version_after: If set, specifies the length of time before a version is deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#delete_version_after KvSecretV2#delete_version_after}
        :param max_versions: The number of versions to keep per key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#max_versions KvSecretV2#max_versions}
        '''
        value = KvSecretV2CustomMetadata(
            cas_required=cas_required,
            data=data,
            delete_version_after=delete_version_after,
            max_versions=max_versions,
        )

        return typing.cast(None, jsii.invoke(self, "putCustomMetadata", [value]))

    @jsii.member(jsii_name="resetCas")
    def reset_cas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCas", []))

    @jsii.member(jsii_name="resetCustomMetadata")
    def reset_custom_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomMetadata", []))

    @jsii.member(jsii_name="resetDataJson")
    def reset_data_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataJson", []))

    @jsii.member(jsii_name="resetDataJsonWo")
    def reset_data_json_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataJsonWo", []))

    @jsii.member(jsii_name="resetDataJsonWoVersion")
    def reset_data_json_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataJsonWoVersion", []))

    @jsii.member(jsii_name="resetDeleteAllVersions")
    def reset_delete_all_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteAllVersions", []))

    @jsii.member(jsii_name="resetDisableRead")
    def reset_disable_read(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableRead", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

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
    @jsii.member(jsii_name="customMetadata")
    def custom_metadata(self) -> "KvSecretV2CustomMetadataOutputReference":
        return typing.cast("KvSecretV2CustomMetadataOutputReference", jsii.get(self, "customMetadata"))

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property
    @jsii.member(jsii_name="casInput")
    def cas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "casInput"))

    @builtins.property
    @jsii.member(jsii_name="customMetadataInput")
    def custom_metadata_input(self) -> typing.Optional["KvSecretV2CustomMetadata"]:
        return typing.cast(typing.Optional["KvSecretV2CustomMetadata"], jsii.get(self, "customMetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="dataJsonInput")
    def data_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="dataJsonWoInput")
    def data_json_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataJsonWoInput"))

    @builtins.property
    @jsii.member(jsii_name="dataJsonWoVersionInput")
    def data_json_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dataJsonWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteAllVersionsInput")
    def delete_all_versions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteAllVersionsInput"))

    @builtins.property
    @jsii.member(jsii_name="disableReadInput")
    def disable_read_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableReadInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mountInput")
    def mount_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mountInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "optionsInput"))

    @builtins.property
    @jsii.member(jsii_name="cas")
    def cas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cas"))

    @cas.setter
    def cas(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b4dd1edaf43f898587d29f6705fc6fdc4be77fa7786e04fe94e55e32fe5d8c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataJson")
    def data_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataJson"))

    @data_json.setter
    def data_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__021de214b2a8c50cd18247e2dad3453a98daeddbdd0e08d456961db11d49740f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataJsonWo")
    def data_json_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataJsonWo"))

    @data_json_wo.setter
    def data_json_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4633a1d25b4b46da45528f5e787214dce2f5874c85af567e3c43f0d3315cd2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataJsonWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataJsonWoVersion")
    def data_json_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dataJsonWoVersion"))

    @data_json_wo_version.setter
    def data_json_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__187781f7b65854519726c465c9d3f42d0fa82415408fbde00c23a19739c7a1b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataJsonWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteAllVersions")
    def delete_all_versions(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deleteAllVersions"))

    @delete_all_versions.setter
    def delete_all_versions(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c447aad2745e9b4f12545f95f144e8d5c7b8ed2b12c88c7bf5eb2d14d5833962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteAllVersions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableRead")
    def disable_read(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableRead"))

    @disable_read.setter
    def disable_read(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__468acd966be3147bd86759ca1624205837b2b9a12d0bc7771523678e0a28b711)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableRead", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b7dd473d4a42c447a0b3edd2e992d4017e600a636097d0be9af8226fc240dca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mount")
    def mount(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mount"))

    @mount.setter
    def mount(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd78ef891a24254758a29a674518d669f0ef26868583886dc46c2defb7dfb377)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cdc1b428361bf8f34496d77bc32ad2ae64f99e7ca6554edc84e269dcfa64cb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ba614b343fafae2d1c4bd356d7cde81085e4b7139f67dd16edc0641da67d8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__891810a2e593f752366c9a967c3120a1b9e64f552222c5adfd651d57f3b19122)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.kvSecretV2.KvSecretV2Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "mount": "mount",
        "name": "name",
        "cas": "cas",
        "custom_metadata": "customMetadata",
        "data_json": "dataJson",
        "data_json_wo": "dataJsonWo",
        "data_json_wo_version": "dataJsonWoVersion",
        "delete_all_versions": "deleteAllVersions",
        "disable_read": "disableRead",
        "id": "id",
        "namespace": "namespace",
        "options": "options",
    },
)
class KvSecretV2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        mount: builtins.str,
        name: builtins.str,
        cas: typing.Optional[jsii.Number] = None,
        custom_metadata: typing.Optional[typing.Union["KvSecretV2CustomMetadata", typing.Dict[builtins.str, typing.Any]]] = None,
        data_json: typing.Optional[builtins.str] = None,
        data_json_wo: typing.Optional[builtins.str] = None,
        data_json_wo_version: typing.Optional[jsii.Number] = None,
        delete_all_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_read: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param mount: Path where KV-V2 engine is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#mount KvSecretV2#mount}
        :param name: Full name of the secret. For a nested secret, the name is the nested path excluding the mount and data prefix. For example, for a secret at 'kvv2/data/foo/bar/baz', the name is 'foo/bar/baz' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#name KvSecretV2#name}
        :param cas: This flag is required if cas_required is set to true on either the secret or the engine's config. In order for a write to be successful, cas must be set to the current version of the secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#cas KvSecretV2#cas}
        :param custom_metadata: custom_metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#custom_metadata KvSecretV2#custom_metadata}
        :param data_json: JSON-encoded secret data to write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json KvSecretV2#data_json}
        :param data_json_wo: Write-Only JSON-encoded secret data to write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json_wo KvSecretV2#data_json_wo}
        :param data_json_wo_version: Version counter for write-only secret data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json_wo_version KvSecretV2#data_json_wo_version}
        :param delete_all_versions: If set to true, permanently deletes all versions for the specified key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#delete_all_versions KvSecretV2#delete_all_versions}
        :param disable_read: If set to true, disables reading secret from Vault; note: drift won't be detected. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#disable_read KvSecretV2#disable_read}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#id KvSecretV2#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#namespace KvSecretV2#namespace}
        :param options: An object that holds option settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#options KvSecretV2#options}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(custom_metadata, dict):
            custom_metadata = KvSecretV2CustomMetadata(**custom_metadata)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94bae1042e48b059ac2760ebd8e822940228add04523fc1b8689f4730e2d2075)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument cas", value=cas, expected_type=type_hints["cas"])
            check_type(argname="argument custom_metadata", value=custom_metadata, expected_type=type_hints["custom_metadata"])
            check_type(argname="argument data_json", value=data_json, expected_type=type_hints["data_json"])
            check_type(argname="argument data_json_wo", value=data_json_wo, expected_type=type_hints["data_json_wo"])
            check_type(argname="argument data_json_wo_version", value=data_json_wo_version, expected_type=type_hints["data_json_wo_version"])
            check_type(argname="argument delete_all_versions", value=delete_all_versions, expected_type=type_hints["delete_all_versions"])
            check_type(argname="argument disable_read", value=disable_read, expected_type=type_hints["disable_read"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mount": mount,
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
        if cas is not None:
            self._values["cas"] = cas
        if custom_metadata is not None:
            self._values["custom_metadata"] = custom_metadata
        if data_json is not None:
            self._values["data_json"] = data_json
        if data_json_wo is not None:
            self._values["data_json_wo"] = data_json_wo
        if data_json_wo_version is not None:
            self._values["data_json_wo_version"] = data_json_wo_version
        if delete_all_versions is not None:
            self._values["delete_all_versions"] = delete_all_versions
        if disable_read is not None:
            self._values["disable_read"] = disable_read
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if options is not None:
            self._values["options"] = options

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
    def mount(self) -> builtins.str:
        '''Path where KV-V2 engine is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#mount KvSecretV2#mount}
        '''
        result = self._values.get("mount")
        assert result is not None, "Required property 'mount' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Full name of the secret.

        For a nested secret, the name is the nested path excluding the mount and data prefix. For example, for a secret at 'kvv2/data/foo/bar/baz', the name is 'foo/bar/baz'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#name KvSecretV2#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cas(self) -> typing.Optional[jsii.Number]:
        '''This flag is required if cas_required is set to true on either the secret or the engine's config.

        In order for a write to be successful, cas must be set to the current version of the secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#cas KvSecretV2#cas}
        '''
        result = self._values.get("cas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def custom_metadata(self) -> typing.Optional["KvSecretV2CustomMetadata"]:
        '''custom_metadata block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#custom_metadata KvSecretV2#custom_metadata}
        '''
        result = self._values.get("custom_metadata")
        return typing.cast(typing.Optional["KvSecretV2CustomMetadata"], result)

    @builtins.property
    def data_json(self) -> typing.Optional[builtins.str]:
        '''JSON-encoded secret data to write.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json KvSecretV2#data_json}
        '''
        result = self._values.get("data_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_json_wo(self) -> typing.Optional[builtins.str]:
        '''Write-Only JSON-encoded secret data to write.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json_wo KvSecretV2#data_json_wo}
        '''
        result = self._values.get("data_json_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_json_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for write-only secret data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data_json_wo_version KvSecretV2#data_json_wo_version}
        '''
        result = self._values.get("data_json_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delete_all_versions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, permanently deletes all versions for the specified key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#delete_all_versions KvSecretV2#delete_all_versions}
        '''
        result = self._values.get("delete_all_versions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_read(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, disables reading secret from Vault; note: drift won't be detected.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#disable_read KvSecretV2#disable_read}
        '''
        result = self._values.get("disable_read")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#id KvSecretV2#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#namespace KvSecretV2#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An object that holds option settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#options KvSecretV2#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KvSecretV2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.kvSecretV2.KvSecretV2CustomMetadata",
    jsii_struct_bases=[],
    name_mapping={
        "cas_required": "casRequired",
        "data": "data",
        "delete_version_after": "deleteVersionAfter",
        "max_versions": "maxVersions",
    },
)
class KvSecretV2CustomMetadata:
    def __init__(
        self,
        *,
        cas_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        delete_version_after: typing.Optional[jsii.Number] = None,
        max_versions: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cas_required: If true, all keys will require the cas parameter to be set on all write requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#cas_required KvSecretV2#cas_required}
        :param data: A map of arbitrary string to string valued user-provided metadata meant to describe the secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data KvSecretV2#data}
        :param delete_version_after: If set, specifies the length of time before a version is deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#delete_version_after KvSecretV2#delete_version_after}
        :param max_versions: The number of versions to keep per key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#max_versions KvSecretV2#max_versions}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59f7d6cd2799f27dda774370edd57aadf303430798cb6a17b2f19085eca7d43a)
            check_type(argname="argument cas_required", value=cas_required, expected_type=type_hints["cas_required"])
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
            check_type(argname="argument delete_version_after", value=delete_version_after, expected_type=type_hints["delete_version_after"])
            check_type(argname="argument max_versions", value=max_versions, expected_type=type_hints["max_versions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cas_required is not None:
            self._values["cas_required"] = cas_required
        if data is not None:
            self._values["data"] = data
        if delete_version_after is not None:
            self._values["delete_version_after"] = delete_version_after
        if max_versions is not None:
            self._values["max_versions"] = max_versions

    @builtins.property
    def cas_required(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, all keys will require the cas parameter to be set on all write requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#cas_required KvSecretV2#cas_required}
        '''
        result = self._values.get("cas_required")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def data(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of arbitrary string to string valued user-provided metadata meant to describe the secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#data KvSecretV2#data}
        '''
        result = self._values.get("data")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def delete_version_after(self) -> typing.Optional[jsii.Number]:
        '''If set, specifies the length of time before a version is deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#delete_version_after KvSecretV2#delete_version_after}
        '''
        result = self._values.get("delete_version_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_versions(self) -> typing.Optional[jsii.Number]:
        '''The number of versions to keep per key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kv_secret_v2#max_versions KvSecretV2#max_versions}
        '''
        result = self._values.get("max_versions")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KvSecretV2CustomMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KvSecretV2CustomMetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.kvSecretV2.KvSecretV2CustomMetadataOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5500df4cedd3c5c0cd936608bb1893d91f0e076cdc2e4d988aab9fc8c93b1c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCasRequired")
    def reset_cas_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCasRequired", []))

    @jsii.member(jsii_name="resetData")
    def reset_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetData", []))

    @jsii.member(jsii_name="resetDeleteVersionAfter")
    def reset_delete_version_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteVersionAfter", []))

    @jsii.member(jsii_name="resetMaxVersions")
    def reset_max_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxVersions", []))

    @builtins.property
    @jsii.member(jsii_name="casRequiredInput")
    def cas_required_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "casRequiredInput"))

    @builtins.property
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dataInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteVersionAfterInput")
    def delete_version_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deleteVersionAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="maxVersionsInput")
    def max_versions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxVersionsInput"))

    @builtins.property
    @jsii.member(jsii_name="casRequired")
    def cas_required(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "casRequired"))

    @cas_required.setter
    def cas_required(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b84ed507bcf1e8db4d4a95ce7ed146af182cd7485f22e9df43937fa48f39b26f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "casRequired", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "data"))

    @data.setter
    def data(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__394cd4c1ec16a1bdf95ff33ed01fa542a177019ab9727817b80e12e744d52249)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "data", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteVersionAfter")
    def delete_version_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deleteVersionAfter"))

    @delete_version_after.setter
    def delete_version_after(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c88ea0b627319849acd7846b4f8772b39410e54b09c794dc9aefeae232deecd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteVersionAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxVersions")
    def max_versions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxVersions"))

    @max_versions.setter
    def max_versions(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__945f00c6f609bffef6458ab4a18f1e5d56e18d5f4b27ddec77386d2f6450ac8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxVersions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[KvSecretV2CustomMetadata]:
        return typing.cast(typing.Optional[KvSecretV2CustomMetadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[KvSecretV2CustomMetadata]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1684e996e74600de24398a0458a252532e3d752296bda2b50b3eaaad7481cd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "KvSecretV2",
    "KvSecretV2Config",
    "KvSecretV2CustomMetadata",
    "KvSecretV2CustomMetadataOutputReference",
]

publication.publish()

def _typecheckingstub__f32c83490a8ab3a1748099ae27f254f1d3736311e94cb7238bf63e03f46a19ca(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    mount: builtins.str,
    name: builtins.str,
    cas: typing.Optional[jsii.Number] = None,
    custom_metadata: typing.Optional[typing.Union[KvSecretV2CustomMetadata, typing.Dict[builtins.str, typing.Any]]] = None,
    data_json: typing.Optional[builtins.str] = None,
    data_json_wo: typing.Optional[builtins.str] = None,
    data_json_wo_version: typing.Optional[jsii.Number] = None,
    delete_all_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_read: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
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

def _typecheckingstub__784a271b49b1e61272b316bc3e25a5242c4cd1d5339fa83606a85d6d4c065784(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b4dd1edaf43f898587d29f6705fc6fdc4be77fa7786e04fe94e55e32fe5d8c7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__021de214b2a8c50cd18247e2dad3453a98daeddbdd0e08d456961db11d49740f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4633a1d25b4b46da45528f5e787214dce2f5874c85af567e3c43f0d3315cd2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__187781f7b65854519726c465c9d3f42d0fa82415408fbde00c23a19739c7a1b7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c447aad2745e9b4f12545f95f144e8d5c7b8ed2b12c88c7bf5eb2d14d5833962(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__468acd966be3147bd86759ca1624205837b2b9a12d0bc7771523678e0a28b711(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b7dd473d4a42c447a0b3edd2e992d4017e600a636097d0be9af8226fc240dca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd78ef891a24254758a29a674518d669f0ef26868583886dc46c2defb7dfb377(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cdc1b428361bf8f34496d77bc32ad2ae64f99e7ca6554edc84e269dcfa64cb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ba614b343fafae2d1c4bd356d7cde81085e4b7139f67dd16edc0641da67d8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__891810a2e593f752366c9a967c3120a1b9e64f552222c5adfd651d57f3b19122(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94bae1042e48b059ac2760ebd8e822940228add04523fc1b8689f4730e2d2075(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mount: builtins.str,
    name: builtins.str,
    cas: typing.Optional[jsii.Number] = None,
    custom_metadata: typing.Optional[typing.Union[KvSecretV2CustomMetadata, typing.Dict[builtins.str, typing.Any]]] = None,
    data_json: typing.Optional[builtins.str] = None,
    data_json_wo: typing.Optional[builtins.str] = None,
    data_json_wo_version: typing.Optional[jsii.Number] = None,
    delete_all_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_read: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59f7d6cd2799f27dda774370edd57aadf303430798cb6a17b2f19085eca7d43a(
    *,
    cas_required: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    delete_version_after: typing.Optional[jsii.Number] = None,
    max_versions: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5500df4cedd3c5c0cd936608bb1893d91f0e076cdc2e4d988aab9fc8c93b1c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b84ed507bcf1e8db4d4a95ce7ed146af182cd7485f22e9df43937fa48f39b26f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__394cd4c1ec16a1bdf95ff33ed01fa542a177019ab9727817b80e12e744d52249(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c88ea0b627319849acd7846b4f8772b39410e54b09c794dc9aefeae232deecd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__945f00c6f609bffef6458ab4a18f1e5d56e18d5f4b27ddec77386d2f6450ac8e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1684e996e74600de24398a0458a252532e3d752296bda2b50b3eaaad7481cd7(
    value: typing.Optional[KvSecretV2CustomMetadata],
) -> None:
    """Type checking stubs"""
    pass
