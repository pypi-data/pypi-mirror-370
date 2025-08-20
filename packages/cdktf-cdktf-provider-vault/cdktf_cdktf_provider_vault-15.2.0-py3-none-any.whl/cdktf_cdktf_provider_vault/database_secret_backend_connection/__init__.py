r'''
# `vault_database_secret_backend_connection`

Refer to the Terraform Registry for docs: [`vault_database_secret_backend_connection`](https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection).
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


class DatabaseSecretBackendConnection(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnection",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection vault_database_secret_backend_connection}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backend: builtins.str,
        name: builtins.str,
        allowed_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        cassandra: typing.Optional[typing.Union["DatabaseSecretBackendConnectionCassandra", typing.Dict[builtins.str, typing.Any]]] = None,
        couchbase: typing.Optional[typing.Union["DatabaseSecretBackendConnectionCouchbase", typing.Dict[builtins.str, typing.Any]]] = None,
        data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        elasticsearch: typing.Optional[typing.Union["DatabaseSecretBackendConnectionElasticsearch", typing.Dict[builtins.str, typing.Any]]] = None,
        hana: typing.Optional[typing.Union["DatabaseSecretBackendConnectionHana", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        influxdb: typing.Optional[typing.Union["DatabaseSecretBackendConnectionInfluxdb", typing.Dict[builtins.str, typing.Any]]] = None,
        mongodb: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMongodb", typing.Dict[builtins.str, typing.Any]]] = None,
        mongodbatlas: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMongodbatlas", typing.Dict[builtins.str, typing.Any]]] = None,
        mssql: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMssql", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysql", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_aurora: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysqlAurora", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_legacy: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysqlLegacy", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_rds: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysqlRds", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        oracle: typing.Optional[typing.Union["DatabaseSecretBackendConnectionOracle", typing.Dict[builtins.str, typing.Any]]] = None,
        plugin_name: typing.Optional[builtins.str] = None,
        postgresql: typing.Optional[typing.Union["DatabaseSecretBackendConnectionPostgresql", typing.Dict[builtins.str, typing.Any]]] = None,
        redis: typing.Optional[typing.Union["DatabaseSecretBackendConnectionRedis", typing.Dict[builtins.str, typing.Any]]] = None,
        redis_elasticache: typing.Optional[typing.Union["DatabaseSecretBackendConnectionRedisElasticache", typing.Dict[builtins.str, typing.Any]]] = None,
        redshift: typing.Optional[typing.Union["DatabaseSecretBackendConnectionRedshift", typing.Dict[builtins.str, typing.Any]]] = None,
        root_rotation_statements: typing.Optional[typing.Sequence[builtins.str]] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        snowflake: typing.Optional[typing.Union["DatabaseSecretBackendConnectionSnowflake", typing.Dict[builtins.str, typing.Any]]] = None,
        verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection vault_database_secret_backend_connection} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backend: Unique name of the Vault mount to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#backend DatabaseSecretBackendConnection#backend}
        :param name: Name of the database connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#name DatabaseSecretBackendConnection#name}
        :param allowed_roles: A list of roles that are allowed to use this connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#allowed_roles DatabaseSecretBackendConnection#allowed_roles}
        :param cassandra: cassandra block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#cassandra DatabaseSecretBackendConnection#cassandra}
        :param couchbase: couchbase block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#couchbase DatabaseSecretBackendConnection#couchbase}
        :param data: A map of sensitive data to pass to the endpoint. Useful for templated connection strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#data DatabaseSecretBackendConnection#data}
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_automated_rotation DatabaseSecretBackendConnection#disable_automated_rotation}
        :param elasticsearch: elasticsearch block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#elasticsearch DatabaseSecretBackendConnection#elasticsearch}
        :param hana: hana block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hana DatabaseSecretBackendConnection#hana}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#id DatabaseSecretBackendConnection#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param influxdb: influxdb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#influxdb DatabaseSecretBackendConnection#influxdb}
        :param mongodb: mongodb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mongodb DatabaseSecretBackendConnection#mongodb}
        :param mongodbatlas: mongodbatlas block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mongodbatlas DatabaseSecretBackendConnection#mongodbatlas}
        :param mssql: mssql block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mssql DatabaseSecretBackendConnection#mssql}
        :param mysql: mysql block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql DatabaseSecretBackendConnection#mysql}
        :param mysql_aurora: mysql_aurora block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_aurora DatabaseSecretBackendConnection#mysql_aurora}
        :param mysql_legacy: mysql_legacy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_legacy DatabaseSecretBackendConnection#mysql_legacy}
        :param mysql_rds: mysql_rds block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_rds DatabaseSecretBackendConnection#mysql_rds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#namespace DatabaseSecretBackendConnection#namespace}
        :param oracle: oracle block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#oracle DatabaseSecretBackendConnection#oracle}
        :param plugin_name: Specifies the name of the plugin to use for this connection. Must be prefixed with the name of one of the supported database engine types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#plugin_name DatabaseSecretBackendConnection#plugin_name}
        :param postgresql: postgresql block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#postgresql DatabaseSecretBackendConnection#postgresql}
        :param redis: redis block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redis DatabaseSecretBackendConnection#redis}
        :param redis_elasticache: redis_elasticache block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redis_elasticache DatabaseSecretBackendConnection#redis_elasticache}
        :param redshift: redshift block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redshift DatabaseSecretBackendConnection#redshift}
        :param root_rotation_statements: A list of database statements to be executed to rotate the root user's credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#root_rotation_statements DatabaseSecretBackendConnection#root_rotation_statements}
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_period DatabaseSecretBackendConnection#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_schedule DatabaseSecretBackendConnection#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_window DatabaseSecretBackendConnection#rotation_window}
        :param snowflake: snowflake block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#snowflake DatabaseSecretBackendConnection#snowflake}
        :param verify_connection: Specifies if the connection is verified during initial configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#verify_connection DatabaseSecretBackendConnection#verify_connection}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c0d5a3815da3620665ede1bbb53a54944253da2a56e46e4dd6fe2d95077ff35)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabaseSecretBackendConnectionConfig(
            backend=backend,
            name=name,
            allowed_roles=allowed_roles,
            cassandra=cassandra,
            couchbase=couchbase,
            data=data,
            disable_automated_rotation=disable_automated_rotation,
            elasticsearch=elasticsearch,
            hana=hana,
            id=id,
            influxdb=influxdb,
            mongodb=mongodb,
            mongodbatlas=mongodbatlas,
            mssql=mssql,
            mysql=mysql,
            mysql_aurora=mysql_aurora,
            mysql_legacy=mysql_legacy,
            mysql_rds=mysql_rds,
            namespace=namespace,
            oracle=oracle,
            plugin_name=plugin_name,
            postgresql=postgresql,
            redis=redis,
            redis_elasticache=redis_elasticache,
            redshift=redshift,
            root_rotation_statements=root_rotation_statements,
            rotation_period=rotation_period,
            rotation_schedule=rotation_schedule,
            rotation_window=rotation_window,
            snowflake=snowflake,
            verify_connection=verify_connection,
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
        '''Generates CDKTF code for importing a DatabaseSecretBackendConnection resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseSecretBackendConnection to import.
        :param import_from_id: The id of the existing DatabaseSecretBackendConnection that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseSecretBackendConnection to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1ea2afca1cc665b5faa92b1257a0a9f5c3e22ca11e89069adbe96b7d508deb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCassandra")
    def put_cassandra(
        self,
        *,
        connect_timeout: typing.Optional[jsii.Number] = None,
        hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        password: typing.Optional[builtins.str] = None,
        pem_bundle: typing.Optional[builtins.str] = None,
        pem_json: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        protocol_version: typing.Optional[jsii.Number] = None,
        skip_verification: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connect_timeout: The number of seconds to use as a connection timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connect_timeout DatabaseSecretBackendConnection#connect_timeout}
        :param hosts: Cassandra hosts to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hosts DatabaseSecretBackendConnection#hosts}
        :param insecure_tls: Whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param password: The password to use when authenticating with Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param pem_bundle: Concatenated PEM blocks containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_bundle DatabaseSecretBackendConnection#pem_bundle}
        :param pem_json: Specifies JSON containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_json DatabaseSecretBackendConnection#pem_json}
        :param port: The transport port to use to connect to Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        :param protocol_version: The CQL protocol version to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#protocol_version DatabaseSecretBackendConnection#protocol_version}
        :param skip_verification: Skip permissions checks when a connection to Cassandra is first created. These checks ensure that Vault is able to create roles, but can be resource intensive in clusters with many roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#skip_verification DatabaseSecretBackendConnection#skip_verification}
        :param tls: Whether to use TLS when connecting to Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        :param username: The username to use when authenticating with Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        value = DatabaseSecretBackendConnectionCassandra(
            connect_timeout=connect_timeout,
            hosts=hosts,
            insecure_tls=insecure_tls,
            password=password,
            pem_bundle=pem_bundle,
            pem_json=pem_json,
            port=port,
            protocol_version=protocol_version,
            skip_verification=skip_verification,
            tls=tls,
            username=username,
        )

        return typing.cast(None, jsii.invoke(self, "putCassandra", [value]))

    @jsii.member(jsii_name="putCouchbase")
    def put_couchbase(
        self,
        *,
        hosts: typing.Sequence[builtins.str],
        password: builtins.str,
        username: builtins.str,
        base64_pem: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosts: A set of Couchbase URIs to connect to. Must use ``couchbases://`` scheme if ``tls`` is ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hosts DatabaseSecretBackendConnection#hosts}
        :param password: Specifies the password corresponding to the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param username: Specifies the username for Vault to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param base64_pem: Required if ``tls`` is ``true``. Specifies the certificate authority of the Couchbase server, as a PEM certificate that has been base64 encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#base64_pem DatabaseSecretBackendConnection#base64_pem}
        :param bucket_name: Required for Couchbase versions prior to 6.5.0. This is only used to verify vault's connection to the server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#bucket_name DatabaseSecretBackendConnection#bucket_name}
        :param insecure_tls: Specifies whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param tls: Specifies whether to use TLS when connecting to Couchbase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionCouchbase(
            hosts=hosts,
            password=password,
            username=username,
            base64_pem=base64_pem,
            bucket_name=bucket_name,
            insecure_tls=insecure_tls,
            tls=tls,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putCouchbase", [value]))

    @jsii.member(jsii_name="putElasticsearch")
    def put_elasticsearch(
        self,
        *,
        password: builtins.str,
        url: builtins.str,
        username: builtins.str,
        ca_cert: typing.Optional[builtins.str] = None,
        ca_path: typing.Optional[builtins.str] = None,
        client_cert: typing.Optional[builtins.str] = None,
        client_key: typing.Optional[builtins.str] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_server_name: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param password: The password to be used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param url: The URL for Elasticsearch's API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#url DatabaseSecretBackendConnection#url}
        :param username: The username to be used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param ca_cert: The path to a PEM-encoded CA cert file to use to verify the Elasticsearch server's identity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_cert DatabaseSecretBackendConnection#ca_cert}
        :param ca_path: The path to a directory of PEM-encoded CA cert files to use to verify the Elasticsearch server's identity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_path DatabaseSecretBackendConnection#ca_path}
        :param client_cert: The path to the certificate for the Elasticsearch client to present for communication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#client_cert DatabaseSecretBackendConnection#client_cert}
        :param client_key: The path to the key for the Elasticsearch client to use for communication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#client_key DatabaseSecretBackendConnection#client_key}
        :param insecure: Whether to disable certificate verification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure DatabaseSecretBackendConnection#insecure}
        :param tls_server_name: This, if set, is used to set the SNI host when connecting via TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_server_name DatabaseSecretBackendConnection#tls_server_name}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionElasticsearch(
            password=password,
            url=url,
            username=username,
            ca_cert=ca_cert,
            ca_path=ca_path,
            client_cert=client_cert,
            client_key=client_key,
            insecure=insecure,
            tls_server_name=tls_server_name,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putElasticsearch", [value]))

    @jsii.member(jsii_name="putHana")
    def put_hana(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        value = DatabaseSecretBackendConnectionHana(
            connection_url=connection_url,
            disable_escaping=disable_escaping,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            username=username,
        )

        return typing.cast(None, jsii.invoke(self, "putHana", [value]))

    @jsii.member(jsii_name="putInfluxdb")
    def put_influxdb(
        self,
        *,
        host: builtins.str,
        password: builtins.str,
        username: builtins.str,
        connect_timeout: typing.Optional[jsii.Number] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pem_bundle: typing.Optional[builtins.str] = None,
        pem_json: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host: Influxdb host to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#host DatabaseSecretBackendConnection#host}
        :param password: Specifies the password corresponding to the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param username: Specifies the username to use for superuser access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param connect_timeout: The number of seconds to use as a connection timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connect_timeout DatabaseSecretBackendConnection#connect_timeout}
        :param insecure_tls: Whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param pem_bundle: Concatenated PEM blocks containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_bundle DatabaseSecretBackendConnection#pem_bundle}
        :param pem_json: Specifies JSON containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_json DatabaseSecretBackendConnection#pem_json}
        :param port: The transport port to use to connect to Influxdb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        :param tls: Whether to use TLS when connecting to Influxdb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionInfluxdb(
            host=host,
            password=password,
            username=username,
            connect_timeout=connect_timeout,
            insecure_tls=insecure_tls,
            pem_bundle=pem_bundle,
            pem_json=pem_json,
            port=port,
            tls=tls,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putInfluxdb", [value]))

    @jsii.member(jsii_name="putMongodb")
    def put_mongodb(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionMongodb(
            connection_url=connection_url,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putMongodb", [value]))

    @jsii.member(jsii_name="putMongodbatlas")
    def put_mongodbatlas(
        self,
        *,
        private_key: builtins.str,
        project_id: builtins.str,
        public_key: builtins.str,
    ) -> None:
        '''
        :param private_key: The Private Programmatic API Key used to connect with MongoDB Atlas API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key DatabaseSecretBackendConnection#private_key}
        :param project_id: The Project ID the Database User should be created within. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#project_id DatabaseSecretBackendConnection#project_id}
        :param public_key: The Public Programmatic API Key used to authenticate with the MongoDB Atlas API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#public_key DatabaseSecretBackendConnection#public_key}
        '''
        value = DatabaseSecretBackendConnectionMongodbatlas(
            private_key=private_key, project_id=project_id, public_key=public_key
        )

        return typing.cast(None, jsii.invoke(self, "putMongodbatlas", [value]))

    @jsii.member(jsii_name="putMssql")
    def put_mssql(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        contained_db: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param contained_db: Set to true when the target is a Contained Database, e.g. AzureSQL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#contained_db DatabaseSecretBackendConnection#contained_db}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionMssql(
            connection_url=connection_url,
            contained_db=contained_db,
            disable_escaping=disable_escaping,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putMssql", [value]))

    @jsii.member(jsii_name="putMysql")
    def put_mysql(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionMysql(
            auth_type=auth_type,
            connection_url=connection_url,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            service_account_json=service_account_json,
            tls_ca=tls_ca,
            tls_certificate_key=tls_certificate_key,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putMysql", [value]))

    @jsii.member(jsii_name="putMysqlAurora")
    def put_mysql_aurora(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionMysqlAurora(
            auth_type=auth_type,
            connection_url=connection_url,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            service_account_json=service_account_json,
            tls_ca=tls_ca,
            tls_certificate_key=tls_certificate_key,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putMysqlAurora", [value]))

    @jsii.member(jsii_name="putMysqlLegacy")
    def put_mysql_legacy(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionMysqlLegacy(
            auth_type=auth_type,
            connection_url=connection_url,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            service_account_json=service_account_json,
            tls_ca=tls_ca,
            tls_certificate_key=tls_certificate_key,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putMysqlLegacy", [value]))

    @jsii.member(jsii_name="putMysqlRds")
    def put_mysql_rds(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionMysqlRds(
            auth_type=auth_type,
            connection_url=connection_url,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            service_account_json=service_account_json,
            tls_ca=tls_ca,
            tls_certificate_key=tls_certificate_key,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putMysqlRds", [value]))

    @jsii.member(jsii_name="putOracle")
    def put_oracle(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        disconnect_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        split_statements: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disconnect_sessions: Set to true to disconnect any open sessions prior to running the revocation statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disconnect_sessions DatabaseSecretBackendConnection#disconnect_sessions}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param split_statements: Set to true in order to split statements after semi-colons. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#split_statements DatabaseSecretBackendConnection#split_statements}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionOracle(
            connection_url=connection_url,
            disconnect_sessions=disconnect_sessions,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            split_statements=split_statements,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putOracle", [value]))

    @jsii.member(jsii_name="putPostgresql")
    def put_postgresql(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_authentication: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        private_key: typing.Optional[builtins.str] = None,
        self_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_authentication: When set to ``scram-sha-256``, passwords will be hashed by Vault before being sent to PostgreSQL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_authentication DatabaseSecretBackendConnection#password_authentication}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param private_key: The secret key used for the x509 client certificate. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key DatabaseSecretBackendConnection#private_key}
        :param self_managed: If set, allows onboarding static roles with a rootless connection configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#self_managed DatabaseSecretBackendConnection#self_managed}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: The x509 CA file for validating the certificate presented by the PostgreSQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate: The x509 client certificate for connecting to the database. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate DatabaseSecretBackendConnection#tls_certificate}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionPostgresql(
            auth_type=auth_type,
            connection_url=connection_url,
            disable_escaping=disable_escaping,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_authentication=password_authentication,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            private_key=private_key,
            self_managed=self_managed,
            service_account_json=service_account_json,
            tls_ca=tls_ca,
            tls_certificate=tls_certificate,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putPostgresql", [value]))

    @jsii.member(jsii_name="putRedis")
    def put_redis(
        self,
        *,
        host: builtins.str,
        password: builtins.str,
        username: builtins.str,
        ca_cert: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        port: typing.Optional[jsii.Number] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param host: Specifies the host to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#host DatabaseSecretBackendConnection#host}
        :param password: Specifies the password corresponding to the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param username: Specifies the username for Vault to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param ca_cert: The contents of a PEM-encoded CA cert file to use to verify the Redis server's identity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_cert DatabaseSecretBackendConnection#ca_cert}
        :param insecure_tls: Specifies whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param port: The transport port to use to connect to Redis. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        :param tls: Specifies whether to use TLS when connecting to Redis. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        '''
        value = DatabaseSecretBackendConnectionRedis(
            host=host,
            password=password,
            username=username,
            ca_cert=ca_cert,
            insecure_tls=insecure_tls,
            port=port,
            tls=tls,
        )

        return typing.cast(None, jsii.invoke(self, "putRedis", [value]))

    @jsii.member(jsii_name="putRedisElasticache")
    def put_redis_elasticache(
        self,
        *,
        url: builtins.str,
        password: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param url: The configuration endpoint for the ElastiCache cluster to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#url DatabaseSecretBackendConnection#url}
        :param password: The AWS secret key id to use to talk to ElastiCache. If omitted the credentials chain provider is used instead. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param region: The AWS region where the ElastiCache cluster is hosted. If omitted the plugin tries to infer the region from the environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#region DatabaseSecretBackendConnection#region}
        :param username: The AWS access key id to use to talk to ElastiCache. If omitted the credentials chain provider is used instead. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        value = DatabaseSecretBackendConnectionRedisElasticache(
            url=url, password=password, region=region, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putRedisElasticache", [value]))

    @jsii.member(jsii_name="putRedshift")
    def put_redshift(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionRedshift(
            connection_url=connection_url,
            disable_escaping=disable_escaping,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putRedshift", [value]))

    @jsii.member(jsii_name="putSnowflake")
    def put_snowflake(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        private_key_wo: typing.Optional[builtins.str] = None,
        private_key_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param private_key_wo: The private key configured for the admin user in Snowflake. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key_wo DatabaseSecretBackendConnection#private_key_wo}
        :param private_key_wo_version: Version counter for the private key key-pair credentials write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key_wo_version DatabaseSecretBackendConnection#private_key_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        value = DatabaseSecretBackendConnectionSnowflake(
            connection_url=connection_url,
            max_connection_lifetime=max_connection_lifetime,
            max_idle_connections=max_idle_connections,
            max_open_connections=max_open_connections,
            password=password,
            password_wo=password_wo,
            password_wo_version=password_wo_version,
            private_key_wo=private_key_wo,
            private_key_wo_version=private_key_wo_version,
            username=username,
            username_template=username_template,
        )

        return typing.cast(None, jsii.invoke(self, "putSnowflake", [value]))

    @jsii.member(jsii_name="resetAllowedRoles")
    def reset_allowed_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedRoles", []))

    @jsii.member(jsii_name="resetCassandra")
    def reset_cassandra(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCassandra", []))

    @jsii.member(jsii_name="resetCouchbase")
    def reset_couchbase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCouchbase", []))

    @jsii.member(jsii_name="resetData")
    def reset_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetData", []))

    @jsii.member(jsii_name="resetDisableAutomatedRotation")
    def reset_disable_automated_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableAutomatedRotation", []))

    @jsii.member(jsii_name="resetElasticsearch")
    def reset_elasticsearch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticsearch", []))

    @jsii.member(jsii_name="resetHana")
    def reset_hana(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHana", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInfluxdb")
    def reset_influxdb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInfluxdb", []))

    @jsii.member(jsii_name="resetMongodb")
    def reset_mongodb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodb", []))

    @jsii.member(jsii_name="resetMongodbatlas")
    def reset_mongodbatlas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbatlas", []))

    @jsii.member(jsii_name="resetMssql")
    def reset_mssql(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMssql", []))

    @jsii.member(jsii_name="resetMysql")
    def reset_mysql(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMysql", []))

    @jsii.member(jsii_name="resetMysqlAurora")
    def reset_mysql_aurora(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMysqlAurora", []))

    @jsii.member(jsii_name="resetMysqlLegacy")
    def reset_mysql_legacy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMysqlLegacy", []))

    @jsii.member(jsii_name="resetMysqlRds")
    def reset_mysql_rds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMysqlRds", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetOracle")
    def reset_oracle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracle", []))

    @jsii.member(jsii_name="resetPluginName")
    def reset_plugin_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginName", []))

    @jsii.member(jsii_name="resetPostgresql")
    def reset_postgresql(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresql", []))

    @jsii.member(jsii_name="resetRedis")
    def reset_redis(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedis", []))

    @jsii.member(jsii_name="resetRedisElasticache")
    def reset_redis_elasticache(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedisElasticache", []))

    @jsii.member(jsii_name="resetRedshift")
    def reset_redshift(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshift", []))

    @jsii.member(jsii_name="resetRootRotationStatements")
    def reset_root_rotation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootRotationStatements", []))

    @jsii.member(jsii_name="resetRotationPeriod")
    def reset_rotation_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationPeriod", []))

    @jsii.member(jsii_name="resetRotationSchedule")
    def reset_rotation_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationSchedule", []))

    @jsii.member(jsii_name="resetRotationWindow")
    def reset_rotation_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationWindow", []))

    @jsii.member(jsii_name="resetSnowflake")
    def reset_snowflake(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnowflake", []))

    @jsii.member(jsii_name="resetVerifyConnection")
    def reset_verify_connection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyConnection", []))

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
    @jsii.member(jsii_name="cassandra")
    def cassandra(self) -> "DatabaseSecretBackendConnectionCassandraOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionCassandraOutputReference", jsii.get(self, "cassandra"))

    @builtins.property
    @jsii.member(jsii_name="couchbase")
    def couchbase(self) -> "DatabaseSecretBackendConnectionCouchbaseOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionCouchbaseOutputReference", jsii.get(self, "couchbase"))

    @builtins.property
    @jsii.member(jsii_name="elasticsearch")
    def elasticsearch(
        self,
    ) -> "DatabaseSecretBackendConnectionElasticsearchOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionElasticsearchOutputReference", jsii.get(self, "elasticsearch"))

    @builtins.property
    @jsii.member(jsii_name="hana")
    def hana(self) -> "DatabaseSecretBackendConnectionHanaOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionHanaOutputReference", jsii.get(self, "hana"))

    @builtins.property
    @jsii.member(jsii_name="influxdb")
    def influxdb(self) -> "DatabaseSecretBackendConnectionInfluxdbOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionInfluxdbOutputReference", jsii.get(self, "influxdb"))

    @builtins.property
    @jsii.member(jsii_name="mongodb")
    def mongodb(self) -> "DatabaseSecretBackendConnectionMongodbOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMongodbOutputReference", jsii.get(self, "mongodb"))

    @builtins.property
    @jsii.member(jsii_name="mongodbatlas")
    def mongodbatlas(
        self,
    ) -> "DatabaseSecretBackendConnectionMongodbatlasOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMongodbatlasOutputReference", jsii.get(self, "mongodbatlas"))

    @builtins.property
    @jsii.member(jsii_name="mssql")
    def mssql(self) -> "DatabaseSecretBackendConnectionMssqlOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMssqlOutputReference", jsii.get(self, "mssql"))

    @builtins.property
    @jsii.member(jsii_name="mysql")
    def mysql(self) -> "DatabaseSecretBackendConnectionMysqlOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMysqlOutputReference", jsii.get(self, "mysql"))

    @builtins.property
    @jsii.member(jsii_name="mysqlAurora")
    def mysql_aurora(
        self,
    ) -> "DatabaseSecretBackendConnectionMysqlAuroraOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMysqlAuroraOutputReference", jsii.get(self, "mysqlAurora"))

    @builtins.property
    @jsii.member(jsii_name="mysqlLegacy")
    def mysql_legacy(
        self,
    ) -> "DatabaseSecretBackendConnectionMysqlLegacyOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMysqlLegacyOutputReference", jsii.get(self, "mysqlLegacy"))

    @builtins.property
    @jsii.member(jsii_name="mysqlRds")
    def mysql_rds(self) -> "DatabaseSecretBackendConnectionMysqlRdsOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionMysqlRdsOutputReference", jsii.get(self, "mysqlRds"))

    @builtins.property
    @jsii.member(jsii_name="oracle")
    def oracle(self) -> "DatabaseSecretBackendConnectionOracleOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionOracleOutputReference", jsii.get(self, "oracle"))

    @builtins.property
    @jsii.member(jsii_name="postgresql")
    def postgresql(self) -> "DatabaseSecretBackendConnectionPostgresqlOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionPostgresqlOutputReference", jsii.get(self, "postgresql"))

    @builtins.property
    @jsii.member(jsii_name="redis")
    def redis(self) -> "DatabaseSecretBackendConnectionRedisOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionRedisOutputReference", jsii.get(self, "redis"))

    @builtins.property
    @jsii.member(jsii_name="redisElasticache")
    def redis_elasticache(
        self,
    ) -> "DatabaseSecretBackendConnectionRedisElasticacheOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionRedisElasticacheOutputReference", jsii.get(self, "redisElasticache"))

    @builtins.property
    @jsii.member(jsii_name="redshift")
    def redshift(self) -> "DatabaseSecretBackendConnectionRedshiftOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionRedshiftOutputReference", jsii.get(self, "redshift"))

    @builtins.property
    @jsii.member(jsii_name="snowflake")
    def snowflake(self) -> "DatabaseSecretBackendConnectionSnowflakeOutputReference":
        return typing.cast("DatabaseSecretBackendConnectionSnowflakeOutputReference", jsii.get(self, "snowflake"))

    @builtins.property
    @jsii.member(jsii_name="allowedRolesInput")
    def allowed_roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="backendInput")
    def backend_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backendInput"))

    @builtins.property
    @jsii.member(jsii_name="cassandraInput")
    def cassandra_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionCassandra"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionCassandra"], jsii.get(self, "cassandraInput"))

    @builtins.property
    @jsii.member(jsii_name="couchbaseInput")
    def couchbase_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionCouchbase"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionCouchbase"], jsii.get(self, "couchbaseInput"))

    @builtins.property
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "dataInput"))

    @builtins.property
    @jsii.member(jsii_name="disableAutomatedRotationInput")
    def disable_automated_rotation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableAutomatedRotationInput"))

    @builtins.property
    @jsii.member(jsii_name="elasticsearchInput")
    def elasticsearch_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionElasticsearch"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionElasticsearch"], jsii.get(self, "elasticsearchInput"))

    @builtins.property
    @jsii.member(jsii_name="hanaInput")
    def hana_input(self) -> typing.Optional["DatabaseSecretBackendConnectionHana"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionHana"], jsii.get(self, "hanaInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="influxdbInput")
    def influxdb_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionInfluxdb"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionInfluxdb"], jsii.get(self, "influxdbInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbatlasInput")
    def mongodbatlas_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMongodbatlas"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMongodbatlas"], jsii.get(self, "mongodbatlasInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbInput")
    def mongodb_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMongodb"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMongodb"], jsii.get(self, "mongodbInput"))

    @builtins.property
    @jsii.member(jsii_name="mssqlInput")
    def mssql_input(self) -> typing.Optional["DatabaseSecretBackendConnectionMssql"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMssql"], jsii.get(self, "mssqlInput"))

    @builtins.property
    @jsii.member(jsii_name="mysqlAuroraInput")
    def mysql_aurora_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMysqlAurora"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysqlAurora"], jsii.get(self, "mysqlAuroraInput"))

    @builtins.property
    @jsii.member(jsii_name="mysqlInput")
    def mysql_input(self) -> typing.Optional["DatabaseSecretBackendConnectionMysql"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysql"], jsii.get(self, "mysqlInput"))

    @builtins.property
    @jsii.member(jsii_name="mysqlLegacyInput")
    def mysql_legacy_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMysqlLegacy"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysqlLegacy"], jsii.get(self, "mysqlLegacyInput"))

    @builtins.property
    @jsii.member(jsii_name="mysqlRdsInput")
    def mysql_rds_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMysqlRds"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysqlRds"], jsii.get(self, "mysqlRdsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleInput")
    def oracle_input(self) -> typing.Optional["DatabaseSecretBackendConnectionOracle"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionOracle"], jsii.get(self, "oracleInput"))

    @builtins.property
    @jsii.member(jsii_name="pluginNameInput")
    def plugin_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginNameInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresqlInput")
    def postgresql_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionPostgresql"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionPostgresql"], jsii.get(self, "postgresqlInput"))

    @builtins.property
    @jsii.member(jsii_name="redisElasticacheInput")
    def redis_elasticache_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionRedisElasticache"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionRedisElasticache"], jsii.get(self, "redisElasticacheInput"))

    @builtins.property
    @jsii.member(jsii_name="redisInput")
    def redis_input(self) -> typing.Optional["DatabaseSecretBackendConnectionRedis"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionRedis"], jsii.get(self, "redisInput"))

    @builtins.property
    @jsii.member(jsii_name="redshiftInput")
    def redshift_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionRedshift"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionRedshift"], jsii.get(self, "redshiftInput"))

    @builtins.property
    @jsii.member(jsii_name="rootRotationStatementsInput")
    def root_rotation_statements_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rootRotationStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationPeriodInput")
    def rotation_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationScheduleInput")
    def rotation_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationWindowInput")
    def rotation_window_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationWindowInput"))

    @builtins.property
    @jsii.member(jsii_name="snowflakeInput")
    def snowflake_input(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionSnowflake"]:
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionSnowflake"], jsii.get(self, "snowflakeInput"))

    @builtins.property
    @jsii.member(jsii_name="verifyConnectionInput")
    def verify_connection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "verifyConnectionInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedRoles")
    def allowed_roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedRoles"))

    @allowed_roles.setter
    def allowed_roles(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51c72012b9fbf2ab2ee5c91b0869b41784cdecd72e1ca9990cfce59d761c3304)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedRoles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backend")
    def backend(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backend"))

    @backend.setter
    def backend(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__372aa857104a1bcfe00934a3a63842629991b1bf1bdc18332646d6b1026f3742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backend", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "data"))

    @data.setter
    def data(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__847456513cb6417549e9279b019915ae1d669e7462a5a457709d77b57604a539)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "data", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableAutomatedRotation")
    def disable_automated_rotation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableAutomatedRotation"))

    @disable_automated_rotation.setter
    def disable_automated_rotation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__259872f41940672b2d1d3449a3216d2fcfc30c8e613bf37f07ec4e71b344505b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableAutomatedRotation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d5d7b8e5503227724608cab8e42f6945a211f970b21ef210ff536c7475ac9f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75883e892b7b08e6e7daa847a2e4104f062b15754c3e58f583e3eed8dec167d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2100f15d57ce41f80b55ee3ff1bf22311cd26ac13c1530c6e38a755d8bf0c8a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginName")
    def plugin_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginName"))

    @plugin_name.setter
    def plugin_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ff326c3ea85b0db935e4a4cc5ff4c1a4bc6bd122ea0ee300676e34cfb015305)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rootRotationStatements")
    def root_rotation_statements(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "rootRotationStatements"))

    @root_rotation_statements.setter
    def root_rotation_statements(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a4f6877fa313b11d07a17c70dd73ca2090ba39fc1e6ad82deefbc659baeebf0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rootRotationStatements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationPeriod")
    def rotation_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationPeriod"))

    @rotation_period.setter
    def rotation_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__462f37ddcf5ed9d5893dd24d1e40952a9ca8c754b49cdd4ee101b0709031f664)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationSchedule")
    def rotation_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationSchedule"))

    @rotation_schedule.setter
    def rotation_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a7b6d14483f5f2f3acfc29ce98c18c51269266f475ff254a1e5976b61000b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rotationWindow")
    def rotation_window(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationWindow"))

    @rotation_window.setter
    def rotation_window(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__889e737b809ac33ac47875ba82011ca305b0f91e3d5a44a64e6783bc0033bb43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationWindow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="verifyConnection")
    def verify_connection(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "verifyConnection"))

    @verify_connection.setter
    def verify_connection(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed522a23a3383e5f557f73263a0ba8138883f42b80cc3875f59d046b52988912)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verifyConnection", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionCassandra",
    jsii_struct_bases=[],
    name_mapping={
        "connect_timeout": "connectTimeout",
        "hosts": "hosts",
        "insecure_tls": "insecureTls",
        "password": "password",
        "pem_bundle": "pemBundle",
        "pem_json": "pemJson",
        "port": "port",
        "protocol_version": "protocolVersion",
        "skip_verification": "skipVerification",
        "tls": "tls",
        "username": "username",
    },
)
class DatabaseSecretBackendConnectionCassandra:
    def __init__(
        self,
        *,
        connect_timeout: typing.Optional[jsii.Number] = None,
        hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        password: typing.Optional[builtins.str] = None,
        pem_bundle: typing.Optional[builtins.str] = None,
        pem_json: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        protocol_version: typing.Optional[jsii.Number] = None,
        skip_verification: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connect_timeout: The number of seconds to use as a connection timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connect_timeout DatabaseSecretBackendConnection#connect_timeout}
        :param hosts: Cassandra hosts to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hosts DatabaseSecretBackendConnection#hosts}
        :param insecure_tls: Whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param password: The password to use when authenticating with Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param pem_bundle: Concatenated PEM blocks containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_bundle DatabaseSecretBackendConnection#pem_bundle}
        :param pem_json: Specifies JSON containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_json DatabaseSecretBackendConnection#pem_json}
        :param port: The transport port to use to connect to Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        :param protocol_version: The CQL protocol version to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#protocol_version DatabaseSecretBackendConnection#protocol_version}
        :param skip_verification: Skip permissions checks when a connection to Cassandra is first created. These checks ensure that Vault is able to create roles, but can be resource intensive in clusters with many roles. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#skip_verification DatabaseSecretBackendConnection#skip_verification}
        :param tls: Whether to use TLS when connecting to Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        :param username: The username to use when authenticating with Cassandra. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16f6bd8ea1ef98b3c22050de90dd6177ebc4e6fb023e09001759d59f1eb13c64)
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument pem_bundle", value=pem_bundle, expected_type=type_hints["pem_bundle"])
            check_type(argname="argument pem_json", value=pem_json, expected_type=type_hints["pem_json"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument protocol_version", value=protocol_version, expected_type=type_hints["protocol_version"])
            check_type(argname="argument skip_verification", value=skip_verification, expected_type=type_hints["skip_verification"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if hosts is not None:
            self._values["hosts"] = hosts
        if insecure_tls is not None:
            self._values["insecure_tls"] = insecure_tls
        if password is not None:
            self._values["password"] = password
        if pem_bundle is not None:
            self._values["pem_bundle"] = pem_bundle
        if pem_json is not None:
            self._values["pem_json"] = pem_json
        if port is not None:
            self._values["port"] = port
        if protocol_version is not None:
            self._values["protocol_version"] = protocol_version
        if skip_verification is not None:
            self._values["skip_verification"] = skip_verification
        if tls is not None:
            self._values["tls"] = tls
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds to use as a connection timeout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connect_timeout DatabaseSecretBackendConnection#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Cassandra hosts to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hosts DatabaseSecretBackendConnection#hosts}
        '''
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to skip verification of the server certificate when using TLS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        '''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The password to use when authenticating with Cassandra.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_bundle(self) -> typing.Optional[builtins.str]:
        '''Concatenated PEM blocks containing a certificate and private key;

        a certificate, private key, and issuing CA certificate; or just a CA certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_bundle DatabaseSecretBackendConnection#pem_bundle}
        '''
        result = self._values.get("pem_bundle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_json(self) -> typing.Optional[builtins.str]:
        '''Specifies JSON containing a certificate and private key;

        a certificate, private key, and issuing CA certificate; or just a CA certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_json DatabaseSecretBackendConnection#pem_json}
        '''
        result = self._values.get("pem_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The transport port to use to connect to Cassandra.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def protocol_version(self) -> typing.Optional[jsii.Number]:
        '''The CQL protocol version to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#protocol_version DatabaseSecretBackendConnection#protocol_version}
        '''
        result = self._values.get("protocol_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def skip_verification(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Skip permissions checks when a connection to Cassandra is first created.

        These checks ensure that Vault is able to create roles, but can be resource intensive in clusters with many roles.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#skip_verification DatabaseSecretBackendConnection#skip_verification}
        '''
        result = self._values.get("skip_verification")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to use TLS when connecting to Cassandra.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The username to use when authenticating with Cassandra.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionCassandra(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionCassandraOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionCassandraOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86930fac2ed6ebb799cd7105d559596aca54946a8d56af307378f5fa228314de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetHosts")
    def reset_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHosts", []))

    @jsii.member(jsii_name="resetInsecureTls")
    def reset_insecure_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureTls", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPemBundle")
    def reset_pem_bundle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemBundle", []))

    @jsii.member(jsii_name="resetPemJson")
    def reset_pem_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemJson", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetProtocolVersion")
    def reset_protocol_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocolVersion", []))

    @jsii.member(jsii_name="resetSkipVerification")
    def reset_skip_verification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipVerification", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="hostsInput")
    def hosts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostsInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureTlsInput")
    def insecure_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureTlsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="pemBundleInput")
    def pem_bundle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemBundleInput"))

    @builtins.property
    @jsii.member(jsii_name="pemJsonInput")
    def pem_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolVersionInput")
    def protocol_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "protocolVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="skipVerificationInput")
    def skip_verification_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipVerificationInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsInput")
    def tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bcd259ce38f8ea1aeaca2d7166d655040ae2a557d149c18724fcced1aea1078)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hosts"))

    @hosts.setter
    def hosts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__278def805539b971174352bd459b2b8787bc0ca32673ac0eb9ea2c62f2065277)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hosts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureTls")
    def insecure_tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecureTls"))

    @insecure_tls.setter
    def insecure_tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0babf0d91766d40ca7f79fe5b829d6574d00ae69e0f53cf2501de05428c70fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__944d0d75386a7144eb3f419a16ba06ccc23e447c165e3b19dd0d6f49d28e02c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemBundle")
    def pem_bundle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemBundle"))

    @pem_bundle.setter
    def pem_bundle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec349756ab880c5b85f6ee81b7d0fd1aae249d225f90ab0fe620ebbd5016bb25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemBundle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemJson")
    def pem_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemJson"))

    @pem_json.setter
    def pem_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692f70aa7a241fc628957f087bba89398747863e4fe8ec42cbcdf7915fd9c321)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a9cc58d526f3af716358ad8126165def7a5c967a2093f241e63146cb3d044ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocolVersion")
    def protocol_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "protocolVersion"))

    @protocol_version.setter
    def protocol_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66bec6e9dc857246e3cdad051454ec5c30850050ee93e0b174c9eaa73e21e07b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocolVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipVerification")
    def skip_verification(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "skipVerification"))

    @skip_verification.setter
    def skip_verification(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c943c28b88b1ea060e503a0d506fa432fce6e3806380f3f4fd9ed0e56487880c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipVerification", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tls")
    def tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tls"))

    @tls.setter
    def tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e049a2ba4817280de17dfa22566e3a797fe2c041aaadae3d8d88249b462ccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__332417dfd8872c211daa4e1e1ba657e7551dbe0f016e176394b281bda7e35fb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionCassandra]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionCassandra], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionCassandra],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__929dad8c507c0daa5a4241909971a10c53d9df716081467fa90f81455fcc3a15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionConfig",
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
        "allowed_roles": "allowedRoles",
        "cassandra": "cassandra",
        "couchbase": "couchbase",
        "data": "data",
        "disable_automated_rotation": "disableAutomatedRotation",
        "elasticsearch": "elasticsearch",
        "hana": "hana",
        "id": "id",
        "influxdb": "influxdb",
        "mongodb": "mongodb",
        "mongodbatlas": "mongodbatlas",
        "mssql": "mssql",
        "mysql": "mysql",
        "mysql_aurora": "mysqlAurora",
        "mysql_legacy": "mysqlLegacy",
        "mysql_rds": "mysqlRds",
        "namespace": "namespace",
        "oracle": "oracle",
        "plugin_name": "pluginName",
        "postgresql": "postgresql",
        "redis": "redis",
        "redis_elasticache": "redisElasticache",
        "redshift": "redshift",
        "root_rotation_statements": "rootRotationStatements",
        "rotation_period": "rotationPeriod",
        "rotation_schedule": "rotationSchedule",
        "rotation_window": "rotationWindow",
        "snowflake": "snowflake",
        "verify_connection": "verifyConnection",
    },
)
class DatabaseSecretBackendConnectionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        cassandra: typing.Optional[typing.Union[DatabaseSecretBackendConnectionCassandra, typing.Dict[builtins.str, typing.Any]]] = None,
        couchbase: typing.Optional[typing.Union["DatabaseSecretBackendConnectionCouchbase", typing.Dict[builtins.str, typing.Any]]] = None,
        data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        elasticsearch: typing.Optional[typing.Union["DatabaseSecretBackendConnectionElasticsearch", typing.Dict[builtins.str, typing.Any]]] = None,
        hana: typing.Optional[typing.Union["DatabaseSecretBackendConnectionHana", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        influxdb: typing.Optional[typing.Union["DatabaseSecretBackendConnectionInfluxdb", typing.Dict[builtins.str, typing.Any]]] = None,
        mongodb: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMongodb", typing.Dict[builtins.str, typing.Any]]] = None,
        mongodbatlas: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMongodbatlas", typing.Dict[builtins.str, typing.Any]]] = None,
        mssql: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMssql", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysql", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_aurora: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysqlAurora", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_legacy: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysqlLegacy", typing.Dict[builtins.str, typing.Any]]] = None,
        mysql_rds: typing.Optional[typing.Union["DatabaseSecretBackendConnectionMysqlRds", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        oracle: typing.Optional[typing.Union["DatabaseSecretBackendConnectionOracle", typing.Dict[builtins.str, typing.Any]]] = None,
        plugin_name: typing.Optional[builtins.str] = None,
        postgresql: typing.Optional[typing.Union["DatabaseSecretBackendConnectionPostgresql", typing.Dict[builtins.str, typing.Any]]] = None,
        redis: typing.Optional[typing.Union["DatabaseSecretBackendConnectionRedis", typing.Dict[builtins.str, typing.Any]]] = None,
        redis_elasticache: typing.Optional[typing.Union["DatabaseSecretBackendConnectionRedisElasticache", typing.Dict[builtins.str, typing.Any]]] = None,
        redshift: typing.Optional[typing.Union["DatabaseSecretBackendConnectionRedshift", typing.Dict[builtins.str, typing.Any]]] = None,
        root_rotation_statements: typing.Optional[typing.Sequence[builtins.str]] = None,
        rotation_period: typing.Optional[jsii.Number] = None,
        rotation_schedule: typing.Optional[builtins.str] = None,
        rotation_window: typing.Optional[jsii.Number] = None,
        snowflake: typing.Optional[typing.Union["DatabaseSecretBackendConnectionSnowflake", typing.Dict[builtins.str, typing.Any]]] = None,
        verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backend: Unique name of the Vault mount to configure. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#backend DatabaseSecretBackendConnection#backend}
        :param name: Name of the database connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#name DatabaseSecretBackendConnection#name}
        :param allowed_roles: A list of roles that are allowed to use this connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#allowed_roles DatabaseSecretBackendConnection#allowed_roles}
        :param cassandra: cassandra block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#cassandra DatabaseSecretBackendConnection#cassandra}
        :param couchbase: couchbase block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#couchbase DatabaseSecretBackendConnection#couchbase}
        :param data: A map of sensitive data to pass to the endpoint. Useful for templated connection strings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#data DatabaseSecretBackendConnection#data}
        :param disable_automated_rotation: Stops rotation of the root credential until set to false. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_automated_rotation DatabaseSecretBackendConnection#disable_automated_rotation}
        :param elasticsearch: elasticsearch block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#elasticsearch DatabaseSecretBackendConnection#elasticsearch}
        :param hana: hana block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hana DatabaseSecretBackendConnection#hana}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#id DatabaseSecretBackendConnection#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param influxdb: influxdb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#influxdb DatabaseSecretBackendConnection#influxdb}
        :param mongodb: mongodb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mongodb DatabaseSecretBackendConnection#mongodb}
        :param mongodbatlas: mongodbatlas block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mongodbatlas DatabaseSecretBackendConnection#mongodbatlas}
        :param mssql: mssql block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mssql DatabaseSecretBackendConnection#mssql}
        :param mysql: mysql block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql DatabaseSecretBackendConnection#mysql}
        :param mysql_aurora: mysql_aurora block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_aurora DatabaseSecretBackendConnection#mysql_aurora}
        :param mysql_legacy: mysql_legacy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_legacy DatabaseSecretBackendConnection#mysql_legacy}
        :param mysql_rds: mysql_rds block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_rds DatabaseSecretBackendConnection#mysql_rds}
        :param namespace: Target namespace. (requires Enterprise). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#namespace DatabaseSecretBackendConnection#namespace}
        :param oracle: oracle block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#oracle DatabaseSecretBackendConnection#oracle}
        :param plugin_name: Specifies the name of the plugin to use for this connection. Must be prefixed with the name of one of the supported database engine types. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#plugin_name DatabaseSecretBackendConnection#plugin_name}
        :param postgresql: postgresql block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#postgresql DatabaseSecretBackendConnection#postgresql}
        :param redis: redis block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redis DatabaseSecretBackendConnection#redis}
        :param redis_elasticache: redis_elasticache block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redis_elasticache DatabaseSecretBackendConnection#redis_elasticache}
        :param redshift: redshift block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redshift DatabaseSecretBackendConnection#redshift}
        :param root_rotation_statements: A list of database statements to be executed to rotate the root user's credentials. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#root_rotation_statements DatabaseSecretBackendConnection#root_rotation_statements}
        :param rotation_period: The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_period DatabaseSecretBackendConnection#rotation_period}
        :param rotation_schedule: The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_schedule DatabaseSecretBackendConnection#rotation_schedule}
        :param rotation_window: The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered. Can only be used with rotation_schedule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_window DatabaseSecretBackendConnection#rotation_window}
        :param snowflake: snowflake block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#snowflake DatabaseSecretBackendConnection#snowflake}
        :param verify_connection: Specifies if the connection is verified during initial configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#verify_connection DatabaseSecretBackendConnection#verify_connection}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cassandra, dict):
            cassandra = DatabaseSecretBackendConnectionCassandra(**cassandra)
        if isinstance(couchbase, dict):
            couchbase = DatabaseSecretBackendConnectionCouchbase(**couchbase)
        if isinstance(elasticsearch, dict):
            elasticsearch = DatabaseSecretBackendConnectionElasticsearch(**elasticsearch)
        if isinstance(hana, dict):
            hana = DatabaseSecretBackendConnectionHana(**hana)
        if isinstance(influxdb, dict):
            influxdb = DatabaseSecretBackendConnectionInfluxdb(**influxdb)
        if isinstance(mongodb, dict):
            mongodb = DatabaseSecretBackendConnectionMongodb(**mongodb)
        if isinstance(mongodbatlas, dict):
            mongodbatlas = DatabaseSecretBackendConnectionMongodbatlas(**mongodbatlas)
        if isinstance(mssql, dict):
            mssql = DatabaseSecretBackendConnectionMssql(**mssql)
        if isinstance(mysql, dict):
            mysql = DatabaseSecretBackendConnectionMysql(**mysql)
        if isinstance(mysql_aurora, dict):
            mysql_aurora = DatabaseSecretBackendConnectionMysqlAurora(**mysql_aurora)
        if isinstance(mysql_legacy, dict):
            mysql_legacy = DatabaseSecretBackendConnectionMysqlLegacy(**mysql_legacy)
        if isinstance(mysql_rds, dict):
            mysql_rds = DatabaseSecretBackendConnectionMysqlRds(**mysql_rds)
        if isinstance(oracle, dict):
            oracle = DatabaseSecretBackendConnectionOracle(**oracle)
        if isinstance(postgresql, dict):
            postgresql = DatabaseSecretBackendConnectionPostgresql(**postgresql)
        if isinstance(redis, dict):
            redis = DatabaseSecretBackendConnectionRedis(**redis)
        if isinstance(redis_elasticache, dict):
            redis_elasticache = DatabaseSecretBackendConnectionRedisElasticache(**redis_elasticache)
        if isinstance(redshift, dict):
            redshift = DatabaseSecretBackendConnectionRedshift(**redshift)
        if isinstance(snowflake, dict):
            snowflake = DatabaseSecretBackendConnectionSnowflake(**snowflake)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0847902127aee9281509569452b51fae959ac561f6c87946ea0c492655092ddb)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backend", value=backend, expected_type=type_hints["backend"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allowed_roles", value=allowed_roles, expected_type=type_hints["allowed_roles"])
            check_type(argname="argument cassandra", value=cassandra, expected_type=type_hints["cassandra"])
            check_type(argname="argument couchbase", value=couchbase, expected_type=type_hints["couchbase"])
            check_type(argname="argument data", value=data, expected_type=type_hints["data"])
            check_type(argname="argument disable_automated_rotation", value=disable_automated_rotation, expected_type=type_hints["disable_automated_rotation"])
            check_type(argname="argument elasticsearch", value=elasticsearch, expected_type=type_hints["elasticsearch"])
            check_type(argname="argument hana", value=hana, expected_type=type_hints["hana"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument influxdb", value=influxdb, expected_type=type_hints["influxdb"])
            check_type(argname="argument mongodb", value=mongodb, expected_type=type_hints["mongodb"])
            check_type(argname="argument mongodbatlas", value=mongodbatlas, expected_type=type_hints["mongodbatlas"])
            check_type(argname="argument mssql", value=mssql, expected_type=type_hints["mssql"])
            check_type(argname="argument mysql", value=mysql, expected_type=type_hints["mysql"])
            check_type(argname="argument mysql_aurora", value=mysql_aurora, expected_type=type_hints["mysql_aurora"])
            check_type(argname="argument mysql_legacy", value=mysql_legacy, expected_type=type_hints["mysql_legacy"])
            check_type(argname="argument mysql_rds", value=mysql_rds, expected_type=type_hints["mysql_rds"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument oracle", value=oracle, expected_type=type_hints["oracle"])
            check_type(argname="argument plugin_name", value=plugin_name, expected_type=type_hints["plugin_name"])
            check_type(argname="argument postgresql", value=postgresql, expected_type=type_hints["postgresql"])
            check_type(argname="argument redis", value=redis, expected_type=type_hints["redis"])
            check_type(argname="argument redis_elasticache", value=redis_elasticache, expected_type=type_hints["redis_elasticache"])
            check_type(argname="argument redshift", value=redshift, expected_type=type_hints["redshift"])
            check_type(argname="argument root_rotation_statements", value=root_rotation_statements, expected_type=type_hints["root_rotation_statements"])
            check_type(argname="argument rotation_period", value=rotation_period, expected_type=type_hints["rotation_period"])
            check_type(argname="argument rotation_schedule", value=rotation_schedule, expected_type=type_hints["rotation_schedule"])
            check_type(argname="argument rotation_window", value=rotation_window, expected_type=type_hints["rotation_window"])
            check_type(argname="argument snowflake", value=snowflake, expected_type=type_hints["snowflake"])
            check_type(argname="argument verify_connection", value=verify_connection, expected_type=type_hints["verify_connection"])
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
        if allowed_roles is not None:
            self._values["allowed_roles"] = allowed_roles
        if cassandra is not None:
            self._values["cassandra"] = cassandra
        if couchbase is not None:
            self._values["couchbase"] = couchbase
        if data is not None:
            self._values["data"] = data
        if disable_automated_rotation is not None:
            self._values["disable_automated_rotation"] = disable_automated_rotation
        if elasticsearch is not None:
            self._values["elasticsearch"] = elasticsearch
        if hana is not None:
            self._values["hana"] = hana
        if id is not None:
            self._values["id"] = id
        if influxdb is not None:
            self._values["influxdb"] = influxdb
        if mongodb is not None:
            self._values["mongodb"] = mongodb
        if mongodbatlas is not None:
            self._values["mongodbatlas"] = mongodbatlas
        if mssql is not None:
            self._values["mssql"] = mssql
        if mysql is not None:
            self._values["mysql"] = mysql
        if mysql_aurora is not None:
            self._values["mysql_aurora"] = mysql_aurora
        if mysql_legacy is not None:
            self._values["mysql_legacy"] = mysql_legacy
        if mysql_rds is not None:
            self._values["mysql_rds"] = mysql_rds
        if namespace is not None:
            self._values["namespace"] = namespace
        if oracle is not None:
            self._values["oracle"] = oracle
        if plugin_name is not None:
            self._values["plugin_name"] = plugin_name
        if postgresql is not None:
            self._values["postgresql"] = postgresql
        if redis is not None:
            self._values["redis"] = redis
        if redis_elasticache is not None:
            self._values["redis_elasticache"] = redis_elasticache
        if redshift is not None:
            self._values["redshift"] = redshift
        if root_rotation_statements is not None:
            self._values["root_rotation_statements"] = root_rotation_statements
        if rotation_period is not None:
            self._values["rotation_period"] = rotation_period
        if rotation_schedule is not None:
            self._values["rotation_schedule"] = rotation_schedule
        if rotation_window is not None:
            self._values["rotation_window"] = rotation_window
        if snowflake is not None:
            self._values["snowflake"] = snowflake
        if verify_connection is not None:
            self._values["verify_connection"] = verify_connection

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
        '''Unique name of the Vault mount to configure.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#backend DatabaseSecretBackendConnection#backend}
        '''
        result = self._values.get("backend")
        assert result is not None, "Required property 'backend' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the database connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#name DatabaseSecretBackendConnection#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of roles that are allowed to use this connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#allowed_roles DatabaseSecretBackendConnection#allowed_roles}
        '''
        result = self._values.get("allowed_roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cassandra(self) -> typing.Optional[DatabaseSecretBackendConnectionCassandra]:
        '''cassandra block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#cassandra DatabaseSecretBackendConnection#cassandra}
        '''
        result = self._values.get("cassandra")
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionCassandra], result)

    @builtins.property
    def couchbase(self) -> typing.Optional["DatabaseSecretBackendConnectionCouchbase"]:
        '''couchbase block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#couchbase DatabaseSecretBackendConnection#couchbase}
        '''
        result = self._values.get("couchbase")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionCouchbase"], result)

    @builtins.property
    def data(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of sensitive data to pass to the endpoint. Useful for templated connection strings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#data DatabaseSecretBackendConnection#data}
        '''
        result = self._values.get("data")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def disable_automated_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Stops rotation of the root credential until set to false.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_automated_rotation DatabaseSecretBackendConnection#disable_automated_rotation}
        '''
        result = self._values.get("disable_automated_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def elasticsearch(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionElasticsearch"]:
        '''elasticsearch block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#elasticsearch DatabaseSecretBackendConnection#elasticsearch}
        '''
        result = self._values.get("elasticsearch")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionElasticsearch"], result)

    @builtins.property
    def hana(self) -> typing.Optional["DatabaseSecretBackendConnectionHana"]:
        '''hana block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hana DatabaseSecretBackendConnection#hana}
        '''
        result = self._values.get("hana")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionHana"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#id DatabaseSecretBackendConnection#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def influxdb(self) -> typing.Optional["DatabaseSecretBackendConnectionInfluxdb"]:
        '''influxdb block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#influxdb DatabaseSecretBackendConnection#influxdb}
        '''
        result = self._values.get("influxdb")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionInfluxdb"], result)

    @builtins.property
    def mongodb(self) -> typing.Optional["DatabaseSecretBackendConnectionMongodb"]:
        '''mongodb block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mongodb DatabaseSecretBackendConnection#mongodb}
        '''
        result = self._values.get("mongodb")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMongodb"], result)

    @builtins.property
    def mongodbatlas(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMongodbatlas"]:
        '''mongodbatlas block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mongodbatlas DatabaseSecretBackendConnection#mongodbatlas}
        '''
        result = self._values.get("mongodbatlas")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMongodbatlas"], result)

    @builtins.property
    def mssql(self) -> typing.Optional["DatabaseSecretBackendConnectionMssql"]:
        '''mssql block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mssql DatabaseSecretBackendConnection#mssql}
        '''
        result = self._values.get("mssql")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMssql"], result)

    @builtins.property
    def mysql(self) -> typing.Optional["DatabaseSecretBackendConnectionMysql"]:
        '''mysql block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql DatabaseSecretBackendConnection#mysql}
        '''
        result = self._values.get("mysql")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysql"], result)

    @builtins.property
    def mysql_aurora(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMysqlAurora"]:
        '''mysql_aurora block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_aurora DatabaseSecretBackendConnection#mysql_aurora}
        '''
        result = self._values.get("mysql_aurora")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysqlAurora"], result)

    @builtins.property
    def mysql_legacy(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionMysqlLegacy"]:
        '''mysql_legacy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_legacy DatabaseSecretBackendConnection#mysql_legacy}
        '''
        result = self._values.get("mysql_legacy")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysqlLegacy"], result)

    @builtins.property
    def mysql_rds(self) -> typing.Optional["DatabaseSecretBackendConnectionMysqlRds"]:
        '''mysql_rds block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#mysql_rds DatabaseSecretBackendConnection#mysql_rds}
        '''
        result = self._values.get("mysql_rds")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionMysqlRds"], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Target namespace. (requires Enterprise).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#namespace DatabaseSecretBackendConnection#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle(self) -> typing.Optional["DatabaseSecretBackendConnectionOracle"]:
        '''oracle block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#oracle DatabaseSecretBackendConnection#oracle}
        '''
        result = self._values.get("oracle")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionOracle"], result)

    @builtins.property
    def plugin_name(self) -> typing.Optional[builtins.str]:
        '''Specifies the name of the plugin to use for this connection.

        Must be prefixed with the name of one of the supported database engine types.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#plugin_name DatabaseSecretBackendConnection#plugin_name}
        '''
        result = self._values.get("plugin_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionPostgresql"]:
        '''postgresql block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#postgresql DatabaseSecretBackendConnection#postgresql}
        '''
        result = self._values.get("postgresql")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionPostgresql"], result)

    @builtins.property
    def redis(self) -> typing.Optional["DatabaseSecretBackendConnectionRedis"]:
        '''redis block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redis DatabaseSecretBackendConnection#redis}
        '''
        result = self._values.get("redis")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionRedis"], result)

    @builtins.property
    def redis_elasticache(
        self,
    ) -> typing.Optional["DatabaseSecretBackendConnectionRedisElasticache"]:
        '''redis_elasticache block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redis_elasticache DatabaseSecretBackendConnection#redis_elasticache}
        '''
        result = self._values.get("redis_elasticache")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionRedisElasticache"], result)

    @builtins.property
    def redshift(self) -> typing.Optional["DatabaseSecretBackendConnectionRedshift"]:
        '''redshift block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#redshift DatabaseSecretBackendConnection#redshift}
        '''
        result = self._values.get("redshift")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionRedshift"], result)

    @builtins.property
    def root_rotation_statements(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of database statements to be executed to rotate the root user's credentials.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#root_rotation_statements DatabaseSecretBackendConnection#root_rotation_statements}
        '''
        result = self._values.get("root_rotation_statements")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rotation_period(self) -> typing.Optional[jsii.Number]:
        '''The period of time in seconds between each rotation of the root credential. Cannot be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_period DatabaseSecretBackendConnection#rotation_period}
        '''
        result = self._values.get("rotation_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_schedule(self) -> typing.Optional[builtins.str]:
        '''The cron-style schedule for the root credential to be rotated on. Cannot be used with rotation_period.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_schedule DatabaseSecretBackendConnection#rotation_schedule}
        '''
        result = self._values.get("rotation_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_window(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of time in seconds Vault is allowed to complete a rotation once a scheduled rotation is triggered.

        Can only be used with rotation_schedule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#rotation_window DatabaseSecretBackendConnection#rotation_window}
        '''
        result = self._values.get("rotation_window")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snowflake(self) -> typing.Optional["DatabaseSecretBackendConnectionSnowflake"]:
        '''snowflake block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#snowflake DatabaseSecretBackendConnection#snowflake}
        '''
        result = self._values.get("snowflake")
        return typing.cast(typing.Optional["DatabaseSecretBackendConnectionSnowflake"], result)

    @builtins.property
    def verify_connection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies if the connection is verified during initial configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#verify_connection DatabaseSecretBackendConnection#verify_connection}
        '''
        result = self._values.get("verify_connection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionCouchbase",
    jsii_struct_bases=[],
    name_mapping={
        "hosts": "hosts",
        "password": "password",
        "username": "username",
        "base64_pem": "base64Pem",
        "bucket_name": "bucketName",
        "insecure_tls": "insecureTls",
        "tls": "tls",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionCouchbase:
    def __init__(
        self,
        *,
        hosts: typing.Sequence[builtins.str],
        password: builtins.str,
        username: builtins.str,
        base64_pem: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosts: A set of Couchbase URIs to connect to. Must use ``couchbases://`` scheme if ``tls`` is ``true``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hosts DatabaseSecretBackendConnection#hosts}
        :param password: Specifies the password corresponding to the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param username: Specifies the username for Vault to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param base64_pem: Required if ``tls`` is ``true``. Specifies the certificate authority of the Couchbase server, as a PEM certificate that has been base64 encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#base64_pem DatabaseSecretBackendConnection#base64_pem}
        :param bucket_name: Required for Couchbase versions prior to 6.5.0. This is only used to verify vault's connection to the server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#bucket_name DatabaseSecretBackendConnection#bucket_name}
        :param insecure_tls: Specifies whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param tls: Specifies whether to use TLS when connecting to Couchbase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5510161a437422a74b4c96a676cd938743f1e480f64a5a815aa118a7f2647a2f)
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument base64_pem", value=base64_pem, expected_type=type_hints["base64_pem"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosts": hosts,
            "password": password,
            "username": username,
        }
        if base64_pem is not None:
            self._values["base64_pem"] = base64_pem
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if insecure_tls is not None:
            self._values["insecure_tls"] = insecure_tls
        if tls is not None:
            self._values["tls"] = tls
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def hosts(self) -> typing.List[builtins.str]:
        '''A set of Couchbase URIs to connect to. Must use ``couchbases://`` scheme if ``tls`` is ``true``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#hosts DatabaseSecretBackendConnection#hosts}
        '''
        result = self._values.get("hosts")
        assert result is not None, "Required property 'hosts' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Specifies the password corresponding to the given username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Specifies the username for Vault to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def base64_pem(self) -> typing.Optional[builtins.str]:
        '''Required if ``tls`` is ``true``.

        Specifies the certificate authority of the Couchbase server, as a PEM certificate that has been base64 encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#base64_pem DatabaseSecretBackendConnection#base64_pem}
        '''
        result = self._values.get("base64_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Required for Couchbase versions prior to 6.5.0. This is only used to verify vault's connection to the server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#bucket_name DatabaseSecretBackendConnection#bucket_name}
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to skip verification of the server certificate when using TLS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        '''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to use TLS when connecting to Couchbase.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how dynamic usernames are generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionCouchbase(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionCouchbaseOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionCouchbaseOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a3bfb5de8aa08fd4e74cc6247d59010cfc6f12dd97b059dad1d913cd5229e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBase64Pem")
    def reset_base64_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBase64Pem", []))

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetInsecureTls")
    def reset_insecure_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureTls", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="base64PemInput")
    def base64_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "base64PemInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="hostsInput")
    def hosts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostsInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureTlsInput")
    def insecure_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureTlsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsInput")
    def tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="base64Pem")
    def base64_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "base64Pem"))

    @base64_pem.setter
    def base64_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42f97940e11e5e7cda31bd76d930b5ef51517c2af20acc16e54006211a92386a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "base64Pem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a9699c016711553005fc2b470d90d724668b243a64e0abf968d4cc273c6a11c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hosts"))

    @hosts.setter
    def hosts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87e36f43b69755bd0828e004604abe0b363dafb118d9388589a212269528570b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hosts", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureTls")
    def insecure_tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecureTls"))

    @insecure_tls.setter
    def insecure_tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__348898f41302670970f4144276783e87136cd45e9f9f9d02c9ad533c62b48768)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1348b5caa82f63e767d0f352899444ecde78e17f9a19dd15e2ebc5845cf0f1e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tls")
    def tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tls"))

    @tls.setter
    def tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a122280378f2e3cf2b4b39930f0f9760065818c82dd58cb46aaef2f737b7892b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22b10126159c85a79dd1c2078c880298cf95e1b6a8e1624b10961a058ec15557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a95c0198ef58488325251b640dd746a92328a1a21fc15322605f5d89e204edaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionCouchbase]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionCouchbase], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionCouchbase],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7ab16ccc300f249f30a431a3be97a802c042f3d63f1ec9b42446b3d615dc43a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionElasticsearch",
    jsii_struct_bases=[],
    name_mapping={
        "password": "password",
        "url": "url",
        "username": "username",
        "ca_cert": "caCert",
        "ca_path": "caPath",
        "client_cert": "clientCert",
        "client_key": "clientKey",
        "insecure": "insecure",
        "tls_server_name": "tlsServerName",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionElasticsearch:
    def __init__(
        self,
        *,
        password: builtins.str,
        url: builtins.str,
        username: builtins.str,
        ca_cert: typing.Optional[builtins.str] = None,
        ca_path: typing.Optional[builtins.str] = None,
        client_cert: typing.Optional[builtins.str] = None,
        client_key: typing.Optional[builtins.str] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tls_server_name: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param password: The password to be used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param url: The URL for Elasticsearch's API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#url DatabaseSecretBackendConnection#url}
        :param username: The username to be used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param ca_cert: The path to a PEM-encoded CA cert file to use to verify the Elasticsearch server's identity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_cert DatabaseSecretBackendConnection#ca_cert}
        :param ca_path: The path to a directory of PEM-encoded CA cert files to use to verify the Elasticsearch server's identity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_path DatabaseSecretBackendConnection#ca_path}
        :param client_cert: The path to the certificate for the Elasticsearch client to present for communication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#client_cert DatabaseSecretBackendConnection#client_cert}
        :param client_key: The path to the key for the Elasticsearch client to use for communication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#client_key DatabaseSecretBackendConnection#client_key}
        :param insecure: Whether to disable certificate verification. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure DatabaseSecretBackendConnection#insecure}
        :param tls_server_name: This, if set, is used to set the SNI host when connecting via TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_server_name DatabaseSecretBackendConnection#tls_server_name}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__813a4819d65f1ec63deef3d99ecc9720678485491411f5d918b6e6b418a1306f)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument ca_cert", value=ca_cert, expected_type=type_hints["ca_cert"])
            check_type(argname="argument ca_path", value=ca_path, expected_type=type_hints["ca_path"])
            check_type(argname="argument client_cert", value=client_cert, expected_type=type_hints["client_cert"])
            check_type(argname="argument client_key", value=client_key, expected_type=type_hints["client_key"])
            check_type(argname="argument insecure", value=insecure, expected_type=type_hints["insecure"])
            check_type(argname="argument tls_server_name", value=tls_server_name, expected_type=type_hints["tls_server_name"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "url": url,
            "username": username,
        }
        if ca_cert is not None:
            self._values["ca_cert"] = ca_cert
        if ca_path is not None:
            self._values["ca_path"] = ca_path
        if client_cert is not None:
            self._values["client_cert"] = client_cert
        if client_key is not None:
            self._values["client_key"] = client_key
        if insecure is not None:
            self._values["insecure"] = insecure
        if tls_server_name is not None:
            self._values["tls_server_name"] = tls_server_name
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def password(self) -> builtins.str:
        '''The password to be used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''The URL for Elasticsearch's API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#url DatabaseSecretBackendConnection#url}
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''The username to be used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ca_cert(self) -> typing.Optional[builtins.str]:
        '''The path to a PEM-encoded CA cert file to use to verify the Elasticsearch server's identity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_cert DatabaseSecretBackendConnection#ca_cert}
        '''
        result = self._values.get("ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_path(self) -> typing.Optional[builtins.str]:
        '''The path to a directory of PEM-encoded CA cert files to use to verify the Elasticsearch server's identity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_path DatabaseSecretBackendConnection#ca_path}
        '''
        result = self._values.get("ca_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_cert(self) -> typing.Optional[builtins.str]:
        '''The path to the certificate for the Elasticsearch client to present for communication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#client_cert DatabaseSecretBackendConnection#client_cert}
        '''
        result = self._values.get("client_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_key(self) -> typing.Optional[builtins.str]:
        '''The path to the key for the Elasticsearch client to use for communication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#client_key DatabaseSecretBackendConnection#client_key}
        '''
        result = self._values.get("client_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to disable certificate verification.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure DatabaseSecretBackendConnection#insecure}
        '''
        result = self._values.get("insecure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tls_server_name(self) -> typing.Optional[builtins.str]:
        '''This, if set, is used to set the SNI host when connecting via TLS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_server_name DatabaseSecretBackendConnection#tls_server_name}
        '''
        result = self._values.get("tls_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how dynamic usernames are generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionElasticsearch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionElasticsearchOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionElasticsearchOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdfde47c66b4e5c88a2a2427780b5bdf2fe31d3f4db5dadf04bc87c97c1876e6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCaCert")
    def reset_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCert", []))

    @jsii.member(jsii_name="resetCaPath")
    def reset_ca_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPath", []))

    @jsii.member(jsii_name="resetClientCert")
    def reset_client_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientCert", []))

    @jsii.member(jsii_name="resetClientKey")
    def reset_client_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientKey", []))

    @jsii.member(jsii_name="resetInsecure")
    def reset_insecure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecure", []))

    @jsii.member(jsii_name="resetTlsServerName")
    def reset_tls_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsServerName", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="caCertInput")
    def ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertInput"))

    @builtins.property
    @jsii.member(jsii_name="caPathInput")
    def ca_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPathInput"))

    @builtins.property
    @jsii.member(jsii_name="clientCertInput")
    def client_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientCertInput"))

    @builtins.property
    @jsii.member(jsii_name="clientKeyInput")
    def client_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureInput")
    def insecure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsServerNameInput")
    def tls_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="caCert")
    def ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCert"))

    @ca_cert.setter
    def ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ef15526b31b3fb4bfb79840e09f8504fdd729b0a0def4af5bdad2b728ba7197)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caPath")
    def ca_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caPath"))

    @ca_path.setter
    def ca_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cf0b3a00d4cc202607291474e0af94913d25414811bcaac026a155715a395ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientCert")
    def client_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientCert"))

    @client_cert.setter
    def client_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b9e2164762d01c35e9cfa9955d67fe1db83aabf5d1740480b0ada364bb258ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientKey")
    def client_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientKey"))

    @client_key.setter
    def client_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78f1d6a2d40a2eb846b708c1246bf16eac08efac56f3e03a60f905aa6588eb44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecure")
    def insecure(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecure"))

    @insecure.setter
    def insecure(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2a2816d7d34dca7b92351f789b294395a9da0a23c9d5aa648aff67a7776456)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76a37169d75c131c47890a3ee74fb5c9e5daee8f8f7a2c5377d00f23c0466eeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsServerName")
    def tls_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsServerName"))

    @tls_server_name.setter
    def tls_server_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f06251bd228441c1af3284df8da8b95d403e6894dbe15fe4432649776cfebbc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsServerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b47bd6506ecbc9ba5331d07e7aad1157ef82fbe65aa6b480487470053ec09020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1cea49426286255a5bcec1c30c7e42eedc06f477d577f668ff46dd1aaa8dc8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd861b4026d46b6d9bda2bf80a6db379837689bed764e1f07e564a2fdd48e49a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionElasticsearch]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionElasticsearch], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionElasticsearch],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e49bdf4b260510892458fcc824f16383c5d349e12f50bcd879b5f3c8ea298f97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionHana",
    jsii_struct_bases=[],
    name_mapping={
        "connection_url": "connectionUrl",
        "disable_escaping": "disableEscaping",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "username": "username",
    },
)
class DatabaseSecretBackendConnectionHana:
    def __init__(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__712968b2b3ccc279e6c67ad8d58abc2efe75e07e3954084825e4dde4b1d173b6)
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument disable_escaping", value=disable_escaping, expected_type=type_hints["disable_escaping"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if disable_escaping is not None:
            self._values["disable_escaping"] = disable_escaping
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_escaping(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable special character escaping in username and password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        '''
        result = self._values.get("disable_escaping")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionHana(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionHanaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionHanaOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50bd0914ea61a6d5acf3a375c30c88b86c06e8dd54c41989e710e233ad4c20f8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetDisableEscaping")
    def reset_disable_escaping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableEscaping", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="disableEscapingInput")
    def disable_escaping_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableEscapingInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ceb9b4a7178394ea555dab0c9cd8397445c1ef61d7bac8198f5c438abdd74a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableEscaping")
    def disable_escaping(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableEscaping"))

    @disable_escaping.setter
    def disable_escaping(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ac94623b5ec54f07ddcdfb2ff00b546dcb7f41ef22d3057291be9fe09b1bc23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableEscaping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9998468bfeeaa90594113692bb77db01403852c1b2667d5a5461a805569b67d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9762f6378f8c186b0a64faa28e5d7948f8bd7b1f011bb056ba400a72ea49d266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b60efd638368d91f9408350d1a2918e8f6b75038a11128013003bd4795413073)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae2af10f8fe2a71d553fd181f2010c86ee24d3c59583e36fb3c2a480bac2ebd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db41f7607efce7066ffbb7a50d6f3ad7298ff67684237e9416511eda4052f60c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__372b7144b7e1e5e8c92685c8d0348a225d4bf627435ddae3148a3dbb2dd08ccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6a5f218be2743a185395ef4303295593c3cd93880decdf1c67cb6622a86dd50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabaseSecretBackendConnectionHana]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionHana], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionHana],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd869116178460d6cb1d8676f29c95a1d3cdac19650ab8b59bd351929d0cbee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionInfluxdb",
    jsii_struct_bases=[],
    name_mapping={
        "host": "host",
        "password": "password",
        "username": "username",
        "connect_timeout": "connectTimeout",
        "insecure_tls": "insecureTls",
        "pem_bundle": "pemBundle",
        "pem_json": "pemJson",
        "port": "port",
        "tls": "tls",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionInfluxdb:
    def __init__(
        self,
        *,
        host: builtins.str,
        password: builtins.str,
        username: builtins.str,
        connect_timeout: typing.Optional[jsii.Number] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pem_bundle: typing.Optional[builtins.str] = None,
        pem_json: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host: Influxdb host to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#host DatabaseSecretBackendConnection#host}
        :param password: Specifies the password corresponding to the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param username: Specifies the username to use for superuser access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param connect_timeout: The number of seconds to use as a connection timeout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connect_timeout DatabaseSecretBackendConnection#connect_timeout}
        :param insecure_tls: Whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param pem_bundle: Concatenated PEM blocks containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_bundle DatabaseSecretBackendConnection#pem_bundle}
        :param pem_json: Specifies JSON containing a certificate and private key; a certificate, private key, and issuing CA certificate; or just a CA certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_json DatabaseSecretBackendConnection#pem_json}
        :param port: The transport port to use to connect to Influxdb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        :param tls: Whether to use TLS when connecting to Influxdb. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        :param username_template: Template describing how dynamic usernames are generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b50c6d1de18d1a927c9c0c4e352103624fade9750ad1446d2feb4340ac4af12a)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument pem_bundle", value=pem_bundle, expected_type=type_hints["pem_bundle"])
            check_type(argname="argument pem_json", value=pem_json, expected_type=type_hints["pem_json"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
            "password": password,
            "username": username,
        }
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if insecure_tls is not None:
            self._values["insecure_tls"] = insecure_tls
        if pem_bundle is not None:
            self._values["pem_bundle"] = pem_bundle
        if pem_json is not None:
            self._values["pem_json"] = pem_json
        if port is not None:
            self._values["port"] = port
        if tls is not None:
            self._values["tls"] = tls
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def host(self) -> builtins.str:
        '''Influxdb host to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#host DatabaseSecretBackendConnection#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Specifies the password corresponding to the given username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Specifies the username to use for superuser access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''The number of seconds to use as a connection timeout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connect_timeout DatabaseSecretBackendConnection#connect_timeout}
        '''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to skip verification of the server certificate when using TLS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        '''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pem_bundle(self) -> typing.Optional[builtins.str]:
        '''Concatenated PEM blocks containing a certificate and private key;

        a certificate, private key, and issuing CA certificate; or just a CA certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_bundle DatabaseSecretBackendConnection#pem_bundle}
        '''
        result = self._values.get("pem_bundle")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_json(self) -> typing.Optional[builtins.str]:
        '''Specifies JSON containing a certificate and private key;

        a certificate, private key, and issuing CA certificate; or just a CA certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#pem_json DatabaseSecretBackendConnection#pem_json}
        '''
        result = self._values.get("pem_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The transport port to use to connect to Influxdb.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to use TLS when connecting to Influxdb.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Template describing how dynamic usernames are generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionInfluxdb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionInfluxdbOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionInfluxdbOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9e10fff3a6b5f70d8a50e4971d04df3019e44b3d663541c0431d03ce7a632b9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetInsecureTls")
    def reset_insecure_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureTls", []))

    @jsii.member(jsii_name="resetPemBundle")
    def reset_pem_bundle(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemBundle", []))

    @jsii.member(jsii_name="resetPemJson")
    def reset_pem_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemJson", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureTlsInput")
    def insecure_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureTlsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="pemBundleInput")
    def pem_bundle_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemBundleInput"))

    @builtins.property
    @jsii.member(jsii_name="pemJsonInput")
    def pem_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsInput")
    def tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad9283d9dc629c7ec4773b3b38f4b2a8e31714a18aad94455d45102197d0a2dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adae2d8ce5b14ba42c38476611612f99375212c1bdc44207e2e94b1f573b5dfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureTls")
    def insecure_tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecureTls"))

    @insecure_tls.setter
    def insecure_tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5312c682f08660567e477a9e54131deda7c27c359ec0a50e94f092a7ab6a6177)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35fc1c0dd9f37600406f5694584c3e8b71f41a32840240544aa30e79cb9bab1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemBundle")
    def pem_bundle(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemBundle"))

    @pem_bundle.setter
    def pem_bundle(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67ce43de6205c3fd2a95d5266ca1285a7db7962731aaf7be74b6be72e6c15d91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemBundle", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemJson")
    def pem_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemJson"))

    @pem_json.setter
    def pem_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a3864d98614599b8cd974158f7898d65e2b5da8b8dbb4a39c3eafbfa1e92052)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f99d05ac50ed9fc46e3a4c718eb4b0d68a2f95e09269653b6867a00ad29c3d7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tls")
    def tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tls"))

    @tls.setter
    def tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f17abdb02924b4dd51db07cf1a5214ca31e85e118c61a636538654047623808b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beb3636171a720e480b54a87d029a92d8bd1e0cf76421d7f42968dec25494fc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdb290c0ee7705fdf32b34f195a06d7bb1e9d83834bb17ec1cd742a4816dbee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionInfluxdb]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionInfluxdb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionInfluxdb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4383e3e62c73c913ed1aec6d61c131cabcde9fa7d49344a66802ea041da568a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMongodb",
    jsii_struct_bases=[],
    name_mapping={
        "connection_url": "connectionUrl",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionMongodb:
    def __init__(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d986b37f6918d4b6df0760a720a1c33247b912bf3fc2a3770c9eae07f74be99)
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMongodb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionMongodbOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMongodbOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83cbf9abd3a9d23a046ae4d40dbaff228ac7945b2ab18ad5e227dd4d42ff1e95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c097380aefe2cd3a9a23cb55032b7ed447339ebd325ab4eefbb2b8b45d07bf90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c323f516dc59699d533fca78edfc390673dd51336553148638da406ac07f6e00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50509a1ee4b43834300d2dd0230ecdb080e5c6957a44619a6130c1622a020659)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73008b969752ee21ec8155b9a9e8f096e8ed1727a94c4cab26b9f48ff567d361)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0284ecf296027f193fd67db693c75a361d4ab7451f5e9533c4b1d834eb2efd37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd6bc190bdacd41cdcc717d467048256f0315136c17797951ddbef6a44fa2d21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbc667655f863a8ed21a51212813fc5eab4da1a3b534cc1d572b367a6c3c8e29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc85b69c211e3646dffcd7498861aca96bf222b40bd1149f09e03270ffcfd672)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9be336bcc871efd871f2392886de53f8bec3b36547f5c6e964bd263eaa134b09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabaseSecretBackendConnectionMongodb]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMongodb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMongodb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__739ecb9c809232b8d2a18b4cff15b3cb2da55ba6a03bb4efdea08ac414d40732)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMongodbatlas",
    jsii_struct_bases=[],
    name_mapping={
        "private_key": "privateKey",
        "project_id": "projectId",
        "public_key": "publicKey",
    },
)
class DatabaseSecretBackendConnectionMongodbatlas:
    def __init__(
        self,
        *,
        private_key: builtins.str,
        project_id: builtins.str,
        public_key: builtins.str,
    ) -> None:
        '''
        :param private_key: The Private Programmatic API Key used to connect with MongoDB Atlas API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key DatabaseSecretBackendConnection#private_key}
        :param project_id: The Project ID the Database User should be created within. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#project_id DatabaseSecretBackendConnection#project_id}
        :param public_key: The Public Programmatic API Key used to authenticate with the MongoDB Atlas API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#public_key DatabaseSecretBackendConnection#public_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08dde2f5021d8a411280e477dbd661f0c9cb6b90870d6807db6db56db78bf3c3)
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument public_key", value=public_key, expected_type=type_hints["public_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "private_key": private_key,
            "project_id": project_id,
            "public_key": public_key,
        }

    @builtins.property
    def private_key(self) -> builtins.str:
        '''The Private Programmatic API Key used to connect with MongoDB Atlas API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key DatabaseSecretBackendConnection#private_key}
        '''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''The Project ID the Database User should be created within.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#project_id DatabaseSecretBackendConnection#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def public_key(self) -> builtins.str:
        '''The Public Programmatic API Key used to authenticate with the MongoDB Atlas API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#public_key DatabaseSecretBackendConnection#public_key}
        '''
        result = self._values.get("public_key")
        assert result is not None, "Required property 'public_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMongodbatlas(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionMongodbatlasOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMongodbatlasOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c56bf7afa1dff19450dd2309ae270905eb23eb70e0f9cca7422eacb52143810b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fdeb6f2c7e01f51446df241052352b9835d7005eea15d830b7fd8616892d0ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd6feade9eb601162c27842b6db477f87536f8d2c2731a4d09c3e6fea2e1ae83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfcbdafdc0f16a575aa0dba38fe5f1f786d9f60c04665f1bf3ac12bbc5e97578)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionMongodbatlas]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMongodbatlas], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMongodbatlas],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b78f96240011ef2b74a31ca0dbb2c9bdd71cb8cefecedd4909762e928e8e12d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMssql",
    jsii_struct_bases=[],
    name_mapping={
        "connection_url": "connectionUrl",
        "contained_db": "containedDb",
        "disable_escaping": "disableEscaping",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionMssql:
    def __init__(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        contained_db: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param contained_db: Set to true when the target is a Contained Database, e.g. AzureSQL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#contained_db DatabaseSecretBackendConnection#contained_db}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c8f78aaac5238cfe6b074c692f6573095d52500f3ec5941ba4bc8a216502d79)
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument contained_db", value=contained_db, expected_type=type_hints["contained_db"])
            check_type(argname="argument disable_escaping", value=disable_escaping, expected_type=type_hints["disable_escaping"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if contained_db is not None:
            self._values["contained_db"] = contained_db
        if disable_escaping is not None:
            self._values["disable_escaping"] = disable_escaping
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def contained_db(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true when the target is a Contained Database, e.g. AzureSQL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#contained_db DatabaseSecretBackendConnection#contained_db}
        '''
        result = self._values.get("contained_db")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def disable_escaping(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable special character escaping in username and password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        '''
        result = self._values.get("disable_escaping")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMssql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionMssqlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMssqlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7a884065eac1a32a7a6f1f8957cd5f2b12fef8ad883bd49b267e54781b930b0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetContainedDb")
    def reset_contained_db(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainedDb", []))

    @jsii.member(jsii_name="resetDisableEscaping")
    def reset_disable_escaping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableEscaping", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="containedDbInput")
    def contained_db_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "containedDbInput"))

    @builtins.property
    @jsii.member(jsii_name="disableEscapingInput")
    def disable_escaping_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableEscapingInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76adeb9557632174632ada90eb9c5736c902352fcf0b16a09189fdcfe097ac9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containedDb")
    def contained_db(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "containedDb"))

    @contained_db.setter
    def contained_db(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d410c4ab8968280035f573fe7540433309ec1b7f917a0e0cb3c4f77f831c5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containedDb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableEscaping")
    def disable_escaping(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableEscaping"))

    @disable_escaping.setter
    def disable_escaping(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab309a246a04558f4f6472c20d0aca10f5c5a08f40c4aae6b1738a143498a39f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableEscaping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61a514dd6752751fd616490075723da7ee9761c252dd12c29e7a9ad8030401c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ffa80f50be95ee21d62e8e7154c152f5ad1c05546320fb4218e8b76fd0352fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d2ab4ddc39ff65c1b9bad1495999626ccf336e3e249caa4e171d8db4c4c6191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4ad4918802bdf3c9db57d86dbf27c6f4bf07957589e311e865ef55a8f76482f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5fa12b114958097e8a695e419cb2ed952ece119cae18adf1b377dc700e60507)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6fe0b92206a89d82d97d4fa976e733fc93968e0eef7dd0d9f0cfadb13e4e0d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244367f87d3478c56ecd43abef9bdcbf905492417bf8ea8d4c974755911859bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2caab17b3c522874ce82a64f8a7c4d2e44b3d696a978f691c41614215646e78d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabaseSecretBackendConnectionMssql]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMssql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMssql],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59a2591db6bf474bd00174a43da4d44d9a44c8fe7b85ec3add3dff0237455a95)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysql",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "connection_url": "connectionUrl",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "service_account_json": "serviceAccountJson",
        "tls_ca": "tlsCa",
        "tls_certificate_key": "tlsCertificateKey",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionMysql:
    def __init__(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf7abd4a1cf6ea2dbd6fc522e03e73b98341dbfa5219b84276360fb11444df13)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument service_account_json", value=service_account_json, expected_type=type_hints["service_account_json"])
            check_type(argname="argument tls_ca", value=tls_ca, expected_type=type_hints["tls_ca"])
            check_type(argname="argument tls_certificate_key", value=tls_certificate_key, expected_type=type_hints["tls_certificate_key"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if service_account_json is not None:
            self._values["service_account_json"] = service_account_json
        if tls_ca is not None:
            self._values["tls_ca"] = tls_ca
        if tls_certificate_key is not None:
            self._values["tls_certificate_key"] = tls_certificate_key
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Specify alternative authorization type. (Only 'gcp_iam' is valid currently).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_account_json(self) -> typing.Optional[builtins.str]:
        '''A JSON encoded credential for use with IAM authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        '''
        result = self._values.get("service_account_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_ca(self) -> typing.Optional[builtins.str]:
        '''x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        '''
        result = self._values.get("tls_ca")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate_key(self) -> typing.Optional[builtins.str]:
        '''x509 certificate for connecting to the database.

        This must be a PEM encoded version of the private key and the certificate combined.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        '''
        result = self._values.get("tls_certificate_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMysql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlAurora",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "connection_url": "connectionUrl",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "service_account_json": "serviceAccountJson",
        "tls_ca": "tlsCa",
        "tls_certificate_key": "tlsCertificateKey",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionMysqlAurora:
    def __init__(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__721cf4b6720e013234dd31a8ce4bba47692ec1ef070292c2976c8b97f5342c21)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument service_account_json", value=service_account_json, expected_type=type_hints["service_account_json"])
            check_type(argname="argument tls_ca", value=tls_ca, expected_type=type_hints["tls_ca"])
            check_type(argname="argument tls_certificate_key", value=tls_certificate_key, expected_type=type_hints["tls_certificate_key"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if service_account_json is not None:
            self._values["service_account_json"] = service_account_json
        if tls_ca is not None:
            self._values["tls_ca"] = tls_ca
        if tls_certificate_key is not None:
            self._values["tls_certificate_key"] = tls_certificate_key
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Specify alternative authorization type. (Only 'gcp_iam' is valid currently).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_account_json(self) -> typing.Optional[builtins.str]:
        '''A JSON encoded credential for use with IAM authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        '''
        result = self._values.get("service_account_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_ca(self) -> typing.Optional[builtins.str]:
        '''x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        '''
        result = self._values.get("tls_ca")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate_key(self) -> typing.Optional[builtins.str]:
        '''x509 certificate for connecting to the database.

        This must be a PEM encoded version of the private key and the certificate combined.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        '''
        result = self._values.get("tls_certificate_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMysqlAurora(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionMysqlAuroraOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlAuroraOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f308af1eb44d630360c272e5556552ff96e627e401b635a5a97d6b7009266a27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetServiceAccountJson")
    def reset_service_account_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountJson", []))

    @jsii.member(jsii_name="resetTlsCa")
    def reset_tls_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCa", []))

    @jsii.member(jsii_name="resetTlsCertificateKey")
    def reset_tls_certificate_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificateKey", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJsonInput")
    def service_account_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaInput")
    def tls_ca_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCaInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKeyInput")
    def tls_certificate_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f0d939a8dff5fd17e9a1adce2f3a5afd7e9f8140eaca1f67c98d9775456baf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7c5d84f79e8082fd26ab7f3b3970a36efc0c9328ee09d391b21a67e6e3a18a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09ac502162f28c541ac2d3632c9d053cec40f6d81a8cceca7f1c821f9b75b622)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d59bf3d265affbc3ac0c35d6ac8427ae75db39273e1b111c0b67f30971771f84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb3f4bf2ef91400779f8f6af7382622bc7b0a783720a8f9f1882a1c922856d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecda563f77b9dad59f6228cf5a86731fe3da31dd969cbacb373c0f854e243be7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f91edaf58a25ff18cbf297cc2243207ac80a528bbfec7420d81867044524918e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f76134f0dfc4422a720f7babb9dddbd684ef00b6d62da9b88204cbdf41ddf408)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJson")
    def service_account_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountJson"))

    @service_account_json.setter
    def service_account_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__828aede2bba16a36361f3136075460ee9790624543029ca344ebbfff43c938d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCa")
    def tls_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCa"))

    @tls_ca.setter
    def tls_ca(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb233af184a5f7d4106d48335b336b777dc43c818dcd9fe09b4d34bab5c019c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKey")
    def tls_certificate_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificateKey"))

    @tls_certificate_key.setter
    def tls_certificate_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b3bcb497ff39834871814cb61bf71d55552697af9db6d6065e8ef103901dcf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b601a9fc41d8ce207733e258a47bdc56ba40678b2c65ae6da669f901512d6e37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec6801d17baa5f300f1d87eca5389fb35a6972cbc2509057977b8c88ff6da1e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionMysqlAurora]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMysqlAurora], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMysqlAurora],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68f44da2845c14c513be55640633193c615d0fa23c24f406f885d3cf464a503b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlLegacy",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "connection_url": "connectionUrl",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "service_account_json": "serviceAccountJson",
        "tls_ca": "tlsCa",
        "tls_certificate_key": "tlsCertificateKey",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionMysqlLegacy:
    def __init__(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b027525e7c7c5b55e80d015bbb97ba1291a1c1f914c5de3578fd6b2d85a36868)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument service_account_json", value=service_account_json, expected_type=type_hints["service_account_json"])
            check_type(argname="argument tls_ca", value=tls_ca, expected_type=type_hints["tls_ca"])
            check_type(argname="argument tls_certificate_key", value=tls_certificate_key, expected_type=type_hints["tls_certificate_key"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if service_account_json is not None:
            self._values["service_account_json"] = service_account_json
        if tls_ca is not None:
            self._values["tls_ca"] = tls_ca
        if tls_certificate_key is not None:
            self._values["tls_certificate_key"] = tls_certificate_key
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Specify alternative authorization type. (Only 'gcp_iam' is valid currently).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_account_json(self) -> typing.Optional[builtins.str]:
        '''A JSON encoded credential for use with IAM authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        '''
        result = self._values.get("service_account_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_ca(self) -> typing.Optional[builtins.str]:
        '''x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        '''
        result = self._values.get("tls_ca")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate_key(self) -> typing.Optional[builtins.str]:
        '''x509 certificate for connecting to the database.

        This must be a PEM encoded version of the private key and the certificate combined.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        '''
        result = self._values.get("tls_certificate_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMysqlLegacy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionMysqlLegacyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlLegacyOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21a0d7c251f6ab261d96f51a8849f174559a775bf5ce80ed78808d80f3f168aa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetServiceAccountJson")
    def reset_service_account_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountJson", []))

    @jsii.member(jsii_name="resetTlsCa")
    def reset_tls_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCa", []))

    @jsii.member(jsii_name="resetTlsCertificateKey")
    def reset_tls_certificate_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificateKey", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJsonInput")
    def service_account_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaInput")
    def tls_ca_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCaInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKeyInput")
    def tls_certificate_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d6e4361216dd48f2c7763ae5f3cfa326ad3d5457157441723635f01d5f8a002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__056d92df5953d202cc84c804a8f7c544bb368723f62ab6bfbdd60d9a12ab4d2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2115db0949411b2504c4a7669ac782012d94935799cedab8e663c790987c24b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b9b79ac5e9c9bc314f7735cc1525ffc7c7fab9de2bb64b8e1d669c43af1db65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2867fce260802d7b154ee8cbe77c3f5657bb6c5930227cfc30932cde5b1cdfec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80f1e6bba57a8d436946f583cf8ef8fc4841a7410aa386556cb1ea52d4c0aaf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9d9158740d9feef9ab43d1ea37382faec9738e8716124e022a50ae0b9b46f0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__224c110d79c1346557e9927009e6caffa6fd46acf22e05b25f858a0277634760)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJson")
    def service_account_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountJson"))

    @service_account_json.setter
    def service_account_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e30640ba59938b1b20f342b336005162e1fdba3abb1d6dd0c09c820736914935)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCa")
    def tls_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCa"))

    @tls_ca.setter
    def tls_ca(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__145fa035f045ff7a56a81db2e19ee9b64b5e218a50488b4afd24b92cce3926e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKey")
    def tls_certificate_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificateKey"))

    @tls_certificate_key.setter
    def tls_certificate_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a822c9d887970f8a86b1f9d3c7e4495a5f7a5a7cd56b4a83e9a465b00e9e8892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e15eb3be436ea0a0cf52e26bd426b59527c388759b6e0b9a51109a1329f78ab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0343e425caa1b4486f753c03a72aa184e0592c35673353f29139b10264879d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionMysqlLegacy]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMysqlLegacy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMysqlLegacy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38bcd5bbe040fc758c59041a767ccd6d0c41c6025f759e27d6fff70788dab1c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSecretBackendConnectionMysqlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48db1a14a3c40ad054e4d7ce1b92d879b8653a876f50d563572c29572b46ec06)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetServiceAccountJson")
    def reset_service_account_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountJson", []))

    @jsii.member(jsii_name="resetTlsCa")
    def reset_tls_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCa", []))

    @jsii.member(jsii_name="resetTlsCertificateKey")
    def reset_tls_certificate_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificateKey", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJsonInput")
    def service_account_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaInput")
    def tls_ca_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCaInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKeyInput")
    def tls_certificate_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e64736a6fd10580afc13a372b8e8ab59867f72876c52f213997530ce8da03d7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23f9f92bcc05cd03cea8ca32f89aa2dc928bde28cfc5edbed5af26a2f98596bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b27f63a25b2f87badfc3b1c956fc541ef8e0224fc8957b4aa30b0af3f36652cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2782ba81ed2a3dfb547366a9992ee4950c3970780ffc5a01f856fcd5e14545c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ab1b4d7afc432d1e6a232bdb9b13c6c43efe5cc3d7f384bb0d85ba3692ecbd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42931f913a2338fb139c6174649d9cdb4ebacbb9cae6c366c225c7f9f20278ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c261647a8408e2ac8ae9aae6c807f1be5e46e79a9620191d05e07889e48b05c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f842e79fb2fdf4a75acc44aa979492ca26797199fa4ce9e86a77127d93f2553c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJson")
    def service_account_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountJson"))

    @service_account_json.setter
    def service_account_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eaec1bd77ed99d299f06f30c5d2682f4ee2901ca09036d99d8c03ef442cdf77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCa")
    def tls_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCa"))

    @tls_ca.setter
    def tls_ca(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08f6e4a6810016c33d9edd2405e04fd1a723828e3505579e5b586d6777c8a4f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKey")
    def tls_certificate_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificateKey"))

    @tls_certificate_key.setter
    def tls_certificate_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cee2209f9e9a249fd58797e6ccf96b7033460270c64a5bf625ed1c7595e7f4f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959496b5242d7ac2e7c30ec049f51d5de5b87b880b4adbac66bc823e53896463)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f54f03bc6482096a4896e499938a16df8a7a338ed01161126762fb5618af963c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabaseSecretBackendConnectionMysql]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMysql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMysql],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4897780af5b4854c6d35aef902b1d465011c3b01a2654dfdc76a9282e722c4c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlRds",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "connection_url": "connectionUrl",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "service_account_json": "serviceAccountJson",
        "tls_ca": "tlsCa",
        "tls_certificate_key": "tlsCertificateKey",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionMysqlRds:
    def __init__(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate_key: x509 certificate for connecting to the database. This must be a PEM encoded version of the private key and the certificate combined. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7f890b39635534eb705e5a772f9432b94588f05c520db1cd548669c82ab6230)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument service_account_json", value=service_account_json, expected_type=type_hints["service_account_json"])
            check_type(argname="argument tls_ca", value=tls_ca, expected_type=type_hints["tls_ca"])
            check_type(argname="argument tls_certificate_key", value=tls_certificate_key, expected_type=type_hints["tls_certificate_key"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if service_account_json is not None:
            self._values["service_account_json"] = service_account_json
        if tls_ca is not None:
            self._values["tls_ca"] = tls_ca
        if tls_certificate_key is not None:
            self._values["tls_certificate_key"] = tls_certificate_key
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Specify alternative authorization type. (Only 'gcp_iam' is valid currently).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_account_json(self) -> typing.Optional[builtins.str]:
        '''A JSON encoded credential for use with IAM authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        '''
        result = self._values.get("service_account_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_ca(self) -> typing.Optional[builtins.str]:
        '''x509 CA file for validating the certificate presented by the MySQL server. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        '''
        result = self._values.get("tls_ca")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate_key(self) -> typing.Optional[builtins.str]:
        '''x509 certificate for connecting to the database.

        This must be a PEM encoded version of the private key and the certificate combined.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate_key DatabaseSecretBackendConnection#tls_certificate_key}
        '''
        result = self._values.get("tls_certificate_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionMysqlRds(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionMysqlRdsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionMysqlRdsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cfed8f81bbaf47fc1a6ee627a339a7bb1dd6485d695a88f6dd662e6bdd23769)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetServiceAccountJson")
    def reset_service_account_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountJson", []))

    @jsii.member(jsii_name="resetTlsCa")
    def reset_tls_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCa", []))

    @jsii.member(jsii_name="resetTlsCertificateKey")
    def reset_tls_certificate_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificateKey", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJsonInput")
    def service_account_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaInput")
    def tls_ca_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCaInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKeyInput")
    def tls_certificate_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1c60532e6dbfb6030d5ad4398d950cf176223c1f5f114cc20d5654fe9f8ead7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453da01e5d042a779efc3426f05a11fbead57198f94167cd8aa90dd5f6e78b34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d63ba162704c5228bd05fbfce7ba9d2d4042008a985fe6ee1483a54b6b5a540)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__611446bbc0262d07ff9f96d449a86618cde438ecbcb861ad82a1347dec386548)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__773e3f4cf1253291e3a9fc3b738d54718152425f082921493ea1e3300fbf6689)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1c5f31c6a90948bba5dfeedc5004231c856e36bcf6c8de947b8350466d5ffe6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cb7c136248e2458c1f8c82ebe1aafab01b4436dd0cbe5e9930b302b41132d39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f8a9979ab4c94a442e62cfa27b83a24a55d2ed16eea039bda63567d10f9c4fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJson")
    def service_account_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountJson"))

    @service_account_json.setter
    def service_account_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fa61a2481e37fef8c3bcd126e77c534bfb9cf16419383a6083468fe595e1de8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCa")
    def tls_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCa"))

    @tls_ca.setter
    def tls_ca(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48467c673476a70f7be859beb1ec59cb21039776d14f87cbebf62c69eb30d943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateKey")
    def tls_certificate_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificateKey"))

    @tls_certificate_key.setter
    def tls_certificate_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa3277ca0899b57a490138b366fad4317fa0283d1aa0bb5390c4e4869db63f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf2c12b23e2f8029fc505f2ca5a649ec26a69942a2421ca954c419bfe2e49212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a1a15f05d8a5df3b3786df0f67d0948d91e90e76a59963f2397895f18d684c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionMysqlRds]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionMysqlRds], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionMysqlRds],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23b80ff4cc1e01309e612681613ced447bedbb5631d5bca2765efd5e972b5260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionOracle",
    jsii_struct_bases=[],
    name_mapping={
        "connection_url": "connectionUrl",
        "disconnect_sessions": "disconnectSessions",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "split_statements": "splitStatements",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionOracle:
    def __init__(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        disconnect_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        split_statements: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disconnect_sessions: Set to true to disconnect any open sessions prior to running the revocation statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disconnect_sessions DatabaseSecretBackendConnection#disconnect_sessions}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param split_statements: Set to true in order to split statements after semi-colons. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#split_statements DatabaseSecretBackendConnection#split_statements}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e6bcc0c58fa57ab784004c16cf49d0f8a14c498e22c2ad68825184998a7474)
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument disconnect_sessions", value=disconnect_sessions, expected_type=type_hints["disconnect_sessions"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument split_statements", value=split_statements, expected_type=type_hints["split_statements"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if disconnect_sessions is not None:
            self._values["disconnect_sessions"] = disconnect_sessions
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if split_statements is not None:
            self._values["split_statements"] = split_statements
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disconnect_sessions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to disconnect any open sessions prior to running the revocation statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disconnect_sessions DatabaseSecretBackendConnection#disconnect_sessions}
        '''
        result = self._values.get("disconnect_sessions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def split_statements(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true in order to split statements after semi-colons.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#split_statements DatabaseSecretBackendConnection#split_statements}
        '''
        result = self._values.get("split_statements")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionOracle(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionOracleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionOracleOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21987430b1f22fc3f621b9af4214a3bbe10a15362e640cf83d348f6abf1b9e85)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetDisconnectSessions")
    def reset_disconnect_sessions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisconnectSessions", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetSplitStatements")
    def reset_split_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSplitStatements", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="disconnectSessionsInput")
    def disconnect_sessions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disconnectSessionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="splitStatementsInput")
    def split_statements_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "splitStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6225857bf1cc7c95ed92df425f87e51dbe4053fbba04b5144554c2bf5b9df7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disconnectSessions")
    def disconnect_sessions(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disconnectSessions"))

    @disconnect_sessions.setter
    def disconnect_sessions(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__758c8a076c78282cfbe12baf9ae0afde8281258da3fc1a69dc9d64cf4379acbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disconnectSessions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3947c5fdbd9f1a706670f55657df003bf20018fc9b9fef69d376bed48358a51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__625bbe43ee79f357e732f4baa482ab4d95fd0bb5d6121a7a5efc946ccfb69d0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5333b9256e1139461ab914dcb1312da934585e8df87d1e7d20906218d5f4234c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7ddf4405195ecb004e204a44e3739668189ba6954a9185591810582714a90b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9e89b09df9ec08eccf596d4de96c73136f24420acc5fb2caea6939c206438ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f953298bf0bdca53ab72a904ca94975de80affb61b5686876118432058c0ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="splitStatements")
    def split_statements(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "splitStatements"))

    @split_statements.setter
    def split_statements(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdeae56345b242e73f1a74f2a7fe1122d7e71418eb1e97cf8af248235d83159c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "splitStatements", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7448c70def54c68a442c6a4f81d316f1d042f58f65eb57790d5aa901fa279337)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bafde8e9c4fb52e3cf822ebb759db3f1b72bb17bc4c4baf4e3a1dbc06dca6ea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabaseSecretBackendConnectionOracle]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionOracle], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionOracle],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef9ec907c51b175de7977b011beb93fc4da6a41f5316a7c728601d7b00931e0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionPostgresql",
    jsii_struct_bases=[],
    name_mapping={
        "auth_type": "authType",
        "connection_url": "connectionUrl",
        "disable_escaping": "disableEscaping",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_authentication": "passwordAuthentication",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "private_key": "privateKey",
        "self_managed": "selfManaged",
        "service_account_json": "serviceAccountJson",
        "tls_ca": "tlsCa",
        "tls_certificate": "tlsCertificate",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionPostgresql:
    def __init__(
        self,
        *,
        auth_type: typing.Optional[builtins.str] = None,
        connection_url: typing.Optional[builtins.str] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_authentication: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        private_key: typing.Optional[builtins.str] = None,
        self_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        service_account_json: typing.Optional[builtins.str] = None,
        tls_ca: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_type: Specify alternative authorization type. (Only 'gcp_iam' is valid currently). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_authentication: When set to ``scram-sha-256``, passwords will be hashed by Vault before being sent to PostgreSQL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_authentication DatabaseSecretBackendConnection#password_authentication}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param private_key: The secret key used for the x509 client certificate. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key DatabaseSecretBackendConnection#private_key}
        :param self_managed: If set, allows onboarding static roles with a rootless connection configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#self_managed DatabaseSecretBackendConnection#self_managed}
        :param service_account_json: A JSON encoded credential for use with IAM authorization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        :param tls_ca: The x509 CA file for validating the certificate presented by the PostgreSQL server. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        :param tls_certificate: The x509 client certificate for connecting to the database. Must be PEM encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate DatabaseSecretBackendConnection#tls_certificate}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca22bb0cf1bddccc82d406f2c418bfd31a774546feecd62aafef104572ac80b)
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument disable_escaping", value=disable_escaping, expected_type=type_hints["disable_escaping"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_authentication", value=password_authentication, expected_type=type_hints["password_authentication"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument self_managed", value=self_managed, expected_type=type_hints["self_managed"])
            check_type(argname="argument service_account_json", value=service_account_json, expected_type=type_hints["service_account_json"])
            check_type(argname="argument tls_ca", value=tls_ca, expected_type=type_hints["tls_ca"])
            check_type(argname="argument tls_certificate", value=tls_certificate, expected_type=type_hints["tls_certificate"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if disable_escaping is not None:
            self._values["disable_escaping"] = disable_escaping
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_authentication is not None:
            self._values["password_authentication"] = password_authentication
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if private_key is not None:
            self._values["private_key"] = private_key
        if self_managed is not None:
            self._values["self_managed"] = self_managed
        if service_account_json is not None:
            self._values["service_account_json"] = service_account_json
        if tls_ca is not None:
            self._values["tls_ca"] = tls_ca
        if tls_certificate is not None:
            self._values["tls_certificate"] = tls_certificate
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Specify alternative authorization type. (Only 'gcp_iam' is valid currently).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#auth_type DatabaseSecretBackendConnection#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_escaping(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable special character escaping in username and password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        '''
        result = self._values.get("disable_escaping")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_authentication(self) -> typing.Optional[builtins.str]:
        '''When set to ``scram-sha-256``, passwords will be hashed by Vault before being sent to PostgreSQL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_authentication DatabaseSecretBackendConnection#password_authentication}
        '''
        result = self._values.get("password_authentication")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def private_key(self) -> typing.Optional[builtins.str]:
        '''The secret key used for the x509 client certificate. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key DatabaseSecretBackendConnection#private_key}
        '''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def self_managed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, allows onboarding static roles with a rootless connection configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#self_managed DatabaseSecretBackendConnection#self_managed}
        '''
        result = self._values.get("self_managed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def service_account_json(self) -> typing.Optional[builtins.str]:
        '''A JSON encoded credential for use with IAM authorization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#service_account_json DatabaseSecretBackendConnection#service_account_json}
        '''
        result = self._values.get("service_account_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_ca(self) -> typing.Optional[builtins.str]:
        '''The x509 CA file for validating the certificate presented by the PostgreSQL server. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_ca DatabaseSecretBackendConnection#tls_ca}
        '''
        result = self._values.get("tls_ca")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate(self) -> typing.Optional[builtins.str]:
        '''The x509 client certificate for connecting to the database. Must be PEM encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls_certificate DatabaseSecretBackendConnection#tls_certificate}
        '''
        result = self._values.get("tls_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionPostgresql(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionPostgresqlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionPostgresqlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d1c54a5a91d52383db09faf629f57b5a90cdbf90a2cda7b888d2f19f9552bc5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetDisableEscaping")
    def reset_disable_escaping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableEscaping", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordAuthentication")
    def reset_password_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordAuthentication", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetPrivateKey")
    def reset_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKey", []))

    @jsii.member(jsii_name="resetSelfManaged")
    def reset_self_managed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSelfManaged", []))

    @jsii.member(jsii_name="resetServiceAccountJson")
    def reset_service_account_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountJson", []))

    @jsii.member(jsii_name="resetTlsCa")
    def reset_tls_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCa", []))

    @jsii.member(jsii_name="resetTlsCertificate")
    def reset_tls_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificate", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="disableEscapingInput")
    def disable_escaping_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableEscapingInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordAuthenticationInput")
    def password_authentication_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordAuthenticationInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="selfManagedInput")
    def self_managed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "selfManagedInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJsonInput")
    def service_account_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountJsonInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCaInput")
    def tls_ca_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCaInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateInput")
    def tls_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__209a499c6e0ce89b268fe5606e93cac8f46b48f0cf52f97327772c13bcd3b356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d98109aff37145409e329b8dadf3b02d2d803acfc03feb68decc066a75a141ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableEscaping")
    def disable_escaping(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableEscaping"))

    @disable_escaping.setter
    def disable_escaping(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76004d918736f6f86396639004d227882d2d499fda016a6ecef1064715ac4f6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableEscaping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfefd50292ef954652cb183b6bb47b27571defde0bdfc2396ff95cf91cedd241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e36648d9355586110400afe982475a4e8f54dcbc87ef39a244c247393cbb91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87e35c322846de4b931558336bc00020086feebd71334795fd9c4c93efb051dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c92d1f060f0f8777b80ae9bfe202774ab0334533760bc6c9e9bfaf391243bf4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordAuthentication")
    def password_authentication(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordAuthentication"))

    @password_authentication.setter
    def password_authentication(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea684df685cf2cab63d8046019e3303c94028e7467e162a298d1f1f4806f9c73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordAuthentication", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83e105debb069a3756dda7fa72a0c9fa530404203b86b660a6a34790307e4b5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__096e5626b7ab81c1017b339e2ac74507103ef5297f948c1c5c7fc60d9d05f851)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9350cc1064664ab25c65e2df89c636c9012d4b976bebefa4d190a9678d8c6dfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="selfManaged")
    def self_managed(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "selfManaged"))

    @self_managed.setter
    def self_managed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__745aff1ec9ff03bfb0d47c323e684e869e0a6922df493f875ea794c47da5b141)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "selfManaged", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountJson")
    def service_account_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountJson"))

    @service_account_json.setter
    def service_account_json(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2aa9114d53c30561cc2fb5c88e5a842f80777fddcccabc7921896ca02da6364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountJson", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCa")
    def tls_ca(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCa"))

    @tls_ca.setter
    def tls_ca(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b07bd482b2220187f1bce0f8d632b5afd1e6e25474f3de0fc3d5d4d534de2d90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCa", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCertificate")
    def tls_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificate"))

    @tls_certificate.setter
    def tls_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a21116fd9cad9da28ead661c47059aa2dc6e694f773aba5fec16bdbb246a5ccd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c57b0cd15fd0d30ebec463edaeab400d18646699729d397d88cb9fc2ca002e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__890b837825c4d4a2f410a95a061c895a4ed399c6bedbda4ad4f4c76276436a3e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionPostgresql]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionPostgresql], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionPostgresql],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71247ef71e653ab5e6722b7888b44ed3424ae19e18df3ffa8f7994a4f31c9a1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionRedis",
    jsii_struct_bases=[],
    name_mapping={
        "host": "host",
        "password": "password",
        "username": "username",
        "ca_cert": "caCert",
        "insecure_tls": "insecureTls",
        "port": "port",
        "tls": "tls",
    },
)
class DatabaseSecretBackendConnectionRedis:
    def __init__(
        self,
        *,
        host: builtins.str,
        password: builtins.str,
        username: builtins.str,
        ca_cert: typing.Optional[builtins.str] = None,
        insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        port: typing.Optional[jsii.Number] = None,
        tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param host: Specifies the host to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#host DatabaseSecretBackendConnection#host}
        :param password: Specifies the password corresponding to the given username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param username: Specifies the username for Vault to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param ca_cert: The contents of a PEM-encoded CA cert file to use to verify the Redis server's identity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_cert DatabaseSecretBackendConnection#ca_cert}
        :param insecure_tls: Specifies whether to skip verification of the server certificate when using TLS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        :param port: The transport port to use to connect to Redis. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        :param tls: Specifies whether to use TLS when connecting to Redis. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f0407d01fcf3512e8b31ae3a90c36c78581e009055376cee27f8f428423c5d6)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument ca_cert", value=ca_cert, expected_type=type_hints["ca_cert"])
            check_type(argname="argument insecure_tls", value=insecure_tls, expected_type=type_hints["insecure_tls"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument tls", value=tls, expected_type=type_hints["tls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
            "password": password,
            "username": username,
        }
        if ca_cert is not None:
            self._values["ca_cert"] = ca_cert
        if insecure_tls is not None:
            self._values["insecure_tls"] = insecure_tls
        if port is not None:
            self._values["port"] = port
        if tls is not None:
            self._values["tls"] = tls

    @builtins.property
    def host(self) -> builtins.str:
        '''Specifies the host to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#host DatabaseSecretBackendConnection#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''Specifies the password corresponding to the given username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''Specifies the username for Vault to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ca_cert(self) -> typing.Optional[builtins.str]:
        '''The contents of a PEM-encoded CA cert file to use to verify the Redis server's identity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#ca_cert DatabaseSecretBackendConnection#ca_cert}
        '''
        result = self._values.get("ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def insecure_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to skip verification of the server certificate when using TLS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#insecure_tls DatabaseSecretBackendConnection#insecure_tls}
        '''
        result = self._values.get("insecure_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''The transport port to use to connect to Redis.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#port DatabaseSecretBackendConnection#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Specifies whether to use TLS when connecting to Redis.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#tls DatabaseSecretBackendConnection#tls}
        '''
        result = self._values.get("tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionRedis(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionRedisElasticache",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "password": "password",
        "region": "region",
        "username": "username",
    },
)
class DatabaseSecretBackendConnectionRedisElasticache:
    def __init__(
        self,
        *,
        url: builtins.str,
        password: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param url: The configuration endpoint for the ElastiCache cluster to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#url DatabaseSecretBackendConnection#url}
        :param password: The AWS secret key id to use to talk to ElastiCache. If omitted the credentials chain provider is used instead. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param region: The AWS region where the ElastiCache cluster is hosted. If omitted the plugin tries to infer the region from the environment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#region DatabaseSecretBackendConnection#region}
        :param username: The AWS access key id to use to talk to ElastiCache. If omitted the credentials chain provider is used instead. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa184cd71473eba5dd2cd57c76d9d203a367bba0dea8327d1049e7a796fce7f4)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url": url,
        }
        if password is not None:
            self._values["password"] = password
        if region is not None:
            self._values["region"] = region
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def url(self) -> builtins.str:
        '''The configuration endpoint for the ElastiCache cluster to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#url DatabaseSecretBackendConnection#url}
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The AWS secret key id to use to talk to ElastiCache.

        If omitted the credentials chain provider is used instead.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The AWS region where the ElastiCache cluster is hosted.

        If omitted the plugin tries to infer the region from the environment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#region DatabaseSecretBackendConnection#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The AWS access key id to use to talk to ElastiCache.

        If omitted the credentials chain provider is used instead.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionRedisElasticache(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionRedisElasticacheOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionRedisElasticacheOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a8275b858252f23aaeda33357b287cc94e908f749afefb82e927b713d166e1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9ee50756820a4a7a511bdf0a54785f0719dbc6fdd56e714783391aa7f23c01e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__683bdcf17ae0768591371ae967c8f5dc3b819cce7f95586f22dd49708b260b69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c81a3b819395623c76950af72692c764c00d59ceffdd5ae355406ec6f591297)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48b056553ea062f991ec51a76a0c3a75b11e1d58f437288ebea50c0c7fd07e07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionRedisElasticache]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionRedisElasticache], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionRedisElasticache],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8e574a91882ad4fe746dee67dad808185d579ad69ae39e0db4fb33a94357a43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseSecretBackendConnectionRedisOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionRedisOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__085fe5bd54f01c76e028897ea2b74bc5b7fd6d9e61b507a598e79d8a7dc4243b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCaCert")
    def reset_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCert", []))

    @jsii.member(jsii_name="resetInsecureTls")
    def reset_insecure_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureTls", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetTls")
    def reset_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTls", []))

    @builtins.property
    @jsii.member(jsii_name="caCertInput")
    def ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="insecureTlsInput")
    def insecure_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "insecureTlsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsInput")
    def tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="caCert")
    def ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCert"))

    @ca_cert.setter
    def ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01fd313f049157f5fc7eb0e376ae8bcf97f5d0f5f7574a512730f8e34278b6cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c92ba127fae4faabd3b05645e85b1649ba1bf32423bd5e2e1d10c8bd78f7d50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="insecureTls")
    def insecure_tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "insecureTls"))

    @insecure_tls.setter
    def insecure_tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04b58d151d3d03010601573f7d0cb33d87e7626dbe440923d9c7d397d82dc24b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "insecureTls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5df578a5f542cbe67467f6757eb348742688666a988a758a4ffaea90b2fc41f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e86d7acb9e4311083b2e3fc2efc3296781500bcd467d09d948470d53815d5755)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tls")
    def tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tls"))

    @tls.setter
    def tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37a208143b405e4520cf12c8cf35a5fae89fff60917eab6fb2d8115beacf3faa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b84bf61555d0403b07fcd2ab21675a5d45cbc0341abd52e1f95d36be0758102)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabaseSecretBackendConnectionRedis]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionRedis], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionRedis],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1666c7ef04f4c5e257f554dd1a17bcb2b0ce00a6ff235e92bca13198e177dbfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionRedshift",
    jsii_struct_bases=[],
    name_mapping={
        "connection_url": "connectionUrl",
        "disable_escaping": "disableEscaping",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionRedshift:
    def __init__(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param disable_escaping: Disable special character escaping in username and password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e58dea7473b1b300f98eda99fa54f35af48a845a49adf53ce061033a9ec1d8d1)
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument disable_escaping", value=disable_escaping, expected_type=type_hints["disable_escaping"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if disable_escaping is not None:
            self._values["disable_escaping"] = disable_escaping
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_escaping(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable special character escaping in username and password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#disable_escaping DatabaseSecretBackendConnection#disable_escaping}
        '''
        result = self._values.get("disable_escaping")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionRedshift(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionRedshiftOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionRedshiftOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab8b5207785e5db9c11f8af97186ba64960b436b020100999c51beb0f4750ad8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetDisableEscaping")
    def reset_disable_escaping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableEscaping", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="disableEscapingInput")
    def disable_escaping_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableEscapingInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53406f24d3d2ed5758e0cf91f9b2635f824a4ddb2f0cf4ce18aa8fca07459bd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableEscaping")
    def disable_escaping(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableEscaping"))

    @disable_escaping.setter
    def disable_escaping(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca164a25f8a0ea1dd3ce26b7d7b949babf37d6c2963a7663ed5d291351075e71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableEscaping", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d93b56cb35882f756a75e975e53259463e443b6fda357685c6ef0ff8bd0131d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6b6018029f849e148045854eeb174b0a70e8b7f5aeaebfff3ad54f2af2ff1ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82fdd305f3516f6d28671dc830295c45ca6d53801d47f6230eb92884f967f443)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3d6eca05672c062a269e2db4c9218e25138500044237d537ed355b9e71badd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__994c4c52d085df587604513417f6f9fa74faf02f80b17a8b21d8d9f367e7d5d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2cd03ee3b09f5d06e006e0b6026a8b25ad054a9c8e5ebe6aa6cea252675bc1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b333dc0be1405372eb17877662f7f51ea5ceab3e164afaf2018440a8dba6c65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__716e20329e2dcdddd18aac3ca6622c63644a006d97e694d03ca6c6c9d26e8ed8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionRedshift]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionRedshift], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionRedshift],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__182bbe7726770edeff373a8a8cc4183049249eca20b6d1b678941c65d144749b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionSnowflake",
    jsii_struct_bases=[],
    name_mapping={
        "connection_url": "connectionUrl",
        "max_connection_lifetime": "maxConnectionLifetime",
        "max_idle_connections": "maxIdleConnections",
        "max_open_connections": "maxOpenConnections",
        "password": "password",
        "password_wo": "passwordWo",
        "password_wo_version": "passwordWoVersion",
        "private_key_wo": "privateKeyWo",
        "private_key_wo_version": "privateKeyWoVersion",
        "username": "username",
        "username_template": "usernameTemplate",
    },
)
class DatabaseSecretBackendConnectionSnowflake:
    def __init__(
        self,
        *,
        connection_url: typing.Optional[builtins.str] = None,
        max_connection_lifetime: typing.Optional[jsii.Number] = None,
        max_idle_connections: typing.Optional[jsii.Number] = None,
        max_open_connections: typing.Optional[jsii.Number] = None,
        password: typing.Optional[builtins.str] = None,
        password_wo: typing.Optional[builtins.str] = None,
        password_wo_version: typing.Optional[jsii.Number] = None,
        private_key_wo: typing.Optional[builtins.str] = None,
        private_key_wo_version: typing.Optional[jsii.Number] = None,
        username: typing.Optional[builtins.str] = None,
        username_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_url: Connection string to use to connect to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        :param max_connection_lifetime: Maximum number of seconds a connection may be reused. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        :param max_idle_connections: Maximum number of idle connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        :param max_open_connections: Maximum number of open connections to the database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        :param password: The root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        :param password_wo: Write-only field for the root credential password used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        :param password_wo_version: Version counter for root credential password write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        :param private_key_wo: The private key configured for the admin user in Snowflake. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key_wo DatabaseSecretBackendConnection#private_key_wo}
        :param private_key_wo_version: Version counter for the private key key-pair credentials write-only field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key_wo_version DatabaseSecretBackendConnection#private_key_wo_version}
        :param username: The root credential username used in the connection URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        :param username_template: Username generation template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74b801c1254e9d497343551365c10840855e1b868da5ea320051a781ebca545a)
            check_type(argname="argument connection_url", value=connection_url, expected_type=type_hints["connection_url"])
            check_type(argname="argument max_connection_lifetime", value=max_connection_lifetime, expected_type=type_hints["max_connection_lifetime"])
            check_type(argname="argument max_idle_connections", value=max_idle_connections, expected_type=type_hints["max_idle_connections"])
            check_type(argname="argument max_open_connections", value=max_open_connections, expected_type=type_hints["max_open_connections"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument password_wo", value=password_wo, expected_type=type_hints["password_wo"])
            check_type(argname="argument password_wo_version", value=password_wo_version, expected_type=type_hints["password_wo_version"])
            check_type(argname="argument private_key_wo", value=private_key_wo, expected_type=type_hints["private_key_wo"])
            check_type(argname="argument private_key_wo_version", value=private_key_wo_version, expected_type=type_hints["private_key_wo_version"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument username_template", value=username_template, expected_type=type_hints["username_template"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection_url is not None:
            self._values["connection_url"] = connection_url
        if max_connection_lifetime is not None:
            self._values["max_connection_lifetime"] = max_connection_lifetime
        if max_idle_connections is not None:
            self._values["max_idle_connections"] = max_idle_connections
        if max_open_connections is not None:
            self._values["max_open_connections"] = max_open_connections
        if password is not None:
            self._values["password"] = password
        if password_wo is not None:
            self._values["password_wo"] = password_wo
        if password_wo_version is not None:
            self._values["password_wo_version"] = password_wo_version
        if private_key_wo is not None:
            self._values["private_key_wo"] = private_key_wo
        if private_key_wo_version is not None:
            self._values["private_key_wo_version"] = private_key_wo_version
        if username is not None:
            self._values["username"] = username
        if username_template is not None:
            self._values["username_template"] = username_template

    @builtins.property
    def connection_url(self) -> typing.Optional[builtins.str]:
        '''Connection string to use to connect to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#connection_url DatabaseSecretBackendConnection#connection_url}
        '''
        result = self._values.get("connection_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_connection_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of seconds a connection may be reused.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_connection_lifetime DatabaseSecretBackendConnection#max_connection_lifetime}
        '''
        result = self._values.get("max_connection_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_idle_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of idle connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_idle_connections DatabaseSecretBackendConnection#max_idle_connections}
        '''
        result = self._values.get("max_idle_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_open_connections(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of open connections to the database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#max_open_connections DatabaseSecretBackendConnection#max_open_connections}
        '''
        result = self._values.get("max_open_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password DatabaseSecretBackendConnection#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo(self) -> typing.Optional[builtins.str]:
        '''Write-only field for the root credential password used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo DatabaseSecretBackendConnection#password_wo}
        '''
        result = self._values.get("password_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for root credential password write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#password_wo_version DatabaseSecretBackendConnection#password_wo_version}
        '''
        result = self._values.get("password_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def private_key_wo(self) -> typing.Optional[builtins.str]:
        '''The private key configured for the admin user in Snowflake.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key_wo DatabaseSecretBackendConnection#private_key_wo}
        '''
        result = self._values.get("private_key_wo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_wo_version(self) -> typing.Optional[jsii.Number]:
        '''Version counter for the private key key-pair credentials write-only field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#private_key_wo_version DatabaseSecretBackendConnection#private_key_wo_version}
        '''
        result = self._values.get("private_key_wo_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The root credential username used in the connection URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username DatabaseSecretBackendConnection#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username_template(self) -> typing.Optional[builtins.str]:
        '''Username generation template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/vault/5.2.1/docs/resources/database_secret_backend_connection#username_template DatabaseSecretBackendConnection#username_template}
        '''
        result = self._values.get("username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseSecretBackendConnectionSnowflake(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseSecretBackendConnectionSnowflakeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-vault.databaseSecretBackendConnection.DatabaseSecretBackendConnectionSnowflakeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8abef43618208b14f038ad63fb2591c61627f3aad2f84ceb62d090791c5c0b8d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionUrl")
    def reset_connection_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionUrl", []))

    @jsii.member(jsii_name="resetMaxConnectionLifetime")
    def reset_max_connection_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxConnectionLifetime", []))

    @jsii.member(jsii_name="resetMaxIdleConnections")
    def reset_max_idle_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxIdleConnections", []))

    @jsii.member(jsii_name="resetMaxOpenConnections")
    def reset_max_open_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxOpenConnections", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPasswordWo")
    def reset_password_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWo", []))

    @jsii.member(jsii_name="resetPasswordWoVersion")
    def reset_password_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordWoVersion", []))

    @jsii.member(jsii_name="resetPrivateKeyWo")
    def reset_private_key_wo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyWo", []))

    @jsii.member(jsii_name="resetPrivateKeyWoVersion")
    def reset_private_key_wo_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyWoVersion", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetUsernameTemplate")
    def reset_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernameTemplate", []))

    @builtins.property
    @jsii.member(jsii_name="connectionUrlInput")
    def connection_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetimeInput")
    def max_connection_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxConnectionLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnectionsInput")
    def max_idle_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxIdleConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnectionsInput")
    def max_open_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxOpenConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoInput")
    def password_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordWoInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersionInput")
    def password_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "passwordWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyWoInput")
    def private_key_wo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyWoInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyWoVersionInput")
    def private_key_wo_version_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "privateKeyWoVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameTemplateInput")
    def username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionUrl")
    def connection_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionUrl"))

    @connection_url.setter
    def connection_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae45dfb73f9adc12fbfee2030ac84cc46a2ac5045b3d75ec6243dba16908a93a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxConnectionLifetime")
    def max_connection_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxConnectionLifetime"))

    @max_connection_lifetime.setter
    def max_connection_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb23ef8e4425d8ee7d24f27fa642a545f4371463eb61d35358088a239df8cdb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxConnectionLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxIdleConnections")
    def max_idle_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxIdleConnections"))

    @max_idle_connections.setter
    def max_idle_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab587b6e89fa58a093fab3f740741db4d6d04f98381ce04452ebe90b844de5ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxIdleConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxOpenConnections")
    def max_open_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxOpenConnections"))

    @max_open_connections.setter
    def max_open_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d924c7f457c8dae352f0f2b7944012399d55725ee9a0435c876b7cad697e083e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxOpenConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64db4135dbec3bb5123765698e0ec12e251bde4c4c4095a60a19944cd2cc4c12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWo")
    def password_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordWo"))

    @password_wo.setter
    def password_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bcdbc89f9233c8a8fcc5dc9c87fdc89bd9753604b534c4991f2348b139ef1c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="passwordWoVersion")
    def password_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "passwordWoVersion"))

    @password_wo_version.setter
    def password_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61e3cb4e83edd38844e1047a21906342c2cc03450f305d74b78a8a66c143c70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyWo")
    def private_key_wo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyWo"))

    @private_key_wo.setter
    def private_key_wo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74c99c802d184ed9d60f05286e0f7d1552a850055561b93117ff78c4dbfac4c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyWo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKeyWoVersion")
    def private_key_wo_version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "privateKeyWoVersion"))

    @private_key_wo_version.setter
    def private_key_wo_version(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8292d8bcf3af4effa03f65daa4c3cb79f4d543a2559265ecf1f4255e07c62d91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyWoVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4422b5154b3b86505c685fa300a1afd58c2b5488e9a182c0ed8f9523567ac65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usernameTemplate")
    def username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernameTemplate"))

    @username_template.setter
    def username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5936755c578f2f72d412c0da0efe5a4a930f7331db969f7b285e002018ab372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usernameTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DatabaseSecretBackendConnectionSnowflake]:
        return typing.cast(typing.Optional[DatabaseSecretBackendConnectionSnowflake], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabaseSecretBackendConnectionSnowflake],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8beb022f0cf0a01f8a7fcfaed4467a55fbb622b0e29a2f07e1a82220053b3082)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DatabaseSecretBackendConnection",
    "DatabaseSecretBackendConnectionCassandra",
    "DatabaseSecretBackendConnectionCassandraOutputReference",
    "DatabaseSecretBackendConnectionConfig",
    "DatabaseSecretBackendConnectionCouchbase",
    "DatabaseSecretBackendConnectionCouchbaseOutputReference",
    "DatabaseSecretBackendConnectionElasticsearch",
    "DatabaseSecretBackendConnectionElasticsearchOutputReference",
    "DatabaseSecretBackendConnectionHana",
    "DatabaseSecretBackendConnectionHanaOutputReference",
    "DatabaseSecretBackendConnectionInfluxdb",
    "DatabaseSecretBackendConnectionInfluxdbOutputReference",
    "DatabaseSecretBackendConnectionMongodb",
    "DatabaseSecretBackendConnectionMongodbOutputReference",
    "DatabaseSecretBackendConnectionMongodbatlas",
    "DatabaseSecretBackendConnectionMongodbatlasOutputReference",
    "DatabaseSecretBackendConnectionMssql",
    "DatabaseSecretBackendConnectionMssqlOutputReference",
    "DatabaseSecretBackendConnectionMysql",
    "DatabaseSecretBackendConnectionMysqlAurora",
    "DatabaseSecretBackendConnectionMysqlAuroraOutputReference",
    "DatabaseSecretBackendConnectionMysqlLegacy",
    "DatabaseSecretBackendConnectionMysqlLegacyOutputReference",
    "DatabaseSecretBackendConnectionMysqlOutputReference",
    "DatabaseSecretBackendConnectionMysqlRds",
    "DatabaseSecretBackendConnectionMysqlRdsOutputReference",
    "DatabaseSecretBackendConnectionOracle",
    "DatabaseSecretBackendConnectionOracleOutputReference",
    "DatabaseSecretBackendConnectionPostgresql",
    "DatabaseSecretBackendConnectionPostgresqlOutputReference",
    "DatabaseSecretBackendConnectionRedis",
    "DatabaseSecretBackendConnectionRedisElasticache",
    "DatabaseSecretBackendConnectionRedisElasticacheOutputReference",
    "DatabaseSecretBackendConnectionRedisOutputReference",
    "DatabaseSecretBackendConnectionRedshift",
    "DatabaseSecretBackendConnectionRedshiftOutputReference",
    "DatabaseSecretBackendConnectionSnowflake",
    "DatabaseSecretBackendConnectionSnowflakeOutputReference",
]

publication.publish()

def _typecheckingstub__6c0d5a3815da3620665ede1bbb53a54944253da2a56e46e4dd6fe2d95077ff35(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backend: builtins.str,
    name: builtins.str,
    allowed_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    cassandra: typing.Optional[typing.Union[DatabaseSecretBackendConnectionCassandra, typing.Dict[builtins.str, typing.Any]]] = None,
    couchbase: typing.Optional[typing.Union[DatabaseSecretBackendConnectionCouchbase, typing.Dict[builtins.str, typing.Any]]] = None,
    data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    elasticsearch: typing.Optional[typing.Union[DatabaseSecretBackendConnectionElasticsearch, typing.Dict[builtins.str, typing.Any]]] = None,
    hana: typing.Optional[typing.Union[DatabaseSecretBackendConnectionHana, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    influxdb: typing.Optional[typing.Union[DatabaseSecretBackendConnectionInfluxdb, typing.Dict[builtins.str, typing.Any]]] = None,
    mongodb: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMongodb, typing.Dict[builtins.str, typing.Any]]] = None,
    mongodbatlas: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMongodbatlas, typing.Dict[builtins.str, typing.Any]]] = None,
    mssql: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMssql, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysql, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_aurora: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysqlAurora, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_legacy: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysqlLegacy, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_rds: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysqlRds, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    oracle: typing.Optional[typing.Union[DatabaseSecretBackendConnectionOracle, typing.Dict[builtins.str, typing.Any]]] = None,
    plugin_name: typing.Optional[builtins.str] = None,
    postgresql: typing.Optional[typing.Union[DatabaseSecretBackendConnectionPostgresql, typing.Dict[builtins.str, typing.Any]]] = None,
    redis: typing.Optional[typing.Union[DatabaseSecretBackendConnectionRedis, typing.Dict[builtins.str, typing.Any]]] = None,
    redis_elasticache: typing.Optional[typing.Union[DatabaseSecretBackendConnectionRedisElasticache, typing.Dict[builtins.str, typing.Any]]] = None,
    redshift: typing.Optional[typing.Union[DatabaseSecretBackendConnectionRedshift, typing.Dict[builtins.str, typing.Any]]] = None,
    root_rotation_statements: typing.Optional[typing.Sequence[builtins.str]] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    snowflake: typing.Optional[typing.Union[DatabaseSecretBackendConnectionSnowflake, typing.Dict[builtins.str, typing.Any]]] = None,
    verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__bc1ea2afca1cc665b5faa92b1257a0a9f5c3e22ca11e89069adbe96b7d508deb(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51c72012b9fbf2ab2ee5c91b0869b41784cdecd72e1ca9990cfce59d761c3304(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__372aa857104a1bcfe00934a3a63842629991b1bf1bdc18332646d6b1026f3742(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__847456513cb6417549e9279b019915ae1d669e7462a5a457709d77b57604a539(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__259872f41940672b2d1d3449a3216d2fcfc30c8e613bf37f07ec4e71b344505b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d5d7b8e5503227724608cab8e42f6945a211f970b21ef210ff536c7475ac9f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75883e892b7b08e6e7daa847a2e4104f062b15754c3e58f583e3eed8dec167d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2100f15d57ce41f80b55ee3ff1bf22311cd26ac13c1530c6e38a755d8bf0c8a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ff326c3ea85b0db935e4a4cc5ff4c1a4bc6bd122ea0ee300676e34cfb015305(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a4f6877fa313b11d07a17c70dd73ca2090ba39fc1e6ad82deefbc659baeebf0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__462f37ddcf5ed9d5893dd24d1e40952a9ca8c754b49cdd4ee101b0709031f664(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a7b6d14483f5f2f3acfc29ce98c18c51269266f475ff254a1e5976b61000b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__889e737b809ac33ac47875ba82011ca305b0f91e3d5a44a64e6783bc0033bb43(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed522a23a3383e5f557f73263a0ba8138883f42b80cc3875f59d046b52988912(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16f6bd8ea1ef98b3c22050de90dd6177ebc4e6fb023e09001759d59f1eb13c64(
    *,
    connect_timeout: typing.Optional[jsii.Number] = None,
    hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    password: typing.Optional[builtins.str] = None,
    pem_bundle: typing.Optional[builtins.str] = None,
    pem_json: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    protocol_version: typing.Optional[jsii.Number] = None,
    skip_verification: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86930fac2ed6ebb799cd7105d559596aca54946a8d56af307378f5fa228314de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bcd259ce38f8ea1aeaca2d7166d655040ae2a557d149c18724fcced1aea1078(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__278def805539b971174352bd459b2b8787bc0ca32673ac0eb9ea2c62f2065277(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0babf0d91766d40ca7f79fe5b829d6574d00ae69e0f53cf2501de05428c70fb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944d0d75386a7144eb3f419a16ba06ccc23e447c165e3b19dd0d6f49d28e02c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec349756ab880c5b85f6ee81b7d0fd1aae249d225f90ab0fe620ebbd5016bb25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692f70aa7a241fc628957f087bba89398747863e4fe8ec42cbcdf7915fd9c321(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a9cc58d526f3af716358ad8126165def7a5c967a2093f241e63146cb3d044ef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66bec6e9dc857246e3cdad051454ec5c30850050ee93e0b174c9eaa73e21e07b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c943c28b88b1ea060e503a0d506fa432fce6e3806380f3f4fd9ed0e56487880c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e049a2ba4817280de17dfa22566e3a797fe2c041aaadae3d8d88249b462ccc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__332417dfd8872c211daa4e1e1ba657e7551dbe0f016e176394b281bda7e35fb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__929dad8c507c0daa5a4241909971a10c53d9df716081467fa90f81455fcc3a15(
    value: typing.Optional[DatabaseSecretBackendConnectionCassandra],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0847902127aee9281509569452b51fae959ac561f6c87946ea0c492655092ddb(
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
    allowed_roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    cassandra: typing.Optional[typing.Union[DatabaseSecretBackendConnectionCassandra, typing.Dict[builtins.str, typing.Any]]] = None,
    couchbase: typing.Optional[typing.Union[DatabaseSecretBackendConnectionCouchbase, typing.Dict[builtins.str, typing.Any]]] = None,
    data: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    disable_automated_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    elasticsearch: typing.Optional[typing.Union[DatabaseSecretBackendConnectionElasticsearch, typing.Dict[builtins.str, typing.Any]]] = None,
    hana: typing.Optional[typing.Union[DatabaseSecretBackendConnectionHana, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    influxdb: typing.Optional[typing.Union[DatabaseSecretBackendConnectionInfluxdb, typing.Dict[builtins.str, typing.Any]]] = None,
    mongodb: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMongodb, typing.Dict[builtins.str, typing.Any]]] = None,
    mongodbatlas: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMongodbatlas, typing.Dict[builtins.str, typing.Any]]] = None,
    mssql: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMssql, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysql, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_aurora: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysqlAurora, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_legacy: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysqlLegacy, typing.Dict[builtins.str, typing.Any]]] = None,
    mysql_rds: typing.Optional[typing.Union[DatabaseSecretBackendConnectionMysqlRds, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    oracle: typing.Optional[typing.Union[DatabaseSecretBackendConnectionOracle, typing.Dict[builtins.str, typing.Any]]] = None,
    plugin_name: typing.Optional[builtins.str] = None,
    postgresql: typing.Optional[typing.Union[DatabaseSecretBackendConnectionPostgresql, typing.Dict[builtins.str, typing.Any]]] = None,
    redis: typing.Optional[typing.Union[DatabaseSecretBackendConnectionRedis, typing.Dict[builtins.str, typing.Any]]] = None,
    redis_elasticache: typing.Optional[typing.Union[DatabaseSecretBackendConnectionRedisElasticache, typing.Dict[builtins.str, typing.Any]]] = None,
    redshift: typing.Optional[typing.Union[DatabaseSecretBackendConnectionRedshift, typing.Dict[builtins.str, typing.Any]]] = None,
    root_rotation_statements: typing.Optional[typing.Sequence[builtins.str]] = None,
    rotation_period: typing.Optional[jsii.Number] = None,
    rotation_schedule: typing.Optional[builtins.str] = None,
    rotation_window: typing.Optional[jsii.Number] = None,
    snowflake: typing.Optional[typing.Union[DatabaseSecretBackendConnectionSnowflake, typing.Dict[builtins.str, typing.Any]]] = None,
    verify_connection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5510161a437422a74b4c96a676cd938743f1e480f64a5a815aa118a7f2647a2f(
    *,
    hosts: typing.Sequence[builtins.str],
    password: builtins.str,
    username: builtins.str,
    base64_pem: typing.Optional[builtins.str] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a3bfb5de8aa08fd4e74cc6247d59010cfc6f12dd97b059dad1d913cd5229e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42f97940e11e5e7cda31bd76d930b5ef51517c2af20acc16e54006211a92386a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a9699c016711553005fc2b470d90d724668b243a64e0abf968d4cc273c6a11c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87e36f43b69755bd0828e004604abe0b363dafb118d9388589a212269528570b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__348898f41302670970f4144276783e87136cd45e9f9f9d02c9ad533c62b48768(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1348b5caa82f63e767d0f352899444ecde78e17f9a19dd15e2ebc5845cf0f1e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a122280378f2e3cf2b4b39930f0f9760065818c82dd58cb46aaef2f737b7892b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22b10126159c85a79dd1c2078c880298cf95e1b6a8e1624b10961a058ec15557(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a95c0198ef58488325251b640dd746a92328a1a21fc15322605f5d89e204edaf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7ab16ccc300f249f30a431a3be97a802c042f3d63f1ec9b42446b3d615dc43a(
    value: typing.Optional[DatabaseSecretBackendConnectionCouchbase],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__813a4819d65f1ec63deef3d99ecc9720678485491411f5d918b6e6b418a1306f(
    *,
    password: builtins.str,
    url: builtins.str,
    username: builtins.str,
    ca_cert: typing.Optional[builtins.str] = None,
    ca_path: typing.Optional[builtins.str] = None,
    client_cert: typing.Optional[builtins.str] = None,
    client_key: typing.Optional[builtins.str] = None,
    insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tls_server_name: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdfde47c66b4e5c88a2a2427780b5bdf2fe31d3f4db5dadf04bc87c97c1876e6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ef15526b31b3fb4bfb79840e09f8504fdd729b0a0def4af5bdad2b728ba7197(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cf0b3a00d4cc202607291474e0af94913d25414811bcaac026a155715a395ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b9e2164762d01c35e9cfa9955d67fe1db83aabf5d1740480b0ada364bb258ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78f1d6a2d40a2eb846b708c1246bf16eac08efac56f3e03a60f905aa6588eb44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2a2816d7d34dca7b92351f789b294395a9da0a23c9d5aa648aff67a7776456(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76a37169d75c131c47890a3ee74fb5c9e5daee8f8f7a2c5377d00f23c0466eeb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f06251bd228441c1af3284df8da8b95d403e6894dbe15fe4432649776cfebbc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b47bd6506ecbc9ba5331d07e7aad1157ef82fbe65aa6b480487470053ec09020(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1cea49426286255a5bcec1c30c7e42eedc06f477d577f668ff46dd1aaa8dc8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd861b4026d46b6d9bda2bf80a6db379837689bed764e1f07e564a2fdd48e49a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e49bdf4b260510892458fcc824f16383c5d349e12f50bcd879b5f3c8ea298f97(
    value: typing.Optional[DatabaseSecretBackendConnectionElasticsearch],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712968b2b3ccc279e6c67ad8d58abc2efe75e07e3954084825e4dde4b1d173b6(
    *,
    connection_url: typing.Optional[builtins.str] = None,
    disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50bd0914ea61a6d5acf3a375c30c88b86c06e8dd54c41989e710e233ad4c20f8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ceb9b4a7178394ea555dab0c9cd8397445c1ef61d7bac8198f5c438abdd74a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ac94623b5ec54f07ddcdfb2ff00b546dcb7f41ef22d3057291be9fe09b1bc23(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9998468bfeeaa90594113692bb77db01403852c1b2667d5a5461a805569b67d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9762f6378f8c186b0a64faa28e5d7948f8bd7b1f011bb056ba400a72ea49d266(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b60efd638368d91f9408350d1a2918e8f6b75038a11128013003bd4795413073(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae2af10f8fe2a71d553fd181f2010c86ee24d3c59583e36fb3c2a480bac2ebd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db41f7607efce7066ffbb7a50d6f3ad7298ff67684237e9416511eda4052f60c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__372b7144b7e1e5e8c92685c8d0348a225d4bf627435ddae3148a3dbb2dd08ccc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6a5f218be2743a185395ef4303295593c3cd93880decdf1c67cb6622a86dd50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd869116178460d6cb1d8676f29c95a1d3cdac19650ab8b59bd351929d0cbee(
    value: typing.Optional[DatabaseSecretBackendConnectionHana],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b50c6d1de18d1a927c9c0c4e352103624fade9750ad1446d2feb4340ac4af12a(
    *,
    host: builtins.str,
    password: builtins.str,
    username: builtins.str,
    connect_timeout: typing.Optional[jsii.Number] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pem_bundle: typing.Optional[builtins.str] = None,
    pem_json: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9e10fff3a6b5f70d8a50e4971d04df3019e44b3d663541c0431d03ce7a632b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad9283d9dc629c7ec4773b3b38f4b2a8e31714a18aad94455d45102197d0a2dc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adae2d8ce5b14ba42c38476611612f99375212c1bdc44207e2e94b1f573b5dfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5312c682f08660567e477a9e54131deda7c27c359ec0a50e94f092a7ab6a6177(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35fc1c0dd9f37600406f5694584c3e8b71f41a32840240544aa30e79cb9bab1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ce43de6205c3fd2a95d5266ca1285a7db7962731aaf7be74b6be72e6c15d91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a3864d98614599b8cd974158f7898d65e2b5da8b8dbb4a39c3eafbfa1e92052(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f99d05ac50ed9fc46e3a4c718eb4b0d68a2f95e09269653b6867a00ad29c3d7b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17abdb02924b4dd51db07cf1a5214ca31e85e118c61a636538654047623808b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb3636171a720e480b54a87d029a92d8bd1e0cf76421d7f42968dec25494fc5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdb290c0ee7705fdf32b34f195a06d7bb1e9d83834bb17ec1cd742a4816dbee7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4383e3e62c73c913ed1aec6d61c131cabcde9fa7d49344a66802ea041da568a4(
    value: typing.Optional[DatabaseSecretBackendConnectionInfluxdb],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d986b37f6918d4b6df0760a720a1c33247b912bf3fc2a3770c9eae07f74be99(
    *,
    connection_url: typing.Optional[builtins.str] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83cbf9abd3a9d23a046ae4d40dbaff228ac7945b2ab18ad5e227dd4d42ff1e95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c097380aefe2cd3a9a23cb55032b7ed447339ebd325ab4eefbb2b8b45d07bf90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c323f516dc59699d533fca78edfc390673dd51336553148638da406ac07f6e00(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50509a1ee4b43834300d2dd0230ecdb080e5c6957a44619a6130c1622a020659(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73008b969752ee21ec8155b9a9e8f096e8ed1727a94c4cab26b9f48ff567d361(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0284ecf296027f193fd67db693c75a361d4ab7451f5e9533c4b1d834eb2efd37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd6bc190bdacd41cdcc717d467048256f0315136c17797951ddbef6a44fa2d21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc667655f863a8ed21a51212813fc5eab4da1a3b534cc1d572b367a6c3c8e29(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc85b69c211e3646dffcd7498861aca96bf222b40bd1149f09e03270ffcfd672(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9be336bcc871efd871f2392886de53f8bec3b36547f5c6e964bd263eaa134b09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__739ecb9c809232b8d2a18b4cff15b3cb2da55ba6a03bb4efdea08ac414d40732(
    value: typing.Optional[DatabaseSecretBackendConnectionMongodb],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08dde2f5021d8a411280e477dbd661f0c9cb6b90870d6807db6db56db78bf3c3(
    *,
    private_key: builtins.str,
    project_id: builtins.str,
    public_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c56bf7afa1dff19450dd2309ae270905eb23eb70e0f9cca7422eacb52143810b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fdeb6f2c7e01f51446df241052352b9835d7005eea15d830b7fd8616892d0ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd6feade9eb601162c27842b6db477f87536f8d2c2731a4d09c3e6fea2e1ae83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfcbdafdc0f16a575aa0dba38fe5f1f786d9f60c04665f1bf3ac12bbc5e97578(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b78f96240011ef2b74a31ca0dbb2c9bdd71cb8cefecedd4909762e928e8e12d5(
    value: typing.Optional[DatabaseSecretBackendConnectionMongodbatlas],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c8f78aaac5238cfe6b074c692f6573095d52500f3ec5941ba4bc8a216502d79(
    *,
    connection_url: typing.Optional[builtins.str] = None,
    contained_db: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7a884065eac1a32a7a6f1f8957cd5f2b12fef8ad883bd49b267e54781b930b0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76adeb9557632174632ada90eb9c5736c902352fcf0b16a09189fdcfe097ac9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d410c4ab8968280035f573fe7540433309ec1b7f917a0e0cb3c4f77f831c5c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab309a246a04558f4f6472c20d0aca10f5c5a08f40c4aae6b1738a143498a39f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61a514dd6752751fd616490075723da7ee9761c252dd12c29e7a9ad8030401c0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ffa80f50be95ee21d62e8e7154c152f5ad1c05546320fb4218e8b76fd0352fe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d2ab4ddc39ff65c1b9bad1495999626ccf336e3e249caa4e171d8db4c4c6191(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4ad4918802bdf3c9db57d86dbf27c6f4bf07957589e311e865ef55a8f76482f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5fa12b114958097e8a695e419cb2ed952ece119cae18adf1b377dc700e60507(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6fe0b92206a89d82d97d4fa976e733fc93968e0eef7dd0d9f0cfadb13e4e0d9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244367f87d3478c56ecd43abef9bdcbf905492417bf8ea8d4c974755911859bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2caab17b3c522874ce82a64f8a7c4d2e44b3d696a978f691c41614215646e78d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59a2591db6bf474bd00174a43da4d44d9a44c8fe7b85ec3add3dff0237455a95(
    value: typing.Optional[DatabaseSecretBackendConnectionMssql],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf7abd4a1cf6ea2dbd6fc522e03e73b98341dbfa5219b84276360fb11444df13(
    *,
    auth_type: typing.Optional[builtins.str] = None,
    connection_url: typing.Optional[builtins.str] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    service_account_json: typing.Optional[builtins.str] = None,
    tls_ca: typing.Optional[builtins.str] = None,
    tls_certificate_key: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__721cf4b6720e013234dd31a8ce4bba47692ec1ef070292c2976c8b97f5342c21(
    *,
    auth_type: typing.Optional[builtins.str] = None,
    connection_url: typing.Optional[builtins.str] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    service_account_json: typing.Optional[builtins.str] = None,
    tls_ca: typing.Optional[builtins.str] = None,
    tls_certificate_key: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f308af1eb44d630360c272e5556552ff96e627e401b635a5a97d6b7009266a27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f0d939a8dff5fd17e9a1adce2f3a5afd7e9f8140eaca1f67c98d9775456baf2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7c5d84f79e8082fd26ab7f3b3970a36efc0c9328ee09d391b21a67e6e3a18a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09ac502162f28c541ac2d3632c9d053cec40f6d81a8cceca7f1c821f9b75b622(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d59bf3d265affbc3ac0c35d6ac8427ae75db39273e1b111c0b67f30971771f84(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb3f4bf2ef91400779f8f6af7382622bc7b0a783720a8f9f1882a1c922856d7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecda563f77b9dad59f6228cf5a86731fe3da31dd969cbacb373c0f854e243be7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f91edaf58a25ff18cbf297cc2243207ac80a528bbfec7420d81867044524918e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f76134f0dfc4422a720f7babb9dddbd684ef00b6d62da9b88204cbdf41ddf408(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__828aede2bba16a36361f3136075460ee9790624543029ca344ebbfff43c938d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb233af184a5f7d4106d48335b336b777dc43c818dcd9fe09b4d34bab5c019c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b3bcb497ff39834871814cb61bf71d55552697af9db6d6065e8ef103901dcf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b601a9fc41d8ce207733e258a47bdc56ba40678b2c65ae6da669f901512d6e37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec6801d17baa5f300f1d87eca5389fb35a6972cbc2509057977b8c88ff6da1e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68f44da2845c14c513be55640633193c615d0fa23c24f406f885d3cf464a503b(
    value: typing.Optional[DatabaseSecretBackendConnectionMysqlAurora],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b027525e7c7c5b55e80d015bbb97ba1291a1c1f914c5de3578fd6b2d85a36868(
    *,
    auth_type: typing.Optional[builtins.str] = None,
    connection_url: typing.Optional[builtins.str] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    service_account_json: typing.Optional[builtins.str] = None,
    tls_ca: typing.Optional[builtins.str] = None,
    tls_certificate_key: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21a0d7c251f6ab261d96f51a8849f174559a775bf5ce80ed78808d80f3f168aa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d6e4361216dd48f2c7763ae5f3cfa326ad3d5457157441723635f01d5f8a002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__056d92df5953d202cc84c804a8f7c544bb368723f62ab6bfbdd60d9a12ab4d2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2115db0949411b2504c4a7669ac782012d94935799cedab8e663c790987c24b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b9b79ac5e9c9bc314f7735cc1525ffc7c7fab9de2bb64b8e1d669c43af1db65(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2867fce260802d7b154ee8cbe77c3f5657bb6c5930227cfc30932cde5b1cdfec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f1e6bba57a8d436946f583cf8ef8fc4841a7410aa386556cb1ea52d4c0aaf9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9d9158740d9feef9ab43d1ea37382faec9738e8716124e022a50ae0b9b46f0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__224c110d79c1346557e9927009e6caffa6fd46acf22e05b25f858a0277634760(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e30640ba59938b1b20f342b336005162e1fdba3abb1d6dd0c09c820736914935(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__145fa035f045ff7a56a81db2e19ee9b64b5e218a50488b4afd24b92cce3926e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a822c9d887970f8a86b1f9d3c7e4495a5f7a5a7cd56b4a83e9a465b00e9e8892(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e15eb3be436ea0a0cf52e26bd426b59527c388759b6e0b9a51109a1329f78ab4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0343e425caa1b4486f753c03a72aa184e0592c35673353f29139b10264879d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38bcd5bbe040fc758c59041a767ccd6d0c41c6025f759e27d6fff70788dab1c5(
    value: typing.Optional[DatabaseSecretBackendConnectionMysqlLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48db1a14a3c40ad054e4d7ce1b92d879b8653a876f50d563572c29572b46ec06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e64736a6fd10580afc13a372b8e8ab59867f72876c52f213997530ce8da03d7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23f9f92bcc05cd03cea8ca32f89aa2dc928bde28cfc5edbed5af26a2f98596bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b27f63a25b2f87badfc3b1c956fc541ef8e0224fc8957b4aa30b0af3f36652cd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2782ba81ed2a3dfb547366a9992ee4950c3970780ffc5a01f856fcd5e14545c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ab1b4d7afc432d1e6a232bdb9b13c6c43efe5cc3d7f384bb0d85ba3692ecbd0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42931f913a2338fb139c6174649d9cdb4ebacbb9cae6c366c225c7f9f20278ca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c261647a8408e2ac8ae9aae6c807f1be5e46e79a9620191d05e07889e48b05c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f842e79fb2fdf4a75acc44aa979492ca26797199fa4ce9e86a77127d93f2553c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eaec1bd77ed99d299f06f30c5d2682f4ee2901ca09036d99d8c03ef442cdf77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08f6e4a6810016c33d9edd2405e04fd1a723828e3505579e5b586d6777c8a4f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cee2209f9e9a249fd58797e6ccf96b7033460270c64a5bf625ed1c7595e7f4f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__959496b5242d7ac2e7c30ec049f51d5de5b87b880b4adbac66bc823e53896463(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f54f03bc6482096a4896e499938a16df8a7a338ed01161126762fb5618af963c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4897780af5b4854c6d35aef902b1d465011c3b01a2654dfdc76a9282e722c4c3(
    value: typing.Optional[DatabaseSecretBackendConnectionMysql],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7f890b39635534eb705e5a772f9432b94588f05c520db1cd548669c82ab6230(
    *,
    auth_type: typing.Optional[builtins.str] = None,
    connection_url: typing.Optional[builtins.str] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    service_account_json: typing.Optional[builtins.str] = None,
    tls_ca: typing.Optional[builtins.str] = None,
    tls_certificate_key: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cfed8f81bbaf47fc1a6ee627a339a7bb1dd6485d695a88f6dd662e6bdd23769(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1c60532e6dbfb6030d5ad4398d950cf176223c1f5f114cc20d5654fe9f8ead7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453da01e5d042a779efc3426f05a11fbead57198f94167cd8aa90dd5f6e78b34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d63ba162704c5228bd05fbfce7ba9d2d4042008a985fe6ee1483a54b6b5a540(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__611446bbc0262d07ff9f96d449a86618cde438ecbcb861ad82a1347dec386548(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__773e3f4cf1253291e3a9fc3b738d54718152425f082921493ea1e3300fbf6689(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1c5f31c6a90948bba5dfeedc5004231c856e36bcf6c8de947b8350466d5ffe6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cb7c136248e2458c1f8c82ebe1aafab01b4436dd0cbe5e9930b302b41132d39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f8a9979ab4c94a442e62cfa27b83a24a55d2ed16eea039bda63567d10f9c4fb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa61a2481e37fef8c3bcd126e77c534bfb9cf16419383a6083468fe595e1de8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48467c673476a70f7be859beb1ec59cb21039776d14f87cbebf62c69eb30d943(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa3277ca0899b57a490138b366fad4317fa0283d1aa0bb5390c4e4869db63f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2c12b23e2f8029fc505f2ca5a649ec26a69942a2421ca954c419bfe2e49212(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a1a15f05d8a5df3b3786df0f67d0948d91e90e76a59963f2397895f18d684c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23b80ff4cc1e01309e612681613ced447bedbb5631d5bca2765efd5e972b5260(
    value: typing.Optional[DatabaseSecretBackendConnectionMysqlRds],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4e6bcc0c58fa57ab784004c16cf49d0f8a14c498e22c2ad68825184998a7474(
    *,
    connection_url: typing.Optional[builtins.str] = None,
    disconnect_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    split_statements: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21987430b1f22fc3f621b9af4214a3bbe10a15362e640cf83d348f6abf1b9e85(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6225857bf1cc7c95ed92df425f87e51dbe4053fbba04b5144554c2bf5b9df7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__758c8a076c78282cfbe12baf9ae0afde8281258da3fc1a69dc9d64cf4379acbd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3947c5fdbd9f1a706670f55657df003bf20018fc9b9fef69d376bed48358a51(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__625bbe43ee79f357e732f4baa482ab4d95fd0bb5d6121a7a5efc946ccfb69d0c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5333b9256e1139461ab914dcb1312da934585e8df87d1e7d20906218d5f4234c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7ddf4405195ecb004e204a44e3739668189ba6954a9185591810582714a90b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9e89b09df9ec08eccf596d4de96c73136f24420acc5fb2caea6939c206438ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f953298bf0bdca53ab72a904ca94975de80affb61b5686876118432058c0ef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdeae56345b242e73f1a74f2a7fe1122d7e71418eb1e97cf8af248235d83159c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7448c70def54c68a442c6a4f81d316f1d042f58f65eb57790d5aa901fa279337(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bafde8e9c4fb52e3cf822ebb759db3f1b72bb17bc4c4baf4e3a1dbc06dca6ea1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef9ec907c51b175de7977b011beb93fc4da6a41f5316a7c728601d7b00931e0c(
    value: typing.Optional[DatabaseSecretBackendConnectionOracle],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca22bb0cf1bddccc82d406f2c418bfd31a774546feecd62aafef104572ac80b(
    *,
    auth_type: typing.Optional[builtins.str] = None,
    connection_url: typing.Optional[builtins.str] = None,
    disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_authentication: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    private_key: typing.Optional[builtins.str] = None,
    self_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    service_account_json: typing.Optional[builtins.str] = None,
    tls_ca: typing.Optional[builtins.str] = None,
    tls_certificate: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d1c54a5a91d52383db09faf629f57b5a90cdbf90a2cda7b888d2f19f9552bc5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__209a499c6e0ce89b268fe5606e93cac8f46b48f0cf52f97327772c13bcd3b356(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d98109aff37145409e329b8dadf3b02d2d803acfc03feb68decc066a75a141ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76004d918736f6f86396639004d227882d2d499fda016a6ecef1064715ac4f6e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfefd50292ef954652cb183b6bb47b27571defde0bdfc2396ff95cf91cedd241(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e36648d9355586110400afe982475a4e8f54dcbc87ef39a244c247393cbb91(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87e35c322846de4b931558336bc00020086feebd71334795fd9c4c93efb051dd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c92d1f060f0f8777b80ae9bfe202774ab0334533760bc6c9e9bfaf391243bf4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea684df685cf2cab63d8046019e3303c94028e7467e162a298d1f1f4806f9c73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83e105debb069a3756dda7fa72a0c9fa530404203b86b660a6a34790307e4b5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__096e5626b7ab81c1017b339e2ac74507103ef5297f948c1c5c7fc60d9d05f851(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9350cc1064664ab25c65e2df89c636c9012d4b976bebefa4d190a9678d8c6dfa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__745aff1ec9ff03bfb0d47c323e684e869e0a6922df493f875ea794c47da5b141(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2aa9114d53c30561cc2fb5c88e5a842f80777fddcccabc7921896ca02da6364(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b07bd482b2220187f1bce0f8d632b5afd1e6e25474f3de0fc3d5d4d534de2d90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a21116fd9cad9da28ead661c47059aa2dc6e694f773aba5fec16bdbb246a5ccd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89c57b0cd15fd0d30ebec463edaeab400d18646699729d397d88cb9fc2ca002e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__890b837825c4d4a2f410a95a061c895a4ed399c6bedbda4ad4f4c76276436a3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71247ef71e653ab5e6722b7888b44ed3424ae19e18df3ffa8f7994a4f31c9a1e(
    value: typing.Optional[DatabaseSecretBackendConnectionPostgresql],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f0407d01fcf3512e8b31ae3a90c36c78581e009055376cee27f8f428423c5d6(
    *,
    host: builtins.str,
    password: builtins.str,
    username: builtins.str,
    ca_cert: typing.Optional[builtins.str] = None,
    insecure_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    port: typing.Optional[jsii.Number] = None,
    tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa184cd71473eba5dd2cd57c76d9d203a367bba0dea8327d1049e7a796fce7f4(
    *,
    url: builtins.str,
    password: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a8275b858252f23aaeda33357b287cc94e908f749afefb82e927b713d166e1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9ee50756820a4a7a511bdf0a54785f0719dbc6fdd56e714783391aa7f23c01e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__683bdcf17ae0768591371ae967c8f5dc3b819cce7f95586f22dd49708b260b69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c81a3b819395623c76950af72692c764c00d59ceffdd5ae355406ec6f591297(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48b056553ea062f991ec51a76a0c3a75b11e1d58f437288ebea50c0c7fd07e07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e574a91882ad4fe746dee67dad808185d579ad69ae39e0db4fb33a94357a43(
    value: typing.Optional[DatabaseSecretBackendConnectionRedisElasticache],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__085fe5bd54f01c76e028897ea2b74bc5b7fd6d9e61b507a598e79d8a7dc4243b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01fd313f049157f5fc7eb0e376ae8bcf97f5d0f5f7574a512730f8e34278b6cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c92ba127fae4faabd3b05645e85b1649ba1bf32423bd5e2e1d10c8bd78f7d50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04b58d151d3d03010601573f7d0cb33d87e7626dbe440923d9c7d397d82dc24b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5df578a5f542cbe67467f6757eb348742688666a988a758a4ffaea90b2fc41f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e86d7acb9e4311083b2e3fc2efc3296781500bcd467d09d948470d53815d5755(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a208143b405e4520cf12c8cf35a5fae89fff60917eab6fb2d8115beacf3faa(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b84bf61555d0403b07fcd2ab21675a5d45cbc0341abd52e1f95d36be0758102(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1666c7ef04f4c5e257f554dd1a17bcb2b0ce00a6ff235e92bca13198e177dbfe(
    value: typing.Optional[DatabaseSecretBackendConnectionRedis],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e58dea7473b1b300f98eda99fa54f35af48a845a49adf53ce061033a9ec1d8d1(
    *,
    connection_url: typing.Optional[builtins.str] = None,
    disable_escaping: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab8b5207785e5db9c11f8af97186ba64960b436b020100999c51beb0f4750ad8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53406f24d3d2ed5758e0cf91f9b2635f824a4ddb2f0cf4ce18aa8fca07459bd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca164a25f8a0ea1dd3ce26b7d7b949babf37d6c2963a7663ed5d291351075e71(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d93b56cb35882f756a75e975e53259463e443b6fda357685c6ef0ff8bd0131d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6b6018029f849e148045854eeb174b0a70e8b7f5aeaebfff3ad54f2af2ff1ef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82fdd305f3516f6d28671dc830295c45ca6d53801d47f6230eb92884f967f443(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3d6eca05672c062a269e2db4c9218e25138500044237d537ed355b9e71badd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__994c4c52d085df587604513417f6f9fa74faf02f80b17a8b21d8d9f367e7d5d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2cd03ee3b09f5d06e006e0b6026a8b25ad054a9c8e5ebe6aa6cea252675bc1c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b333dc0be1405372eb17877662f7f51ea5ceab3e164afaf2018440a8dba6c65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__716e20329e2dcdddd18aac3ca6622c63644a006d97e694d03ca6c6c9d26e8ed8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__182bbe7726770edeff373a8a8cc4183049249eca20b6d1b678941c65d144749b(
    value: typing.Optional[DatabaseSecretBackendConnectionRedshift],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b801c1254e9d497343551365c10840855e1b868da5ea320051a781ebca545a(
    *,
    connection_url: typing.Optional[builtins.str] = None,
    max_connection_lifetime: typing.Optional[jsii.Number] = None,
    max_idle_connections: typing.Optional[jsii.Number] = None,
    max_open_connections: typing.Optional[jsii.Number] = None,
    password: typing.Optional[builtins.str] = None,
    password_wo: typing.Optional[builtins.str] = None,
    password_wo_version: typing.Optional[jsii.Number] = None,
    private_key_wo: typing.Optional[builtins.str] = None,
    private_key_wo_version: typing.Optional[jsii.Number] = None,
    username: typing.Optional[builtins.str] = None,
    username_template: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8abef43618208b14f038ad63fb2591c61627f3aad2f84ceb62d090791c5c0b8d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae45dfb73f9adc12fbfee2030ac84cc46a2ac5045b3d75ec6243dba16908a93a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb23ef8e4425d8ee7d24f27fa642a545f4371463eb61d35358088a239df8cdb1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab587b6e89fa58a093fab3f740741db4d6d04f98381ce04452ebe90b844de5ae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d924c7f457c8dae352f0f2b7944012399d55725ee9a0435c876b7cad697e083e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64db4135dbec3bb5123765698e0ec12e251bde4c4c4095a60a19944cd2cc4c12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bcdbc89f9233c8a8fcc5dc9c87fdc89bd9753604b534c4991f2348b139ef1c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61e3cb4e83edd38844e1047a21906342c2cc03450f305d74b78a8a66c143c70(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74c99c802d184ed9d60f05286e0f7d1552a850055561b93117ff78c4dbfac4c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8292d8bcf3af4effa03f65daa4c3cb79f4d543a2559265ecf1f4255e07c62d91(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4422b5154b3b86505c685fa300a1afd58c2b5488e9a182c0ed8f9523567ac65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5936755c578f2f72d412c0da0efe5a4a930f7331db969f7b285e002018ab372(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8beb022f0cf0a01f8a7fcfaed4467a55fbb622b0e29a2f07e1a82220053b3082(
    value: typing.Optional[DatabaseSecretBackendConnectionSnowflake],
) -> None:
    """Type checking stubs"""
    pass
