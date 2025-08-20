r'''
# `vault_aws_auth_backend_role_tag`

Refer to the Terraform Registry for docs: [`vault_aws_auth_backend_role_tag`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag).
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


class AwsAuthBackendRoleTag(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.awsAuthBackendRoleTag.AwsAuthBackendRoleTag",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag vault_aws_auth_backend_role_tag}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        role: builtins.str,
        allow_instance_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backend: typing.Optional[builtins.str] = None,
        disallow_reauthentication: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag vault_aws_auth_backend_role_tag} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#role AwsAuthBackendRoleTag#role}
        :param allow_instance_migration: Allows migration of the underlying instance where the client resides. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#allow_instance_migration AwsAuthBackendRoleTag#allow_instance_migration}
        :param backend: AWS auth backend to read tags from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#backend AwsAuthBackendRoleTag#backend}
        :param disallow_reauthentication: Only allow a single token to be granted per instance ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#disallow_reauthentication AwsAuthBackendRoleTag#disallow_reauthentication}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#id AwsAuthBackendRoleTag#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_id: Instance ID for which this tag is intended. The created tag can only be used by the instance with the given ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#instance_id AwsAuthBackendRoleTag#instance_id}
        :param max_ttl: The maximum allowed lifetime of tokens issued using this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#max_ttl AwsAuthBackendRoleTag#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#namespace AwsAuthBackendRoleTag#namespace}
        :param policies: Policies to be associated with the tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#policies AwsAuthBackendRoleTag#policies}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23e059643f87fbbb601328e82e00871ccfdef56495990d5fcdbca341c1578004)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AwsAuthBackendRoleTagConfig(
            role=role,
            allow_instance_migration=allow_instance_migration,
            backend=backend,
            disallow_reauthentication=disallow_reauthentication,
            id=id,
            instance_id=instance_id,
            max_ttl=max_ttl,
            namespace=namespace,
            policies=policies,
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
        '''Generates CDKTF code for importing a AwsAuthBackendRoleTag resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AwsAuthBackendRoleTag to import.
        :param import_from_id: The id of the existing AwsAuthBackendRoleTag that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AwsAuthBackendRoleTag to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02225703ccab1dfeaa6ada8189d2c20196a6f93f8991ed72e0ae5f873dbedb03)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowInstanceMigration")
    def reset_allow_instance_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowInstanceMigration", []))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetDisallowReauthentication")
    def reset_disallow_reauthentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisallowReauthentication", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstanceId")
    def reset_instance_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceId", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPolicies")
    def reset_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicies", []))

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
    @jsii.member(jsii_name="tagKey")
    def tag_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagKey"))

    @builtins.property
    @jsii.member(jsii_name="tagValue")
    def tag_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tagValue"))

    @builtins.property
    @jsii.member(jsii_name="allowInstanceMigrationInput")
    def allow_instance_migration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowInstanceMigrationInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="disallowReauthenticationInput")
    def disallow_reauthentication_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disallowReauthenticationInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceIdInput")
    def instance_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="policiesInput")
    def policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "policiesInput"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="allowInstanceMigration")
    def allow_instance_migration(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowInstanceMigration"))

    @allow_instance_migration.setter
    def allow_instance_migration(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9210e32a801dd92ef75007858601d68bebe8effd4cae1a63390d8321d0195d69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowInstanceMigration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d5f28b09f5399a698d32829b40545a6ddeb3e30b2bd8f7c077ab28a07415fdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disallowReauthentication")
    def disallow_reauthentication(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disallowReauthentication"))

    @disallow_reauthentication.setter
    def disallow_reauthentication(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e808c6c44a03e0673dc1cf84823df1d45f502c6e482d36742321b6ffee2fa5e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disallowReauthentication", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4806178d1cd82a67a0dc839bdfd34ed4414a5028b515a40593c7da8cb7f0e8d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceId")
    def instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceId"))

    @instance_id.setter
    def instance_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1655ef8f10ee807aa0f65444a5fe0e922eeb3b60477c34e4abffaee46766ca5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__340d7a729232c95f78e6c3789853b5260f020d37855f7c7fea78af3e78be5469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a8b7d919d1f558ed19e2d1808e8acbec8a8ea37f229cca760ce146c0b3ea3d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "policies"))

    @policies.setter
    def policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46c68c45dc4ae040866e0a244d3a7eb28bcc3816f0d21a4033d8eb12ac671804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d8d213b5cbda4468268a28b498a0357c50f7b573e6e83d190c7a568fbabb6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.awsAuthBackendRoleTag.AwsAuthBackendRoleTagConfig",
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
        "allow_instance_migration": "allowInstanceMigration",
        "backend": "backend",
        "disallow_reauthentication": "disallowReauthentication",
        "id": "id",
        "instance_id": "instanceId",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "policies": "policies",
    },
)
class AwsAuthBackendRoleTagConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allow_instance_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backend: typing.Optional[builtins.str] = None,
        disallow_reauthentication: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        instance_id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#role AwsAuthBackendRoleTag#role}
        :param allow_instance_migration: Allows migration of the underlying instance where the client resides. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#allow_instance_migration AwsAuthBackendRoleTag#allow_instance_migration}
        :param backend: AWS auth backend to read tags from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#backend AwsAuthBackendRoleTag#backend}
        :param disallow_reauthentication: Only allow a single token to be granted per instance ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#disallow_reauthentication AwsAuthBackendRoleTag#disallow_reauthentication}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#id AwsAuthBackendRoleTag#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param instance_id: Instance ID for which this tag is intended. The created tag can only be used by the instance with the given ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#instance_id AwsAuthBackendRoleTag#instance_id}
        :param max_ttl: The maximum allowed lifetime of tokens issued using this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#max_ttl AwsAuthBackendRoleTag#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#namespace AwsAuthBackendRoleTag#namespace}
        :param policies: Policies to be associated with the tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#policies AwsAuthBackendRoleTag#policies}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce67d279e263155cb8869352688fe19ec803041928e8d1b91a3a319139714c78)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument allow_instance_migration", value=allow_instance_migration, expected_type=type_hints["allow_instance_migration"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument disallow_reauthentication", value=disallow_reauthentication, expected_type=type_hints["disallow_reauthentication"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument instance_id", value=instance_id, expected_type=type_hints["instance_id"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument policies", value=policies, expected_type=type_hints["policies"])
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
        if allow_instance_migration is not None:
            self._values["allow_instance_migration"] = allow_instance_migration
        if backend is not None:
            self._values["backend"] = backend
        if disallow_reauthentication is not None:
            self._values["disallow_reauthentication"] = disallow_reauthentication
        if id is not None:
            self._values["id"] = id
        if instance_id is not None:
            self._values["instance_id"] = instance_id
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if policies is not None:
            self._values["policies"] = policies

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
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#role AwsAuthBackendRoleTag#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_instance_migration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allows migration of the underlying instance where the client resides.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#allow_instance_migration AwsAuthBackendRoleTag#allow_instance_migration}
        '''
        result = self._values.get("allow_instance_migration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''AWS auth backend to read tags from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#backend AwsAuthBackendRoleTag#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disallow_reauthentication(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Only allow a single token to be granted per instance ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#disallow_reauthentication AwsAuthBackendRoleTag#disallow_reauthentication}
        '''
        result = self._values.get("disallow_reauthentication")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#id AwsAuthBackendRoleTag#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_id(self) -> typing.Optional[builtins.str]:
        '''Instance ID for which this tag is intended.

        The created tag can only be used by the instance with the given ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#instance_id AwsAuthBackendRoleTag#instance_id}
        '''
        result = self._values.get("instance_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[builtins.str]:
        '''The maximum allowed lifetime of tokens issued using this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#max_ttl AwsAuthBackendRoleTag#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#namespace AwsAuthBackendRoleTag#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Policies to be associated with the tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_role_tag#policies AwsAuthBackendRoleTag#policies}
        '''
        result = self._values.get("policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsAuthBackendRoleTagConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsAuthBackendRoleTag",
    "AwsAuthBackendRoleTagConfig",
]

publication.publish()

def _typecheckingstub__23e059643f87fbbb601328e82e00871ccfdef56495990d5fcdbca341c1578004(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    role: builtins.str,
    allow_instance_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backend: typing.Optional[builtins.str] = None,
    disallow_reauthentication: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    policies: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__02225703ccab1dfeaa6ada8189d2c20196a6f93f8991ed72e0ae5f873dbedb03(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9210e32a801dd92ef75007858601d68bebe8effd4cae1a63390d8321d0195d69(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d5f28b09f5399a698d32829b40545a6ddeb3e30b2bd8f7c077ab28a07415fdf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e808c6c44a03e0673dc1cf84823df1d45f502c6e482d36742321b6ffee2fa5e7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4806178d1cd82a67a0dc839bdfd34ed4414a5028b515a40593c7da8cb7f0e8d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1655ef8f10ee807aa0f65444a5fe0e922eeb3b60477c34e4abffaee46766ca5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__340d7a729232c95f78e6c3789853b5260f020d37855f7c7fea78af3e78be5469(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a8b7d919d1f558ed19e2d1808e8acbec8a8ea37f229cca760ce146c0b3ea3d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46c68c45dc4ae040866e0a244d3a7eb28bcc3816f0d21a4033d8eb12ac671804(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d8d213b5cbda4468268a28b498a0357c50f7b573e6e83d190c7a568fbabb6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce67d279e263155cb8869352688fe19ec803041928e8d1b91a3a319139714c78(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    role: builtins.str,
    allow_instance_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backend: typing.Optional[builtins.str] = None,
    disallow_reauthentication: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    instance_id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    policies: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
