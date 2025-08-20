r'''
# CDKTF prebuilt bindings for hashicorp/vault provider version 5.2.1

This repo builds and publishes the [Terraform vault provider](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-vault](https://www.npmjs.com/package/@cdktf/provider-vault).

`npm install @cdktf/provider-vault`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-vault](https://pypi.org/project/cdktf-cdktf-provider-vault).

`pipenv install cdktf-cdktf-provider-vault`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Vault](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Vault).

`dotnet add package HashiCorp.Cdktf.Providers.Vault`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-vault](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-vault).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-vault</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-vault-go`](https://github.com/cdktf/cdktf-provider-vault-go) package.

`go get github.com/cdktf/cdktf-provider-vault-go/vault/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-vault-go/blob/main/vault/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-vault).

## Versioning

This project is explicitly not tracking the Terraform vault provider version 1:1. In fact, it always tracks `latest` of `~> 5.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform vault provider](https://registry.terraform.io/providers/hashicorp/vault/5.2.1)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "ad_secret_backend",
    "ad_secret_library",
    "ad_secret_role",
    "alicloud_auth_backend_role",
    "approle_auth_backend_login",
    "approle_auth_backend_role",
    "approle_auth_backend_role_secret_id",
    "audit",
    "audit_request_header",
    "auth_backend",
    "aws_auth_backend_cert",
    "aws_auth_backend_client",
    "aws_auth_backend_config_identity",
    "aws_auth_backend_identity_whitelist",
    "aws_auth_backend_login",
    "aws_auth_backend_role",
    "aws_auth_backend_role_tag",
    "aws_auth_backend_roletag_blacklist",
    "aws_auth_backend_sts_role",
    "aws_secret_backend",
    "aws_secret_backend_role",
    "aws_secret_backend_static_role",
    "azure_auth_backend_config",
    "azure_auth_backend_role",
    "azure_secret_backend",
    "azure_secret_backend_role",
    "cert_auth_backend_role",
    "config_ui_custom_message",
    "consul_secret_backend",
    "consul_secret_backend_role",
    "data_vault_ad_access_credentials",
    "data_vault_approle_auth_backend_role_id",
    "data_vault_auth_backend",
    "data_vault_auth_backends",
    "data_vault_aws_access_credentials",
    "data_vault_aws_static_access_credentials",
    "data_vault_azure_access_credentials",
    "data_vault_gcp_auth_backend_role",
    "data_vault_generic_secret",
    "data_vault_identity_entity",
    "data_vault_identity_group",
    "data_vault_identity_oidc_client_creds",
    "data_vault_identity_oidc_openid_config",
    "data_vault_identity_oidc_public_keys",
    "data_vault_kubernetes_auth_backend_config",
    "data_vault_kubernetes_auth_backend_role",
    "data_vault_kubernetes_service_account_token",
    "data_vault_kv_secret",
    "data_vault_kv_secret_subkeys_v2",
    "data_vault_kv_secret_v2",
    "data_vault_kv_secrets_list",
    "data_vault_kv_secrets_list_v2",
    "data_vault_ldap_dynamic_credentials",
    "data_vault_ldap_static_credentials",
    "data_vault_namespace",
    "data_vault_namespaces",
    "data_vault_nomad_access_token",
    "data_vault_pki_secret_backend_cert_metadata",
    "data_vault_pki_secret_backend_config_cmpv2",
    "data_vault_pki_secret_backend_config_est",
    "data_vault_pki_secret_backend_config_scep",
    "data_vault_pki_secret_backend_issuer",
    "data_vault_pki_secret_backend_issuers",
    "data_vault_pki_secret_backend_key",
    "data_vault_pki_secret_backend_keys",
    "data_vault_policy_document",
    "data_vault_raft_autopilot_state",
    "data_vault_ssh_secret_backend_sign",
    "data_vault_transform_decode",
    "data_vault_transform_encode",
    "data_vault_transit_cmac",
    "data_vault_transit_decrypt",
    "data_vault_transit_encrypt",
    "data_vault_transit_sign",
    "data_vault_transit_verify",
    "database_secret_backend_connection",
    "database_secret_backend_role",
    "database_secret_backend_static_role",
    "database_secrets_mount",
    "egp_policy",
    "gcp_auth_backend",
    "gcp_auth_backend_role",
    "gcp_secret_backend",
    "gcp_secret_impersonated_account",
    "gcp_secret_roleset",
    "gcp_secret_static_account",
    "generic_endpoint",
    "generic_secret",
    "github_auth_backend",
    "github_team",
    "github_user",
    "identity_entity",
    "identity_entity_alias",
    "identity_entity_policies",
    "identity_group",
    "identity_group_alias",
    "identity_group_member_entity_ids",
    "identity_group_member_group_ids",
    "identity_group_policies",
    "identity_mfa_duo",
    "identity_mfa_login_enforcement",
    "identity_mfa_okta",
    "identity_mfa_pingid",
    "identity_mfa_totp",
    "identity_oidc",
    "identity_oidc_assignment",
    "identity_oidc_client",
    "identity_oidc_key",
    "identity_oidc_key_allowed_client_id",
    "identity_oidc_provider",
    "identity_oidc_role",
    "identity_oidc_scope",
    "jwt_auth_backend",
    "jwt_auth_backend_role",
    "kmip_secret_backend",
    "kmip_secret_role",
    "kmip_secret_scope",
    "kubernetes_auth_backend_config",
    "kubernetes_auth_backend_role",
    "kubernetes_secret_backend",
    "kubernetes_secret_backend_role",
    "kv_secret",
    "kv_secret_backend_v2",
    "kv_secret_v2",
    "ldap_auth_backend",
    "ldap_auth_backend_group",
    "ldap_auth_backend_user",
    "ldap_secret_backend",
    "ldap_secret_backend_dynamic_role",
    "ldap_secret_backend_library_set",
    "ldap_secret_backend_static_role",
    "managed_keys",
    "mfa_duo",
    "mfa_okta",
    "mfa_pingid",
    "mfa_totp",
    "mongodbatlas_secret_backend",
    "mongodbatlas_secret_role",
    "mount",
    "namespace",
    "nomad_secret_backend",
    "nomad_secret_role",
    "oci_auth_backend",
    "oci_auth_backend_role",
    "okta_auth_backend",
    "okta_auth_backend_group",
    "okta_auth_backend_user",
    "password_policy",
    "pki_secret_backend_acme_eab",
    "pki_secret_backend_cert",
    "pki_secret_backend_config_acme",
    "pki_secret_backend_config_auto_tidy",
    "pki_secret_backend_config_ca",
    "pki_secret_backend_config_cluster",
    "pki_secret_backend_config_cmpv2",
    "pki_secret_backend_config_est",
    "pki_secret_backend_config_issuers",
    "pki_secret_backend_config_scep",
    "pki_secret_backend_config_urls",
    "pki_secret_backend_crl_config",
    "pki_secret_backend_intermediate_cert_request",
    "pki_secret_backend_intermediate_set_signed",
    "pki_secret_backend_issuer",
    "pki_secret_backend_key",
    "pki_secret_backend_role",
    "pki_secret_backend_root_cert",
    "pki_secret_backend_root_sign_intermediate",
    "pki_secret_backend_sign",
    "plugin",
    "plugin_pinned_version",
    "policy",
    "provider",
    "quota_lease_count",
    "quota_rate_limit",
    "rabbitmq_secret_backend",
    "rabbitmq_secret_backend_role",
    "raft_autopilot",
    "raft_snapshot_agent_config",
    "rgp_policy",
    "saml_auth_backend",
    "saml_auth_backend_role",
    "scep_auth_backend_role",
    "secrets_sync_association",
    "secrets_sync_aws_destination",
    "secrets_sync_azure_destination",
    "secrets_sync_config",
    "secrets_sync_gcp_destination",
    "secrets_sync_gh_destination",
    "secrets_sync_github_apps",
    "secrets_sync_vercel_destination",
    "ssh_secret_backend_ca",
    "ssh_secret_backend_role",
    "terraform_cloud_secret_backend",
    "terraform_cloud_secret_creds",
    "terraform_cloud_secret_role",
    "token",
    "token_auth_backend_role",
    "transform_alphabet",
    "transform_role",
    "transform_template",
    "transform_transformation",
    "transit_secret_backend_key",
    "transit_secret_cache_config",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import ad_secret_backend
from . import ad_secret_library
from . import ad_secret_role
from . import alicloud_auth_backend_role
from . import approle_auth_backend_login
from . import approle_auth_backend_role
from . import approle_auth_backend_role_secret_id
from . import audit
from . import audit_request_header
from . import auth_backend
from . import aws_auth_backend_cert
from . import aws_auth_backend_client
from . import aws_auth_backend_config_identity
from . import aws_auth_backend_identity_whitelist
from . import aws_auth_backend_login
from . import aws_auth_backend_role
from . import aws_auth_backend_role_tag
from . import aws_auth_backend_roletag_blacklist
from . import aws_auth_backend_sts_role
from . import aws_secret_backend
from . import aws_secret_backend_role
from . import aws_secret_backend_static_role
from . import azure_auth_backend_config
from . import azure_auth_backend_role
from . import azure_secret_backend
from . import azure_secret_backend_role
from . import cert_auth_backend_role
from . import config_ui_custom_message
from . import consul_secret_backend
from . import consul_secret_backend_role
from . import data_vault_ad_access_credentials
from . import data_vault_approle_auth_backend_role_id
from . import data_vault_auth_backend
from . import data_vault_auth_backends
from . import data_vault_aws_access_credentials
from . import data_vault_aws_static_access_credentials
from . import data_vault_azure_access_credentials
from . import data_vault_gcp_auth_backend_role
from . import data_vault_generic_secret
from . import data_vault_identity_entity
from . import data_vault_identity_group
from . import data_vault_identity_oidc_client_creds
from . import data_vault_identity_oidc_openid_config
from . import data_vault_identity_oidc_public_keys
from . import data_vault_kubernetes_auth_backend_config
from . import data_vault_kubernetes_auth_backend_role
from . import data_vault_kubernetes_service_account_token
from . import data_vault_kv_secret
from . import data_vault_kv_secret_subkeys_v2
from . import data_vault_kv_secret_v2
from . import data_vault_kv_secrets_list
from . import data_vault_kv_secrets_list_v2
from . import data_vault_ldap_dynamic_credentials
from . import data_vault_ldap_static_credentials
from . import data_vault_namespace
from . import data_vault_namespaces
from . import data_vault_nomad_access_token
from . import data_vault_pki_secret_backend_cert_metadata
from . import data_vault_pki_secret_backend_config_cmpv2
from . import data_vault_pki_secret_backend_config_est
from . import data_vault_pki_secret_backend_config_scep
from . import data_vault_pki_secret_backend_issuer
from . import data_vault_pki_secret_backend_issuers
from . import data_vault_pki_secret_backend_key
from . import data_vault_pki_secret_backend_keys
from . import data_vault_policy_document
from . import data_vault_raft_autopilot_state
from . import data_vault_ssh_secret_backend_sign
from . import data_vault_transform_decode
from . import data_vault_transform_encode
from . import data_vault_transit_cmac
from . import data_vault_transit_decrypt
from . import data_vault_transit_encrypt
from . import data_vault_transit_sign
from . import data_vault_transit_verify
from . import database_secret_backend_connection
from . import database_secret_backend_role
from . import database_secret_backend_static_role
from . import database_secrets_mount
from . import egp_policy
from . import gcp_auth_backend
from . import gcp_auth_backend_role
from . import gcp_secret_backend
from . import gcp_secret_impersonated_account
from . import gcp_secret_roleset
from . import gcp_secret_static_account
from . import generic_endpoint
from . import generic_secret
from . import github_auth_backend
from . import github_team
from . import github_user
from . import identity_entity
from . import identity_entity_alias
from . import identity_entity_policies
from . import identity_group
from . import identity_group_alias
from . import identity_group_member_entity_ids
from . import identity_group_member_group_ids
from . import identity_group_policies
from . import identity_mfa_duo
from . import identity_mfa_login_enforcement
from . import identity_mfa_okta
from . import identity_mfa_pingid
from . import identity_mfa_totp
from . import identity_oidc
from . import identity_oidc_assignment
from . import identity_oidc_client
from . import identity_oidc_key
from . import identity_oidc_key_allowed_client_id
from . import identity_oidc_provider
from . import identity_oidc_role
from . import identity_oidc_scope
from . import jwt_auth_backend
from . import jwt_auth_backend_role
from . import kmip_secret_backend
from . import kmip_secret_role
from . import kmip_secret_scope
from . import kubernetes_auth_backend_config
from . import kubernetes_auth_backend_role
from . import kubernetes_secret_backend
from . import kubernetes_secret_backend_role
from . import kv_secret
from . import kv_secret_backend_v2
from . import kv_secret_v2
from . import ldap_auth_backend
from . import ldap_auth_backend_group
from . import ldap_auth_backend_user
from . import ldap_secret_backend
from . import ldap_secret_backend_dynamic_role
from . import ldap_secret_backend_library_set
from . import ldap_secret_backend_static_role
from . import managed_keys
from . import mfa_duo
from . import mfa_okta
from . import mfa_pingid
from . import mfa_totp
from . import mongodbatlas_secret_backend
from . import mongodbatlas_secret_role
from . import mount
from . import namespace
from . import nomad_secret_backend
from . import nomad_secret_role
from . import oci_auth_backend
from . import oci_auth_backend_role
from . import okta_auth_backend
from . import okta_auth_backend_group
from . import okta_auth_backend_user
from . import password_policy
from . import pki_secret_backend_acme_eab
from . import pki_secret_backend_cert
from . import pki_secret_backend_config_acme
from . import pki_secret_backend_config_auto_tidy
from . import pki_secret_backend_config_ca
from . import pki_secret_backend_config_cluster
from . import pki_secret_backend_config_cmpv2
from . import pki_secret_backend_config_est
from . import pki_secret_backend_config_issuers
from . import pki_secret_backend_config_scep
from . import pki_secret_backend_config_urls
from . import pki_secret_backend_crl_config
from . import pki_secret_backend_intermediate_cert_request
from . import pki_secret_backend_intermediate_set_signed
from . import pki_secret_backend_issuer
from . import pki_secret_backend_key
from . import pki_secret_backend_role
from . import pki_secret_backend_root_cert
from . import pki_secret_backend_root_sign_intermediate
from . import pki_secret_backend_sign
from . import plugin
from . import plugin_pinned_version
from . import policy
from . import provider
from . import quota_lease_count
from . import quota_rate_limit
from . import rabbitmq_secret_backend
from . import rabbitmq_secret_backend_role
from . import raft_autopilot
from . import raft_snapshot_agent_config
from . import rgp_policy
from . import saml_auth_backend
from . import saml_auth_backend_role
from . import scep_auth_backend_role
from . import secrets_sync_association
from . import secrets_sync_aws_destination
from . import secrets_sync_azure_destination
from . import secrets_sync_config
from . import secrets_sync_gcp_destination
from . import secrets_sync_gh_destination
from . import secrets_sync_github_apps
from . import secrets_sync_vercel_destination
from . import ssh_secret_backend_ca
from . import ssh_secret_backend_role
from . import terraform_cloud_secret_backend
from . import terraform_cloud_secret_creds
from . import terraform_cloud_secret_role
from . import token
from . import token_auth_backend_role
from . import transform_alphabet
from . import transform_role
from . import transform_template
from . import transform_transformation
from . import transit_secret_backend_key
from . import transit_secret_cache_config
