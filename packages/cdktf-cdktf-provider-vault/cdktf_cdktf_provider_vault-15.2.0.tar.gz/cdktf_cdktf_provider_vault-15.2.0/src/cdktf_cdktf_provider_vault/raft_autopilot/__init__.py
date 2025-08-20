r'''
# `vault_raft_autopilot`

Refer to the Terraform Registry for docs: [`vault_raft_autopilot`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot).
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


class RaftAutopilot(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.raftAutopilot.RaftAutopilot",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot vault_raft_autopilot}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cleanup_dead_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dead_server_last_contact_threshold: typing.Optional[builtins.str] = None,
        disable_upgrade_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        last_contact_threshold: typing.Optional[builtins.str] = None,
        max_trailing_logs: typing.Optional[jsii.Number] = None,
        min_quorum: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        server_stabilization_time: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot vault_raft_autopilot} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cleanup_dead_servers: Specifies whether to remove dead server nodes periodically or when a new server joins. This requires that min-quorum is also set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#cleanup_dead_servers RaftAutopilot#cleanup_dead_servers}
        :param dead_server_last_contact_threshold: Limit the amount of time a server can go without leader contact before being considered failed. This only takes effect when cleanup_dead_servers is set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#dead_server_last_contact_threshold RaftAutopilot#dead_server_last_contact_threshold}
        :param disable_upgrade_migration: Disables automatically upgrading Vault using autopilot. (Enterprise-only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#disable_upgrade_migration RaftAutopilot#disable_upgrade_migration}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#id RaftAutopilot#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param last_contact_threshold: Limit the amount of time a server can go without leader contact before being considered unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#last_contact_threshold RaftAutopilot#last_contact_threshold}
        :param max_trailing_logs: Maximum number of log entries in the Raft log that a server can be behind its leader before being considered unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#max_trailing_logs RaftAutopilot#max_trailing_logs}
        :param min_quorum: Minimum number of servers allowed in a cluster before autopilot can prune dead servers. This should at least be 3. Applicable only for voting nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#min_quorum RaftAutopilot#min_quorum}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#namespace RaftAutopilot#namespace}
        :param server_stabilization_time: Minimum amount of time a server must be stable in the 'healthy' state before being added to the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#server_stabilization_time RaftAutopilot#server_stabilization_time}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96590e2db801d9028a7b377732d622d508452cb1161561fde97649509cc90c67)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RaftAutopilotConfig(
            cleanup_dead_servers=cleanup_dead_servers,
            dead_server_last_contact_threshold=dead_server_last_contact_threshold,
            disable_upgrade_migration=disable_upgrade_migration,
            id=id,
            last_contact_threshold=last_contact_threshold,
            max_trailing_logs=max_trailing_logs,
            min_quorum=min_quorum,
            namespace=namespace,
            server_stabilization_time=server_stabilization_time,
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
        '''Generates CDKTF code for importing a RaftAutopilot resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RaftAutopilot to import.
        :param import_from_id: The id of the existing RaftAutopilot that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RaftAutopilot to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2931372607e1e13d7d78a94f2afdd309363da7868a90f0ed72a4b85f146cb828)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCleanupDeadServers")
    def reset_cleanup_dead_servers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCleanupDeadServers", []))

    @jsii.member(jsii_name="resetDeadServerLastContactThreshold")
    def reset_dead_server_last_contact_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeadServerLastContactThreshold", []))

    @jsii.member(jsii_name="resetDisableUpgradeMigration")
    def reset_disable_upgrade_migration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableUpgradeMigration", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLastContactThreshold")
    def reset_last_contact_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastContactThreshold", []))

    @jsii.member(jsii_name="resetMaxTrailingLogs")
    def reset_max_trailing_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTrailingLogs", []))

    @jsii.member(jsii_name="resetMinQuorum")
    def reset_min_quorum(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinQuorum", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetServerStabilizationTime")
    def reset_server_stabilization_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerStabilizationTime", []))

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
    @jsii.member(jsii_name="cleanupDeadServersInput")
    def cleanup_dead_servers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cleanupDeadServersInput"))

    @builtins.property
    @jsii.member(jsii_name="deadServerLastContactThresholdInput")
    def dead_server_last_contact_threshold_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deadServerLastContactThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="disableUpgradeMigrationInput")
    def disable_upgrade_migration_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableUpgradeMigrationInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="lastContactThresholdInput")
    def last_contact_threshold_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastContactThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTrailingLogsInput")
    def max_trailing_logs_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTrailingLogsInput"))

    @builtins.property
    @jsii.member(jsii_name="minQuorumInput")
    def min_quorum_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minQuorumInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="serverStabilizationTimeInput")
    def server_stabilization_time_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverStabilizationTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="cleanupDeadServers")
    def cleanup_dead_servers(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cleanupDeadServers"))

    @cleanup_dead_servers.setter
    def cleanup_dead_servers(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecf469deaa74bc0a7ff8a006ed72166a3039a4993363e0d9f0fc0d1df880289c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cleanupDeadServers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deadServerLastContactThreshold")
    def dead_server_last_contact_threshold(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deadServerLastContactThreshold"))

    @dead_server_last_contact_threshold.setter
    def dead_server_last_contact_threshold(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b271943a884d489c6b9c419d323613564fe822b3f3aecc0412321049805829)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deadServerLastContactThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableUpgradeMigration")
    def disable_upgrade_migration(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableUpgradeMigration"))

    @disable_upgrade_migration.setter
    def disable_upgrade_migration(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d107292c74bf5c3d4de48a211f4a082d3bcc170c7885271ec51bc21cfe962dd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableUpgradeMigration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f3c566611351b781fe9846c0e87286f85ecf5188e5918910c146cdf1add4b32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lastContactThreshold")
    def last_contact_threshold(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastContactThreshold"))

    @last_contact_threshold.setter
    def last_contact_threshold(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3ada04dedcb7df5de676916d32d02a38b479f1f819c6040f26f5332077bafd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lastContactThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTrailingLogs")
    def max_trailing_logs(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTrailingLogs"))

    @max_trailing_logs.setter
    def max_trailing_logs(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adf4af6ba6d2441582eb6e7e910adff6e350e41faeda499d2689898a4edddd82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTrailingLogs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minQuorum")
    def min_quorum(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minQuorum"))

    @min_quorum.setter
    def min_quorum(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331e0c557f5796c9ba038906890e2d8fac13372bb89e5c3fe0879251c7d35ca5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minQuorum", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efbd75240cab31f79fc327a0142473aac6c95f553e902e6dae7bf96a36a5af62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverStabilizationTime")
    def server_stabilization_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverStabilizationTime"))

    @server_stabilization_time.setter
    def server_stabilization_time(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1f016811aa032e0158d73fbd119a1e09b91179c02e821f93d1629c28a534e99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverStabilizationTime", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.raftAutopilot.RaftAutopilotConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cleanup_dead_servers": "cleanupDeadServers",
        "dead_server_last_contact_threshold": "deadServerLastContactThreshold",
        "disable_upgrade_migration": "disableUpgradeMigration",
        "id": "id",
        "last_contact_threshold": "lastContactThreshold",
        "max_trailing_logs": "maxTrailingLogs",
        "min_quorum": "minQuorum",
        "namespace": "namespace",
        "server_stabilization_time": "serverStabilizationTime",
    },
)
class RaftAutopilotConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cleanup_dead_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dead_server_last_contact_threshold: typing.Optional[builtins.str] = None,
        disable_upgrade_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        last_contact_threshold: typing.Optional[builtins.str] = None,
        max_trailing_logs: typing.Optional[jsii.Number] = None,
        min_quorum: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        server_stabilization_time: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cleanup_dead_servers: Specifies whether to remove dead server nodes periodically or when a new server joins. This requires that min-quorum is also set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#cleanup_dead_servers RaftAutopilot#cleanup_dead_servers}
        :param dead_server_last_contact_threshold: Limit the amount of time a server can go without leader contact before being considered failed. This only takes effect when cleanup_dead_servers is set. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#dead_server_last_contact_threshold RaftAutopilot#dead_server_last_contact_threshold}
        :param disable_upgrade_migration: Disables automatically upgrading Vault using autopilot. (Enterprise-only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#disable_upgrade_migration RaftAutopilot#disable_upgrade_migration}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#id RaftAutopilot#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param last_contact_threshold: Limit the amount of time a server can go without leader contact before being considered unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#last_contact_threshold RaftAutopilot#last_contact_threshold}
        :param max_trailing_logs: Maximum number of log entries in the Raft log that a server can be behind its leader before being considered unhealthy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#max_trailing_logs RaftAutopilot#max_trailing_logs}
        :param min_quorum: Minimum number of servers allowed in a cluster before autopilot can prune dead servers. This should at least be 3. Applicable only for voting nodes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#min_quorum RaftAutopilot#min_quorum}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#namespace RaftAutopilot#namespace}
        :param server_stabilization_time: Minimum amount of time a server must be stable in the 'healthy' state before being added to the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#server_stabilization_time RaftAutopilot#server_stabilization_time}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e618618284da4900f700673556a040be5aae2f1ed60280067d980a15bc12afeb)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cleanup_dead_servers", value=cleanup_dead_servers, expected_type=type_hints["cleanup_dead_servers"])
            check_type(argname="argument dead_server_last_contact_threshold", value=dead_server_last_contact_threshold, expected_type=type_hints["dead_server_last_contact_threshold"])
            check_type(argname="argument disable_upgrade_migration", value=disable_upgrade_migration, expected_type=type_hints["disable_upgrade_migration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument last_contact_threshold", value=last_contact_threshold, expected_type=type_hints["last_contact_threshold"])
            check_type(argname="argument max_trailing_logs", value=max_trailing_logs, expected_type=type_hints["max_trailing_logs"])
            check_type(argname="argument min_quorum", value=min_quorum, expected_type=type_hints["min_quorum"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument server_stabilization_time", value=server_stabilization_time, expected_type=type_hints["server_stabilization_time"])
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
        if cleanup_dead_servers is not None:
            self._values["cleanup_dead_servers"] = cleanup_dead_servers
        if dead_server_last_contact_threshold is not None:
            self._values["dead_server_last_contact_threshold"] = dead_server_last_contact_threshold
        if disable_upgrade_migration is not None:
            self._values["disable_upgrade_migration"] = disable_upgrade_migration
        if id is not None:
            self._values["id"] = id
        if last_contact_threshold is not None:
            self._values["last_contact_threshold"] = last_contact_threshold
        if max_trailing_logs is not None:
            self._values["max_trailing_logs"] = max_trailing_logs
        if min_quorum is not None:
            self._values["min_quorum"] = min_quorum
        if namespace is not None:
            self._values["namespace"] = namespace
        if server_stabilization_time is not None:
            self._values["server_stabilization_time"] = server_stabilization_time

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
    def cleanup_dead_servers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to remove dead server nodes periodically or when a new server joins.

        This requires that min-quorum is also set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#cleanup_dead_servers RaftAutopilot#cleanup_dead_servers}
        '''
        result = self._values.get("cleanup_dead_servers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dead_server_last_contact_threshold(self) -> typing.Optional[builtins.str]:
        '''Limit the amount of time a server can go without leader contact before being considered failed.

        This only takes effect when cleanup_dead_servers is set.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#dead_server_last_contact_threshold RaftAutopilot#dead_server_last_contact_threshold}
        '''
        result = self._values.get("dead_server_last_contact_threshold")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_upgrade_migration(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables automatically upgrading Vault using autopilot. (Enterprise-only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#disable_upgrade_migration RaftAutopilot#disable_upgrade_migration}
        '''
        result = self._values.get("disable_upgrade_migration")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#id RaftAutopilot#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_contact_threshold(self) -> typing.Optional[builtins.str]:
        '''Limit the amount of time a server can go without leader contact before being considered unhealthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#last_contact_threshold RaftAutopilot#last_contact_threshold}
        '''
        result = self._values.get("last_contact_threshold")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_trailing_logs(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of log entries in the Raft log that a server can be behind its leader before being considered unhealthy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#max_trailing_logs RaftAutopilot#max_trailing_logs}
        '''
        result = self._values.get("max_trailing_logs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_quorum(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of servers allowed in a cluster before autopilot can prune dead servers.

        This should at least be 3. Applicable only for voting nodes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#min_quorum RaftAutopilot#min_quorum}
        '''
        result = self._values.get("min_quorum")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#namespace RaftAutopilot#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_stabilization_time(self) -> typing.Optional[builtins.str]:
        '''Minimum amount of time a server must be stable in the 'healthy' state before being added to the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/raft_autopilot#server_stabilization_time RaftAutopilot#server_stabilization_time}
        '''
        result = self._values.get("server_stabilization_time")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RaftAutopilotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RaftAutopilot",
    "RaftAutopilotConfig",
]

publication.publish()

def _typecheckingstub__96590e2db801d9028a7b377732d622d508452cb1161561fde97649509cc90c67(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cleanup_dead_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dead_server_last_contact_threshold: typing.Optional[builtins.str] = None,
    disable_upgrade_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    last_contact_threshold: typing.Optional[builtins.str] = None,
    max_trailing_logs: typing.Optional[jsii.Number] = None,
    min_quorum: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    server_stabilization_time: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__2931372607e1e13d7d78a94f2afdd309363da7868a90f0ed72a4b85f146cb828(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecf469deaa74bc0a7ff8a006ed72166a3039a4993363e0d9f0fc0d1df880289c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b271943a884d489c6b9c419d323613564fe822b3f3aecc0412321049805829(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d107292c74bf5c3d4de48a211f4a082d3bcc170c7885271ec51bc21cfe962dd3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f3c566611351b781fe9846c0e87286f85ecf5188e5918910c146cdf1add4b32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3ada04dedcb7df5de676916d32d02a38b479f1f819c6040f26f5332077bafd0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adf4af6ba6d2441582eb6e7e910adff6e350e41faeda499d2689898a4edddd82(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331e0c557f5796c9ba038906890e2d8fac13372bb89e5c3fe0879251c7d35ca5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efbd75240cab31f79fc327a0142473aac6c95f553e902e6dae7bf96a36a5af62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f016811aa032e0158d73fbd119a1e09b91179c02e821f93d1629c28a534e99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e618618284da4900f700673556a040be5aae2f1ed60280067d980a15bc12afeb(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cleanup_dead_servers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dead_server_last_contact_threshold: typing.Optional[builtins.str] = None,
    disable_upgrade_migration: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    last_contact_threshold: typing.Optional[builtins.str] = None,
    max_trailing_logs: typing.Optional[jsii.Number] = None,
    min_quorum: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    server_stabilization_time: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
