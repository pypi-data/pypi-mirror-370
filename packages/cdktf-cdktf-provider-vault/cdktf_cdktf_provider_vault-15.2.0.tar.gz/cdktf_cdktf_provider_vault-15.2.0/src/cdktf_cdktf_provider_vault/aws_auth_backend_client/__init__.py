r'''
# `vault_aws_auth_backend_client`

Refer to the Terraform Registry for docs: [`vault_aws_auth_backend_client`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client).
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


class AwsAuthBackendClient(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.awsAuthBackendClient.AwsAuthBackendClient",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client vault_aws_auth_backend_client}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        access_key: typing.Optional[builtins.str] = None,
        backend: typing.Optional[builtins.str] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ec2_endpoint: typing.Optional[builtins.str] = None,
        iam_endpoint: typing.Optional[builtins.str] = None,
        iam_server_id_header_value: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_audience: typing.Optional[builtins.str] = None,
        identity_token_ttl: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        secret_key: typing.Optional[builtins.str] = None,
        sts_endpoint: typing.Optional[builtins.str] = None,
        sts_region: typing.Optional[builtins.str] = None,
        use_sts_region_from_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client vault_aws_auth_backend_client} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_key: AWS Access key with permissions to query AWS APIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#access_key AwsAuthBackendClient#access_key}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#backend AwsAuthBackendClient#backend}
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#disable_automated_rotation AwsAuthBackendClient#disable_automated_rotation}
        :param ec2_endpoint: URL to override the default generated endpoint for making AWS EC2 API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#ec2_endpoint AwsAuthBackendClient#ec2_endpoint}
        :param iam_endpoint: URL to override the default generated endpoint for making AWS IAM API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#iam_endpoint AwsAuthBackendClient#iam_endpoint}
        :param iam_server_id_header_value: The value to require in the X-Vault-AWS-IAM-Server-ID header as part of GetCallerIdentity requests that are used in the iam auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#iam_server_id_header_value AwsAuthBackendClient#iam_server_id_header_value}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#id AwsAuthBackendClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_audience: The audience claim value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#identity_token_audience AwsAuthBackendClient#identity_token_audience}
        :param identity_token_ttl: The TTL of generated identity tokens in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#identity_token_ttl AwsAuthBackendClient#identity_token_ttl}
        :param max_retries: Number of max retries the client should use for recoverable errors. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#max_retries AwsAuthBackendClient#max_retries}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#namespace AwsAuthBackendClient#namespace}
        :param role_arn: Role ARN to assume for plugin identity token federation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#role_arn AwsAuthBackendClient#role_arn}
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_period AwsAuthBackendClient#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_schedule AwsAuthBackendClient#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_window AwsAuthBackendClient#rotation_window}
        :param secret_key: AWS Secret key with permissions to query AWS APIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#secret_key AwsAuthBackendClient#secret_key}
        :param sts_endpoint: URL to override the default generated endpoint for making AWS STS API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#sts_endpoint AwsAuthBackendClient#sts_endpoint}
        :param sts_region: Region to override the default region for making AWS STS API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#sts_region AwsAuthBackendClient#sts_region}
        :param use_sts_region_from_client: If set, will override sts_region and use the region from the client request's header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#use_sts_region_from_client AwsAuthBackendClient#use_sts_region_from_client}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfa6e487fdbc5232f14f2d67eb1078e4415b71e13c58da3d85b0f0e5c8b0a75c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AwsAuthBackendClientConfig(
            access_key=access_key,
            backend=backend,
            disable_automated_rotation=disable_automated_rotation,
            ec2_endpoint=ec2_endpoint,
            iam_endpoint=iam_endpoint,
            iam_server_id_header_value=iam_server_id_header_value,
            id=id,
            identity_token_audience=identity_token_audience,
            identity_token_ttl=identity_token_ttl,
            max_retries=max_retries,
            namespace=namespace,
            role_arn=role_arn,
            rotation_period=rotation_period,
            rotation_schedule=rotation_schedule,
            rotation_window=rotation_window,
            secret_key=secret_key,
            sts_endpoint=sts_endpoint,
            sts_region=sts_region,
            use_sts_region_from_client=use_sts_region_from_client,
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
        '''Generates CDKTF code for importing a AwsAuthBackendClient resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AwsAuthBackendClient to import.
        :param import_from_id: The id of the existing AwsAuthBackendClient that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AwsAuthBackendClient to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483a48bfb92098e440056ac7b07503f7c284d7641840275a361e1669d4fc5b99)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessKey")
    def reset_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessKey", []))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetDisableAutomatedRotation")
    def reset_disable_automated_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAutomatedRotation", []))

    @jsii.member(jsii_name="resetEc2Endpoint")
    def reset_ec2_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEc2Endpoint", []))

    @jsii.member(jsii_name="resetIamEndpoint")
    def reset_iam_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamEndpoint", []))

    @jsii.member(jsii_name="resetIamServerIdHeaderValue")
    def reset_iam_server_id_header_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamServerIdHeaderValue", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentityTokenAudience")
    def reset_identity_token_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityTokenAudience", []))

    @jsii.member(jsii_name="resetIdentityTokenTtl")
    def reset_identity_token_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityTokenTtl", []))

    @jsii.member(jsii_name="resetMaxRetries")
    def reset_max_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetries", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="resetRotationPeriod")
    def reset_rotation_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationPeriod", []))

    @jsii.member(jsii_name="resetRotationSchedule")
    def reset_rotation_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationSchedule", []))

    @jsii.member(jsii_name="resetRotationWindow")
    def reset_rotation_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationWindow", []))

    @jsii.member(jsii_name="resetSecretKey")
    def reset_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretKey", []))

    @jsii.member(jsii_name="resetStsEndpoint")
    def reset_sts_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStsEndpoint", []))

    @jsii.member(jsii_name="resetStsRegion")
    def reset_sts_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStsRegion", []))

    @jsii.member(jsii_name="resetUseStsRegionFromClient")
    def reset_use_sts_region_from_client(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseStsRegionFromClient", []))

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
    @jsii.member(jsii_name="accessKeyInput")
    def access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="disableAutomatedRotationInput")
    def disable_automated_rotation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableAutomatedRotationInput"))

    @builtins.property
    @jsii.member(jsii_name="ec2EndpointInput")
    def ec2_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ec2EndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="iamEndpointInput")
    def iam_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="iamServerIdHeaderValueInput")
    def iam_server_id_header_value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamServerIdHeaderValueInput"))

    @builtins.property
    @jsii.member(jsii_name="identityTokenAudienceInput")
    def identity_token_audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityTokenAudienceInput"))

    @builtins.property
    @jsii.member(jsii_name="identityTokenTtlInput")
    def identity_token_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "identityTokenTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxRetriesInput")
    def max_retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetriesInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationPeriodInput")
    def rotation_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationScheduleInput")
    def rotation_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationWindowInput")
    def rotation_window_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="secretKeyInput")
    def secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="stsEndpointInput")
    def sts_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stsEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="stsRegionInput")
    def sts_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stsRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="useStsRegionFromClientInput")
    def use_sts_region_from_client_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useStsRegionFromClientInput"))

    @builtins.property
    @jsii.member(jsii_name="accessKey")
    def access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKey"))

    @access_key.setter
    def access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2be031cbde7462658178ab8d7b04061f56db5f483ade847f1479df65cbefe47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8363cad1c9b1d05dad87001295bddc23914dcd9d124afe0d4f6c46d2c999156)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableAutomatedRotation")
    def disable_automated_rotation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableAutomatedRotation"))

    @disable_automated_rotation.setter
    def disable_automated_rotation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc44285e2260035b3ac1dc033351e50fbf451680f9a4eb9e2fc8a1680fe8132c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAutomatedRotation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ec2Endpoint")
    def ec2_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2Endpoint"))

    @ec2_endpoint.setter
    def ec2_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__656042bbd8614a5cb113ce07b2595595678feea44054d8b4df1b0c0d954e2646)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ec2Endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamEndpoint")
    def iam_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamEndpoint"))

    @iam_endpoint.setter
    def iam_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a3b1973fa2828aa5d08fd32cb94a53dd0c3ae06a739a0bf00f6af54e41dd363)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamServerIdHeaderValue")
    def iam_server_id_header_value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamServerIdHeaderValue"))

    @iam_server_id_header_value.setter
    def iam_server_id_header_value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77599775871108af478c2d36beda349e1127f9c615b93bf426e26cdec4dac766)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamServerIdHeaderValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b6e1879708145882fca8341be84be24c469797a5e884a488b2c657401e865cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenAudience")
    def identity_token_audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityTokenAudience"))

    @identity_token_audience.setter
    def identity_token_audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeec8473e9c2ce2137bb2cad4aa3675d16f2346a98262bb10cb32f84ba9c2435)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenAudience", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityTokenTtl")
    def identity_token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "identityTokenTtl"))

    @identity_token_ttl.setter
    def identity_token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b134e9341ab0fa82c01cf2726e46e8cb29a9aa31f518218acaf0e6a7e66ac69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityTokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7395dea6d26a9e2c149ca7abdeb46837a0c84ec59ed1c0b204d67274df92b949)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxRetries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__633c8a0753a62a79a8b1efb695f080e29e69d78eb283ac7e7ceeb27ee77623a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ecb1b74d823bae3da23d29a8ef4fa9a0e030e7eb82390a6c8f858b22fb0f913)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationPeriod")
    def rotation_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationPeriod"))

    @rotation_period.setter
    def rotation_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ca640c2d745a6386f0c9af42c2ca0cb2913440abe04340fd05ab6485cb29799)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationSchedule")
    def rotation_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationSchedule"))

    @rotation_schedule.setter
    def rotation_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b655cfd27b12c040726efd508d5442785de0bc8820dea8d2e4fa4cde33de73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationWindow")
    def rotation_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationWindow"))

    @rotation_window.setter
    def rotation_window(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c131e71dc957079ad01fb9a933889460001b26fdbc3c035cf1372e896b86b9c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationWindow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__039177425e1fbbb14bdcd06e02288aaf9dca62e4616df207db4da49d2aba389f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stsEndpoint")
    def sts_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stsEndpoint"))

    @sts_endpoint.setter
    def sts_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db2e879e04ec00d0724e594de776c385b1a287b875a3d33c31ac0e89fa408360)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stsEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stsRegion")
    def sts_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stsRegion"))

    @sts_region.setter
    def sts_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e43706d2e615cbf77cb17c6e463e72e89c97725003e5a8ecbabd24d8e8e6954)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stsRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useStsRegionFromClient")
    def use_sts_region_from_client(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useStsRegionFromClient"))

    @use_sts_region_from_client.setter
    def use_sts_region_from_client(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59cb41bda1d061f08cd2c37c57debf9e2996ced3fc94bc0197ca3e0d01cc8e30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useStsRegionFromClient", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.awsAuthBackendClient.AwsAuthBackendClientConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "access_key": "accessKey",
        "backend": "backend",
        "disable_automated_rotation": "disableAutomatedRotation",
        "ec2_endpoint": "ec2Endpoint",
        "iam_endpoint": "iamEndpoint",
        "iam_server_id_header_value": "iamServerIdHeaderValue",
        "id": "id",
        "identity_token_audience": "identityTokenAudience",
        "identity_token_ttl": "identityTokenTtl",
        "max_retries": "maxRetries",
        "namespace": "namespace",
        "role_arn": "roleArn",
        "rotation_period": "rotationPeriod",
        "rotation_schedule": "rotationSchedule",
        "rotation_window": "rotationWindow",
        "secret_key": "secretKey",
        "sts_endpoint": "stsEndpoint",
        "sts_region": "stsRegion",
        "use_sts_region_from_client": "useStsRegionFromClient",
    },
)
class AwsAuthBackendClientConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_key: typing.Optional[builtins.str] = None,
        backend: typing.Optional[builtins.str] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ec2_endpoint: typing.Optional[builtins.str] = None,
        iam_endpoint: typing.Optional[builtins.str] = None,
        iam_server_id_header_value: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity_token_audience: typing.Optional[builtins.str] = None,
        identity_token_ttl: typing.Optional[jsii.Number] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        secret_key: typing.Optional[builtins.str] = None,
        sts_endpoint: typing.Optional[builtins.str] = None,
        sts_region: typing.Optional[builtins.str] = None,
        use_sts_region_from_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param access_key: AWS Access key with permissions to query AWS APIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#access_key AwsAuthBackendClient#access_key}
        :param backend: Unique name of the auth backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#backend AwsAuthBackendClient#backend}
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#disable_automated_rotation AwsAuthBackendClient#disable_automated_rotation}
        :param ec2_endpoint: URL to override the default generated endpoint for making AWS EC2 API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#ec2_endpoint AwsAuthBackendClient#ec2_endpoint}
        :param iam_endpoint: URL to override the default generated endpoint for making AWS IAM API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#iam_endpoint AwsAuthBackendClient#iam_endpoint}
        :param iam_server_id_header_value: The value to require in the X-Vault-AWS-IAM-Server-ID header as part of GetCallerIdentity requests that are used in the iam auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#iam_server_id_header_value AwsAuthBackendClient#iam_server_id_header_value}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#id AwsAuthBackendClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_token_audience: The audience claim value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#identity_token_audience AwsAuthBackendClient#identity_token_audience}
        :param identity_token_ttl: The TTL of generated identity tokens in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#identity_token_ttl AwsAuthBackendClient#identity_token_ttl}
        :param max_retries: Number of max retries the client should use for recoverable errors. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#max_retries AwsAuthBackendClient#max_retries}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#namespace AwsAuthBackendClient#namespace}
        :param role_arn: Role ARN to assume for plugin identity token federation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#role_arn AwsAuthBackendClient#role_arn}
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_period AwsAuthBackendClient#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_schedule AwsAuthBackendClient#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_window AwsAuthBackendClient#rotation_window}
        :param secret_key: AWS Secret key with permissions to query AWS APIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#secret_key AwsAuthBackendClient#secret_key}
        :param sts_endpoint: URL to override the default generated endpoint for making AWS STS API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#sts_endpoint AwsAuthBackendClient#sts_endpoint}
        :param sts_region: Region to override the default region for making AWS STS API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#sts_region AwsAuthBackendClient#sts_region}
        :param use_sts_region_from_client: If set, will override sts_region and use the region from the client request's header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#use_sts_region_from_client AwsAuthBackendClient#use_sts_region_from_client}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a70d6fbd3fd20b0f695485e64da2585954c8d582660fa2abfda01392ea1d14)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument access_key", value=access_key, expected_type=type_hints["access_key"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument disable_automated_rotation", value=disable_automated_rotation, expected_type=type_hints["disable_automated_rotation"])
            check_type(argname="argument ec2_endpoint", value=ec2_endpoint, expected_type=type_hints["ec2_endpoint"])
            check_type(argname="argument iam_endpoint", value=iam_endpoint, expected_type=type_hints["iam_endpoint"])
            check_type(argname="argument iam_server_id_header_value", value=iam_server_id_header_value, expected_type=type_hints["iam_server_id_header_value"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_token_audience", value=identity_token_audience, expected_type=type_hints["identity_token_audience"])
            check_type(argname="argument identity_token_ttl", value=identity_token_ttl, expected_type=type_hints["identity_token_ttl"])
            check_type(argname="argument max_retries", value=max_retries, expected_type=type_hints["max_retries"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument rotation_period", value=rotation_period, expected_type=type_hints["rotation_period"])
            check_type(argname="argument rotation_schedule", value=rotation_schedule, expected_type=type_hints["rotation_schedule"])
            check_type(argname="argument rotation_window", value=rotation_window, expected_type=type_hints["rotation_window"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument sts_endpoint", value=sts_endpoint, expected_type=type_hints["sts_endpoint"])
            check_type(argname="argument sts_region", value=sts_region, expected_type=type_hints["sts_region"])
            check_type(argname="argument use_sts_region_from_client", value=use_sts_region_from_client, expected_type=type_hints["use_sts_region_from_client"])
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
        if access_key is not None:
            self._values["access_key"] = access_key
        if backend is not None:
            self._values["backend"] = backend
        if disable_automated_rotation is not None:
            self._values["disable_automated_rotation"] = disable_automated_rotation
        if ec2_endpoint is not None:
            self._values["ec2_endpoint"] = ec2_endpoint
        if iam_endpoint is not None:
            self._values["iam_endpoint"] = iam_endpoint
        if iam_server_id_header_value is not None:
            self._values["iam_server_id_header_value"] = iam_server_id_header_value
        if id is not None:
            self._values["id"] = id
        if identity_token_audience is not None:
            self._values["identity_token_audience"] = identity_token_audience
        if identity_token_ttl is not None:
            self._values["identity_token_ttl"] = identity_token_ttl
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if namespace is not None:
            self._values["namespace"] = namespace
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if rotation_period is not None:
            self._values["rotation_period"] = rotation_period
        if rotation_schedule is not None:
            self._values["rotation_schedule"] = rotation_schedule
        if rotation_window is not None:
            self._values["rotation_window"] = rotation_window
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if sts_endpoint is not None:
            self._values["sts_endpoint"] = sts_endpoint
        if sts_region is not None:
            self._values["sts_region"] = sts_region
        if use_sts_region_from_client is not None:
            self._values["use_sts_region_from_client"] = use_sts_region_from_client

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
    def access_key(self) -> typing.Optional[builtins.str]:
        '''AWS Access key with permissions to query AWS APIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#access_key AwsAuthBackendClient#access_key}
        '''
        result = self._values.get("access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the auth backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#backend AwsAuthBackendClient#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_automated_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Stops rotation of the root credential until set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#disable_automated_rotation AwsAuthBackendClient#disable_automated_rotation}
        '''
        result = self._values.get("disable_automated_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ec2_endpoint(self) -> typing.Optional[builtins.str]:
        '''URL to override the default generated endpoint for making AWS EC2 API calls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#ec2_endpoint AwsAuthBackendClient#ec2_endpoint}
        '''
        result = self._values.get("ec2_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_endpoint(self) -> typing.Optional[builtins.str]:
        '''URL to override the default generated endpoint for making AWS IAM API calls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#iam_endpoint AwsAuthBackendClient#iam_endpoint}
        '''
        result = self._values.get("iam_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_server_id_header_value(self) -> typing.Optional[builtins.str]:
        '''The value to require in the X-Vault-AWS-IAM-Server-ID header as part of GetCallerIdentity requests that are used in the iam auth method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#iam_server_id_header_value AwsAuthBackendClient#iam_server_id_header_value}
        '''
        result = self._values.get("iam_server_id_header_value")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#id AwsAuthBackendClient#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_audience(self) -> typing.Optional[builtins.str]:
        '''The audience claim value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#identity_token_audience AwsAuthBackendClient#identity_token_audience}
        '''
        result = self._values.get("identity_token_audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The TTL of generated identity tokens in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#identity_token_ttl AwsAuthBackendClient#identity_token_ttl}
        '''
        result = self._values.get("identity_token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''Number of max retries the client should use for recoverable errors.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#max_retries AwsAuthBackendClient#max_retries}
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#namespace AwsAuthBackendClient#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Role ARN to assume for plugin identity token federation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#role_arn AwsAuthBackendClient#role_arn}
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_period(self) -> typing.Optional[jsii.Number]:
        '''The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_period AwsAuthBackendClient#rotation_period}
        '''
        result = self._values.get("rotation_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_schedule(self) -> typing.Optional[builtins.str]:
        '''The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_schedule AwsAuthBackendClient#rotation_schedule}
        '''
        result = self._values.get("rotation_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_window(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered.

        Can only be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#rotation_window AwsAuthBackendClient#rotation_window}
        '''
        result = self._values.get("rotation_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        '''AWS Secret key with permissions to query AWS APIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#secret_key AwsAuthBackendClient#secret_key}
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sts_endpoint(self) -> typing.Optional[builtins.str]:
        '''URL to override the default generated endpoint for making AWS STS API calls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#sts_endpoint AwsAuthBackendClient#sts_endpoint}
        '''
        result = self._values.get("sts_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sts_region(self) -> typing.Optional[builtins.str]:
        '''Region to override the default region for making AWS STS API calls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#sts_region AwsAuthBackendClient#sts_region}
        '''
        result = self._values.get("sts_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_sts_region_from_client(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, will override sts_region and use the region from the client request's header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_client#use_sts_region_from_client AwsAuthBackendClient#use_sts_region_from_client}
        '''
        result = self._values.get("use_sts_region_from_client")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsAuthBackendClientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsAuthBackendClient",
    "AwsAuthBackendClientConfig",
]

publication.publish()

def _typecheckingstub__cfa6e487fdbc5232f14f2d67eb1078e4415b71e13c58da3d85b0f0e5c8b0a75c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    access_key: typing.Optional[builtins.str] = None,
    backend: typing.Optional[builtins.str] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ec2_endpoint: typing.Optional[builtins.str] = None,
    iam_endpoint: typing.Optional[builtins.str] = None,
    iam_server_id_header_value: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_audience: typing.Optional[builtins.str] = None,
    identity_token_ttl: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    secret_key: typing.Optional[builtins.str] = None,
    sts_endpoint: typing.Optional[builtins.str] = None,
    sts_region: typing.Optional[builtins.str] = None,
    use_sts_region_from_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__483a48bfb92098e440056ac7b07503f7c284d7641840275a361e1669d4fc5b99(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2be031cbde7462658178ab8d7b04061f56db5f483ade847f1479df65cbefe47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8363cad1c9b1d05dad87001295bddc23914dcd9d124afe0d4f6c46d2c999156(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc44285e2260035b3ac1dc033351e50fbf451680f9a4eb9e2fc8a1680fe8132c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__656042bbd8614a5cb113ce07b2595595678feea44054d8b4df1b0c0d954e2646(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a3b1973fa2828aa5d08fd32cb94a53dd0c3ae06a739a0bf00f6af54e41dd363(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77599775871108af478c2d36beda349e1127f9c615b93bf426e26cdec4dac766(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b6e1879708145882fca8341be84be24c469797a5e884a488b2c657401e865cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeec8473e9c2ce2137bb2cad4aa3675d16f2346a98262bb10cb32f84ba9c2435(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b134e9341ab0fa82c01cf2726e46e8cb29a9aa31f518218acaf0e6a7e66ac69(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7395dea6d26a9e2c149ca7abdeb46837a0c84ec59ed1c0b204d67274df92b949(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__633c8a0753a62a79a8b1efb695f080e29e69d78eb283ac7e7ceeb27ee77623a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ecb1b74d823bae3da23d29a8ef4fa9a0e030e7eb82390a6c8f858b22fb0f913(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ca640c2d745a6386f0c9af42c2ca0cb2913440abe04340fd05ab6485cb29799(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b655cfd27b12c040726efd508d5442785de0bc8820dea8d2e4fa4cde33de73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c131e71dc957079ad01fb9a933889460001b26fdbc3c035cf1372e896b86b9c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__039177425e1fbbb14bdcd06e02288aaf9dca62e4616df207db4da49d2aba389f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db2e879e04ec00d0724e594de776c385b1a287b875a3d33c31ac0e89fa408360(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e43706d2e615cbf77cb17c6e463e72e89c97725003e5a8ecbabd24d8e8e6954(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59cb41bda1d061f08cd2c37c57debf9e2996ced3fc94bc0197ca3e0d01cc8e30(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a70d6fbd3fd20b0f695485e64da2585954c8d582660fa2abfda01392ea1d14(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    access_key: typing.Optional[builtins.str] = None,
    backend: typing.Optional[builtins.str] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ec2_endpoint: typing.Optional[builtins.str] = None,
    iam_endpoint: typing.Optional[builtins.str] = None,
    iam_server_id_header_value: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    identity_token_audience: typing.Optional[builtins.str] = None,
    identity_token_ttl: typing.Optional[jsii.Number] = None,
    max_retries: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    secret_key: typing.Optional[builtins.str] = None,
    sts_endpoint: typing.Optional[builtins.str] = None,
    sts_region: typing.Optional[builtins.str] = None,
    use_sts_region_from_client: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
