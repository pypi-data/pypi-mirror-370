r'''
# `vault_secrets_sync_vercel_destination`

Refer to the Terraform Registry for docs: [`vault_secrets_sync_vercel_destination`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination).
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


class SecretsSyncVercelDestination(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.secretsSyncVercelDestination.SecretsSyncVercelDestination",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination vault_secrets_sync_vercel_destination}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        access_token: builtins.str,
        deployment_environments: typing.Sequence[builtins.str],
        name: builtins.str,
        project_id: builtins.str,
        granularity: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        secret_name_template: typing.Optional[builtins.str] = None,
        team_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination vault_secrets_sync_vercel_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_token: Vercel API access token with the permissions to manage environment variables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#access_token SecretsSyncVercelDestination#access_token}
        :param deployment_environments: Deployment environments where the environment variables are available. Accepts 'development', 'preview' & 'production'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#deployment_environments SecretsSyncVercelDestination#deployment_environments}
        :param name: Unique name of the Vercel destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#name SecretsSyncVercelDestination#name}
        :param project_id: Project ID where to manage environment variables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#project_id SecretsSyncVercelDestination#project_id}
        :param granularity: Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#granularity SecretsSyncVercelDestination#granularity}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#id SecretsSyncVercelDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#namespace SecretsSyncVercelDestination#namespace}
        :param secret_name_template: Template describing how to generate external secret names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#secret_name_template SecretsSyncVercelDestination#secret_name_template}
        :param team_id: Team ID the project belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#team_id SecretsSyncVercelDestination#team_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56eb2c614585bc1ea324349483643e8d952dcec6edd20bc7e039e2d98252e08a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SecretsSyncVercelDestinationConfig(
            access_token=access_token,
            deployment_environments=deployment_environments,
            name=name,
            project_id=project_id,
            granularity=granularity,
            id=id,
            namespace=namespace,
            secret_name_template=secret_name_template,
            team_id=team_id,
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
        '''Generates CDKTF code for importing a SecretsSyncVercelDestination resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SecretsSyncVercelDestination to import.
        :param import_from_id: The id of the existing SecretsSyncVercelDestination that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SecretsSyncVercelDestination to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17127899350d6f1e78745593600fad5c06d4d4c3c261bb8e3b46edc365faae4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetGranularity")
    def reset_granularity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGranularity", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetSecretNameTemplate")
    def reset_secret_name_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretNameTemplate", []))

    @jsii.member(jsii_name="resetTeamId")
    def reset_team_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamId", []))

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
    @jsii.member(jsii_name="deploymentEnvironmentsInput")
    def deployment_environments_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "deploymentEnvironmentsInput"))

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
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="secretNameTemplateInput")
    def secret_name_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretNameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accessToken")
    def access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessToken"))

    @access_token.setter
    def access_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88e5da473b3503fb84a6c7794391c42e02dea3c88ac1def9c192a6e93a3edfc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deploymentEnvironments")
    def deployment_environments(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deploymentEnvironments"))

    @deployment_environments.setter
    def deployment_environments(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac3d4434e261bbc4e3342d32eea5738dee558de0ffa20278fe786ddabcde5169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deploymentEnvironments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="granularity")
    def granularity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "granularity"))

    @granularity.setter
    def granularity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__055d08e9da8a2c62d8fe391124c1190098d54d97caccd3ec149609a69c882281)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "granularity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5cb5b8eb6b3cc49ad96923651288552094244a38dcb398a5bb5599fa98272b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a2021e01ef10ec74940465d019e2fab66a7ab7482506634644c7fa4b676c64f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eac20cfce0befe4b61b632fdc9e996963732416d6529b5b3c916bbc07e8a5dbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9c8b77f6f38cb72f22fa05caabe0deb9b889f221305ab64d10a7c5333994e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretNameTemplate")
    def secret_name_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretNameTemplate"))

    @secret_name_template.setter
    def secret_name_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce1d0f6e1cf69b66f974e6ecf762531fadac730ec5b6fd88e7e284fb5dba2269)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretNameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamId"))

    @team_id.setter
    def team_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c9c3b1c3932ae0b043faf1c39f916fda36c33f42c90ecab24e1ea6a5c2979b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.secretsSyncVercelDestination.SecretsSyncVercelDestinationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "access_token": "accessToken",
        "deployment_environments": "deploymentEnvironments",
        "name": "name",
        "project_id": "projectId",
        "granularity": "granularity",
        "id": "id",
        "namespace": "namespace",
        "secret_name_template": "secretNameTemplate",
        "team_id": "teamId",
    },
)
class SecretsSyncVercelDestinationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_token: builtins.str,
        deployment_environments: typing.Sequence[builtins.str],
        name: builtins.str,
        project_id: builtins.str,
        granularity: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        secret_name_template: typing.Optional[builtins.str] = None,
        team_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param access_token: Vercel API access token with the permissions to manage environment variables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#access_token SecretsSyncVercelDestination#access_token}
        :param deployment_environments: Deployment environments where the environment variables are available. Accepts 'development', 'preview' & 'production'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#deployment_environments SecretsSyncVercelDestination#deployment_environments}
        :param name: Unique name of the Vercel destination. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#name SecretsSyncVercelDestination#name}
        :param project_id: Project ID where to manage environment variables. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#project_id SecretsSyncVercelDestination#project_id}
        :param granularity: Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#granularity SecretsSyncVercelDestination#granularity}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#id SecretsSyncVercelDestination#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#namespace SecretsSyncVercelDestination#namespace}
        :param secret_name_template: Template describing how to generate external secret names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#secret_name_template SecretsSyncVercelDestination#secret_name_template}
        :param team_id: Team ID the project belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#team_id SecretsSyncVercelDestination#team_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__835a25119e9761f812ce6f37f7107a046df71963d1ba467bac0b98c1fc84ac63)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument deployment_environments", value=deployment_environments, expected_type=type_hints["deployment_environments"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument granularity", value=granularity, expected_type=type_hints["granularity"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument secret_name_template", value=secret_name_template, expected_type=type_hints["secret_name_template"])
            check_type(argname="argument team_id", value=team_id, expected_type=type_hints["team_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_token": access_token,
            "deployment_environments": deployment_environments,
            "name": name,
            "project_id": project_id,
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
        if granularity is not None:
            self._values["granularity"] = granularity
        if id is not None:
            self._values["id"] = id
        if namespace is not None:
            self._values["namespace"] = namespace
        if secret_name_template is not None:
            self._values["secret_name_template"] = secret_name_template
        if team_id is not None:
            self._values["team_id"] = team_id

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
    def access_token(self) -> builtins.str:
        '''Vercel API access token with the permissions to manage environment variables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#access_token SecretsSyncVercelDestination#access_token}
        '''
        result = self._values.get("access_token")
        assert result is not None, "Required property 'access_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deployment_environments(self) -> typing.List[builtins.str]:
        '''Deployment environments where the environment variables are available. Accepts 'development', 'preview' & 'production'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#deployment_environments SecretsSyncVercelDestination#deployment_environments}
        '''
        result = self._values.get("deployment_environments")
        assert result is not None, "Required property 'deployment_environments' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Unique name of the Vercel destination.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#name SecretsSyncVercelDestination#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Project ID where to manage environment variables.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#project_id SecretsSyncVercelDestination#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def granularity(self) -> typing.Optional[builtins.str]:
        '''Determines what level of information is synced as a distinct resource at the destination. Can be 'secret-path' or 'secret-key'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#granularity SecretsSyncVercelDestination#granularity}
        '''
        result = self._values.get("granularity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#id SecretsSyncVercelDestination#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#namespace SecretsSyncVercelDestination#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how to generate external secret names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#secret_name_template SecretsSyncVercelDestination#secret_name_template}
        '''
        result = self._values.get("secret_name_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def team_id(self) -> typing.Optional[builtins.str]:
        '''Team ID the project belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/secrets_sync_vercel_destination#team_id SecretsSyncVercelDestination#team_id}
        '''
        result = self._values.get("team_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretsSyncVercelDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SecretsSyncVercelDestination",
    "SecretsSyncVercelDestinationConfig",
]

publication.publish()

def _typecheckingstub__56eb2c614585bc1ea324349483643e8d952dcec6edd20bc7e039e2d98252e08a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    access_token: builtins.str,
    deployment_environments: typing.Sequence[builtins.str],
    name: builtins.str,
    project_id: builtins.str,
    granularity: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    secret_name_template: typing.Optional[builtins.str] = None,
    team_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e17127899350d6f1e78745593600fad5c06d4d4c3c261bb8e3b46edc365faae4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88e5da473b3503fb84a6c7794391c42e02dea3c88ac1def9c192a6e93a3edfc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac3d4434e261bbc4e3342d32eea5738dee558de0ffa20278fe786ddabcde5169(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__055d08e9da8a2c62d8fe391124c1190098d54d97caccd3ec149609a69c882281(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5cb5b8eb6b3cc49ad96923651288552094244a38dcb398a5bb5599fa98272b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a2021e01ef10ec74940465d019e2fab66a7ab7482506634644c7fa4b676c64f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eac20cfce0befe4b61b632fdc9e996963732416d6529b5b3c916bbc07e8a5dbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9c8b77f6f38cb72f22fa05caabe0deb9b889f221305ab64d10a7c5333994e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce1d0f6e1cf69b66f974e6ecf762531fadac730ec5b6fd88e7e284fb5dba2269(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c9c3b1c3932ae0b043faf1c39f916fda36c33f42c90ecab24e1ea6a5c2979b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__835a25119e9761f812ce6f37f7107a046df71963d1ba467bac0b98c1fc84ac63(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    access_token: builtins.str,
    deployment_environments: typing.Sequence[builtins.str],
    name: builtins.str,
    project_id: builtins.str,
    granularity: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    secret_name_template: typing.Optional[builtins.str] = None,
    team_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
