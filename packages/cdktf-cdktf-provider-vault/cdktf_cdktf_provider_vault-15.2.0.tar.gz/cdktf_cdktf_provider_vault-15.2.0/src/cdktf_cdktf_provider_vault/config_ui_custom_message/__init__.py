r'''
# `vault_config_ui_custom_message`

Refer to the Terraform Registry for docs: [`vault_config_ui_custom_message`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message).
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


class ConfigUiCustomMessage(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.configUiCustomMessage.ConfigUiCustomMessage",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message vault_config_ui_custom_message}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        message_base64: builtins.str,
        start_time: builtins.str,
        title: builtins.str,
        authenticated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        end_time: typing.Optional[builtins.str] = None,
        link: typing.Optional[typing.Union["ConfigUiCustomMessageLink", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message vault_config_ui_custom_message} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param message_base64: The base64-encoded content of the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#message_base64 ConfigUiCustomMessage#message_base64}
        :param start_time: The starting time of the active period of the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#start_time ConfigUiCustomMessage#start_time}
        :param title: The title of the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#title ConfigUiCustomMessage#title}
        :param authenticated: A flag indicating whether the custom message is displayed pre-login (false) or post-login (true). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#authenticated ConfigUiCustomMessage#authenticated}
        :param end_time: The ending time of the active period of the custom message. Can be omitted for non-expiring message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#end_time ConfigUiCustomMessage#end_time}
        :param link: link block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#link ConfigUiCustomMessage#link}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#namespace ConfigUiCustomMessage#namespace}
        :param options: A map containing additional options for the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#options ConfigUiCustomMessage#options}
        :param type: The display type of custom message. Allowed values are banner and modal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#type ConfigUiCustomMessage#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe832f8c1115c4e640d6e3cd270be6994de1d441f14e9e63ac463187947261f2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ConfigUiCustomMessageConfig(
            message_base64=message_base64,
            start_time=start_time,
            title=title,
            authenticated=authenticated,
            end_time=end_time,
            link=link,
            namespace=namespace,
            options=options,
            type=type,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a ConfigUiCustomMessage resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConfigUiCustomMessage to import.
        :param import_from_id: The id of the existing ConfigUiCustomMessage that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConfigUiCustomMessage to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__687b09d643e69a7051e9fc77a9fc00e0a766cd2121c8f0f869bc59905c8c6404)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putLink")
    def put_link(self, *, href: builtins.str, title: builtins.str) -> None:
        '''
        :param href: The URL of the hyperlink. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#href ConfigUiCustomMessage#href}
        :param title: The title of the hyperlink. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#title ConfigUiCustomMessage#title}
        '''
        value = ConfigUiCustomMessageLink(href=href, title=title)

        return typing.cast(None, jsii.invoke(self, "putLink", [value]))

    @jsii.member(jsii_name="resetAuthenticated")
    def reset_authenticated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticated", []))

    @jsii.member(jsii_name="resetEndTime")
    def reset_end_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndTime", []))

    @jsii.member(jsii_name="resetLink")
    def reset_link(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLink", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="link")
    def link(self) -> "ConfigUiCustomMessageLinkOutputReference":
        return typing.cast("ConfigUiCustomMessageLinkOutputReference", jsii.get(self, "link"))

    @builtins.property
    @jsii.member(jsii_name="authenticatedInput")
    def authenticated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "authenticatedInput"))

    @builtins.property
    @jsii.member(jsii_name="endTimeInput")
    def end_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="linkInput")
    def link_input(self) -> typing.Optional["ConfigUiCustomMessageLink"]:
        return typing.cast(typing.Optional["ConfigUiCustomMessageLink"], jsii.get(self, "linkInput"))

    @builtins.property
    @jsii.member(jsii_name="messageBase64Input")
    def message_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageBase64Input"))

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
    @jsii.member(jsii_name="startTimeInput")
    def start_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticated")
    def authenticated(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "authenticated"))

    @authenticated.setter
    def authenticated(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__983323cac4684b6f977c04082b8723ec098c69209b6d51a28e3dc4a5d1983b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endTime")
    def end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endTime"))

    @end_time.setter
    def end_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f634a0750a02911db3023ec0d41a4e9e6b6980c3d3b69a7de2560dc425e0e231)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageBase64")
    def message_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageBase64"))

    @message_base64.setter
    def message_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eef0f714d40e10392b8ec2c52efdc27fcb8609dd0fcf32d017a82f011180812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageBase64", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57a3640340dc0e27f15e81e99888b467cacda9ebfff9aa418a037fedc8c65abe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dea281279e09fe2982156be93f7c71cff4fa12878908c054a47d388f291d20ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "options", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startTime")
    def start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startTime"))

    @start_time.setter
    def start_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3409f1203f694aad59a1d613e8a17959d06f4726ce0d2dd00b74291cc31aea33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c82a925c9af934f3753b602fd39633c83f60adb0a7491fbb48415780141c110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1111d257063a23b7f81f141b6ba5493efaaa5555124f21cdd52a18e3443d4033)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.configUiCustomMessage.ConfigUiCustomMessageConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "message_base64": "messageBase64",
        "start_time": "startTime",
        "title": "title",
        "authenticated": "authenticated",
        "end_time": "endTime",
        "link": "link",
        "namespace": "namespace",
        "options": "options",
        "type": "type",
    },
)
class ConfigUiCustomMessageConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        message_base64: builtins.str,
        start_time: builtins.str,
        title: builtins.str,
        authenticated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        end_time: typing.Optional[builtins.str] = None,
        link: typing.Optional[typing.Union["ConfigUiCustomMessageLink", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param message_base64: The base64-encoded content of the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#message_base64 ConfigUiCustomMessage#message_base64}
        :param start_time: The starting time of the active period of the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#start_time ConfigUiCustomMessage#start_time}
        :param title: The title of the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#title ConfigUiCustomMessage#title}
        :param authenticated: A flag indicating whether the custom message is displayed pre-login (false) or post-login (true). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#authenticated ConfigUiCustomMessage#authenticated}
        :param end_time: The ending time of the active period of the custom message. Can be omitted for non-expiring message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#end_time ConfigUiCustomMessage#end_time}
        :param link: link block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#link ConfigUiCustomMessage#link}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#namespace ConfigUiCustomMessage#namespace}
        :param options: A map containing additional options for the custom message. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#options ConfigUiCustomMessage#options}
        :param type: The display type of custom message. Allowed values are banner and modal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#type ConfigUiCustomMessage#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(link, dict):
            link = ConfigUiCustomMessageLink(**link)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67a88e561982d46bd031764ac75ef48d5f97274b716603e47a9d50e57c90b2a0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument message_base64", value=message_base64, expected_type=type_hints["message_base64"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
            check_type(argname="argument authenticated", value=authenticated, expected_type=type_hints["authenticated"])
            check_type(argname="argument end_time", value=end_time, expected_type=type_hints["end_time"])
            check_type(argname="argument link", value=link, expected_type=type_hints["link"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "message_base64": message_base64,
            "start_time": start_time,
            "title": title,
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
        if authenticated is not None:
            self._values["authenticated"] = authenticated
        if end_time is not None:
            self._values["end_time"] = end_time
        if link is not None:
            self._values["link"] = link
        if namespace is not None:
            self._values["namespace"] = namespace
        if options is not None:
            self._values["options"] = options
        if type is not None:
            self._values["type"] = type

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
    def message_base64(self) -> builtins.str:
        '''The base64-encoded content of the custom message.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#message_base64 ConfigUiCustomMessage#message_base64}
        '''
        result = self._values.get("message_base64")
        assert result is not None, "Required property 'message_base64' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def start_time(self) -> builtins.str:
        '''The starting time of the active period of the custom message.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#start_time ConfigUiCustomMessage#start_time}
        '''
        result = self._values.get("start_time")
        assert result is not None, "Required property 'start_time' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''The title of the custom message.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#title ConfigUiCustomMessage#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authenticated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''A flag indicating whether the custom message is displayed pre-login (false) or post-login (true).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#authenticated ConfigUiCustomMessage#authenticated}
        '''
        result = self._values.get("authenticated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def end_time(self) -> typing.Optional[builtins.str]:
        '''The ending time of the active period of the custom message. Can be omitted for non-expiring message.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#end_time ConfigUiCustomMessage#end_time}
        '''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def link(self) -> typing.Optional["ConfigUiCustomMessageLink"]:
        '''link block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#link ConfigUiCustomMessage#link}
        '''
        result = self._values.get("link")
        return typing.cast(typing.Optional["ConfigUiCustomMessageLink"], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#namespace ConfigUiCustomMessage#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map containing additional options for the custom message.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#options ConfigUiCustomMessage#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The display type of custom message. Allowed values are banner and modal.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#type ConfigUiCustomMessage#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigUiCustomMessageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.configUiCustomMessage.ConfigUiCustomMessageLink",
    jsii_struct_bases=[],
    name_mapping={"href": "href", "title": "title"},
)
class ConfigUiCustomMessageLink:
    def __init__(self, *, href: builtins.str, title: builtins.str) -> None:
        '''
        :param href: The URL of the hyperlink. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#href ConfigUiCustomMessage#href}
        :param title: The title of the hyperlink. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#title ConfigUiCustomMessage#title}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df1fe0311d1fb6b6eb6ea51d2910c171351277b32b256acc8d52693a59e80578)
            check_type(argname="argument href", value=href, expected_type=type_hints["href"])
            check_type(argname="argument title", value=title, expected_type=type_hints["title"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "href": href,
            "title": title,
        }

    @builtins.property
    def href(self) -> builtins.str:
        '''The URL of the hyperlink.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#href ConfigUiCustomMessage#href}
        '''
        result = self._values.get("href")
        assert result is not None, "Required property 'href' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''The title of the hyperlink.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/config_ui_custom_message#title ConfigUiCustomMessage#title}
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigUiCustomMessageLink(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConfigUiCustomMessageLinkOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.configUiCustomMessage.ConfigUiCustomMessageLinkOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__901ccd87dbf6b4b9ef70daf6cc23b78c0557be1e8c49623e64f9f5750f0e7db6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="hrefInput")
    def href_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hrefInput"))

    @builtins.property
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property
    @jsii.member(jsii_name="href")
    def href(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "href"))

    @href.setter
    def href(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee8ac0b73b58edd7a4226d6387c0375460193b9e3ce3ee809987c9c1c4f5763e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "href", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2407a64b72f9e80b624a56d87116f2f8b3aad26e92e0b80a6ea4700563a7132f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "title", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ConfigUiCustomMessageLink]:
        return typing.cast(typing.Optional[ConfigUiCustomMessageLink], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ConfigUiCustomMessageLink]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0368c86ea2009c12888b047b499d63296456f85deafcc238d229d7666542ddfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "ConfigUiCustomMessage",
    "ConfigUiCustomMessageConfig",
    "ConfigUiCustomMessageLink",
    "ConfigUiCustomMessageLinkOutputReference",
]

publication.publish()

def _typecheckingstub__fe832f8c1115c4e640d6e3cd270be6994de1d441f14e9e63ac463187947261f2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    message_base64: builtins.str,
    start_time: builtins.str,
    title: builtins.str,
    authenticated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    end_time: typing.Optional[builtins.str] = None,
    link: typing.Optional[typing.Union[ConfigUiCustomMessageLink, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__687b09d643e69a7051e9fc77a9fc00e0a766cd2121c8f0f869bc59905c8c6404(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__983323cac4684b6f977c04082b8723ec098c69209b6d51a28e3dc4a5d1983b91(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f634a0750a02911db3023ec0d41a4e9e6b6980c3d3b69a7de2560dc425e0e231(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eef0f714d40e10392b8ec2c52efdc27fcb8609dd0fcf32d017a82f011180812(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57a3640340dc0e27f15e81e99888b467cacda9ebfff9aa418a037fedc8c65abe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dea281279e09fe2982156be93f7c71cff4fa12878908c054a47d388f291d20ba(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3409f1203f694aad59a1d613e8a17959d06f4726ce0d2dd00b74291cc31aea33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c82a925c9af934f3753b602fd39633c83f60adb0a7491fbb48415780141c110(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1111d257063a23b7f81f141b6ba5493efaaa5555124f21cdd52a18e3443d4033(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67a88e561982d46bd031764ac75ef48d5f97274b716603e47a9d50e57c90b2a0(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    message_base64: builtins.str,
    start_time: builtins.str,
    title: builtins.str,
    authenticated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    end_time: typing.Optional[builtins.str] = None,
    link: typing.Optional[typing.Union[ConfigUiCustomMessageLink, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1fe0311d1fb6b6eb6ea51d2910c171351277b32b256acc8d52693a59e80578(
    *,
    href: builtins.str,
    title: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__901ccd87dbf6b4b9ef70daf6cc23b78c0557be1e8c49623e64f9f5750f0e7db6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee8ac0b73b58edd7a4226d6387c0375460193b9e3ce3ee809987c9c1c4f5763e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2407a64b72f9e80b624a56d87116f2f8b3aad26e92e0b80a6ea4700563a7132f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0368c86ea2009c12888b047b499d63296456f85deafcc238d229d7666542ddfc(
    value: typing.Optional[ConfigUiCustomMessageLink],
) -> None:
    """Type checking stubs"""
    pass
