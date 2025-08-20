r'''
# `vault_mfa_totp`

Refer to the Terraform Registry for docs: [`vault_mfa_totp`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp).
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


class MfaTotp(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.mfaTotp.MfaTotp",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp vault_mfa_totp}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        issuer: builtins.str,
        name: builtins.str,
        algorithm: typing.Optional[builtins.str] = None,
        digits: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        key_size: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        qr_size: typing.Optional[jsii.Number] = None,
        skew: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp vault_mfa_totp} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param issuer: The name of the key's issuing organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#issuer MfaTotp#issuer}
        :param name: Name of the MFA method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#name MfaTotp#name}
        :param algorithm: Specifies the hashing algorithm used to generate the TOTP code. Options include 'SHA1', 'SHA256' and 'SHA512'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#algorithm MfaTotp#algorithm}
        :param digits: The number of digits in the generated TOTP token. This value can either be 6 or 8. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#digits MfaTotp#digits}
        :param id: ID computed by Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#id MfaTotp#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_size: Specifies the size in bytes of the generated key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#key_size MfaTotp#key_size}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#namespace MfaTotp#namespace}
        :param period: The length of time used to generate a counter for the TOTP token calculation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#period MfaTotp#period}
        :param qr_size: The pixel size of the generated square QR code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#qr_size MfaTotp#qr_size}
        :param skew: The number of delay periods that are allowed when validating a TOTP token. This value can either be 0 or 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#skew MfaTotp#skew}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40658ed28e4021767c18cddf07237e4bb90dc090ea12b8ef4d3c1a3e8740fded)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MfaTotpConfig(
            issuer=issuer,
            name=name,
            algorithm=algorithm,
            digits=digits,
            id=id,
            key_size=key_size,
            namespace=namespace,
            period=period,
            qr_size=qr_size,
            skew=skew,
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
        '''Generates CDKTF code for importing a MfaTotp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MfaTotp to import.
        :param import_from_id: The id of the existing MfaTotp that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MfaTotp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4885396b39ab26cc60d73ff8944cd6be9575b7432363b57a89d1ccbe2edd4fe4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlgorithm")
    def reset_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithm", []))

    @jsii.member(jsii_name="resetDigits")
    def reset_digits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDigits", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeySize")
    def reset_key_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeySize", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPeriod")
    def reset_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeriod", []))

    @jsii.member(jsii_name="resetQrSize")
    def reset_qr_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQrSize", []))

    @jsii.member(jsii_name="resetSkew")
    def reset_skew(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkew", []))

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
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="digitsInput")
    def digits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "digitsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerInput")
    def issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerInput"))

    @builtins.property
    @jsii.member(jsii_name="keySizeInput")
    def key_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keySizeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="periodInput")
    def period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "periodInput"))

    @builtins.property
    @jsii.member(jsii_name="qrSizeInput")
    def qr_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "qrSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="skewInput")
    def skew_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "skewInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2d3b233dc862039c51f088b6f909236f2190671eb693a88c833838043bb03e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="digits")
    def digits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "digits"))

    @digits.setter
    def digits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c456f15540da03c9d370a4e0022b24891c19a03544cf0cef1f1a611eaff3329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "digits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a43d3d22c0b2b30d3f4d23b7eeae4def97133f17f5397b03eea8e8c28620dcac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3851b94afd538b6b455bc5217edaa1c2df66e13ac0b6d09e22b6c3093a7651d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keySize")
    def key_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keySize"))

    @key_size.setter
    def key_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0de2fe46be6a41ec85490261099a7062ecfc0698b0c0e28d25d9f76b09cc8cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keySize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4efda43ac47451bccdaa6de94e82db125dd1be1342a6beee9ca1e6ada33a57a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__062e32cff31656a253b92107c8a72039a6b7bb11126aaa5cfbd7d5d5f15edeb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="period")
    def period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "period"))

    @period.setter
    def period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f274404fa29bd97035bd2c938d51fb73314f4089457eb468e4541426d9767fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "period", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="qrSize")
    def qr_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "qrSize"))

    @qr_size.setter
    def qr_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ebbdd9802708fadfe1b885a708688c68b80923040b8f35c69e83f731f09aa31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "qrSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skew")
    def skew(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "skew"))

    @skew.setter
    def skew(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f3905f91faa412a8d8dd85dc028276ed74b616210844c16a871fe04a3c1ee2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skew", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.mfaTotp.MfaTotpConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "issuer": "issuer",
        "name": "name",
        "algorithm": "algorithm",
        "digits": "digits",
        "id": "id",
        "key_size": "keySize",
        "namespace": "namespace",
        "period": "period",
        "qr_size": "qrSize",
        "skew": "skew",
    },
)
class MfaTotpConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        issuer: builtins.str,
        name: builtins.str,
        algorithm: typing.Optional[builtins.str] = None,
        digits: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        key_size: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        period: typing.Optional[jsii.Number] = None,
        qr_size: typing.Optional[jsii.Number] = None,
        skew: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param issuer: The name of the key's issuing organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#issuer MfaTotp#issuer}
        :param name: Name of the MFA method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#name MfaTotp#name}
        :param algorithm: Specifies the hashing algorithm used to generate the TOTP code. Options include 'SHA1', 'SHA256' and 'SHA512'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#algorithm MfaTotp#algorithm}
        :param digits: The number of digits in the generated TOTP token. This value can either be 6 or 8. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#digits MfaTotp#digits}
        :param id: ID computed by Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#id MfaTotp#id} Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_size: Specifies the size in bytes of the generated key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#key_size MfaTotp#key_size}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#namespace MfaTotp#namespace}
        :param period: The length of time used to generate a counter for the TOTP token calculation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#period MfaTotp#period}
        :param qr_size: The pixel size of the generated square QR code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#qr_size MfaTotp#qr_size}
        :param skew: The number of delay periods that are allowed when validating a TOTP token. This value can either be 0 or 1. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#skew MfaTotp#skew}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c10cb546c24689a193579c788fdc94fe0ca240bd4194e0de06923436e3b5f337)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument issuer", value=issuer, expected_type=type_hints["issuer"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument digits", value=digits, expected_type=type_hints["digits"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_size", value=key_size, expected_type=type_hints["key_size"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument period", value=period, expected_type=type_hints["period"])
            check_type(argname="argument qr_size", value=qr_size, expected_type=type_hints["qr_size"])
            check_type(argname="argument skew", value=skew, expected_type=type_hints["skew"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "issuer": issuer,
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
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if digits is not None:
            self._values["digits"] = digits
        if id is not None:
            self._values["id"] = id
        if key_size is not None:
            self._values["key_size"] = key_size
        if namespace is not None:
            self._values["namespace"] = namespace
        if period is not None:
            self._values["period"] = period
        if qr_size is not None:
            self._values["qr_size"] = qr_size
        if skew is not None:
            self._values["skew"] = skew

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
    def issuer(self) -> builtins.str:
        '''The name of the key's issuing organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#issuer MfaTotp#issuer}
        '''
        result = self._values.get("issuer")
        assert result is not None, "Required property 'issuer' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the MFA method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#name MfaTotp#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Specifies the hashing algorithm used to generate the TOTP code. Options include 'SHA1', 'SHA256' and 'SHA512'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#algorithm MfaTotp#algorithm}
        '''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def digits(self) -> typing.Optional[jsii.Number]:
        '''The number of digits in the generated TOTP token. This value can either be 6 or 8.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#digits MfaTotp#digits}
        '''
        result = self._values.get("digits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''ID computed by Vault.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#id MfaTotp#id}

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_size(self) -> typing.Optional[jsii.Number]:
        '''Specifies the size in bytes of the generated key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#key_size MfaTotp#key_size}
        '''
        result = self._values.get("key_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#namespace MfaTotp#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def period(self) -> typing.Optional[jsii.Number]:
        '''The length of time used to generate a counter for the TOTP token calculation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#period MfaTotp#period}
        '''
        result = self._values.get("period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def qr_size(self) -> typing.Optional[jsii.Number]:
        '''The pixel size of the generated square QR code.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#qr_size MfaTotp#qr_size}
        '''
        result = self._values.get("qr_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def skew(self) -> typing.Optional[jsii.Number]:
        '''The number of delay periods that are allowed when validating a TOTP token.

        This value can either be 0 or 1.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/mfa_totp#skew MfaTotp#skew}
        '''
        result = self._values.get("skew")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MfaTotpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MfaTotp",
    "MfaTotpConfig",
]

publication.publish()

def _typecheckingstub__40658ed28e4021767c18cddf07237e4bb90dc090ea12b8ef4d3c1a3e8740fded(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    issuer: builtins.str,
    name: builtins.str,
    algorithm: typing.Optional[builtins.str] = None,
    digits: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    key_size: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    qr_size: typing.Optional[jsii.Number] = None,
    skew: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__4885396b39ab26cc60d73ff8944cd6be9575b7432363b57a89d1ccbe2edd4fe4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2d3b233dc862039c51f088b6f909236f2190671eb693a88c833838043bb03e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c456f15540da03c9d370a4e0022b24891c19a03544cf0cef1f1a611eaff3329(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a43d3d22c0b2b30d3f4d23b7eeae4def97133f17f5397b03eea8e8c28620dcac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3851b94afd538b6b455bc5217edaa1c2df66e13ac0b6d09e22b6c3093a7651d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0de2fe46be6a41ec85490261099a7062ecfc0698b0c0e28d25d9f76b09cc8cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4efda43ac47451bccdaa6de94e82db125dd1be1342a6beee9ca1e6ada33a57a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__062e32cff31656a253b92107c8a72039a6b7bb11126aaa5cfbd7d5d5f15edeb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f274404fa29bd97035bd2c938d51fb73314f4089457eb468e4541426d9767fa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ebbdd9802708fadfe1b885a708688c68b80923040b8f35c69e83f731f09aa31(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f3905f91faa412a8d8dd85dc028276ed74b616210844c16a871fe04a3c1ee2b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c10cb546c24689a193579c788fdc94fe0ca240bd4194e0de06923436e3b5f337(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    issuer: builtins.str,
    name: builtins.str,
    algorithm: typing.Optional[builtins.str] = None,
    digits: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    key_size: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    period: typing.Optional[jsii.Number] = None,
    qr_size: typing.Optional[jsii.Number] = None,
    skew: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
