r'''
# `vault_aws_auth_backend_config_identity`

Refer to the Terraform Registry for docs: [`vault_aws_auth_backend_config_identity`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity).
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


class AwsAuthBackendConfigIdentity(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.awsAuthBackendConfigIdentity.AwsAuthBackendConfigIdentity",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity vault_aws_auth_backend_config_identity}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: typing.Optional[builtins.str] = None,
        ec2_alias: typing.Optional[builtins.str] = None,
        ec2_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
        iam_alias: typing.Optional[builtins.str] = None,
        iam_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity vault_aws_auth_backend_config_identity} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#backend AwsAuthBackendConfigIdentity#backend}
        :param ec2_alias: Configures how to generate the identity alias when using the ec2 auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#ec2_alias AwsAuthBackendConfigIdentity#ec2_alias}
        :param ec2_metadata: The metadata to include on the token returned by the login endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#ec2_metadata AwsAuthBackendConfigIdentity#ec2_metadata}
        :param iam_alias: How to generate the identity alias when using the iam auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#iam_alias AwsAuthBackendConfigIdentity#iam_alias}
        :param iam_metadata: The metadata to include on the token returned by the login endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#iam_metadata AwsAuthBackendConfigIdentity#iam_metadata}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#id AwsAuthBackendConfigIdentity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#namespace AwsAuthBackendConfigIdentity#namespace}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__109cc0b24f14a861754baf4ed7b852266d2b63c2a3e9617510cd7486c477fe42)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AwsAuthBackendConfigIdentityConfig(
            backend=backend,
            ec2_alias=ec2_alias,
            ec2_metadata=ec2_metadata,
            iam_alias=iam_alias,
            iam_metadata=iam_metadata,
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
        '''Generates CDKTF code for importing a AwsAuthBackendConfigIdentity resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AwsAuthBackendConfigIdentity to import.
        :param import_from_id: The id of the existing AwsAuthBackendConfigIdentity that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AwsAuthBackendConfigIdentity to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92cee01c9f02091979430ab76e3443eb95dee2aa77088aa2a06b8ff1441b6a21)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetEc2Alias")
    def reset_ec2_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2Alias", []))

    @jsii.member(jsii_name="resetEc2Metadata")
    def reset_ec2_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2Metadata", []))

    @jsii.member(jsii_name="resetIamAlias")
    def reset_iam_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamAlias", []))

    @jsii.member(jsii_name="resetIamMetadata")
    def reset_iam_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamMetadata", []))

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
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="ec2AliasInput")
    def ec2_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2AliasInput"))

    @builtins.property
    @jsii.member(jsii_name="ec2MetadataInput")
    def ec2_metadata_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ec2MetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="iamAliasInput")
    def iam_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="iamMetadataInput")
    def iam_metadata_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "iamMetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c85f0d0cad02ac218794364115a1f9543413f0d50e2552bb8e78ba7ae83c95bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ec2Alias")
    def ec2_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2Alias"))

    @ec2_alias.setter
    def ec2_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bddeb3d10ae3f5c73137f2c42c84c2248e7c2e60e55b84e2a8300fe26e04ed77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ec2Alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ec2Metadata")
    def ec2_metadata(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ec2Metadata"))

    @ec2_metadata.setter
    def ec2_metadata(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bce2d842d904a10abfe3bb84a59dc919280ac51b0cc72caa7031ece94eabd01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ec2Metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamAlias")
    def iam_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamAlias"))

    @iam_alias.setter
    def iam_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac046271d03e10ae4bdc24386ac5565111afeb0514ec1cfdd56b2c603fc99f55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamAlias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamMetadata")
    def iam_metadata(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "iamMetadata"))

    @iam_metadata.setter
    def iam_metadata(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cc3c0d803a10e099c405df38afc793cedd1c7a6f96dd1a3b931bb3e9e7d4962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamMetadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d1013422f035052bac29da168e9f9c92732d8d5daf88056ce1d8e2a9a9c12b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8708c2503084136a3fd705060f53ab94fd967a91e0209486de9fa83f158a026)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.awsAuthBackendConfigIdentity.AwsAuthBackendConfigIdentityConfig",
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
        "ec2_alias": "ec2Alias",
        "ec2_metadata": "ec2Metadata",
        "iam_alias": "iamAlias",
        "iam_metadata": "iamMetadata",
        "id": "id",
        "namespace": "namespace",
    },
)
class AwsAuthBackendConfigIdentityConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: typing.Optional[builtins.str] = None,
        ec2_alias: typing.Optional[builtins.str] = None,
        ec2_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
        iam_alias: typing.Optional[builtins.str] = None,
        iam_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#backend AwsAuthBackendConfigIdentity#backend}
        :param ec2_alias: Configures how to generate the identity alias when using the ec2 auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#ec2_alias AwsAuthBackendConfigIdentity#ec2_alias}
        :param ec2_metadata: The metadata to include on the token returned by the login endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#ec2_metadata AwsAuthBackendConfigIdentity#ec2_metadata}
        :param iam_alias: How to generate the identity alias when using the iam auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#iam_alias AwsAuthBackendConfigIdentity#iam_alias}
        :param iam_metadata: The metadata to include on the token returned by the login endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#iam_metadata AwsAuthBackendConfigIdentity#iam_metadata}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#id AwsAuthBackendConfigIdentity#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#namespace AwsAuthBackendConfigIdentity#namespace}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61319444d204c36248a3c9e1e9178970b6f7bac2a2ddd2760f53049874d77465)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument ec2_alias", value=ec2_alias, expected_type=type_hints["ec2_alias"])
            check_type(argname="argument ec2_metadata", value=ec2_metadata, expected_type=type_hints["ec2_metadata"])
            check_type(argname="argument iam_alias", value=iam_alias, expected_type=type_hints["iam_alias"])
            check_type(argname="argument iam_metadata", value=iam_metadata, expected_type=type_hints["iam_metadata"])
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
        if backend is not None:
            self._values["backend"] = backend
        if ec2_alias is not None:
            self._values["ec2_alias"] = ec2_alias
        if ec2_metadata is not None:
            self._values["ec2_metadata"] = ec2_metadata
        if iam_alias is not None:
            self._values["iam_alias"] = iam_alias
        if iam_metadata is not None:
            self._values["iam_metadata"] = iam_metadata
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
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the auth backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#backend AwsAuthBackendConfigIdentity#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_alias(self) -> typing.Optional[builtins.str]:
        '''Configures how to generate the identity alias when using the ec2 auth method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#ec2_alias AwsAuthBackendConfigIdentity#ec2_alias}
        '''
        result = self._values.get("ec2_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_metadata(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The metadata to include on the token returned by the login endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#ec2_metadata AwsAuthBackendConfigIdentity#ec2_metadata}
        '''
        result = self._values.get("ec2_metadata")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def iam_alias(self) -> typing.Optional[builtins.str]:
        '''How to generate the identity alias when using the iam auth method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#iam_alias AwsAuthBackendConfigIdentity#iam_alias}
        '''
        result = self._values.get("iam_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_metadata(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The metadata to include on the token returned by the login endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#iam_metadata AwsAuthBackendConfigIdentity#iam_metadata}
        '''
        result = self._values.get("iam_metadata")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#id AwsAuthBackendConfigIdentity#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_config_identity#namespace AwsAuthBackendConfigIdentity#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsAuthBackendConfigIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsAuthBackendConfigIdentity",
    "AwsAuthBackendConfigIdentityConfig",
]

publication.publish()

def _typecheckingstub__109cc0b24f14a861754baf4ed7b852266d2b63c2a3e9617510cd7486c477fe42(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: typing.Optional[builtins.str] = None,
    ec2_alias: typing.Optional[builtins.str] = None,
    ec2_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
    iam_alias: typing.Optional[builtins.str] = None,
    iam_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__92cee01c9f02091979430ab76e3443eb95dee2aa77088aa2a06b8ff1441b6a21(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c85f0d0cad02ac218794364115a1f9543413f0d50e2552bb8e78ba7ae83c95bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bddeb3d10ae3f5c73137f2c42c84c2248e7c2e60e55b84e2a8300fe26e04ed77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bce2d842d904a10abfe3bb84a59dc919280ac51b0cc72caa7031ece94eabd01(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac046271d03e10ae4bdc24386ac5565111afeb0514ec1cfdd56b2c603fc99f55(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cc3c0d803a10e099c405df38afc793cedd1c7a6f96dd1a3b931bb3e9e7d4962(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d1013422f035052bac29da168e9f9c92732d8d5daf88056ce1d8e2a9a9c12b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8708c2503084136a3fd705060f53ab94fd967a91e0209486de9fa83f158a026(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61319444d204c36248a3c9e1e9178970b6f7bac2a2ddd2760f53049874d77465(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: typing.Optional[builtins.str] = None,
    ec2_alias: typing.Optional[builtins.str] = None,
    ec2_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
    iam_alias: typing.Optional[builtins.str] = None,
    iam_metadata: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
