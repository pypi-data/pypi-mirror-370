r'''
# `vault_aws_auth_backend_login`

Refer to the Terraform Registry for docs: [`vault_aws_auth_backend_login`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login).
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


class AwsAuthBackendLogin(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.awsAuthBackendLogin.AwsAuthBackendLogin",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login vault_aws_auth_backend_login}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: typing.Optional[builtins.str] = None,
        iam_http_request_method: typing.Optional[builtins.str] = None,
        iam_request_body: typing.Optional[builtins.str] = None,
        iam_request_headers: typing.Optional[builtins.str] = None,
        iam_request_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        nonce: typing.Optional[builtins.str] = None,
        pkcs7: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        signature: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login vault_aws_auth_backend_login} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: AWS Auth Backend to read the token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#backend AwsAuthBackendLogin#backend}
        :param iam_http_request_method: The HTTP method used in the signed request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_http_request_method AwsAuthBackendLogin#iam_http_request_method}
        :param iam_request_body: The Base64-encoded body of the signed request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_body AwsAuthBackendLogin#iam_request_body}
        :param iam_request_headers: The Base64-encoded, JSON serialized representation of the sts:GetCallerIdentity HTTP request headers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_headers AwsAuthBackendLogin#iam_request_headers}
        :param iam_request_url: The Base64-encoded HTTP URL used in the signed request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_url AwsAuthBackendLogin#iam_request_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#id AwsAuthBackendLogin#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity: Base64-encoded EC2 instance identity document to authenticate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#identity AwsAuthBackendLogin#identity}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#namespace AwsAuthBackendLogin#namespace}
        :param nonce: The nonce to be used for subsequent login requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#nonce AwsAuthBackendLogin#nonce}
        :param pkcs7: PKCS7 signature of the identity document to authenticate with, with all newline characters removed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#pkcs7 AwsAuthBackendLogin#pkcs7}
        :param role: AWS Auth Role to read the token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#role AwsAuthBackendLogin#role}
        :param signature: Base64-encoded SHA256 RSA signature of the instance identtiy document to authenticate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#signature AwsAuthBackendLogin#signature}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf23c043c17302c1f574ff18db36036c454a0d7b68af339e52bdebe01cdcfa04)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AwsAuthBackendLoginConfig(
            backend=backend,
            iam_http_request_method=iam_http_request_method,
            iam_request_body=iam_request_body,
            iam_request_headers=iam_request_headers,
            iam_request_url=iam_request_url,
            id=id,
            identity=identity,
            namespace=namespace,
            nonce=nonce,
            pkcs7=pkcs7,
            role=role,
            signature=signature,
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
        '''Generates CDKTF code for importing a AwsAuthBackendLogin resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AwsAuthBackendLogin to import.
        :param import_from_id: The id of the existing AwsAuthBackendLogin that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AwsAuthBackendLogin to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7827eaff0fd6fb5c24b8bcde2092a2bacad25d55d30259005f9b92095f4463f4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetIamHttpRequestMethod")
    def reset_iam_http_request_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamHttpRequestMethod", []))

    @jsii.member(jsii_name="resetIamRequestBody")
    def reset_iam_request_body(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRequestBody", []))

    @jsii.member(jsii_name="resetIamRequestHeaders")
    def reset_iam_request_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRequestHeaders", []))

    @jsii.member(jsii_name="resetIamRequestUrl")
    def reset_iam_request_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamRequestUrl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentity")
    def reset_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentity", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNonce")
    def reset_nonce(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNonce", []))

    @jsii.member(jsii_name="resetPkcs7")
    def reset_pkcs7(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPkcs7", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="resetSignature")
    def reset_signature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignature", []))

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
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @builtins.property
    @jsii.member(jsii_name="clientToken")
    def client_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientToken"))

    @builtins.property
    @jsii.member(jsii_name="leaseDuration")
    def lease_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "leaseDuration"))

    @builtins.property
    @jsii.member(jsii_name="leaseStartTime")
    def lease_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "leaseStartTime"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="renewable")
    def renewable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "renewable"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="iamHttpRequestMethodInput")
    def iam_http_request_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamHttpRequestMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="iamRequestBodyInput")
    def iam_request_body_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRequestBodyInput"))

    @builtins.property
    @jsii.member(jsii_name="iamRequestHeadersInput")
    def iam_request_headers_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRequestHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="iamRequestUrlInput")
    def iam_request_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamRequestUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="identityInput")
    def identity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="nonceInput")
    def nonce_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nonceInput"))

    @builtins.property
    @jsii.member(jsii_name="pkcs7Input")
    def pkcs7_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pkcs7Input"))

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureInput")
    def signature_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signatureInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fce4dc6fc8a5476c00ea7f25db571d2555f4acd23894b616aa1d1dfd695d6fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamHttpRequestMethod")
    def iam_http_request_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamHttpRequestMethod"))

    @iam_http_request_method.setter
    def iam_http_request_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e23419a9bfd938ffee23af4c3e71f027809f5ee542cf2571de1430f8fb580c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamHttpRequestMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamRequestBody")
    def iam_request_body(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRequestBody"))

    @iam_request_body.setter
    def iam_request_body(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b62b125cbd38b40fe0be35d595bc61022a9f0d50ecf9af1421ef1099a021931d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamRequestBody", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamRequestHeaders")
    def iam_request_headers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRequestHeaders"))

    @iam_request_headers.setter
    def iam_request_headers(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56a77e0e46c9652972f5d6a2a2d95e4f3ddc2e7007f0c2a54158708169ff441f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamRequestHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="iamRequestUrl")
    def iam_request_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamRequestUrl"))

    @iam_request_url.setter
    def iam_request_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ced9811cb2736d63a340198b9357b541f2ecec06d52ce6bd02ccc1c00180425e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamRequestUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b35a095c3c17d922383a3c95e8ecfb7fc4a15ad066d752d7ecebcccc092f613)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identity")
    def identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identity"))

    @identity.setter
    def identity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8a654bd1f6a2b463536bccfd8e49f1facc82b3bbb636c41a240207e30a345ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3d80fa52c1dbea2f7750cb70075d8c727eb0896eccef69fed6bbdd6788c6754)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nonce")
    def nonce(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nonce"))

    @nonce.setter
    def nonce(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e4c4f58ab1a163e7106d571b0720c116ec99655a4b0a1aeb9102c9b6be01b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nonce", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pkcs7")
    def pkcs7(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pkcs7"))

    @pkcs7.setter
    def pkcs7(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30674eb0ed283be57ea3303cefc2abfc5b765f427b1012ca1b294ea676ceb91a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pkcs7", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d91c9146739701046f340e6f68a816e7abc69d2eb87e36069fd1a608d356d33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signature")
    def signature(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signature"))

    @signature.setter
    def signature(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc0ee144edc00d98a28d68372b260c3d0cd9a0ccd9d38efad39de8e30959f434)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signature", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.awsAuthBackendLogin.AwsAuthBackendLoginConfig",
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
        "iam_http_request_method": "iamHttpRequestMethod",
        "iam_request_body": "iamRequestBody",
        "iam_request_headers": "iamRequestHeaders",
        "iam_request_url": "iamRequestUrl",
        "id": "id",
        "identity": "identity",
        "namespace": "namespace",
        "nonce": "nonce",
        "pkcs7": "pkcs7",
        "role": "role",
        "signature": "signature",
    },
)
class AwsAuthBackendLoginConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backend: typing.Optional[builtins.str] = None,
        iam_http_request_method: typing.Optional[builtins.str] = None,
        iam_request_body: typing.Optional[builtins.str] = None,
        iam_request_headers: typing.Optional[builtins.str] = None,
        iam_request_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        identity: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        nonce: typing.Optional[builtins.str] = None,
        pkcs7: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        signature: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: AWS Auth Backend to read the token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#backend AwsAuthBackendLogin#backend}
        :param iam_http_request_method: The HTTP method used in the signed request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_http_request_method AwsAuthBackendLogin#iam_http_request_method}
        :param iam_request_body: The Base64-encoded body of the signed request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_body AwsAuthBackendLogin#iam_request_body}
        :param iam_request_headers: The Base64-encoded, JSON serialized representation of the sts:GetCallerIdentity HTTP request headers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_headers AwsAuthBackendLogin#iam_request_headers}
        :param iam_request_url: The Base64-encoded HTTP URL used in the signed request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_url AwsAuthBackendLogin#iam_request_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#id AwsAuthBackendLogin#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity: Base64-encoded EC2 instance identity document to authenticate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#identity AwsAuthBackendLogin#identity}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#namespace AwsAuthBackendLogin#namespace}
        :param nonce: The nonce to be used for subsequent login requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#nonce AwsAuthBackendLogin#nonce}
        :param pkcs7: PKCS7 signature of the identity document to authenticate with, with all newline characters removed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#pkcs7 AwsAuthBackendLogin#pkcs7}
        :param role: AWS Auth Role to read the token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#role AwsAuthBackendLogin#role}
        :param signature: Base64-encoded SHA256 RSA signature of the instance identtiy document to authenticate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#signature AwsAuthBackendLogin#signature}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23b6786635c5bd766f9dbd4a052b9a3de6496be11ac8f1d3adca40b7725e6793)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument iam_http_request_method", value=iam_http_request_method, expected_type=type_hints["iam_http_request_method"])
            check_type(argname="argument iam_request_body", value=iam_request_body, expected_type=type_hints["iam_request_body"])
            check_type(argname="argument iam_request_headers", value=iam_request_headers, expected_type=type_hints["iam_request_headers"])
            check_type(argname="argument iam_request_url", value=iam_request_url, expected_type=type_hints["iam_request_url"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument nonce", value=nonce, expected_type=type_hints["nonce"])
            check_type(argname="argument pkcs7", value=pkcs7, expected_type=type_hints["pkcs7"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument signature", value=signature, expected_type=type_hints["signature"])
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
        if backend is not None:
            self._values["backend"] = backend
        if iam_http_request_method is not None:
            self._values["iam_http_request_method"] = iam_http_request_method
        if iam_request_body is not None:
            self._values["iam_request_body"] = iam_request_body
        if iam_request_headers is not None:
            self._values["iam_request_headers"] = iam_request_headers
        if iam_request_url is not None:
            self._values["iam_request_url"] = iam_request_url
        if id is not None:
            self._values["id"] = id
        if identity is not None:
            self._values["identity"] = identity
        if namespace is not None:
            self._values["namespace"] = namespace
        if nonce is not None:
            self._values["nonce"] = nonce
        if pkcs7 is not None:
            self._values["pkcs7"] = pkcs7
        if role is not None:
            self._values["role"] = role
        if signature is not None:
            self._values["signature"] = signature

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
    def backend(self) -> typing.Optional[builtins.str]:
        '''AWS Auth Backend to read the token from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#backend AwsAuthBackendLogin#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_http_request_method(self) -> typing.Optional[builtins.str]:
        '''The HTTP method used in the signed request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_http_request_method AwsAuthBackendLogin#iam_http_request_method}
        '''
        result = self._values.get("iam_http_request_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_request_body(self) -> typing.Optional[builtins.str]:
        '''The Base64-encoded body of the signed request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_body AwsAuthBackendLogin#iam_request_body}
        '''
        result = self._values.get("iam_request_body")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_request_headers(self) -> typing.Optional[builtins.str]:
        '''The Base64-encoded, JSON serialized representation of the sts:GetCallerIdentity HTTP request headers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_headers AwsAuthBackendLogin#iam_request_headers}
        '''
        result = self._values.get("iam_request_headers")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam_request_url(self) -> typing.Optional[builtins.str]:
        '''The Base64-encoded HTTP URL used in the signed request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#iam_request_url AwsAuthBackendLogin#iam_request_url}
        '''
        result = self._values.get("iam_request_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#id AwsAuthBackendLogin#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded EC2 instance identity document to authenticate with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#identity AwsAuthBackendLogin#identity}
        '''
        result = self._values.get("identity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#namespace AwsAuthBackendLogin#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nonce(self) -> typing.Optional[builtins.str]:
        '''The nonce to be used for subsequent login requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#nonce AwsAuthBackendLogin#nonce}
        '''
        result = self._values.get("nonce")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pkcs7(self) -> typing.Optional[builtins.str]:
        '''PKCS7 signature of the identity document to authenticate with, with all newline characters removed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#pkcs7 AwsAuthBackendLogin#pkcs7}
        '''
        result = self._values.get("pkcs7")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''AWS Auth Role to read the token from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#role AwsAuthBackendLogin#role}
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded SHA256 RSA signature of the instance identtiy document to authenticate with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/aws_auth_backend_login#signature AwsAuthBackendLogin#signature}
        '''
        result = self._values.get("signature")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsAuthBackendLoginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsAuthBackendLogin",
    "AwsAuthBackendLoginConfig",
]

publication.publish()

def _typecheckingstub__bf23c043c17302c1f574ff18db36036c454a0d7b68af339e52bdebe01cdcfa04(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: typing.Optional[builtins.str] = None,
    iam_http_request_method: typing.Optional[builtins.str] = None,
    iam_request_body: typing.Optional[builtins.str] = None,
    iam_request_headers: typing.Optional[builtins.str] = None,
    iam_request_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    identity: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    nonce: typing.Optional[builtins.str] = None,
    pkcs7: typing.Optional[builtins.str] = None,
    role: typing.Optional[builtins.str] = None,
    signature: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__7827eaff0fd6fb5c24b8bcde2092a2bacad25d55d30259005f9b92095f4463f4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fce4dc6fc8a5476c00ea7f25db571d2555f4acd23894b616aa1d1dfd695d6fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e23419a9bfd938ffee23af4c3e71f027809f5ee542cf2571de1430f8fb580c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b62b125cbd38b40fe0be35d595bc61022a9f0d50ecf9af1421ef1099a021931d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56a77e0e46c9652972f5d6a2a2d95e4f3ddc2e7007f0c2a54158708169ff441f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ced9811cb2736d63a340198b9357b541f2ecec06d52ce6bd02ccc1c00180425e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b35a095c3c17d922383a3c95e8ecfb7fc4a15ad066d752d7ecebcccc092f613(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8a654bd1f6a2b463536bccfd8e49f1facc82b3bbb636c41a240207e30a345ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3d80fa52c1dbea2f7750cb70075d8c727eb0896eccef69fed6bbdd6788c6754(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e4c4f58ab1a163e7106d571b0720c116ec99655a4b0a1aeb9102c9b6be01b47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30674eb0ed283be57ea3303cefc2abfc5b765f427b1012ca1b294ea676ceb91a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d91c9146739701046f340e6f68a816e7abc69d2eb87e36069fd1a608d356d33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc0ee144edc00d98a28d68372b260c3d0cd9a0ccd9d38efad39de8e30959f434(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23b6786635c5bd766f9dbd4a052b9a3de6496be11ac8f1d3adca40b7725e6793(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: typing.Optional[builtins.str] = None,
    iam_http_request_method: typing.Optional[builtins.str] = None,
    iam_request_body: typing.Optional[builtins.str] = None,
    iam_request_headers: typing.Optional[builtins.str] = None,
    iam_request_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    identity: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    nonce: typing.Optional[builtins.str] = None,
    pkcs7: typing.Optional[builtins.str] = None,
    role: typing.Optional[builtins.str] = None,
    signature: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
