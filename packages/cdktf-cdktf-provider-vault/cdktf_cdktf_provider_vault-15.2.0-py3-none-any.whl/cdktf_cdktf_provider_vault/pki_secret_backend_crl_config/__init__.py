r'''
# `vault_pki_secret_backend_crl_config`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_crl_config`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config).
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


class PkiSecretBackendCrlConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendCrlConfig.PkiSecretBackendCrlConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config vault_pki_secret_backend_crl_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        auto_rebuild: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_rebuild_grace_period: typing.Optional[builtins.str] = None,
        cross_cluster_revocation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        delta_rebuild_interval: typing.Optional[builtins.str] = None,
        disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_delta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiry: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_crl_entries: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        ocsp_disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_expiry: typing.Optional[builtins.str] = None,
        unified_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unified_crl_on_existing_paths: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config vault_pki_secret_backend_crl_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The path of the PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#backend PkiSecretBackendCrlConfig#backend}
        :param auto_rebuild: Enables or disables periodic rebuilding of the CRL upon expiry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#auto_rebuild PkiSecretBackendCrlConfig#auto_rebuild}
        :param auto_rebuild_grace_period: Grace period before CRL expiry to attempt rebuild of CRL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#auto_rebuild_grace_period PkiSecretBackendCrlConfig#auto_rebuild_grace_period}
        :param cross_cluster_revocation: Enable cross-cluster revocation request queues. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#cross_cluster_revocation PkiSecretBackendCrlConfig#cross_cluster_revocation}
        :param delta_rebuild_interval: Interval to check for new revocations on, to regenerate the delta CRL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#delta_rebuild_interval PkiSecretBackendCrlConfig#delta_rebuild_interval}
        :param disable: Disables or enables CRL building. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#disable PkiSecretBackendCrlConfig#disable}
        :param enable_delta: Enables or disables building of delta CRLs with up-to-date revocation information, augmenting the last complete CRL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#enable_delta PkiSecretBackendCrlConfig#enable_delta}
        :param expiry: Specifies the time until expiration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#expiry PkiSecretBackendCrlConfig#expiry}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#id PkiSecretBackendCrlConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_crl_entries: The maximum number of entries a CRL can contain. This option exists to prevent accidental runaway issuance/revocation from overloading Vault. If set to -1, the limit is disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#max_crl_entries PkiSecretBackendCrlConfig#max_crl_entries}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#namespace PkiSecretBackendCrlConfig#namespace}
        :param ocsp_disable: Disables or enables the OCSP responder in Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#ocsp_disable PkiSecretBackendCrlConfig#ocsp_disable}
        :param ocsp_expiry: The amount of time an OCSP response can be cached for, useful for OCSP stapling refresh durations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#ocsp_expiry PkiSecretBackendCrlConfig#ocsp_expiry}
        :param unified_crl: Enables unified CRL and OCSP building. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#unified_crl PkiSecretBackendCrlConfig#unified_crl}
        :param unified_crl_on_existing_paths: Enables serving the unified CRL and OCSP on the existing, previously cluster-local paths. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#unified_crl_on_existing_paths PkiSecretBackendCrlConfig#unified_crl_on_existing_paths}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ea65a20e6b443fc69f679bf537e86e551241d2fa218785f49ec72a5c1e2cec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendCrlConfigConfig(
            backend=backend,
            auto_rebuild=auto_rebuild,
            auto_rebuild_grace_period=auto_rebuild_grace_period,
            cross_cluster_revocation=cross_cluster_revocation,
            delta_rebuild_interval=delta_rebuild_interval,
            disable=disable,
            enable_delta=enable_delta,
            expiry=expiry,
            id=id,
            max_crl_entries=max_crl_entries,
            namespace=namespace,
            ocsp_disable=ocsp_disable,
            ocsp_expiry=ocsp_expiry,
            unified_crl=unified_crl,
            unified_crl_on_existing_paths=unified_crl_on_existing_paths,
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
        '''Generates CDKTF code for importing a PkiSecretBackendCrlConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendCrlConfig to import.
        :param import_from_id: The id of the existing PkiSecretBackendCrlConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendCrlConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3dc15a4f54152fdfd263db80a02fea3f49d8e30597c6afb314433a790de077a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAutoRebuild")
    def reset_auto_rebuild(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRebuild", []))

    @jsii.member(jsii_name="resetAutoRebuildGracePeriod")
    def reset_auto_rebuild_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRebuildGracePeriod", []))

    @jsii.member(jsii_name="resetCrossClusterRevocation")
    def reset_cross_cluster_revocation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrossClusterRevocation", []))

    @jsii.member(jsii_name="resetDeltaRebuildInterval")
    def reset_delta_rebuild_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeltaRebuildInterval", []))

    @jsii.member(jsii_name="resetDisable")
    def reset_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisable", []))

    @jsii.member(jsii_name="resetEnableDelta")
    def reset_enable_delta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableDelta", []))

    @jsii.member(jsii_name="resetExpiry")
    def reset_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpiry", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxCrlEntries")
    def reset_max_crl_entries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCrlEntries", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOcspDisable")
    def reset_ocsp_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspDisable", []))

    @jsii.member(jsii_name="resetOcspExpiry")
    def reset_ocsp_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOcspExpiry", []))

    @jsii.member(jsii_name="resetUnifiedCrl")
    def reset_unified_crl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnifiedCrl", []))

    @jsii.member(jsii_name="resetUnifiedCrlOnExistingPaths")
    def reset_unified_crl_on_existing_paths(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnifiedCrlOnExistingPaths", []))

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
    @jsii.member(jsii_name="autoRebuildGracePeriodInput")
    def auto_rebuild_grace_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoRebuildGracePeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRebuildInput")
    def auto_rebuild_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoRebuildInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="crossClusterRevocationInput")
    def cross_cluster_revocation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "crossClusterRevocationInput"))

    @builtins.property
    @jsii.member(jsii_name="deltaRebuildIntervalInput")
    def delta_rebuild_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deltaRebuildIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="disableInput")
    def disable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableInput"))

    @builtins.property
    @jsii.member(jsii_name="enableDeltaInput")
    def enable_delta_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableDeltaInput"))

    @builtins.property
    @jsii.member(jsii_name="expiryInput")
    def expiry_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expiryInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCrlEntriesInput")
    def max_crl_entries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxCrlEntriesInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspDisableInput")
    def ocsp_disable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ocspDisableInput"))

    @builtins.property
    @jsii.member(jsii_name="ocspExpiryInput")
    def ocsp_expiry_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ocspExpiryInput"))

    @builtins.property
    @jsii.member(jsii_name="unifiedCrlInput")
    def unified_crl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unifiedCrlInput"))

    @builtins.property
    @jsii.member(jsii_name="unifiedCrlOnExistingPathsInput")
    def unified_crl_on_existing_paths_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unifiedCrlOnExistingPathsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRebuild")
    def auto_rebuild(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoRebuild"))

    @auto_rebuild.setter
    def auto_rebuild(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3953bf3934058e4cf6bd06b28f8a3fabd40242943b853835062a49ee7337d0d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRebuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoRebuildGracePeriod")
    def auto_rebuild_grace_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRebuildGracePeriod"))

    @auto_rebuild_grace_period.setter
    def auto_rebuild_grace_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b6c1763a91376557b267fbf24af8c7ad40a222ee356ec4de979166ffb500c26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRebuildGracePeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5da4b3f145c6c3b9c1dcb2df6cb876b40f116bfaa45eafe1cfb21d272eb3144)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crossClusterRevocation")
    def cross_cluster_revocation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "crossClusterRevocation"))

    @cross_cluster_revocation.setter
    def cross_cluster_revocation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75eb28663fac2c86c4a5e518555b3bb04ec35a11bef613d23e79c79b21f69887)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crossClusterRevocation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deltaRebuildInterval")
    def delta_rebuild_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deltaRebuildInterval"))

    @delta_rebuild_interval.setter
    def delta_rebuild_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f6fe45944c2fe086a1e771dd664d02c3f3e874717e4736d35111680d0fc42e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deltaRebuildInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disable")
    def disable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disable"))

    @disable.setter
    def disable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ecc20e60597559b7f4f7e88a13445de5c53700e038dfdf5b28a76d6b28d98f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableDelta")
    def enable_delta(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableDelta"))

    @enable_delta.setter
    def enable_delta(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98491dbdf9f6b33c6c823469d7ac7d4f1c2a742118522066ca6deb053abf84cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableDelta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expiry")
    def expiry(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiry"))

    @expiry.setter
    def expiry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6d8f233ae644167746cc43092c4ce2fa57ac53067e3901f1d3cf748e76158b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expiry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f62c51973d63248348fb4200b0368e83c6cc9f5d9f9628f2a772aa3e0244c5b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCrlEntries")
    def max_crl_entries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxCrlEntries"))

    @max_crl_entries.setter
    def max_crl_entries(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de247b92019dcda590c56c2da801c0608ecad0905d52df84015bbe39c7b50b52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCrlEntries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3891047ebec1cad4ed73335eee5f4325bdf83692c1a7ec02cea244dbb9938942)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspDisable")
    def ocsp_disable(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ocspDisable"))

    @ocsp_disable.setter
    def ocsp_disable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f67b82706f4bb79e47972db238b8036b91cc1ab6fc38b108b1feb1011708d7ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspDisable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ocspExpiry")
    def ocsp_expiry(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ocspExpiry"))

    @ocsp_expiry.setter
    def ocsp_expiry(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20aeaf5171e80fc2d2e6a6840a3ab03edfe828689089da3bbe0a16554d26bb2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ocspExpiry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unifiedCrl")
    def unified_crl(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unifiedCrl"))

    @unified_crl.setter
    def unified_crl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c1a1be9e8f7b5603af293d86fe4201d7eeed006d88a871b392f33d787b7b36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unifiedCrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unifiedCrlOnExistingPaths")
    def unified_crl_on_existing_paths(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unifiedCrlOnExistingPaths"))

    @unified_crl_on_existing_paths.setter
    def unified_crl_on_existing_paths(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22f7fd48f8d8e67ca6b727f8e7b6884d92b5b9fce1f4575f8a37ba33c7a66ef7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unifiedCrlOnExistingPaths", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendCrlConfig.PkiSecretBackendCrlConfigConfig",
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
        "auto_rebuild": "autoRebuild",
        "auto_rebuild_grace_period": "autoRebuildGracePeriod",
        "cross_cluster_revocation": "crossClusterRevocation",
        "delta_rebuild_interval": "deltaRebuildInterval",
        "disable": "disable",
        "enable_delta": "enableDelta",
        "expiry": "expiry",
        "id": "id",
        "max_crl_entries": "maxCrlEntries",
        "namespace": "namespace",
        "ocsp_disable": "ocspDisable",
        "ocsp_expiry": "ocspExpiry",
        "unified_crl": "unifiedCrl",
        "unified_crl_on_existing_paths": "unifiedCrlOnExistingPaths",
    },
)
class PkiSecretBackendCrlConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        auto_rebuild: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_rebuild_grace_period: typing.Optional[builtins.str] = None,
        cross_cluster_revocation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        delta_rebuild_interval: typing.Optional[builtins.str] = None,
        disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_delta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiry: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        max_crl_entries: typing.Optional[jsii.Number] = None,
        namespace: typing.Optional[builtins.str] = None,
        ocsp_disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ocsp_expiry: typing.Optional[builtins.str] = None,
        unified_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        unified_crl_on_existing_paths: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The path of the PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#backend PkiSecretBackendCrlConfig#backend}
        :param auto_rebuild: Enables or disables periodic rebuilding of the CRL upon expiry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#auto_rebuild PkiSecretBackendCrlConfig#auto_rebuild}
        :param auto_rebuild_grace_period: Grace period before CRL expiry to attempt rebuild of CRL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#auto_rebuild_grace_period PkiSecretBackendCrlConfig#auto_rebuild_grace_period}
        :param cross_cluster_revocation: Enable cross-cluster revocation request queues. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#cross_cluster_revocation PkiSecretBackendCrlConfig#cross_cluster_revocation}
        :param delta_rebuild_interval: Interval to check for new revocations on, to regenerate the delta CRL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#delta_rebuild_interval PkiSecretBackendCrlConfig#delta_rebuild_interval}
        :param disable: Disables or enables CRL building. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#disable PkiSecretBackendCrlConfig#disable}
        :param enable_delta: Enables or disables building of delta CRLs with up-to-date revocation information, augmenting the last complete CRL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#enable_delta PkiSecretBackendCrlConfig#enable_delta}
        :param expiry: Specifies the time until expiration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#expiry PkiSecretBackendCrlConfig#expiry}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#id PkiSecretBackendCrlConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_crl_entries: The maximum number of entries a CRL can contain. This option exists to prevent accidental runaway issuance/revocation from overloading Vault. If set to -1, the limit is disabled. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#max_crl_entries PkiSecretBackendCrlConfig#max_crl_entries}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#namespace PkiSecretBackendCrlConfig#namespace}
        :param ocsp_disable: Disables or enables the OCSP responder in Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#ocsp_disable PkiSecretBackendCrlConfig#ocsp_disable}
        :param ocsp_expiry: The amount of time an OCSP response can be cached for, useful for OCSP stapling refresh durations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#ocsp_expiry PkiSecretBackendCrlConfig#ocsp_expiry}
        :param unified_crl: Enables unified CRL and OCSP building. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#unified_crl PkiSecretBackendCrlConfig#unified_crl}
        :param unified_crl_on_existing_paths: Enables serving the unified CRL and OCSP on the existing, previously cluster-local paths. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#unified_crl_on_existing_paths PkiSecretBackendCrlConfig#unified_crl_on_existing_paths}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__461bdae0739980bea0caae519159cf42f77284799676ad837232ce787bc52b90)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument auto_rebuild", value=auto_rebuild, expected_type=type_hints["auto_rebuild"])
            check_type(argname="argument auto_rebuild_grace_period", value=auto_rebuild_grace_period, expected_type=type_hints["auto_rebuild_grace_period"])
            check_type(argname="argument cross_cluster_revocation", value=cross_cluster_revocation, expected_type=type_hints["cross_cluster_revocation"])
            check_type(argname="argument delta_rebuild_interval", value=delta_rebuild_interval, expected_type=type_hints["delta_rebuild_interval"])
            check_type(argname="argument disable", value=disable, expected_type=type_hints["disable"])
            check_type(argname="argument enable_delta", value=enable_delta, expected_type=type_hints["enable_delta"])
            check_type(argname="argument expiry", value=expiry, expected_type=type_hints["expiry"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_crl_entries", value=max_crl_entries, expected_type=type_hints["max_crl_entries"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument ocsp_disable", value=ocsp_disable, expected_type=type_hints["ocsp_disable"])
            check_type(argname="argument ocsp_expiry", value=ocsp_expiry, expected_type=type_hints["ocsp_expiry"])
            check_type(argname="argument unified_crl", value=unified_crl, expected_type=type_hints["unified_crl"])
            check_type(argname="argument unified_crl_on_existing_paths", value=unified_crl_on_existing_paths, expected_type=type_hints["unified_crl_on_existing_paths"])
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
        if auto_rebuild is not None:
            self._values["auto_rebuild"] = auto_rebuild
        if auto_rebuild_grace_period is not None:
            self._values["auto_rebuild_grace_period"] = auto_rebuild_grace_period
        if cross_cluster_revocation is not None:
            self._values["cross_cluster_revocation"] = cross_cluster_revocation
        if delta_rebuild_interval is not None:
            self._values["delta_rebuild_interval"] = delta_rebuild_interval
        if disable is not None:
            self._values["disable"] = disable
        if enable_delta is not None:
            self._values["enable_delta"] = enable_delta
        if expiry is not None:
            self._values["expiry"] = expiry
        if id is not None:
            self._values["id"] = id
        if max_crl_entries is not None:
            self._values["max_crl_entries"] = max_crl_entries
        if namespace is not None:
            self._values["namespace"] = namespace
        if ocsp_disable is not None:
            self._values["ocsp_disable"] = ocsp_disable
        if ocsp_expiry is not None:
            self._values["ocsp_expiry"] = ocsp_expiry
        if unified_crl is not None:
            self._values["unified_crl"] = unified_crl
        if unified_crl_on_existing_paths is not None:
            self._values["unified_crl_on_existing_paths"] = unified_crl_on_existing_paths

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
        '''The path of the PKI secret backend the resource belongs to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#backend PkiSecretBackendCrlConfig#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_rebuild(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables or disables periodic rebuilding of the CRL upon expiry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#auto_rebuild PkiSecretBackendCrlConfig#auto_rebuild}
        '''
        result = self._values.get("auto_rebuild")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_rebuild_grace_period(self) -> typing.Optional[builtins.str]:
        '''Grace period before CRL expiry to attempt rebuild of CRL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#auto_rebuild_grace_period PkiSecretBackendCrlConfig#auto_rebuild_grace_period}
        '''
        result = self._values.get("auto_rebuild_grace_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cross_cluster_revocation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable cross-cluster revocation request queues.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#cross_cluster_revocation PkiSecretBackendCrlConfig#cross_cluster_revocation}
        '''
        result = self._values.get("cross_cluster_revocation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def delta_rebuild_interval(self) -> typing.Optional[builtins.str]:
        '''Interval to check for new revocations on, to regenerate the delta CRL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#delta_rebuild_interval PkiSecretBackendCrlConfig#delta_rebuild_interval}
        '''
        result = self._values.get("delta_rebuild_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables or enables CRL building.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#disable PkiSecretBackendCrlConfig#disable}
        '''
        result = self._values.get("disable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_delta(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables or disables building of delta CRLs with up-to-date revocation information, augmenting the last complete CRL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#enable_delta PkiSecretBackendCrlConfig#enable_delta}
        '''
        result = self._values.get("enable_delta")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def expiry(self) -> typing.Optional[builtins.str]:
        '''Specifies the time until expiration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#expiry PkiSecretBackendCrlConfig#expiry}
        '''
        result = self._values.get("expiry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#id PkiSecretBackendCrlConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_crl_entries(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of entries a CRL can contain.

        This option exists to prevent accidental runaway issuance/revocation from overloading Vault. If set to -1, the limit is disabled.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#max_crl_entries PkiSecretBackendCrlConfig#max_crl_entries}
        '''
        result = self._values.get("max_crl_entries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#namespace PkiSecretBackendCrlConfig#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ocsp_disable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disables or enables the OCSP responder in Vault.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#ocsp_disable PkiSecretBackendCrlConfig#ocsp_disable}
        '''
        result = self._values.get("ocsp_disable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ocsp_expiry(self) -> typing.Optional[builtins.str]:
        '''The amount of time an OCSP response can be cached for, useful for OCSP stapling refresh durations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#ocsp_expiry PkiSecretBackendCrlConfig#ocsp_expiry}
        '''
        result = self._values.get("ocsp_expiry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unified_crl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables unified CRL and OCSP building.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#unified_crl PkiSecretBackendCrlConfig#unified_crl}
        '''
        result = self._values.get("unified_crl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def unified_crl_on_existing_paths(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enables serving the unified CRL and OCSP on the existing, previously cluster-local paths.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_crl_config#unified_crl_on_existing_paths PkiSecretBackendCrlConfig#unified_crl_on_existing_paths}
        '''
        result = self._values.get("unified_crl_on_existing_paths")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendCrlConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendCrlConfig",
    "PkiSecretBackendCrlConfigConfig",
]

publication.publish()

def _typecheckingstub__e6ea65a20e6b443fc69f679bf537e86e551241d2fa218785f49ec72a5c1e2cec(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    auto_rebuild: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_rebuild_grace_period: typing.Optional[builtins.str] = None,
    cross_cluster_revocation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    delta_rebuild_interval: typing.Optional[builtins.str] = None,
    disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_delta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiry: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_crl_entries: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    ocsp_disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_expiry: typing.Optional[builtins.str] = None,
    unified_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unified_crl_on_existing_paths: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__d3dc15a4f54152fdfd263db80a02fea3f49d8e30597c6afb314433a790de077a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3953bf3934058e4cf6bd06b28f8a3fabd40242943b853835062a49ee7337d0d9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6c1763a91376557b267fbf24af8c7ad40a222ee356ec4de979166ffb500c26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5da4b3f145c6c3b9c1dcb2df6cb876b40f116bfaa45eafe1cfb21d272eb3144(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75eb28663fac2c86c4a5e518555b3bb04ec35a11bef613d23e79c79b21f69887(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f6fe45944c2fe086a1e771dd664d02c3f3e874717e4736d35111680d0fc42e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ecc20e60597559b7f4f7e88a13445de5c53700e038dfdf5b28a76d6b28d98f3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98491dbdf9f6b33c6c823469d7ac7d4f1c2a742118522066ca6deb053abf84cc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef6d8f233ae644167746cc43092c4ce2fa57ac53067e3901f1d3cf748e76158b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f62c51973d63248348fb4200b0368e83c6cc9f5d9f9628f2a772aa3e0244c5b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de247b92019dcda590c56c2da801c0608ecad0905d52df84015bbe39c7b50b52(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3891047ebec1cad4ed73335eee5f4325bdf83692c1a7ec02cea244dbb9938942(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f67b82706f4bb79e47972db238b8036b91cc1ab6fc38b108b1feb1011708d7ad(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20aeaf5171e80fc2d2e6a6840a3ab03edfe828689089da3bbe0a16554d26bb2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c1a1be9e8f7b5603af293d86fe4201d7eeed006d88a871b392f33d787b7b36(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22f7fd48f8d8e67ca6b727f8e7b6884d92b5b9fce1f4575f8a37ba33c7a66ef7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__461bdae0739980bea0caae519159cf42f77284799676ad837232ce787bc52b90(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    auto_rebuild: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_rebuild_grace_period: typing.Optional[builtins.str] = None,
    cross_cluster_revocation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    delta_rebuild_interval: typing.Optional[builtins.str] = None,
    disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_delta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiry: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    max_crl_entries: typing.Optional[jsii.Number] = None,
    namespace: typing.Optional[builtins.str] = None,
    ocsp_disable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ocsp_expiry: typing.Optional[builtins.str] = None,
    unified_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    unified_crl_on_existing_paths: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
