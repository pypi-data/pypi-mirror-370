r'''
# `vault_identity_oidc_client`

Refer to the Terraform Registry for docs: [`vault_identity_oidc_client`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client).
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


class IdentityOidcClient(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.identityOidcClient.IdentityOidcClient",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client vault_identity_oidc_client}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        access_token_ttl: typing.Optional[jsii.Number] = None,
        assignments: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        id_token_ttl: typing.Optional[jsii.Number] = None,
        key: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client vault_identity_oidc_client} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#name IdentityOidcClient#name}
        :param access_token_ttl: The time-to-live for access tokens obtained by the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#access_token_ttl IdentityOidcClient#access_token_ttl}
        :param assignments: A list of assignment resources associated with the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#assignments IdentityOidcClient#assignments}
        :param client_type: The client type based on its ability to maintain confidentiality of credentials.Defaults to 'confidential'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#client_type IdentityOidcClient#client_type}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#id IdentityOidcClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param id_token_ttl: The time-to-live for ID tokens obtained by the client. The value should be less than the verification_ttl on the key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#id_token_ttl IdentityOidcClient#id_token_ttl}
        :param key: A reference to a named key resource in Vault. This cannot be modified after creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#key IdentityOidcClient#key}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#namespace IdentityOidcClient#namespace}
        :param redirect_uris: Redirection URI values used by the client. One of these values must exactly match the redirect_uri parameter value used in each authentication request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#redirect_uris IdentityOidcClient#redirect_uris}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93cb5e31114f7b2a2972142ad38d59a2d0e85cc44adc33fa491a308cb274314e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = IdentityOidcClientConfig(
            name=name,
            access_token_ttl=access_token_ttl,
            assignments=assignments,
            client_type=client_type,
            id=id,
            id_token_ttl=id_token_ttl,
            key=key,
            namespace=namespace,
            redirect_uris=redirect_uris,
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
        '''Generates CDKTF code for importing a IdentityOidcClient resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the IdentityOidcClient to import.
        :param import_from_id: The id of the existing IdentityOidcClient that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the IdentityOidcClient to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe0e676562e70084a76abe6efa0c261304c3458c39ec675b3ced6b253ac2974d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessTokenTtl")
    def reset_access_token_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessTokenTtl", []))

    @jsii.member(jsii_name="resetAssignments")
    def reset_assignments(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssignments", []))

    @jsii.member(jsii_name="resetClientType")
    def reset_client_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientType", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdTokenTtl")
    def reset_id_token_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdTokenTtl", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRedirectUris")
    def reset_redirect_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectUris", []))

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
    @jsii.member(jsii_name="accessTokenTtlInput")
    def access_token_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessTokenTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="assignmentsInput")
    def assignments_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "assignmentsInput"))

    @builtins.property
    @jsii.member(jsii_name="clientTypeInput")
    def client_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="idTokenTtlInput")
    def id_token_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idTokenTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectUrisInput")
    def redirect_uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "redirectUrisInput"))

    @builtins.property
    @jsii.member(jsii_name="accessTokenTtl")
    def access_token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessTokenTtl"))

    @access_token_ttl.setter
    def access_token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fca4aaec77b4e1c59da381844d7cfaf7b2196ee39f7ede0962aecc96dc194879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessTokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="assignments")
    def assignments(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "assignments"))

    @assignments.setter
    def assignments(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d91d57cf942035f18c9f48c4560cabd8f8749837e59ba5bae3f15df9f60b553)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assignments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientType")
    def client_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientType"))

    @client_type.setter
    def client_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f536f00345316720bedb12a113258b1abaa61a91fca34adafafc68ac9eb02273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16408fe9ad209ea596f5ae20c85a5f4ba12699bb11d8de5e80359b8b2cc36ed1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idTokenTtl")
    def id_token_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idTokenTtl"))

    @id_token_ttl.setter
    def id_token_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cc89ce8c8e0e3333cac1c3960371a73a96597ea7b3debed3314c78796375ceb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idTokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d705357e399570471d2803516dcf7b488d0630ec1cdd9e9c125d0cac84db5a4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d241bb7c7448004c73b77b66d04e9b3279671727078a7802acb5da825395a77f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__712ad885a3a87e5a93f48295f16a55ee2f38d39f0d9148b6dcff457b13fb1c99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redirectUris")
    def redirect_uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "redirectUris"))

    @redirect_uris.setter
    def redirect_uris(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b87c6436ffa4ec4a060ea80a5bef6849df79cf259ae42def470b4a1e45ff01b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectUris", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.identityOidcClient.IdentityOidcClientConfig",
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
        "access_token_ttl": "accessTokenTtl",
        "assignments": "assignments",
        "client_type": "clientType",
        "id": "id",
        "id_token_ttl": "idTokenTtl",
        "key": "key",
        "namespace": "namespace",
        "redirect_uris": "redirectUris",
    },
)
class IdentityOidcClientConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_token_ttl: typing.Optional[jsii.Number] = None,
        assignments: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_type: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        id_token_ttl: typing.Optional[jsii.Number] = None,
        key: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: The name of the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#name IdentityOidcClient#name}
        :param access_token_ttl: The time-to-live for access tokens obtained by the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#access_token_ttl IdentityOidcClient#access_token_ttl}
        :param assignments: A list of assignment resources associated with the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#assignments IdentityOidcClient#assignments}
        :param client_type: The client type based on its ability to maintain confidentiality of credentials.Defaults to 'confidential'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#client_type IdentityOidcClient#client_type}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#id IdentityOidcClient#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param id_token_ttl: The time-to-live for ID tokens obtained by the client. The value should be less than the verification_ttl on the key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#id_token_ttl IdentityOidcClient#id_token_ttl}
        :param key: A reference to a named key resource in Vault. This cannot be modified after creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#key IdentityOidcClient#key}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#namespace IdentityOidcClient#namespace}
        :param redirect_uris: Redirection URI values used by the client. One of these values must exactly match the redirect_uri parameter value used in each authentication request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#redirect_uris IdentityOidcClient#redirect_uris}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724a7a9bda44626ac097801911762dea5fa59147f474f952fc38d5fb6674f112)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_token_ttl", value=access_token_ttl, expected_type=type_hints["access_token_ttl"])
            check_type(argname="argument assignments", value=assignments, expected_type=type_hints["assignments"])
            check_type(argname="argument client_type", value=client_type, expected_type=type_hints["client_type"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument id_token_ttl", value=id_token_ttl, expected_type=type_hints["id_token_ttl"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument redirect_uris", value=redirect_uris, expected_type=type_hints["redirect_uris"])
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
        if access_token_ttl is not None:
            self._values["access_token_ttl"] = access_token_ttl
        if assignments is not None:
            self._values["assignments"] = assignments
        if client_type is not None:
            self._values["client_type"] = client_type
        if id is not None:
            self._values["id"] = id
        if id_token_ttl is not None:
            self._values["id_token_ttl"] = id_token_ttl
        if key is not None:
            self._values["key"] = key
        if namespace is not None:
            self._values["namespace"] = namespace
        if redirect_uris is not None:
            self._values["redirect_uris"] = redirect_uris

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
        '''The name of the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#name IdentityOidcClient#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The time-to-live for access tokens obtained by the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#access_token_ttl IdentityOidcClient#access_token_ttl}
        '''
        result = self._values.get("access_token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def assignments(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of assignment resources associated with the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#assignments IdentityOidcClient#assignments}
        '''
        result = self._values.get("assignments")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def client_type(self) -> typing.Optional[builtins.str]:
        '''The client type based on its ability to maintain confidentiality of credentials.Defaults to 'confidential'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#client_type IdentityOidcClient#client_type}
        '''
        result = self._values.get("client_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#id IdentityOidcClient#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id_token_ttl(self) -> typing.Optional[jsii.Number]:
        '''The time-to-live for ID tokens obtained by the client.

        The value should be less than the verification_ttl on the key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#id_token_ttl IdentityOidcClient#id_token_ttl}
        '''
        result = self._values.get("id_token_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''A reference to a named key resource in Vault. This cannot be modified after creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#key IdentityOidcClient#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#namespace IdentityOidcClient#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect_uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Redirection URI values used by the client.

        One of these values must exactly match the redirect_uri parameter value used in each authentication request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/identity_oidc_client#redirect_uris IdentityOidcClient#redirect_uris}
        '''
        result = self._values.get("redirect_uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityOidcClientConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IdentityOidcClient",
    "IdentityOidcClientConfig",
]

publication.publish()

def _typecheckingstub__93cb5e31114f7b2a2972142ad38d59a2d0e85cc44adc33fa491a308cb274314e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    access_token_ttl: typing.Optional[jsii.Number] = None,
    assignments: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_type: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    id_token_ttl: typing.Optional[jsii.Number] = None,
    key: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__fe0e676562e70084a76abe6efa0c261304c3458c39ec675b3ced6b253ac2974d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fca4aaec77b4e1c59da381844d7cfaf7b2196ee39f7ede0962aecc96dc194879(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d91d57cf942035f18c9f48c4560cabd8f8749837e59ba5bae3f15df9f60b553(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f536f00345316720bedb12a113258b1abaa61a91fca34adafafc68ac9eb02273(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16408fe9ad209ea596f5ae20c85a5f4ba12699bb11d8de5e80359b8b2cc36ed1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cc89ce8c8e0e3333cac1c3960371a73a96597ea7b3debed3314c78796375ceb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d705357e399570471d2803516dcf7b488d0630ec1cdd9e9c125d0cac84db5a4b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d241bb7c7448004c73b77b66d04e9b3279671727078a7802acb5da825395a77f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712ad885a3a87e5a93f48295f16a55ee2f38d39f0d9148b6dcff457b13fb1c99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b87c6436ffa4ec4a060ea80a5bef6849df79cf259ae42def470b4a1e45ff01b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724a7a9bda44626ac097801911762dea5fa59147f474f952fc38d5fb6674f112(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    access_token_ttl: typing.Optional[jsii.Number] = None,
    assignments: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_type: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    id_token_ttl: typing.Optional[jsii.Number] = None,
    key: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
