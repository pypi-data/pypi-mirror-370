r'''
# `vault_terraform_cloud_secret_role`

Refer to the Terraform Registry for docs: [`vault_terraform_cloud_secret_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role).
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


class TerraformCloudSecretRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.terraformCloudSecretRole.TerraformCloudSecretRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role vault_terraform_cloud_secret_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        team_id: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        user_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role vault_terraform_cloud_secret_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of an existing role against which to create this Terraform Cloud credential. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#name TerraformCloudSecretRole#name}
        :param backend: The path of the Terraform Cloud Secret Backend the role belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#backend TerraformCloudSecretRole#backend}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#id TerraformCloudSecretRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_ttl: Maximum allowed lease for generated credentials. If not set or set to 0, will use system default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#max_ttl TerraformCloudSecretRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#namespace TerraformCloudSecretRole#namespace}
        :param organization: Name of the Terraform Cloud or Enterprise organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#organization TerraformCloudSecretRole#organization}
        :param team_id: ID of the Terraform Cloud or Enterprise team under organization (e.g., settings/teams/team-xxxxxxxxxxxxx). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#team_id TerraformCloudSecretRole#team_id}
        :param ttl: Default lease for generated credentials. If not set or set to 0, will use system default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#ttl TerraformCloudSecretRole#ttl}
        :param user_id: ID of the Terraform Cloud or Enterprise user (e.g., user-xxxxxxxxxxxxxxxx). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#user_id TerraformCloudSecretRole#user_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__799c9fe77fae97c80c973c47339cc44bea11a8cbae4cac03e1b2145cff05d270)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TerraformCloudSecretRoleConfig(
            name=name,
            backend=backend,
            id=id,
            max_ttl=max_ttl,
            namespace=namespace,
            organization=organization,
            team_id=team_id,
            ttl=ttl,
            user_id=user_id,
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
        '''Generates CDKTF code for importing a TerraformCloudSecretRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TerraformCloudSecretRole to import.
        :param import_from_id: The id of the existing TerraformCloudSecretRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TerraformCloudSecretRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0826b1e5a8fff1d45f0330ee22afd16250823431e3e2ebd31eae1d7230120cee)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetTeamId")
    def reset_team_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamId", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffeed73a3b69fb99fcf529af25d7ffd6ac37986e664bb35ba0bddb379abbb233)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e00705ebf02fb9f86e189b6cde77675f7aa954bc26d66b7f120f3bf26a6bde1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__765b33ee577eaf06c193a957595c705f421041a4e20fa62ceed78a78a74c40f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__865ec2dd3e849761337dc9899b38ef5f2619f5e3edc7696e25eab80f6de2a25d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fe598c1cc6850c2089307316880953838f1bde0d6aae370cb28725c98780c92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__550b3940d6c19e54f2afc476e05452e27d5787c186294370c4d5ee48d9f7001f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamId"))

    @team_id.setter
    def team_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03ee9e50e5b110aaec68755e7f9c3e7b00f3d5287646d4a757ee9ad5cf175343)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dc06e782bd4a2842599b05a412d2f779f6cd8c42609545d5b24d386c9ae77cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87ceb9a74c8758e6291fd5670533d1d9d9e8192beb8ca60c899ad70832529f29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.terraformCloudSecretRole.TerraformCloudSecretRoleConfig",
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
        "backend": "backend",
        "id": "id",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "organization": "organization",
        "team_id": "teamId",
        "ttl": "ttl",
        "user_id": "userId",
    },
)
class TerraformCloudSecretRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        team_id: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: The name of an existing role against which to create this Terraform Cloud credential. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#name TerraformCloudSecretRole#name}
        :param backend: The path of the Terraform Cloud Secret Backend the role belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#backend TerraformCloudSecretRole#backend}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#id TerraformCloudSecretRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_ttl: Maximum allowed lease for generated credentials. If not set or set to 0, will use system default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#max_ttl TerraformCloudSecretRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#namespace TerraformCloudSecretRole#namespace}
        :param organization: Name of the Terraform Cloud or Enterprise organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#organization TerraformCloudSecretRole#organization}
        :param team_id: ID of the Terraform Cloud or Enterprise team under organization (e.g., settings/teams/team-xxxxxxxxxxxxx). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#team_id TerraformCloudSecretRole#team_id}
        :param ttl: Default lease for generated credentials. If not set or set to 0, will use system default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#ttl TerraformCloudSecretRole#ttl}
        :param user_id: ID of the Terraform Cloud or Enterprise user (e.g., user-xxxxxxxxxxxxxxxx). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#user_id TerraformCloudSecretRole#user_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c41088a482917bc39fb12a7c2148e6093160d70c592a3994a6db7562441ca3e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
            check_type(argname="argument team_id", value=team_id, expected_type=type_hints["team_id"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if backend is not None:
            self._values["backend"] = backend
        if id is not None:
            self._values["id"] = id
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if organization is not None:
            self._values["organization"] = organization
        if team_id is not None:
            self._values["team_id"] = team_id
        if ttl is not None:
            self._values["ttl"] = ttl
        if user_id is not None:
            self._values["user_id"] = user_id

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
        '''The name of an existing role against which to create this Terraform Cloud credential.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#name TerraformCloudSecretRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''The path of the Terraform Cloud Secret Backend the role belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#backend TerraformCloudSecretRole#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#id TerraformCloudSecretRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Maximum allowed lease for generated credentials. If not set or set to 0, will use system default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#max_ttl TerraformCloudSecretRole#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#namespace TerraformCloudSecretRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Name of the Terraform Cloud or Enterprise organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#organization TerraformCloudSecretRole#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def team_id(self) -> typing.Optional[builtins.str]:
        '''ID of the Terraform Cloud or Enterprise team under organization (e.g., settings/teams/team-xxxxxxxxxxxxx).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#team_id TerraformCloudSecretRole#team_id}
        '''
        result = self._values.get("team_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Default lease for generated credentials. If not set or set to 0, will use system default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#ttl TerraformCloudSecretRole#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''ID of the Terraform Cloud or Enterprise user (e.g., user-xxxxxxxxxxxxxxxx).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/terraform_cloud_secret_role#user_id TerraformCloudSecretRole#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TerraformCloudSecretRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TerraformCloudSecretRole",
    "TerraformCloudSecretRoleConfig",
]

publication.publish()

def _typecheckingstub__799c9fe77fae97c80c973c47339cc44bea11a8cbae4cac03e1b2145cff05d270(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    team_id: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    user_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__0826b1e5a8fff1d45f0330ee22afd16250823431e3e2ebd31eae1d7230120cee(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffeed73a3b69fb99fcf529af25d7ffd6ac37986e664bb35ba0bddb379abbb233(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e00705ebf02fb9f86e189b6cde77675f7aa954bc26d66b7f120f3bf26a6bde1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__765b33ee577eaf06c193a957595c705f421041a4e20fa62ceed78a78a74c40f4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__865ec2dd3e849761337dc9899b38ef5f2619f5e3edc7696e25eab80f6de2a25d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fe598c1cc6850c2089307316880953838f1bde0d6aae370cb28725c98780c92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__550b3940d6c19e54f2afc476e05452e27d5787c186294370c4d5ee48d9f7001f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03ee9e50e5b110aaec68755e7f9c3e7b00f3d5287646d4a757ee9ad5cf175343(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dc06e782bd4a2842599b05a412d2f779f6cd8c42609545d5b24d386c9ae77cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87ceb9a74c8758e6291fd5670533d1d9d9e8192beb8ca60c899ad70832529f29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c41088a482917bc39fb12a7c2148e6093160d70c592a3994a6db7562441ca3e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    team_id: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
