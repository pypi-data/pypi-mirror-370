r'''
# `vault_ssh_secret_backend_ca`

Refer to the Terraform Registry for docs: [`vault_ssh_secret_backend_ca`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca).
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


class SshSecretBackendCa(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.sshSecretBackendCa.SshSecretBackendCa",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca vault_ssh_secret_backend_ca}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: typing.Optional[builtins.str] = None,
        generate_signing_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_type: typing.Optional[builtins.str] = None,
        managed_key_id: typing.Optional[builtins.str] = None,
        managed_key_name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        private_key: typing.Optional[builtins.str] = None,
        public_key: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca vault_ssh_secret_backend_ca} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The path of the SSH Secret Backend where the CA should be configured. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#backend SshSecretBackendCa#backend}
        :param generate_signing_key: Whether Vault should generate the signing key pair internally. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#generate_signing_key SshSecretBackendCa#generate_signing_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#id SshSecretBackendCa#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_bits: Specifies the desired key bits for the generated SSH CA key when ``generate_signing_key`` is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#key_bits SshSecretBackendCa#key_bits}
        :param key_type: Specifies the desired key type for the generated SSH CA key when ``generate_signing_key`` is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#key_type SshSecretBackendCa#key_type}
        :param managed_key_id: The id of the managed key to use. When using a managed key, this field or managed_key_name is required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#managed_key_id SshSecretBackendCa#managed_key_id}
        :param managed_key_name: The name of the managed key to use. When using a managed key, this field or managed_key_id is required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#managed_key_name SshSecretBackendCa#managed_key_name}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#namespace SshSecretBackendCa#namespace}
        :param private_key: Private key part the SSH CA key pair; required if generate_signing_key is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#private_key SshSecretBackendCa#private_key}
        :param public_key: Public key part the SSH CA key pair; required if generate_signing_key is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#public_key SshSecretBackendCa#public_key}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9423e71a6d20c5beeb9e45e411c63e68d3262c9b03d07dbd26c4b5466da89bf5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SshSecretBackendCaConfig(
            backend=backend,
            generate_signing_key=generate_signing_key,
            id=id,
            key_bits=key_bits,
            key_type=key_type,
            managed_key_id=managed_key_id,
            managed_key_name=managed_key_name,
            namespace=namespace,
            private_key=private_key,
            public_key=public_key,
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
        '''Generates CDKTF code for importing a SshSecretBackendCa resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SshSecretBackendCa to import.
        :param import_from_id: The id of the existing SshSecretBackendCa that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SshSecretBackendCa to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e85a4200ef55e925248c9835ec970753edffc08cd91262a2d4a7d60ad2c8fece)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackend")
    def reset_backend(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackend", []))

    @jsii.member(jsii_name="resetGenerateSigningKey")
    def reset_generate_signing_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateSigningKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyBits")
    def reset_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyBits", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetManagedKeyId")
    def reset_managed_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedKeyId", []))

    @jsii.member(jsii_name="resetManagedKeyName")
    def reset_managed_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedKeyName", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPrivateKey")
    def reset_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKey", []))

    @jsii.member(jsii_name="resetPublicKey")
    def reset_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicKey", []))

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
    @jsii.member(jsii_name="generateSigningKeyInput")
    def generate_signing_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "generateSigningKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyBitsInput")
    def key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="managedKeyIdInput")
    def managed_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="managedKeyNameInput")
    def managed_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managedKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23cdfa4c93a53ca5594819b04154e66256bffa2d10f0476165d9b486134adb0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="generateSigningKey")
    def generate_signing_key(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "generateSigningKey"))

    @generate_signing_key.setter
    def generate_signing_key(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__030e5e1d0c219cf5334b32c4e9728610917e4057c7e77e79129c2323757e8f7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateSigningKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae9c159f1d44550d698fa40b2704fba43a48cfecd8aefe1ee8feddf7ed614ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyBits")
    def key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyBits"))

    @key_bits.setter
    def key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ca555ec412fd040724822a00b4c1d6ddeadac5947ac40737f9ca79edf602bdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6e4db3a5c752820880bd56265063b10ca76bd80ff732bc5a79406df8ed07c2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedKeyId")
    def managed_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedKeyId"))

    @managed_key_id.setter
    def managed_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d46843b9c1e6545425ffaf0d34f4c821fd4b90466b8553fb54731df45740a0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedKeyName")
    def managed_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedKeyName"))

    @managed_key_name.setter
    def managed_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc7dca913c745b99f598234909231ae028f5c1e4af9374a9cd745132b2eec6d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedKeyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e6bb5666512d03211ab89d30efd84e9340e95365c87491f0cf5b9340fe43ed0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d64e3106d756ad1ab061920bfcbc40f6da08cb55774da9e5bb9afe2d50325aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11aa8b7e21490e2c6d733a40937b2ffe1fa1e5005024112132bc7596743b0274)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicKey", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.sshSecretBackendCa.SshSecretBackendCaConfig",
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
        "generate_signing_key": "generateSigningKey",
        "id": "id",
        "key_bits": "keyBits",
        "key_type": "keyType",
        "managed_key_id": "managedKeyId",
        "managed_key_name": "managedKeyName",
        "namespace": "namespace",
        "private_key": "privateKey",
        "public_key": "publicKey",
    },
)
class SshSecretBackendCaConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        generate_signing_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_type: typing.Optional[builtins.str] = None,
        managed_key_id: typing.Optional[builtins.str] = None,
        managed_key_name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        private_key: typing.Optional[builtins.str] = None,
        public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The path of the SSH Secret Backend where the CA should be configured. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#backend SshSecretBackendCa#backend}
        :param generate_signing_key: Whether Vault should generate the signing key pair internally. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#generate_signing_key SshSecretBackendCa#generate_signing_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#id SshSecretBackendCa#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_bits: Specifies the desired key bits for the generated SSH CA key when ``generate_signing_key`` is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#key_bits SshSecretBackendCa#key_bits}
        :param key_type: Specifies the desired key type for the generated SSH CA key when ``generate_signing_key`` is set to ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#key_type SshSecretBackendCa#key_type}
        :param managed_key_id: The id of the managed key to use. When using a managed key, this field or managed_key_name is required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#managed_key_id SshSecretBackendCa#managed_key_id}
        :param managed_key_name: The name of the managed key to use. When using a managed key, this field or managed_key_id is required. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#managed_key_name SshSecretBackendCa#managed_key_name}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#namespace SshSecretBackendCa#namespace}
        :param private_key: Private key part the SSH CA key pair; required if generate_signing_key is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#private_key SshSecretBackendCa#private_key}
        :param public_key: Public key part the SSH CA key pair; required if generate_signing_key is false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#public_key SshSecretBackendCa#public_key}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdeae561e7ee83a231f84520089ca61b32d7b62467b8e8db3d44b64a68b8ff24)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument generate_signing_key", value=generate_signing_key, expected_type=type_hints["generate_signing_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_bits", value=key_bits, expected_type=type_hints["key_bits"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument managed_key_id", value=managed_key_id, expected_type=type_hints["managed_key_id"])
            check_type(argname="argument managed_key_name", value=managed_key_name, expected_type=type_hints["managed_key_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument public_key", value=public_key, expected_type=type_hints["public_key"])
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
        if generate_signing_key is not None:
            self._values["generate_signing_key"] = generate_signing_key
        if id is not None:
            self._values["id"] = id
        if key_bits is not None:
            self._values["key_bits"] = key_bits
        if key_type is not None:
            self._values["key_type"] = key_type
        if managed_key_id is not None:
            self._values["managed_key_id"] = managed_key_id
        if managed_key_name is not None:
            self._values["managed_key_name"] = managed_key_name
        if namespace is not None:
            self._values["namespace"] = namespace
        if private_key is not None:
            self._values["private_key"] = private_key
        if public_key is not None:
            self._values["public_key"] = public_key

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
        '''The path of the SSH Secret Backend where the CA should be configured.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#backend SshSecretBackendCa#backend}
        '''
        result = self._values.get("backend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def generate_signing_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether Vault should generate the signing key pair internally.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#generate_signing_key SshSecretBackendCa#generate_signing_key}
        '''
        result = self._values.get("generate_signing_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#id SshSecretBackendCa#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_bits(self) -> typing.Optional[jsii.Number]:
        '''Specifies the desired key bits for the generated SSH CA key when ``generate_signing_key`` is set to ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#key_bits SshSecretBackendCa#key_bits}
        '''
        result = self._values.get("key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''Specifies the desired key type for the generated SSH CA key when ``generate_signing_key`` is set to ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#key_type SshSecretBackendCa#key_type}
        '''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_key_id(self) -> typing.Optional[builtins.str]:
        '''The id of the managed key to use. When using a managed key, this field or managed_key_name is required.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#managed_key_id SshSecretBackendCa#managed_key_id}
        '''
        result = self._values.get("managed_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_key_name(self) -> typing.Optional[builtins.str]:
        '''The name of the managed key to use. When using a managed key, this field or managed_key_id is required.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#managed_key_name SshSecretBackendCa#managed_key_name}
        '''
        result = self._values.get("managed_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#namespace SshSecretBackendCa#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key(self) -> typing.Optional[builtins.str]:
        '''Private key part the SSH CA key pair; required if generate_signing_key is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#private_key SshSecretBackendCa#private_key}
        '''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_key(self) -> typing.Optional[builtins.str]:
        '''Public key part the SSH CA key pair; required if generate_signing_key is false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ssh_secret_backend_ca#public_key SshSecretBackendCa#public_key}
        '''
        result = self._values.get("public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SshSecretBackendCaConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SshSecretBackendCa",
    "SshSecretBackendCaConfig",
]

publication.publish()

def _typecheckingstub__9423e71a6d20c5beeb9e45e411c63e68d3262c9b03d07dbd26c4b5466da89bf5(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: typing.Optional[builtins.str] = None,
    generate_signing_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_type: typing.Optional[builtins.str] = None,
    managed_key_id: typing.Optional[builtins.str] = None,
    managed_key_name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    private_key: typing.Optional[builtins.str] = None,
    public_key: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e85a4200ef55e925248c9835ec970753edffc08cd91262a2d4a7d60ad2c8fece(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23cdfa4c93a53ca5594819b04154e66256bffa2d10f0476165d9b486134adb0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__030e5e1d0c219cf5334b32c4e9728610917e4057c7e77e79129c2323757e8f7b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae9c159f1d44550d698fa40b2704fba43a48cfecd8aefe1ee8feddf7ed614ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ca555ec412fd040724822a00b4c1d6ddeadac5947ac40737f9ca79edf602bdc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6e4db3a5c752820880bd56265063b10ca76bd80ff732bc5a79406df8ed07c2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d46843b9c1e6545425ffaf0d34f4c821fd4b90466b8553fb54731df45740a0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc7dca913c745b99f598234909231ae028f5c1e4af9374a9cd745132b2eec6d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e6bb5666512d03211ab89d30efd84e9340e95365c87491f0cf5b9340fe43ed0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d64e3106d756ad1ab061920bfcbc40f6da08cb55774da9e5bb9afe2d50325aee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11aa8b7e21490e2c6d733a40937b2ffe1fa1e5005024112132bc7596743b0274(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdeae561e7ee83a231f84520089ca61b32d7b62467b8e8db3d44b64a68b8ff24(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: typing.Optional[builtins.str] = None,
    generate_signing_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_type: typing.Optional[builtins.str] = None,
    managed_key_id: typing.Optional[builtins.str] = None,
    managed_key_name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    private_key: typing.Optional[builtins.str] = None,
    public_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
