r'''
# `vault_mongodbatlas_secret_role`

Refer to the Terraform Registry for docs: [`vault_mongodbatlas_secret_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role).
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


class MongodbatlasSecretRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.mongodbatlasSecretRole.MongodbatlasSecretRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role vault_mongodbatlas_secret_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        mount: builtins.str,
        name: builtins.str,
        roles: typing.Sequence[builtins.str],
        cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        organization_id: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        project_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role vault_mongodbatlas_secret_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param mount: Path where MongoDB Atlas secret backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#mount MongodbatlasSecretRole#mount}
        :param name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#name MongodbatlasSecretRole#name}
        :param roles: List of roles that the API Key needs to have. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#roles MongodbatlasSecretRole#roles}
        :param cidr_blocks: Whitelist entry in CIDR notation to be added for the API key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#cidr_blocks MongodbatlasSecretRole#cidr_blocks}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#id MongodbatlasSecretRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_addresses: IP address to be added to the whitelist for the API key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#ip_addresses MongodbatlasSecretRole#ip_addresses}
        :param max_ttl: The maximum allowed lifetime of credentials issued using this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#max_ttl MongodbatlasSecretRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#namespace MongodbatlasSecretRole#namespace}
        :param organization_id: ID for the organization to which the target API Key belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#organization_id MongodbatlasSecretRole#organization_id}
        :param project_id: ID for the project to which the target API Key belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#project_id MongodbatlasSecretRole#project_id}
        :param project_roles: Roles assigned when an org API key is assigned to a project API key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#project_roles MongodbatlasSecretRole#project_roles}
        :param ttl: Duration in seconds after which the issued credential should expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#ttl MongodbatlasSecretRole#ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0321f92dff3bbb9efd5c4653ca39fbe6c85f32f2b82028c08ce7f815763cfe5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MongodbatlasSecretRoleConfig(
            mount=mount,
            name=name,
            roles=roles,
            cidr_blocks=cidr_blocks,
            id=id,
            ip_addresses=ip_addresses,
            max_ttl=max_ttl,
            namespace=namespace,
            organization_id=organization_id,
            project_id=project_id,
            project_roles=project_roles,
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
        '''Generates CDKTF code for importing a MongodbatlasSecretRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MongodbatlasSecretRole to import.
        :param import_from_id: The id of the existing MongodbatlasSecretRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MongodbatlasSecretRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__332dbfdf952aa9475cc675de385cf9a739fae350bb0fcdcd2fa393887ccb119a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCidrBlocks")
    def reset_cidr_blocks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCidrBlocks", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpAddresses")
    def reset_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddresses", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOrganizationId")
    def reset_organization_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationId", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetProjectRoles")
    def reset_project_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectRoles", []))

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
    @jsii.member(jsii_name="cidrBlocksInput")
    def cidr_blocks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cidrBlocksInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipAddressesInput")
    def ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTtlInput"))

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
    @jsii.member(jsii_name="organizationIdInput")
    def organization_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectRolesInput")
    def project_roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "projectRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="rolesInput")
    def roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rolesInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="cidrBlocks")
    def cidr_blocks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cidrBlocks"))

    @cidr_blocks.setter
    def cidr_blocks(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c6614de7e3d19ea2f0caa072ca85fcfc12831ef82b55754c461214e997f17e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidrBlocks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21f4165816d7840314d5e2c07604a101db2777ea29787838039ab58361ce8ff2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ed2499079cd4455b3e72e5e2672cbd05317852f4873dbfabae95daf0da7672a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipAddresses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8148749827257ce8a2d68ede23cb96bd3fe198f230245841431d54736eb30a54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mount")
    def mount(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mount"))

    @mount.setter
    def mount(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf4870d156d5551d94b32d1b9d1fc2a710ee17e429ba7592c534804585139556)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79953e9e6ef2d870116642e4fb7ef026e5f213943f61f5a5099f9d6411f7456d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__979cb186d54cfee58543c9784d0308e2029eeb9575f0e8dd7471af214feeb7a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @organization_id.setter
    def organization_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c06f35be8595baaa2dc2bca46843820a40c6369507a6a2d5e4a5d78f83b649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d2a315903df7dc260d09fc541c473becb5171f61bf2c16d1caf67e94e67b9f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectRoles")
    def project_roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "projectRoles"))

    @project_roles.setter
    def project_roles(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d2c8f300cc294b09f15431d923bc9cf9cecb49bcc68cbf6ec5e33c1cad1c0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectRoles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "roles"))

    @roles.setter
    def roles(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c79293d4b82c4e47635731debbd076fd7d300dd2c62ed6238acc4fa9b54bbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f50a06ca142f6997d8619671aa110724c575ad404248fc74d14efec51f6539)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.mongodbatlasSecretRole.MongodbatlasSecretRoleConfig",
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
        "roles": "roles",
        "cidr_blocks": "cidrBlocks",
        "id": "id",
        "ip_addresses": "ipAddresses",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "organization_id": "organizationId",
        "project_id": "projectId",
        "project_roles": "projectRoles",
        "ttl": "ttl",
    },
)
class MongodbatlasSecretRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        roles: typing.Sequence[builtins.str],
        cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        organization_id: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        project_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        :param mount: Path where MongoDB Atlas secret backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#mount MongodbatlasSecretRole#mount}
        :param name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#name MongodbatlasSecretRole#name}
        :param roles: List of roles that the API Key needs to have. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#roles MongodbatlasSecretRole#roles}
        :param cidr_blocks: Whitelist entry in CIDR notation to be added for the API key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#cidr_blocks MongodbatlasSecretRole#cidr_blocks}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#id MongodbatlasSecretRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_addresses: IP address to be added to the whitelist for the API key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#ip_addresses MongodbatlasSecretRole#ip_addresses}
        :param max_ttl: The maximum allowed lifetime of credentials issued using this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#max_ttl MongodbatlasSecretRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#namespace MongodbatlasSecretRole#namespace}
        :param organization_id: ID for the organization to which the target API Key belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#organization_id MongodbatlasSecretRole#organization_id}
        :param project_id: ID for the project to which the target API Key belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#project_id MongodbatlasSecretRole#project_id}
        :param project_roles: Roles assigned when an org API key is assigned to a project API key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#project_roles MongodbatlasSecretRole#project_roles}
        :param ttl: Duration in seconds after which the issued credential should expire. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#ttl MongodbatlasSecretRole#ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a682319aa1d7c99f3aa86094a1ef1ee7be75a6fcd155d7da974ce1b8e5a13e4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument roles", value=roles, expected_type=type_hints["roles"])
            check_type(argname="argument cidr_blocks", value=cidr_blocks, expected_type=type_hints["cidr_blocks"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument organization_id", value=organization_id, expected_type=type_hints["organization_id"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument project_roles", value=project_roles, expected_type=type_hints["project_roles"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mount": mount,
            "name": name,
            "roles": roles,
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
        if cidr_blocks is not None:
            self._values["cidr_blocks"] = cidr_blocks
        if id is not None:
            self._values["id"] = id
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if organization_id is not None:
            self._values["organization_id"] = organization_id
        if project_id is not None:
            self._values["project_id"] = project_id
        if project_roles is not None:
            self._values["project_roles"] = project_roles
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
    def mount(self) -> builtins.str:
        '''Path where MongoDB Atlas secret backend is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#mount MongodbatlasSecretRole#mount}
        '''
        result = self._values.get("mount")
        assert result is not None, "Required property 'mount' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#name MongodbatlasSecretRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def roles(self) -> typing.List[builtins.str]:
        '''List of roles that the API Key needs to have.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#roles MongodbatlasSecretRole#roles}
        '''
        result = self._values.get("roles")
        assert result is not None, "Required property 'roles' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cidr_blocks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Whitelist entry in CIDR notation to be added for the API key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#cidr_blocks MongodbatlasSecretRole#cidr_blocks}
        '''
        result = self._values.get("cidr_blocks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#id MongodbatlasSecretRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IP address to be added to the whitelist for the API key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#ip_addresses MongodbatlasSecretRole#ip_addresses}
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[builtins.str]:
        '''The maximum allowed lifetime of credentials issued using this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#max_ttl MongodbatlasSecretRole#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#namespace MongodbatlasSecretRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization_id(self) -> typing.Optional[builtins.str]:
        '''ID for the organization to which the target API Key belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#organization_id MongodbatlasSecretRole#organization_id}
        '''
        result = self._values.get("organization_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''ID for the project to which the target API Key belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#project_id MongodbatlasSecretRole#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Roles assigned when an org API key is assigned to a project API key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#project_roles MongodbatlasSecretRole#project_roles}
        '''
        result = self._values.get("project_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Duration in seconds after which the issued credential should expire.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mongodbatlas_secret_role#ttl MongodbatlasSecretRole#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MongodbatlasSecretRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MongodbatlasSecretRole",
    "MongodbatlasSecretRoleConfig",
]

publication.publish()

def _typecheckingstub__f0321f92dff3bbb9efd5c4653ca39fbe6c85f32f2b82028c08ce7f815763cfe5(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    mount: builtins.str,
    name: builtins.str,
    roles: typing.Sequence[builtins.str],
    cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    organization_id: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    project_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__332dbfdf952aa9475cc675de385cf9a739fae350bb0fcdcd2fa393887ccb119a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c6614de7e3d19ea2f0caa072ca85fcfc12831ef82b55754c461214e997f17e3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f4165816d7840314d5e2c07604a101db2777ea29787838039ab58361ce8ff2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed2499079cd4455b3e72e5e2672cbd05317852f4873dbfabae95daf0da7672a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8148749827257ce8a2d68ede23cb96bd3fe198f230245841431d54736eb30a54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf4870d156d5551d94b32d1b9d1fc2a710ee17e429ba7592c534804585139556(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79953e9e6ef2d870116642e4fb7ef026e5f213943f61f5a5099f9d6411f7456d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__979cb186d54cfee58543c9784d0308e2029eeb9575f0e8dd7471af214feeb7a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c06f35be8595baaa2dc2bca46843820a40c6369507a6a2d5e4a5d78f83b649(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d2a315903df7dc260d09fc541c473becb5171f61bf2c16d1caf67e94e67b9f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59d2c8f300cc294b09f15431d923bc9cf9cecb49bcc68cbf6ec5e33c1cad1c0f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c79293d4b82c4e47635731debbd076fd7d300dd2c62ed6238acc4fa9b54bbd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f50a06ca142f6997d8619671aa110724c575ad404248fc74d14efec51f6539(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a682319aa1d7c99f3aa86094a1ef1ee7be75a6fcd155d7da974ce1b8e5a13e4(
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
    roles: typing.Sequence[builtins.str],
    cidr_blocks: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    organization_id: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    project_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
