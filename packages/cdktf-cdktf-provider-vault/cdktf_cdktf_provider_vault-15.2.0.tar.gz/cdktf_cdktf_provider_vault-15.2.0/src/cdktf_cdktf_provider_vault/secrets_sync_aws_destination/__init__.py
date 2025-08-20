r'''
# `vault_secrets_sync_aws_destination`

Refer to the Terraform Registry for docs: [`vault_secrets_sync_aws_destination`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination).
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


class SecretsSyncAwsDestination(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.secretsSyncAwsDestination.SecretsSyncAwsDestination",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination vault_secrets_sync_aws_destination}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        access_key_id: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        external_id: typing.Optional[builtins.str] = None,
        granularity: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
        secret_name_template: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination vault_secrets_sync_aws_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Unique name of the AWS destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#name SecretsSyncAwsDestination#name}
        :param access_key_id: Access key id to authenticate against the AWS secrets manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#access_key_id SecretsSyncAwsDestination#access_key_id}
        :param custom_tags: Custom tags to set on the secret managed at the destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#custom_tags SecretsSyncAwsDestination#custom_tags}
        :param external_id: Extra protection that must match the trust policy granting access to the AWS IAM role ARN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#external_id SecretsSyncAwsDestination#external_id}
        :param granularity: Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#granularity SecretsSyncAwsDestination#granularity}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#id SecretsSyncAwsDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#namespace SecretsSyncAwsDestination#namespace}
        :param region: Region where to manage the secrets manager entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#region SecretsSyncAwsDestination#region}
        :param role_arn: Specifies a role to assume when connecting to AWS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#role_arn SecretsSyncAwsDestination#role_arn}
        :param secret_access_key: Secret access key to authenticate against the AWS secrets manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#secret_access_key SecretsSyncAwsDestination#secret_access_key}
        :param secret_name_template: Template describing how to generate external secret names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#secret_name_template SecretsSyncAwsDestination#secret_name_template}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1064f10362c6a2038e6a7581f71ff681098e334223eeeb692dd211fcbd2e53fb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SecretsSyncAwsDestinationConfig(
            name=name,
            access_key_id=access_key_id,
            custom_tags=custom_tags,
            external_id=external_id,
            granularity=granularity,
            id=id,
            namespace=namespace,
            region=region,
            role_arn=role_arn,
            secret_access_key=secret_access_key,
            secret_name_template=secret_name_template,
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
        '''Generates CDKTF code for importing a SecretsSyncAwsDestination resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SecretsSyncAwsDestination to import.
        :param import_from_id: The id of the existing SecretsSyncAwsDestination that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SecretsSyncAwsDestination to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e04cab82161a2fc235af0353bb042b33391df7db6bd3a3dba42b33d7c64c0ae)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessKeyId")
    def reset_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessKeyId", []))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetExternalId")
    def reset_external_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalId", []))

    @jsii.member(jsii_name="resetGranularity")
    def reset_granularity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGranularity", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="resetSecretAccessKey")
    def reset_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretAccessKey", []))

    @jsii.member(jsii_name="resetSecretNameTemplate")
    def reset_secret_name_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretNameTemplate", []))

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyIdInput")
    def access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property
    @jsii.member(jsii_name="granularityInput")
    def granularity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "granularityInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property
    @jsii.member(jsii_name="secretAccessKeyInput")
    def secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="secretNameTemplateInput")
    def secret_name_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretNameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyId")
    def access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKeyId"))

    @access_key_id.setter
    def access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0630dc6d069e71c54c49e9a3ac39e543679ea54f2f8915364d82efc616bfc6a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customTags"))

    @custom_tags.setter
    def custom_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06cef6697c9542bb514bce3a7dcfc89dd9eaddffe41904207d9359620b17a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63162bdb525fc8c9d0a8401a8a7d2c12870c0ede3ea6cbe0b26f93219ae17a38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="granularity")
    def granularity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "granularity"))

    @granularity.setter
    def granularity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0db17d19f52a49511e070fcf48ee730c8f2e91feaf295aa80a1f762995a20a9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "granularity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f6cf089c02ebb76cda8c91650a006542f12fe2ff04b8fa096470611136287f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__526d79391b9c81dabb1a5c755ce8e23a0c6773b465518b6fbb403252e206d95a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bca0d1236b498f5d385c3eb66d7e3e6f27b03329b98b3cff58b27e345ae269f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67586211f2dd893ff218ae1904f31432ac71d1ce2357206d9a28880ae280ff26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e27ce0e662095f1b5afe98511a6d4415523f3df18d57ad135d5d26339254c8aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretAccessKey")
    def secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretAccessKey"))

    @secret_access_key.setter
    def secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48cccfb1b888f63a86b20374d72118b166050fc8599b6a2fd7e8fb4aaf354333)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretNameTemplate")
    def secret_name_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretNameTemplate"))

    @secret_name_template.setter
    def secret_name_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41c63fddac861c292d61ba6f57c6f0787e7ca70a8a7f856943a6cc94ba396280)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretNameTemplate", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.secretsSyncAwsDestination.SecretsSyncAwsDestinationConfig",
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
        "access_key_id": "accessKeyId",
        "custom_tags": "customTags",
        "external_id": "externalId",
        "granularity": "granularity",
        "id": "id",
        "namespace": "namespace",
        "region": "region",
        "role_arn": "roleArn",
        "secret_access_key": "secretAccessKey",
        "secret_name_template": "secretNameTemplate",
    },
)
class SecretsSyncAwsDestinationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_key_id: typing.Optional[builtins.str] = None,
        custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        external_id: typing.Optional[builtins.str] = None,
        granularity: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        role_arn: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
        secret_name_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Unique name of the AWS destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#name SecretsSyncAwsDestination#name}
        :param access_key_id: Access key id to authenticate against the AWS secrets manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#access_key_id SecretsSyncAwsDestination#access_key_id}
        :param custom_tags: Custom tags to set on the secret managed at the destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#custom_tags SecretsSyncAwsDestination#custom_tags}
        :param external_id: Extra protection that must match the trust policy granting access to the AWS IAM role ARN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#external_id SecretsSyncAwsDestination#external_id}
        :param granularity: Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#granularity SecretsSyncAwsDestination#granularity}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#id SecretsSyncAwsDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#namespace SecretsSyncAwsDestination#namespace}
        :param region: Region where to manage the secrets manager entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#region SecretsSyncAwsDestination#region}
        :param role_arn: Specifies a role to assume when connecting to AWS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#role_arn SecretsSyncAwsDestination#role_arn}
        :param secret_access_key: Secret access key to authenticate against the AWS secrets manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#secret_access_key SecretsSyncAwsDestination#secret_access_key}
        :param secret_name_template: Template describing how to generate external secret names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#secret_name_template SecretsSyncAwsDestination#secret_name_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd436aa87a876180fb9c37794563064e6239b8f9b7d1e0ae72980b1e4fa7297)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_key_id", value=access_key_id, expected_type=type_hints["access_key_id"])
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument granularity", value=granularity, expected_type=type_hints["granularity"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument secret_access_key", value=secret_access_key, expected_type=type_hints["secret_access_key"])
            check_type(argname="argument secret_name_template", value=secret_name_template, expected_type=type_hints["secret_name_template"])
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
        if access_key_id is not None:
            self._values["access_key_id"] = access_key_id
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if external_id is not None:
            self._values["external_id"] = external_id
        if granularity is not None:
            self._values["granularity"] = granularity
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if region is not None:
            self._values["region"] = region
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if secret_access_key is not None:
            self._values["secret_access_key"] = secret_access_key
        if secret_name_template is not None:
            self._values["secret_name_template"] = secret_name_template

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
        '''Unique name of the AWS destination.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#name SecretsSyncAwsDestination#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_key_id(self) -> typing.Optional[builtins.str]:
        '''Access key id to authenticate against the AWS secrets manager.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#access_key_id SecretsSyncAwsDestination#access_key_id}
        '''
        result = self._values.get("access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Custom tags to set on the secret managed at the destination.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#custom_tags SecretsSyncAwsDestination#custom_tags}
        '''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def external_id(self) -> typing.Optional[builtins.str]:
        '''Extra protection that must match the trust policy granting access to the AWS IAM role ARN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#external_id SecretsSyncAwsDestination#external_id}
        '''
        result = self._values.get("external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def granularity(self) -> typing.Optional[builtins.str]:
        '''Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#granularity SecretsSyncAwsDestination#granularity}
        '''
        result = self._values.get("granularity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#id SecretsSyncAwsDestination#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#namespace SecretsSyncAwsDestination#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region where to manage the secrets manager entries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#region SecretsSyncAwsDestination#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Specifies a role to assume when connecting to AWS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#role_arn SecretsSyncAwsDestination#role_arn}
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_access_key(self) -> typing.Optional[builtins.str]:
        '''Secret access key to authenticate against the AWS secrets manager.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#secret_access_key SecretsSyncAwsDestination#secret_access_key}
        '''
        result = self._values.get("secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how to generate external secret names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_aws_destination#secret_name_template SecretsSyncAwsDestination#secret_name_template}
        '''
        result = self._values.get("secret_name_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretsSyncAwsDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecretsSyncAwsDestination",
    "SecretsSyncAwsDestinationConfig",
]

publication.publish()

def _typecheckingstub__1064f10362c6a2038e6a7581f71ff681098e334223eeeb692dd211fcbd2e53fb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    access_key_id: typing.Optional[builtins.str] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    external_id: typing.Optional[builtins.str] = None,
    granularity: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    secret_access_key: typing.Optional[builtins.str] = None,
    secret_name_template: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__4e04cab82161a2fc235af0353bb042b33391df7db6bd3a3dba42b33d7c64c0ae(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0630dc6d069e71c54c49e9a3ac39e543679ea54f2f8915364d82efc616bfc6a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06cef6697c9542bb514bce3a7dcfc89dd9eaddffe41904207d9359620b17a85(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63162bdb525fc8c9d0a8401a8a7d2c12870c0ede3ea6cbe0b26f93219ae17a38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0db17d19f52a49511e070fcf48ee730c8f2e91feaf295aa80a1f762995a20a9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f6cf089c02ebb76cda8c91650a006542f12fe2ff04b8fa096470611136287f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__526d79391b9c81dabb1a5c755ce8e23a0c6773b465518b6fbb403252e206d95a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bca0d1236b498f5d385c3eb66d7e3e6f27b03329b98b3cff58b27e345ae269f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67586211f2dd893ff218ae1904f31432ac71d1ce2357206d9a28880ae280ff26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e27ce0e662095f1b5afe98511a6d4415523f3df18d57ad135d5d26339254c8aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48cccfb1b888f63a86b20374d72118b166050fc8599b6a2fd7e8fb4aaf354333(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41c63fddac861c292d61ba6f57c6f0787e7ca70a8a7f856943a6cc94ba396280(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd436aa87a876180fb9c37794563064e6239b8f9b7d1e0ae72980b1e4fa7297(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    access_key_id: typing.Optional[builtins.str] = None,
    custom_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    external_id: typing.Optional[builtins.str] = None,
    granularity: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    role_arn: typing.Optional[builtins.str] = None,
    secret_access_key: typing.Optional[builtins.str] = None,
    secret_name_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
