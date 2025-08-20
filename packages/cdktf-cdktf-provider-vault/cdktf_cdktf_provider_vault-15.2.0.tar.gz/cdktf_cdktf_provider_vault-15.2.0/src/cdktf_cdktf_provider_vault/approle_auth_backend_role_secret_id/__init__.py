r'''
# `vault_approle_auth_backend_role_secret_id`

Refer to the Terraform Registry for docs: [`vault_approle_auth_backend_role_secret_id`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id).
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


class ApproleAuthBackendRoleSecretId(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.approleAuthBackendRoleSecretId.ApproleAuthBackendRoleSecretId",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id vault_approle_auth_backend_role_secret_id}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        role_name: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        cidr_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        num_uses: typing.Optional[jsii.Number] = None,
        secret_id: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        with_wrapped_accessor: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        wrapping_ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id vault_approle_auth_backend_role_secret_id} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#role_name ApproleAuthBackendRoleSecretId#role_name}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#backend ApproleAuthBackendRoleSecretId#backend}
        :param cidr_list: List of CIDR blocks that can log in using the SecretID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#cidr_list ApproleAuthBackendRoleSecretId#cidr_list}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#id ApproleAuthBackendRoleSecretId#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metadata: JSON-encoded secret data to write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#metadata ApproleAuthBackendRoleSecretId#metadata}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#namespace ApproleAuthBackendRoleSecretId#namespace}
        :param num_uses: The number of uses for the secret-id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#num_uses ApproleAuthBackendRoleSecretId#num_uses}
        :param secret_id: The SecretID to be managed. If not specified, Vault auto-generates one. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#secret_id ApproleAuthBackendRoleSecretId#secret_id}
        :param ttl: The TTL duration of the SecretID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#ttl ApproleAuthBackendRoleSecretId#ttl}
        :param with_wrapped_accessor: Use the wrapped secret-id accessor as the id of this resource. If false, a fresh secret-id will be regenerated whenever the wrapping token is expired or invalidated through unwrapping. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#with_wrapped_accessor ApproleAuthBackendRoleSecretId#with_wrapped_accessor}
        :param wrapping_ttl: The TTL duration of the wrapped SecretID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#wrapping_ttl ApproleAuthBackendRoleSecretId#wrapping_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2adf1e9bcf6dae03b68ab233df1e00e52977736a51c8e89d667b550d294ac58)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ApproleAuthBackendRoleSecretIdConfig(
            role_name=role_name,
            backend=backend,
            cidr_list=cidr_list,
            id=id,
            metadata=metadata,
            namespace=namespace,
            num_uses=num_uses,
            secret_id=secret_id,
            ttl=ttl,
            with_wrapped_accessor=with_wrapped_accessor,
            wrapping_ttl=wrapping_ttl,
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
        '''Generates CDKTF code for importing a ApproleAuthBackendRoleSecretId resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ApproleAuthBackendRoleSecretId to import.
        :param import_from_id: The id of the existing ApproleAuthBackendRoleSecretId that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ApproleAuthBackendRoleSecretId to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__172c8c8464a25cc33f7fb4a9f34f047f93eec3654d33b120e24f4951e0747245)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetCidrList")
    def reset_cidr_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCidrList", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMetadata")
    def reset_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetadata", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNumUses")
    def reset_num_uses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumUses", []))

    @jsii.member(jsii_name="resetSecretId")
    def reset_secret_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretId", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

    @jsii.member(jsii_name="resetWithWrappedAccessor")
    def reset_with_wrapped_accessor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWithWrappedAccessor", []))

    @jsii.member(jsii_name="resetWrappingTtl")
    def reset_wrapping_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWrappingTtl", []))

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
    @jsii.member(jsii_name="accessor")
    def accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessor"))

    @builtins.property
    @jsii.member(jsii_name="wrappingAccessor")
    def wrapping_accessor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wrappingAccessor"))

    @builtins.property
    @jsii.member(jsii_name="wrappingToken")
    def wrapping_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wrappingToken"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="cidrListInput")
    def cidr_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cidrListInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="numUsesInput")
    def num_uses_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numUsesInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretIdInput")
    def secret_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretIdInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="withWrappedAccessorInput")
    def with_wrapped_accessor_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "withWrappedAccessorInput"))

    @builtins.property
    @jsii.member(jsii_name="wrappingTtlInput")
    def wrapping_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "wrappingTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17201cf952ac38c026fb696cc2d158d106aa69ffe74c715bd838d6ea29c0438a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cidrList")
    def cidr_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cidrList"))

    @cidr_list.setter
    def cidr_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5806fa35c7cdfd03895088230f6b80a4f2023473067aeebf1633004626e775f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cidrList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81a454b52d37b612081c4582740a620009173eccf16bedac6d0abd04a9de2f02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metadata"))

    @metadata.setter
    def metadata(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f78a9ed5ff9824172691cc17b227a39af2518d46b0bbd79b3f4a9b0830c7144)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5756ba949b87d6b556f601cb2023770332b3eac5226c156ff80856271b6c1206)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numUses")
    def num_uses(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numUses"))

    @num_uses.setter
    def num_uses(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfe7de60911b27509042f9418c51414663efb250c0da2784f337db2960d7438e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numUses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1cb45649e9df1bf3486d45dc8c62d7ae3b852e3df33bacdf181edc184ab2b87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretId"))

    @secret_id.setter
    def secret_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e1368ef247657555561cc6785f5eb7abc33592756c64df097550eb4ad68872f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ff2db674a0c9b06cadc20309485c55c13224326045f69d632bdc3bf070116e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="withWrappedAccessor")
    def with_wrapped_accessor(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "withWrappedAccessor"))

    @with_wrapped_accessor.setter
    def with_wrapped_accessor(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7f6895cf03c1b0902a7ac0c3a7e5bfd11954f49b8fbf39be3469f7c89a08ce0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "withWrappedAccessor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrappingTtl")
    def wrapping_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "wrappingTtl"))

    @wrapping_ttl.setter
    def wrapping_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0110aad99f3b9690405df671533a4dc77ec42736d29cd6c9056fe2ac3a097bdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrappingTtl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.approleAuthBackendRoleSecretId.ApproleAuthBackendRoleSecretIdConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "role_name": "roleName",
        "backend": "backend",
        "cidr_list": "cidrList",
        "id": "id",
        "metadata": "metadata",
        "namespace": "namespace",
        "num_uses": "numUses",
        "secret_id": "secretId",
        "ttl": "ttl",
        "with_wrapped_accessor": "withWrappedAccessor",
        "wrapping_ttl": "wrappingTtl",
    },
)
class ApproleAuthBackendRoleSecretIdConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        role_name: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        cidr_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        num_uses: typing.Optional[jsii.Number] = None,
        secret_id: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        with_wrapped_accessor: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        wrapping_ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#role_name ApproleAuthBackendRoleSecretId#role_name}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#backend ApproleAuthBackendRoleSecretId#backend}
        :param cidr_list: List of CIDR blocks that can log in using the SecretID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#cidr_list ApproleAuthBackendRoleSecretId#cidr_list}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#id ApproleAuthBackendRoleSecretId#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param metadata: JSON-encoded secret data to write. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#metadata ApproleAuthBackendRoleSecretId#metadata}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#namespace ApproleAuthBackendRoleSecretId#namespace}
        :param num_uses: The number of uses for the secret-id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#num_uses ApproleAuthBackendRoleSecretId#num_uses}
        :param secret_id: The SecretID to be managed. If not specified, Vault auto-generates one. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#secret_id ApproleAuthBackendRoleSecretId#secret_id}
        :param ttl: The TTL duration of the SecretID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#ttl ApproleAuthBackendRoleSecretId#ttl}
        :param with_wrapped_accessor: Use the wrapped secret-id accessor as the id of this resource. If false, a fresh secret-id will be regenerated whenever the wrapping token is expired or invalidated through unwrapping. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#with_wrapped_accessor ApproleAuthBackendRoleSecretId#with_wrapped_accessor}
        :param wrapping_ttl: The TTL duration of the wrapped SecretID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#wrapping_ttl ApproleAuthBackendRoleSecretId#wrapping_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398d9313da8923f3686c46e15e84f9e0673d56bf3bb2a4a482c64707021c6ce2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument cidr_list", value=cidr_list, expected_type=type_hints["cidr_list"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument num_uses", value=num_uses, expected_type=type_hints["num_uses"])
            check_type(argname="argument secret_id", value=secret_id, expected_type=type_hints["secret_id"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument with_wrapped_accessor", value=with_wrapped_accessor, expected_type=type_hints["with_wrapped_accessor"])
            check_type(argname="argument wrapping_ttl", value=wrapping_ttl, expected_type=type_hints["wrapping_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_name": role_name,
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
        if cidr_list is not None:
            self._values["cidr_list"] = cidr_list
        if id is not None:
            self._values["id"] = id
        if metadata is not None:
            self._values["metadata"] = metadata
        if namespace is not None:
            self._values["namespace"] = namespace
        if num_uses is not None:
            self._values["num_uses"] = num_uses
        if secret_id is not None:
            self._values["secret_id"] = secret_id
        if ttl is not None:
            self._values["ttl"] = ttl
        if with_wrapped_accessor is not None:
            self._values["with_wrapped_accessor"] = with_wrapped_accessor
        if wrapping_ttl is not None:
            self._values["wrapping_ttl"] = wrapping_ttl

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
    def role_name(self) -> builtins.str:
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#role_name ApproleAuthBackendRoleSecretId#role_name}
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the auth backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#backend ApproleAuthBackendRoleSecretId#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cidr_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of CIDR blocks that can log in using the SecretID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#cidr_list ApproleAuthBackendRoleSecretId#cidr_list}
        '''
        result = self._values.get("cidr_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#id ApproleAuthBackendRoleSecretId#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(self) -> typing.Optional[builtins.str]:
        '''JSON-encoded secret data to write.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#metadata ApproleAuthBackendRoleSecretId#metadata}
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#namespace ApproleAuthBackendRoleSecretId#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_uses(self) -> typing.Optional[jsii.Number]:
        '''The number of uses for the secret-id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#num_uses ApproleAuthBackendRoleSecretId#num_uses}
        '''
        result = self._values.get("num_uses")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def secret_id(self) -> typing.Optional[builtins.str]:
        '''The SecretID to be managed. If not specified, Vault auto-generates one.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#secret_id ApproleAuthBackendRoleSecretId#secret_id}
        '''
        result = self._values.get("secret_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''The TTL duration of the SecretID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#ttl ApproleAuthBackendRoleSecretId#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def with_wrapped_accessor(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use the wrapped secret-id accessor as the id of this resource.

        If false, a fresh secret-id will be regenerated whenever the wrapping token is expired or invalidated through unwrapping.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#with_wrapped_accessor ApproleAuthBackendRoleSecretId#with_wrapped_accessor}
        '''
        result = self._values.get("with_wrapped_accessor")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def wrapping_ttl(self) -> typing.Optional[builtins.str]:
        '''The TTL duration of the wrapped SecretID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/approle_auth_backend_role_secret_id#wrapping_ttl ApproleAuthBackendRoleSecretId#wrapping_ttl}
        '''
        result = self._values.get("wrapping_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApproleAuthBackendRoleSecretIdConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApproleAuthBackendRoleSecretId",
    "ApproleAuthBackendRoleSecretIdConfig",
]

publication.publish()

def _typecheckingstub__c2adf1e9bcf6dae03b68ab233df1e00e52977736a51c8e89d667b550d294ac58(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    role_name: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    cidr_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    metadata: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    num_uses: typing.Optional[jsii.Number] = None,
    secret_id: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    with_wrapped_accessor: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    wrapping_ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__172c8c8464a25cc33f7fb4a9f34f047f93eec3654d33b120e24f4951e0747245(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17201cf952ac38c026fb696cc2d158d106aa69ffe74c715bd838d6ea29c0438a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5806fa35c7cdfd03895088230f6b80a4f2023473067aeebf1633004626e775f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81a454b52d37b612081c4582740a620009173eccf16bedac6d0abd04a9de2f02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f78a9ed5ff9824172691cc17b227a39af2518d46b0bbd79b3f4a9b0830c7144(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5756ba949b87d6b556f601cb2023770332b3eac5226c156ff80856271b6c1206(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfe7de60911b27509042f9418c51414663efb250c0da2784f337db2960d7438e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1cb45649e9df1bf3486d45dc8c62d7ae3b852e3df33bacdf181edc184ab2b87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e1368ef247657555561cc6785f5eb7abc33592756c64df097550eb4ad68872f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ff2db674a0c9b06cadc20309485c55c13224326045f69d632bdc3bf070116e4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7f6895cf03c1b0902a7ac0c3a7e5bfd11954f49b8fbf39be3469f7c89a08ce0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0110aad99f3b9690405df671533a4dc77ec42736d29cd6c9056fe2ac3a097bdd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398d9313da8923f3686c46e15e84f9e0673d56bf3bb2a4a482c64707021c6ce2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    role_name: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    cidr_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    metadata: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    num_uses: typing.Optional[jsii.Number] = None,
    secret_id: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    with_wrapped_accessor: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    wrapping_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
