r'''
# `vault_kubernetes_secret_backend_role`

Refer to the Terraform Registry for docs: [`vault_kubernetes_secret_backend_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role).
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


class KubernetesSecretBackendRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.kubernetesSecretBackendRole.KubernetesSecretBackendRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role vault_kubernetes_secret_backend_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        name: builtins.str,
        allowed_kubernetes_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_kubernetes_namespace_selector: typing.Optional[builtins.str] = None,
        extra_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        generated_role_rules: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kubernetes_role_name: typing.Optional[builtins.str] = None,
        kubernetes_role_type: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        name_template: typing.Optional[builtins.str] = None,
        service_account_name: typing.Optional[builtins.str] = None,
        token_default_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role vault_kubernetes_secret_backend_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: The mount path for the Kubernetes secrets engine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#backend KubernetesSecretBackendRole#backend}
        :param name: The name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#name KubernetesSecretBackendRole#name}
        :param allowed_kubernetes_namespaces: The list of Kubernetes namespaces this role can generate credentials for. If set to '*' all namespaces are allowed. If set with``allowed_kubernetes_namespace_selector``, the conditions are ``OR``ed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#allowed_kubernetes_namespaces KubernetesSecretBackendRole#allowed_kubernetes_namespaces}
        :param allowed_kubernetes_namespace_selector: A label selector for Kubernetes namespaces in which credentials can begenerated. Accepts either a JSON or YAML object. The value should be of typeLabelSelector. If set with ``allowed_kubernetes_namespace``, the conditions are ``OR``ed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#allowed_kubernetes_namespace_selector KubernetesSecretBackendRole#allowed_kubernetes_namespace_selector}
        :param extra_annotations: Additional annotations to apply to all generated Kubernetes objects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#extra_annotations KubernetesSecretBackendRole#extra_annotations}
        :param extra_labels: Additional labels to apply to all generated Kubernetes objects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#extra_labels KubernetesSecretBackendRole#extra_labels}
        :param generated_role_rules: The Role or ClusterRole rules to use when generating a role. Accepts either JSON or YAML formatted rules. Mutually exclusive with 'service_account_name' and 'kubernetes_role_name'. If set, the entire chain of Kubernetes objects will be generated when credentials are requested. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#generated_role_rules KubernetesSecretBackendRole#generated_role_rules}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#id KubernetesSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kubernetes_role_name: The pre-existing Role or ClusterRole to bind a generated service account to. Mutually exclusive with 'service_account_name' and 'generated_role_rules'. If set, Kubernetes token, service account, and role binding objects will be created when credentials are requested. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#kubernetes_role_name KubernetesSecretBackendRole#kubernetes_role_name}
        :param kubernetes_role_type: Specifies whether the Kubernetes role is a Role or ClusterRole. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#kubernetes_role_type KubernetesSecretBackendRole#kubernetes_role_type}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#namespace KubernetesSecretBackendRole#namespace}
        :param name_template: The name template to use when generating service accounts, roles and role bindings. If unset, a default template is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#name_template KubernetesSecretBackendRole#name_template}
        :param service_account_name: The pre-existing service account to generate tokens for. Mutually exclusive with 'kubernetes_role_name' and 'generated_role_rules'. If set, only a Kubernetes token will be created when credentials are requested. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#service_account_name KubernetesSecretBackendRole#service_account_name}
        :param token_default_ttl: The default TTL for generated Kubernetes tokens in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#token_default_ttl KubernetesSecretBackendRole#token_default_ttl}
        :param token_max_ttl: The maximum TTL for generated Kubernetes tokens in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#token_max_ttl KubernetesSecretBackendRole#token_max_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__550c920d5de92f09465a946ff11355183eb6a6e9d0c8d06f568f6ea59ad632a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = KubernetesSecretBackendRoleConfig(
            backend=backend,
            name=name,
            allowed_kubernetes_namespaces=allowed_kubernetes_namespaces,
            allowed_kubernetes_namespace_selector=allowed_kubernetes_namespace_selector,
            extra_annotations=extra_annotations,
            extra_labels=extra_labels,
            generated_role_rules=generated_role_rules,
            id=id,
            kubernetes_role_name=kubernetes_role_name,
            kubernetes_role_type=kubernetes_role_type,
            namespace=namespace,
            name_template=name_template,
            service_account_name=service_account_name,
            token_default_ttl=token_default_ttl,
            token_max_ttl=token_max_ttl,
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
        '''Generates CDKTF code for importing a KubernetesSecretBackendRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the KubernetesSecretBackendRole to import.
        :param import_from_id: The id of the existing KubernetesSecretBackendRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the KubernetesSecretBackendRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8f3266a1de3d4d8147621a0c9960016fb835b92bc47e9747e3ef04b42d2903c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedKubernetesNamespaces")
    def reset_allowed_kubernetes_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedKubernetesNamespaces", []))

    @jsii.member(jsii_name="resetAllowedKubernetesNamespaceSelector")
    def reset_allowed_kubernetes_namespace_selector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedKubernetesNamespaceSelector", []))

    @jsii.member(jsii_name="resetExtraAnnotations")
    def reset_extra_annotations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraAnnotations", []))

    @jsii.member(jsii_name="resetExtraLabels")
    def reset_extra_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraLabels", []))

    @jsii.member(jsii_name="resetGeneratedRoleRules")
    def reset_generated_role_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGeneratedRoleRules", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKubernetesRoleName")
    def reset_kubernetes_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKubernetesRoleName", []))

    @jsii.member(jsii_name="resetKubernetesRoleType")
    def reset_kubernetes_role_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKubernetesRoleType", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNameTemplate")
    def reset_name_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNameTemplate", []))

    @jsii.member(jsii_name="resetServiceAccountName")
    def reset_service_account_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountName", []))

    @jsii.member(jsii_name="resetTokenDefaultTtl")
    def reset_token_default_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenDefaultTtl", []))

    @jsii.member(jsii_name="resetTokenMaxTtl")
    def reset_token_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenMaxTtl", []))

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
    @jsii.member(jsii_name="allowedKubernetesNamespaceSelectorInput")
    def allowed_kubernetes_namespace_selector_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedKubernetesNamespaceSelectorInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedKubernetesNamespacesInput")
    def allowed_kubernetes_namespaces_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedKubernetesNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="extraAnnotationsInput")
    def extra_annotations_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "extraAnnotationsInput"))

    @builtins.property
    @jsii.member(jsii_name="extraLabelsInput")
    def extra_labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "extraLabelsInput"))

    @builtins.property
    @jsii.member(jsii_name="generatedRoleRulesInput")
    def generated_role_rules_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "generatedRoleRulesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="kubernetesRoleNameInput")
    def kubernetes_role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kubernetesRoleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="kubernetesRoleTypeInput")
    def kubernetes_role_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kubernetesRoleTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="nameTemplateInput")
    def name_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountNameInput")
    def service_account_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenDefaultTtlInput")
    def token_default_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenDefaultTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtlInput")
    def token_max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenMaxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedKubernetesNamespaces")
    def allowed_kubernetes_namespaces(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedKubernetesNamespaces"))

    @allowed_kubernetes_namespaces.setter
    def allowed_kubernetes_namespaces(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0369277f69c6505aa09b16d618b9cb08b1c549ee657788fa36a0dd3768b1f38b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedKubernetesNamespaces", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowedKubernetesNamespaceSelector")
    def allowed_kubernetes_namespace_selector(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedKubernetesNamespaceSelector"))

    @allowed_kubernetes_namespace_selector.setter
    def allowed_kubernetes_namespace_selector(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cc927dc9379fea9c358f7a00e42428f025f884c14af9ad699bc7ebc42cbd62d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedKubernetesNamespaceSelector", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1a7c93123c83c743c27fb422d13b99ec26630b076e2a671275ccc9c88e811b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extraAnnotations")
    def extra_annotations(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extraAnnotations"))

    @extra_annotations.setter
    def extra_annotations(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__767977e762c5f2ad27b6f52d82d3a3368acb56ff4eded92e373b922c8f69f55d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extraAnnotations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extraLabels")
    def extra_labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extraLabels"))

    @extra_labels.setter
    def extra_labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__171038a9eb462431db71660f26e3879e7ee321ef65940b8184c998c9182481a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extraLabels", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="generatedRoleRules")
    def generated_role_rules(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "generatedRoleRules"))

    @generated_role_rules.setter
    def generated_role_rules(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59583c9e386b38bec602ec4a5e815880af9ff0054214c3b54654dda5bc6bc35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generatedRoleRules", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf9a00174a84c9045c1aa66676b7c217c5d2bf6d92650528364a1bcfa3759cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kubernetesRoleName")
    def kubernetes_role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kubernetesRoleName"))

    @kubernetes_role_name.setter
    def kubernetes_role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7af6ac54b13276be0a473a75308962ff8883de3cd873676713c1593f1ed0cae6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kubernetesRoleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kubernetesRoleType")
    def kubernetes_role_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kubernetesRoleType"))

    @kubernetes_role_type.setter
    def kubernetes_role_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a75e2eee4e3a946ec216a31bf2f1fe66a357f9f727b2a1c86aa3c9d8b94761e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kubernetesRoleType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cf627d26b53c774c6a57933fc1fbb09bc282675070258cc6b13f3b18cebbb7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fda152a2494e9f295ad3c4ce1fdf741362f9e2f4e69d0fda9ff62cab260e729)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nameTemplate")
    def name_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameTemplate"))

    @name_template.setter
    def name_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35f121e3b637b53168ad53d2f5d1da88f154b70cfe4527c8274493de1d32bf46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountName"))

    @service_account_name.setter
    def service_account_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06244725be1bd701a65baa7493b321f7810a92e379929d0b3e7db02e6aaa2804)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenDefaultTtl")
    def token_default_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenDefaultTtl"))

    @token_default_ttl.setter
    def token_default_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd0a712373acd2d22cd189f27c8bc7f68a7198321753cf31743ae0ea9e908194)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenDefaultTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenMaxTtl")
    def token_max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenMaxTtl"))

    @token_max_ttl.setter
    def token_max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef70a92ea2818247d030c7c139722c2c7e64d9c4d416d86febdb6e613e31e343)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenMaxTtl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.kubernetesSecretBackendRole.KubernetesSecretBackendRoleConfig",
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
        "allowed_kubernetes_namespaces": "allowedKubernetesNamespaces",
        "allowed_kubernetes_namespace_selector": "allowedKubernetesNamespaceSelector",
        "extra_annotations": "extraAnnotations",
        "extra_labels": "extraLabels",
        "generated_role_rules": "generatedRoleRules",
        "id": "id",
        "kubernetes_role_name": "kubernetesRoleName",
        "kubernetes_role_type": "kubernetesRoleType",
        "namespace": "namespace",
        "name_template": "nameTemplate",
        "service_account_name": "serviceAccountName",
        "token_default_ttl": "tokenDefaultTtl",
        "token_max_ttl": "tokenMaxTtl",
    },
)
class KubernetesSecretBackendRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_kubernetes_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_kubernetes_namespace_selector: typing.Optional[builtins.str] = None,
        extra_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        extra_labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        generated_role_rules: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kubernetes_role_name: typing.Optional[builtins.str] = None,
        kubernetes_role_type: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        name_template: typing.Optional[builtins.str] = None,
        service_account_name: typing.Optional[builtins.str] = None,
        token_default_ttl: typing.Optional[jsii.Number] = None,
        token_max_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: The mount path for the Kubernetes secrets engine. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#backend KubernetesSecretBackendRole#backend}
        :param name: The name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#name KubernetesSecretBackendRole#name}
        :param allowed_kubernetes_namespaces: The list of Kubernetes namespaces this role can generate credentials for. If set to '*' all namespaces are allowed. If set with``allowed_kubernetes_namespace_selector``, the conditions are ``OR``ed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#allowed_kubernetes_namespaces KubernetesSecretBackendRole#allowed_kubernetes_namespaces}
        :param allowed_kubernetes_namespace_selector: A label selector for Kubernetes namespaces in which credentials can begenerated. Accepts either a JSON or YAML object. The value should be of typeLabelSelector. If set with ``allowed_kubernetes_namespace``, the conditions are ``OR``ed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#allowed_kubernetes_namespace_selector KubernetesSecretBackendRole#allowed_kubernetes_namespace_selector}
        :param extra_annotations: Additional annotations to apply to all generated Kubernetes objects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#extra_annotations KubernetesSecretBackendRole#extra_annotations}
        :param extra_labels: Additional labels to apply to all generated Kubernetes objects. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#extra_labels KubernetesSecretBackendRole#extra_labels}
        :param generated_role_rules: The Role or ClusterRole rules to use when generating a role. Accepts either JSON or YAML formatted rules. Mutually exclusive with 'service_account_name' and 'kubernetes_role_name'. If set, the entire chain of Kubernetes objects will be generated when credentials are requested. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#generated_role_rules KubernetesSecretBackendRole#generated_role_rules}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#id KubernetesSecretBackendRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kubernetes_role_name: The pre-existing Role or ClusterRole to bind a generated service account to. Mutually exclusive with 'service_account_name' and 'generated_role_rules'. If set, Kubernetes token, service account, and role binding objects will be created when credentials are requested. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#kubernetes_role_name KubernetesSecretBackendRole#kubernetes_role_name}
        :param kubernetes_role_type: Specifies whether the Kubernetes role is a Role or ClusterRole. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#kubernetes_role_type KubernetesSecretBackendRole#kubernetes_role_type}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#namespace KubernetesSecretBackendRole#namespace}
        :param name_template: The name template to use when generating service accounts, roles and role bindings. If unset, a default template is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#name_template KubernetesSecretBackendRole#name_template}
        :param service_account_name: The pre-existing service account to generate tokens for. Mutually exclusive with 'kubernetes_role_name' and 'generated_role_rules'. If set, only a Kubernetes token will be created when credentials are requested. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#service_account_name KubernetesSecretBackendRole#service_account_name}
        :param token_default_ttl: The default TTL for generated Kubernetes tokens in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#token_default_ttl KubernetesSecretBackendRole#token_default_ttl}
        :param token_max_ttl: The maximum TTL for generated Kubernetes tokens in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#token_max_ttl KubernetesSecretBackendRole#token_max_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b40f072d0d6c37deb197b57529464b470b29134b16c6465848b02c69af06082e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allowed_kubernetes_namespaces", value=allowed_kubernetes_namespaces, expected_type=type_hints["allowed_kubernetes_namespaces"])
            check_type(argname="argument allowed_kubernetes_namespace_selector", value=allowed_kubernetes_namespace_selector, expected_type=type_hints["allowed_kubernetes_namespace_selector"])
            check_type(argname="argument extra_annotations", value=extra_annotations, expected_type=type_hints["extra_annotations"])
            check_type(argname="argument extra_labels", value=extra_labels, expected_type=type_hints["extra_labels"])
            check_type(argname="argument generated_role_rules", value=generated_role_rules, expected_type=type_hints["generated_role_rules"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument kubernetes_role_name", value=kubernetes_role_name, expected_type=type_hints["kubernetes_role_name"])
            check_type(argname="argument kubernetes_role_type", value=kubernetes_role_type, expected_type=type_hints["kubernetes_role_type"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument name_template", value=name_template, expected_type=type_hints["name_template"])
            check_type(argname="argument service_account_name", value=service_account_name, expected_type=type_hints["service_account_name"])
            check_type(argname="argument token_default_ttl", value=token_default_ttl, expected_type=type_hints["token_default_ttl"])
            check_type(argname="argument token_max_ttl", value=token_max_ttl, expected_type=type_hints["token_max_ttl"])
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
        if allowed_kubernetes_namespaces is not None:
            self._values["allowed_kubernetes_namespaces"] = allowed_kubernetes_namespaces
        if allowed_kubernetes_namespace_selector is not None:
            self._values["allowed_kubernetes_namespace_selector"] = allowed_kubernetes_namespace_selector
        if extra_annotations is not None:
            self._values["extra_annotations"] = extra_annotations
        if extra_labels is not None:
            self._values["extra_labels"] = extra_labels
        if generated_role_rules is not None:
            self._values["generated_role_rules"] = generated_role_rules
        if id is not None:
            self._values["id"] = id
        if kubernetes_role_name is not None:
            self._values["kubernetes_role_name"] = kubernetes_role_name
        if kubernetes_role_type is not None:
            self._values["kubernetes_role_type"] = kubernetes_role_type
        if namespace is not None:
            self._values["namespace"] = namespace
        if name_template is not None:
            self._values["name_template"] = name_template
        if service_account_name is not None:
            self._values["service_account_name"] = service_account_name
        if token_default_ttl is not None:
            self._values["token_default_ttl"] = token_default_ttl
        if token_max_ttl is not None:
            self._values["token_max_ttl"] = token_max_ttl

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
        '''The mount path for the Kubernetes secrets engine.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#backend KubernetesSecretBackendRole#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#name KubernetesSecretBackendRole#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_kubernetes_namespaces(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''The list of Kubernetes namespaces this role can generate credentials for.

        If set to '*' all namespaces are allowed. If set with``allowed_kubernetes_namespace_selector``, the conditions are ``OR``ed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#allowed_kubernetes_namespaces KubernetesSecretBackendRole#allowed_kubernetes_namespaces}
        '''
        result = self._values.get("allowed_kubernetes_namespaces")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allowed_kubernetes_namespace_selector(self) -> typing.Optional[builtins.str]:
        '''A label selector for Kubernetes namespaces in which credentials can begenerated.

        Accepts either a JSON or YAML object. The value should be of typeLabelSelector. If set with ``allowed_kubernetes_namespace``, the conditions are ``OR``ed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#allowed_kubernetes_namespace_selector KubernetesSecretBackendRole#allowed_kubernetes_namespace_selector}
        '''
        result = self._values.get("allowed_kubernetes_namespace_selector")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional annotations to apply to all generated Kubernetes objects.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#extra_annotations KubernetesSecretBackendRole#extra_annotations}
        '''
        result = self._values.get("extra_annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def extra_labels(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional labels to apply to all generated Kubernetes objects.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#extra_labels KubernetesSecretBackendRole#extra_labels}
        '''
        result = self._values.get("extra_labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def generated_role_rules(self) -> typing.Optional[builtins.str]:
        '''The Role or ClusterRole rules to use when generating a role.

        Accepts either JSON or YAML formatted rules. Mutually exclusive with 'service_account_name' and 'kubernetes_role_name'. If set, the entire chain of Kubernetes objects will be generated when credentials are requested.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#generated_role_rules KubernetesSecretBackendRole#generated_role_rules}
        '''
        result = self._values.get("generated_role_rules")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#id KubernetesSecretBackendRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kubernetes_role_name(self) -> typing.Optional[builtins.str]:
        '''The pre-existing Role or ClusterRole to bind a generated service account to.

        Mutually exclusive with 'service_account_name' and 'generated_role_rules'. If set, Kubernetes token, service account, and role binding objects will be created when credentials are requested.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#kubernetes_role_name KubernetesSecretBackendRole#kubernetes_role_name}
        '''
        result = self._values.get("kubernetes_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kubernetes_role_type(self) -> typing.Optional[builtins.str]:
        '''Specifies whether the Kubernetes role is a Role or ClusterRole.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#kubernetes_role_type KubernetesSecretBackendRole#kubernetes_role_type}
        '''
        result = self._values.get("kubernetes_role_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#namespace KubernetesSecretBackendRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_template(self) -> typing.Optional[builtins.str]:
        '''The name template to use when generating service accounts, roles and role bindings.

        If unset, a default template is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#name_template KubernetesSecretBackendRole#name_template}
        '''
        result = self._values.get("name_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_account_name(self) -> typing.Optional[builtins.str]:
        '''The pre-existing service account to generate tokens for.

        Mutually exclusive with 'kubernetes_role_name' and 'generated_role_rules'. If set, only a Kubernetes token will be created when credentials are requested.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#service_account_name KubernetesSecretBackendRole#service_account_name}
        '''
        result = self._values.get("service_account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_default_ttl(self) -> typing.Optional[jsii.Number]:
        '''The default TTL for generated Kubernetes tokens in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#token_default_ttl KubernetesSecretBackendRole#token_default_ttl}
        '''
        result = self._values.get("token_default_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_max_ttl(self) -> typing.Optional[jsii.Number]:
        '''The maximum TTL for generated Kubernetes tokens in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/kubernetes_secret_backend_role#token_max_ttl KubernetesSecretBackendRole#token_max_ttl}
        '''
        result = self._values.get("token_max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesSecretBackendRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KubernetesSecretBackendRole",
    "KubernetesSecretBackendRoleConfig",
]

publication.publish()

def _typecheckingstub__550c920d5de92f09465a946ff11355183eb6a6e9d0c8d06f568f6ea59ad632a7(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    name: builtins.str,
    allowed_kubernetes_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_kubernetes_namespace_selector: typing.Optional[builtins.str] = None,
    extra_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    generated_role_rules: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    kubernetes_role_name: typing.Optional[builtins.str] = None,
    kubernetes_role_type: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    name_template: typing.Optional[builtins.str] = None,
    service_account_name: typing.Optional[builtins.str] = None,
    token_default_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__b8f3266a1de3d4d8147621a0c9960016fb835b92bc47e9747e3ef04b42d2903c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0369277f69c6505aa09b16d618b9cb08b1c549ee657788fa36a0dd3768b1f38b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cc927dc9379fea9c358f7a00e42428f025f884c14af9ad699bc7ebc42cbd62d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1a7c93123c83c743c27fb422d13b99ec26630b076e2a671275ccc9c88e811b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__767977e762c5f2ad27b6f52d82d3a3368acb56ff4eded92e373b922c8f69f55d(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__171038a9eb462431db71660f26e3879e7ee321ef65940b8184c998c9182481a8(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59583c9e386b38bec602ec4a5e815880af9ff0054214c3b54654dda5bc6bc35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf9a00174a84c9045c1aa66676b7c217c5d2bf6d92650528364a1bcfa3759cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7af6ac54b13276be0a473a75308962ff8883de3cd873676713c1593f1ed0cae6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a75e2eee4e3a946ec216a31bf2f1fe66a357f9f727b2a1c86aa3c9d8b94761e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cf627d26b53c774c6a57933fc1fbb09bc282675070258cc6b13f3b18cebbb7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fda152a2494e9f295ad3c4ce1fdf741362f9e2f4e69d0fda9ff62cab260e729(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35f121e3b637b53168ad53d2f5d1da88f154b70cfe4527c8274493de1d32bf46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06244725be1bd701a65baa7493b321f7810a92e379929d0b3e7db02e6aaa2804(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd0a712373acd2d22cd189f27c8bc7f68a7198321753cf31743ae0ea9e908194(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef70a92ea2818247d030c7c139722c2c7e64d9c4d416d86febdb6e613e31e343(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b40f072d0d6c37deb197b57529464b470b29134b16c6465848b02c69af06082e(
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
    allowed_kubernetes_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_kubernetes_namespace_selector: typing.Optional[builtins.str] = None,
    extra_annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    extra_labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    generated_role_rules: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    kubernetes_role_name: typing.Optional[builtins.str] = None,
    kubernetes_role_type: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    name_template: typing.Optional[builtins.str] = None,
    service_account_name: typing.Optional[builtins.str] = None,
    token_default_ttl: typing.Optional[jsii.Number] = None,
    token_max_ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
