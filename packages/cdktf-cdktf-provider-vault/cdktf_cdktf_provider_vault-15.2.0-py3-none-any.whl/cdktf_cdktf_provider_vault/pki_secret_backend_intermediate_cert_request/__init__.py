r'''
# `vault_pki_secret_backend_intermediate_cert_request`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_intermediate_cert_request`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request).
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


class PkiSecretBackendIntermediateCertRequest(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendIntermediateCertRequest.PkiSecretBackendIntermediateCertRequest",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request vault_pki_secret_backend_intermediate_cert_request}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        common_name: builtins.str,
        type: builtins.str,
        add_basic_constraints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        country: typing.Optional[builtins.str] = None,
        exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_ref: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        locality: typing.Optional[builtins.str] = None,
        managed_key_id: typing.Optional[builtins.str] = None,
        managed_key_name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        private_key_format: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        street_address: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request vault_pki_secret_backend_intermediate_cert_request} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#backend PkiSecretBackendIntermediateCertRequest#backend}
        :param common_name: CN of intermediate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#common_name PkiSecretBackendIntermediateCertRequest#common_name}
        :param type: Type of intermediate to create. Must be either "existing", "exported", "internal" or "kms". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#type PkiSecretBackendIntermediateCertRequest#type}
        :param add_basic_constraints: Set 'CA: true' in a Basic Constraints extension. Only needed as a workaround in some compatibility scenarios with Active Directory Certificate Services. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#add_basic_constraints PkiSecretBackendIntermediateCertRequest#add_basic_constraints}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#alt_names PkiSecretBackendIntermediateCertRequest#alt_names}
        :param country: The country. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#country PkiSecretBackendIntermediateCertRequest#country}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#exclude_cn_from_sans PkiSecretBackendIntermediateCertRequest#exclude_cn_from_sans}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#format PkiSecretBackendIntermediateCertRequest#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#id PkiSecretBackendIntermediateCertRequest#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#ip_sans PkiSecretBackendIntermediateCertRequest#ip_sans}
        :param key_bits: The number of bits to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_bits PkiSecretBackendIntermediateCertRequest#key_bits}
        :param key_name: When a new key is created with this request, optionally specifies the name for this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_name PkiSecretBackendIntermediateCertRequest#key_name}
        :param key_ref: Specifies the key to use for generating this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_ref PkiSecretBackendIntermediateCertRequest#key_ref}
        :param key_type: The desired key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_type PkiSecretBackendIntermediateCertRequest#key_type}
        :param key_usage: Specify the key usages to encode in the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_usage PkiSecretBackendIntermediateCertRequest#key_usage}
        :param locality: The locality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#locality PkiSecretBackendIntermediateCertRequest#locality}
        :param managed_key_id: The ID of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#managed_key_id PkiSecretBackendIntermediateCertRequest#managed_key_id}
        :param managed_key_name: The name of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#managed_key_name PkiSecretBackendIntermediateCertRequest#managed_key_name}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#namespace PkiSecretBackendIntermediateCertRequest#namespace}
        :param organization: The organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#organization PkiSecretBackendIntermediateCertRequest#organization}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#other_sans PkiSecretBackendIntermediateCertRequest#other_sans}
        :param ou: The organization unit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#ou PkiSecretBackendIntermediateCertRequest#ou}
        :param postal_code: The postal code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#postal_code PkiSecretBackendIntermediateCertRequest#postal_code}
        :param private_key_format: The private key format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#private_key_format PkiSecretBackendIntermediateCertRequest#private_key_format}
        :param province: The province. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#province PkiSecretBackendIntermediateCertRequest#province}
        :param serial_number: The requested Subject's named serial number. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#serial_number PkiSecretBackendIntermediateCertRequest#serial_number}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#signature_bits PkiSecretBackendIntermediateCertRequest#signature_bits}
        :param street_address: The street address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#street_address PkiSecretBackendIntermediateCertRequest#street_address}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#uri_sans PkiSecretBackendIntermediateCertRequest#uri_sans}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__541809fe9c62cac752db1b18be7325c575458795df39b93166c3015d8342ce30)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendIntermediateCertRequestConfig(
            backend=backend,
            common_name=common_name,
            type=type,
            add_basic_constraints=add_basic_constraints,
            alt_names=alt_names,
            country=country,
            exclude_cn_from_sans=exclude_cn_from_sans,
            format=format,
            id=id,
            ip_sans=ip_sans,
            key_bits=key_bits,
            key_name=key_name,
            key_ref=key_ref,
            key_type=key_type,
            key_usage=key_usage,
            locality=locality,
            managed_key_id=managed_key_id,
            managed_key_name=managed_key_name,
            namespace=namespace,
            organization=organization,
            other_sans=other_sans,
            ou=ou,
            postal_code=postal_code,
            private_key_format=private_key_format,
            province=province,
            serial_number=serial_number,
            signature_bits=signature_bits,
            street_address=street_address,
            uri_sans=uri_sans,
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
        '''Generates CDKTF code for importing a PkiSecretBackendIntermediateCertRequest resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendIntermediateCertRequest to import.
        :param import_from_id: The id of the existing PkiSecretBackendIntermediateCertRequest that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendIntermediateCertRequest to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48d70692ce1f7087393ac2d482fac43ddd23e8d5d1dc38306d7140ddb4fdaf2b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAddBasicConstraints")
    def reset_add_basic_constraints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddBasicConstraints", []))

    @jsii.member(jsii_name="resetAltNames")
    def reset_alt_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAltNames", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetExcludeCnFromSans")
    def reset_exclude_cn_from_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeCnFromSans", []))

    @jsii.member(jsii_name="resetFormat")
    def reset_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormat", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpSans")
    def reset_ip_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpSans", []))

    @jsii.member(jsii_name="resetKeyBits")
    def reset_key_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyBits", []))

    @jsii.member(jsii_name="resetKeyName")
    def reset_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyName", []))

    @jsii.member(jsii_name="resetKeyRef")
    def reset_key_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyRef", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetKeyUsage")
    def reset_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyUsage", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetManagedKeyId")
    def reset_managed_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedKeyId", []))

    @jsii.member(jsii_name="resetManagedKeyName")
    def reset_managed_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManagedKeyName", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetOtherSans")
    def reset_other_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOtherSans", []))

    @jsii.member(jsii_name="resetOu")
    def reset_ou(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOu", []))

    @jsii.member(jsii_name="resetPostalCode")
    def reset_postal_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostalCode", []))

    @jsii.member(jsii_name="resetPrivateKeyFormat")
    def reset_private_key_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyFormat", []))

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetSerialNumber")
    def reset_serial_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSerialNumber", []))

    @jsii.member(jsii_name="resetSignatureBits")
    def reset_signature_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignatureBits", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

    @jsii.member(jsii_name="resetUriSans")
    def reset_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUriSans", []))

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
    @jsii.member(jsii_name="csr")
    def csr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csr"))

    @builtins.property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyType")
    def private_key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyType"))

    @builtins.property
    @jsii.member(jsii_name="addBasicConstraintsInput")
    def add_basic_constraints_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "addBasicConstraintsInput"))

    @builtins.property
    @jsii.member(jsii_name="altNamesInput")
    def alt_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "altNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeCnFromSansInput")
    def exclude_cn_from_sans_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeCnFromSansInput"))

    @builtins.property
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipSansInput")
    def ip_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipSansInput"))

    @builtins.property
    @jsii.member(jsii_name="keyBitsInput")
    def key_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "keyBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyNameInput")
    def key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="keyRefInput")
    def key_ref_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyRefInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="keyUsageInput")
    def key_usage_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "keyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localityInput"))

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
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property
    @jsii.member(jsii_name="otherSansInput")
    def other_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "otherSansInput"))

    @builtins.property
    @jsii.member(jsii_name="ouInput")
    def ou_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ouInput"))

    @builtins.property
    @jsii.member(jsii_name="postalCodeInput")
    def postal_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postalCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyFormatInput")
    def private_key_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provinceInput"))

    @builtins.property
    @jsii.member(jsii_name="serialNumberInput")
    def serial_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serialNumberInput"))

    @builtins.property
    @jsii.member(jsii_name="signatureBitsInput")
    def signature_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "signatureBitsInput"))

    @builtins.property
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streetAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="uriSansInput")
    def uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "uriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="addBasicConstraints")
    def add_basic_constraints(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "addBasicConstraints"))

    @add_basic_constraints.setter
    def add_basic_constraints(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3763586802f25a7f87471c9c39b5e5c4820d87cbfea1d5556843acd3d626539d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addBasicConstraints", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="altNames")
    def alt_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "altNames"))

    @alt_names.setter
    def alt_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d822e56c661dff4ed7226e3505f7bb9c67275aca7cec7fb154a6e3bf8216376f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__801cdf23771b375a508c7b95f6d7ff73529f6cb5cc1cd2196aa52d0b09db1476)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f90c0bb5c1915ee05f8dc5cd6eb18dc03767ba3371902249ebfb120f1ac918fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d698d4c5efd22e541f89efbc9f76eb6a1ad185113edfeea4d6f0cfd069897d89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "country", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="excludeCnFromSans")
    def exclude_cn_from_sans(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludeCnFromSans"))

    @exclude_cn_from_sans.setter
    def exclude_cn_from_sans(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2127fb5210f9a55ed21b3adc20995227e80b3ea22cf728179e53c9aa41016c94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeCnFromSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0efd1ecd0f87a230935ffa223a03e17c2d23332ba3c030be1e641f5ebe9616c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36d1082f4e7449142f7493dbdcefbd0ce7ffca2fa6d40371f85187564d2565c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipSans")
    def ip_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipSans"))

    @ip_sans.setter
    def ip_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca18b1325684fc83b3a2f4891b89eb03de955ec0e6f43d26835e3f8e5a688c8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyBits")
    def key_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "keyBits"))

    @key_bits.setter
    def key_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a967c4b609cca9320a2f835c652f9c62bb5565f48a4268367e2afb71e5454e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyName")
    def key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyName"))

    @key_name.setter
    def key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e14f1024e0aadf0b6e45d8049b9fc31b767d10116cc0b61ac376c58aa90943f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyRef")
    def key_ref(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyRef"))

    @key_ref.setter
    def key_ref(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6cba68c3980064d2030d97567705c2ded950f90ff2fa5e3c75451c91fbc8dee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyRef", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38832bf1144def79084371142d4889b684ceb16df59e2d84cf5df9269c9adc47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyUsage")
    def key_usage(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keyUsage"))

    @key_usage.setter
    def key_usage(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6acffc887f09a1d4373dc00a6bb25d65f78dd3dc15105a0d2b787ea2b8871b6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyUsage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="locality")
    def locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2c1f52467ae6caab8e3dd6f12666379bc93103b1f17ef0a1305983a88cefc6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locality", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedKeyId")
    def managed_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedKeyId"))

    @managed_key_id.setter
    def managed_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d5f41e3c7f4629ded070303bcb23f8839ff6fb2395a2597b6c20df80d401a22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="managedKeyName")
    def managed_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "managedKeyName"))

    @managed_key_name.setter
    def managed_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9cf1d23261615e200d95bf100024f4abfb4e15e68b7a7dd2d723370eee79463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "managedKeyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61dac9a0b326a103a11c423a1f9804747b6274d2550169cbad6b3979d82d0d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f43d131b181965401ae81fa68b8ba9bbc1727f20e7837ae20c5173a318f4300c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="otherSans")
    def other_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "otherSans"))

    @other_sans.setter
    def other_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c61507d718126508f364dea3ea6481fba724bd3f10bae597172413b61d0b37e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "otherSans", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ou")
    def ou(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ou"))

    @ou.setter
    def ou(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9493bd490da1b591649e100c4c7ee5e170e50a32d54a66cc63442e9b88d17765)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ou", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f66cb3dea934f645cb247bdf87c8453a87df901814d811c8ae784d85edd2e14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postalCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyFormat")
    def private_key_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyFormat"))

    @private_key_format.setter
    def private_key_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75229867952eebaeda0b68008ac95095f3c408bd07f31dd09b6e2bb2906faab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="province")
    def province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "province"))

    @province.setter
    def province(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0411a2feafeb79c528a89c1c5828670f10eb5874d6b8e3bfb55eb87f68822afd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "province", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @serial_number.setter
    def serial_number(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b4e1124648684171ca8807ff542bd2a921eadcb29be2cd4b1a01055d6813185)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serialNumber", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signatureBits")
    def signature_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "signatureBits"))

    @signature_bits.setter
    def signature_bits(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f2a08cc80263d595f6e3636cfcee30c75a2c05cd4f6a058275625d79b45dbf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signatureBits", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e88528560bba5645feed0766b4a5b6b83a5c78b0dcbeb369a508aa80d5fb5356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "streetAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c59078c9e1e9dc93ac9b0c613a58659eb86f2e940b7e64b1ef31ac0e2c92a50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b160b4af6ef76f15ade1084cdaf1456878f90ef51b7537aefcd5b543572edcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendIntermediateCertRequest.PkiSecretBackendIntermediateCertRequestConfig",
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
        "common_name": "commonName",
        "type": "type",
        "add_basic_constraints": "addBasicConstraints",
        "alt_names": "altNames",
        "country": "country",
        "exclude_cn_from_sans": "excludeCnFromSans",
        "format": "format",
        "id": "id",
        "ip_sans": "ipSans",
        "key_bits": "keyBits",
        "key_name": "keyName",
        "key_ref": "keyRef",
        "key_type": "keyType",
        "key_usage": "keyUsage",
        "locality": "locality",
        "managed_key_id": "managedKeyId",
        "managed_key_name": "managedKeyName",
        "namespace": "namespace",
        "organization": "organization",
        "other_sans": "otherSans",
        "ou": "ou",
        "postal_code": "postalCode",
        "private_key_format": "privateKeyFormat",
        "province": "province",
        "serial_number": "serialNumber",
        "signature_bits": "signatureBits",
        "street_address": "streetAddress",
        "uri_sans": "uriSans",
    },
)
class PkiSecretBackendIntermediateCertRequestConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        common_name: builtins.str,
        type: builtins.str,
        add_basic_constraints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        country: typing.Optional[builtins.str] = None,
        exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        key_bits: typing.Optional[jsii.Number] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_ref: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
        locality: typing.Optional[builtins.str] = None,
        managed_key_id: typing.Optional[builtins.str] = None,
        managed_key_name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        ou: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        private_key_format: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        signature_bits: typing.Optional[jsii.Number] = None,
        street_address: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#backend PkiSecretBackendIntermediateCertRequest#backend}
        :param common_name: CN of intermediate to create. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#common_name PkiSecretBackendIntermediateCertRequest#common_name}
        :param type: Type of intermediate to create. Must be either "existing", "exported", "internal" or "kms". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#type PkiSecretBackendIntermediateCertRequest#type}
        :param add_basic_constraints: Set 'CA: true' in a Basic Constraints extension. Only needed as a workaround in some compatibility scenarios with Active Directory Certificate Services. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#add_basic_constraints PkiSecretBackendIntermediateCertRequest#add_basic_constraints}
        :param alt_names: List of alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#alt_names PkiSecretBackendIntermediateCertRequest#alt_names}
        :param country: The country. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#country PkiSecretBackendIntermediateCertRequest#country}
        :param exclude_cn_from_sans: Flag to exclude CN from SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#exclude_cn_from_sans PkiSecretBackendIntermediateCertRequest#exclude_cn_from_sans}
        :param format: The format of data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#format PkiSecretBackendIntermediateCertRequest#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#id PkiSecretBackendIntermediateCertRequest#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_sans: List of alternative IPs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#ip_sans PkiSecretBackendIntermediateCertRequest#ip_sans}
        :param key_bits: The number of bits to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_bits PkiSecretBackendIntermediateCertRequest#key_bits}
        :param key_name: When a new key is created with this request, optionally specifies the name for this. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_name PkiSecretBackendIntermediateCertRequest#key_name}
        :param key_ref: Specifies the key to use for generating this request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_ref PkiSecretBackendIntermediateCertRequest#key_ref}
        :param key_type: The desired key type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_type PkiSecretBackendIntermediateCertRequest#key_type}
        :param key_usage: Specify the key usages to encode in the generated certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_usage PkiSecretBackendIntermediateCertRequest#key_usage}
        :param locality: The locality. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#locality PkiSecretBackendIntermediateCertRequest#locality}
        :param managed_key_id: The ID of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#managed_key_id PkiSecretBackendIntermediateCertRequest#managed_key_id}
        :param managed_key_name: The name of the previously configured managed key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#managed_key_name PkiSecretBackendIntermediateCertRequest#managed_key_name}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#namespace PkiSecretBackendIntermediateCertRequest#namespace}
        :param organization: The organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#organization PkiSecretBackendIntermediateCertRequest#organization}
        :param other_sans: List of other SANs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#other_sans PkiSecretBackendIntermediateCertRequest#other_sans}
        :param ou: The organization unit. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#ou PkiSecretBackendIntermediateCertRequest#ou}
        :param postal_code: The postal code. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#postal_code PkiSecretBackendIntermediateCertRequest#postal_code}
        :param private_key_format: The private key format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#private_key_format PkiSecretBackendIntermediateCertRequest#private_key_format}
        :param province: The province. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#province PkiSecretBackendIntermediateCertRequest#province}
        :param serial_number: The requested Subject's named serial number. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#serial_number PkiSecretBackendIntermediateCertRequest#serial_number}
        :param signature_bits: The number of bits to use in the signature algorithm. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#signature_bits PkiSecretBackendIntermediateCertRequest#signature_bits}
        :param street_address: The street address. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#street_address PkiSecretBackendIntermediateCertRequest#street_address}
        :param uri_sans: List of alternative URIs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#uri_sans PkiSecretBackendIntermediateCertRequest#uri_sans}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a80c811048c32135a8cbf92b4ecd7f881815fe5c77bfb8374fd7ee5c07cb350)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument add_basic_constraints", value=add_basic_constraints, expected_type=type_hints["add_basic_constraints"])
            check_type(argname="argument alt_names", value=alt_names, expected_type=type_hints["alt_names"])
            check_type(argname="argument country", value=country, expected_type=type_hints["country"])
            check_type(argname="argument exclude_cn_from_sans", value=exclude_cn_from_sans, expected_type=type_hints["exclude_cn_from_sans"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_sans", value=ip_sans, expected_type=type_hints["ip_sans"])
            check_type(argname="argument key_bits", value=key_bits, expected_type=type_hints["key_bits"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument key_ref", value=key_ref, expected_type=type_hints["key_ref"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument key_usage", value=key_usage, expected_type=type_hints["key_usage"])
            check_type(argname="argument locality", value=locality, expected_type=type_hints["locality"])
            check_type(argname="argument managed_key_id", value=managed_key_id, expected_type=type_hints["managed_key_id"])
            check_type(argname="argument managed_key_name", value=managed_key_name, expected_type=type_hints["managed_key_name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
            check_type(argname="argument other_sans", value=other_sans, expected_type=type_hints["other_sans"])
            check_type(argname="argument ou", value=ou, expected_type=type_hints["ou"])
            check_type(argname="argument postal_code", value=postal_code, expected_type=type_hints["postal_code"])
            check_type(argname="argument private_key_format", value=private_key_format, expected_type=type_hints["private_key_format"])
            check_type(argname="argument province", value=province, expected_type=type_hints["province"])
            check_type(argname="argument serial_number", value=serial_number, expected_type=type_hints["serial_number"])
            check_type(argname="argument signature_bits", value=signature_bits, expected_type=type_hints["signature_bits"])
            check_type(argname="argument street_address", value=street_address, expected_type=type_hints["street_address"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "common_name": common_name,
            "type": type,
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
        if add_basic_constraints is not None:
            self._values["add_basic_constraints"] = add_basic_constraints
        if alt_names is not None:
            self._values["alt_names"] = alt_names
        if country is not None:
            self._values["country"] = country
        if exclude_cn_from_sans is not None:
            self._values["exclude_cn_from_sans"] = exclude_cn_from_sans
        if format is not None:
            self._values["format"] = format
        if id is not None:
            self._values["id"] = id
        if ip_sans is not None:
            self._values["ip_sans"] = ip_sans
        if key_bits is not None:
            self._values["key_bits"] = key_bits
        if key_name is not None:
            self._values["key_name"] = key_name
        if key_ref is not None:
            self._values["key_ref"] = key_ref
        if key_type is not None:
            self._values["key_type"] = key_type
        if key_usage is not None:
            self._values["key_usage"] = key_usage
        if locality is not None:
            self._values["locality"] = locality
        if managed_key_id is not None:
            self._values["managed_key_id"] = managed_key_id
        if managed_key_name is not None:
            self._values["managed_key_name"] = managed_key_name
        if namespace is not None:
            self._values["namespace"] = namespace
        if organization is not None:
            self._values["organization"] = organization
        if other_sans is not None:
            self._values["other_sans"] = other_sans
        if ou is not None:
            self._values["ou"] = ou
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if private_key_format is not None:
            self._values["private_key_format"] = private_key_format
        if province is not None:
            self._values["province"] = province
        if serial_number is not None:
            self._values["serial_number"] = serial_number
        if signature_bits is not None:
            self._values["signature_bits"] = signature_bits
        if street_address is not None:
            self._values["street_address"] = street_address
        if uri_sans is not None:
            self._values["uri_sans"] = uri_sans

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#backend PkiSecretBackendIntermediateCertRequest#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def common_name(self) -> builtins.str:
        '''CN of intermediate to create.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#common_name PkiSecretBackendIntermediateCertRequest#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Type of intermediate to create. Must be either "existing", "exported", "internal" or "kms".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#type PkiSecretBackendIntermediateCertRequest#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def add_basic_constraints(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set 'CA: true' in a Basic Constraints extension.

        Only needed as
        a workaround in some compatibility scenarios with Active Directory Certificate Services.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#add_basic_constraints PkiSecretBackendIntermediateCertRequest#add_basic_constraints}
        '''
        result = self._values.get("add_basic_constraints")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def alt_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#alt_names PkiSecretBackendIntermediateCertRequest#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''The country.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#country PkiSecretBackendIntermediateCertRequest#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exclude_cn_from_sans(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag to exclude CN from SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#exclude_cn_from_sans PkiSecretBackendIntermediateCertRequest#exclude_cn_from_sans}
        '''
        result = self._values.get("exclude_cn_from_sans")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''The format of data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#format PkiSecretBackendIntermediateCertRequest#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#id PkiSecretBackendIntermediateCertRequest#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative IPs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#ip_sans PkiSecretBackendIntermediateCertRequest#ip_sans}
        '''
        result = self._values.get("ip_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_bits PkiSecretBackendIntermediateCertRequest#key_bits}
        '''
        result = self._values.get("key_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''When a new key is created with this request, optionally specifies the name for this.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_name PkiSecretBackendIntermediateCertRequest#key_name}
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_ref(self) -> typing.Optional[builtins.str]:
        '''Specifies the key to use for generating this request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_ref PkiSecretBackendIntermediateCertRequest#key_ref}
        '''
        result = self._values.get("key_ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''The desired key type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_type PkiSecretBackendIntermediateCertRequest#key_type}
        '''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_usage(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Specify the key usages to encode in the generated certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#key_usage PkiSecretBackendIntermediateCertRequest#key_usage}
        '''
        result = self._values.get("key_usage")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''The locality.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#locality PkiSecretBackendIntermediateCertRequest#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_key_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the previously configured managed key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#managed_key_id PkiSecretBackendIntermediateCertRequest#managed_key_id}
        '''
        result = self._values.get("managed_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managed_key_name(self) -> typing.Optional[builtins.str]:
        '''The name of the previously configured managed key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#managed_key_name PkiSecretBackendIntermediateCertRequest#managed_key_name}
        '''
        result = self._values.get("managed_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#namespace PkiSecretBackendIntermediateCertRequest#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''The organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#organization PkiSecretBackendIntermediateCertRequest#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def other_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of other SANs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#other_sans PkiSecretBackendIntermediateCertRequest#other_sans}
        '''
        result = self._values.get("other_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ou(self) -> typing.Optional[builtins.str]:
        '''The organization unit.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#ou PkiSecretBackendIntermediateCertRequest#ou}
        '''
        result = self._values.get("ou")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''The postal code.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#postal_code PkiSecretBackendIntermediateCertRequest#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_format(self) -> typing.Optional[builtins.str]:
        '''The private key format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#private_key_format PkiSecretBackendIntermediateCertRequest#private_key_format}
        '''
        result = self._values.get("private_key_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''The province.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#province PkiSecretBackendIntermediateCertRequest#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serial_number(self) -> typing.Optional[builtins.str]:
        '''The requested Subject's named serial number.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#serial_number PkiSecretBackendIntermediateCertRequest#serial_number}
        '''
        result = self._values.get("serial_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signature_bits(self) -> typing.Optional[jsii.Number]:
        '''The number of bits to use in the signature algorithm.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#signature_bits PkiSecretBackendIntermediateCertRequest#signature_bits}
        '''
        result = self._values.get("signature_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def street_address(self) -> typing.Optional[builtins.str]:
        '''The street address.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#street_address PkiSecretBackendIntermediateCertRequest#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of alternative URIs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_intermediate_cert_request#uri_sans PkiSecretBackendIntermediateCertRequest#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendIntermediateCertRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendIntermediateCertRequest",
    "PkiSecretBackendIntermediateCertRequestConfig",
]

publication.publish()

def _typecheckingstub__541809fe9c62cac752db1b18be7325c575458795df39b93166c3015d8342ce30(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    common_name: builtins.str,
    type: builtins.str,
    add_basic_constraints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    country: typing.Optional[builtins.str] = None,
    exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_ref: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    locality: typing.Optional[builtins.str] = None,
    managed_key_id: typing.Optional[builtins.str] = None,
    managed_key_name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[builtins.str] = None,
    postal_code: typing.Optional[builtins.str] = None,
    private_key_format: typing.Optional[builtins.str] = None,
    province: typing.Optional[builtins.str] = None,
    serial_number: typing.Optional[builtins.str] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    street_address: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__48d70692ce1f7087393ac2d482fac43ddd23e8d5d1dc38306d7140ddb4fdaf2b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3763586802f25a7f87471c9c39b5e5c4820d87cbfea1d5556843acd3d626539d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d822e56c661dff4ed7226e3505f7bb9c67275aca7cec7fb154a6e3bf8216376f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__801cdf23771b375a508c7b95f6d7ff73529f6cb5cc1cd2196aa52d0b09db1476(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f90c0bb5c1915ee05f8dc5cd6eb18dc03767ba3371902249ebfb120f1ac918fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d698d4c5efd22e541f89efbc9f76eb6a1ad185113edfeea4d6f0cfd069897d89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2127fb5210f9a55ed21b3adc20995227e80b3ea22cf728179e53c9aa41016c94(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0efd1ecd0f87a230935ffa223a03e17c2d23332ba3c030be1e641f5ebe9616c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36d1082f4e7449142f7493dbdcefbd0ce7ffca2fa6d40371f85187564d2565c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca18b1325684fc83b3a2f4891b89eb03de955ec0e6f43d26835e3f8e5a688c8b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a967c4b609cca9320a2f835c652f9c62bb5565f48a4268367e2afb71e5454e5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e14f1024e0aadf0b6e45d8049b9fc31b767d10116cc0b61ac376c58aa90943f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6cba68c3980064d2030d97567705c2ded950f90ff2fa5e3c75451c91fbc8dee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38832bf1144def79084371142d4889b684ceb16df59e2d84cf5df9269c9adc47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6acffc887f09a1d4373dc00a6bb25d65f78dd3dc15105a0d2b787ea2b8871b6c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2c1f52467ae6caab8e3dd6f12666379bc93103b1f17ef0a1305983a88cefc6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d5f41e3c7f4629ded070303bcb23f8839ff6fb2395a2597b6c20df80d401a22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9cf1d23261615e200d95bf100024f4abfb4e15e68b7a7dd2d723370eee79463(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61dac9a0b326a103a11c423a1f9804747b6274d2550169cbad6b3979d82d0d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f43d131b181965401ae81fa68b8ba9bbc1727f20e7837ae20c5173a318f4300c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c61507d718126508f364dea3ea6481fba724bd3f10bae597172413b61d0b37e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9493bd490da1b591649e100c4c7ee5e170e50a32d54a66cc63442e9b88d17765(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f66cb3dea934f645cb247bdf87c8453a87df901814d811c8ae784d85edd2e14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75229867952eebaeda0b68008ac95095f3c408bd07f31dd09b6e2bb2906faab4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0411a2feafeb79c528a89c1c5828670f10eb5874d6b8e3bfb55eb87f68822afd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b4e1124648684171ca8807ff542bd2a921eadcb29be2cd4b1a01055d6813185(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f2a08cc80263d595f6e3636cfcee30c75a2c05cd4f6a058275625d79b45dbf8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e88528560bba5645feed0766b4a5b6b83a5c78b0dcbeb369a508aa80d5fb5356(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c59078c9e1e9dc93ac9b0c613a58659eb86f2e940b7e64b1ef31ac0e2c92a50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b160b4af6ef76f15ade1084cdaf1456878f90ef51b7537aefcd5b543572edcd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a80c811048c32135a8cbf92b4ecd7f881815fe5c77bfb8374fd7ee5c07cb350(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    common_name: builtins.str,
    type: builtins.str,
    add_basic_constraints: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    alt_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    country: typing.Optional[builtins.str] = None,
    exclude_cn_from_sans: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    ip_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    key_bits: typing.Optional[jsii.Number] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_ref: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    key_usage: typing.Optional[typing.Sequence[builtins.str]] = None,
    locality: typing.Optional[builtins.str] = None,
    managed_key_id: typing.Optional[builtins.str] = None,
    managed_key_name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    other_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    ou: typing.Optional[builtins.str] = None,
    postal_code: typing.Optional[builtins.str] = None,
    private_key_format: typing.Optional[builtins.str] = None,
    province: typing.Optional[builtins.str] = None,
    serial_number: typing.Optional[builtins.str] = None,
    signature_bits: typing.Optional[jsii.Number] = None,
    street_address: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
