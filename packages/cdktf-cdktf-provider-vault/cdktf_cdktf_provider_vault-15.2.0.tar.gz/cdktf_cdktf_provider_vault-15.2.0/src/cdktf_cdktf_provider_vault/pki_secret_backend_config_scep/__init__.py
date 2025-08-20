r'''
# `vault_pki_secret_backend_config_scep`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_config_scep`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep).
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


class PkiSecretBackendConfigScep(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScep",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep vault_pki_secret_backend_config_scep}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        allowed_digest_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_encryption_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        authenticators: typing.Optional[typing.Union["PkiSecretBackendConfigScepAuthenticators", typing.Dict[builtins.str, typing.Any]]] = None,
        default_path_policy: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_validation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PkiSecretBackendConfigScepExternalValidation", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        restrict_ca_chain_to_issuer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep vault_pki_secret_backend_config_scep} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#backend PkiSecretBackendConfigScep#backend}
        :param allowed_digest_algorithms: List of allowed digest algorithms for SCEP requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#allowed_digest_algorithms PkiSecretBackendConfigScep#allowed_digest_algorithms}
        :param allowed_encryption_algorithms: List of allowed encryption algorithms for SCEP requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#allowed_encryption_algorithms PkiSecretBackendConfigScep#allowed_encryption_algorithms}
        :param authenticators: authenticators block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#authenticators PkiSecretBackendConfigScep#authenticators}
        :param default_path_policy: Specifies the behavior for requests using the default SCEP label. Can be sign-verbatim or a role given by role:<role_name>. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#default_path_policy PkiSecretBackendConfigScep#default_path_policy}
        :param enabled: Specifies whether SCEP is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#enabled PkiSecretBackendConfigScep#enabled}
        :param external_validation: external_validation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#external_validation PkiSecretBackendConfigScep#external_validation}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#id PkiSecretBackendConfigScep#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_level: The level of logging verbosity, affects only SCEP logs on this mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#log_level PkiSecretBackendConfigScep#log_level}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#namespace PkiSecretBackendConfigScep#namespace}
        :param restrict_ca_chain_to_issuer: If true, only return the issuer CA, otherwise the entire CA certificate chain will be returned if available from the PKI mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#restrict_ca_chain_to_issuer PkiSecretBackendConfigScep#restrict_ca_chain_to_issuer}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__549a72e5111b7a4a42de954759c6c513ce3f30e6433547e9ded323a79137b786)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendConfigScepConfig(
            backend=backend,
            allowed_digest_algorithms=allowed_digest_algorithms,
            allowed_encryption_algorithms=allowed_encryption_algorithms,
            authenticators=authenticators,
            default_path_policy=default_path_policy,
            enabled=enabled,
            external_validation=external_validation,
            id=id,
            log_level=log_level,
            namespace=namespace,
            restrict_ca_chain_to_issuer=restrict_ca_chain_to_issuer,
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
        '''Generates CDKTF code for importing a PkiSecretBackendConfigScep resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendConfigScep to import.
        :param import_from_id: The id of the existing PkiSecretBackendConfigScep that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendConfigScep to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ced91137281aaf411d31e189d0695004c4798183d8073abee1e38eb2dae48ea1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAuthenticators")
    def put_authenticators(
        self,
        *,
        cert: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        scep: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param cert: The accessor and cert_role properties for cert auth backends. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#cert PkiSecretBackendConfigScep#cert}
        :param scep: The accessor property for SCEP auth backends. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#scep PkiSecretBackendConfigScep#scep}
        '''
        value = PkiSecretBackendConfigScepAuthenticators(cert=cert, scep=scep)

        return typing.cast(None, jsii.invoke(self, "putAuthenticators", [value]))

    @jsii.member(jsii_name="putExternalValidation")
    def put_external_validation(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PkiSecretBackendConfigScepExternalValidation", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a885447ecffd7b927da99ddaeee93da6c96d603386e9b8d26e265e35b934fbd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putExternalValidation", [value]))

    @jsii.member(jsii_name="resetAllowedDigestAlgorithms")
    def reset_allowed_digest_algorithms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDigestAlgorithms", []))

    @jsii.member(jsii_name="resetAllowedEncryptionAlgorithms")
    def reset_allowed_encryption_algorithms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedEncryptionAlgorithms", []))

    @jsii.member(jsii_name="resetAuthenticators")
    def reset_authenticators(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticators", []))

    @jsii.member(jsii_name="resetDefaultPathPolicy")
    def reset_default_path_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultPathPolicy", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetExternalValidation")
    def reset_external_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalValidation", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLogLevel")
    def reset_log_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogLevel", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRestrictCaChainToIssuer")
    def reset_restrict_ca_chain_to_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestrictCaChainToIssuer", []))

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
    @jsii.member(jsii_name="authenticators")
    def authenticators(
        self,
    ) -> "PkiSecretBackendConfigScepAuthenticatorsOutputReference":
        return typing.cast("PkiSecretBackendConfigScepAuthenticatorsOutputReference", jsii.get(self, "authenticators"))

    @builtins.property
    @jsii.member(jsii_name="externalValidation")
    def external_validation(self) -> "PkiSecretBackendConfigScepExternalValidationList":
        return typing.cast("PkiSecretBackendConfigScepExternalValidationList", jsii.get(self, "externalValidation"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdated")
    def last_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastUpdated"))

    @builtins.property
    @jsii.member(jsii_name="allowedDigestAlgorithmsInput")
    def allowed_digest_algorithms_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedDigestAlgorithmsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedEncryptionAlgorithmsInput")
    def allowed_encryption_algorithms_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedEncryptionAlgorithmsInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticatorsInput")
    def authenticators_input(
        self,
    ) -> typing.Optional["PkiSecretBackendConfigScepAuthenticators"]:
        return typing.cast(typing.Optional["PkiSecretBackendConfigScepAuthenticators"], jsii.get(self, "authenticatorsInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultPathPolicyInput")
    def default_path_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultPathPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="externalValidationInput")
    def external_validation_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendConfigScepExternalValidation"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendConfigScepExternalValidation"]]], jsii.get(self, "externalValidationInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="logLevelInput")
    def log_level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="restrictCaChainToIssuerInput")
    def restrict_ca_chain_to_issuer_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "restrictCaChainToIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDigestAlgorithms")
    def allowed_digest_algorithms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedDigestAlgorithms"))

    @allowed_digest_algorithms.setter
    def allowed_digest_algorithms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff719a8514a5ce83d1045f10cca0e81bf53208950e5fe839a781b4dc33506ad6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDigestAlgorithms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedEncryptionAlgorithms")
    def allowed_encryption_algorithms(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedEncryptionAlgorithms"))

    @allowed_encryption_algorithms.setter
    def allowed_encryption_algorithms(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fa020d40a0287fbc35202f3d860e3f98b590d3e092988eb1ad080bf699fd283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedEncryptionAlgorithms", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc8ea33b3cb82e02ca2651539ea2ee66891bdd8fa4e9988e4779590127ffcef6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultPathPolicy")
    def default_path_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultPathPolicy"))

    @default_path_policy.setter
    def default_path_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e955555179d4b69b6f79b04bf507fbad1ad8ababa9d3a1c69f43872de30a1ce6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultPathPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b60e0f14822b5e3ac5e252d9c2e75ada03267169e2d06d7985563eb91faaac1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efac9920ae72fca81190a7c6f123faa409a817e981f151e71691cd4b486a5940)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logLevel")
    def log_level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLevel"))

    @log_level.setter
    def log_level(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__566bce11ceb09619117fbdd6d424a7eb53fee85fc847f3a8f9b26f5c6273fe43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logLevel", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ec92649191c6f54703003f4d90f98949927ba40ba748a2409ab6fd46494dae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restrictCaChainToIssuer")
    def restrict_ca_chain_to_issuer(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "restrictCaChainToIssuer"))

    @restrict_ca_chain_to_issuer.setter
    def restrict_ca_chain_to_issuer(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__961349db9ba1d4e9672eefa6ed97418391c5b9804a08a1d2275ad76bda67e13d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restrictCaChainToIssuer", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScepAuthenticators",
    jsii_struct_bases=[],
    name_mapping={"cert": "cert", "scep": "scep"},
)
class PkiSecretBackendConfigScepAuthenticators:
    def __init__(
        self,
        *,
        cert: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        scep: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param cert: The accessor and cert_role properties for cert auth backends. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#cert PkiSecretBackendConfigScep#cert}
        :param scep: The accessor property for SCEP auth backends. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#scep PkiSecretBackendConfigScep#scep}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23620cf266ab5ca91699e3db5a8d24e7ee6e2fb6fb2af9a67c19d78cb10d8c10)
            check_type(argname="argument cert", value=cert, expected_type=type_hints["cert"])
            check_type(argname="argument scep", value=scep, expected_type=type_hints["scep"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cert is not None:
            self._values["cert"] = cert
        if scep is not None:
            self._values["scep"] = scep

    @builtins.property
    def cert(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The accessor and cert_role properties for cert auth backends.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#cert PkiSecretBackendConfigScep#cert}
        '''
        result = self._values.get("cert")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def scep(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The accessor property for SCEP auth backends.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#scep PkiSecretBackendConfigScep#scep}
        '''
        result = self._values.get("scep")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendConfigScepAuthenticators(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PkiSecretBackendConfigScepAuthenticatorsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScepAuthenticatorsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96a6b1564ab2e20ec4f51afc0c366ad77d04c190358b7a0817780001e2c84208)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCert")
    def reset_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCert", []))

    @jsii.member(jsii_name="resetScep")
    def reset_scep(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScep", []))

    @builtins.property
    @jsii.member(jsii_name="certInput")
    def cert_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "certInput"))

    @builtins.property
    @jsii.member(jsii_name="scepInput")
    def scep_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "scepInput"))

    @builtins.property
    @jsii.member(jsii_name="cert")
    def cert(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "cert"))

    @cert.setter
    def cert(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bd136e80625b8181b7e327d1fa86c73ca503d904992b55fae7cf7aea66f8b4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scep")
    def scep(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "scep"))

    @scep.setter
    def scep(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a51d36e8c946ef6cb634248c7263188de0389d6af9176b5552d544a72cc9849)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scep", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[PkiSecretBackendConfigScepAuthenticators]:
        return typing.cast(typing.Optional[PkiSecretBackendConfigScepAuthenticators], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[PkiSecretBackendConfigScepAuthenticators],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21348ea56be2a1c820dec1d78628bb3af19e57fa4173d6af88086315d4a5de5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScepConfig",
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
        "allowed_digest_algorithms": "allowedDigestAlgorithms",
        "allowed_encryption_algorithms": "allowedEncryptionAlgorithms",
        "authenticators": "authenticators",
        "default_path_policy": "defaultPathPolicy",
        "enabled": "enabled",
        "external_validation": "externalValidation",
        "id": "id",
        "log_level": "logLevel",
        "namespace": "namespace",
        "restrict_ca_chain_to_issuer": "restrictCaChainToIssuer",
    },
)
class PkiSecretBackendConfigScepConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_digest_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_encryption_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
        authenticators: typing.Optional[typing.Union[PkiSecretBackendConfigScepAuthenticators, typing.Dict[builtins.str, typing.Any]]] = None,
        default_path_policy: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        external_validation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["PkiSecretBackendConfigScepExternalValidation", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        log_level: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        restrict_ca_chain_to_issuer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#backend PkiSecretBackendConfigScep#backend}
        :param allowed_digest_algorithms: List of allowed digest algorithms for SCEP requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#allowed_digest_algorithms PkiSecretBackendConfigScep#allowed_digest_algorithms}
        :param allowed_encryption_algorithms: List of allowed encryption algorithms for SCEP requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#allowed_encryption_algorithms PkiSecretBackendConfigScep#allowed_encryption_algorithms}
        :param authenticators: authenticators block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#authenticators PkiSecretBackendConfigScep#authenticators}
        :param default_path_policy: Specifies the behavior for requests using the default SCEP label. Can be sign-verbatim or a role given by role:<role_name>. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#default_path_policy PkiSecretBackendConfigScep#default_path_policy}
        :param enabled: Specifies whether SCEP is enabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#enabled PkiSecretBackendConfigScep#enabled}
        :param external_validation: external_validation block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#external_validation PkiSecretBackendConfigScep#external_validation}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#id PkiSecretBackendConfigScep#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_level: The level of logging verbosity, affects only SCEP logs on this mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#log_level PkiSecretBackendConfigScep#log_level}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#namespace PkiSecretBackendConfigScep#namespace}
        :param restrict_ca_chain_to_issuer: If true, only return the issuer CA, otherwise the entire CA certificate chain will be returned if available from the PKI mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#restrict_ca_chain_to_issuer PkiSecretBackendConfigScep#restrict_ca_chain_to_issuer}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(authenticators, dict):
            authenticators = PkiSecretBackendConfigScepAuthenticators(**authenticators)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4e60ef0de298db4476c18df5ab94e291a4b6b660b368cd9920ee2a5dee34756)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument allowed_digest_algorithms", value=allowed_digest_algorithms, expected_type=type_hints["allowed_digest_algorithms"])
            check_type(argname="argument allowed_encryption_algorithms", value=allowed_encryption_algorithms, expected_type=type_hints["allowed_encryption_algorithms"])
            check_type(argname="argument authenticators", value=authenticators, expected_type=type_hints["authenticators"])
            check_type(argname="argument default_path_policy", value=default_path_policy, expected_type=type_hints["default_path_policy"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument external_validation", value=external_validation, expected_type=type_hints["external_validation"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument log_level", value=log_level, expected_type=type_hints["log_level"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument restrict_ca_chain_to_issuer", value=restrict_ca_chain_to_issuer, expected_type=type_hints["restrict_ca_chain_to_issuer"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
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
        if allowed_digest_algorithms is not None:
            self._values["allowed_digest_algorithms"] = allowed_digest_algorithms
        if allowed_encryption_algorithms is not None:
            self._values["allowed_encryption_algorithms"] = allowed_encryption_algorithms
        if authenticators is not None:
            self._values["authenticators"] = authenticators
        if default_path_policy is not None:
            self._values["default_path_policy"] = default_path_policy
        if enabled is not None:
            self._values["enabled"] = enabled
        if external_validation is not None:
            self._values["external_validation"] = external_validation
        if id is not None:
            self._values["id"] = id
        if log_level is not None:
            self._values["log_level"] = log_level
        if namespace is not None:
            self._values["namespace"] = namespace
        if restrict_ca_chain_to_issuer is not None:
            self._values["restrict_ca_chain_to_issuer"] = restrict_ca_chain_to_issuer

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
        '''The PKI secret backend the resource belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#backend PkiSecretBackendConfigScep#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_digest_algorithms(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of allowed digest algorithms for SCEP requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#allowed_digest_algorithms PkiSecretBackendConfigScep#allowed_digest_algorithms}
        '''
        result = self._values.get("allowed_digest_algorithms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_encryption_algorithms(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''List of allowed encryption algorithms for SCEP requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#allowed_encryption_algorithms PkiSecretBackendConfigScep#allowed_encryption_algorithms}
        '''
        result = self._values.get("allowed_encryption_algorithms")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def authenticators(
        self,
    ) -> typing.Optional[PkiSecretBackendConfigScepAuthenticators]:
        '''authenticators block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#authenticators PkiSecretBackendConfigScep#authenticators}
        '''
        result = self._values.get("authenticators")
        return typing.cast(typing.Optional[PkiSecretBackendConfigScepAuthenticators], result)

    @builtins.property
    def default_path_policy(self) -> typing.Optional[builtins.str]:
        '''Specifies the behavior for requests using the default SCEP label. Can be sign-verbatim or a role given by role:<role_name>.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#default_path_policy PkiSecretBackendConfigScep#default_path_policy}
        '''
        result = self._values.get("default_path_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether SCEP is enabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#enabled PkiSecretBackendConfigScep#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def external_validation(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendConfigScepExternalValidation"]]]:
        '''external_validation block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#external_validation PkiSecretBackendConfigScep#external_validation}
        '''
        result = self._values.get("external_validation")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["PkiSecretBackendConfigScepExternalValidation"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#id PkiSecretBackendConfigScep#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_level(self) -> typing.Optional[builtins.str]:
        '''The level of logging verbosity, affects only SCEP logs on this mount.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#log_level PkiSecretBackendConfigScep#log_level}
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#namespace PkiSecretBackendConfigScep#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def restrict_ca_chain_to_issuer(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, only return the issuer CA, otherwise the entire CA certificate chain will be returned if available from the PKI mount.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#restrict_ca_chain_to_issuer PkiSecretBackendConfigScep#restrict_ca_chain_to_issuer}
        '''
        result = self._values.get("restrict_ca_chain_to_issuer")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendConfigScepConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScepExternalValidation",
    jsii_struct_bases=[],
    name_mapping={"intune": "intune"},
)
class PkiSecretBackendConfigScepExternalValidation:
    def __init__(
        self,
        *,
        intune: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param intune: The credentials to enable Microsoft Intune validation of SCEP requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#intune PkiSecretBackendConfigScep#intune}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bfa9b14a287a80e50e31327dfb4389a4526d987fe9017c68a70f4521d8905d2)
            check_type(argname="argument intune", value=intune, expected_type=type_hints["intune"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if intune is not None:
            self._values["intune"] = intune

    @builtins.property
    def intune(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The credentials to enable Microsoft Intune validation of SCEP requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_scep#intune PkiSecretBackendConfigScep#intune}
        '''
        result = self._values.get("intune")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendConfigScepExternalValidation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PkiSecretBackendConfigScepExternalValidationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScepExternalValidationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a3be12de0d9f5c8b5698f0514956327117c48ed6a6a61ce58a95bf8c09ad50b3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "PkiSecretBackendConfigScepExternalValidationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cff333f018d724602a1b492513d9dcc005619e4731cb2c159c1be15a5b893818)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("PkiSecretBackendConfigScepExternalValidationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0742f0d534a53b7965d4ebea1f20f48be37ee547962a7be9929bba8d4bb120e1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ff47aa4d75acece2e9297092c9c85380f2accf585add1f951975181a3211efc2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7fca6a7dd47c017dfa709f5bf552a00b65d4c77b7b6175526e0913aafa49209)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendConfigScepExternalValidation]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendConfigScepExternalValidation]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendConfigScepExternalValidation]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e24a5d8a6cac24ee3378fd3bbf149e496b7ba85f0c5ec08c6988d368059a9b7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class PkiSecretBackendConfigScepExternalValidationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigScep.PkiSecretBackendConfigScepExternalValidationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b9fc1d252571562121362f923fc6688d60f712a0349177230733d87e35b22ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIntune")
    def reset_intune(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntune", []))

    @builtins.property
    @jsii.member(jsii_name="intuneInput")
    def intune_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "intuneInput"))

    @builtins.property
    @jsii.member(jsii_name="intune")
    def intune(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "intune"))

    @intune.setter
    def intune(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d60a767af4be89604f074442ce0deb859898e4aaeece520d6130f8cef6e14876)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intune", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendConfigScepExternalValidation]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendConfigScepExternalValidation]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendConfigScepExternalValidation]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__265771c7e3d13ca2fafb75033db29794a481e24d5820c76a646a05e734f96f96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PkiSecretBackendConfigScep",
    "PkiSecretBackendConfigScepAuthenticators",
    "PkiSecretBackendConfigScepAuthenticatorsOutputReference",
    "PkiSecretBackendConfigScepConfig",
    "PkiSecretBackendConfigScepExternalValidation",
    "PkiSecretBackendConfigScepExternalValidationList",
    "PkiSecretBackendConfigScepExternalValidationOutputReference",
]

publication.publish()

def _typecheckingstub__549a72e5111b7a4a42de954759c6c513ce3f30e6433547e9ded323a79137b786(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    allowed_digest_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_encryption_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    authenticators: typing.Optional[typing.Union[PkiSecretBackendConfigScepAuthenticators, typing.Dict[builtins.str, typing.Any]]] = None,
    default_path_policy: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_validation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PkiSecretBackendConfigScepExternalValidation, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    log_level: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    restrict_ca_chain_to_issuer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__ced91137281aaf411d31e189d0695004c4798183d8073abee1e38eb2dae48ea1(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a885447ecffd7b927da99ddaeee93da6c96d603386e9b8d26e265e35b934fbd9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PkiSecretBackendConfigScepExternalValidation, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff719a8514a5ce83d1045f10cca0e81bf53208950e5fe839a781b4dc33506ad6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fa020d40a0287fbc35202f3d860e3f98b590d3e092988eb1ad080bf699fd283(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc8ea33b3cb82e02ca2651539ea2ee66891bdd8fa4e9988e4779590127ffcef6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e955555179d4b69b6f79b04bf507fbad1ad8ababa9d3a1c69f43872de30a1ce6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b60e0f14822b5e3ac5e252d9c2e75ada03267169e2d06d7985563eb91faaac1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efac9920ae72fca81190a7c6f123faa409a817e981f151e71691cd4b486a5940(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__566bce11ceb09619117fbdd6d424a7eb53fee85fc847f3a8f9b26f5c6273fe43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec92649191c6f54703003f4d90f98949927ba40ba748a2409ab6fd46494dae7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__961349db9ba1d4e9672eefa6ed97418391c5b9804a08a1d2275ad76bda67e13d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23620cf266ab5ca91699e3db5a8d24e7ee6e2fb6fb2af9a67c19d78cb10d8c10(
    *,
    cert: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    scep: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96a6b1564ab2e20ec4f51afc0c366ad77d04c190358b7a0817780001e2c84208(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bd136e80625b8181b7e327d1fa86c73ca503d904992b55fae7cf7aea66f8b4a(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a51d36e8c946ef6cb634248c7263188de0389d6af9176b5552d544a72cc9849(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21348ea56be2a1c820dec1d78628bb3af19e57fa4173d6af88086315d4a5de5f(
    value: typing.Optional[PkiSecretBackendConfigScepAuthenticators],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4e60ef0de298db4476c18df5ab94e291a4b6b660b368cd9920ee2a5dee34756(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    allowed_digest_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_encryption_algorithms: typing.Optional[typing.Sequence[builtins.str]] = None,
    authenticators: typing.Optional[typing.Union[PkiSecretBackendConfigScepAuthenticators, typing.Dict[builtins.str, typing.Any]]] = None,
    default_path_policy: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    external_validation: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[PkiSecretBackendConfigScepExternalValidation, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    log_level: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    restrict_ca_chain_to_issuer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bfa9b14a287a80e50e31327dfb4389a4526d987fe9017c68a70f4521d8905d2(
    *,
    intune: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3be12de0d9f5c8b5698f0514956327117c48ed6a6a61ce58a95bf8c09ad50b3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cff333f018d724602a1b492513d9dcc005619e4731cb2c159c1be15a5b893818(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0742f0d534a53b7965d4ebea1f20f48be37ee547962a7be9929bba8d4bb120e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff47aa4d75acece2e9297092c9c85380f2accf585add1f951975181a3211efc2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7fca6a7dd47c017dfa709f5bf552a00b65d4c77b7b6175526e0913aafa49209(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e24a5d8a6cac24ee3378fd3bbf149e496b7ba85f0c5ec08c6988d368059a9b7e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[PkiSecretBackendConfigScepExternalValidation]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b9fc1d252571562121362f923fc6688d60f712a0349177230733d87e35b22ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d60a767af4be89604f074442ce0deb859898e4aaeece520d6130f8cef6e14876(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265771c7e3d13ca2fafb75033db29794a481e24d5820c76a646a05e734f96f96(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PkiSecretBackendConfigScepExternalValidation]],
) -> None:
    """Type checking stubs"""
    pass
