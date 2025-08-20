r'''
# `data_vault_transit_sign`

Refer to the Terraform Registry for docs: [`data_vault_transit_sign`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign).
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


class DataVaultTransitSign(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultTransitSign.DataVaultTransitSign",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign vault_transit_sign}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        path: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        context: typing.Optional[builtins.str] = None,
        hash_algorithm: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input: typing.Optional[builtins.str] = None,
        key_version: typing.Optional[jsii.Number] = None,
        marshaling_algorithm: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reference: typing.Optional[builtins.str] = None,
        salt_length: typing.Optional[builtins.str] = None,
        signature: typing.Optional[builtins.str] = None,
        signature_algorithm: typing.Optional[builtins.str] = None,
        signature_context: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign vault_transit_sign} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the signing key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#name DataVaultTransitSign#name}
        :param path: The Transit secret backend the key belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#path DataVaultTransitSign#path}
        :param batch_input: Specifies a list of items for processing. When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#batch_input DataVaultTransitSign#batch_input}
        :param batch_results: The results returned from Vault if using batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#batch_results DataVaultTransitSign#batch_results}
        :param context: Base64 encoded context for key derivation. Required if key derivation is enabled; currently only available with ed25519 keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#context DataVaultTransitSign#context}
        :param hash_algorithm: Specifies the hash algorithm to use for supporting key types (notably, not including ed25519 which specifies its own hash algorithm). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#hash_algorithm DataVaultTransitSign#hash_algorithm}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#id DataVaultTransitSign#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input: Specifies the base64 encoded input data. One of input or batch_input must be supplied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#input DataVaultTransitSign#input}
        :param key_version: The version of the key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#key_version DataVaultTransitSign#key_version}
        :param marshaling_algorithm: Specifies the way in which the signature should be marshaled. This currently only applies to ECDSA keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#marshaling_algorithm DataVaultTransitSign#marshaling_algorithm}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#namespace DataVaultTransitSign#namespace}
        :param prehashed: Set to true when the input is already hashed. If the key type is rsa-2048, rsa-3072 or rsa-4096, then the algorithm used to hash the input should be indicated by the hash_algorithm parameter. Just as the value to sign should be the base64-encoded representation of the exact binary data you want signed, when set, input is expected to be base64-encoded binary hashed data, not hex-formatted. (As an example, on the command line, you could generate a suitable input via openssl dgst -sha256 -binary | base64.) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#prehashed DataVaultTransitSign#prehashed}
        :param reference: A user-supplied string that will be present in the reference field on the corresponding batch_results item in the response, to assist in understanding which result corresponds to a particular input. Only valid on batch requests when using ‘batch_input’ below. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#reference DataVaultTransitSign#reference}
        :param salt_length: The salt length used to sign. This currently only applies to the RSA PSS signature scheme. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#salt_length DataVaultTransitSign#salt_length}
        :param signature: The signature returned from Vault if using input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature DataVaultTransitSign#signature}
        :param signature_algorithm: When using a RSA key, specifies the RSA signature algorithm to use for signing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature_algorithm DataVaultTransitSign#signature_algorithm}
        :param signature_context: Base64 encoded context for Ed25519ctx and Ed25519ph signatures. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature_context DataVaultTransitSign#signature_context}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec2e9e123b20fc1e92b8e66415e7bf6ad9a57913c33df6919da0258f7bde8954)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultTransitSignConfig(
            name=name,
            path=path,
            batch_input=batch_input,
            batch_results=batch_results,
            context=context,
            hash_algorithm=hash_algorithm,
            id=id,
            input=input,
            key_version=key_version,
            marshaling_algorithm=marshaling_algorithm,
            namespace=namespace,
            prehashed=prehashed,
            reference=reference,
            salt_length=salt_length,
            signature=signature,
            signature_algorithm=signature_algorithm,
            signature_context=signature_context,
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
        '''Generates CDKTF code for importing a DataVaultTransitSign resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultTransitSign to import.
        :param import_from_id: The id of the existing DataVaultTransitSign that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultTransitSign to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97a9d5d62c8f09d39ee787a1b3460df0bf578b3514b26a81dff1248f47084d51)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBatchInput")
    def reset_batch_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchInput", []))

    @jsii.member(jsii_name="resetBatchResults")
    def reset_batch_results(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBatchResults", []))

    @jsii.member(jsii_name="resetContext")
    def reset_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContext", []))

    @jsii.member(jsii_name="resetHashAlgorithm")
    def reset_hash_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashAlgorithm", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInput")
    def reset_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInput", []))

    @jsii.member(jsii_name="resetKeyVersion")
    def reset_key_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyVersion", []))

    @jsii.member(jsii_name="resetMarshalingAlgorithm")
    def reset_marshaling_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMarshalingAlgorithm", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPrehashed")
    def reset_prehashed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrehashed", []))

    @jsii.member(jsii_name="resetReference")
    def reset_reference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReference", []))

    @jsii.member(jsii_name="resetSaltLength")
    def reset_salt_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaltLength", []))

    @jsii.member(jsii_name="resetSignature")
    def reset_signature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignature", []))

    @jsii.member(jsii_name="resetSignatureAlgorithm")
    def reset_signature_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureAlgorithm", []))

    @jsii.member(jsii_name="resetSignatureContext")
    def reset_signature_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureContext", []))

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
    @jsii.member(jsii_name="batchInputInput")
    def batch_input_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], jsii.get(self, "batchInputInput"))

    @builtins.property
    @jsii.member(jsii_name="batchResultsInput")
    def batch_results_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], jsii.get(self, "batchResultsInput"))

    @builtins.property
    @jsii.member(jsii_name="contextInput")
    def context_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contextInput"))

    @builtins.property
    @jsii.member(jsii_name="hashAlgorithmInput")
    def hash_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="keyVersionInput")
    def key_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="marshalingAlgorithmInput")
    def marshaling_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "marshalingAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="prehashedInput")
    def prehashed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "prehashedInput"))

    @builtins.property
    @jsii.member(jsii_name="referenceInput")
    def reference_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "referenceInput"))

    @builtins.property
    @jsii.member(jsii_name="saltLengthInput")
    def salt_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "saltLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureAlgorithmInput")
    def signature_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signatureAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureContextInput")
    def signature_context_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signatureContextInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureInput")
    def signature_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signatureInput"))

    @builtins.property
    @jsii.member(jsii_name="batchInput")
    def batch_input(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "batchInput"))

    @batch_input.setter
    def batch_input(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cdfb2ab17708dae0003cacdca301f7d2e34b340e69bb6ea71dfefe5d572900b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchInput", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="batchResults")
    def batch_results(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "batchResults"))

    @batch_results.setter
    def batch_results(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f09f99c67a810aecc937fdf20a9b2de5747c527cf4a10c6a2993aa9cfbc2f341)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchResults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "context"))

    @context.setter
    def context(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e349ef885a7c306fc4eaa93613024d11454e08e93e8634f232999515dfeeea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hashAlgorithm")
    def hash_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashAlgorithm"))

    @hash_algorithm.setter
    def hash_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f8a9305e43324013bf0dfb1ae535571220e52a4ea727ade4e03aacf2ffa96f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hashAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9ee65f455444aff12e462279d6ff9759e98f56243b7b1c7e5449d5369f29081)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "input"))

    @input.setter
    def input(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c27860a29ebe0766d0f557b4996397cb316159885496a2b735babb7802c9f1e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "input", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyVersion")
    def key_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyVersion"))

    @key_version.setter
    def key_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af1644fe2a6f4be2a53bc73ed40843316152d9408ef98f42f88ba08eee3f2b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="marshalingAlgorithm")
    def marshaling_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "marshalingAlgorithm"))

    @marshaling_algorithm.setter
    def marshaling_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6165d9b22f51a558ce70707804c678192d6fd0ac21556c305c2671f74adf229)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "marshalingAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36efa65686dcb4b8a213f27918dd3a8e4b1add60abec9d1547e13dbb97ffa75b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57ed265984f198be54e31da156de1a2ce504b031ab881a0ef1d8aa4b516d8297)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7986b4ae620510512639374161e0477107fa136a5257856c0b344254d95c79b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prehashed")
    def prehashed(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "prehashed"))

    @prehashed.setter
    def prehashed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1efca78147147ed3ac70a100ec56e625492d7e94fcbf11330d2c3187731907c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prehashed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reference")
    def reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reference"))

    @reference.setter
    def reference(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e85201ffbf6ead827de0bb5740cf3b2f9c2634ff1a4ab51b913487559032b60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reference", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="saltLength")
    def salt_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "saltLength"))

    @salt_length.setter
    def salt_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bc1f864e827131b89e10b0e43661e4d47cc558f9e7a94e04602a45fcd73de32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "saltLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signature")
    def signature(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signature"))

    @signature.setter
    def signature(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44d70cd64aeb95845ac7a453f6e0cdedde1b309b38bc783be0f52a6402a9e700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureAlgorithm")
    def signature_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureAlgorithm"))

    @signature_algorithm.setter
    def signature_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52c3e03fe6e12f3daa912ce65f189c7e8ccd196ea5ae582a44c80eee52956ec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureContext")
    def signature_context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureContext"))

    @signature_context.setter
    def signature_context(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7cbea1a3ea39ee79ca3bb4db9876846c5df953f45d2e046833ee5310d61f07c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureContext", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultTransitSign.DataVaultTransitSignConfig",
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
        "path": "path",
        "batch_input": "batchInput",
        "batch_results": "batchResults",
        "context": "context",
        "hash_algorithm": "hashAlgorithm",
        "id": "id",
        "input": "input",
        "key_version": "keyVersion",
        "marshaling_algorithm": "marshalingAlgorithm",
        "namespace": "namespace",
        "prehashed": "prehashed",
        "reference": "reference",
        "salt_length": "saltLength",
        "signature": "signature",
        "signature_algorithm": "signatureAlgorithm",
        "signature_context": "signatureContext",
    },
)
class DataVaultTransitSignConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        path: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        context: typing.Optional[builtins.str] = None,
        hash_algorithm: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input: typing.Optional[builtins.str] = None,
        key_version: typing.Optional[jsii.Number] = None,
        marshaling_algorithm: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reference: typing.Optional[builtins.str] = None,
        salt_length: typing.Optional[builtins.str] = None,
        signature: typing.Optional[builtins.str] = None,
        signature_algorithm: typing.Optional[builtins.str] = None,
        signature_context: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Name of the signing key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#name DataVaultTransitSign#name}
        :param path: The Transit secret backend the key belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#path DataVaultTransitSign#path}
        :param batch_input: Specifies a list of items for processing. When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#batch_input DataVaultTransitSign#batch_input}
        :param batch_results: The results returned from Vault if using batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#batch_results DataVaultTransitSign#batch_results}
        :param context: Base64 encoded context for key derivation. Required if key derivation is enabled; currently only available with ed25519 keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#context DataVaultTransitSign#context}
        :param hash_algorithm: Specifies the hash algorithm to use for supporting key types (notably, not including ed25519 which specifies its own hash algorithm). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#hash_algorithm DataVaultTransitSign#hash_algorithm}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#id DataVaultTransitSign#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input: Specifies the base64 encoded input data. One of input or batch_input must be supplied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#input DataVaultTransitSign#input}
        :param key_version: The version of the key to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#key_version DataVaultTransitSign#key_version}
        :param marshaling_algorithm: Specifies the way in which the signature should be marshaled. This currently only applies to ECDSA keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#marshaling_algorithm DataVaultTransitSign#marshaling_algorithm}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#namespace DataVaultTransitSign#namespace}
        :param prehashed: Set to true when the input is already hashed. If the key type is rsa-2048, rsa-3072 or rsa-4096, then the algorithm used to hash the input should be indicated by the hash_algorithm parameter. Just as the value to sign should be the base64-encoded representation of the exact binary data you want signed, when set, input is expected to be base64-encoded binary hashed data, not hex-formatted. (As an example, on the command line, you could generate a suitable input via openssl dgst -sha256 -binary | base64.) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#prehashed DataVaultTransitSign#prehashed}
        :param reference: A user-supplied string that will be present in the reference field on the corresponding batch_results item in the response, to assist in understanding which result corresponds to a particular input. Only valid on batch requests when using ‘batch_input’ below. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#reference DataVaultTransitSign#reference}
        :param salt_length: The salt length used to sign. This currently only applies to the RSA PSS signature scheme. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#salt_length DataVaultTransitSign#salt_length}
        :param signature: The signature returned from Vault if using input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature DataVaultTransitSign#signature}
        :param signature_algorithm: When using a RSA key, specifies the RSA signature algorithm to use for signing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature_algorithm DataVaultTransitSign#signature_algorithm}
        :param signature_context: Base64 encoded context for Ed25519ctx and Ed25519ph signatures. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature_context DataVaultTransitSign#signature_context}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9a92f3c6ec16e1c2685ff06ced5a09955281b36035f0feb3345deceab3a6172)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument batch_input", value=batch_input, expected_type=type_hints["batch_input"])
            check_type(argname="argument batch_results", value=batch_results, expected_type=type_hints["batch_results"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument hash_algorithm", value=hash_algorithm, expected_type=type_hints["hash_algorithm"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument key_version", value=key_version, expected_type=type_hints["key_version"])
            check_type(argname="argument marshaling_algorithm", value=marshaling_algorithm, expected_type=type_hints["marshaling_algorithm"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument prehashed", value=prehashed, expected_type=type_hints["prehashed"])
            check_type(argname="argument reference", value=reference, expected_type=type_hints["reference"])
            check_type(argname="argument salt_length", value=salt_length, expected_type=type_hints["salt_length"])
            check_type(argname="argument signature", value=signature, expected_type=type_hints["signature"])
            check_type(argname="argument signature_algorithm", value=signature_algorithm, expected_type=type_hints["signature_algorithm"])
            check_type(argname="argument signature_context", value=signature_context, expected_type=type_hints["signature_context"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "path": path,
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
        if batch_input is not None:
            self._values["batch_input"] = batch_input
        if batch_results is not None:
            self._values["batch_results"] = batch_results
        if context is not None:
            self._values["context"] = context
        if hash_algorithm is not None:
            self._values["hash_algorithm"] = hash_algorithm
        if id is not None:
            self._values["id"] = id
        if input is not None:
            self._values["input"] = input
        if key_version is not None:
            self._values["key_version"] = key_version
        if marshaling_algorithm is not None:
            self._values["marshaling_algorithm"] = marshaling_algorithm
        if namespace is not None:
            self._values["namespace"] = namespace
        if prehashed is not None:
            self._values["prehashed"] = prehashed
        if reference is not None:
            self._values["reference"] = reference
        if salt_length is not None:
            self._values["salt_length"] = salt_length
        if signature is not None:
            self._values["signature"] = signature
        if signature_algorithm is not None:
            self._values["signature_algorithm"] = signature_algorithm
        if signature_context is not None:
            self._values["signature_context"] = signature_context

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
        '''Name of the signing key to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#name DataVaultTransitSign#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''The Transit secret backend the key belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#path DataVaultTransitSign#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def batch_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''Specifies a list of items for processing.

        When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#batch_input DataVaultTransitSign#batch_input}
        '''
        result = self._values.get("batch_input")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def batch_results(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''The results returned from Vault if using batch_input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#batch_results DataVaultTransitSign#batch_results}
        '''
        result = self._values.get("batch_results")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def context(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded context for key derivation. Required if key derivation is enabled; currently only available with ed25519 keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#context DataVaultTransitSign#context}
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hash_algorithm(self) -> typing.Optional[builtins.str]:
        '''Specifies the hash algorithm to use for supporting key types (notably, not including ed25519 which specifies its own hash algorithm).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#hash_algorithm DataVaultTransitSign#hash_algorithm}
        '''
        result = self._values.get("hash_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#id DataVaultTransitSign#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input(self) -> typing.Optional[builtins.str]:
        '''Specifies the base64 encoded input data. One of input or batch_input must be supplied.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#input DataVaultTransitSign#input}
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_version(self) -> typing.Optional[jsii.Number]:
        '''The version of the key to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#key_version DataVaultTransitSign#key_version}
        '''
        result = self._values.get("key_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def marshaling_algorithm(self) -> typing.Optional[builtins.str]:
        '''Specifies the way in which the signature should be marshaled. This currently only applies to ECDSA keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#marshaling_algorithm DataVaultTransitSign#marshaling_algorithm}
        '''
        result = self._values.get("marshaling_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#namespace DataVaultTransitSign#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prehashed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true when the input is already hashed.

        If the key type is rsa-2048, rsa-3072 or rsa-4096, then the algorithm used to hash the input should be indicated by the hash_algorithm parameter. Just as the value to sign should be the base64-encoded representation of the exact binary data you want signed, when set, input is expected to be base64-encoded binary hashed data, not hex-formatted. (As an example, on the command line, you could generate a suitable input via openssl dgst -sha256 -binary | base64.)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#prehashed DataVaultTransitSign#prehashed}
        '''
        result = self._values.get("prehashed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def reference(self) -> typing.Optional[builtins.str]:
        '''A user-supplied string that will be present in the reference field on the corresponding batch_results item in the response, to assist in understanding which result corresponds to a particular input.

        Only valid on batch requests when using ‘batch_input’ below.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#reference DataVaultTransitSign#reference}
        '''
        result = self._values.get("reference")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def salt_length(self) -> typing.Optional[builtins.str]:
        '''The salt length used to sign. This currently only applies to the RSA PSS signature scheme.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#salt_length DataVaultTransitSign#salt_length}
        '''
        result = self._values.get("salt_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature(self) -> typing.Optional[builtins.str]:
        '''The signature returned from Vault if using input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature DataVaultTransitSign#signature}
        '''
        result = self._values.get("signature")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_algorithm(self) -> typing.Optional[builtins.str]:
        '''When using a RSA key, specifies the RSA signature algorithm to use for signing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature_algorithm DataVaultTransitSign#signature_algorithm}
        '''
        result = self._values.get("signature_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_context(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded context for Ed25519ctx and Ed25519ph signatures.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_sign#signature_context DataVaultTransitSign#signature_context}
        '''
        result = self._values.get("signature_context")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultTransitSignConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVaultTransitSign",
    "DataVaultTransitSignConfig",
]

publication.publish()

def _typecheckingstub__ec2e9e123b20fc1e92b8e66415e7bf6ad9a57913c33df6919da0258f7bde8954(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    path: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    context: typing.Optional[builtins.str] = None,
    hash_algorithm: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    input: typing.Optional[builtins.str] = None,
    key_version: typing.Optional[jsii.Number] = None,
    marshaling_algorithm: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reference: typing.Optional[builtins.str] = None,
    salt_length: typing.Optional[builtins.str] = None,
    signature: typing.Optional[builtins.str] = None,
    signature_algorithm: typing.Optional[builtins.str] = None,
    signature_context: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__97a9d5d62c8f09d39ee787a1b3460df0bf578b3514b26a81dff1248f47084d51(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cdfb2ab17708dae0003cacdca301f7d2e34b340e69bb6ea71dfefe5d572900b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f09f99c67a810aecc937fdf20a9b2de5747c527cf4a10c6a2993aa9cfbc2f341(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e349ef885a7c306fc4eaa93613024d11454e08e93e8634f232999515dfeeea2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f8a9305e43324013bf0dfb1ae535571220e52a4ea727ade4e03aacf2ffa96f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9ee65f455444aff12e462279d6ff9759e98f56243b7b1c7e5449d5369f29081(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c27860a29ebe0766d0f557b4996397cb316159885496a2b735babb7802c9f1e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af1644fe2a6f4be2a53bc73ed40843316152d9408ef98f42f88ba08eee3f2b47(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6165d9b22f51a558ce70707804c678192d6fd0ac21556c305c2671f74adf229(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36efa65686dcb4b8a213f27918dd3a8e4b1add60abec9d1547e13dbb97ffa75b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57ed265984f198be54e31da156de1a2ce504b031ab881a0ef1d8aa4b516d8297(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7986b4ae620510512639374161e0477107fa136a5257856c0b344254d95c79b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1efca78147147ed3ac70a100ec56e625492d7e94fcbf11330d2c3187731907c1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e85201ffbf6ead827de0bb5740cf3b2f9c2634ff1a4ab51b913487559032b60(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bc1f864e827131b89e10b0e43661e4d47cc558f9e7a94e04602a45fcd73de32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44d70cd64aeb95845ac7a453f6e0cdedde1b309b38bc783be0f52a6402a9e700(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52c3e03fe6e12f3daa912ce65f189c7e8ccd196ea5ae582a44c80eee52956ec3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7cbea1a3ea39ee79ca3bb4db9876846c5df953f45d2e046833ee5310d61f07c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9a92f3c6ec16e1c2685ff06ced5a09955281b36035f0feb3345deceab3a6172(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    path: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    context: typing.Optional[builtins.str] = None,
    hash_algorithm: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    input: typing.Optional[builtins.str] = None,
    key_version: typing.Optional[jsii.Number] = None,
    marshaling_algorithm: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reference: typing.Optional[builtins.str] = None,
    salt_length: typing.Optional[builtins.str] = None,
    signature: typing.Optional[builtins.str] = None,
    signature_algorithm: typing.Optional[builtins.str] = None,
    signature_context: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
