r'''
# `vault_consul_secret_backend_role`

Refer to the Terraform Registry for docs: [`vault_consul_secret_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role).
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


class ConsulSecretBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.consulSecretBackendRole.ConsulSecretBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role vault_consul_secret_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        consul_namespace: typing.Optional[builtins.str] = None,
        consul_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        consul_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        node_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
        partition: typing.Optional[builtins.str] = None,
        policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role vault_consul_secret_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of an existing role against which to create this Consul credential. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#name ConsulSecretBackendRole#name}
        :param backend: The path of the Consul Secret Backend the role belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#backend ConsulSecretBackendRole#backend}
        :param consul_namespace: The Consul namespace that the token will be created in. Applicable for Vault 1.10+ and Consul 1.7+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_namespace ConsulSecretBackendRole#consul_namespace}
        :param consul_policies: List of Consul policies to associate with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_policies ConsulSecretBackendRole#consul_policies}
        :param consul_roles: Set of Consul roles to attach to the token. Applicable for Vault 1.10+ with Consul 1.5+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_roles ConsulSecretBackendRole#consul_roles}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#id ConsulSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param local: Indicates that the token should not be replicated globally and instead be local to the current datacenter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#local ConsulSecretBackendRole#local}
        :param max_ttl: Maximum TTL for leases associated with this role, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#max_ttl ConsulSecretBackendRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#namespace ConsulSecretBackendRole#namespace}
        :param node_identities: Set of Consul node identities to attach to the token. Applicable for Vault 1.11+ with Consul 1.8+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#node_identities ConsulSecretBackendRole#node_identities}
        :param partition: The Consul admin partition that the token will be created in. Applicable for Vault 1.10+ and Consul 1.11+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#partition ConsulSecretBackendRole#partition}
        :param policies: List of Consul policies to associate with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#policies ConsulSecretBackendRole#policies}
        :param service_identities: Set of Consul service identities to attach to the token. Applicable for Vault 1.11+ with Consul 1.5+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#service_identities ConsulSecretBackendRole#service_identities}
        :param ttl: Specifies the TTL for this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#ttl ConsulSecretBackendRole#ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c87e893cfec863dc67427e0ea6c76aa44c3f3dc72964580d80fe09e7934d8c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ConsulSecretBackendRoleConfig(
            name=name,
            backend=backend,
            consul_namespace=consul_namespace,
            consul_policies=consul_policies,
            consul_roles=consul_roles,
            id=id,
            local=local,
            max_ttl=max_ttl,
            namespace=namespace,
            node_identities=node_identities,
            partition=partition,
            policies=policies,
            service_identities=service_identities,
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
        '''Generates CDKTF code for importing a ConsulSecretBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ConsulSecretBackendRole to import.
        :param import_from_id: The id of the existing ConsulSecretBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ConsulSecretBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4ebf9e4da83c89cdde54e496dea92f8954323840fc3f33221e91332ac62d389)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetConsulNamespace")
    def reset_consul_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsulNamespace", []))

    @jsii.member(jsii_name="resetConsulPolicies")
    def reset_consul_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsulPolicies", []))

    @jsii.member(jsii_name="resetConsulRoles")
    def reset_consul_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsulRoles", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLocal")
    def reset_local(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocal", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNodeIdentities")
    def reset_node_identities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeIdentities", []))

    @jsii.member(jsii_name="resetPartition")
    def reset_partition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartition", []))

    @jsii.member(jsii_name="resetPolicies")
    def reset_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicies", []))

    @jsii.member(jsii_name="resetServiceIdentities")
    def reset_service_identities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceIdentities", []))

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
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="consulNamespaceInput")
    def consul_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consulNamespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="consulPoliciesInput")
    def consul_policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "consulPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="consulRolesInput")
    def consul_roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "consulRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="localInput")
    def local_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "localInput"))

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
    @jsii.member(jsii_name="nodeIdentitiesInput")
    def node_identities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "nodeIdentitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionInput")
    def partition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "partitionInput"))

    @builtins.property
    @jsii.member(jsii_name="policiesInput")
    def policies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "policiesInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceIdentitiesInput")
    def service_identities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "serviceIdentitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b793634e9b860f8753763555f73d7fb360f589cad8568546bc5374f4a44d589)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consulNamespace")
    def consul_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "consulNamespace"))

    @consul_namespace.setter
    def consul_namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4518bb1ea7f0fe589063cf46ba6d214445536d40471d4dd1b1de273c1dc900f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consulNamespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consulPolicies")
    def consul_policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "consulPolicies"))

    @consul_policies.setter
    def consul_policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6359eb0f6957a10bd7a26faec4c1ed60fcbb206630b1f4c313218f1151400bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consulPolicies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consulRoles")
    def consul_roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "consulRoles"))

    @consul_roles.setter
    def consul_roles(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__720245f29442b3beeb304959e92496f752bbcb900a5fc0545b469e1400a8ad84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consulRoles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710b6b84ec2058aa30d79b3b19cdafe7e663cc98332d1c11b47e63c64453e942)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="local")
    def local(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "local"))

    @local.setter
    def local(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f4b280650b79e2e0a09490fa41aa73f0641243f4bd3241773b0ebc63df8e518)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "local", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcc7b1ace984edc0023553b641c1aea90851a8015d2c68afc7d6c33e7c807426)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ea5421c5831cdc8a8102ebf95aa8c25e84292974ad94ab139dd16ca18816ef8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6619345365d5fca29852a9d80a8baa1a478c5e9eaa20156bfe50ad962102a75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeIdentities")
    def node_identities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nodeIdentities"))

    @node_identities.setter
    def node_identities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57756575af1431e643eccb2f0ab7ce2cc218d516a411b9387660f4289a047f77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeIdentities", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partition")
    def partition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "partition"))

    @partition.setter
    def partition(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a967326e331f8c6b122ece44736340b332b409b27e113700b4a3d5661d3aec07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partition", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "policies"))

    @policies.setter
    def policies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__609b7f6cb8821a0f89306b8af85f03f0131fec2e0d52600c8b719a872ff553a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceIdentities")
    def service_identities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "serviceIdentities"))

    @service_identities.setter
    def service_identities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__425f4e478387e693cec37a5a2ac7bbe569c0b1df394c00b92fe8e09bb7107ddf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceIdentities", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc261ba534d9d904686babbb899d8fa5aca6701069230ce6e05701a14734099)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.consulSecretBackendRole.ConsulSecretBackendRoleConfig",
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
        "consul_namespace": "consulNamespace",
        "consul_policies": "consulPolicies",
        "consul_roles": "consulRoles",
        "id": "id",
        "local": "local",
        "max_ttl": "maxTtl",
        "namespace": "namespace",
        "node_identities": "nodeIdentities",
        "partition": "partition",
        "policies": "policies",
        "service_identities": "serviceIdentities",
        "ttl": "ttl",
    },
)
class ConsulSecretBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        consul_namespace: typing.Optional[builtins.str] = None,
        consul_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        consul_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        node_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
        partition: typing.Optional[builtins.str] = None,
        policies: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
        ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: The name of an existing role against which to create this Consul credential. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#name ConsulSecretBackendRole#name}
        :param backend: The path of the Consul Secret Backend the role belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#backend ConsulSecretBackendRole#backend}
        :param consul_namespace: The Consul namespace that the token will be created in. Applicable for Vault 1.10+ and Consul 1.7+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_namespace ConsulSecretBackendRole#consul_namespace}
        :param consul_policies: List of Consul policies to associate with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_policies ConsulSecretBackendRole#consul_policies}
        :param consul_roles: Set of Consul roles to attach to the token. Applicable for Vault 1.10+ with Consul 1.5+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_roles ConsulSecretBackendRole#consul_roles}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#id ConsulSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param local: Indicates that the token should not be replicated globally and instead be local to the current datacenter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#local ConsulSecretBackendRole#local}
        :param max_ttl: Maximum TTL for leases associated with this role, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#max_ttl ConsulSecretBackendRole#max_ttl}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#namespace ConsulSecretBackendRole#namespace}
        :param node_identities: Set of Consul node identities to attach to the token. Applicable for Vault 1.11+ with Consul 1.8+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#node_identities ConsulSecretBackendRole#node_identities}
        :param partition: The Consul admin partition that the token will be created in. Applicable for Vault 1.10+ and Consul 1.11+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#partition ConsulSecretBackendRole#partition}
        :param policies: List of Consul policies to associate with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#policies ConsulSecretBackendRole#policies}
        :param service_identities: Set of Consul service identities to attach to the token. Applicable for Vault 1.11+ with Consul 1.5+. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#service_identities ConsulSecretBackendRole#service_identities}
        :param ttl: Specifies the TTL for this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#ttl ConsulSecretBackendRole#ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c79b1f701c14be9ad268f2afb7e0e06529a7f134c478f6dc1998c33a0b988223)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument consul_namespace", value=consul_namespace, expected_type=type_hints["consul_namespace"])
            check_type(argname="argument consul_policies", value=consul_policies, expected_type=type_hints["consul_policies"])
            check_type(argname="argument consul_roles", value=consul_roles, expected_type=type_hints["consul_roles"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument local", value=local, expected_type=type_hints["local"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument node_identities", value=node_identities, expected_type=type_hints["node_identities"])
            check_type(argname="argument partition", value=partition, expected_type=type_hints["partition"])
            check_type(argname="argument policies", value=policies, expected_type=type_hints["policies"])
            check_type(argname="argument service_identities", value=service_identities, expected_type=type_hints["service_identities"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
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
        if consul_namespace is not None:
            self._values["consul_namespace"] = consul_namespace
        if consul_policies is not None:
            self._values["consul_policies"] = consul_policies
        if consul_roles is not None:
            self._values["consul_roles"] = consul_roles
        if id is not None:
            self._values["id"] = id
        if local is not None:
            self._values["local"] = local
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if namespace is not None:
            self._values["namespace"] = namespace
        if node_identities is not None:
            self._values["node_identities"] = node_identities
        if partition is not None:
            self._values["partition"] = partition
        if policies is not None:
            self._values["policies"] = policies
        if service_identities is not None:
            self._values["service_identities"] = service_identities
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
    def name(self) -> builtins.str:
        '''The name of an existing role against which to create this Consul credential.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#name ConsulSecretBackendRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''The path of the Consul Secret Backend the role belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#backend ConsulSecretBackendRole#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def consul_namespace(self) -> typing.Optional[builtins.str]:
        '''The Consul namespace that the token will be created in. Applicable for Vault 1.10+ and Consul 1.7+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_namespace ConsulSecretBackendRole#consul_namespace}
        '''
        result = self._values.get("consul_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def consul_policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Consul policies to associate with this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_policies ConsulSecretBackendRole#consul_policies}
        '''
        result = self._values.get("consul_policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def consul_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of Consul roles to attach to the token. Applicable for Vault 1.10+ with Consul 1.5+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#consul_roles ConsulSecretBackendRole#consul_roles}
        '''
        result = self._values.get("consul_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#id ConsulSecretBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates that the token should not be replicated globally and instead be local to the current datacenter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#local ConsulSecretBackendRole#local}
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Maximum TTL for leases associated with this role, in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#max_ttl ConsulSecretBackendRole#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#namespace ConsulSecretBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_identities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of Consul node identities to attach to 				the token. Applicable for Vault 1.11+ with Consul 1.8+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#node_identities ConsulSecretBackendRole#node_identities}
        '''
        result = self._values.get("node_identities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def partition(self) -> typing.Optional[builtins.str]:
        '''The Consul admin partition that the token will be created in. Applicable for Vault 1.10+ and Consul 1.11+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#partition ConsulSecretBackendRole#partition}
        '''
        result = self._values.get("partition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Consul policies to associate with this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#policies ConsulSecretBackendRole#policies}
        '''
        result = self._values.get("policies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_identities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of Consul service identities to attach to 				the token. Applicable for Vault 1.11+ with Consul 1.5+.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#service_identities ConsulSecretBackendRole#service_identities}
        '''
        result = self._values.get("service_identities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Specifies the TTL for this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/consul_secret_backend_role#ttl ConsulSecretBackendRole#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConsulSecretBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ConsulSecretBackendRole",
    "ConsulSecretBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__a4c87e893cfec863dc67427e0ea6c76aa44c3f3dc72964580d80fe09e7934d8c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    consul_namespace: typing.Optional[builtins.str] = None,
    consul_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    consul_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    node_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
    partition: typing.Optional[builtins.str] = None,
    policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__e4ebf9e4da83c89cdde54e496dea92f8954323840fc3f33221e91332ac62d389(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b793634e9b860f8753763555f73d7fb360f589cad8568546bc5374f4a44d589(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4518bb1ea7f0fe589063cf46ba6d214445536d40471d4dd1b1de273c1dc900f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6359eb0f6957a10bd7a26faec4c1ed60fcbb206630b1f4c313218f1151400bc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__720245f29442b3beeb304959e92496f752bbcb900a5fc0545b469e1400a8ad84(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710b6b84ec2058aa30d79b3b19cdafe7e663cc98332d1c11b47e63c64453e942(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f4b280650b79e2e0a09490fa41aa73f0641243f4bd3241773b0ebc63df8e518(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcc7b1ace984edc0023553b641c1aea90851a8015d2c68afc7d6c33e7c807426(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea5421c5831cdc8a8102ebf95aa8c25e84292974ad94ab139dd16ca18816ef8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6619345365d5fca29852a9d80a8baa1a478c5e9eaa20156bfe50ad962102a75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57756575af1431e643eccb2f0ab7ce2cc218d516a411b9387660f4289a047f77(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a967326e331f8c6b122ece44736340b332b409b27e113700b4a3d5661d3aec07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__609b7f6cb8821a0f89306b8af85f03f0131fec2e0d52600c8b719a872ff553a2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__425f4e478387e693cec37a5a2ac7bbe569c0b1df394c00b92fe8e09bb7107ddf(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbc261ba534d9d904686babbb899d8fa5aca6701069230ce6e05701a14734099(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c79b1f701c14be9ad268f2afb7e0e06529a7f134c478f6dc1998c33a0b988223(
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
    consul_namespace: typing.Optional[builtins.str] = None,
    consul_policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    consul_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    local: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    node_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
    partition: typing.Optional[builtins.str] = None,
    policies: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_identities: typing.Optional[typing.Sequence[builtins.str]] = None,
    ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
