r'''
# `vault_azure_secret_backend_role`

Refer to the Terraform Registry for docs: [`vault_azure_secret_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role).
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


class AzureSecretBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role vault_azure_secret_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        role: builtins.str,
        application_object_id: typing.Optional[builtins.str] = None,
        azure_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AzureSecretBackendRoleAzureGroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_roles: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AzureSecretBackendRoleAzureRoles", typing.Dict[builtins.str, typing.Any]]]]] = None,
        backend: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        explicit_max_ttl: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        permanently_delete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sign_in_audience: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role vault_azure_secret_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role: Name of the role to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role AzureSecretBackendRole#role}
        :param application_object_id: Application Object ID for an existing service principal that will be used instead of creating dynamic service principals. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#application_object_id AzureSecretBackendRole#application_object_id}
        :param azure_groups: azure_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#azure_groups AzureSecretBackendRole#azure_groups}
        :param azure_roles: azure_roles block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#azure_roles AzureSecretBackendRole#azure_roles}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#backend AzureSecretBackendRole#backend}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#description AzureSecretBackendRole#description}
        :param explicit_max_ttl: Specifies the explicit maximum lifetime of the lease and service principal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#explicit_max_ttl AzureSecretBackendRole#explicit_max_ttl}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#id AzureSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_ttl: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#max_ttl AzureSecretBackendRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#namespace AzureSecretBackendRole#namespace}
        :param permanently_delete: Indicates whether the applications and service principals created by Vault will be permanently deleted when the corresponding leases expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#permanently_delete AzureSecretBackendRole#permanently_delete}
        :param sign_in_audience: Specifies the security principal types that are allowed to sign in to the application. Valid values are: AzureADMyOrg, AzureADMultipleOrgs, AzureADandPersonalMicrosoftAccount, PersonalMicrosoftAccount Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#sign_in_audience AzureSecretBackendRole#sign_in_audience}
        :param tags: Comma-separated strings of Azure tags to attach to an application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#tags AzureSecretBackendRole#tags}
        :param ttl: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#ttl AzureSecretBackendRole#ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49b44d1579c486ccc959c25c13051ccbc7a678f6f01d8d8a9957b30f719b42b0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AzureSecretBackendRoleConfig(
            role=role,
            application_object_id=application_object_id,
            azure_groups=azure_groups,
            azure_roles=azure_roles,
            backend=backend,
            description=description,
            explicit_max_ttl=explicit_max_ttl,
            id=id,
            max_ttl=max_ttl,
            namespace=namespace,
            permanently_delete=permanently_delete,
            sign_in_audience=sign_in_audience,
            tags=tags,
            ttl=ttl,
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
        '''Generates CDKTF code for importing a AzureSecretBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AzureSecretBackendRole to import.
        :param import_from_id: The id of the existing AzureSecretBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AzureSecretBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e49adad89a424818101bf2f81c49af0d2a3da25e2ffbd68ccaec6146f923c8df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAzureGroups")
    def put_azure_groups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AzureSecretBackendRoleAzureGroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7712bb0770ec21e0203520ed2573650b3bdf6fb97abc5223dc26c241be16aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzureGroups", [value]))

    @jsii.member(jsii_name="putAzureRoles")
    def put_azure_roles(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AzureSecretBackendRoleAzureRoles", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9acccdb5fd75157ab6b5b74208cb6bd40d1639b3da99c3a1b21e4aaffb04513)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzureRoles", [value]))

    @jsii.member(jsii_name="resetApplicationObjectId")
    def reset_application_object_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApplicationObjectId", []))

    @jsii.member(jsii_name="resetAzureGroups")
    def reset_azure_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureGroups", []))

    @jsii.member(jsii_name="resetAzureRoles")
    def reset_azure_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureRoles", []))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExplicitMaxTtl")
    def reset_explicit_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExplicitMaxTtl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPermanentlyDelete")
    def reset_permanently_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPermanentlyDelete", []))

    @jsii.member(jsii_name="resetSignInAudience")
    def reset_sign_in_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignInAudience", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="azureGroups")
    def azure_groups(self) -> "AzureSecretBackendRoleAzureGroupsList":
        return typing.cast("AzureSecretBackendRoleAzureGroupsList", jsii.get(self, "azureGroups"))

    @builtins.property
    @jsii.member(jsii_name="azureRoles")
    def azure_roles(self) -> "AzureSecretBackendRoleAzureRolesList":
        return typing.cast("AzureSecretBackendRoleAzureRolesList", jsii.get(self, "azureRoles"))

    @builtins.property
    @jsii.member(jsii_name="applicationObjectIdInput")
    def application_object_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationObjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureGroupsInput")
    def azure_groups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AzureSecretBackendRoleAzureGroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AzureSecretBackendRoleAzureGroups"]]], jsii.get(self, "azureGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="azureRolesInput")
    def azure_roles_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AzureSecretBackendRoleAzureRoles"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AzureSecretBackendRoleAzureRoles"]]], jsii.get(self, "azureRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="explicitMaxTtlInput")
    def explicit_max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "explicitMaxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="permanentlyDeleteInput")
    def permanently_delete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "permanentlyDeleteInput"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="signInAudienceInput")
    def sign_in_audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signInAudienceInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="applicationObjectId")
    def application_object_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "applicationObjectId"))

    @application_object_id.setter
    def application_object_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01ac67f9ce5550d7a6cd5c5117ada3f1e79b32d529f44fb89666a0a46e853155)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "applicationObjectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a12ac548a1a6a817e1e5ae855f8fdcedc8bf6e6341f113deb771c05dc364251)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da4730ee942bd47ba9bd17084d9e34ed1cd0516ce8afe1ea7c9bc03a95273366)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="explicitMaxTtl")
    def explicit_max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "explicitMaxTtl"))

    @explicit_max_ttl.setter
    def explicit_max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0b2bbe49cf8c58508c76c717c49593ad4a823affa7828cfef025aab7441cef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "explicitMaxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce31910f8c6968bdccd8f48f2b9b86b4301013c12dea8dec24802a8da39ad622)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5c25219abfc2af01377a4f9226f9961c289f6c1707f28dcc51bc8da6e6ca980)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__730b36f1b3e63f1620c72c4b12aa13839797902b160213e5a117fb7bf88743b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="permanentlyDelete")
    def permanently_delete(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "permanentlyDelete"))

    @permanently_delete.setter
    def permanently_delete(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a7577688ab11a8b4a4b38c21cba3c41695b051bf1a157dc43e90d6a589e8a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "permanentlyDelete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b372ab6ec939970ec79da28ba3423752f93de99258272ca7eb440bd077ebb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signInAudience")
    def sign_in_audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signInAudience"))

    @sign_in_audience.setter
    def sign_in_audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b9e246b2f92ebffab0d6ef1ebef41e47de9af2081b803a5a218c0598fdda5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signInAudience", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea06cc059727d8edd91c1d169613d518283f5506fa0248c2122d7a02b7386de4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a916095def10bb79dbd21b791d077abec7fffde65e6430e2f1d9705967169c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleAzureGroups",
    jsii_struct_bases=[],
    name_mapping={"group_name": "groupName"},
)
class AzureSecretBackendRoleAzureGroups:
    def __init__(self, *, group_name: builtins.str) -> None:
        '''
        :param group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#group_name AzureSecretBackendRole#group_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a05e3040df4e681b0aa0cd90f263a34f4e75257434746ce17f00ee3700b099c)
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "group_name": group_name,
        }

    @builtins.property
    def group_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#group_name AzureSecretBackendRole#group_name}.'''
        result = self._values.get("group_name")
        assert result is not None, "Required property 'group_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AzureSecretBackendRoleAzureGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AzureSecretBackendRoleAzureGroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleAzureGroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5c5e1599213b0a7227e9bd1101ceeb5b58eca70a93e3c7cc5d2eb35a7b65ee9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AzureSecretBackendRoleAzureGroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1f1add65dec558a8b54b18020ba5c1c0804c20dc7e8a208baa0c5f53622e5e6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AzureSecretBackendRoleAzureGroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9db37475565778ee51facf9d4098dd90cda40a53027aab29547172ccc6cfdf2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df010ecaa36c1f01087f59ec97a200d052be85cb41487bc81dd602f81cf58d87)
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
            type_hints = typing.get_type_hints(_typecheckingstub__92a0bf94eca47e1919f76008b563c389bb8326f7b8e7ea98b43d91a92d60d6f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureGroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureGroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureGroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b312800cc2fde4cf1654f1085d4bd154cc41a93e8fcca6c80bc6cded1bd9dd6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AzureSecretBackendRoleAzureGroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleAzureGroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__88f1fc4461d10eb217fd3dda3c09045a0c44a490226d7bb8935954d3cc74291a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="objectId")
    def object_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "objectId"))

    @builtins.property
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44c803b08b4e6bf551049627f6b4a741a9caaaae8cca735274c0c2cb94a49ded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureGroups]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureGroups]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureGroups]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__735239ab519d96911071aead7b75362d1ba82434f21936f509284dbf5bd66916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleAzureRoles",
    jsii_struct_bases=[],
    name_mapping={"scope": "scope", "role_id": "roleId", "role_name": "roleName"},
)
class AzureSecretBackendRoleAzureRoles:
    def __init__(
        self,
        *,
        scope: builtins.str,
        role_id: typing.Optional[builtins.str] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#scope AzureSecretBackendRole#scope}.
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role_id AzureSecretBackendRole#role_id}.
        :param role_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role_name AzureSecretBackendRole#role_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__458586c17aa75d8597cd14acce557fa964a0ba0ce7e76aa1bc2e7f57b794d4b0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument role_id", value=role_id, expected_type=type_hints["role_id"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "scope": scope,
        }
        if role_id is not None:
            self._values["role_id"] = role_id
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def scope(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#scope AzureSecretBackendRole#scope}.'''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role_id AzureSecretBackendRole#role_id}.'''
        result = self._values.get("role_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role_name AzureSecretBackendRole#role_name}.'''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AzureSecretBackendRoleAzureRoles(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AzureSecretBackendRoleAzureRolesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleAzureRolesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b347d4b9c2441bee4d6b772f02126bb45fd59fd456d2b3aa287e1fa9b765ab1d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AzureSecretBackendRoleAzureRolesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e66c89598269f9121932074a7a418c9b507e18fa1f860a669a7572866eece20f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AzureSecretBackendRoleAzureRolesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1780b6625a00af1a400fc6526ede38f7eda75790cdbf0857c622bd054c6be1e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__427b053c1e8fd6e6ce38d8357babf32ca7c6e3d2fd582f3f6b4280a3c22d1556)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d78b4bc697509f1e73038c8329b35f2691c72847bffc548963a4d4607a0a5b24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureRoles]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureRoles]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureRoles]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd29a1ff123cbd70655d68b9ffcf4bddba7bece9b22fb6583177bdd797fee93c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AzureSecretBackendRoleAzureRolesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleAzureRolesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__edd89e139a223b1ef1d18f595efba2b96ea1a14c75f5f4972911419c98c42be6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetRoleId")
    def reset_role_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleId", []))

    @jsii.member(jsii_name="resetRoleName")
    def reset_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleName", []))

    @builtins.property
    @jsii.member(jsii_name="roleIdInput")
    def role_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="scopeInput")
    def scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scopeInput"))

    @builtins.property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @role_id.setter
    def role_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88b745afeb032874c092594731598d85995a00304676bc55e37a6ef143db5192)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beef246f30058a3d3a2f0ab51442ceb57228d2691e99848c790792803d1c7c0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @scope.setter
    def scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb6e45aad43c21819f4be62d80254e61f5115d9a0830fc70ccebb759e96fcf56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scope", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureRoles]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureRoles]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureRoles]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96927d06dcdc781733babec99f3a002ec324e774ccec9e08ba1ca8a8c309cc38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.azureSecretBackendRole.AzureSecretBackendRoleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "role": "role",
        "application_object_id": "applicationObjectId",
        "azure_groups": "azureGroups",
        "azure_roles": "azureRoles",
        "backend": "backend",
        "description": "description",
        "explicit_max_ttl": "explicitMaxTtl",
        "id": "id",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "permanently_delete": "permanentlyDelete",
        "sign_in_audience": "signInAudience",
        "tags": "tags",
        "ttl": "ttl",
    },
)
class AzureSecretBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        role: builtins.str,
        application_object_id: typing.Optional[builtins.str] = None,
        azure_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_roles: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureRoles, typing.Dict[builtins.str, typing.Any]]]]] = None,
        backend: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        explicit_max_ttl: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        permanently_delete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sign_in_audience: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role: Name of the role to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role AzureSecretBackendRole#role}
        :param application_object_id: Application Object ID for an existing service principal that will be used instead of creating dynamic service principals. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#application_object_id AzureSecretBackendRole#application_object_id}
        :param azure_groups: azure_groups block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#azure_groups AzureSecretBackendRole#azure_groups}
        :param azure_roles: azure_roles block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#azure_roles AzureSecretBackendRole#azure_roles}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#backend AzureSecretBackendRole#backend}
        :param description: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#description AzureSecretBackendRole#description}
        :param explicit_max_ttl: Specifies the explicit maximum lifetime of the lease and service principal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#explicit_max_ttl AzureSecretBackendRole#explicit_max_ttl}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#id AzureSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_ttl: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#max_ttl AzureSecretBackendRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#namespace AzureSecretBackendRole#namespace}
        :param permanently_delete: Indicates whether the applications and service principals created by Vault will be permanently deleted when the corresponding leases expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#permanently_delete AzureSecretBackendRole#permanently_delete}
        :param sign_in_audience: Specifies the security principal types that are allowed to sign in to the application. Valid values are: AzureADMyOrg, AzureADMultipleOrgs, AzureADandPersonalMicrosoftAccount, PersonalMicrosoftAccount Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#sign_in_audience AzureSecretBackendRole#sign_in_audience}
        :param tags: Comma-separated strings of Azure tags to attach to an application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#tags AzureSecretBackendRole#tags}
        :param ttl: Human-friendly description of the mount for the backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#ttl AzureSecretBackendRole#ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c16c8590791c5a181e9f5a01d453e19cbc98c8d3d9f157279bfe078368754499)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument application_object_id", value=application_object_id, expected_type=type_hints["application_object_id"])
            check_type(argname="argument azure_groups", value=azure_groups, expected_type=type_hints["azure_groups"])
            check_type(argname="argument azure_roles", value=azure_roles, expected_type=type_hints["azure_roles"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument explicit_max_ttl", value=explicit_max_ttl, expected_type=type_hints["explicit_max_ttl"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument permanently_delete", value=permanently_delete, expected_type=type_hints["permanently_delete"])
            check_type(argname="argument sign_in_audience", value=sign_in_audience, expected_type=type_hints["sign_in_audience"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
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
        if application_object_id is not None:
            self._values["application_object_id"] = application_object_id
        if azure_groups is not None:
            self._values["azure_groups"] = azure_groups
        if azure_roles is not None:
            self._values["azure_roles"] = azure_roles
        if backend is not None:
            self._values["backend"] = backend
        if description is not None:
            self._values["description"] = description
        if explicit_max_ttl is not None:
            self._values["explicit_max_ttl"] = explicit_max_ttl
        if id is not None:
            self._values["id"] = id
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if permanently_delete is not None:
            self._values["permanently_delete"] = permanently_delete
        if sign_in_audience is not None:
            self._values["sign_in_audience"] = sign_in_audience
        if tags is not None:
            self._values["tags"] = tags
        if ttl is not None:
            self._values["ttl"] = ttl

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
    def role(self) -> builtins.str:
        '''Name of the role to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#role AzureSecretBackendRole#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_object_id(self) -> typing.Optional[builtins.str]:
        '''Application Object ID for an existing service principal that will be used instead of creating dynamic service principals.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#application_object_id AzureSecretBackendRole#application_object_id}
        '''
        result = self._values.get("application_object_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_groups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureGroups]]]:
        '''azure_groups block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#azure_groups AzureSecretBackendRole#azure_groups}
        '''
        result = self._values.get("azure_groups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureGroups]]], result)

    @builtins.property
    def azure_roles(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureRoles]]]:
        '''azure_roles block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#azure_roles AzureSecretBackendRole#azure_roles}
        '''
        result = self._values.get("azure_roles")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureRoles]]], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the auth backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#backend AzureSecretBackendRole#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#description AzureSecretBackendRole#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def explicit_max_ttl(self) -> typing.Optional[builtins.str]:
        '''Specifies the explicit maximum lifetime of the lease and service principal.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#explicit_max_ttl AzureSecretBackendRole#explicit_max_ttl}
        '''
        result = self._values.get("explicit_max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#id AzureSecretBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#max_ttl AzureSecretBackendRole#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#namespace AzureSecretBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permanently_delete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the applications and service principals created by Vault will be permanently deleted when the corresponding leases expire.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#permanently_delete AzureSecretBackendRole#permanently_delete}
        '''
        result = self._values.get("permanently_delete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sign_in_audience(self) -> typing.Optional[builtins.str]:
        '''Specifies the security principal types that are allowed to sign in to the application.

        Valid values are: AzureADMyOrg, AzureADMultipleOrgs, AzureADandPersonalMicrosoftAccount, PersonalMicrosoftAccount

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#sign_in_audience AzureSecretBackendRole#sign_in_audience}
        '''
        result = self._values.get("sign_in_audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Comma-separated strings of Azure tags to attach to an application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#tags AzureSecretBackendRole#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Human-friendly description of the mount for the backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/azure_secret_backend_role#ttl AzureSecretBackendRole#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AzureSecretBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AzureSecretBackendRole",
    "AzureSecretBackendRoleAzureGroups",
    "AzureSecretBackendRoleAzureGroupsList",
    "AzureSecretBackendRoleAzureGroupsOutputReference",
    "AzureSecretBackendRoleAzureRoles",
    "AzureSecretBackendRoleAzureRolesList",
    "AzureSecretBackendRoleAzureRolesOutputReference",
    "AzureSecretBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__49b44d1579c486ccc959c25c13051ccbc7a678f6f01d8d8a9957b30f719b42b0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    role: builtins.str,
    application_object_id: typing.Optional[builtins.str] = None,
    azure_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_roles: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureRoles, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    explicit_max_ttl: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    permanently_delete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sign_in_audience: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e49adad89a424818101bf2f81c49af0d2a3da25e2ffbd68ccaec6146f923c8df(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7712bb0770ec21e0203520ed2573650b3bdf6fb97abc5223dc26c241be16aa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureGroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9acccdb5fd75157ab6b5b74208cb6bd40d1639b3da99c3a1b21e4aaffb04513(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureRoles, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01ac67f9ce5550d7a6cd5c5117ada3f1e79b32d529f44fb89666a0a46e853155(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a12ac548a1a6a817e1e5ae855f8fdcedc8bf6e6341f113deb771c05dc364251(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da4730ee942bd47ba9bd17084d9e34ed1cd0516ce8afe1ea7c9bc03a95273366(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0b2bbe49cf8c58508c76c717c49593ad4a823affa7828cfef025aab7441cef5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce31910f8c6968bdccd8f48f2b9b86b4301013c12dea8dec24802a8da39ad622(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5c25219abfc2af01377a4f9226f9961c289f6c1707f28dcc51bc8da6e6ca980(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__730b36f1b3e63f1620c72c4b12aa13839797902b160213e5a117fb7bf88743b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a7577688ab11a8b4a4b38c21cba3c41695b051bf1a157dc43e90d6a589e8a6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b372ab6ec939970ec79da28ba3423752f93de99258272ca7eb440bd077ebb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b9e246b2f92ebffab0d6ef1ebef41e47de9af2081b803a5a218c0598fdda5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea06cc059727d8edd91c1d169613d518283f5506fa0248c2122d7a02b7386de4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a916095def10bb79dbd21b791d077abec7fffde65e6430e2f1d9705967169c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a05e3040df4e681b0aa0cd90f263a34f4e75257434746ce17f00ee3700b099c(
    *,
    group_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c5e1599213b0a7227e9bd1101ceeb5b58eca70a93e3c7cc5d2eb35a7b65ee9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1f1add65dec558a8b54b18020ba5c1c0804c20dc7e8a208baa0c5f53622e5e6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9db37475565778ee51facf9d4098dd90cda40a53027aab29547172ccc6cfdf2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df010ecaa36c1f01087f59ec97a200d052be85cb41487bc81dd602f81cf58d87(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92a0bf94eca47e1919f76008b563c389bb8326f7b8e7ea98b43d91a92d60d6f0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b312800cc2fde4cf1654f1085d4bd154cc41a93e8fcca6c80bc6cded1bd9dd6a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureGroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88f1fc4461d10eb217fd3dda3c09045a0c44a490226d7bb8935954d3cc74291a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44c803b08b4e6bf551049627f6b4a741a9caaaae8cca735274c0c2cb94a49ded(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__735239ab519d96911071aead7b75362d1ba82434f21936f509284dbf5bd66916(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureGroups]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__458586c17aa75d8597cd14acce557fa964a0ba0ce7e76aa1bc2e7f57b794d4b0(
    *,
    scope: builtins.str,
    role_id: typing.Optional[builtins.str] = None,
    role_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b347d4b9c2441bee4d6b772f02126bb45fd59fd456d2b3aa287e1fa9b765ab1d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e66c89598269f9121932074a7a418c9b507e18fa1f860a669a7572866eece20f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1780b6625a00af1a400fc6526ede38f7eda75790cdbf0857c622bd054c6be1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427b053c1e8fd6e6ce38d8357babf32ca7c6e3d2fd582f3f6b4280a3c22d1556(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d78b4bc697509f1e73038c8329b35f2691c72847bffc548963a4d4607a0a5b24(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd29a1ff123cbd70655d68b9ffcf4bddba7bece9b22fb6583177bdd797fee93c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AzureSecretBackendRoleAzureRoles]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edd89e139a223b1ef1d18f595efba2b96ea1a14c75f5f4972911419c98c42be6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88b745afeb032874c092594731598d85995a00304676bc55e37a6ef143db5192(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beef246f30058a3d3a2f0ab51442ceb57228d2691e99848c790792803d1c7c0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb6e45aad43c21819f4be62d80254e61f5115d9a0830fc70ccebb759e96fcf56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96927d06dcdc781733babec99f3a002ec324e774ccec9e08ba1ca8a8c309cc38(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AzureSecretBackendRoleAzureRoles]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c16c8590791c5a181e9f5a01d453e19cbc98c8d3d9f157279bfe078368754499(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    role: builtins.str,
    application_object_id: typing.Optional[builtins.str] = None,
    azure_groups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureGroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_roles: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AzureSecretBackendRoleAzureRoles, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    explicit_max_ttl: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    permanently_delete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sign_in_audience: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
