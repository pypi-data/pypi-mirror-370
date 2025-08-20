r'''
# `data_vault_policy_document`

Refer to the Terraform Registry for docs: [`data_vault_policy_document`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document).
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


class DataVaultPolicyDocument(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocument",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document vault_policy_document}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataVaultPolicyDocumentRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document vault_policy_document} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#id DataVaultPolicyDocument#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#namespace DataVaultPolicyDocument#namespace}
        :param rule: rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#rule DataVaultPolicyDocument#rule}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47281c0cac287616e9dcf4fb19fa7cc7a9fb0fe62f63861350b802a7bcf2c6df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultPolicyDocumentConfig(
            id=id,
            namespace=namespace,
            rule=rule,
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
        '''Generates CDKTF code for importing a DataVaultPolicyDocument resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultPolicyDocument to import.
        :param import_from_id: The id of the existing DataVaultPolicyDocument that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultPolicyDocument to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d0514e59217bc694e60ebf6eea062e0b1f9244d008fb0641601011aeb73cc5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putRule")
    def put_rule(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataVaultPolicyDocumentRule", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__519935692e8b88310033eb9ee207458fbdbcb164470531c872ff0c25fd3dadc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRule", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRule")
    def reset_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRule", []))

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
    @jsii.member(jsii_name="hcl")
    def hcl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hcl"))

    @builtins.property
    @jsii.member(jsii_name="rule")
    def rule(self) -> "DataVaultPolicyDocumentRuleList":
        return typing.cast("DataVaultPolicyDocumentRuleList", jsii.get(self, "rule"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleInput")
    def rule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRule"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRule"]]], jsii.get(self, "ruleInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dabb3ef31bd6f61062945cc96ce77b605e6fa89c25faf24e5d9d308cdfdf781)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c186911a22d34ad5e9bf3743cd57416055383a1d160bd0f033021afd6acb002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "id": "id",
        "namespace": "namespace",
        "rule": "rule",
    },
)
class DataVaultPolicyDocumentConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataVaultPolicyDocumentRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#id DataVaultPolicyDocument#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#namespace DataVaultPolicyDocument#namespace}
        :param rule: rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#rule DataVaultPolicyDocument#rule}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__568e4b0e04bea1cee07689896a0c4ad7fcabf1bb628b15baf2eccc7fc20f565a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument rule", value=rule, expected_type=type_hints["rule"])
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
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if rule is not None:
            self._values["rule"] = rule

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#id DataVaultPolicyDocument#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#namespace DataVaultPolicyDocument#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rule(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRule"]]]:
        '''rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#rule DataVaultPolicyDocument#rule}
        '''
        result = self._values.get("rule")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRule"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultPolicyDocumentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRule",
    jsii_struct_bases=[],
    name_mapping={
        "capabilities": "capabilities",
        "path": "path",
        "allowed_parameter": "allowedParameter",
        "denied_parameter": "deniedParameter",
        "description": "description",
        "max_wrapping_ttl": "maxWrappingTtl",
        "min_wrapping_ttl": "minWrappingTtl",
        "required_parameters": "requiredParameters",
        "subscribe_event_types": "subscribeEventTypes",
    },
)
class DataVaultPolicyDocumentRule:
    def __init__(
        self,
        *,
        capabilities: typing.Sequence[builtins.str],
        path: builtins.str,
        allowed_parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataVaultPolicyDocumentRuleAllowedParameter", typing.Dict[builtins.str, typing.Any]]]]] = None,
        denied_parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataVaultPolicyDocumentRuleDeniedParameter", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        max_wrapping_ttl: typing.Optional[builtins.str] = None,
        min_wrapping_ttl: typing.Optional[builtins.str] = None,
        required_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        subscribe_event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param capabilities: A list of capabilities to apply to the specified path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#capabilities DataVaultPolicyDocument#capabilities}
        :param path: A path in Vault that this rule applies to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#path DataVaultPolicyDocument#path}
        :param allowed_parameter: allowed_parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#allowed_parameter DataVaultPolicyDocument#allowed_parameter}
        :param denied_parameter: denied_parameter block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#denied_parameter DataVaultPolicyDocument#denied_parameter}
        :param description: Description of the rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#description DataVaultPolicyDocument#description}
        :param max_wrapping_ttl: The maximum allowed TTL that clients can specify for a wrapped response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#max_wrapping_ttl DataVaultPolicyDocument#max_wrapping_ttl}
        :param min_wrapping_ttl: The minimum allowed TTL that clients can specify for a wrapped response. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#min_wrapping_ttl DataVaultPolicyDocument#min_wrapping_ttl}
        :param required_parameters: A list of parameters that must be specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#required_parameters DataVaultPolicyDocument#required_parameters}
        :param subscribe_event_types: A list of event types to subscribe to when using ``subscribe`` capability. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#subscribe_event_types DataVaultPolicyDocument#subscribe_event_types}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a124883181eebef185b15016820c8666131b30f49f2f4731d10d6ac9a931ce)
            check_type(argname="argument capabilities", value=capabilities, expected_type=type_hints["capabilities"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument allowed_parameter", value=allowed_parameter, expected_type=type_hints["allowed_parameter"])
            check_type(argname="argument denied_parameter", value=denied_parameter, expected_type=type_hints["denied_parameter"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument max_wrapping_ttl", value=max_wrapping_ttl, expected_type=type_hints["max_wrapping_ttl"])
            check_type(argname="argument min_wrapping_ttl", value=min_wrapping_ttl, expected_type=type_hints["min_wrapping_ttl"])
            check_type(argname="argument required_parameters", value=required_parameters, expected_type=type_hints["required_parameters"])
            check_type(argname="argument subscribe_event_types", value=subscribe_event_types, expected_type=type_hints["subscribe_event_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capabilities": capabilities,
            "path": path,
        }
        if allowed_parameter is not None:
            self._values["allowed_parameter"] = allowed_parameter
        if denied_parameter is not None:
            self._values["denied_parameter"] = denied_parameter
        if description is not None:
            self._values["description"] = description
        if max_wrapping_ttl is not None:
            self._values["max_wrapping_ttl"] = max_wrapping_ttl
        if min_wrapping_ttl is not None:
            self._values["min_wrapping_ttl"] = min_wrapping_ttl
        if required_parameters is not None:
            self._values["required_parameters"] = required_parameters
        if subscribe_event_types is not None:
            self._values["subscribe_event_types"] = subscribe_event_types

    @builtins.property
    def capabilities(self) -> typing.List[builtins.str]:
        '''A list of capabilities to apply to the specified path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#capabilities DataVaultPolicyDocument#capabilities}
        '''
        result = self._values.get("capabilities")
        assert result is not None, "Required property 'capabilities' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def path(self) -> builtins.str:
        '''A path in Vault that this rule applies to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#path DataVaultPolicyDocument#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_parameter(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRuleAllowedParameter"]]]:
        '''allowed_parameter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#allowed_parameter DataVaultPolicyDocument#allowed_parameter}
        '''
        result = self._values.get("allowed_parameter")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRuleAllowedParameter"]]], result)

    @builtins.property
    def denied_parameter(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRuleDeniedParameter"]]]:
        '''denied_parameter block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#denied_parameter DataVaultPolicyDocument#denied_parameter}
        '''
        result = self._values.get("denied_parameter")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataVaultPolicyDocumentRuleDeniedParameter"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#description DataVaultPolicyDocument#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_wrapping_ttl(self) -> typing.Optional[builtins.str]:
        '''The maximum allowed TTL that clients can specify for a wrapped response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#max_wrapping_ttl DataVaultPolicyDocument#max_wrapping_ttl}
        '''
        result = self._values.get("max_wrapping_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_wrapping_ttl(self) -> typing.Optional[builtins.str]:
        '''The minimum allowed TTL that clients can specify for a wrapped response.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#min_wrapping_ttl DataVaultPolicyDocument#min_wrapping_ttl}
        '''
        result = self._values.get("min_wrapping_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def required_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of parameters that must be specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#required_parameters DataVaultPolicyDocument#required_parameters}
        '''
        result = self._values.get("required_parameters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subscribe_event_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of event types to subscribe to when using ``subscribe`` capability.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#subscribe_event_types DataVaultPolicyDocument#subscribe_event_types}
        '''
        result = self._values.get("subscribe_event_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultPolicyDocumentRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleAllowedParameter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataVaultPolicyDocumentRuleAllowedParameter:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: Name of permitted key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#key DataVaultPolicyDocument#key}
        :param value: A list of values what are permitted by policy rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#value DataVaultPolicyDocument#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__152e48d18fdabfa445e69e886da67571c406ad6686582fe05d5448a69e4f9dc1)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Name of permitted key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#key DataVaultPolicyDocument#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.List[builtins.str]:
        '''A list of values what are permitted by policy rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#value DataVaultPolicyDocument#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultPolicyDocumentRuleAllowedParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataVaultPolicyDocumentRuleAllowedParameterList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleAllowedParameterList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa07529010321f81100e0bae4806570f2b73c37e4ba0a52edf51c57c59512134)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataVaultPolicyDocumentRuleAllowedParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2996b0623bf41bd79c8f81a50690aa1aa817d75bb36c22f7172864d09c8898cc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataVaultPolicyDocumentRuleAllowedParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdb84977322f870a7245b85c4329102c582bd420d0aaafe69e73983fb7bc7319)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef9b90f291f8fd5506819d98d12f00508fabf3fc8b4cb71e3556d74682e4e28c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b37702a50e83ae045b7e516c87e87df7afa42d0066b27d5233cd8b2559da4292)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleAllowedParameter]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleAllowedParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleAllowedParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f7ceb1cd7a05d33e7ef62bee59c55d5750759a17d00af49f1c27ed457b2ae62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataVaultPolicyDocumentRuleAllowedParameterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleAllowedParameterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64aed8a525a0a31d77ccc8ebcd73e2af6c071c0b87b95a6e78a36b4590125457)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc5dd1d7e1e30149a2a27289fc83ab56088d991205c1b37d873b26d2333b2107)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "value"))

    @value.setter
    def value(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6a0659007f1cbc5ac76e1c965ebbb78046febc235378d680628deade8eb6229)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleAllowedParameter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleAllowedParameter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleAllowedParameter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf058f44aac389b6719f4aa17a403e59065b21d7e91666ebf81f1d314a8e9dd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleDeniedParameter",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataVaultPolicyDocumentRuleDeniedParameter:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param key: Name of denied key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#key DataVaultPolicyDocument#key}
        :param value: A list of values what are denied by policy rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#value DataVaultPolicyDocument#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef0a8032ee5b9494b3ef8adf967d6d590c4e4210cbd6cea18e080ed2b001de6a)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Name of denied key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#key DataVaultPolicyDocument#key}
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.List[builtins.str]:
        '''A list of values what are denied by policy rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/policy_document#value DataVaultPolicyDocument#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultPolicyDocumentRuleDeniedParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataVaultPolicyDocumentRuleDeniedParameterList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleDeniedParameterList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2cafe1f16fdf56690e2fd4bbc61b3a46923a01dda5f55c0602cb4de53f3f186d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataVaultPolicyDocumentRuleDeniedParameterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5b3a1581c7a1173bd1702f8ba0676c37721500f996d95007c10afb66be6c28a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataVaultPolicyDocumentRuleDeniedParameterOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f44d0f3d158118facd60ceb1092a08ea32c472bb4126dcd15c9c4ddf977b6bf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f428094f06cdb7ede22c58be5a6856672771ac1b092c71168a8b2fe94ad04e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a770588c56c8377ed8bd3999b206fd74012f6964d92d8f015250fb025617c888)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleDeniedParameter]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleDeniedParameter]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleDeniedParameter]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c82c3e1576d88ef852c2323482e2efa172e53a0080171e43042e3654471575bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataVaultPolicyDocumentRuleDeniedParameterOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleDeniedParameterOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a38909df09ecd5b802ca2d6a765aef9160c8dd6826808a12e4bddb1e35622a61)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f2999f0567b16def0c69e5c9e9695e162aa77d63ad4cd2258f27d815524226a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "value"))

    @value.setter
    def value(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b03df7fa6db6113b87e00bab83ae6dedbf6b99657864bcdc3c05bc1165b33f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleDeniedParameter]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleDeniedParameter]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleDeniedParameter]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5511372ca5a4ecf6c8d6389262ee83a3545b708fffc3139cedc60f5e5e5dbe7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataVaultPolicyDocumentRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0757bc9fa642ea5ee72ade2b5fd1e1f1e6be0399e0124f3a4af300bdff19b128)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataVaultPolicyDocumentRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1520e9c4ec2755b7eeab1f0fa515ba9d077d590ded076978a19b32b4d5f31b18)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataVaultPolicyDocumentRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93eeda866ba61388baf09b44f5e18d5bcae927b383b65319b38e86189d8ed2f7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__63e7d6bac498e30344aab0cad2e767934179218e31bb46ef11a0aa197c4be381)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6618c2b0ffe180f482915cbe8fa6e004743227abe58d2272767118c401a147b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRule]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8c0cb65af37ea924748070696d0f5daf2807f60efe7afe85a74ccf117c5d721)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataVaultPolicyDocumentRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultPolicyDocument.DataVaultPolicyDocumentRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a68659a3d6c6a0ce640e8a55d3cd93f365c78759c33bb796a56cdcfc059dcf2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAllowedParameter")
    def put_allowed_parameter(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRuleAllowedParameter, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abd2142fb484530edb8bc1301252be9480ddd41aa949ed0eac5a45bb3b0900bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAllowedParameter", [value]))

    @jsii.member(jsii_name="putDeniedParameter")
    def put_denied_parameter(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRuleDeniedParameter, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b4d2a2ab521926fb2b319ebfe9b97dc3f71804c05d16a7064c5648a0ad80893)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDeniedParameter", [value]))

    @jsii.member(jsii_name="resetAllowedParameter")
    def reset_allowed_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedParameter", []))

    @jsii.member(jsii_name="resetDeniedParameter")
    def reset_denied_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeniedParameter", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetMaxWrappingTtl")
    def reset_max_wrapping_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWrappingTtl", []))

    @jsii.member(jsii_name="resetMinWrappingTtl")
    def reset_min_wrapping_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinWrappingTtl", []))

    @jsii.member(jsii_name="resetRequiredParameters")
    def reset_required_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredParameters", []))

    @jsii.member(jsii_name="resetSubscribeEventTypes")
    def reset_subscribe_event_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscribeEventTypes", []))

    @builtins.property
    @jsii.member(jsii_name="allowedParameter")
    def allowed_parameter(self) -> DataVaultPolicyDocumentRuleAllowedParameterList:
        return typing.cast(DataVaultPolicyDocumentRuleAllowedParameterList, jsii.get(self, "allowedParameter"))

    @builtins.property
    @jsii.member(jsii_name="deniedParameter")
    def denied_parameter(self) -> DataVaultPolicyDocumentRuleDeniedParameterList:
        return typing.cast(DataVaultPolicyDocumentRuleDeniedParameterList, jsii.get(self, "deniedParameter"))

    @builtins.property
    @jsii.member(jsii_name="allowedParameterInput")
    def allowed_parameter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleAllowedParameter]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleAllowedParameter]]], jsii.get(self, "allowedParameterInput"))

    @builtins.property
    @jsii.member(jsii_name="capabilitiesInput")
    def capabilities_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "capabilitiesInput"))

    @builtins.property
    @jsii.member(jsii_name="deniedParameterInput")
    def denied_parameter_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleDeniedParameter]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleDeniedParameter]]], jsii.get(self, "deniedParameterInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWrappingTtlInput")
    def max_wrapping_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxWrappingTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="minWrappingTtlInput")
    def min_wrapping_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minWrappingTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredParametersInput")
    def required_parameters_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "requiredParametersInput"))

    @builtins.property
    @jsii.member(jsii_name="subscribeEventTypesInput")
    def subscribe_event_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subscribeEventTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capabilities"))

    @capabilities.setter
    def capabilities(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16dfd7332569484488a929caaca154f5be0679ce5008258bc3b12de40367aaa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capabilities", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd3ceb8482a7773bbea5bbc2babb11130a45977ccb4fcc0289219ddfc1f0426c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxWrappingTtl")
    def max_wrapping_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxWrappingTtl"))

    @max_wrapping_ttl.setter
    def max_wrapping_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__915dd56f1728fb114a1f50103dff02332133a01b4fa301d64ca17c1cd6626f4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWrappingTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minWrappingTtl")
    def min_wrapping_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minWrappingTtl"))

    @min_wrapping_ttl.setter
    def min_wrapping_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2606f89d97f328d576a89b26dd0f57d83c4720e179ff7a68b36520c336daa97c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minWrappingTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dbafb93c042e237b35f323f4df3ea3087fb2efc29272440edd81b1edf5f440c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requiredParameters")
    def required_parameters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "requiredParameters"))

    @required_parameters.setter
    def required_parameters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8ce9ed9ba4cb20e1bd2e522bfbaaf5173e953e63aa58450a10f1c4c46d38af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredParameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscribeEventTypes")
    def subscribe_event_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subscribeEventTypes"))

    @subscribe_event_types.setter
    def subscribe_event_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dc6c8a572857a65dcd143cd22f1f78d6d05f1be99dc69dec7b51f31e6fda392)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscribeEventTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de92045b6c27f09935a279e6f4df940628a33e1fb5c208d955f98be5e72947ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataVaultPolicyDocument",
    "DataVaultPolicyDocumentConfig",
    "DataVaultPolicyDocumentRule",
    "DataVaultPolicyDocumentRuleAllowedParameter",
    "DataVaultPolicyDocumentRuleAllowedParameterList",
    "DataVaultPolicyDocumentRuleAllowedParameterOutputReference",
    "DataVaultPolicyDocumentRuleDeniedParameter",
    "DataVaultPolicyDocumentRuleDeniedParameterList",
    "DataVaultPolicyDocumentRuleDeniedParameterOutputReference",
    "DataVaultPolicyDocumentRuleList",
    "DataVaultPolicyDocumentRuleOutputReference",
]

publication.publish()

def _typecheckingstub__47281c0cac287616e9dcf4fb19fa7cc7a9fb0fe62f63861350b802a7bcf2c6df(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__51d0514e59217bc694e60ebf6eea062e0b1f9244d008fb0641601011aeb73cc5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__519935692e8b88310033eb9ee207458fbdbcb164470531c872ff0c25fd3dadc5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRule, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dabb3ef31bd6f61062945cc96ce77b605e6fa89c25faf24e5d9d308cdfdf781(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c186911a22d34ad5e9bf3743cd57416055383a1d160bd0f033021afd6acb002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__568e4b0e04bea1cee07689896a0c4ad7fcabf1bb628b15baf2eccc7fc20f565a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a124883181eebef185b15016820c8666131b30f49f2f4731d10d6ac9a931ce(
    *,
    capabilities: typing.Sequence[builtins.str],
    path: builtins.str,
    allowed_parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRuleAllowedParameter, typing.Dict[builtins.str, typing.Any]]]]] = None,
    denied_parameter: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRuleDeniedParameter, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    max_wrapping_ttl: typing.Optional[builtins.str] = None,
    min_wrapping_ttl: typing.Optional[builtins.str] = None,
    required_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
    subscribe_event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__152e48d18fdabfa445e69e886da67571c406ad6686582fe05d5448a69e4f9dc1(
    *,
    key: builtins.str,
    value: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa07529010321f81100e0bae4806570f2b73c37e4ba0a52edf51c57c59512134(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2996b0623bf41bd79c8f81a50690aa1aa817d75bb36c22f7172864d09c8898cc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdb84977322f870a7245b85c4329102c582bd420d0aaafe69e73983fb7bc7319(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef9b90f291f8fd5506819d98d12f00508fabf3fc8b4cb71e3556d74682e4e28c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b37702a50e83ae045b7e516c87e87df7afa42d0066b27d5233cd8b2559da4292(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f7ceb1cd7a05d33e7ef62bee59c55d5750759a17d00af49f1c27ed457b2ae62(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleAllowedParameter]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64aed8a525a0a31d77ccc8ebcd73e2af6c071c0b87b95a6e78a36b4590125457(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc5dd1d7e1e30149a2a27289fc83ab56088d991205c1b37d873b26d2333b2107(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6a0659007f1cbc5ac76e1c965ebbb78046febc235378d680628deade8eb6229(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf058f44aac389b6719f4aa17a403e59065b21d7e91666ebf81f1d314a8e9dd5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleAllowedParameter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef0a8032ee5b9494b3ef8adf967d6d590c4e4210cbd6cea18e080ed2b001de6a(
    *,
    key: builtins.str,
    value: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cafe1f16fdf56690e2fd4bbc61b3a46923a01dda5f55c0602cb4de53f3f186d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5b3a1581c7a1173bd1702f8ba0676c37721500f996d95007c10afb66be6c28a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f44d0f3d158118facd60ceb1092a08ea32c472bb4126dcd15c9c4ddf977b6bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f428094f06cdb7ede22c58be5a6856672771ac1b092c71168a8b2fe94ad04e5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a770588c56c8377ed8bd3999b206fd74012f6964d92d8f015250fb025617c888(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c82c3e1576d88ef852c2323482e2efa172e53a0080171e43042e3654471575bd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRuleDeniedParameter]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38909df09ecd5b802ca2d6a765aef9160c8dd6826808a12e4bddb1e35622a61(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f2999f0567b16def0c69e5c9e9695e162aa77d63ad4cd2258f27d815524226a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b03df7fa6db6113b87e00bab83ae6dedbf6b99657864bcdc3c05bc1165b33f2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5511372ca5a4ecf6c8d6389262ee83a3545b708fffc3139cedc60f5e5e5dbe7c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRuleDeniedParameter]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0757bc9fa642ea5ee72ade2b5fd1e1f1e6be0399e0124f3a4af300bdff19b128(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1520e9c4ec2755b7eeab1f0fa515ba9d077d590ded076978a19b32b4d5f31b18(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93eeda866ba61388baf09b44f5e18d5bcae927b383b65319b38e86189d8ed2f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e7d6bac498e30344aab0cad2e767934179218e31bb46ef11a0aa197c4be381(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6618c2b0ffe180f482915cbe8fa6e004743227abe58d2272767118c401a147b0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8c0cb65af37ea924748070696d0f5daf2807f60efe7afe85a74ccf117c5d721(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataVaultPolicyDocumentRule]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a68659a3d6c6a0ce640e8a55d3cd93f365c78759c33bb796a56cdcfc059dcf2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abd2142fb484530edb8bc1301252be9480ddd41aa949ed0eac5a45bb3b0900bf(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRuleAllowedParameter, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b4d2a2ab521926fb2b319ebfe9b97dc3f71804c05d16a7064c5648a0ad80893(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataVaultPolicyDocumentRuleDeniedParameter, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16dfd7332569484488a929caaca154f5be0679ce5008258bc3b12de40367aaa7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd3ceb8482a7773bbea5bbc2babb11130a45977ccb4fcc0289219ddfc1f0426c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__915dd56f1728fb114a1f50103dff02332133a01b4fa301d64ca17c1cd6626f4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2606f89d97f328d576a89b26dd0f57d83c4720e179ff7a68b36520c336daa97c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dbafb93c042e237b35f323f4df3ea3087fb2efc29272440edd81b1edf5f440c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8ce9ed9ba4cb20e1bd2e522bfbaaf5173e953e63aa58450a10f1c4c46d38af8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dc6c8a572857a65dcd143cd22f1f78d6d05f1be99dc69dec7b51f31e6fda392(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de92045b6c27f09935a279e6f4df940628a33e1fb5c208d955f98be5e72947ee(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataVaultPolicyDocumentRule]],
) -> None:
    """Type checking stubs"""
    pass
