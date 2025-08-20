r'''
# `vault_kmip_secret_role`

Refer to the Terraform Registry for docs: [`vault_kmip_secret_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role).
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


class KmipSecretRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.kmipSecretRole.KmipSecretRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role vault_kmip_secret_role}.'''

    def __init__(
        self,
        scope_: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        path: builtins.str,
        role: builtins.str,
        scope: builtins.str,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        operation_activate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_add_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_create: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_discover_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_get: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_get_attribute_list: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_get_attributes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_locate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_none: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_register: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_rekey: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_client_key_bits: typing.Optional[jsii.Number] = None,
        tls_client_key_type: typing.Optional[builtins.str] = None,
        tls_client_ttl: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role vault_kmip_secret_role} Resource.

        :param scope_: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param path: Path where KMIP backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#path KmipSecretRole#path}
        :param role: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#role KmipSecretRole#role}
        :param scope: Name of the scope. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#scope KmipSecretRole#scope}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#id KmipSecretRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#namespace KmipSecretRole#namespace}
        :param operation_activate: Grant permission to use the KMIP Activate operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_activate KmipSecretRole#operation_activate}
        :param operation_add_attribute: Grant permission to use the KMIP Add Attribute operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_add_attribute KmipSecretRole#operation_add_attribute}
        :param operation_all: Grant all permissions to this role. May not be specified with any other operation_* params. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_all KmipSecretRole#operation_all}
        :param operation_create: Grant permission to use the KMIP Create operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_create KmipSecretRole#operation_create}
        :param operation_destroy: Grant permission to use the KMIP Destroy operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_destroy KmipSecretRole#operation_destroy}
        :param operation_discover_versions: Grant permission to use the KMIP Discover Version operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_discover_versions KmipSecretRole#operation_discover_versions}
        :param operation_get: Grant permission to use the KMIP Get operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get KmipSecretRole#operation_get}
        :param operation_get_attribute_list: Grant permission to use the KMIP Get Attribute List operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get_attribute_list KmipSecretRole#operation_get_attribute_list}
        :param operation_get_attributes: Grant permission to use the KMIP Get Attributes operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get_attributes KmipSecretRole#operation_get_attributes}
        :param operation_locate: Grant permission to use the KMIP Locate operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_locate KmipSecretRole#operation_locate}
        :param operation_none: Remove all permissions from this role. May not be specified with any other operation_* params. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_none KmipSecretRole#operation_none}
        :param operation_register: Grant permission to use the KMIP Register operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_register KmipSecretRole#operation_register}
        :param operation_rekey: Grant permission to use the KMIP Rekey operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_rekey KmipSecretRole#operation_rekey}
        :param operation_revoke: Grant permission to use the KMIP Revoke operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_revoke KmipSecretRole#operation_revoke}
        :param tls_client_key_bits: Client certificate key bits, valid values depend on key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_key_bits KmipSecretRole#tls_client_key_bits}
        :param tls_client_key_type: Client certificate key type, rsa or ec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_key_type KmipSecretRole#tls_client_key_type}
        :param tls_client_ttl: Client certificate TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_ttl KmipSecretRole#tls_client_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__961a56dcf683d2a5c0f431afcde60991c4794a967d05b04125e336709e2359d6)
            check_type(argname="argument scope_", value=scope_, expected_type=type_hints["scope_"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = KmipSecretRoleConfig(
            path=path,
            role=role,
            scope=scope,
            id=id,
            namespace=namespace,
            operation_activate=operation_activate,
            operation_add_attribute=operation_add_attribute,
            operation_all=operation_all,
            operation_create=operation_create,
            operation_destroy=operation_destroy,
            operation_discover_versions=operation_discover_versions,
            operation_get=operation_get,
            operation_get_attribute_list=operation_get_attribute_list,
            operation_get_attributes=operation_get_attributes,
            operation_locate=operation_locate,
            operation_none=operation_none,
            operation_register=operation_register,
            operation_rekey=operation_rekey,
            operation_revoke=operation_revoke,
            tls_client_key_bits=tls_client_key_bits,
            tls_client_key_type=tls_client_key_type,
            tls_client_ttl=tls_client_ttl,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope_, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a KmipSecretRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KmipSecretRole to import.
        :param import_from_id: The id of the existing KmipSecretRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KmipSecretRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb3cb2bc44521cd2d1d2d335ba0a055278dc8c32d46cc24245751c5b6d2b34e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOperationActivate")
    def reset_operation_activate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationActivate", []))

    @jsii.member(jsii_name="resetOperationAddAttribute")
    def reset_operation_add_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationAddAttribute", []))

    @jsii.member(jsii_name="resetOperationAll")
    def reset_operation_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationAll", []))

    @jsii.member(jsii_name="resetOperationCreate")
    def reset_operation_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationCreate", []))

    @jsii.member(jsii_name="resetOperationDestroy")
    def reset_operation_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationDestroy", []))

    @jsii.member(jsii_name="resetOperationDiscoverVersions")
    def reset_operation_discover_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationDiscoverVersions", []))

    @jsii.member(jsii_name="resetOperationGet")
    def reset_operation_get(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationGet", []))

    @jsii.member(jsii_name="resetOperationGetAttributeList")
    def reset_operation_get_attribute_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationGetAttributeList", []))

    @jsii.member(jsii_name="resetOperationGetAttributes")
    def reset_operation_get_attributes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationGetAttributes", []))

    @jsii.member(jsii_name="resetOperationLocate")
    def reset_operation_locate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationLocate", []))

    @jsii.member(jsii_name="resetOperationNone")
    def reset_operation_none(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationNone", []))

    @jsii.member(jsii_name="resetOperationRegister")
    def reset_operation_register(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationRegister", []))

    @jsii.member(jsii_name="resetOperationRekey")
    def reset_operation_rekey(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationRekey", []))

    @jsii.member(jsii_name="resetOperationRevoke")
    def reset_operation_revoke(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperationRevoke", []))

    @jsii.member(jsii_name="resetTlsClientKeyBits")
    def reset_tls_client_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsClientKeyBits", []))

    @jsii.member(jsii_name="resetTlsClientKeyType")
    def reset_tls_client_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsClientKeyType", []))

    @jsii.member(jsii_name="resetTlsClientTtl")
    def reset_tls_client_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsClientTtl", []))

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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="operationActivateInput")
    def operation_activate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationActivateInput"))

    @builtins.property
    @jsii.member(jsii_name="operationAddAttributeInput")
    def operation_add_attribute_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationAddAttributeInput"))

    @builtins.property
    @jsii.member(jsii_name="operationAllInput")
    def operation_all_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationAllInput"))

    @builtins.property
    @jsii.member(jsii_name="operationCreateInput")
    def operation_create_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationCreateInput"))

    @builtins.property
    @jsii.member(jsii_name="operationDestroyInput")
    def operation_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="operationDiscoverVersionsInput")
    def operation_discover_versions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationDiscoverVersionsInput"))

    @builtins.property
    @jsii.member(jsii_name="operationGetAttributeListInput")
    def operation_get_attribute_list_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationGetAttributeListInput"))

    @builtins.property
    @jsii.member(jsii_name="operationGetAttributesInput")
    def operation_get_attributes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationGetAttributesInput"))

    @builtins.property
    @jsii.member(jsii_name="operationGetInput")
    def operation_get_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationGetInput"))

    @builtins.property
    @jsii.member(jsii_name="operationLocateInput")
    def operation_locate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationLocateInput"))

    @builtins.property
    @jsii.member(jsii_name="operationNoneInput")
    def operation_none_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationNoneInput"))

    @builtins.property
    @jsii.member(jsii_name="operationRegisterInput")
    def operation_register_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationRegisterInput"))

    @builtins.property
    @jsii.member(jsii_name="operationRekeyInput")
    def operation_rekey_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationRekeyInput"))

    @builtins.property
    @jsii.member(jsii_name="operationRevokeInput")
    def operation_revoke_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "operationRevokeInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsClientKeyBitsInput")
    def tls_client_key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tlsClientKeyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsClientKeyTypeInput")
    def tls_client_key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsClientKeyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsClientTtlInput")
    def tls_client_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tlsClientTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4123f93722a96ed76209efbcb5ebccc141f5e199a0cc766bed09ac11eab10daa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f63bf1c944aafd15e304619ac2f876924a1bc0e5155defdb2c0e9ff948f4d490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationActivate")
    def operation_activate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationActivate"))

    @operation_activate.setter
    def operation_activate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e232b7143ccb2433629abeff21ad5044bfad7c8c3b4ad11fdd02f57ce7a3dfe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationActivate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationAddAttribute")
    def operation_add_attribute(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationAddAttribute"))

    @operation_add_attribute.setter
    def operation_add_attribute(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c28a11bd5422cc08a3dddcfc758228cb76b8fc1f80293a9d31d60547ce0770bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationAddAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationAll")
    def operation_all(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationAll"))

    @operation_all.setter
    def operation_all(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89dfcdcdcecbeb2000adfc9277806aa4845c74b24ad6d686d357869e6ea0ea10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationAll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationCreate")
    def operation_create(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationCreate"))

    @operation_create.setter
    def operation_create(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__211fdc3f1d717192aa269fb7d9544b738a31092c8e38c2685adc6e46075160a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationCreate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationDestroy")
    def operation_destroy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationDestroy"))

    @operation_destroy.setter
    def operation_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdedb1b17585dc88e5636c706630ad1618104c9e12b0b05f6f56cf4e8dd2448c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationDiscoverVersions")
    def operation_discover_versions(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationDiscoverVersions"))

    @operation_discover_versions.setter
    def operation_discover_versions(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__706d533831a6009149679d787fa835d51cc870e3bbcce4166f6211e45158d739)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationDiscoverVersions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationGet")
    def operation_get(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationGet"))

    @operation_get.setter
    def operation_get(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96fda92216f1064a63170dbca41e3fb3a8f6069b888b38f2c0f23cac422fcba3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationGet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationGetAttributeList")
    def operation_get_attribute_list(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationGetAttributeList"))

    @operation_get_attribute_list.setter
    def operation_get_attribute_list(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed39158158876138cab4e12b1de20891a16f0b4eab8e5f54bc469eb79b7c1d0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationGetAttributeList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationGetAttributes")
    def operation_get_attributes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationGetAttributes"))

    @operation_get_attributes.setter
    def operation_get_attributes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a873cda72f3d71485599092a543db81d7f197702338a50a19598106e2805b49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationGetAttributes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationLocate")
    def operation_locate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationLocate"))

    @operation_locate.setter
    def operation_locate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8f2fd815193c8e07f2f914c575a77f6ec947fade879cf7cac983fd2e3c3a3a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationLocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationNone")
    def operation_none(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationNone"))

    @operation_none.setter
    def operation_none(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ea87a9ca4df97462be39286672f655cbea638fe0b3658a6b4cc57f62408b040)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationNone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationRegister")
    def operation_register(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationRegister"))

    @operation_register.setter
    def operation_register(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f350501ea8966a01b83b30efcc33cbf455b314b7e751d8a8f756c240d365f20e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationRegister", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationRekey")
    def operation_rekey(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationRekey"))

    @operation_rekey.setter
    def operation_rekey(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc239ce9bc5356917f1dd5eb4da8a76f38ba96638ff8ac23c13f68d97625998b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationRekey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operationRevoke")
    def operation_revoke(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "operationRevoke"))

    @operation_revoke.setter
    def operation_revoke(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4039dd4d20c2843941a5f9d4353c2a460366bf19bdf10ad8e5e84c079c77e243)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operationRevoke", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41cec25a8a38b26a81aee1b82d367e57110df535085b4104b99871638a371314)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__742609fe04e43ee402d9df22b916de88ddcaa1f1df17307746428584713ad9e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__809362ac6e034d575165914c8d10f5b50828cb172614ea4871b65aa0a177794c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsClientKeyBits")
    def tls_client_key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tlsClientKeyBits"))

    @tls_client_key_bits.setter
    def tls_client_key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66f93a06b67032c139c9f1230f78142efc2e09b5ad104f598d610c9990405a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsClientKeyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsClientKeyType")
    def tls_client_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsClientKeyType"))

    @tls_client_key_type.setter
    def tls_client_key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b9c57b7748597ffddeb2f7a645ba72a612e8a94d9b4bf0c265b5d82546de3e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsClientKeyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsClientTtl")
    def tls_client_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tlsClientTtl"))

    @tls_client_ttl.setter
    def tls_client_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c673f88e05fa21bbd34f6f0132c5fcec3f4ddb354b20113ab22f14ec878e9b35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsClientTtl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.kmipSecretRole.KmipSecretRoleConfig",
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
        "role": "role",
        "scope": "scope",
        "id": "id",
        "namespace": "namespace",
        "operation_activate": "operationActivate",
        "operation_add_attribute": "operationAddAttribute",
        "operation_all": "operationAll",
        "operation_create": "operationCreate",
        "operation_destroy": "operationDestroy",
        "operation_discover_versions": "operationDiscoverVersions",
        "operation_get": "operationGet",
        "operation_get_attribute_list": "operationGetAttributeList",
        "operation_get_attributes": "operationGetAttributes",
        "operation_locate": "operationLocate",
        "operation_none": "operationNone",
        "operation_register": "operationRegister",
        "operation_rekey": "operationRekey",
        "operation_revoke": "operationRevoke",
        "tls_client_key_bits": "tlsClientKeyBits",
        "tls_client_key_type": "tlsClientKeyType",
        "tls_client_ttl": "tlsClientTtl",
    },
)
class KmipSecretRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        role: builtins.str,
        scope: builtins.str,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        operation_activate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_add_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_create: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_discover_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_get: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_get_attribute_list: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_get_attributes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_locate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_none: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_register: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_rekey: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        operation_revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_client_key_bits: typing.Optional[jsii.Number] = None,
        tls_client_key_type: typing.Optional[builtins.str] = None,
        tls_client_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param path: Path where KMIP backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#path KmipSecretRole#path}
        :param role: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#role KmipSecretRole#role}
        :param scope: Name of the scope. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#scope KmipSecretRole#scope}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#id KmipSecretRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#namespace KmipSecretRole#namespace}
        :param operation_activate: Grant permission to use the KMIP Activate operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_activate KmipSecretRole#operation_activate}
        :param operation_add_attribute: Grant permission to use the KMIP Add Attribute operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_add_attribute KmipSecretRole#operation_add_attribute}
        :param operation_all: Grant all permissions to this role. May not be specified with any other operation_* params. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_all KmipSecretRole#operation_all}
        :param operation_create: Grant permission to use the KMIP Create operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_create KmipSecretRole#operation_create}
        :param operation_destroy: Grant permission to use the KMIP Destroy operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_destroy KmipSecretRole#operation_destroy}
        :param operation_discover_versions: Grant permission to use the KMIP Discover Version operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_discover_versions KmipSecretRole#operation_discover_versions}
        :param operation_get: Grant permission to use the KMIP Get operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get KmipSecretRole#operation_get}
        :param operation_get_attribute_list: Grant permission to use the KMIP Get Attribute List operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get_attribute_list KmipSecretRole#operation_get_attribute_list}
        :param operation_get_attributes: Grant permission to use the KMIP Get Attributes operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get_attributes KmipSecretRole#operation_get_attributes}
        :param operation_locate: Grant permission to use the KMIP Locate operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_locate KmipSecretRole#operation_locate}
        :param operation_none: Remove all permissions from this role. May not be specified with any other operation_* params. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_none KmipSecretRole#operation_none}
        :param operation_register: Grant permission to use the KMIP Register operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_register KmipSecretRole#operation_register}
        :param operation_rekey: Grant permission to use the KMIP Rekey operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_rekey KmipSecretRole#operation_rekey}
        :param operation_revoke: Grant permission to use the KMIP Revoke operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_revoke KmipSecretRole#operation_revoke}
        :param tls_client_key_bits: Client certificate key bits, valid values depend on key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_key_bits KmipSecretRole#tls_client_key_bits}
        :param tls_client_key_type: Client certificate key type, rsa or ec. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_key_type KmipSecretRole#tls_client_key_type}
        :param tls_client_ttl: Client certificate TTL in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_ttl KmipSecretRole#tls_client_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dfa721ab0364e828d56ca9c55155bd145ab3679f6a439a10f2bad1f2b56b265)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument operation_activate", value=operation_activate, expected_type=type_hints["operation_activate"])
            check_type(argname="argument operation_add_attribute", value=operation_add_attribute, expected_type=type_hints["operation_add_attribute"])
            check_type(argname="argument operation_all", value=operation_all, expected_type=type_hints["operation_all"])
            check_type(argname="argument operation_create", value=operation_create, expected_type=type_hints["operation_create"])
            check_type(argname="argument operation_destroy", value=operation_destroy, expected_type=type_hints["operation_destroy"])
            check_type(argname="argument operation_discover_versions", value=operation_discover_versions, expected_type=type_hints["operation_discover_versions"])
            check_type(argname="argument operation_get", value=operation_get, expected_type=type_hints["operation_get"])
            check_type(argname="argument operation_get_attribute_list", value=operation_get_attribute_list, expected_type=type_hints["operation_get_attribute_list"])
            check_type(argname="argument operation_get_attributes", value=operation_get_attributes, expected_type=type_hints["operation_get_attributes"])
            check_type(argname="argument operation_locate", value=operation_locate, expected_type=type_hints["operation_locate"])
            check_type(argname="argument operation_none", value=operation_none, expected_type=type_hints["operation_none"])
            check_type(argname="argument operation_register", value=operation_register, expected_type=type_hints["operation_register"])
            check_type(argname="argument operation_rekey", value=operation_rekey, expected_type=type_hints["operation_rekey"])
            check_type(argname="argument operation_revoke", value=operation_revoke, expected_type=type_hints["operation_revoke"])
            check_type(argname="argument tls_client_key_bits", value=tls_client_key_bits, expected_type=type_hints["tls_client_key_bits"])
            check_type(argname="argument tls_client_key_type", value=tls_client_key_type, expected_type=type_hints["tls_client_key_type"])
            check_type(argname="argument tls_client_ttl", value=tls_client_ttl, expected_type=type_hints["tls_client_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
            "role": role,
            "scope": scope,
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
        if operation_activate is not None:
            self._values["operation_activate"] = operation_activate
        if operation_add_attribute is not None:
            self._values["operation_add_attribute"] = operation_add_attribute
        if operation_all is not None:
            self._values["operation_all"] = operation_all
        if operation_create is not None:
            self._values["operation_create"] = operation_create
        if operation_destroy is not None:
            self._values["operation_destroy"] = operation_destroy
        if operation_discover_versions is not None:
            self._values["operation_discover_versions"] = operation_discover_versions
        if operation_get is not None:
            self._values["operation_get"] = operation_get
        if operation_get_attribute_list is not None:
            self._values["operation_get_attribute_list"] = operation_get_attribute_list
        if operation_get_attributes is not None:
            self._values["operation_get_attributes"] = operation_get_attributes
        if operation_locate is not None:
            self._values["operation_locate"] = operation_locate
        if operation_none is not None:
            self._values["operation_none"] = operation_none
        if operation_register is not None:
            self._values["operation_register"] = operation_register
        if operation_rekey is not None:
            self._values["operation_rekey"] = operation_rekey
        if operation_revoke is not None:
            self._values["operation_revoke"] = operation_revoke
        if tls_client_key_bits is not None:
            self._values["tls_client_key_bits"] = tls_client_key_bits
        if tls_client_key_type is not None:
            self._values["tls_client_key_type"] = tls_client_key_type
        if tls_client_ttl is not None:
            self._values["tls_client_ttl"] = tls_client_ttl

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
        '''Path where KMIP backend is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#path KmipSecretRole#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#role KmipSecretRole#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scope(self) -> builtins.str:
        '''Name of the scope.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#scope KmipSecretRole#scope}
        '''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#id KmipSecretRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#namespace KmipSecretRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operation_activate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Activate operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_activate KmipSecretRole#operation_activate}
        '''
        result = self._values.get("operation_activate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_add_attribute(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Add Attribute operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_add_attribute KmipSecretRole#operation_add_attribute}
        '''
        result = self._values.get("operation_add_attribute")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_all(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant all permissions to this role. May not be specified with any other operation_* params.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_all KmipSecretRole#operation_all}
        '''
        result = self._values.get("operation_all")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_create(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Create operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_create KmipSecretRole#operation_create}
        '''
        result = self._values.get("operation_create")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Destroy operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_destroy KmipSecretRole#operation_destroy}
        '''
        result = self._values.get("operation_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_discover_versions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Discover Version operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_discover_versions KmipSecretRole#operation_discover_versions}
        '''
        result = self._values.get("operation_discover_versions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_get(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Get operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get KmipSecretRole#operation_get}
        '''
        result = self._values.get("operation_get")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_get_attribute_list(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Get Attribute List operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get_attribute_list KmipSecretRole#operation_get_attribute_list}
        '''
        result = self._values.get("operation_get_attribute_list")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_get_attributes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Get Attributes operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_get_attributes KmipSecretRole#operation_get_attributes}
        '''
        result = self._values.get("operation_get_attributes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_locate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Locate operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_locate KmipSecretRole#operation_locate}
        '''
        result = self._values.get("operation_locate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_none(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Remove all permissions from this role. May not be specified with any other operation_* params.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_none KmipSecretRole#operation_none}
        '''
        result = self._values.get("operation_none")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_register(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Register operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_register KmipSecretRole#operation_register}
        '''
        result = self._values.get("operation_register")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_rekey(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Rekey operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_rekey KmipSecretRole#operation_rekey}
        '''
        result = self._values.get("operation_rekey")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def operation_revoke(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Grant permission to use the KMIP Revoke operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#operation_revoke KmipSecretRole#operation_revoke}
        '''
        result = self._values.get("operation_revoke")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_client_key_bits(self) -> typing.Optional[jsii.Number]:
        '''Client certificate key bits, valid values depend on key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_key_bits KmipSecretRole#tls_client_key_bits}
        '''
        result = self._values.get("tls_client_key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_client_key_type(self) -> typing.Optional[builtins.str]:
        '''Client certificate key type, rsa or ec.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_key_type KmipSecretRole#tls_client_key_type}
        '''
        result = self._values.get("tls_client_key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_client_ttl(self) -> typing.Optional[jsii.Number]:
        '''Client certificate TTL in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kmip_secret_role#tls_client_ttl KmipSecretRole#tls_client_ttl}
        '''
        result = self._values.get("tls_client_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KmipSecretRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KmipSecretRole",
    "KmipSecretRoleConfig",
]

publication.publish()

def _typecheckingstub__961a56dcf683d2a5c0f431afcde60991c4794a967d05b04125e336709e2359d6(
    scope_: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    path: builtins.str,
    role: builtins.str,
    scope: builtins.str,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    operation_activate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_add_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_create: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_discover_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_get: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_get_attribute_list: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_get_attributes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_locate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_none: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_register: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_rekey: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_client_key_bits: typing.Optional[jsii.Number] = None,
    tls_client_key_type: typing.Optional[builtins.str] = None,
    tls_client_ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__cb3cb2bc44521cd2d1d2d335ba0a055278dc8c32d46cc24245751c5b6d2b34e8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4123f93722a96ed76209efbcb5ebccc141f5e199a0cc766bed09ac11eab10daa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f63bf1c944aafd15e304619ac2f876924a1bc0e5155defdb2c0e9ff948f4d490(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e232b7143ccb2433629abeff21ad5044bfad7c8c3b4ad11fdd02f57ce7a3dfe1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28a11bd5422cc08a3dddcfc758228cb76b8fc1f80293a9d31d60547ce0770bc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89dfcdcdcecbeb2000adfc9277806aa4845c74b24ad6d686d357869e6ea0ea10(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__211fdc3f1d717192aa269fb7d9544b738a31092c8e38c2685adc6e46075160a5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdedb1b17585dc88e5636c706630ad1618104c9e12b0b05f6f56cf4e8dd2448c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__706d533831a6009149679d787fa835d51cc870e3bbcce4166f6211e45158d739(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96fda92216f1064a63170dbca41e3fb3a8f6069b888b38f2c0f23cac422fcba3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed39158158876138cab4e12b1de20891a16f0b4eab8e5f54bc469eb79b7c1d0e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a873cda72f3d71485599092a543db81d7f197702338a50a19598106e2805b49(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8f2fd815193c8e07f2f914c575a77f6ec947fade879cf7cac983fd2e3c3a3a7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ea87a9ca4df97462be39286672f655cbea638fe0b3658a6b4cc57f62408b040(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f350501ea8966a01b83b30efcc33cbf455b314b7e751d8a8f756c240d365f20e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc239ce9bc5356917f1dd5eb4da8a76f38ba96638ff8ac23c13f68d97625998b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4039dd4d20c2843941a5f9d4353c2a460366bf19bdf10ad8e5e84c079c77e243(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41cec25a8a38b26a81aee1b82d367e57110df535085b4104b99871638a371314(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__742609fe04e43ee402d9df22b916de88ddcaa1f1df17307746428584713ad9e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__809362ac6e034d575165914c8d10f5b50828cb172614ea4871b65aa0a177794c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66f93a06b67032c139c9f1230f78142efc2e09b5ad104f598d610c9990405a0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b9c57b7748597ffddeb2f7a645ba72a612e8a94d9b4bf0c265b5d82546de3e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c673f88e05fa21bbd34f6f0132c5fcec3f4ddb354b20113ab22f14ec878e9b35(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dfa721ab0364e828d56ca9c55155bd145ab3679f6a439a10f2bad1f2b56b265(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    path: builtins.str,
    role: builtins.str,
    scope: builtins.str,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    operation_activate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_add_attribute: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_all: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_create: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_discover_versions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_get: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_get_attribute_list: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_get_attributes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_locate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_none: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_register: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_rekey: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    operation_revoke: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_client_key_bits: typing.Optional[jsii.Number] = None,
    tls_client_key_type: typing.Optional[builtins.str] = None,
    tls_client_ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
