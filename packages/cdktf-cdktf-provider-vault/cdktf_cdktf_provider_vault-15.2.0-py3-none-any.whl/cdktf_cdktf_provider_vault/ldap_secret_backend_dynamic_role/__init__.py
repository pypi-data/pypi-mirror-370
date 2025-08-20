r'''
# `vault_ldap_secret_backend_dynamic_role`

Refer to the Terraform Registry for docs: [`vault_ldap_secret_backend_dynamic_role`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role).
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


class LdapSecretBackendDynamicRole(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.ldapSecretBackendDynamicRole.LdapSecretBackendDynamicRole",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role vault_ldap_secret_backend_dynamic_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        creation_ldif: builtins.str,
        deletion_ldif: builtins.str,
        role_name: builtins.str,
        default_ttl: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        rollback_ldif: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role vault_ldap_secret_backend_dynamic_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param creation_ldif: A templatized LDIF string used to create a user account. May contain multiple entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#creation_ldif LdapSecretBackendDynamicRole#creation_ldif}
        :param deletion_ldif: A templatized LDIF string used to delete the user account once its TTL has expired. This may contain multiple LDIF entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#deletion_ldif LdapSecretBackendDynamicRole#deletion_ldif}
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#role_name LdapSecretBackendDynamicRole#role_name}
        :param default_ttl: Specifies the TTL for the leases associated with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#default_ttl LdapSecretBackendDynamicRole#default_ttl}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#id LdapSecretBackendDynamicRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_ttl: Specifies the maximum TTL for the leases associated with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#max_ttl LdapSecretBackendDynamicRole#max_ttl}
        :param mount: The path where the LDAP secrets backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#mount LdapSecretBackendDynamicRole#mount}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#namespace LdapSecretBackendDynamicRole#namespace}
        :param rollback_ldif: A templatized LDIF string used to attempt to rollback any changes in the event that execution of the creation_ldif results in an error. This may contain multiple LDIF entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#rollback_ldif LdapSecretBackendDynamicRole#rollback_ldif}
        :param username_template: A template used to generate a dynamic username. This will be used to fill in the .Username field within the creation_ldif string. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#username_template LdapSecretBackendDynamicRole#username_template}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fd9aa84fb350911cf8c4e82f67c7971fc5b567b5cfc44d2d5f0d733380477c9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = LdapSecretBackendDynamicRoleConfig(
            creation_ldif=creation_ldif,
            deletion_ldif=deletion_ldif,
            role_name=role_name,
            default_ttl=default_ttl,
            id=id,
            max_ttl=max_ttl,
            mount=mount,
            namespace=namespace,
            rollback_ldif=rollback_ldif,
            username_template=username_template,
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
        '''Generates CDKTF code for importing a LdapSecretBackendDynamicRole resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LdapSecretBackendDynamicRole to import.
        :param import_from_id: The id of the existing LdapSecretBackendDynamicRole that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LdapSecretBackendDynamicRole to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__114d1cc2f3d0a54a8cc8027e7ba16215d176a30d5f3d691250aabcad5ede873c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDefaultTtl")
    def reset_default_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTtl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetMount")
    def reset_mount(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMount", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetRollbackLdif")
    def reset_rollback_ldif(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollbackLdif", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

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
    @jsii.member(jsii_name="creationLdifInput")
    def creation_ldif_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creationLdifInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTtlInput")
    def default_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="deletionLdifInput")
    def deletion_ldif_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deletionLdifInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="mountInput")
    def mount_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mountInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="rollbackLdifInput")
    def rollback_ldif_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rollbackLdifInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="creationLdif")
    def creation_ldif(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationLdif"))

    @creation_ldif.setter
    def creation_ldif(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d849efe7b14061478cfb33593a1dbed281805e27a321266988b766a97c9c96e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationLdif", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTtl")
    def default_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultTtl"))

    @default_ttl.setter
    def default_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__370ec748a240e8b07f20236847522a1ca5533b8c44149044a86966a5c09514c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deletionLdif")
    def deletion_ldif(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletionLdif"))

    @deletion_ldif.setter
    def deletion_ldif(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d057699ad5f394e7122c1b210c962c45009d71c07cc3ef952544f6960462e2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deletionLdif", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8a7a5032c3639adee370f312120195ab8fab076ee268949e27fc9b66fc755ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1b8b278b386dcaeb3696410171cd290f258336c5b4f2b3dfe9d47cbc5b99f98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mount")
    def mount(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mount"))

    @mount.setter
    def mount(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b77a643cc387595598156589f6336b2aa3c5e047cb72094604eeaf40d63322b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__696fe486f13dcd85c0bffa6668e91b8417773d20e27432698d6c97df18a731dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2b5c28434f8e7619ab1be928826c46c49e058dcc43b67e566ce75eea96fae44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rollbackLdif")
    def rollback_ldif(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rollbackLdif"))

    @rollback_ldif.setter
    def rollback_ldif(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e39c9be6334b74d0847da184bc8b06e7190d2698a7e3b6ec57cc34bd727d0bd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rollbackLdif", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e4280ecbed80e4fb9584d67c978f4b417dafce7b2dedaf823ba6fe6b669dc39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.ldapSecretBackendDynamicRole.LdapSecretBackendDynamicRoleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "creation_ldif": "creationLdif",
        "deletion_ldif": "deletionLdif",
        "role_name": "roleName",
        "default_ttl": "defaultTtl",
        "id": "id",
        "max_ttl": "maxTtl",
        "mount": "mount",
        "namespace": "namespace",
        "rollback_ldif": "rollbackLdif",
        "username_template": "usernameTemplate",
    },
)
class LdapSecretBackendDynamicRoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        creation_ldif: builtins.str,
        deletion_ldif: builtins.str,
        role_name: builtins.str,
        default_ttl: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        mount: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        rollback_ldif: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param creation_ldif: A templatized LDIF string used to create a user account. May contain multiple entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#creation_ldif LdapSecretBackendDynamicRole#creation_ldif}
        :param deletion_ldif: A templatized LDIF string used to delete the user account once its TTL has expired. This may contain multiple LDIF entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#deletion_ldif LdapSecretBackendDynamicRole#deletion_ldif}
        :param role_name: Name of the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#role_name LdapSecretBackendDynamicRole#role_name}
        :param default_ttl: Specifies the TTL for the leases associated with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#default_ttl LdapSecretBackendDynamicRole#default_ttl}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#id LdapSecretBackendDynamicRole#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param max_ttl: Specifies the maximum TTL for the leases associated with this role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#max_ttl LdapSecretBackendDynamicRole#max_ttl}
        :param mount: The path where the LDAP secrets backend is mounted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#mount LdapSecretBackendDynamicRole#mount}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#namespace LdapSecretBackendDynamicRole#namespace}
        :param rollback_ldif: A templatized LDIF string used to attempt to rollback any changes in the event that execution of the creation_ldif results in an error. This may contain multiple LDIF entries. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#rollback_ldif LdapSecretBackendDynamicRole#rollback_ldif}
        :param username_template: A template used to generate a dynamic username. This will be used to fill in the .Username field within the creation_ldif string. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#username_template LdapSecretBackendDynamicRole#username_template}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1dd94ce742ec21fc588ba39c4679865a81a5b860ae948f0768929e050a3a243)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument creation_ldif", value=creation_ldif, expected_type=type_hints["creation_ldif"])
            check_type(argname="argument deletion_ldif", value=deletion_ldif, expected_type=type_hints["deletion_ldif"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument default_ttl", value=default_ttl, expected_type=type_hints["default_ttl"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument max_ttl", value=max_ttl, expected_type=type_hints["max_ttl"])
            check_type(argname="argument mount", value=mount, expected_type=type_hints["mount"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument rollback_ldif", value=rollback_ldif, expected_type=type_hints["rollback_ldif"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "creation_ldif": creation_ldif,
            "deletion_ldif": deletion_ldif,
            "role_name": role_name,
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
        if default_ttl is not None:
            self._values["default_ttl"] = default_ttl
        if id is not None:
            self._values["id"] = id
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if mount is not None:
            self._values["mount"] = mount
        if namespace is not None:
            self._values["namespace"] = namespace
        if rollback_ldif is not None:
            self._values["rollback_ldif"] = rollback_ldif
        if username_template is not None:
            self._values["username_template"] = username_template

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
    def creation_ldif(self) -> builtins.str:
        '''A templatized LDIF string used to create a user account. May contain multiple entries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#creation_ldif LdapSecretBackendDynamicRole#creation_ldif}
        '''
        result = self._values.get("creation_ldif")
        assert result is not None, "Required property 'creation_ldif' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def deletion_ldif(self) -> builtins.str:
        '''A templatized LDIF string used to delete the user account once its TTL has expired.

        This may contain multiple LDIF entries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#deletion_ldif LdapSecretBackendDynamicRole#deletion_ldif}
        '''
        result = self._values.get("deletion_ldif")
        assert result is not None, "Required property 'deletion_ldif' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> builtins.str:
        '''Name of the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#role_name LdapSecretBackendDynamicRole#role_name}
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default_ttl(self) -> typing.Optional[jsii.Number]:
        '''Specifies the TTL for the leases associated with this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#default_ttl LdapSecretBackendDynamicRole#default_ttl}
        '''
        result = self._values.get("default_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#id LdapSecretBackendDynamicRole#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Specifies the maximum TTL for the leases associated with this role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#max_ttl LdapSecretBackendDynamicRole#max_ttl}
        '''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mount(self) -> typing.Optional[builtins.str]:
        '''The path where the LDAP secrets backend is mounted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#mount LdapSecretBackendDynamicRole#mount}
        '''
        result = self._values.get("mount")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#namespace LdapSecretBackendDynamicRole#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rollback_ldif(self) -> typing.Optional[builtins.str]:
        '''A templatized LDIF string used to attempt to rollback any changes in the event that execution of the creation_ldif results in an error.

        This may contain multiple LDIF entries.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#rollback_ldif LdapSecretBackendDynamicRole#rollback_ldif}
        '''
        result = self._values.get("rollback_ldif")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''A template used to generate a dynamic username.

        This will be used to fill in the .Username field within the creation_ldif string.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/ldap_secret_backend_dynamic_role#username_template LdapSecretBackendDynamicRole#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LdapSecretBackendDynamicRoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LdapSecretBackendDynamicRole",
    "LdapSecretBackendDynamicRoleConfig",
]

publication.publish()

def _typecheckingstub__3fd9aa84fb350911cf8c4e82f67c7971fc5b567b5cfc44d2d5f0d733380477c9(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    creation_ldif: builtins.str,
    deletion_ldif: builtins.str,
    role_name: builtins.str,
    default_ttl: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    rollback_ldif: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__114d1cc2f3d0a54a8cc8027e7ba16215d176a30d5f3d691250aabcad5ede873c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d849efe7b14061478cfb33593a1dbed281805e27a321266988b766a97c9c96e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__370ec748a240e8b07f20236847522a1ca5533b8c44149044a86966a5c09514c3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d057699ad5f394e7122c1b210c962c45009d71c07cc3ef952544f6960462e2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8a7a5032c3639adee370f312120195ab8fab076ee268949e27fc9b66fc755ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1b8b278b386dcaeb3696410171cd290f258336c5b4f2b3dfe9d47cbc5b99f98(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b77a643cc387595598156589f6336b2aa3c5e047cb72094604eeaf40d63322b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__696fe486f13dcd85c0bffa6668e91b8417773d20e27432698d6c97df18a731dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b5c28434f8e7619ab1be928826c46c49e058dcc43b67e566ce75eea96fae44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e39c9be6334b74d0847da184bc8b06e7190d2698a7e3b6ec57cc34bd727d0bd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e4280ecbed80e4fb9584d67c978f4b417dafce7b2dedaf823ba6fe6b669dc39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1dd94ce742ec21fc588ba39c4679865a81a5b860ae948f0768929e050a3a243(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    creation_ldif: builtins.str,
    deletion_ldif: builtins.str,
    role_name: builtins.str,
    default_ttl: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    max_ttl: typing.Optional[jsii.Number] = None,
    mount: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    rollback_ldif: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
