r'''
# `vault_transit_secret_backend_key`

Refer to the Terraform Registry for docs: [`vault_transit_secret_backend_key`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key).
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


class TransitSecretBackendKey(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.transitSecretBackendKey.TransitSecretBackendKey",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key vault_transit_secret_backend_key}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        name: builtins.str,
        allow_plaintext_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_rotate_period: typing.Optional[jsii.Number] = None,
        convergent_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deletion_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        derived: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exportable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hybrid_key_type_ec: typing.Optional[builtins.str] = None,
        hybrid_key_type_pqc: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_size: typing.Optional[jsii.Number] = None,
        min_decryption_version: typing.Optional[jsii.Number] = None,
        min_encryption_version: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameter_set: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key vault_transit_secret_backend_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The Transit secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#backend TransitSecretBackendKey#backend}
        :param name: Name of the encryption key to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#name TransitSecretBackendKey#name}
        :param allow_plaintext_backup: If set, enables taking backup of named key in the plaintext format. Once set, this cannot be disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#allow_plaintext_backup TransitSecretBackendKey#allow_plaintext_backup}
        :param auto_rotate_period: Amount of seconds the key should live before being automatically rotated. A value of 0 disables automatic rotation for the key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#auto_rotate_period TransitSecretBackendKey#auto_rotate_period}
        :param convergent_encryption: Whether or not to support convergent encryption, where the same plaintext creates the same ciphertext. This requires derived to be set to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#convergent_encryption TransitSecretBackendKey#convergent_encryption}
        :param deletion_allowed: Specifies if the key is allowed to be deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#deletion_allowed TransitSecretBackendKey#deletion_allowed}
        :param derived: Specifies if key derivation is to be used. If enabled, all encrypt/decrypt requests to this key must provide a context which is used for key derivation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#derived TransitSecretBackendKey#derived}
        :param exportable: Enables keys to be exportable. This allows for all the valid keys in the key ring to be exported. Once set, this cannot be disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#exportable TransitSecretBackendKey#exportable}
        :param hybrid_key_type_ec: The elliptic curve algorithm to use for hybrid signatures. Supported key types are ``ecdsa-p256``, ``ecdsa-p384``, ``ecdsa-p521``, and ``ed25519``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#hybrid_key_type_ec TransitSecretBackendKey#hybrid_key_type_ec}
        :param hybrid_key_type_pqc: The post-quantum algorithm to use for hybrid signatures. Currently, ML-DSA is the only supported key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#hybrid_key_type_pqc TransitSecretBackendKey#hybrid_key_type_pqc}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#id TransitSecretBackendKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_size: The key size in bytes for algorithms that allow variable key sizes. Currently only applicable to HMAC; this value must be between 32 and 512. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#key_size TransitSecretBackendKey#key_size}
        :param min_decryption_version: Minimum key version to use for decryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#min_decryption_version TransitSecretBackendKey#min_decryption_version}
        :param min_encryption_version: Minimum key version to use for encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#min_encryption_version TransitSecretBackendKey#min_encryption_version}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#namespace TransitSecretBackendKey#namespace}
        :param parameter_set: The parameter set to use for ML-DSA. Required for ML-DSA and hybrid keys. Valid values for ML-DSA are ``44``, ``65``, and ``87``. Valid values for SLH-DSA are ``slh-dsa-sha2-128s``, ``slh-dsa-shake-128s``, ``slh-dsa-sha2-128f``, ``slh-dsa-shake-128``, ``slh-dsa-sha2-192s``, ``slh-dsa-shake-192s``, ``slh-dsa-sha2-192f``, ``slh-dsa-shake-192f``, ``slh-dsa-sha2-256s``, ``slh-dsa-shake-256s``, ``slh-dsa-sha2-256f``, and ``slh-dsa-shake-256f``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#parameter_set TransitSecretBackendKey#parameter_set}
        :param type: Specifies the type of key to create. The currently-supported types are: ``aes128-gcm96``, ``aes256-gcm96`` (default), ``chacha20-poly1305``, ``ed25519``, ``ecdsa-p256``, ``ecdsa-p384``, ``ecdsa-p521``, ``hmac``, ``rsa-2048``, ``rsa-3072``, ``rsa-4096``, ``managed_key``, ``aes128-cmac``, ``aes192-cmac``, ``aes256-cmac``, ``ml-dsa``, ``hybrid``, and ``slh-dsa``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#type TransitSecretBackendKey#type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dbdf2bc50a24caad4ed943995eaf4cd642c0393c4045c91d66171ebb9c26fd8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TransitSecretBackendKeyConfig(
            backend=backend,
            name=name,
            allow_plaintext_backup=allow_plaintext_backup,
            auto_rotate_period=auto_rotate_period,
            convergent_encryption=convergent_encryption,
            deletion_allowed=deletion_allowed,
            derived=derived,
            exportable=exportable,
            hybrid_key_type_ec=hybrid_key_type_ec,
            hybrid_key_type_pqc=hybrid_key_type_pqc,
            id=id,
            key_size=key_size,
            min_decryption_version=min_decryption_version,
            min_encryption_version=min_encryption_version,
            namespace=namespace,
            parameter_set=parameter_set,
            type=type,
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
        '''Generates CDKTF code for importing a TransitSecretBackendKey resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TransitSecretBackendKey to import.
        :param import_from_id: The id of the existing TransitSecretBackendKey that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TransitSecretBackendKey to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75ca41a347826b951d90fc347590a76a6fbcc7382027b078d82206dd4ea8a7c0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowPlaintextBackup")
    def reset_allow_plaintext_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowPlaintextBackup", []))

    @jsii.member(jsii_name="resetAutoRotatePeriod")
    def reset_auto_rotate_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRotatePeriod", []))

    @jsii.member(jsii_name="resetConvergentEncryption")
    def reset_convergent_encryption(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConvergentEncryption", []))

    @jsii.member(jsii_name="resetDeletionAllowed")
    def reset_deletion_allowed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeletionAllowed", []))

    @jsii.member(jsii_name="resetDerived")
    def reset_derived(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDerived", []))

    @jsii.member(jsii_name="resetExportable")
    def reset_exportable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExportable", []))

    @jsii.member(jsii_name="resetHybridKeyTypeEc")
    def reset_hybrid_key_type_ec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHybridKeyTypeEc", []))

    @jsii.member(jsii_name="resetHybridKeyTypePqc")
    def reset_hybrid_key_type_pqc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHybridKeyTypePqc", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeySize")
    def reset_key_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeySize", []))

    @jsii.member(jsii_name="resetMinDecryptionVersion")
    def reset_min_decryption_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinDecryptionVersion", []))

    @jsii.member(jsii_name="resetMinEncryptionVersion")
    def reset_min_encryption_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinEncryptionVersion", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetParameterSet")
    def reset_parameter_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterSet", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="keys")
    def keys(self) -> _cdktf_9a9027ec.StringMapList:
        return typing.cast(_cdktf_9a9027ec.StringMapList, jsii.get(self, "keys"))

    @builtins.property
    @jsii.member(jsii_name="latestVersion")
    def latest_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "latestVersion"))

    @builtins.property
    @jsii.member(jsii_name="minAvailableVersion")
    def min_available_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minAvailableVersion"))

    @builtins.property
    @jsii.member(jsii_name="supportsDecryption")
    def supports_decryption(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "supportsDecryption"))

    @builtins.property
    @jsii.member(jsii_name="supportsDerivation")
    def supports_derivation(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "supportsDerivation"))

    @builtins.property
    @jsii.member(jsii_name="supportsEncryption")
    def supports_encryption(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "supportsEncryption"))

    @builtins.property
    @jsii.member(jsii_name="supportsSigning")
    def supports_signing(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "supportsSigning"))

    @builtins.property
    @jsii.member(jsii_name="allowPlaintextBackupInput")
    def allow_plaintext_backup_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowPlaintextBackupInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRotatePeriodInput")
    def auto_rotate_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autoRotatePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="convergentEncryptionInput")
    def convergent_encryption_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "convergentEncryptionInput"))

    @builtins.property
    @jsii.member(jsii_name="deletionAllowedInput")
    def deletion_allowed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deletionAllowedInput"))

    @builtins.property
    @jsii.member(jsii_name="derivedInput")
    def derived_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "derivedInput"))

    @builtins.property
    @jsii.member(jsii_name="exportableInput")
    def exportable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "exportableInput"))

    @builtins.property
    @jsii.member(jsii_name="hybridKeyTypeEcInput")
    def hybrid_key_type_ec_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hybridKeyTypeEcInput"))

    @builtins.property
    @jsii.member(jsii_name="hybridKeyTypePqcInput")
    def hybrid_key_type_pqc_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hybridKeyTypePqcInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keySizeInput")
    def key_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keySizeInput"))

    @builtins.property
    @jsii.member(jsii_name="minDecryptionVersionInput")
    def min_decryption_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minDecryptionVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="minEncryptionVersionInput")
    def min_encryption_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minEncryptionVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="parameterSetInput")
    def parameter_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterSetInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="allowPlaintextBackup")
    def allow_plaintext_backup(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowPlaintextBackup"))

    @allow_plaintext_backup.setter
    def allow_plaintext_backup(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__225450d04eb44c76328f00ced3379f0aedd53c378ac58862d567c75c31b1dfee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowPlaintextBackup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoRotatePeriod")
    def auto_rotate_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autoRotatePeriod"))

    @auto_rotate_period.setter
    def auto_rotate_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7746584b586214651ec8a9a20a9a010d02bad51ef55b88aff326772b0e9f5c17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotatePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21ee870bb73952dd172f3129046cc1170d75a26cd9c53cfb89eb567689159235)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="convergentEncryption")
    def convergent_encryption(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "convergentEncryption"))

    @convergent_encryption.setter
    def convergent_encryption(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29078f5f0dba5b3c888d5bc4ba1629e1341f421a723a5d2b6a296c40f1f169d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "convergentEncryption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletionAllowed")
    def deletion_allowed(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deletionAllowed"))

    @deletion_allowed.setter
    def deletion_allowed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02c511da5bea79691452251cc5d871887641fc531ccf9d61d25c3a35fb249c60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletionAllowed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="derived")
    def derived(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "derived"))

    @derived.setter
    def derived(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5834a31d32ace9c8fdc0e58065e364820f2ae6c071f50f23dc9c801a427fafad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "derived", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exportable")
    def exportable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "exportable"))

    @exportable.setter
    def exportable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce7b8c6987f10c4fcf74a4a630d628e03e7a0d21e6a83d74004060c260414cdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exportable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hybridKeyTypeEc")
    def hybrid_key_type_ec(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hybridKeyTypeEc"))

    @hybrid_key_type_ec.setter
    def hybrid_key_type_ec(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3884c0cdb2e9e924031cefc07116aa2f1abe71ea0531e1aec6f4afed00cfaac5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hybridKeyTypeEc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hybridKeyTypePqc")
    def hybrid_key_type_pqc(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hybridKeyTypePqc"))

    @hybrid_key_type_pqc.setter
    def hybrid_key_type_pqc(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0307b7850796c136183146de05fc1dcb0ef1f2995bd7481b351e31a0d8f9e357)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hybridKeyTypePqc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8adbd7daacb17e2951a2b2613d0f771f7db2425ab202f6ca547cb80a326fe944)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keySize")
    def key_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keySize"))

    @key_size.setter
    def key_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12101650479c914cdf917b33cc501663e38899d0c945396cb875ca137e1fde58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keySize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minDecryptionVersion")
    def min_decryption_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minDecryptionVersion"))

    @min_decryption_version.setter
    def min_decryption_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a502b7bdcb542e92f74c403554ee9e714971f80ab5fbe4db754c1c41066856c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minDecryptionVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minEncryptionVersion")
    def min_encryption_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minEncryptionVersion"))

    @min_encryption_version.setter
    def min_encryption_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d0d2c1da652c43fb6901a5149c09e69ecc75d62d4cd0c3f33f8b0aafbc9f9bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minEncryptionVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e8f944a95eeec87ccd861e417d467d227dba99ccd8c8ece236333c8b51d550c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da252cb812a8934833b247b7048cc150897d16fed851bda8f0a0f4afba03ff46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameterSet")
    def parameter_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterSet"))

    @parameter_set.setter
    def parameter_set(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d46ae539d221ed0a23f1de7e4fcbe685f2624406c50544b76b4c2a5962bb12c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameterSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89745c2d46264327145b74c874f2d1be67e440b927fc5657b76fcb01157911c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.transitSecretBackendKey.TransitSecretBackendKeyConfig",
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
        "name": "name",
        "allow_plaintext_backup": "allowPlaintextBackup",
        "auto_rotate_period": "autoRotatePeriod",
        "convergent_encryption": "convergentEncryption",
        "deletion_allowed": "deletionAllowed",
        "derived": "derived",
        "exportable": "exportable",
        "hybrid_key_type_ec": "hybridKeyTypeEc",
        "hybrid_key_type_pqc": "hybridKeyTypePqc",
        "id": "id",
        "key_size": "keySize",
        "min_decryption_version": "minDecryptionVersion",
        "min_encryption_version": "minEncryptionVersion",
        "namespace": "namespace",
        "parameter_set": "parameterSet",
        "type": "type",
    },
)
class TransitSecretBackendKeyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        allow_plaintext_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_rotate_period: typing.Optional[jsii.Number] = None,
        convergent_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deletion_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        derived: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        exportable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hybrid_key_type_ec: typing.Optional[builtins.str] = None,
        hybrid_key_type_pqc: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_size: typing.Optional[jsii.Number] = None,
        min_decryption_version: typing.Optional[jsii.Number] = None,
        min_encryption_version: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameter_set: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The Transit secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#backend TransitSecretBackendKey#backend}
        :param name: Name of the encryption key to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#name TransitSecretBackendKey#name}
        :param allow_plaintext_backup: If set, enables taking backup of named key in the plaintext format. Once set, this cannot be disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#allow_plaintext_backup TransitSecretBackendKey#allow_plaintext_backup}
        :param auto_rotate_period: Amount of seconds the key should live before being automatically rotated. A value of 0 disables automatic rotation for the key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#auto_rotate_period TransitSecretBackendKey#auto_rotate_period}
        :param convergent_encryption: Whether or not to support convergent encryption, where the same plaintext creates the same ciphertext. This requires derived to be set to true. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#convergent_encryption TransitSecretBackendKey#convergent_encryption}
        :param deletion_allowed: Specifies if the key is allowed to be deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#deletion_allowed TransitSecretBackendKey#deletion_allowed}
        :param derived: Specifies if key derivation is to be used. If enabled, all encrypt/decrypt requests to this key must provide a context which is used for key derivation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#derived TransitSecretBackendKey#derived}
        :param exportable: Enables keys to be exportable. This allows for all the valid keys in the key ring to be exported. Once set, this cannot be disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#exportable TransitSecretBackendKey#exportable}
        :param hybrid_key_type_ec: The elliptic curve algorithm to use for hybrid signatures. Supported key types are ``ecdsa-p256``, ``ecdsa-p384``, ``ecdsa-p521``, and ``ed25519``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#hybrid_key_type_ec TransitSecretBackendKey#hybrid_key_type_ec}
        :param hybrid_key_type_pqc: The post-quantum algorithm to use for hybrid signatures. Currently, ML-DSA is the only supported key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#hybrid_key_type_pqc TransitSecretBackendKey#hybrid_key_type_pqc}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#id TransitSecretBackendKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_size: The key size in bytes for algorithms that allow variable key sizes. Currently only applicable to HMAC; this value must be between 32 and 512. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#key_size TransitSecretBackendKey#key_size}
        :param min_decryption_version: Minimum key version to use for decryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#min_decryption_version TransitSecretBackendKey#min_decryption_version}
        :param min_encryption_version: Minimum key version to use for encryption. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#min_encryption_version TransitSecretBackendKey#min_encryption_version}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#namespace TransitSecretBackendKey#namespace}
        :param parameter_set: The parameter set to use for ML-DSA. Required for ML-DSA and hybrid keys. Valid values for ML-DSA are ``44``, ``65``, and ``87``. Valid values for SLH-DSA are ``slh-dsa-sha2-128s``, ``slh-dsa-shake-128s``, ``slh-dsa-sha2-128f``, ``slh-dsa-shake-128``, ``slh-dsa-sha2-192s``, ``slh-dsa-shake-192s``, ``slh-dsa-sha2-192f``, ``slh-dsa-shake-192f``, ``slh-dsa-sha2-256s``, ``slh-dsa-shake-256s``, ``slh-dsa-sha2-256f``, and ``slh-dsa-shake-256f``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#parameter_set TransitSecretBackendKey#parameter_set}
        :param type: Specifies the type of key to create. The currently-supported types are: ``aes128-gcm96``, ``aes256-gcm96`` (default), ``chacha20-poly1305``, ``ed25519``, ``ecdsa-p256``, ``ecdsa-p384``, ``ecdsa-p521``, ``hmac``, ``rsa-2048``, ``rsa-3072``, ``rsa-4096``, ``managed_key``, ``aes128-cmac``, ``aes192-cmac``, ``aes256-cmac``, ``ml-dsa``, ``hybrid``, and ``slh-dsa``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#type TransitSecretBackendKey#type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__452c790eefb5720de4ff8c8c54d5c122ae5da2c91656945ce52833428f568ee2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allow_plaintext_backup", value=allow_plaintext_backup, expected_type=type_hints["allow_plaintext_backup"])
            check_type(argname="argument auto_rotate_period", value=auto_rotate_period, expected_type=type_hints["auto_rotate_period"])
            check_type(argname="argument convergent_encryption", value=convergent_encryption, expected_type=type_hints["convergent_encryption"])
            check_type(argname="argument deletion_allowed", value=deletion_allowed, expected_type=type_hints["deletion_allowed"])
            check_type(argname="argument derived", value=derived, expected_type=type_hints["derived"])
            check_type(argname="argument exportable", value=exportable, expected_type=type_hints["exportable"])
            check_type(argname="argument hybrid_key_type_ec", value=hybrid_key_type_ec, expected_type=type_hints["hybrid_key_type_ec"])
            check_type(argname="argument hybrid_key_type_pqc", value=hybrid_key_type_pqc, expected_type=type_hints["hybrid_key_type_pqc"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_size", value=key_size, expected_type=type_hints["key_size"])
            check_type(argname="argument min_decryption_version", value=min_decryption_version, expected_type=type_hints["min_decryption_version"])
            check_type(argname="argument min_encryption_version", value=min_encryption_version, expected_type=type_hints["min_encryption_version"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument parameter_set", value=parameter_set, expected_type=type_hints["parameter_set"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
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
        if allow_plaintext_backup is not None:
            self._values["allow_plaintext_backup"] = allow_plaintext_backup
        if auto_rotate_period is not None:
            self._values["auto_rotate_period"] = auto_rotate_period
        if convergent_encryption is not None:
            self._values["convergent_encryption"] = convergent_encryption
        if deletion_allowed is not None:
            self._values["deletion_allowed"] = deletion_allowed
        if derived is not None:
            self._values["derived"] = derived
        if exportable is not None:
            self._values["exportable"] = exportable
        if hybrid_key_type_ec is not None:
            self._values["hybrid_key_type_ec"] = hybrid_key_type_ec
        if hybrid_key_type_pqc is not None:
            self._values["hybrid_key_type_pqc"] = hybrid_key_type_pqc
        if id is not None:
            self._values["id"] = id
        if key_size is not None:
            self._values["key_size"] = key_size
        if min_decryption_version is not None:
            self._values["min_decryption_version"] = min_decryption_version
        if min_encryption_version is not None:
            self._values["min_encryption_version"] = min_encryption_version
        if namespace is not None:
            self._values["namespace"] = namespace
        if parameter_set is not None:
            self._values["parameter_set"] = parameter_set
        if type is not None:
            self._values["type"] = type

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
        '''The Transit secret backend the resource belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#backend TransitSecretBackendKey#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the encryption key to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#name TransitSecretBackendKey#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_plaintext_backup(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, enables taking backup of named key in the plaintext format. Once set, this cannot be disabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#allow_plaintext_backup TransitSecretBackendKey#allow_plaintext_backup}
        '''
        result = self._values.get("allow_plaintext_backup")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_rotate_period(self) -> typing.Optional[jsii.Number]:
        '''Amount of seconds the key should live before being automatically rotated.

        A value of 0 disables automatic rotation for the key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#auto_rotate_period TransitSecretBackendKey#auto_rotate_period}
        '''
        result = self._values.get("auto_rotate_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def convergent_encryption(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether or not to support convergent encryption, where the same plaintext creates the same ciphertext.

        This requires derived to be set to true.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#convergent_encryption TransitSecretBackendKey#convergent_encryption}
        '''
        result = self._values.get("convergent_encryption")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deletion_allowed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if the key is allowed to be deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#deletion_allowed TransitSecretBackendKey#deletion_allowed}
        '''
        result = self._values.get("deletion_allowed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def derived(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if key derivation is to be used.

        If enabled, all encrypt/decrypt requests to this key must provide a context which is used for key derivation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#derived TransitSecretBackendKey#derived}
        '''
        result = self._values.get("derived")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def exportable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables keys to be exportable.

        This allows for all the valid keys in the key ring to be exported. Once set, this cannot be disabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#exportable TransitSecretBackendKey#exportable}
        '''
        result = self._values.get("exportable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hybrid_key_type_ec(self) -> typing.Optional[builtins.str]:
        '''The elliptic curve algorithm to use for hybrid signatures. Supported key types are ``ecdsa-p256``, ``ecdsa-p384``, ``ecdsa-p521``, and ``ed25519``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#hybrid_key_type_ec TransitSecretBackendKey#hybrid_key_type_ec}
        '''
        result = self._values.get("hybrid_key_type_ec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hybrid_key_type_pqc(self) -> typing.Optional[builtins.str]:
        '''The post-quantum algorithm to use for hybrid signatures. Currently, ML-DSA is the only supported key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#hybrid_key_type_pqc TransitSecretBackendKey#hybrid_key_type_pqc}
        '''
        result = self._values.get("hybrid_key_type_pqc")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#id TransitSecretBackendKey#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_size(self) -> typing.Optional[jsii.Number]:
        '''The key size in bytes for algorithms that allow variable key sizes.

        Currently only applicable to HMAC; this value must be between 32 and 512.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#key_size TransitSecretBackendKey#key_size}
        '''
        result = self._values.get("key_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_decryption_version(self) -> typing.Optional[jsii.Number]:
        '''Minimum key version to use for decryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#min_decryption_version TransitSecretBackendKey#min_decryption_version}
        '''
        result = self._values.get("min_decryption_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_encryption_version(self) -> typing.Optional[jsii.Number]:
        '''Minimum key version to use for encryption.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#min_encryption_version TransitSecretBackendKey#min_encryption_version}
        '''
        result = self._values.get("min_encryption_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#namespace TransitSecretBackendKey#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_set(self) -> typing.Optional[builtins.str]:
        '''The parameter set to use for ML-DSA.

        Required for ML-DSA and hybrid keys.  Valid values for ML-DSA are ``44``, ``65``, and ``87``. Valid values for SLH-DSA are ``slh-dsa-sha2-128s``, ``slh-dsa-shake-128s``, ``slh-dsa-sha2-128f``, ``slh-dsa-shake-128``, ``slh-dsa-sha2-192s``, ``slh-dsa-shake-192s``, ``slh-dsa-sha2-192f``, ``slh-dsa-shake-192f``, ``slh-dsa-sha2-256s``, ``slh-dsa-shake-256s``, ``slh-dsa-sha2-256f``, and ``slh-dsa-shake-256f``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#parameter_set TransitSecretBackendKey#parameter_set}
        '''
        result = self._values.get("parameter_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of key to create.

        The currently-supported types are: ``aes128-gcm96``, ``aes256-gcm96`` (default), ``chacha20-poly1305``, ``ed25519``, ``ecdsa-p256``, ``ecdsa-p384``, ``ecdsa-p521``, ``hmac``, ``rsa-2048``, ``rsa-3072``, ``rsa-4096``, ``managed_key``, ``aes128-cmac``, ``aes192-cmac``, ``aes256-cmac``, ``ml-dsa``, ``hybrid``, and ``slh-dsa``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/transit_secret_backend_key#type TransitSecretBackendKey#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TransitSecretBackendKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TransitSecretBackendKey",
    "TransitSecretBackendKeyConfig",
]

publication.publish()

def _typecheckingstub__1dbdf2bc50a24caad4ed943995eaf4cd642c0393c4045c91d66171ebb9c26fd8(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    name: builtins.str,
    allow_plaintext_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_rotate_period: typing.Optional[jsii.Number] = None,
    convergent_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deletion_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    derived: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exportable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hybrid_key_type_ec: typing.Optional[builtins.str] = None,
    hybrid_key_type_pqc: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_size: typing.Optional[jsii.Number] = None,
    min_decryption_version: typing.Optional[jsii.Number] = None,
    min_encryption_version: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameter_set: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__75ca41a347826b951d90fc347590a76a6fbcc7382027b078d82206dd4ea8a7c0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__225450d04eb44c76328f00ced3379f0aedd53c378ac58862d567c75c31b1dfee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7746584b586214651ec8a9a20a9a010d02bad51ef55b88aff326772b0e9f5c17(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21ee870bb73952dd172f3129046cc1170d75a26cd9c53cfb89eb567689159235(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29078f5f0dba5b3c888d5bc4ba1629e1341f421a723a5d2b6a296c40f1f169d2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02c511da5bea79691452251cc5d871887641fc531ccf9d61d25c3a35fb249c60(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5834a31d32ace9c8fdc0e58065e364820f2ae6c071f50f23dc9c801a427fafad(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce7b8c6987f10c4fcf74a4a630d628e03e7a0d21e6a83d74004060c260414cdf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3884c0cdb2e9e924031cefc07116aa2f1abe71ea0531e1aec6f4afed00cfaac5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0307b7850796c136183146de05fc1dcb0ef1f2995bd7481b351e31a0d8f9e357(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8adbd7daacb17e2951a2b2613d0f771f7db2425ab202f6ca547cb80a326fe944(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12101650479c914cdf917b33cc501663e38899d0c945396cb875ca137e1fde58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a502b7bdcb542e92f74c403554ee9e714971f80ab5fbe4db754c1c41066856c6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d0d2c1da652c43fb6901a5149c09e69ecc75d62d4cd0c3f33f8b0aafbc9f9bd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e8f944a95eeec87ccd861e417d467d227dba99ccd8c8ece236333c8b51d550c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da252cb812a8934833b247b7048cc150897d16fed851bda8f0a0f4afba03ff46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46ae539d221ed0a23f1de7e4fcbe685f2624406c50544b76b4c2a5962bb12c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89745c2d46264327145b74c874f2d1be67e440b927fc5657b76fcb01157911c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__452c790eefb5720de4ff8c8c54d5c122ae5da2c91656945ce52833428f568ee2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    name: builtins.str,
    allow_plaintext_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_rotate_period: typing.Optional[jsii.Number] = None,
    convergent_encryption: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deletion_allowed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    derived: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    exportable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hybrid_key_type_ec: typing.Optional[builtins.str] = None,
    hybrid_key_type_pqc: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_size: typing.Optional[jsii.Number] = None,
    min_decryption_version: typing.Optional[jsii.Number] = None,
    min_encryption_version: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameter_set: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
