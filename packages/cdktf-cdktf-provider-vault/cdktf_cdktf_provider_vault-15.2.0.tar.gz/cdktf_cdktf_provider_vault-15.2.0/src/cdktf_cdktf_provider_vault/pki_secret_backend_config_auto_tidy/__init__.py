r'''
# `vault_pki_secret_backend_config_auto_tidy`

Refer to the Terraform Registry for docs: [`vault_pki_secret_backend_config_auto_tidy`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy).
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


class PkiSecretBackendConfigAutoTidy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigAutoTidy.PkiSecretBackendConfigAutoTidy",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy vault_pki_secret_backend_config_auto_tidy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        acme_account_safety_buffer: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        interval_duration: typing.Optional[builtins.str] = None,
        issuer_safety_buffer: typing.Optional[builtins.str] = None,
        maintain_stored_certificate_counts: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_startup_backoff_duration: typing.Optional[builtins.str] = None,
        min_startup_backoff_duration: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        pause_duration: typing.Optional[builtins.str] = None,
        publish_stored_certificate_count_metrics: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        revocation_queue_safety_buffer: typing.Optional[builtins.str] = None,
        safety_buffer: typing.Optional[builtins.str] = None,
        tidy_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cert_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cert_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cmpv2_nonce_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cross_cluster_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_expired_issuers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_move_legacy_ca_bundle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_revocation_queue: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_revoked_cert_issuer_associations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy vault_pki_secret_backend_config_auto_tidy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The path of the PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#backend PkiSecretBackendConfigAutoTidy#backend}
        :param enabled: Specifies whether automatic tidy is enabled or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#enabled PkiSecretBackendConfigAutoTidy#enabled}
        :param acme_account_safety_buffer: The amount of time that must pass after creation that an account with no orders is marked revoked, and the amount of time after being marked revoked or deactivated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#acme_account_safety_buffer PkiSecretBackendConfigAutoTidy#acme_account_safety_buffer}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#id PkiSecretBackendConfigAutoTidy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param interval_duration: Interval at which to run an auto-tidy operation. This is the time between tidy invocations (after one finishes to the start of the next). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#interval_duration PkiSecretBackendConfigAutoTidy#interval_duration}
        :param issuer_safety_buffer: The amount of extra time that must have passed beyond issuer's expiration before it is removed from the backend storage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#issuer_safety_buffer PkiSecretBackendConfigAutoTidy#issuer_safety_buffer}
        :param maintain_stored_certificate_counts: This configures whether stored certificate are counted upon initialization of the backend, and whether during normal operation, a running count of certificates stored is maintained. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#maintain_stored_certificate_counts PkiSecretBackendConfigAutoTidy#maintain_stored_certificate_counts}
        :param max_startup_backoff_duration: The maximum amount of time auto-tidy will be delayed after startup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#max_startup_backoff_duration PkiSecretBackendConfigAutoTidy#max_startup_backoff_duration}
        :param min_startup_backoff_duration: The minimum amount of time auto-tidy will be delayed after startup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#min_startup_backoff_duration PkiSecretBackendConfigAutoTidy#min_startup_backoff_duration}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#namespace PkiSecretBackendConfigAutoTidy#namespace}
        :param pause_duration: The amount of time to wait between processing certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#pause_duration PkiSecretBackendConfigAutoTidy#pause_duration}
        :param publish_stored_certificate_count_metrics: This configures whether the stored certificate count is published to the metrics consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#publish_stored_certificate_count_metrics PkiSecretBackendConfigAutoTidy#publish_stored_certificate_count_metrics}
        :param revocation_queue_safety_buffer: The amount of time that must pass from the cross-cluster revocation request being initiated to when it will be slated for removal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#revocation_queue_safety_buffer PkiSecretBackendConfigAutoTidy#revocation_queue_safety_buffer}
        :param safety_buffer: The amount of extra time that must have passed beyond certificate expiration before it is removed from the backend storage and/or revocation list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#safety_buffer PkiSecretBackendConfigAutoTidy#safety_buffer}
        :param tidy_acme: Set to true to enable tidying ACME accounts, orders and authorizations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_acme PkiSecretBackendConfigAutoTidy#tidy_acme}
        :param tidy_cert_metadata: Set to true to enable tidying up certificate metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cert_metadata PkiSecretBackendConfigAutoTidy#tidy_cert_metadata}
        :param tidy_cert_store: Set to true to enable tidying up the certificate store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cert_store PkiSecretBackendConfigAutoTidy#tidy_cert_store}
        :param tidy_cmpv2_nonce_store: Set to true to enable tidying up the CMPv2 nonce store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cmpv2_nonce_store PkiSecretBackendConfigAutoTidy#tidy_cmpv2_nonce_store}
        :param tidy_cross_cluster_revoked_certs: Set to true to enable tidying up the cross-cluster revoked certificate store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cross_cluster_revoked_certs PkiSecretBackendConfigAutoTidy#tidy_cross_cluster_revoked_certs}
        :param tidy_expired_issuers: Set to true to automatically remove expired issuers past the issuer_safety_buffer. No keys will be removed as part of this operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_expired_issuers PkiSecretBackendConfigAutoTidy#tidy_expired_issuers}
        :param tidy_move_legacy_ca_bundle: Set to true to move the legacy ca_bundle from /config/ca_bundle to /config/ca_bundle.bak. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_move_legacy_ca_bundle PkiSecretBackendConfigAutoTidy#tidy_move_legacy_ca_bundle}
        :param tidy_revocation_queue: Set to true to remove stale revocation queue entries that haven't been confirmed by any active cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revocation_queue PkiSecretBackendConfigAutoTidy#tidy_revocation_queue}
        :param tidy_revoked_cert_issuer_associations: Set to true to validate issuer associations on revocation entries. This helps increase the performance of CRL building and OCSP responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revoked_cert_issuer_associations PkiSecretBackendConfigAutoTidy#tidy_revoked_cert_issuer_associations}
        :param tidy_revoked_certs: Set to true to remove all invalid and expired certificates from storage. A revoked storage entry is considered invalid if the entry is empty, or the value within the entry is empty. If a certificate is removed due to expiry, the entry will also be removed from the CRL, and the CRL will be rotated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revoked_certs PkiSecretBackendConfigAutoTidy#tidy_revoked_certs}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f95d58e6a70315c72586049567eab917dc8c203f0a9dadd28c6a40a5d5d782a8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiSecretBackendConfigAutoTidyConfig(
            backend=backend,
            enabled=enabled,
            acme_account_safety_buffer=acme_account_safety_buffer,
            id=id,
            interval_duration=interval_duration,
            issuer_safety_buffer=issuer_safety_buffer,
            maintain_stored_certificate_counts=maintain_stored_certificate_counts,
            max_startup_backoff_duration=max_startup_backoff_duration,
            min_startup_backoff_duration=min_startup_backoff_duration,
            namespace=namespace,
            pause_duration=pause_duration,
            publish_stored_certificate_count_metrics=publish_stored_certificate_count_metrics,
            revocation_queue_safety_buffer=revocation_queue_safety_buffer,
            safety_buffer=safety_buffer,
            tidy_acme=tidy_acme,
            tidy_cert_metadata=tidy_cert_metadata,
            tidy_cert_store=tidy_cert_store,
            tidy_cmpv2_nonce_store=tidy_cmpv2_nonce_store,
            tidy_cross_cluster_revoked_certs=tidy_cross_cluster_revoked_certs,
            tidy_expired_issuers=tidy_expired_issuers,
            tidy_move_legacy_ca_bundle=tidy_move_legacy_ca_bundle,
            tidy_revocation_queue=tidy_revocation_queue,
            tidy_revoked_cert_issuer_associations=tidy_revoked_cert_issuer_associations,
            tidy_revoked_certs=tidy_revoked_certs,
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
        '''Generates CDKTF code for importing a PkiSecretBackendConfigAutoTidy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiSecretBackendConfigAutoTidy to import.
        :param import_from_id: The id of the existing PkiSecretBackendConfigAutoTidy that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiSecretBackendConfigAutoTidy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d89a254450b0ad1776864c69ba6957cc25c4052e731fa94cd7bd84f724c4dfa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAcmeAccountSafetyBuffer")
    def reset_acme_account_safety_buffer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcmeAccountSafetyBuffer", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIntervalDuration")
    def reset_interval_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalDuration", []))

    @jsii.member(jsii_name="resetIssuerSafetyBuffer")
    def reset_issuer_safety_buffer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuerSafetyBuffer", []))

    @jsii.member(jsii_name="resetMaintainStoredCertificateCounts")
    def reset_maintain_stored_certificate_counts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintainStoredCertificateCounts", []))

    @jsii.member(jsii_name="resetMaxStartupBackoffDuration")
    def reset_max_startup_backoff_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStartupBackoffDuration", []))

    @jsii.member(jsii_name="resetMinStartupBackoffDuration")
    def reset_min_startup_backoff_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinStartupBackoffDuration", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetPauseDuration")
    def reset_pause_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPauseDuration", []))

    @jsii.member(jsii_name="resetPublishStoredCertificateCountMetrics")
    def reset_publish_stored_certificate_count_metrics(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublishStoredCertificateCountMetrics", []))

    @jsii.member(jsii_name="resetRevocationQueueSafetyBuffer")
    def reset_revocation_queue_safety_buffer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevocationQueueSafetyBuffer", []))

    @jsii.member(jsii_name="resetSafetyBuffer")
    def reset_safety_buffer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSafetyBuffer", []))

    @jsii.member(jsii_name="resetTidyAcme")
    def reset_tidy_acme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyAcme", []))

    @jsii.member(jsii_name="resetTidyCertMetadata")
    def reset_tidy_cert_metadata(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyCertMetadata", []))

    @jsii.member(jsii_name="resetTidyCertStore")
    def reset_tidy_cert_store(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyCertStore", []))

    @jsii.member(jsii_name="resetTidyCmpv2NonceStore")
    def reset_tidy_cmpv2_nonce_store(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyCmpv2NonceStore", []))

    @jsii.member(jsii_name="resetTidyCrossClusterRevokedCerts")
    def reset_tidy_cross_cluster_revoked_certs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyCrossClusterRevokedCerts", []))

    @jsii.member(jsii_name="resetTidyExpiredIssuers")
    def reset_tidy_expired_issuers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyExpiredIssuers", []))

    @jsii.member(jsii_name="resetTidyMoveLegacyCaBundle")
    def reset_tidy_move_legacy_ca_bundle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyMoveLegacyCaBundle", []))

    @jsii.member(jsii_name="resetTidyRevocationQueue")
    def reset_tidy_revocation_queue(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyRevocationQueue", []))

    @jsii.member(jsii_name="resetTidyRevokedCertIssuerAssociations")
    def reset_tidy_revoked_cert_issuer_associations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyRevokedCertIssuerAssociations", []))

    @jsii.member(jsii_name="resetTidyRevokedCerts")
    def reset_tidy_revoked_certs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTidyRevokedCerts", []))

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
    @jsii.member(jsii_name="acmeAccountSafetyBufferInput")
    def acme_account_safety_buffer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acmeAccountSafetyBufferInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalDurationInput")
    def interval_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerSafetyBufferInput")
    def issuer_safety_buffer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerSafetyBufferInput"))

    @builtins.property
    @jsii.member(jsii_name="maintainStoredCertificateCountsInput")
    def maintain_stored_certificate_counts_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "maintainStoredCertificateCountsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStartupBackoffDurationInput")
    def max_startup_backoff_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxStartupBackoffDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="minStartupBackoffDurationInput")
    def min_startup_backoff_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minStartupBackoffDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="pauseDurationInput")
    def pause_duration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pauseDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="publishStoredCertificateCountMetricsInput")
    def publish_stored_certificate_count_metrics_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "publishStoredCertificateCountMetricsInput"))

    @builtins.property
    @jsii.member(jsii_name="revocationQueueSafetyBufferInput")
    def revocation_queue_safety_buffer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "revocationQueueSafetyBufferInput"))

    @builtins.property
    @jsii.member(jsii_name="safetyBufferInput")
    def safety_buffer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "safetyBufferInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyAcmeInput")
    def tidy_acme_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyAcmeInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyCertMetadataInput")
    def tidy_cert_metadata_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyCertMetadataInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyCertStoreInput")
    def tidy_cert_store_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyCertStoreInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyCmpv2NonceStoreInput")
    def tidy_cmpv2_nonce_store_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyCmpv2NonceStoreInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyCrossClusterRevokedCertsInput")
    def tidy_cross_cluster_revoked_certs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyCrossClusterRevokedCertsInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyExpiredIssuersInput")
    def tidy_expired_issuers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyExpiredIssuersInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyMoveLegacyCaBundleInput")
    def tidy_move_legacy_ca_bundle_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyMoveLegacyCaBundleInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyRevocationQueueInput")
    def tidy_revocation_queue_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyRevocationQueueInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyRevokedCertIssuerAssociationsInput")
    def tidy_revoked_cert_issuer_associations_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyRevokedCertIssuerAssociationsInput"))

    @builtins.property
    @jsii.member(jsii_name="tidyRevokedCertsInput")
    def tidy_revoked_certs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tidyRevokedCertsInput"))

    @builtins.property
    @jsii.member(jsii_name="acmeAccountSafetyBuffer")
    def acme_account_safety_buffer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acmeAccountSafetyBuffer"))

    @acme_account_safety_buffer.setter
    def acme_account_safety_buffer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4411bf9fb22a02f1cda51cb780bbdca4219b97a0559d03b04b97f786edb128e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acmeAccountSafetyBuffer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0269329b08d355ed078b26ec621ba067c41a5e605da6ef60bcf566836dc2aa18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__6c30db7b677fb70adab89b87e11e95aaeaaf4aaeb2f7af195cd47ac2f084e6d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad111d684b6d94efc58264bc7bb2ac2c6aa48253b995d8d33e4a5244935aee2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalDuration")
    def interval_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "intervalDuration"))

    @interval_duration.setter
    def interval_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__919969d8421dc91f4e837f56e8ccc5e7f1aff77ad9e1756ce61205358e647cd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerSafetyBuffer")
    def issuer_safety_buffer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerSafetyBuffer"))

    @issuer_safety_buffer.setter
    def issuer_safety_buffer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afa04c7f4939d0059430deb5604d24b917548c73bd4c94bb6b6d41c2a7360a7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerSafetyBuffer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maintainStoredCertificateCounts")
    def maintain_stored_certificate_counts(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "maintainStoredCertificateCounts"))

    @maintain_stored_certificate_counts.setter
    def maintain_stored_certificate_counts(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__666f8e2be040b84a44f23a8dc6284039c6aa96f3697d0a7088939aa2ea463e7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maintainStoredCertificateCounts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStartupBackoffDuration")
    def max_startup_backoff_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxStartupBackoffDuration"))

    @max_startup_backoff_duration.setter
    def max_startup_backoff_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e58b32ca033d3ba36bd6d85ff7790343aed2e9d4eb3963962896773a5bd3041)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStartupBackoffDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minStartupBackoffDuration")
    def min_startup_backoff_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minStartupBackoffDuration"))

    @min_startup_backoff_duration.setter
    def min_startup_backoff_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6caf7d4c4116a3de50485ca059f165b4daf85d67527cf1c7197a8386090d7e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minStartupBackoffDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d04930401e7aa730d56665c1e187a62ae54a4652056b40bd2a15f9b9e78cf1fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pauseDuration")
    def pause_duration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pauseDuration"))

    @pause_duration.setter
    def pause_duration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39ae9f6e41a8ee40366e725c575af1099abb08d3be4e1c58ab06a71e9c684d1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pauseDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publishStoredCertificateCountMetrics")
    def publish_stored_certificate_count_metrics(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "publishStoredCertificateCountMetrics"))

    @publish_stored_certificate_count_metrics.setter
    def publish_stored_certificate_count_metrics(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ed4b7743004bc2598bcc254d676cfa6a6e35ecb15db74eba7c061d9a2a60c9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publishStoredCertificateCountMetrics", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="revocationQueueSafetyBuffer")
    def revocation_queue_safety_buffer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revocationQueueSafetyBuffer"))

    @revocation_queue_safety_buffer.setter
    def revocation_queue_safety_buffer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d19adaad0deff0c3a754bc137785fde7fc193309e4bf0d514f0a5cd10494b9e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revocationQueueSafetyBuffer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="safetyBuffer")
    def safety_buffer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "safetyBuffer"))

    @safety_buffer.setter
    def safety_buffer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc472b800c3671aec180035b6a6c78f4d9b7def36d5c3e5f4b8d5020a44183c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "safetyBuffer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyAcme")
    def tidy_acme(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyAcme"))

    @tidy_acme.setter
    def tidy_acme(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd0b471ef786db3f7c66753e3c7f8400402c3c58c2494b0321a2890d70966499)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyAcme", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyCertMetadata")
    def tidy_cert_metadata(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyCertMetadata"))

    @tidy_cert_metadata.setter
    def tidy_cert_metadata(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a77013b61f773c0ec4e8c516c15b19297b9e8dcc645835497b25cd1c71c51d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyCertMetadata", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyCertStore")
    def tidy_cert_store(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyCertStore"))

    @tidy_cert_store.setter
    def tidy_cert_store(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c32d273e992fe69d13759c6767805ef44fd2d1de2409a7394754d960ec472c27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyCertStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyCmpv2NonceStore")
    def tidy_cmpv2_nonce_store(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyCmpv2NonceStore"))

    @tidy_cmpv2_nonce_store.setter
    def tidy_cmpv2_nonce_store(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2fa895a79e164526921c4dec56a58fa8d375be6f77f7ce14195786799f2638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyCmpv2NonceStore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyCrossClusterRevokedCerts")
    def tidy_cross_cluster_revoked_certs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyCrossClusterRevokedCerts"))

    @tidy_cross_cluster_revoked_certs.setter
    def tidy_cross_cluster_revoked_certs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1266e91c9eb20ee68975d352d0d5e5b73304f1eab33b1d5423450ef86da7c8df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyCrossClusterRevokedCerts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyExpiredIssuers")
    def tidy_expired_issuers(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyExpiredIssuers"))

    @tidy_expired_issuers.setter
    def tidy_expired_issuers(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18688019a726376d1f5bd2fbfed0a5d9b65196653d599770b393742c18b34d7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyExpiredIssuers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyMoveLegacyCaBundle")
    def tidy_move_legacy_ca_bundle(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyMoveLegacyCaBundle"))

    @tidy_move_legacy_ca_bundle.setter
    def tidy_move_legacy_ca_bundle(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4c27b3abc0b2db24b6b8f9af4d24979e0f3b8c755018c2c3447f3459969f0bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyMoveLegacyCaBundle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyRevocationQueue")
    def tidy_revocation_queue(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyRevocationQueue"))

    @tidy_revocation_queue.setter
    def tidy_revocation_queue(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a00655f8abfe148ecaf46893e2c8cf8d65da422459e25f42bde86741b36e16a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyRevocationQueue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyRevokedCertIssuerAssociations")
    def tidy_revoked_cert_issuer_associations(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyRevokedCertIssuerAssociations"))

    @tidy_revoked_cert_issuer_associations.setter
    def tidy_revoked_cert_issuer_associations(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3c3dca53b85922729bcb3368350a037ec008ea6ace3fb28bf7a0845d7972b16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyRevokedCertIssuerAssociations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tidyRevokedCerts")
    def tidy_revoked_certs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tidyRevokedCerts"))

    @tidy_revoked_certs.setter
    def tidy_revoked_certs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d516604d38656473b80e1fdb8a024496cb14a10bb34aef57dc19d62078725e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tidyRevokedCerts", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.pkiSecretBackendConfigAutoTidy.PkiSecretBackendConfigAutoTidyConfig",
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
        "enabled": "enabled",
        "acme_account_safety_buffer": "acmeAccountSafetyBuffer",
        "id": "id",
        "interval_duration": "intervalDuration",
        "issuer_safety_buffer": "issuerSafetyBuffer",
        "maintain_stored_certificate_counts": "maintainStoredCertificateCounts",
        "max_startup_backoff_duration": "maxStartupBackoffDuration",
        "min_startup_backoff_duration": "minStartupBackoffDuration",
        "namespace": "namespace",
        "pause_duration": "pauseDuration",
        "publish_stored_certificate_count_metrics": "publishStoredCertificateCountMetrics",
        "revocation_queue_safety_buffer": "revocationQueueSafetyBuffer",
        "safety_buffer": "safetyBuffer",
        "tidy_acme": "tidyAcme",
        "tidy_cert_metadata": "tidyCertMetadata",
        "tidy_cert_store": "tidyCertStore",
        "tidy_cmpv2_nonce_store": "tidyCmpv2NonceStore",
        "tidy_cross_cluster_revoked_certs": "tidyCrossClusterRevokedCerts",
        "tidy_expired_issuers": "tidyExpiredIssuers",
        "tidy_move_legacy_ca_bundle": "tidyMoveLegacyCaBundle",
        "tidy_revocation_queue": "tidyRevocationQueue",
        "tidy_revoked_cert_issuer_associations": "tidyRevokedCertIssuerAssociations",
        "tidy_revoked_certs": "tidyRevokedCerts",
    },
)
class PkiSecretBackendConfigAutoTidyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        acme_account_safety_buffer: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        interval_duration: typing.Optional[builtins.str] = None,
        issuer_safety_buffer: typing.Optional[builtins.str] = None,
        maintain_stored_certificate_counts: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_startup_backoff_duration: typing.Optional[builtins.str] = None,
        min_startup_backoff_duration: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        pause_duration: typing.Optional[builtins.str] = None,
        publish_stored_certificate_count_metrics: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        revocation_queue_safety_buffer: typing.Optional[builtins.str] = None,
        safety_buffer: typing.Optional[builtins.str] = None,
        tidy_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cert_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cert_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cmpv2_nonce_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_cross_cluster_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_expired_issuers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_move_legacy_ca_bundle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_revocation_queue: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_revoked_cert_issuer_associations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tidy_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The path of the PKI secret backend the resource belongs to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#backend PkiSecretBackendConfigAutoTidy#backend}
        :param enabled: Specifies whether automatic tidy is enabled or not. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#enabled PkiSecretBackendConfigAutoTidy#enabled}
        :param acme_account_safety_buffer: The amount of time that must pass after creation that an account with no orders is marked revoked, and the amount of time after being marked revoked or deactivated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#acme_account_safety_buffer PkiSecretBackendConfigAutoTidy#acme_account_safety_buffer}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#id PkiSecretBackendConfigAutoTidy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param interval_duration: Interval at which to run an auto-tidy operation. This is the time between tidy invocations (after one finishes to the start of the next). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#interval_duration PkiSecretBackendConfigAutoTidy#interval_duration}
        :param issuer_safety_buffer: The amount of extra time that must have passed beyond issuer's expiration before it is removed from the backend storage. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#issuer_safety_buffer PkiSecretBackendConfigAutoTidy#issuer_safety_buffer}
        :param maintain_stored_certificate_counts: This configures whether stored certificate are counted upon initialization of the backend, and whether during normal operation, a running count of certificates stored is maintained. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#maintain_stored_certificate_counts PkiSecretBackendConfigAutoTidy#maintain_stored_certificate_counts}
        :param max_startup_backoff_duration: The maximum amount of time auto-tidy will be delayed after startup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#max_startup_backoff_duration PkiSecretBackendConfigAutoTidy#max_startup_backoff_duration}
        :param min_startup_backoff_duration: The minimum amount of time auto-tidy will be delayed after startup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#min_startup_backoff_duration PkiSecretBackendConfigAutoTidy#min_startup_backoff_duration}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#namespace PkiSecretBackendConfigAutoTidy#namespace}
        :param pause_duration: The amount of time to wait between processing certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#pause_duration PkiSecretBackendConfigAutoTidy#pause_duration}
        :param publish_stored_certificate_count_metrics: This configures whether the stored certificate count is published to the metrics consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#publish_stored_certificate_count_metrics PkiSecretBackendConfigAutoTidy#publish_stored_certificate_count_metrics}
        :param revocation_queue_safety_buffer: The amount of time that must pass from the cross-cluster revocation request being initiated to when it will be slated for removal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#revocation_queue_safety_buffer PkiSecretBackendConfigAutoTidy#revocation_queue_safety_buffer}
        :param safety_buffer: The amount of extra time that must have passed beyond certificate expiration before it is removed from the backend storage and/or revocation list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#safety_buffer PkiSecretBackendConfigAutoTidy#safety_buffer}
        :param tidy_acme: Set to true to enable tidying ACME accounts, orders and authorizations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_acme PkiSecretBackendConfigAutoTidy#tidy_acme}
        :param tidy_cert_metadata: Set to true to enable tidying up certificate metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cert_metadata PkiSecretBackendConfigAutoTidy#tidy_cert_metadata}
        :param tidy_cert_store: Set to true to enable tidying up the certificate store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cert_store PkiSecretBackendConfigAutoTidy#tidy_cert_store}
        :param tidy_cmpv2_nonce_store: Set to true to enable tidying up the CMPv2 nonce store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cmpv2_nonce_store PkiSecretBackendConfigAutoTidy#tidy_cmpv2_nonce_store}
        :param tidy_cross_cluster_revoked_certs: Set to true to enable tidying up the cross-cluster revoked certificate store. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cross_cluster_revoked_certs PkiSecretBackendConfigAutoTidy#tidy_cross_cluster_revoked_certs}
        :param tidy_expired_issuers: Set to true to automatically remove expired issuers past the issuer_safety_buffer. No keys will be removed as part of this operation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_expired_issuers PkiSecretBackendConfigAutoTidy#tidy_expired_issuers}
        :param tidy_move_legacy_ca_bundle: Set to true to move the legacy ca_bundle from /config/ca_bundle to /config/ca_bundle.bak. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_move_legacy_ca_bundle PkiSecretBackendConfigAutoTidy#tidy_move_legacy_ca_bundle}
        :param tidy_revocation_queue: Set to true to remove stale revocation queue entries that haven't been confirmed by any active cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revocation_queue PkiSecretBackendConfigAutoTidy#tidy_revocation_queue}
        :param tidy_revoked_cert_issuer_associations: Set to true to validate issuer associations on revocation entries. This helps increase the performance of CRL building and OCSP responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revoked_cert_issuer_associations PkiSecretBackendConfigAutoTidy#tidy_revoked_cert_issuer_associations}
        :param tidy_revoked_certs: Set to true to remove all invalid and expired certificates from storage. A revoked storage entry is considered invalid if the entry is empty, or the value within the entry is empty. If a certificate is removed due to expiry, the entry will also be removed from the CRL, and the CRL will be rotated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revoked_certs PkiSecretBackendConfigAutoTidy#tidy_revoked_certs}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e329c31aaddefe1fe3438a82777cf24574626cdac37f163668414d61fea64de3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument acme_account_safety_buffer", value=acme_account_safety_buffer, expected_type=type_hints["acme_account_safety_buffer"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument interval_duration", value=interval_duration, expected_type=type_hints["interval_duration"])
            check_type(argname="argument issuer_safety_buffer", value=issuer_safety_buffer, expected_type=type_hints["issuer_safety_buffer"])
            check_type(argname="argument maintain_stored_certificate_counts", value=maintain_stored_certificate_counts, expected_type=type_hints["maintain_stored_certificate_counts"])
            check_type(argname="argument max_startup_backoff_duration", value=max_startup_backoff_duration, expected_type=type_hints["max_startup_backoff_duration"])
            check_type(argname="argument min_startup_backoff_duration", value=min_startup_backoff_duration, expected_type=type_hints["min_startup_backoff_duration"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument pause_duration", value=pause_duration, expected_type=type_hints["pause_duration"])
            check_type(argname="argument publish_stored_certificate_count_metrics", value=publish_stored_certificate_count_metrics, expected_type=type_hints["publish_stored_certificate_count_metrics"])
            check_type(argname="argument revocation_queue_safety_buffer", value=revocation_queue_safety_buffer, expected_type=type_hints["revocation_queue_safety_buffer"])
            check_type(argname="argument safety_buffer", value=safety_buffer, expected_type=type_hints["safety_buffer"])
            check_type(argname="argument tidy_acme", value=tidy_acme, expected_type=type_hints["tidy_acme"])
            check_type(argname="argument tidy_cert_metadata", value=tidy_cert_metadata, expected_type=type_hints["tidy_cert_metadata"])
            check_type(argname="argument tidy_cert_store", value=tidy_cert_store, expected_type=type_hints["tidy_cert_store"])
            check_type(argname="argument tidy_cmpv2_nonce_store", value=tidy_cmpv2_nonce_store, expected_type=type_hints["tidy_cmpv2_nonce_store"])
            check_type(argname="argument tidy_cross_cluster_revoked_certs", value=tidy_cross_cluster_revoked_certs, expected_type=type_hints["tidy_cross_cluster_revoked_certs"])
            check_type(argname="argument tidy_expired_issuers", value=tidy_expired_issuers, expected_type=type_hints["tidy_expired_issuers"])
            check_type(argname="argument tidy_move_legacy_ca_bundle", value=tidy_move_legacy_ca_bundle, expected_type=type_hints["tidy_move_legacy_ca_bundle"])
            check_type(argname="argument tidy_revocation_queue", value=tidy_revocation_queue, expected_type=type_hints["tidy_revocation_queue"])
            check_type(argname="argument tidy_revoked_cert_issuer_associations", value=tidy_revoked_cert_issuer_associations, expected_type=type_hints["tidy_revoked_cert_issuer_associations"])
            check_type(argname="argument tidy_revoked_certs", value=tidy_revoked_certs, expected_type=type_hints["tidy_revoked_certs"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backend": backend,
            "enabled": enabled,
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
        if acme_account_safety_buffer is not None:
            self._values["acme_account_safety_buffer"] = acme_account_safety_buffer
        if id is not None:
            self._values["id"] = id
        if interval_duration is not None:
            self._values["interval_duration"] = interval_duration
        if issuer_safety_buffer is not None:
            self._values["issuer_safety_buffer"] = issuer_safety_buffer
        if maintain_stored_certificate_counts is not None:
            self._values["maintain_stored_certificate_counts"] = maintain_stored_certificate_counts
        if max_startup_backoff_duration is not None:
            self._values["max_startup_backoff_duration"] = max_startup_backoff_duration
        if min_startup_backoff_duration is not None:
            self._values["min_startup_backoff_duration"] = min_startup_backoff_duration
        if namespace is not None:
            self._values["namespace"] = namespace
        if pause_duration is not None:
            self._values["pause_duration"] = pause_duration
        if publish_stored_certificate_count_metrics is not None:
            self._values["publish_stored_certificate_count_metrics"] = publish_stored_certificate_count_metrics
        if revocation_queue_safety_buffer is not None:
            self._values["revocation_queue_safety_buffer"] = revocation_queue_safety_buffer
        if safety_buffer is not None:
            self._values["safety_buffer"] = safety_buffer
        if tidy_acme is not None:
            self._values["tidy_acme"] = tidy_acme
        if tidy_cert_metadata is not None:
            self._values["tidy_cert_metadata"] = tidy_cert_metadata
        if tidy_cert_store is not None:
            self._values["tidy_cert_store"] = tidy_cert_store
        if tidy_cmpv2_nonce_store is not None:
            self._values["tidy_cmpv2_nonce_store"] = tidy_cmpv2_nonce_store
        if tidy_cross_cluster_revoked_certs is not None:
            self._values["tidy_cross_cluster_revoked_certs"] = tidy_cross_cluster_revoked_certs
        if tidy_expired_issuers is not None:
            self._values["tidy_expired_issuers"] = tidy_expired_issuers
        if tidy_move_legacy_ca_bundle is not None:
            self._values["tidy_move_legacy_ca_bundle"] = tidy_move_legacy_ca_bundle
        if tidy_revocation_queue is not None:
            self._values["tidy_revocation_queue"] = tidy_revocation_queue
        if tidy_revoked_cert_issuer_associations is not None:
            self._values["tidy_revoked_cert_issuer_associations"] = tidy_revoked_cert_issuer_associations
        if tidy_revoked_certs is not None:
            self._values["tidy_revoked_certs"] = tidy_revoked_certs

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#backend PkiSecretBackendConfigAutoTidy#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Specifies whether automatic tidy is enabled or not.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#enabled PkiSecretBackendConfigAutoTidy#enabled}
        '''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def acme_account_safety_buffer(self) -> typing.Optional[builtins.str]:
        '''The amount of time that must pass after creation that an account with no orders is marked revoked, and the amount of time after being marked revoked or deactivated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#acme_account_safety_buffer PkiSecretBackendConfigAutoTidy#acme_account_safety_buffer}
        '''
        result = self._values.get("acme_account_safety_buffer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#id PkiSecretBackendConfigAutoTidy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def interval_duration(self) -> typing.Optional[builtins.str]:
        '''Interval at which to run an auto-tidy operation.

        This is the time between tidy invocations (after one finishes to the start of the next).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#interval_duration PkiSecretBackendConfigAutoTidy#interval_duration}
        '''
        result = self._values.get("interval_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issuer_safety_buffer(self) -> typing.Optional[builtins.str]:
        '''The amount of extra time that must have passed beyond issuer's expiration before it is removed from the backend storage.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#issuer_safety_buffer PkiSecretBackendConfigAutoTidy#issuer_safety_buffer}
        '''
        result = self._values.get("issuer_safety_buffer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintain_stored_certificate_counts(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''This configures whether stored certificate are counted upon initialization of the backend, and whether during normal operation, a running count of certificates stored is maintained.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#maintain_stored_certificate_counts PkiSecretBackendConfigAutoTidy#maintain_stored_certificate_counts}
        '''
        result = self._values.get("maintain_stored_certificate_counts")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_startup_backoff_duration(self) -> typing.Optional[builtins.str]:
        '''The maximum amount of time auto-tidy will be delayed after startup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#max_startup_backoff_duration PkiSecretBackendConfigAutoTidy#max_startup_backoff_duration}
        '''
        result = self._values.get("max_startup_backoff_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_startup_backoff_duration(self) -> typing.Optional[builtins.str]:
        '''The minimum amount of time auto-tidy will be delayed after startup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#min_startup_backoff_duration PkiSecretBackendConfigAutoTidy#min_startup_backoff_duration}
        '''
        result = self._values.get("min_startup_backoff_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#namespace PkiSecretBackendConfigAutoTidy#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pause_duration(self) -> typing.Optional[builtins.str]:
        '''The amount of time to wait between processing certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#pause_duration PkiSecretBackendConfigAutoTidy#pause_duration}
        '''
        result = self._values.get("pause_duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_stored_certificate_count_metrics(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''This configures whether the stored certificate count is published to the metrics consumer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#publish_stored_certificate_count_metrics PkiSecretBackendConfigAutoTidy#publish_stored_certificate_count_metrics}
        '''
        result = self._values.get("publish_stored_certificate_count_metrics")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def revocation_queue_safety_buffer(self) -> typing.Optional[builtins.str]:
        '''The amount of time that must pass from the cross-cluster revocation request being initiated to when it will be slated for removal.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#revocation_queue_safety_buffer PkiSecretBackendConfigAutoTidy#revocation_queue_safety_buffer}
        '''
        result = self._values.get("revocation_queue_safety_buffer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def safety_buffer(self) -> typing.Optional[builtins.str]:
        '''The amount of extra time that must have passed beyond certificate expiration before it is removed from the backend storage and/or revocation list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#safety_buffer PkiSecretBackendConfigAutoTidy#safety_buffer}
        '''
        result = self._values.get("safety_buffer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tidy_acme(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable tidying ACME accounts, orders and authorizations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_acme PkiSecretBackendConfigAutoTidy#tidy_acme}
        '''
        result = self._values.get("tidy_acme")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_cert_metadata(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable tidying up certificate metadata.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cert_metadata PkiSecretBackendConfigAutoTidy#tidy_cert_metadata}
        '''
        result = self._values.get("tidy_cert_metadata")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_cert_store(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable tidying up the certificate store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cert_store PkiSecretBackendConfigAutoTidy#tidy_cert_store}
        '''
        result = self._values.get("tidy_cert_store")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_cmpv2_nonce_store(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable tidying up the CMPv2 nonce store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cmpv2_nonce_store PkiSecretBackendConfigAutoTidy#tidy_cmpv2_nonce_store}
        '''
        result = self._values.get("tidy_cmpv2_nonce_store")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_cross_cluster_revoked_certs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to enable tidying up the cross-cluster revoked certificate store.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_cross_cluster_revoked_certs PkiSecretBackendConfigAutoTidy#tidy_cross_cluster_revoked_certs}
        '''
        result = self._values.get("tidy_cross_cluster_revoked_certs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_expired_issuers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to automatically remove expired issuers past the issuer_safety_buffer.

        No keys will be removed as part of this operation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_expired_issuers PkiSecretBackendConfigAutoTidy#tidy_expired_issuers}
        '''
        result = self._values.get("tidy_expired_issuers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_move_legacy_ca_bundle(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to move the legacy ca_bundle from /config/ca_bundle to /config/ca_bundle.bak.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_move_legacy_ca_bundle PkiSecretBackendConfigAutoTidy#tidy_move_legacy_ca_bundle}
        '''
        result = self._values.get("tidy_move_legacy_ca_bundle")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_revocation_queue(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to remove stale revocation queue entries that haven't been confirmed by any active cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revocation_queue PkiSecretBackendConfigAutoTidy#tidy_revocation_queue}
        '''
        result = self._values.get("tidy_revocation_queue")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_revoked_cert_issuer_associations(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to validate issuer associations on revocation entries.

        This helps increase the performance of CRL building and OCSP responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revoked_cert_issuer_associations PkiSecretBackendConfigAutoTidy#tidy_revoked_cert_issuer_associations}
        '''
        result = self._values.get("tidy_revoked_cert_issuer_associations")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tidy_revoked_certs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to remove all invalid and expired certificates from storage.

        A revoked storage entry is considered invalid if the entry is empty, or the value within the entry is empty. If a certificate is removed due to expiry, the entry will also be removed from the CRL, and the CRL will be rotated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/pki_secret_backend_config_auto_tidy#tidy_revoked_certs PkiSecretBackendConfigAutoTidy#tidy_revoked_certs}
        '''
        result = self._values.get("tidy_revoked_certs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiSecretBackendConfigAutoTidyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiSecretBackendConfigAutoTidy",
    "PkiSecretBackendConfigAutoTidyConfig",
]

publication.publish()

def _typecheckingstub__f95d58e6a70315c72586049567eab917dc8c203f0a9dadd28c6a40a5d5d782a8(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    acme_account_safety_buffer: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    interval_duration: typing.Optional[builtins.str] = None,
    issuer_safety_buffer: typing.Optional[builtins.str] = None,
    maintain_stored_certificate_counts: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_startup_backoff_duration: typing.Optional[builtins.str] = None,
    min_startup_backoff_duration: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    pause_duration: typing.Optional[builtins.str] = None,
    publish_stored_certificate_count_metrics: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    revocation_queue_safety_buffer: typing.Optional[builtins.str] = None,
    safety_buffer: typing.Optional[builtins.str] = None,
    tidy_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cert_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cert_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cmpv2_nonce_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cross_cluster_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_expired_issuers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_move_legacy_ca_bundle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_revocation_queue: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_revoked_cert_issuer_associations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__5d89a254450b0ad1776864c69ba6957cc25c4052e731fa94cd7bd84f724c4dfa(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4411bf9fb22a02f1cda51cb780bbdca4219b97a0559d03b04b97f786edb128e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0269329b08d355ed078b26ec621ba067c41a5e605da6ef60bcf566836dc2aa18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c30db7b677fb70adab89b87e11e95aaeaaf4aaeb2f7af195cd47ac2f084e6d7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad111d684b6d94efc58264bc7bb2ac2c6aa48253b995d8d33e4a5244935aee2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__919969d8421dc91f4e837f56e8ccc5e7f1aff77ad9e1756ce61205358e647cd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afa04c7f4939d0059430deb5604d24b917548c73bd4c94bb6b6d41c2a7360a7f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__666f8e2be040b84a44f23a8dc6284039c6aa96f3697d0a7088939aa2ea463e7f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e58b32ca033d3ba36bd6d85ff7790343aed2e9d4eb3963962896773a5bd3041(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6caf7d4c4116a3de50485ca059f165b4daf85d67527cf1c7197a8386090d7e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d04930401e7aa730d56665c1e187a62ae54a4652056b40bd2a15f9b9e78cf1fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39ae9f6e41a8ee40366e725c575af1099abb08d3be4e1c58ab06a71e9c684d1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ed4b7743004bc2598bcc254d676cfa6a6e35ecb15db74eba7c061d9a2a60c9e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d19adaad0deff0c3a754bc137785fde7fc193309e4bf0d514f0a5cd10494b9e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc472b800c3671aec180035b6a6c78f4d9b7def36d5c3e5f4b8d5020a44183c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd0b471ef786db3f7c66753e3c7f8400402c3c58c2494b0321a2890d70966499(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a77013b61f773c0ec4e8c516c15b19297b9e8dcc645835497b25cd1c71c51d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c32d273e992fe69d13759c6767805ef44fd2d1de2409a7394754d960ec472c27(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2fa895a79e164526921c4dec56a58fa8d375be6f77f7ce14195786799f2638(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1266e91c9eb20ee68975d352d0d5e5b73304f1eab33b1d5423450ef86da7c8df(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18688019a726376d1f5bd2fbfed0a5d9b65196653d599770b393742c18b34d7f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4c27b3abc0b2db24b6b8f9af4d24979e0f3b8c755018c2c3447f3459969f0bb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a00655f8abfe148ecaf46893e2c8cf8d65da422459e25f42bde86741b36e16a0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3c3dca53b85922729bcb3368350a037ec008ea6ace3fb28bf7a0845d7972b16(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59d516604d38656473b80e1fdb8a024496cb14a10bb34aef57dc19d62078725e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e329c31aaddefe1fe3438a82777cf24574626cdac37f163668414d61fea64de3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backend: builtins.str,
    enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    acme_account_safety_buffer: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    interval_duration: typing.Optional[builtins.str] = None,
    issuer_safety_buffer: typing.Optional[builtins.str] = None,
    maintain_stored_certificate_counts: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_startup_backoff_duration: typing.Optional[builtins.str] = None,
    min_startup_backoff_duration: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    pause_duration: typing.Optional[builtins.str] = None,
    publish_stored_certificate_count_metrics: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    revocation_queue_safety_buffer: typing.Optional[builtins.str] = None,
    safety_buffer: typing.Optional[builtins.str] = None,
    tidy_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cert_metadata: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cert_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cmpv2_nonce_store: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_cross_cluster_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_expired_issuers: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_move_legacy_ca_bundle: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_revocation_queue: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_revoked_cert_issuer_associations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tidy_revoked_certs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
