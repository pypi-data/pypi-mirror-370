r'''
# `vault_rabbitmq_secret_backend_role`

Refer to the Terraform Registry for docs: [`vault_rabbitmq_secret_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role).
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


class RabbitmqSecretBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role vault_rabbitmq_secret_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        tags: typing.Optional[builtins.str] = None,
        vhost: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhost", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vhost_topic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhostTopic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role vault_rabbitmq_secret_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The path of the Rabbitmq Secret Backend the role belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#backend RabbitmqSecretBackendRole#backend}
        :param name: Unique name for the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#name RabbitmqSecretBackendRole#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#id RabbitmqSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#namespace RabbitmqSecretBackendRole#namespace}
        :param tags: Specifies a comma-separated RabbitMQ management tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#tags RabbitmqSecretBackendRole#tags}
        :param vhost: vhost block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost RabbitmqSecretBackendRole#vhost}
        :param vhost_topic: vhost_topic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost_topic RabbitmqSecretBackendRole#vhost_topic}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1edc072112152e5e0646d462290961812dce2dfe3829436d80ee4fd2981e849f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RabbitmqSecretBackendRoleConfig(
            backend=backend,
            name=name,
            id=id,
            namespace=namespace,
            tags=tags,
            vhost=vhost,
            vhost_topic=vhost_topic,
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
        '''Generates CDKTF code for importing a RabbitmqSecretBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RabbitmqSecretBackendRole to import.
        :param import_from_id: The id of the existing RabbitmqSecretBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RabbitmqSecretBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9afd988a314fbf6da7756a8022c127f275864d881aad0b120107b1cff58f9e0e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putVhost")
    def put_vhost(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhost", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cf7a07128e60b282f38988f2a09921382f2bd0994ca5a31e1a46f7015e87e3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVhost", [value]))

    @jsii.member(jsii_name="putVhostTopic")
    def put_vhost_topic(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhostTopic", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b8361433e6c35002cbf86643b8653b690b1e4fa78fc393bac905b407544d9c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVhostTopic", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetVhost")
    def reset_vhost(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVhost", []))

    @jsii.member(jsii_name="resetVhostTopic")
    def reset_vhost_topic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVhostTopic", []))

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
    @jsii.member(jsii_name="vhost")
    def vhost(self) -> "RabbitmqSecretBackendRoleVhostList":
        return typing.cast("RabbitmqSecretBackendRoleVhostList", jsii.get(self, "vhost"))

    @builtins.property
    @jsii.member(jsii_name="vhostTopic")
    def vhost_topic(self) -> "RabbitmqSecretBackendRoleVhostTopicList":
        return typing.cast("RabbitmqSecretBackendRoleVhostTopicList", jsii.get(self, "vhostTopic"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="vhostInput")
    def vhost_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhost"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhost"]]], jsii.get(self, "vhostInput"))

    @builtins.property
    @jsii.member(jsii_name="vhostTopicInput")
    def vhost_topic_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopic"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopic"]]], jsii.get(self, "vhostTopicInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b45d8ca2867d8519a1ac0ce16545fb7d7e81b9e2f12718c4677dc388af70791)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d55bcc33ce4645efe15ff8fe0e95888fc9ff25f34f7564624f2b9a10eacaf98d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__473adcc855cbe198f88eee679be31c26846e6a2ce0acb66bc2950ccfb04b2e2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b45d7826ab6dd668304ffc1e6d6433edff8e69234ec5842af4bc5b578919cd1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05eae25fd60814f25a007d44534599a11f5be8c6a52bdf51577828b0d6fcd0ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleConfig",
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
        "name": "name",
        "id": "id",
        "namespace": "namespace",
        "tags": "tags",
        "vhost": "vhost",
        "vhost_topic": "vhostTopic",
    },
)
class RabbitmqSecretBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: builtins.str,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        tags: typing.Optional[builtins.str] = None,
        vhost: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhost", typing.Dict[builtins.str, typing.Any]]]]] = None,
        vhost_topic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhostTopic", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The path of the Rabbitmq Secret Backend the role belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#backend RabbitmqSecretBackendRole#backend}
        :param name: Unique name for the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#name RabbitmqSecretBackendRole#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#id RabbitmqSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#namespace RabbitmqSecretBackendRole#namespace}
        :param tags: Specifies a comma-separated RabbitMQ management tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#tags RabbitmqSecretBackendRole#tags}
        :param vhost: vhost block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost RabbitmqSecretBackendRole#vhost}
        :param vhost_topic: vhost_topic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost_topic RabbitmqSecretBackendRole#vhost_topic}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9051b1e06780c7fffb9b0a5b8235fb3ba7b2e8a0ee06d7208b4dc3c4d20fb774)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vhost", value=vhost, expected_type=type_hints["vhost"])
            check_type(argname="argument vhost_topic", value=vhost_topic, expected_type=type_hints["vhost_topic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
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
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if tags is not None:
            self._values["tags"] = tags
        if vhost is not None:
            self._values["vhost"] = vhost
        if vhost_topic is not None:
            self._values["vhost_topic"] = vhost_topic

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
    def backend(self) -> builtins.str:
        '''The path of the Rabbitmq Secret Backend the role belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#backend RabbitmqSecretBackendRole#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Unique name for the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#name RabbitmqSecretBackendRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#id RabbitmqSecretBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#namespace RabbitmqSecretBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[builtins.str]:
        '''Specifies a comma-separated RabbitMQ management tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#tags RabbitmqSecretBackendRole#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vhost(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhost"]]]:
        '''vhost block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost RabbitmqSecretBackendRole#vhost}
        '''
        result = self._values.get("vhost")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhost"]]], result)

    @builtins.property
    def vhost_topic(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopic"]]]:
        '''vhost_topic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost_topic RabbitmqSecretBackendRole#vhost_topic}
        '''
        result = self._values.get("vhost_topic")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopic"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RabbitmqSecretBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhost",
    jsii_struct_bases=[],
    name_mapping={
        "configure": "configure",
        "host": "host",
        "read": "read",
        "write": "write",
    },
)
class RabbitmqSecretBackendRoleVhost:
    def __init__(
        self,
        *,
        configure: builtins.str,
        host: builtins.str,
        read: builtins.str,
        write: builtins.str,
    ) -> None:
        '''
        :param configure: The configure permissions for this vhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#configure RabbitmqSecretBackendRole#configure}
        :param host: The vhost to set permissions for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#host RabbitmqSecretBackendRole#host}
        :param read: The read permissions for this vhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#read RabbitmqSecretBackendRole#read}
        :param write: The write permissions for this vhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#write RabbitmqSecretBackendRole#write}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d775741708d553fe4b6588ffad0e109b3063c0c6dd55ef99c5f6b853e8183a2)
            check_type(argname="argument configure", value=configure, expected_type=type_hints["configure"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
            check_type(argname="argument write", value=write, expected_type=type_hints["write"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "configure": configure,
            "host": host,
            "read": read,
            "write": write,
        }

    @builtins.property
    def configure(self) -> builtins.str:
        '''The configure permissions for this vhost.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#configure RabbitmqSecretBackendRole#configure}
        '''
        result = self._values.get("configure")
        assert result is not None, "Required property 'configure' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def host(self) -> builtins.str:
        '''The vhost to set permissions for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#host RabbitmqSecretBackendRole#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def read(self) -> builtins.str:
        '''The read permissions for this vhost.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#read RabbitmqSecretBackendRole#read}
        '''
        result = self._values.get("read")
        assert result is not None, "Required property 'read' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def write(self) -> builtins.str:
        '''The write permissions for this vhost.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#write RabbitmqSecretBackendRole#write}
        '''
        result = self._values.get("write")
        assert result is not None, "Required property 'write' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RabbitmqSecretBackendRoleVhost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RabbitmqSecretBackendRoleVhostList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cd93d71ff98dee98f324db53cc9037159a3bca20a8617c49d0c8918cf7ca80ad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "RabbitmqSecretBackendRoleVhostOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc2ece8f69805d169c4d35f23742a9fb44a03654bbb0fb076acba0eb696e9f01)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RabbitmqSecretBackendRoleVhostOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__862af1dfeddbe81e2c61f777b9bdc076fd65a995d648c07c32df0cf33d10787e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb9114878d010286498525b1be218065073a43ee632a2313c8eda2b4291dbcd8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed14f157370f877e80293f97b9d69b6af461790cbfab9e0c0797283a21685b1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhost]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhost]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhost]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6697ecc6b6b1afa4b0cc9525b88ab49d545eb0ff38f7c7c1055db19bd96a1cdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class RabbitmqSecretBackendRoleVhostOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ec95bf3b95a1ba484b3a07195f39b0e789c19b3b456205705224e3e755660cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="configureInput")
    def configure_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configureInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property
    @jsii.member(jsii_name="writeInput")
    def write_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "writeInput"))

    @builtins.property
    @jsii.member(jsii_name="configure")
    def configure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configure"))

    @configure.setter
    def configure(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a8f63457500978e19f83fe79f481971d9715b0f47213bb627988c83a55420ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f54301417573110132f9627d3b45ecb4d780c3c7c0d92d1480fec23fbc93d6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72783524442a8a982745a2bad1b9bdffbb608d6be6aab6810654aff3805adee9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="write")
    def write(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "write"))

    @write.setter
    def write(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f4b9bf5e05e97c0647b7566187fe0058a323114751ea7d4eed57cb8c23d5874)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "write", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhost]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhost]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhost]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3483d7ac7e3f3d16572f5d332a141920e9808df564e9b0ca5dff1dce77110125)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostTopic",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "vhost": "vhost"},
)
class RabbitmqSecretBackendRoleVhostTopic:
    def __init__(
        self,
        *,
        host: builtins.str,
        vhost: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhostTopicVhost", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param host: The vhost to set permissions for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#host RabbitmqSecretBackendRole#host}
        :param vhost: vhost block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost RabbitmqSecretBackendRole#vhost}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd8f9c7a1265066958d6e37126dff5c5e60ac5d26feba877d297e9fae53d882)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument vhost", value=vhost, expected_type=type_hints["vhost"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
        }
        if vhost is not None:
            self._values["vhost"] = vhost

    @builtins.property
    def host(self) -> builtins.str:
        '''The vhost to set permissions for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#host RabbitmqSecretBackendRole#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vhost(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopicVhost"]]]:
        '''vhost block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#vhost RabbitmqSecretBackendRole#vhost}
        '''
        result = self._values.get("vhost")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopicVhost"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RabbitmqSecretBackendRoleVhostTopic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RabbitmqSecretBackendRoleVhostTopicList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostTopicList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4361dda370f9c5eac7cbf977ca5daa1a974a929384da4a9a509e688c48c9a81b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "RabbitmqSecretBackendRoleVhostTopicOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e37c1cafe0ac358b7f68f7ddb3e152027c19bad7c8e19842533d14fcd712a1fc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RabbitmqSecretBackendRoleVhostTopicOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4c52b9c7220c0543d8bb9abd8a1aee3c1e98c7db0a2cd4585635df85caf7adc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffa1096fb96f05f73df1567c74fb10fe5f6486e7b1b53b4aaf27a146b93963d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fb24c6e830ddb0cbdc612abf5cef837790f7122d61f720ebc42fc360d5fcc1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopic]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopic]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22e9b805bb4a98793eb9304689ffff806ddde0daaab6f309a11cbc922bc89364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class RabbitmqSecretBackendRoleVhostTopicOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostTopicOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ecbf7537ea9b998e529969576eea4dc880671006146d75afb0a5cb04782aa7f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putVhost")
    def put_vhost(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RabbitmqSecretBackendRoleVhostTopicVhost", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fdb383b1067e7a09bff07e6c6db4dd80e434ac9c7b9388f621c7183e3a0381d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVhost", [value]))

    @jsii.member(jsii_name="resetVhost")
    def reset_vhost(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVhost", []))

    @builtins.property
    @jsii.member(jsii_name="vhost")
    def vhost(self) -> "RabbitmqSecretBackendRoleVhostTopicVhostList":
        return typing.cast("RabbitmqSecretBackendRoleVhostTopicVhostList", jsii.get(self, "vhost"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="vhostInput")
    def vhost_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopicVhost"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RabbitmqSecretBackendRoleVhostTopicVhost"]]], jsii.get(self, "vhostInput"))

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f8086990eb0ba333287860aa2e9a0f15d5fbe07f8138d582bb897911f65e9fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopic]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopic]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopic]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9ac97e9555baf011dd5aa2ff8e81f1630c66bd7872a900598fa330040f9fbcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostTopicVhost",
    jsii_struct_bases=[],
    name_mapping={"read": "read", "topic": "topic", "write": "write"},
)
class RabbitmqSecretBackendRoleVhostTopicVhost:
    def __init__(
        self,
        *,
        read: builtins.str,
        topic: builtins.str,
        write: builtins.str,
    ) -> None:
        '''
        :param read: The read permissions for this vhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#read RabbitmqSecretBackendRole#read}
        :param topic: The vhost to set permissions for. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#topic RabbitmqSecretBackendRole#topic}
        :param write: The write permissions for this vhost. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#write RabbitmqSecretBackendRole#write}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b12f5e026213a457beb3fbdfa3e00ecaec6a54e2203468a069def33cfcec652)
            check_type(argname="argument read", value=read, expected_type=type_hints["read"])
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
            check_type(argname="argument write", value=write, expected_type=type_hints["write"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "read": read,
            "topic": topic,
            "write": write,
        }

    @builtins.property
    def read(self) -> builtins.str:
        '''The read permissions for this vhost.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#read RabbitmqSecretBackendRole#read}
        '''
        result = self._values.get("read")
        assert result is not None, "Required property 'read' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic(self) -> builtins.str:
        '''The vhost to set permissions for.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#topic RabbitmqSecretBackendRole#topic}
        '''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def write(self) -> builtins.str:
        '''The write permissions for this vhost.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/rabbitmq_secret_backend_role#write RabbitmqSecretBackendRole#write}
        '''
        result = self._values.get("write")
        assert result is not None, "Required property 'write' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RabbitmqSecretBackendRoleVhostTopicVhost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RabbitmqSecretBackendRoleVhostTopicVhostList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostTopicVhostList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d66c757601342caf0bb7cfb637af65bf6c8bec6fa9cba8d4f603c069c0f806ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "RabbitmqSecretBackendRoleVhostTopicVhostOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__447f9b9b1d395a88bc8d303f7fd0db9826459ecc565ce5800db0443563e26633)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RabbitmqSecretBackendRoleVhostTopicVhostOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4980f2ca44fc99b61fae0dec35914762b1ad65d267d5ed9a9009df461fd12414)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6561c9243499b55392b60edb1bda1b558427c97fb4aa7ddd816d01d1f23e29dc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8399f58aadc9372e2f13be1ac81d475eefeb82a4daab00d5d20a0bf0841b90a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopicVhost]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopicVhost]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopicVhost]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29ce46361b1aca551cd79cb1910c1f5be91715d7a91c0e176c86f36e3c3921b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class RabbitmqSecretBackendRoleVhostTopicVhostOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.rabbitmqSecretBackendRole.RabbitmqSecretBackendRoleVhostTopicVhostOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bfce349435f422f5bfed4d7d3fadb488ce2f504e235064270184e9f15e38d56)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="readInput")
    def read_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readInput"))

    @builtins.property
    @jsii.member(jsii_name="topicInput")
    def topic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicInput"))

    @builtins.property
    @jsii.member(jsii_name="writeInput")
    def write_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "writeInput"))

    @builtins.property
    @jsii.member(jsii_name="read")
    def read(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "read"))

    @read.setter
    def read(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcb377562acc61f70665ddff1c405275592459c46e9776449efdfab65249d502)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "read", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topic")
    def topic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topic"))

    @topic.setter
    def topic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f00b84b1cea1e2ee2b96f1180cef755f753c3122256e2551fa4f7651cd65bf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="write")
    def write(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "write"))

    @write.setter
    def write(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d53bf8b5dd78ecadad4c6e9c81368c40b8615d5960242d17e40bab0e0783ca76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "write", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopicVhost]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopicVhost]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopicVhost]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__704f8b20ab2e3ad5ef6288d2a7e5395b30d3963c92fdcd24fd9de1ac040228df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "RabbitmqSecretBackendRole",
    "RabbitmqSecretBackendRoleConfig",
    "RabbitmqSecretBackendRoleVhost",
    "RabbitmqSecretBackendRoleVhostList",
    "RabbitmqSecretBackendRoleVhostOutputReference",
    "RabbitmqSecretBackendRoleVhostTopic",
    "RabbitmqSecretBackendRoleVhostTopicList",
    "RabbitmqSecretBackendRoleVhostTopicOutputReference",
    "RabbitmqSecretBackendRoleVhostTopicVhost",
    "RabbitmqSecretBackendRoleVhostTopicVhostList",
    "RabbitmqSecretBackendRoleVhostTopicVhostOutputReference",
]

publication.publish()

def _typecheckingstub__1edc072112152e5e0646d462290961812dce2dfe3829436d80ee4fd2981e849f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    tags: typing.Optional[builtins.str] = None,
    vhost: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhost, typing.Dict[builtins.str, typing.Any]]]]] = None,
    vhost_topic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhostTopic, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__9afd988a314fbf6da7756a8022c127f275864d881aad0b120107b1cff58f9e0e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cf7a07128e60b282f38988f2a09921382f2bd0994ca5a31e1a46f7015e87e3f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhost, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b8361433e6c35002cbf86643b8653b690b1e4fa78fc393bac905b407544d9c5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhostTopic, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b45d8ca2867d8519a1ac0ce16545fb7d7e81b9e2f12718c4677dc388af70791(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d55bcc33ce4645efe15ff8fe0e95888fc9ff25f34f7564624f2b9a10eacaf98d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__473adcc855cbe198f88eee679be31c26846e6a2ce0acb66bc2950ccfb04b2e2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b45d7826ab6dd668304ffc1e6d6433edff8e69234ec5842af4bc5b578919cd1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05eae25fd60814f25a007d44534599a11f5be8c6a52bdf51577828b0d6fcd0ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9051b1e06780c7fffb9b0a5b8235fb3ba7b2e8a0ee06d7208b4dc3c4d20fb774(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    tags: typing.Optional[builtins.str] = None,
    vhost: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhost, typing.Dict[builtins.str, typing.Any]]]]] = None,
    vhost_topic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhostTopic, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d775741708d553fe4b6588ffad0e109b3063c0c6dd55ef99c5f6b853e8183a2(
    *,
    configure: builtins.str,
    host: builtins.str,
    read: builtins.str,
    write: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd93d71ff98dee98f324db53cc9037159a3bca20a8617c49d0c8918cf7ca80ad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc2ece8f69805d169c4d35f23742a9fb44a03654bbb0fb076acba0eb696e9f01(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__862af1dfeddbe81e2c61f777b9bdc076fd65a995d648c07c32df0cf33d10787e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb9114878d010286498525b1be218065073a43ee632a2313c8eda2b4291dbcd8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed14f157370f877e80293f97b9d69b6af461790cbfab9e0c0797283a21685b1d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6697ecc6b6b1afa4b0cc9525b88ab49d545eb0ff38f7c7c1055db19bd96a1cdf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhost]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec95bf3b95a1ba484b3a07195f39b0e789c19b3b456205705224e3e755660cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a8f63457500978e19f83fe79f481971d9715b0f47213bb627988c83a55420ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f54301417573110132f9627d3b45ecb4d780c3c7c0d92d1480fec23fbc93d6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72783524442a8a982745a2bad1b9bdffbb608d6be6aab6810654aff3805adee9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f4b9bf5e05e97c0647b7566187fe0058a323114751ea7d4eed57cb8c23d5874(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3483d7ac7e3f3d16572f5d332a141920e9808df564e9b0ca5dff1dce77110125(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhost]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd8f9c7a1265066958d6e37126dff5c5e60ac5d26feba877d297e9fae53d882(
    *,
    host: builtins.str,
    vhost: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhostTopicVhost, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4361dda370f9c5eac7cbf977ca5daa1a974a929384da4a9a509e688c48c9a81b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e37c1cafe0ac358b7f68f7ddb3e152027c19bad7c8e19842533d14fcd712a1fc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4c52b9c7220c0543d8bb9abd8a1aee3c1e98c7db0a2cd4585635df85caf7adc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffa1096fb96f05f73df1567c74fb10fe5f6486e7b1b53b4aaf27a146b93963d3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fb24c6e830ddb0cbdc612abf5cef837790f7122d61f720ebc42fc360d5fcc1d(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22e9b805bb4a98793eb9304689ffff806ddde0daaab6f309a11cbc922bc89364(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopic]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ecbf7537ea9b998e529969576eea4dc880671006146d75afb0a5cb04782aa7f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fdb383b1067e7a09bff07e6c6db4dd80e434ac9c7b9388f621c7183e3a0381d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RabbitmqSecretBackendRoleVhostTopicVhost, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f8086990eb0ba333287860aa2e9a0f15d5fbe07f8138d582bb897911f65e9fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9ac97e9555baf011dd5aa2ff8e81f1630c66bd7872a900598fa330040f9fbcd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopic]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b12f5e026213a457beb3fbdfa3e00ecaec6a54e2203468a069def33cfcec652(
    *,
    read: builtins.str,
    topic: builtins.str,
    write: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d66c757601342caf0bb7cfb637af65bf6c8bec6fa9cba8d4f603c069c0f806ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__447f9b9b1d395a88bc8d303f7fd0db9826459ecc565ce5800db0443563e26633(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4980f2ca44fc99b61fae0dec35914762b1ad65d267d5ed9a9009df461fd12414(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6561c9243499b55392b60edb1bda1b558427c97fb4aa7ddd816d01d1f23e29dc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8399f58aadc9372e2f13be1ac81d475eefeb82a4daab00d5d20a0bf0841b90a8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29ce46361b1aca551cd79cb1910c1f5be91715d7a91c0e176c86f36e3c3921b9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RabbitmqSecretBackendRoleVhostTopicVhost]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bfce349435f422f5bfed4d7d3fadb488ce2f504e235064270184e9f15e38d56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcb377562acc61f70665ddff1c405275592459c46e9776449efdfab65249d502(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f00b84b1cea1e2ee2b96f1180cef755f753c3122256e2551fa4f7651cd65bf6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d53bf8b5dd78ecadad4c6e9c81368c40b8615d5960242d17e40bab0e0783ca76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__704f8b20ab2e3ad5ef6288d2a7e5395b30d3963c92fdcd24fd9de1ac040228df(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RabbitmqSecretBackendRoleVhostTopicVhost]],
) -> None:
    """Type checking stubs"""
    pass
