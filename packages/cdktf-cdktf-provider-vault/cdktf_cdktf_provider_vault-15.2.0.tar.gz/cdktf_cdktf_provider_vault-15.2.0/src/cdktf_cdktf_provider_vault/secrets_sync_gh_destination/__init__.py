r'''
# `vault_secrets_sync_gh_destination`

Refer to the Terraform Registry for docs: [`vault_secrets_sync_gh_destination`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination).
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


class SecretsSyncGhDestination(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.secretsSyncGhDestination.SecretsSyncGhDestination",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination vault_secrets_sync_gh_destination}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        access_token: typing.Optional[builtins.str] = None,
        app_name: typing.Optional[builtins.str] = None,
        granularity: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        installation_id: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        repository_owner: typing.Optional[builtins.str] = None,
        secret_name_template: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination vault_secrets_sync_gh_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Unique name of the github destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#name SecretsSyncGhDestination#name}
        :param access_token: Fine-grained or personal access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#access_token SecretsSyncGhDestination#access_token}
        :param app_name: The user-defined name of the GitHub App configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#app_name SecretsSyncGhDestination#app_name}
        :param granularity: Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#granularity SecretsSyncGhDestination#granularity}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#id SecretsSyncGhDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param installation_id: The ID of the installation generated by GitHub when the app referenced by the app_name was installed in the user’s GitHub account. Necessary if the app_name field is also provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#installation_id SecretsSyncGhDestination#installation_id}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#namespace SecretsSyncGhDestination#namespace}
        :param repository_name: Name of the repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#repository_name SecretsSyncGhDestination#repository_name}
        :param repository_owner: GitHub organization or username that owns the repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#repository_owner SecretsSyncGhDestination#repository_owner}
        :param secret_name_template: Template describing how to generate external secret names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#secret_name_template SecretsSyncGhDestination#secret_name_template}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ca7edf3af3e8b683ccf6c00f5076f6b99508cfcd2448f8cbcffebca6842d3a1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SecretsSyncGhDestinationConfig(
            name=name,
            access_token=access_token,
            app_name=app_name,
            granularity=granularity,
            id=id,
            installation_id=installation_id,
            namespace=namespace,
            repository_name=repository_name,
            repository_owner=repository_owner,
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
        '''Generates CDKTF code for importing a SecretsSyncGhDestination resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SecretsSyncGhDestination to import.
        :param import_from_id: The id of the existing SecretsSyncGhDestination that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SecretsSyncGhDestination to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6507a23a6fbe86c18066481e039163291bfe5c322ecd49b906ab773bb818e545)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessToken")
    def reset_access_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessToken", []))

    @jsii.member(jsii_name="resetAppName")
    def reset_app_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppName", []))

    @jsii.member(jsii_name="resetGranularity")
    def reset_granularity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGranularity", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstallationId")
    def reset_installation_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallationId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRepositoryName")
    def reset_repository_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepositoryName", []))

    @jsii.member(jsii_name="resetRepositoryOwner")
    def reset_repository_owner(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepositoryOwner", []))

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
    @jsii.member(jsii_name="accessTokenInput")
    def access_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="appNameInput")
    def app_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appNameInput"))

    @builtins.property
    @jsii.member(jsii_name="granularityInput")
    def granularity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "granularityInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="installationIdInput")
    def installation_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "installationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryNameInput")
    def repository_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryNameInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryOwnerInput")
    def repository_owner_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryOwnerInput"))

    @builtins.property
    @jsii.member(jsii_name="secretNameTemplateInput")
    def secret_name_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretNameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebc7c8e855bf260388dff954ed8124e625a633157f789db165e6ceee7cb1630e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="appName")
    def app_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appName"))

    @app_name.setter
    def app_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c0402b17695be39e1647c6a9058a5c44cf8d229a7ddaf0433efb1b26ad4d99a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="granularity")
    def granularity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "granularity"))

    @granularity.setter
    def granularity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81f3a7835541f8d0d5480b2a042516c563dd4d45de58ba246b4c468f3a781dac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "granularity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f64122d1a6343f68b2a5f58b8668efc36db4353c3aab06ad905b9a739f0d10ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="installationId")
    def installation_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "installationId"))

    @installation_id.setter
    def installation_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a161cb24dd50e2890ccc71821d4440a7ba5a5302d2aebfdd70837dc104c70f62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "installationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04a48a54abca341451f9852243b62fbce26d7ea97b0ab8be42bb303399345bd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2489f32d36b28c7f035a0b3f1f6f36053daeca1c6e373edfc8c0b6acd2a2dca5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @repository_name.setter
    def repository_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5658c63e18063c65d543245519582a1e8264e2f155dcde3b51a1f8843c7e4faa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositoryName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repositoryOwner")
    def repository_owner(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repositoryOwner"))

    @repository_owner.setter
    def repository_owner(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ee4ff8a25dc5f797b3f92518793d356cc056b526196159093461f84dbd44212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repositoryOwner", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretNameTemplate")
    def secret_name_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretNameTemplate"))

    @secret_name_template.setter
    def secret_name_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2a089c4d0002cfd20e67daf243c28ab2be299de4c74867d5beae110288ba9db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretNameTemplate", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.secretsSyncGhDestination.SecretsSyncGhDestinationConfig",
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
        "access_token": "accessToken",
        "app_name": "appName",
        "granularity": "granularity",
        "id": "id",
        "installation_id": "installationId",
        "namespace": "namespace",
        "repository_name": "repositoryName",
        "repository_owner": "repositoryOwner",
        "secret_name_template": "secretNameTemplate",
    },
)
class SecretsSyncGhDestinationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_token: typing.Optional[builtins.str] = None,
        app_name: typing.Optional[builtins.str] = None,
        granularity: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        installation_id: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        repository_owner: typing.Optional[builtins.str] = None,
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
        :param name: Unique name of the github destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#name SecretsSyncGhDestination#name}
        :param access_token: Fine-grained or personal access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#access_token SecretsSyncGhDestination#access_token}
        :param app_name: The user-defined name of the GitHub App configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#app_name SecretsSyncGhDestination#app_name}
        :param granularity: Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#granularity SecretsSyncGhDestination#granularity}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#id SecretsSyncGhDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param installation_id: The ID of the installation generated by GitHub when the app referenced by the app_name was installed in the user’s GitHub account. Necessary if the app_name field is also provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#installation_id SecretsSyncGhDestination#installation_id}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#namespace SecretsSyncGhDestination#namespace}
        :param repository_name: Name of the repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#repository_name SecretsSyncGhDestination#repository_name}
        :param repository_owner: GitHub organization or username that owns the repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#repository_owner SecretsSyncGhDestination#repository_owner}
        :param secret_name_template: Template describing how to generate external secret names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#secret_name_template SecretsSyncGhDestination#secret_name_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0b3345e157bf5537389f067a2b038b9524c667f6de56fefc5f7b2737dc897ff)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument app_name", value=app_name, expected_type=type_hints["app_name"])
            check_type(argname="argument granularity", value=granularity, expected_type=type_hints["granularity"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument installation_id", value=installation_id, expected_type=type_hints["installation_id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
            check_type(argname="argument repository_owner", value=repository_owner, expected_type=type_hints["repository_owner"])
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
        if access_token is not None:
            self._values["access_token"] = access_token
        if app_name is not None:
            self._values["app_name"] = app_name
        if granularity is not None:
            self._values["granularity"] = granularity
        if id is not None:
            self._values["id"] = id
        if installation_id is not None:
            self._values["installation_id"] = installation_id
        if namespace is not None:
            self._values["namespace"] = namespace
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if repository_owner is not None:
            self._values["repository_owner"] = repository_owner
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
        '''Unique name of the github destination.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#name SecretsSyncGhDestination#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token(self) -> typing.Optional[builtins.str]:
        '''Fine-grained or personal access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#access_token SecretsSyncGhDestination#access_token}
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_name(self) -> typing.Optional[builtins.str]:
        '''The user-defined name of the GitHub App configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#app_name SecretsSyncGhDestination#app_name}
        '''
        result = self._values.get("app_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def granularity(self) -> typing.Optional[builtins.str]:
        '''Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#granularity SecretsSyncGhDestination#granularity}
        '''
        result = self._values.get("granularity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#id SecretsSyncGhDestination#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def installation_id(self) -> typing.Optional[jsii.Number]:
        '''The ID of the installation generated by GitHub when the app referenced by the app_name was installed in the user’s GitHub account.

        Necessary if the app_name field is also provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#installation_id SecretsSyncGhDestination#installation_id}
        '''
        result = self._values.get("installation_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#namespace SecretsSyncGhDestination#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''Name of the repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#repository_name SecretsSyncGhDestination#repository_name}
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_owner(self) -> typing.Optional[builtins.str]:
        '''GitHub organization or username that owns the repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#repository_owner SecretsSyncGhDestination#repository_owner}
        '''
        result = self._values.get("repository_owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how to generate external secret names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_gh_destination#secret_name_template SecretsSyncGhDestination#secret_name_template}
        '''
        result = self._values.get("secret_name_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretsSyncGhDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecretsSyncGhDestination",
    "SecretsSyncGhDestinationConfig",
]

publication.publish()

def _typecheckingstub__3ca7edf3af3e8b683ccf6c00f5076f6b99508cfcd2448f8cbcffebca6842d3a1(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    access_token: typing.Optional[builtins.str] = None,
    app_name: typing.Optional[builtins.str] = None,
    granularity: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    installation_id: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    repository_owner: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6507a23a6fbe86c18066481e039163291bfe5c322ecd49b906ab773bb818e545(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc7c8e855bf260388dff954ed8124e625a633157f789db165e6ceee7cb1630e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c0402b17695be39e1647c6a9058a5c44cf8d229a7ddaf0433efb1b26ad4d99a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81f3a7835541f8d0d5480b2a042516c563dd4d45de58ba246b4c468f3a781dac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f64122d1a6343f68b2a5f58b8668efc36db4353c3aab06ad905b9a739f0d10ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a161cb24dd50e2890ccc71821d4440a7ba5a5302d2aebfdd70837dc104c70f62(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04a48a54abca341451f9852243b62fbce26d7ea97b0ab8be42bb303399345bd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2489f32d36b28c7f035a0b3f1f6f36053daeca1c6e373edfc8c0b6acd2a2dca5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5658c63e18063c65d543245519582a1e8264e2f155dcde3b51a1f8843c7e4faa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ee4ff8a25dc5f797b3f92518793d356cc056b526196159093461f84dbd44212(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2a089c4d0002cfd20e67daf243c28ab2be299de4c74867d5beae110288ba9db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0b3345e157bf5537389f067a2b038b9524c667f6de56fefc5f7b2737dc897ff(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    access_token: typing.Optional[builtins.str] = None,
    app_name: typing.Optional[builtins.str] = None,
    granularity: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    installation_id: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    repository_name: typing.Optional[builtins.str] = None,
    repository_owner: typing.Optional[builtins.str] = None,
    secret_name_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
