r'''
# `data_vault_azure_access_credentials`

Refer to the Terraform Registry for docs: [`data_vault_azure_access_credentials`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials).
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


class DataVaultAzureAccessCredentials(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultAzureAccessCredentials.DataVaultAzureAccessCredentials",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials vault_azure_access_credentials}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        role: builtins.str,
        environment: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_cred_validation_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        num_seconds_between_tests: typing.Optional[jsii.Number] = None,
        num_sequential_successes: typing.Optional[jsii.Number] = None,
        subscription_id: typing.Optional[builtins.str] = None,
        tenant_id: typing.Optional[builtins.str] = None,
        validate_creds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials vault_azure_access_credentials} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: Azure Secret Backend to read credentials from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#backend DataVaultAzureAccessCredentials#backend}
        :param role: Azure Secret Role to read credentials from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#role DataVaultAzureAccessCredentials#role}
        :param environment: The Azure environment to use during credential validation. Defaults to the Azure Public Cloud. Some possible values: AzurePublicCloud, AzureUSGovernmentCloud. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#environment DataVaultAzureAccessCredentials#environment}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#id DataVaultAzureAccessCredentials#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_cred_validation_seconds: If 'validate_creds' is true, the number of seconds after which to give up validating credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#max_cred_validation_seconds DataVaultAzureAccessCredentials#max_cred_validation_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#namespace DataVaultAzureAccessCredentials#namespace}
        :param num_seconds_between_tests: If 'validate_creds' is true, the number of seconds to wait between each test of generated credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#num_seconds_between_tests DataVaultAzureAccessCredentials#num_seconds_between_tests}
        :param num_sequential_successes: If 'validate_creds' is true, the number of sequential successes required to validate generated credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#num_sequential_successes DataVaultAzureAccessCredentials#num_sequential_successes}
        :param subscription_id: The subscription ID to use during credential validation. Defaults to the subscription ID configured in the Vault backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#subscription_id DataVaultAzureAccessCredentials#subscription_id}
        :param tenant_id: The tenant ID to use during credential validation. Defaults to the tenant ID configured in the Vault backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#tenant_id DataVaultAzureAccessCredentials#tenant_id}
        :param validate_creds: Whether generated credentials should be validated before being returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#validate_creds DataVaultAzureAccessCredentials#validate_creds}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d2de0c3852fe047f32097dff0876b1ea5b1d6c361c58cee22049a232dc477e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultAzureAccessCredentialsConfig(
            backend=backend,
            role=role,
            environment=environment,
            id=id,
            max_cred_validation_seconds=max_cred_validation_seconds,
            namespace=namespace,
            num_seconds_between_tests=num_seconds_between_tests,
            num_sequential_successes=num_sequential_successes,
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            validate_creds=validate_creds,
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
        '''Generates CDKTF code for importing a DataVaultAzureAccessCredentials resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultAzureAccessCredentials to import.
        :param import_from_id: The id of the existing DataVaultAzureAccessCredentials that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultAzureAccessCredentials to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__162412cb1a1b63a91d03b7ef280aa17a0b0ff7de8eea688834c10b008e50818a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxCredValidationSeconds")
    def reset_max_cred_validation_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCredValidationSeconds", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNumSecondsBetweenTests")
    def reset_num_seconds_between_tests(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumSecondsBetweenTests", []))

    @jsii.member(jsii_name="resetNumSequentialSuccesses")
    def reset_num_sequential_successes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumSequentialSuccesses", []))

    @jsii.member(jsii_name="resetSubscriptionId")
    def reset_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionId", []))

    @jsii.member(jsii_name="resetTenantId")
    def reset_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTenantId", []))

    @jsii.member(jsii_name="resetValidateCreds")
    def reset_validate_creds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValidateCreds", []))

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
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property
    @jsii.member(jsii_name="leaseDuration")
    def lease_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "leaseDuration"))

    @builtins.property
    @jsii.member(jsii_name="leaseId")
    def lease_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "leaseId"))

    @builtins.property
    @jsii.member(jsii_name="leaseRenewable")
    def lease_renewable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "leaseRenewable"))

    @builtins.property
    @jsii.member(jsii_name="leaseStartTime")
    def lease_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "leaseStartTime"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCredValidationSecondsInput")
    def max_cred_validation_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCredValidationSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="numSecondsBetweenTestsInput")
    def num_seconds_between_tests_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numSecondsBetweenTestsInput"))

    @builtins.property
    @jsii.member(jsii_name="numSequentialSuccessesInput")
    def num_sequential_successes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numSequentialSuccessesInput"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tenantIdInput")
    def tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="validateCredsInput")
    def validate_creds_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "validateCredsInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a88793e13c336aa0fb18aca0e1d74bf24aaaa3a7dd3eb762bcc4eaef94cfc63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9640a3697697dce91943240442990d7119f1879f85ce308f4041d9edf94b17f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__233b919506e16e51fac18ba965cbb086cc53cb7726d206fa0ab364ceb3d3e35f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCredValidationSeconds")
    def max_cred_validation_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCredValidationSeconds"))

    @max_cred_validation_seconds.setter
    def max_cred_validation_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a39d9117aca7fed7fc4bfc3b92cc775ae063fa6c6a05698d6b1bfed9060a50ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCredValidationSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5002e8eb63b5796b3fa4a4080d2a5d40515246c9d0d32cd3e7ba1b5c1cdbeec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numSecondsBetweenTests")
    def num_seconds_between_tests(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numSecondsBetweenTests"))

    @num_seconds_between_tests.setter
    def num_seconds_between_tests(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c799687143a6c23b480dcfc240dd2e53c998a2e85c8a19c62fbccf83f70f0e1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numSecondsBetweenTests", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numSequentialSuccesses")
    def num_sequential_successes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numSequentialSuccesses"))

    @num_sequential_successes.setter
    def num_sequential_successes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96e97ff34c920481ec2f9f30f281c061773e0337f262d99ed968ad2530948e1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numSequentialSuccesses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baabd984d382ad5bae412e1c8106f6050e70f05b0a32745a941ad4ec1c2671ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00db86ea889a8ba2365f85bc5ccb7c8594890c315334510969eea7f03ffcb3f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tenantId")
    def tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenantId"))

    @tenant_id.setter
    def tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec5b3c755374a1ab915ec89789d66af1bd8eecb5e7fdf415df470bcc0dc74411)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="validateCreds")
    def validate_creds(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "validateCreds"))

    @validate_creds.setter
    def validate_creds(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8141cb1372b54a97579ab99924c3a39d9ba3884f283611e1a728ca9b4cbea4f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "validateCreds", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultAzureAccessCredentials.DataVaultAzureAccessCredentialsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "backend": "backend",
        "role": "role",
        "environment": "environment",
        "id": "id",
        "max_cred_validation_seconds": "maxCredValidationSeconds",
        "namespace": "namespace",
        "num_seconds_between_tests": "numSecondsBetweenTests",
        "num_sequential_successes": "numSequentialSuccesses",
        "subscription_id": "subscriptionId",
        "tenant_id": "tenantId",
        "validate_creds": "validateCreds",
    },
)
class DataVaultAzureAccessCredentialsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: builtins.str,
        role: builtins.str,
        environment: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_cred_validation_seconds: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        num_seconds_between_tests: typing.Optional[jsii.Number] = None,
        num_sequential_successes: typing.Optional[jsii.Number] = None,
        subscription_id: typing.Optional[builtins.str] = None,
        tenant_id: typing.Optional[builtins.str] = None,
        validate_creds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: Azure Secret Backend to read credentials from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#backend DataVaultAzureAccessCredentials#backend}
        :param role: Azure Secret Role to read credentials from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#role DataVaultAzureAccessCredentials#role}
        :param environment: The Azure environment to use during credential validation. Defaults to the Azure Public Cloud. Some possible values: AzurePublicCloud, AzureUSGovernmentCloud. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#environment DataVaultAzureAccessCredentials#environment}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#id DataVaultAzureAccessCredentials#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_cred_validation_seconds: If 'validate_creds' is true, the number of seconds after which to give up validating credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#max_cred_validation_seconds DataVaultAzureAccessCredentials#max_cred_validation_seconds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#namespace DataVaultAzureAccessCredentials#namespace}
        :param num_seconds_between_tests: If 'validate_creds' is true, the number of seconds to wait between each test of generated credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#num_seconds_between_tests DataVaultAzureAccessCredentials#num_seconds_between_tests}
        :param num_sequential_successes: If 'validate_creds' is true, the number of sequential successes required to validate generated credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#num_sequential_successes DataVaultAzureAccessCredentials#num_sequential_successes}
        :param subscription_id: The subscription ID to use during credential validation. Defaults to the subscription ID configured in the Vault backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#subscription_id DataVaultAzureAccessCredentials#subscription_id}
        :param tenant_id: The tenant ID to use during credential validation. Defaults to the tenant ID configured in the Vault backend. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#tenant_id DataVaultAzureAccessCredentials#tenant_id}
        :param validate_creds: Whether generated credentials should be validated before being returned. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#validate_creds DataVaultAzureAccessCredentials#validate_creds}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6dbdeba309b7f40c5fbfc8a37ae02588e22e2cc7cffe6a3cd2c36ad18c266dd)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_cred_validation_seconds", value=max_cred_validation_seconds, expected_type=type_hints["max_cred_validation_seconds"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument num_seconds_between_tests", value=num_seconds_between_tests, expected_type=type_hints["num_seconds_between_tests"])
            check_type(argname="argument num_sequential_successes", value=num_sequential_successes, expected_type=type_hints["num_sequential_successes"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
            check_type(argname="argument validate_creds", value=validate_creds, expected_type=type_hints["validate_creds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
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
        if environment is not None:
            self._values["environment"] = environment
        if id is not None:
            self._values["id"] = id
        if max_cred_validation_seconds is not None:
            self._values["max_cred_validation_seconds"] = max_cred_validation_seconds
        if namespace is not None:
            self._values["namespace"] = namespace
        if num_seconds_between_tests is not None:
            self._values["num_seconds_between_tests"] = num_seconds_between_tests
        if num_sequential_successes is not None:
            self._values["num_sequential_successes"] = num_sequential_successes
        if subscription_id is not None:
            self._values["subscription_id"] = subscription_id
        if tenant_id is not None:
            self._values["tenant_id"] = tenant_id
        if validate_creds is not None:
            self._values["validate_creds"] = validate_creds

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
    def backend(self) -> builtins.str:
        '''Azure Secret Backend to read credentials from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#backend DataVaultAzureAccessCredentials#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> builtins.str:
        '''Azure Secret Role to read credentials from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#role DataVaultAzureAccessCredentials#role}
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''The Azure environment to use during credential validation. Defaults to the Azure Public Cloud. Some possible values: AzurePublicCloud, AzureUSGovernmentCloud.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#environment DataVaultAzureAccessCredentials#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#id DataVaultAzureAccessCredentials#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_cred_validation_seconds(self) -> typing.Optional[jsii.Number]:
        '''If 'validate_creds' is true, the number of seconds after which to give up validating credentials.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#max_cred_validation_seconds DataVaultAzureAccessCredentials#max_cred_validation_seconds}
        '''
        result = self._values.get("max_cred_validation_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#namespace DataVaultAzureAccessCredentials#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_seconds_between_tests(self) -> typing.Optional[jsii.Number]:
        '''If 'validate_creds' is true, the number of seconds to wait between each test of generated credentials.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#num_seconds_between_tests DataVaultAzureAccessCredentials#num_seconds_between_tests}
        '''
        result = self._values.get("num_seconds_between_tests")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_sequential_successes(self) -> typing.Optional[jsii.Number]:
        '''If 'validate_creds' is true, the number of sequential successes required to validate generated credentials.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#num_sequential_successes DataVaultAzureAccessCredentials#num_sequential_successes}
        '''
        result = self._values.get("num_sequential_successes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subscription_id(self) -> typing.Optional[builtins.str]:
        '''The subscription ID to use during credential validation. Defaults to the subscription ID configured in the Vault backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#subscription_id DataVaultAzureAccessCredentials#subscription_id}
        '''
        result = self._values.get("subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tenant_id(self) -> typing.Optional[builtins.str]:
        '''The tenant ID to use during credential validation. Defaults to the tenant ID configured in the Vault backend.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#tenant_id DataVaultAzureAccessCredentials#tenant_id}
        '''
        result = self._values.get("tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def validate_creds(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether generated credentials should be validated before being returned.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/azure_access_credentials#validate_creds DataVaultAzureAccessCredentials#validate_creds}
        '''
        result = self._values.get("validate_creds")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultAzureAccessCredentialsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVaultAzureAccessCredentials",
    "DataVaultAzureAccessCredentialsConfig",
]

publication.publish()

def _typecheckingstub__59d2de0c3852fe047f32097dff0876b1ea5b1d6c361c58cee22049a232dc477e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    role: builtins.str,
    environment: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_cred_validation_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    num_seconds_between_tests: typing.Optional[jsii.Number] = None,
    num_sequential_successes: typing.Optional[jsii.Number] = None,
    subscription_id: typing.Optional[builtins.str] = None,
    tenant_id: typing.Optional[builtins.str] = None,
    validate_creds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__162412cb1a1b63a91d03b7ef280aa17a0b0ff7de8eea688834c10b008e50818a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a88793e13c336aa0fb18aca0e1d74bf24aaaa3a7dd3eb762bcc4eaef94cfc63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9640a3697697dce91943240442990d7119f1879f85ce308f4041d9edf94b17f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__233b919506e16e51fac18ba965cbb086cc53cb7726d206fa0ab364ceb3d3e35f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a39d9117aca7fed7fc4bfc3b92cc775ae063fa6c6a05698d6b1bfed9060a50ed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5002e8eb63b5796b3fa4a4080d2a5d40515246c9d0d32cd3e7ba1b5c1cdbeec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c799687143a6c23b480dcfc240dd2e53c998a2e85c8a19c62fbccf83f70f0e1a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96e97ff34c920481ec2f9f30f281c061773e0337f262d99ed968ad2530948e1b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baabd984d382ad5bae412e1c8106f6050e70f05b0a32745a941ad4ec1c2671ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00db86ea889a8ba2365f85bc5ccb7c8594890c315334510969eea7f03ffcb3f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec5b3c755374a1ab915ec89789d66af1bd8eecb5e7fdf415df470bcc0dc74411(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8141cb1372b54a97579ab99924c3a39d9ba3884f283611e1a728ca9b4cbea4f1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6dbdeba309b7f40c5fbfc8a37ae02588e22e2cc7cffe6a3cd2c36ad18c266dd(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    role: builtins.str,
    environment: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_cred_validation_seconds: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    num_seconds_between_tests: typing.Optional[jsii.Number] = None,
    num_sequential_successes: typing.Optional[jsii.Number] = None,
    subscription_id: typing.Optional[builtins.str] = None,
    tenant_id: typing.Optional[builtins.str] = None,
    validate_creds: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
