r'''
# `vault_kubernetes_auth_backend_config`

Refer to the Terraform Registry for docs: [`vault_kubernetes_auth_backend_config`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config).
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


class KubernetesAuthBackendConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.kubernetesAuthBackendConfig.KubernetesAuthBackendConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config vault_kubernetes_auth_backend_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        kubernetes_host: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        disable_iss_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
        kubernetes_ca_cert: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        pem_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_reviewer_jwt: typing.Optional[builtins.str] = None,
        use_annotations_as_alias_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config vault_kubernetes_auth_backend_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param kubernetes_host: Host must be a host string, a host:port pair, or a URL to the base of the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#kubernetes_host KubernetesAuthBackendConfig#kubernetes_host}
        :param backend: Unique name of the kubernetes backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#backend KubernetesAuthBackendConfig#backend}
        :param disable_iss_validation: Optional disable JWT issuer validation. Allows to skip ISS validation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#disable_iss_validation KubernetesAuthBackendConfig#disable_iss_validation}
        :param disable_local_ca_jwt: Optional disable defaulting to the local CA cert and service account JWT when running in a Kubernetes pod. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#disable_local_ca_jwt KubernetesAuthBackendConfig#disable_local_ca_jwt}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#id KubernetesAuthBackendConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Optional JWT issuer. If no issuer is specified, kubernetes.io/serviceaccount will be used as the default issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#issuer KubernetesAuthBackendConfig#issuer}
        :param kubernetes_ca_cert: PEM encoded CA cert for use by the TLS client used to talk with the Kubernetes API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#kubernetes_ca_cert KubernetesAuthBackendConfig#kubernetes_ca_cert}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#namespace KubernetesAuthBackendConfig#namespace}
        :param pem_keys: Optional list of PEM-formatted public keys or certificates used to verify the signatures of Kubernetes service account JWTs. If a certificate is given, its public key will be extracted. Not every installation of Kubernetes exposes these keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#pem_keys KubernetesAuthBackendConfig#pem_keys}
        :param token_reviewer_jwt: A service account JWT (or other token) used as a bearer token to access the TokenReview API to validate other JWTs during login. If not set the JWT used for login will be used to access the API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#token_reviewer_jwt KubernetesAuthBackendConfig#token_reviewer_jwt}
        :param use_annotations_as_alias_metadata: Use annotations from the client token's associated service account as alias metadata for the Vault entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#use_annotations_as_alias_metadata KubernetesAuthBackendConfig#use_annotations_as_alias_metadata}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__357cbc145f6d3f2fa55b04e95630a83646819e69ff2b4c9ad0e42997f7ce47ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = KubernetesAuthBackendConfigConfig(
            kubernetes_host=kubernetes_host,
            backend=backend,
            disable_iss_validation=disable_iss_validation,
            disable_local_ca_jwt=disable_local_ca_jwt,
            id=id,
            issuer=issuer,
            kubernetes_ca_cert=kubernetes_ca_cert,
            namespace=namespace,
            pem_keys=pem_keys,
            token_reviewer_jwt=token_reviewer_jwt,
            use_annotations_as_alias_metadata=use_annotations_as_alias_metadata,
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
        '''Generates CDKTF code for importing a KubernetesAuthBackendConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KubernetesAuthBackendConfig to import.
        :param import_from_id: The id of the existing KubernetesAuthBackendConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KubernetesAuthBackendConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93b21b7df0d4a4284ebdf45d7ef2262b145c5bc70fb0a7688bbbb067db0f1956)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetDisableIssValidation")
    def reset_disable_iss_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableIssValidation", []))

    @jsii.member(jsii_name="resetDisableLocalCaJwt")
    def reset_disable_local_ca_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableLocalCaJwt", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIssuer")
    def reset_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuer", []))

    @jsii.member(jsii_name="resetKubernetesCaCert")
    def reset_kubernetes_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKubernetesCaCert", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPemKeys")
    def reset_pem_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemKeys", []))

    @jsii.member(jsii_name="resetTokenReviewerJwt")
    def reset_token_reviewer_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenReviewerJwt", []))

    @jsii.member(jsii_name="resetUseAnnotationsAsAliasMetadata")
    def reset_use_annotations_as_alias_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseAnnotationsAsAliasMetadata", []))

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
    @jsii.member(jsii_name="disableIssValidationInput")
    def disable_iss_validation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableIssValidationInput"))

    @builtins.property
    @jsii.member(jsii_name="disableLocalCaJwtInput")
    def disable_local_ca_jwt_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableLocalCaJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerInput")
    def issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerInput"))

    @builtins.property
    @jsii.member(jsii_name="kubernetesCaCertInput")
    def kubernetes_ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kubernetesCaCertInput"))

    @builtins.property
    @jsii.member(jsii_name="kubernetesHostInput")
    def kubernetes_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kubernetesHostInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="pemKeysInput")
    def pem_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pemKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenReviewerJwtInput")
    def token_reviewer_jwt_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenReviewerJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="useAnnotationsAsAliasMetadataInput")
    def use_annotations_as_alias_metadata_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useAnnotationsAsAliasMetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__474c5b1f7ef06936f6c0bb90b6f27829578ece7e71ec46c982877495aee4969a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableIssValidation")
    def disable_iss_validation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableIssValidation"))

    @disable_iss_validation.setter
    def disable_iss_validation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ad43f397148c570689b82f9a5a59ed36feb51e809b483ab17e6df23939623c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableIssValidation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableLocalCaJwt")
    def disable_local_ca_jwt(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableLocalCaJwt"))

    @disable_local_ca_jwt.setter
    def disable_local_ca_jwt(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d515246c8c4db70ab04f5a9055bc0fe989ea4fd8ec2ff460d3a28cb842a46dcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableLocalCaJwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9de903021450b319299495c52e239e4507e6fa17fbbb90787e8f4b7861294e14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccc29b218d1492dac52651cb24d1bd727d73db2f8b3249f29fb9369c1e663c64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kubernetesCaCert")
    def kubernetes_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kubernetesCaCert"))

    @kubernetes_ca_cert.setter
    def kubernetes_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4381a457df4c8868623796667dd0325082c900370a498232348c62a1325e7d71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kubernetesCaCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kubernetesHost")
    def kubernetes_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kubernetesHost"))

    @kubernetes_host.setter
    def kubernetes_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4c54cca71251e3774e8369ac1ebcd1b852b0b4f23855a15893a610936d5433f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kubernetesHost", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1450af9b4cc7158825e3f1ff6036da62094726e6a45e8b0537ca96c4f3c46cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemKeys")
    def pem_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pemKeys"))

    @pem_keys.setter
    def pem_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43c726daa674166459bc1496c18f850c0af6ffc4a128f5bcb67360532f271fca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenReviewerJwt")
    def token_reviewer_jwt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenReviewerJwt"))

    @token_reviewer_jwt.setter
    def token_reviewer_jwt(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a41e28602acb30b9a8b6766c656b717b55a80aadd1213a6870a469b2d6b052d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenReviewerJwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useAnnotationsAsAliasMetadata")
    def use_annotations_as_alias_metadata(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useAnnotationsAsAliasMetadata"))

    @use_annotations_as_alias_metadata.setter
    def use_annotations_as_alias_metadata(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79304e868267e5d64de37c5f67a91650a1c844e87176ee09a7e81174bcf3ab83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useAnnotationsAsAliasMetadata", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.kubernetesAuthBackendConfig.KubernetesAuthBackendConfigConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "kubernetes_host": "kubernetesHost",
        "backend": "backend",
        "disable_iss_validation": "disableIssValidation",
        "disable_local_ca_jwt": "disableLocalCaJwt",
        "id": "id",
        "issuer": "issuer",
        "kubernetes_ca_cert": "kubernetesCaCert",
        "namespace": "namespace",
        "pem_keys": "pemKeys",
        "token_reviewer_jwt": "tokenReviewerJwt",
        "use_annotations_as_alias_metadata": "useAnnotationsAsAliasMetadata",
    },
)
class KubernetesAuthBackendConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        kubernetes_host: builtins.str,
        backend: typing.Optional[builtins.str] = None,
        disable_iss_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
        kubernetes_ca_cert: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        pem_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_reviewer_jwt: typing.Optional[builtins.str] = None,
        use_annotations_as_alias_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param kubernetes_host: Host must be a host string, a host:port pair, or a URL to the base of the Kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#kubernetes_host KubernetesAuthBackendConfig#kubernetes_host}
        :param backend: Unique name of the kubernetes backend to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#backend KubernetesAuthBackendConfig#backend}
        :param disable_iss_validation: Optional disable JWT issuer validation. Allows to skip ISS validation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#disable_iss_validation KubernetesAuthBackendConfig#disable_iss_validation}
        :param disable_local_ca_jwt: Optional disable defaulting to the local CA cert and service account JWT when running in a Kubernetes pod. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#disable_local_ca_jwt KubernetesAuthBackendConfig#disable_local_ca_jwt}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#id KubernetesAuthBackendConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Optional JWT issuer. If no issuer is specified, kubernetes.io/serviceaccount will be used as the default issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#issuer KubernetesAuthBackendConfig#issuer}
        :param kubernetes_ca_cert: PEM encoded CA cert for use by the TLS client used to talk with the Kubernetes API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#kubernetes_ca_cert KubernetesAuthBackendConfig#kubernetes_ca_cert}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#namespace KubernetesAuthBackendConfig#namespace}
        :param pem_keys: Optional list of PEM-formatted public keys or certificates used to verify the signatures of Kubernetes service account JWTs. If a certificate is given, its public key will be extracted. Not every installation of Kubernetes exposes these keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#pem_keys KubernetesAuthBackendConfig#pem_keys}
        :param token_reviewer_jwt: A service account JWT (or other token) used as a bearer token to access the TokenReview API to validate other JWTs during login. If not set the JWT used for login will be used to access the API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#token_reviewer_jwt KubernetesAuthBackendConfig#token_reviewer_jwt}
        :param use_annotations_as_alias_metadata: Use annotations from the client token's associated service account as alias metadata for the Vault entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#use_annotations_as_alias_metadata KubernetesAuthBackendConfig#use_annotations_as_alias_metadata}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0f267a61313c0a3bb26593cfb7d61acf3b95579b14cbe8541cde2e7a7beb872)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument kubernetes_host", value=kubernetes_host, expected_type=type_hints["kubernetes_host"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument disable_iss_validation", value=disable_iss_validation, expected_type=type_hints["disable_iss_validation"])
            check_type(argname="argument disable_local_ca_jwt", value=disable_local_ca_jwt, expected_type=type_hints["disable_local_ca_jwt"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issuer", value=issuer, expected_type=type_hints["issuer"])
            check_type(argname="argument kubernetes_ca_cert", value=kubernetes_ca_cert, expected_type=type_hints["kubernetes_ca_cert"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument pem_keys", value=pem_keys, expected_type=type_hints["pem_keys"])
            check_type(argname="argument token_reviewer_jwt", value=token_reviewer_jwt, expected_type=type_hints["token_reviewer_jwt"])
            check_type(argname="argument use_annotations_as_alias_metadata", value=use_annotations_as_alias_metadata, expected_type=type_hints["use_annotations_as_alias_metadata"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "kubernetes_host": kubernetes_host,
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
        if disable_iss_validation is not None:
            self._values["disable_iss_validation"] = disable_iss_validation
        if disable_local_ca_jwt is not None:
            self._values["disable_local_ca_jwt"] = disable_local_ca_jwt
        if id is not None:
            self._values["id"] = id
        if issuer is not None:
            self._values["issuer"] = issuer
        if kubernetes_ca_cert is not None:
            self._values["kubernetes_ca_cert"] = kubernetes_ca_cert
        if namespace is not None:
            self._values["namespace"] = namespace
        if pem_keys is not None:
            self._values["pem_keys"] = pem_keys
        if token_reviewer_jwt is not None:
            self._values["token_reviewer_jwt"] = token_reviewer_jwt
        if use_annotations_as_alias_metadata is not None:
            self._values["use_annotations_as_alias_metadata"] = use_annotations_as_alias_metadata

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
    def kubernetes_host(self) -> builtins.str:
        '''Host must be a host string, a host:port pair, or a URL to the base of the Kubernetes API server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#kubernetes_host KubernetesAuthBackendConfig#kubernetes_host}
        '''
        result = self._values.get("kubernetes_host")
        assert result is not None, "Required property 'kubernetes_host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backend(self) -> typing.Optional[builtins.str]:
        '''Unique name of the kubernetes backend to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#backend KubernetesAuthBackendConfig#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_iss_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Optional disable JWT issuer validation. Allows to skip ISS validation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#disable_iss_validation KubernetesAuthBackendConfig#disable_iss_validation}
        '''
        result = self._values.get("disable_iss_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_local_ca_jwt(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Optional disable defaulting to the local CA cert and service account JWT when running in a Kubernetes pod.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#disable_local_ca_jwt KubernetesAuthBackendConfig#disable_local_ca_jwt}
        '''
        result = self._values.get("disable_local_ca_jwt")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#id KubernetesAuthBackendConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issuer(self) -> typing.Optional[builtins.str]:
        '''Optional JWT issuer. If no issuer is specified, kubernetes.io/serviceaccount will be used as the default issuer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#issuer KubernetesAuthBackendConfig#issuer}
        '''
        result = self._values.get("issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kubernetes_ca_cert(self) -> typing.Optional[builtins.str]:
        '''PEM encoded CA cert for use by the TLS client used to talk with the Kubernetes API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#kubernetes_ca_cert KubernetesAuthBackendConfig#kubernetes_ca_cert}
        '''
        result = self._values.get("kubernetes_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#namespace KubernetesAuthBackendConfig#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Optional list of PEM-formatted public keys or certificates used to verify the signatures of Kubernetes service account JWTs.

        If a certificate is given, its public key will be extracted. Not every installation of Kubernetes exposes these keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#pem_keys KubernetesAuthBackendConfig#pem_keys}
        '''
        result = self._values.get("pem_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_reviewer_jwt(self) -> typing.Optional[builtins.str]:
        '''A service account JWT (or other token) used as a bearer token to access the TokenReview API to validate other JWTs during login.

        If not set the JWT used for login will be used to access the API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#token_reviewer_jwt KubernetesAuthBackendConfig#token_reviewer_jwt}
        '''
        result = self._values.get("token_reviewer_jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_annotations_as_alias_metadata(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use annotations from the client token's associated service account as alias metadata for the Vault entity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_auth_backend_config#use_annotations_as_alias_metadata KubernetesAuthBackendConfig#use_annotations_as_alias_metadata}
        '''
        result = self._values.get("use_annotations_as_alias_metadata")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesAuthBackendConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KubernetesAuthBackendConfig",
    "KubernetesAuthBackendConfigConfig",
]

publication.publish()

def _typecheckingstub__357cbc145f6d3f2fa55b04e95630a83646819e69ff2b4c9ad0e42997f7ce47ca(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    kubernetes_host: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    disable_iss_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    kubernetes_ca_cert: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    pem_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_reviewer_jwt: typing.Optional[builtins.str] = None,
    use_annotations_as_alias_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__93b21b7df0d4a4284ebdf45d7ef2262b145c5bc70fb0a7688bbbb067db0f1956(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__474c5b1f7ef06936f6c0bb90b6f27829578ece7e71ec46c982877495aee4969a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ad43f397148c570689b82f9a5a59ed36feb51e809b483ab17e6df23939623c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d515246c8c4db70ab04f5a9055bc0fe989ea4fd8ec2ff460d3a28cb842a46dcd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9de903021450b319299495c52e239e4507e6fa17fbbb90787e8f4b7861294e14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccc29b218d1492dac52651cb24d1bd727d73db2f8b3249f29fb9369c1e663c64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4381a457df4c8868623796667dd0325082c900370a498232348c62a1325e7d71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4c54cca71251e3774e8369ac1ebcd1b852b0b4f23855a15893a610936d5433f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1450af9b4cc7158825e3f1ff6036da62094726e6a45e8b0537ca96c4f3c46cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43c726daa674166459bc1496c18f850c0af6ffc4a128f5bcb67360532f271fca(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a41e28602acb30b9a8b6766c656b717b55a80aadd1213a6870a469b2d6b052d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79304e868267e5d64de37c5f67a91650a1c844e87176ee09a7e81174bcf3ab83(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f267a61313c0a3bb26593cfb7d61acf3b95579b14cbe8541cde2e7a7beb872(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    kubernetes_host: builtins.str,
    backend: typing.Optional[builtins.str] = None,
    disable_iss_validation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    kubernetes_ca_cert: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    pem_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_reviewer_jwt: typing.Optional[builtins.str] = None,
    use_annotations_as_alias_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
