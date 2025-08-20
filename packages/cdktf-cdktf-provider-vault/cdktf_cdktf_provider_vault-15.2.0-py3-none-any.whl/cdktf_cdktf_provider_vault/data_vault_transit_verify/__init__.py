r'''
# `data_vault_transit_verify`

Refer to the Terraform Registry for docs: [`data_vault_transit_verify`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify).
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


class DataVaultTransitVerify(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.dataVaultTransitVerify.DataVaultTransitVerify",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify vault_transit_verify}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        path: builtins.str,
        batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
        cmac: typing.Optional[builtins.str] = None,
        context: typing.Optional[builtins.str] = None,
        hash_algorithm: typing.Optional[builtins.str] = None,
        hmac: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input: typing.Optional[builtins.str] = None,
        mac_length: typing.Optional[jsii.Number] = None,
        marshaling_algorithm: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reference: typing.Optional[builtins.str] = None,
        salt_length: typing.Optional[builtins.str] = None,
        signature: typing.Optional[builtins.str] = None,
        signature_algorithm: typing.Optional[builtins.str] = None,
        signature_context: typing.Optional[builtins.str] = None,
        valid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify vault_transit_verify} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Specifies the name of the encryption key that was used to generate the signature or HMAC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#name DataVaultTransitVerify#name}
        :param path: The Transit secret backend the key belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#path DataVaultTransitVerify#path}
        :param batch_input: Specifies a list of items for processing. When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#batch_input DataVaultTransitVerify#batch_input}
        :param batch_results: The results returned from Vault if using batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#batch_results DataVaultTransitVerify#batch_results}
        :param cmac: (Enterprise only) Specifies the signature output from the /transit/cmac function. One of the following arguments must be supplied signature, hmac or cmac. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#cmac DataVaultTransitVerify#cmac}
        :param context: Base64 encoded context for key derivation. Required if key derivation is enabled; currently only available with ed25519 keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#context DataVaultTransitVerify#context}
        :param hash_algorithm: Specifies the hash algorithm to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#hash_algorithm DataVaultTransitVerify#hash_algorithm}
        :param hmac: Specifies the signature output from the /transit/hmac function. One of the following arguments must be supplied signature, hmac or cmac. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#hmac DataVaultTransitVerify#hmac}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#id DataVaultTransitVerify#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input: Specifies the base64 encoded input data. One of input or batch_input must be supplied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#input DataVaultTransitVerify#input}
        :param mac_length: Specifies the MAC length used to generate a CMAC. The mac_length cannot be larger than the cipher's block size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#mac_length DataVaultTransitVerify#mac_length}
        :param marshaling_algorithm: Specifies the way in which the signature was originally marshaled. This currently only applies to ECDSA keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#marshaling_algorithm DataVaultTransitVerify#marshaling_algorithm}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#namespace DataVaultTransitVerify#namespace}
        :param prehashed: Set to true when the input is already hashed. If the key type is rsa-2048, rsa-3072 or rsa-4096, then the algorithm used to hash the input should be indicated by the hash_algorithm parameter. Just as the value to sign should be the base64-encoded representation of the exact binary data you want signed, when set, input is expected to be base64-encoded binary hashed data, not hex-formatted. (As an example, on the command line, you could generate a suitable input via openssl dgst -sha256 -binary | base64.) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#prehashed DataVaultTransitVerify#prehashed}
        :param reference: A user-supplied string that will be present in the reference field on the corresponding batch_results item in the response, to assist in understanding which result corresponds to a particular input. Only valid on batch requests when using ‘batch_input’ below. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#reference DataVaultTransitVerify#reference}
        :param salt_length: The salt length used to sign. This currently only applies to the RSA PSS signature scheme. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#salt_length DataVaultTransitVerify#salt_length}
        :param signature: Specifies the signature output from the /transit/sign function. One of the following arguments must be supplied signature, hmac or cmac. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature DataVaultTransitVerify#signature}
        :param signature_algorithm: When using a RSA key, specifies the RSA signature algorithm to use for signature verification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature_algorithm DataVaultTransitVerify#signature_algorithm}
        :param signature_context: Base64 encoded context for Ed25519ctx and Ed25519ph signatures. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature_context DataVaultTransitVerify#signature_context}
        :param valid: Indicates whether verification succeeded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#valid DataVaultTransitVerify#valid}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d27e54c331ab2e20b4e1c52a7197718a0706e935595ecd32fef279a2bee61d10)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataVaultTransitVerifyConfig(
            name=name,
            path=path,
            batch_input=batch_input,
            batch_results=batch_results,
            cmac=cmac,
            context=context,
            hash_algorithm=hash_algorithm,
            hmac=hmac,
            id=id,
            input=input,
            mac_length=mac_length,
            marshaling_algorithm=marshaling_algorithm,
            namespace=namespace,
            prehashed=prehashed,
            reference=reference,
            salt_length=salt_length,
            signature=signature,
            signature_algorithm=signature_algorithm,
            signature_context=signature_context,
            valid=valid,
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
        '''Generates CDKTF code for importing a DataVaultTransitVerify resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataVaultTransitVerify to import.
        :param import_from_id: The id of the existing DataVaultTransitVerify that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataVaultTransitVerify to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8942d6e780fa2d15a5d919633603695ea7e99c75c787a21f6100d40ee99f5d7f)
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

    @jsii.member(jsii_name="resetCmac")
    def reset_cmac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCmac", []))

    @jsii.member(jsii_name="resetContext")
    def reset_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContext", []))

    @jsii.member(jsii_name="resetHashAlgorithm")
    def reset_hash_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHashAlgorithm", []))

    @jsii.member(jsii_name="resetHmac")
    def reset_hmac(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHmac", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInput")
    def reset_input(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInput", []))

    @jsii.member(jsii_name="resetMacLength")
    def reset_mac_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMacLength", []))

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

    @jsii.member(jsii_name="resetValid")
    def reset_valid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValid", []))

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
    @jsii.member(jsii_name="cmacInput")
    def cmac_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cmacInput"))

    @builtins.property
    @jsii.member(jsii_name="contextInput")
    def context_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contextInput"))

    @builtins.property
    @jsii.member(jsii_name="hashAlgorithmInput")
    def hash_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hashAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="hmacInput")
    def hmac_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hmacInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="inputInput")
    def input_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputInput"))

    @builtins.property
    @jsii.member(jsii_name="macLengthInput")
    def mac_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "macLengthInput"))

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
    @jsii.member(jsii_name="validInput")
    def valid_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "validInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__963e0cbbb5312616431a8a8c0f388435466d9f089123354b4bc36c77ec682bfa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c037aa5b0a6619b45e2ffe63a730588212e0dc5414561476dbe9ffd2bb88b7e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "batchResults", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cmac")
    def cmac(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cmac"))

    @cmac.setter
    def cmac(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa4996842c9e358796fd8b642493ddad07a181cd164f29e284aee771f41e78d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cmac", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "context"))

    @context.setter
    def context(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f4d308912dc21ab567dfaaa749f9e7a4b95c1efa52249f3fbc4c3e057dbec29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hashAlgorithm")
    def hash_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hashAlgorithm"))

    @hash_algorithm.setter
    def hash_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a694a50b25dd26b993bca72df39d97b9b27b8237e10fa1f3378bcc45b09da97c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hashAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hmac")
    def hmac(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hmac"))

    @hmac.setter
    def hmac(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__768122229bbe4e9f22769fff49f0465b48e6afd9f3fa3b016bbfeeafe1d188bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hmac", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__975e6f49fa63b44a354f7dc3bf5d709f2bb69e4deff3f5b92053e9ddc9c0155f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="input")
    def input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "input"))

    @input.setter
    def input(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a09c36d35728f0e2f0d8b05eb3dbff4ceb99b6d60a24dd3c876f1bdd94360e2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "input", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="macLength")
    def mac_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "macLength"))

    @mac_length.setter
    def mac_length(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10664c5cefa9c279b0bf8326c6b17960bddc7cadeed48b40a27ad15e26ed720b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "macLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="marshalingAlgorithm")
    def marshaling_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "marshalingAlgorithm"))

    @marshaling_algorithm.setter
    def marshaling_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63fa0b47ea172fceb7fab26e20e4aaa8c4b88b99ec5b3b49c051742c1b1f18c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "marshalingAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eed40845dfd67890b1fbfc6137a4cac3db05b788a533a0330916a0cab347589)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb4327edb886df0dc536c0a31f3a939e0338030c4cd35a41d4ebea92eef4d02a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__051358b609774a3fde57c1c11e80b6dbaca3482f613e57f7933cdfb4628a92bd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__77c98e51e6752b3553e27694fd0990f9ddaeed8495edc6a7476585534a54776d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prehashed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reference")
    def reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reference"))

    @reference.setter
    def reference(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fdca60cb8f914ba23f8d1678feac5f15b5125dd156b7b21f908595e72a8f746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reference", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="saltLength")
    def salt_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "saltLength"))

    @salt_length.setter
    def salt_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b7924b60875ec44f9f763d90b5ef687a2a4cd3ea2d87f78eec547fbc78084a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "saltLength", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signature")
    def signature(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signature"))

    @signature.setter
    def signature(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__057f51fad294707c6316b4087eee24f877644fcdad6778a52b91756f85724ba0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureAlgorithm")
    def signature_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureAlgorithm"))

    @signature_algorithm.setter
    def signature_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7109e8493f92e2f48ce93874fed333561e20c6c2a2de386a043fe91b3a484a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureContext")
    def signature_context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureContext"))

    @signature_context.setter
    def signature_context(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a34ac3d472846c7e328bc2b6c744c2b543489d748f0498df482ae4e4edfc7f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureContext", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valid")
    def valid(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "valid"))

    @valid.setter
    def valid(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7115ba1d891a1c1af848b35abe12d9460f3b8b5cc024c0180438be204aff6ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valid", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.dataVaultTransitVerify.DataVaultTransitVerifyConfig",
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
        "cmac": "cmac",
        "context": "context",
        "hash_algorithm": "hashAlgorithm",
        "hmac": "hmac",
        "id": "id",
        "input": "input",
        "mac_length": "macLength",
        "marshaling_algorithm": "marshalingAlgorithm",
        "namespace": "namespace",
        "prehashed": "prehashed",
        "reference": "reference",
        "salt_length": "saltLength",
        "signature": "signature",
        "signature_algorithm": "signatureAlgorithm",
        "signature_context": "signatureContext",
        "valid": "valid",
    },
)
class DataVaultTransitVerifyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cmac: typing.Optional[builtins.str] = None,
        context: typing.Optional[builtins.str] = None,
        hash_algorithm: typing.Optional[builtins.str] = None,
        hmac: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        input: typing.Optional[builtins.str] = None,
        mac_length: typing.Optional[jsii.Number] = None,
        marshaling_algorithm: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reference: typing.Optional[builtins.str] = None,
        salt_length: typing.Optional[builtins.str] = None,
        signature: typing.Optional[builtins.str] = None,
        signature_algorithm: typing.Optional[builtins.str] = None,
        signature_context: typing.Optional[builtins.str] = None,
        valid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Specifies the name of the encryption key that was used to generate the signature or HMAC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#name DataVaultTransitVerify#name}
        :param path: The Transit secret backend the key belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#path DataVaultTransitVerify#path}
        :param batch_input: Specifies a list of items for processing. When this parameter is set, any supplied 'input' or 'context' parameters will be ignored. Responses are returned in the 'batch_results' array component of the 'data' element of the response. Any batch output will preserve the order of the batch input. If the input data value of an item is invalid, the corresponding item in the 'batch_results' will have the key 'error' with a value describing the error. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#batch_input DataVaultTransitVerify#batch_input}
        :param batch_results: The results returned from Vault if using batch_input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#batch_results DataVaultTransitVerify#batch_results}
        :param cmac: (Enterprise only) Specifies the signature output from the /transit/cmac function. One of the following arguments must be supplied signature, hmac or cmac. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#cmac DataVaultTransitVerify#cmac}
        :param context: Base64 encoded context for key derivation. Required if key derivation is enabled; currently only available with ed25519 keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#context DataVaultTransitVerify#context}
        :param hash_algorithm: Specifies the hash algorithm to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#hash_algorithm DataVaultTransitVerify#hash_algorithm}
        :param hmac: Specifies the signature output from the /transit/hmac function. One of the following arguments must be supplied signature, hmac or cmac. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#hmac DataVaultTransitVerify#hmac}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#id DataVaultTransitVerify#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param input: Specifies the base64 encoded input data. One of input or batch_input must be supplied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#input DataVaultTransitVerify#input}
        :param mac_length: Specifies the MAC length used to generate a CMAC. The mac_length cannot be larger than the cipher's block size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#mac_length DataVaultTransitVerify#mac_length}
        :param marshaling_algorithm: Specifies the way in which the signature was originally marshaled. This currently only applies to ECDSA keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#marshaling_algorithm DataVaultTransitVerify#marshaling_algorithm}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#namespace DataVaultTransitVerify#namespace}
        :param prehashed: Set to true when the input is already hashed. If the key type is rsa-2048, rsa-3072 or rsa-4096, then the algorithm used to hash the input should be indicated by the hash_algorithm parameter. Just as the value to sign should be the base64-encoded representation of the exact binary data you want signed, when set, input is expected to be base64-encoded binary hashed data, not hex-formatted. (As an example, on the command line, you could generate a suitable input via openssl dgst -sha256 -binary | base64.) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#prehashed DataVaultTransitVerify#prehashed}
        :param reference: A user-supplied string that will be present in the reference field on the corresponding batch_results item in the response, to assist in understanding which result corresponds to a particular input. Only valid on batch requests when using ‘batch_input’ below. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#reference DataVaultTransitVerify#reference}
        :param salt_length: The salt length used to sign. This currently only applies to the RSA PSS signature scheme. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#salt_length DataVaultTransitVerify#salt_length}
        :param signature: Specifies the signature output from the /transit/sign function. One of the following arguments must be supplied signature, hmac or cmac. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature DataVaultTransitVerify#signature}
        :param signature_algorithm: When using a RSA key, specifies the RSA signature algorithm to use for signature verification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature_algorithm DataVaultTransitVerify#signature_algorithm}
        :param signature_context: Base64 encoded context for Ed25519ctx and Ed25519ph signatures. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature_context DataVaultTransitVerify#signature_context}
        :param valid: Indicates whether verification succeeded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#valid DataVaultTransitVerify#valid}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c66098ebbc7684f58309c13ed598a292c21a1f8a1d53937241f62af258fca47)
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
            check_type(argname="argument cmac", value=cmac, expected_type=type_hints["cmac"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument hash_algorithm", value=hash_algorithm, expected_type=type_hints["hash_algorithm"])
            check_type(argname="argument hmac", value=hmac, expected_type=type_hints["hmac"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument input", value=input, expected_type=type_hints["input"])
            check_type(argname="argument mac_length", value=mac_length, expected_type=type_hints["mac_length"])
            check_type(argname="argument marshaling_algorithm", value=marshaling_algorithm, expected_type=type_hints["marshaling_algorithm"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument prehashed", value=prehashed, expected_type=type_hints["prehashed"])
            check_type(argname="argument reference", value=reference, expected_type=type_hints["reference"])
            check_type(argname="argument salt_length", value=salt_length, expected_type=type_hints["salt_length"])
            check_type(argname="argument signature", value=signature, expected_type=type_hints["signature"])
            check_type(argname="argument signature_algorithm", value=signature_algorithm, expected_type=type_hints["signature_algorithm"])
            check_type(argname="argument signature_context", value=signature_context, expected_type=type_hints["signature_context"])
            check_type(argname="argument valid", value=valid, expected_type=type_hints["valid"])
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
        if cmac is not None:
            self._values["cmac"] = cmac
        if context is not None:
            self._values["context"] = context
        if hash_algorithm is not None:
            self._values["hash_algorithm"] = hash_algorithm
        if hmac is not None:
            self._values["hmac"] = hmac
        if id is not None:
            self._values["id"] = id
        if input is not None:
            self._values["input"] = input
        if mac_length is not None:
            self._values["mac_length"] = mac_length
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
        if valid is not None:
            self._values["valid"] = valid

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
        '''Specifies the name of the encryption key that was used to generate the signature or HMAC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#name DataVaultTransitVerify#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''The Transit secret backend the key belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#path DataVaultTransitVerify#path}
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#batch_input DataVaultTransitVerify#batch_input}
        '''
        result = self._values.get("batch_input")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def batch_results(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]]:
        '''The results returned from Vault if using batch_input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#batch_results DataVaultTransitVerify#batch_results}
        '''
        result = self._values.get("batch_results")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]]], result)

    @builtins.property
    def cmac(self) -> typing.Optional[builtins.str]:
        '''(Enterprise only) Specifies the signature output from the /transit/cmac function.

        One of the following arguments must be supplied signature, hmac or cmac.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#cmac DataVaultTransitVerify#cmac}
        '''
        result = self._values.get("cmac")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded context for key derivation. Required if key derivation is enabled; currently only available with ed25519 keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#context DataVaultTransitVerify#context}
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hash_algorithm(self) -> typing.Optional[builtins.str]:
        '''Specifies the hash algorithm to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#hash_algorithm DataVaultTransitVerify#hash_algorithm}
        '''
        result = self._values.get("hash_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hmac(self) -> typing.Optional[builtins.str]:
        '''Specifies the signature output from the /transit/hmac function.

        One of the following arguments must be supplied signature, hmac or cmac.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#hmac DataVaultTransitVerify#hmac}
        '''
        result = self._values.get("hmac")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#id DataVaultTransitVerify#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def input(self) -> typing.Optional[builtins.str]:
        '''Specifies the base64 encoded input data. One of input or batch_input must be supplied.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#input DataVaultTransitVerify#input}
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mac_length(self) -> typing.Optional[jsii.Number]:
        '''Specifies the MAC length used to generate a CMAC. The mac_length cannot be larger than the cipher's block size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#mac_length DataVaultTransitVerify#mac_length}
        '''
        result = self._values.get("mac_length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def marshaling_algorithm(self) -> typing.Optional[builtins.str]:
        '''Specifies the way in which the signature was originally marshaled. This currently only applies to ECDSA keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#marshaling_algorithm DataVaultTransitVerify#marshaling_algorithm}
        '''
        result = self._values.get("marshaling_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#namespace DataVaultTransitVerify#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prehashed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true when the input is already hashed.

        If the key type is rsa-2048, rsa-3072 or rsa-4096, then the algorithm used to hash the input should be indicated by the hash_algorithm parameter. Just as the value to sign should be the base64-encoded representation of the exact binary data you want signed, when set, input is expected to be base64-encoded binary hashed data, not hex-formatted. (As an example, on the command line, you could generate a suitable input via openssl dgst -sha256 -binary | base64.)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#prehashed DataVaultTransitVerify#prehashed}
        '''
        result = self._values.get("prehashed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def reference(self) -> typing.Optional[builtins.str]:
        '''A user-supplied string that will be present in the reference field on the corresponding batch_results item in the response, to assist in understanding which result corresponds to a particular input.

        Only valid on batch requests when using ‘batch_input’ below.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#reference DataVaultTransitVerify#reference}
        '''
        result = self._values.get("reference")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def salt_length(self) -> typing.Optional[builtins.str]:
        '''The salt length used to sign. This currently only applies to the RSA PSS signature scheme.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#salt_length DataVaultTransitVerify#salt_length}
        '''
        result = self._values.get("salt_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature(self) -> typing.Optional[builtins.str]:
        '''Specifies the signature output from the /transit/sign function.

        One of the following arguments must be supplied signature, hmac or cmac.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature DataVaultTransitVerify#signature}
        '''
        result = self._values.get("signature")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_algorithm(self) -> typing.Optional[builtins.str]:
        '''When using a RSA key, specifies the RSA signature algorithm to use for signature verification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature_algorithm DataVaultTransitVerify#signature_algorithm}
        '''
        result = self._values.get("signature_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_context(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded context for Ed25519ctx and Ed25519ph signatures.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#signature_context DataVaultTransitVerify#signature_context}
        '''
        result = self._values.get("signature_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def valid(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether verification succeeded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/data-sources/transit_verify#valid DataVaultTransitVerify#valid}
        '''
        result = self._values.get("valid")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataVaultTransitVerifyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataVaultTransitVerify",
    "DataVaultTransitVerifyConfig",
]

publication.publish()

def _typecheckingstub__d27e54c331ab2e20b4e1c52a7197718a0706e935595ecd32fef279a2bee61d10(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    path: builtins.str,
    batch_input: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    batch_results: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Mapping[builtins.str, builtins.str]]]] = None,
    cmac: typing.Optional[builtins.str] = None,
    context: typing.Optional[builtins.str] = None,
    hash_algorithm: typing.Optional[builtins.str] = None,
    hmac: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    input: typing.Optional[builtins.str] = None,
    mac_length: typing.Optional[jsii.Number] = None,
    marshaling_algorithm: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reference: typing.Optional[builtins.str] = None,
    salt_length: typing.Optional[builtins.str] = None,
    signature: typing.Optional[builtins.str] = None,
    signature_algorithm: typing.Optional[builtins.str] = None,
    signature_context: typing.Optional[builtins.str] = None,
    valid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__8942d6e780fa2d15a5d919633603695ea7e99c75c787a21f6100d40ee99f5d7f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__963e0cbbb5312616431a8a8c0f388435466d9f089123354b4bc36c77ec682bfa(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c037aa5b0a6619b45e2ffe63a730588212e0dc5414561476dbe9ffd2bb88b7e4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[typing.Mapping[builtins.str, builtins.str]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa4996842c9e358796fd8b642493ddad07a181cd164f29e284aee771f41e78d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f4d308912dc21ab567dfaaa749f9e7a4b95c1efa52249f3fbc4c3e057dbec29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a694a50b25dd26b993bca72df39d97b9b27b8237e10fa1f3378bcc45b09da97c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__768122229bbe4e9f22769fff49f0465b48e6afd9f3fa3b016bbfeeafe1d188bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__975e6f49fa63b44a354f7dc3bf5d709f2bb69e4deff3f5b92053e9ddc9c0155f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a09c36d35728f0e2f0d8b05eb3dbff4ceb99b6d60a24dd3c876f1bdd94360e2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10664c5cefa9c279b0bf8326c6b17960bddc7cadeed48b40a27ad15e26ed720b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63fa0b47ea172fceb7fab26e20e4aaa8c4b88b99ec5b3b49c051742c1b1f18c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eed40845dfd67890b1fbfc6137a4cac3db05b788a533a0330916a0cab347589(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb4327edb886df0dc536c0a31f3a939e0338030c4cd35a41d4ebea92eef4d02a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__051358b609774a3fde57c1c11e80b6dbaca3482f613e57f7933cdfb4628a92bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77c98e51e6752b3553e27694fd0990f9ddaeed8495edc6a7476585534a54776d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fdca60cb8f914ba23f8d1678feac5f15b5125dd156b7b21f908595e72a8f746(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b7924b60875ec44f9f763d90b5ef687a2a4cd3ea2d87f78eec547fbc78084a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__057f51fad294707c6316b4087eee24f877644fcdad6778a52b91756f85724ba0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7109e8493f92e2f48ce93874fed333561e20c6c2a2de386a043fe91b3a484a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a34ac3d472846c7e328bc2b6c744c2b543489d748f0498df482ae4e4edfc7f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7115ba1d891a1c1af848b35abe12d9460f3b8b5cc024c0180438be204aff6ad(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c66098ebbc7684f58309c13ed598a292c21a1f8a1d53937241f62af258fca47(
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
    cmac: typing.Optional[builtins.str] = None,
    context: typing.Optional[builtins.str] = None,
    hash_algorithm: typing.Optional[builtins.str] = None,
    hmac: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    input: typing.Optional[builtins.str] = None,
    mac_length: typing.Optional[jsii.Number] = None,
    marshaling_algorithm: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    prehashed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reference: typing.Optional[builtins.str] = None,
    salt_length: typing.Optional[builtins.str] = None,
    signature: typing.Optional[builtins.str] = None,
    signature_algorithm: typing.Optional[builtins.str] = None,
    signature_context: typing.Optional[builtins.str] = None,
    valid: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
