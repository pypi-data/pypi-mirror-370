'''
# `akeyless_target_db`

Refer to the Terraform Registry for docs: [`akeyless_target_db`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db).
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class TargetDb(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.targetDb.TargetDb",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db akeyless_target_db}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        db_type: builtins.str,
        name: builtins.str,
        db_name: typing.Optional[builtins.str] = None,
        db_server_certificates: typing.Optional[builtins.str] = None,
        db_server_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        mongodb_atlas: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
        mongodb_default_auth_db: typing.Optional[builtins.str] = None,
        mongodb_uri_options: typing.Optional[builtins.str] = None,
        oracle_service_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[builtins.str] = None,
        pwd: typing.Optional[builtins.str] = None,
        snowflake_account: typing.Optional[builtins.str] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ssl_certificate: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db akeyless_target_db} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_type: Database type: mysql/mssql/postgres/mongodb/snowflake/oracle/cassandra/redshift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_type TargetDb#db_type}
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#name TargetDb#name}
        :param db_name: Database name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_name TargetDb#db_name}
        :param db_server_certificates: Set of root certificate authorities in base64 encoding used by clients to verify server certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_server_certificates TargetDb#db_server_certificates}
        :param db_server_name: Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is provided. It is also included in the client's handshake to support virtual hosting unless it is an IP address Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_server_name TargetDb#db_server_name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#description TargetDb#description}
        :param host: Database host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#host TargetDb#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#id TargetDb#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#key TargetDb#key}
        :param mongodb_atlas: Flag, set database type to mongodb and the flag to true to create Mongo Atlas target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas TargetDb#mongodb_atlas}
        :param mongodb_atlas_api_private_key: MongoDB Atlas private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_api_private_key TargetDb#mongodb_atlas_api_private_key}
        :param mongodb_atlas_api_public_key: MongoDB Atlas public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_api_public_key TargetDb#mongodb_atlas_api_public_key}
        :param mongodb_atlas_project_id: MongoDB Atlas project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_project_id TargetDb#mongodb_atlas_project_id}
        :param mongodb_default_auth_db: MongoDB server default authentication database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_default_auth_db TargetDb#mongodb_default_auth_db}
        :param mongodb_uri_options: MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_uri_options TargetDb#mongodb_uri_options}
        :param oracle_service_name: oracle db service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#oracle_service_name TargetDb#oracle_service_name}
        :param port: Database port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#port TargetDb#port}
        :param pwd: Database password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#pwd TargetDb#pwd}
        :param snowflake_account: Snowflake account name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#snowflake_account TargetDb#snowflake_account}
        :param ssl: Enable/Disable SSL [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#ssl TargetDb#ssl}
        :param ssl_certificate: SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#ssl_certificate TargetDb#ssl_certificate}
        :param user_name: Database user name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#user_name TargetDb#user_name}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04ee075eae61cb54abe3dc00f017184cb0030deae9607e6e73b30acc53cc2126)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TargetDbConfig(
            db_type=db_type,
            name=name,
            db_name=db_name,
            db_server_certificates=db_server_certificates,
            db_server_name=db_server_name,
            description=description,
            host=host,
            id=id,
            key=key,
            mongodb_atlas=mongodb_atlas,
            mongodb_atlas_api_private_key=mongodb_atlas_api_private_key,
            mongodb_atlas_api_public_key=mongodb_atlas_api_public_key,
            mongodb_atlas_project_id=mongodb_atlas_project_id,
            mongodb_default_auth_db=mongodb_default_auth_db,
            mongodb_uri_options=mongodb_uri_options,
            oracle_service_name=oracle_service_name,
            port=port,
            pwd=pwd,
            snowflake_account=snowflake_account,
            ssl=ssl,
            ssl_certificate=ssl_certificate,
            user_name=user_name,
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
        '''Generates CDKTF code for importing a TargetDb resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TargetDb to import.
        :param import_from_id: The id of the existing TargetDb that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TargetDb to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26747a1e62a55b0076642ab77d5b590c88d2aa437c34aad73d1f692b1eb37d84)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDbName")
    def reset_db_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbName", []))

    @jsii.member(jsii_name="resetDbServerCertificates")
    def reset_db_server_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbServerCertificates", []))

    @jsii.member(jsii_name="resetDbServerName")
    def reset_db_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbServerName", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetMongodbAtlas")
    def reset_mongodb_atlas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlas", []))

    @jsii.member(jsii_name="resetMongodbAtlasApiPrivateKey")
    def reset_mongodb_atlas_api_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlasApiPrivateKey", []))

    @jsii.member(jsii_name="resetMongodbAtlasApiPublicKey")
    def reset_mongodb_atlas_api_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlasApiPublicKey", []))

    @jsii.member(jsii_name="resetMongodbAtlasProjectId")
    def reset_mongodb_atlas_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlasProjectId", []))

    @jsii.member(jsii_name="resetMongodbDefaultAuthDb")
    def reset_mongodb_default_auth_db(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbDefaultAuthDb", []))

    @jsii.member(jsii_name="resetMongodbUriOptions")
    def reset_mongodb_uri_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbUriOptions", []))

    @jsii.member(jsii_name="resetOracleServiceName")
    def reset_oracle_service_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleServiceName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetPwd")
    def reset_pwd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPwd", []))

    @jsii.member(jsii_name="resetSnowflakeAccount")
    def reset_snowflake_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnowflakeAccount", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetSslCertificate")
    def reset_ssl_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslCertificate", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

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
    @jsii.member(jsii_name="dbNameInput")
    def db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbServerCertificatesInput")
    def db_server_certificates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbServerCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="dbServerNameInput")
    def db_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbTypeInput")
    def db_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPrivateKeyInput")
    def mongodb_atlas_api_private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbAtlasApiPrivateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPublicKeyInput")
    def mongodb_atlas_api_public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbAtlasApiPublicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasInput")
    def mongodb_atlas_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "mongodbAtlasInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasProjectIdInput")
    def mongodb_atlas_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbAtlasProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbDefaultAuthDbInput")
    def mongodb_default_auth_db_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbDefaultAuthDbInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbUriOptionsInput")
    def mongodb_uri_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbUriOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleServiceNameInput")
    def oracle_service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleServiceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="pwdInput")
    def pwd_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pwdInput"))

    @builtins.property
    @jsii.member(jsii_name="snowflakeAccountInput")
    def snowflake_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snowflakeAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="sslCertificateInput")
    def ssl_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sslInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbName"))

    @db_name.setter
    def db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__046cd7002d32efa9afc4022d447c1edac4d5afd660bd66bbcdc47b961fa48d23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbName", value)

    @builtins.property
    @jsii.member(jsii_name="dbServerCertificates")
    def db_server_certificates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbServerCertificates"))

    @db_server_certificates.setter
    def db_server_certificates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a7046bec191393e72f3d70b139eab77e13d8616059e1af04706e78036cd074a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbServerCertificates", value)

    @builtins.property
    @jsii.member(jsii_name="dbServerName")
    def db_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbServerName"))

    @db_server_name.setter
    def db_server_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab1f2a0c37c9f3d3f6d643361500338b081ab8abd2d17e091c83cde1b4e6a472)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbServerName", value)

    @builtins.property
    @jsii.member(jsii_name="dbType")
    def db_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbType"))

    @db_type.setter
    def db_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a976017014c1c81795b6cff69b77c0e27fd1d15edcfa75e1710ba6736fd12f0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbType", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e727d9f2289e2c2edf56844c2b14d002fe6555fc2400e29fe3e2afcc4930181e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86a29c6497fdf69d0838d97b45ebeed3f9168d58dd60ebc75869ba9f79ad9fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e5a929dae341bbee72a3c3eb50ebb2699c053561318284beb11cddeaee96681)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dda047976deb350766cc710e2c299bbcd3c76b4a65ffc2063a1fd42f191b8f35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlas")
    def mongodb_atlas(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "mongodbAtlas"))

    @mongodb_atlas.setter
    def mongodb_atlas(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dffb39913171e38bf640a22ace5ab2fd0bb921f280aa929817f2815a9d5f856)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlas", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPrivateKey")
    def mongodb_atlas_api_private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasApiPrivateKey"))

    @mongodb_atlas_api_private_key.setter
    def mongodb_atlas_api_private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b578eaeb9f7086a07dd290643e960a3ebac03a47dd54499cf91ee39260e19167)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasApiPrivateKey", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPublicKey")
    def mongodb_atlas_api_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasApiPublicKey"))

    @mongodb_atlas_api_public_key.setter
    def mongodb_atlas_api_public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bcd83441bd63de03f3216386917615e3c86dfd03162b0473aea51b8a6f0ec53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasApiPublicKey", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasProjectId")
    def mongodb_atlas_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasProjectId"))

    @mongodb_atlas_project_id.setter
    def mongodb_atlas_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da26de7b59c65c2c2e03ed7974d2578a6bf719114cb285592372be2ae3cfd27e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasProjectId", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbDefaultAuthDb")
    def mongodb_default_auth_db(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbDefaultAuthDb"))

    @mongodb_default_auth_db.setter
    def mongodb_default_auth_db(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbea5e23e94b867822d342aca86add6586aa2890931a5263e044cadcc52743bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbDefaultAuthDb", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbUriOptions")
    def mongodb_uri_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbUriOptions"))

    @mongodb_uri_options.setter
    def mongodb_uri_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeb5f844dd9591ad45141da587e313d9a02d9df574f3202675e48dfd69c3738e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbUriOptions", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b515a6f658f6e1cab74b44fc47a1ba4504885d5656a46271ee38302671043a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="oracleServiceName")
    def oracle_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleServiceName"))

    @oracle_service_name.setter
    def oracle_service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6684d16e15cb119462c1d0c667eb4e24e79aee0216befeb64a59dadf0c522397)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleServiceName", value)

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "port"))

    @port.setter
    def port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__274ca015bd76a169122a9ed73b8499893d4f8e5bbd5dd3aae6975f0d087c3e49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property
    @jsii.member(jsii_name="pwd")
    def pwd(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pwd"))

    @pwd.setter
    def pwd(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bda53c72e854b59f38ae15d4d6ee8f3002ae5b84d418d6ad9f017063d06ed963)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pwd", value)

    @builtins.property
    @jsii.member(jsii_name="snowflakeAccount")
    def snowflake_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snowflakeAccount"))

    @snowflake_account.setter
    def snowflake_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4874536baada0e340002f2a38bd9f4f335f80786dba36594720d44ba7cdd4aa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snowflakeAccount", value)

    @builtins.property
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a56bcc29ef90ccbe0d4e518d3714147a56d72433cf2e2239799cbc5b2e567709)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value)

    @builtins.property
    @jsii.member(jsii_name="sslCertificate")
    def ssl_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslCertificate"))

    @ssl_certificate.setter
    def ssl_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__268620d2cd4435a525be5211a0a60992a4714fcbe6d79a527dba40c27dae65f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sslCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa26313425b45e5f1457d685f36f8c2dc85c555df54a90a732489270a6e4655b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="akeyless.targetDb.TargetDbConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "db_type": "dbType",
        "name": "name",
        "db_name": "dbName",
        "db_server_certificates": "dbServerCertificates",
        "db_server_name": "dbServerName",
        "description": "description",
        "host": "host",
        "id": "id",
        "key": "key",
        "mongodb_atlas": "mongodbAtlas",
        "mongodb_atlas_api_private_key": "mongodbAtlasApiPrivateKey",
        "mongodb_atlas_api_public_key": "mongodbAtlasApiPublicKey",
        "mongodb_atlas_project_id": "mongodbAtlasProjectId",
        "mongodb_default_auth_db": "mongodbDefaultAuthDb",
        "mongodb_uri_options": "mongodbUriOptions",
        "oracle_service_name": "oracleServiceName",
        "port": "port",
        "pwd": "pwd",
        "snowflake_account": "snowflakeAccount",
        "ssl": "ssl",
        "ssl_certificate": "sslCertificate",
        "user_name": "userName",
    },
)
class TargetDbConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        db_type: builtins.str,
        name: builtins.str,
        db_name: typing.Optional[builtins.str] = None,
        db_server_certificates: typing.Optional[builtins.str] = None,
        db_server_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        mongodb_atlas: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
        mongodb_default_auth_db: typing.Optional[builtins.str] = None,
        mongodb_uri_options: typing.Optional[builtins.str] = None,
        oracle_service_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[builtins.str] = None,
        pwd: typing.Optional[builtins.str] = None,
        snowflake_account: typing.Optional[builtins.str] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ssl_certificate: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param db_type: Database type: mysql/mssql/postgres/mongodb/snowflake/oracle/cassandra/redshift. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_type TargetDb#db_type}
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#name TargetDb#name}
        :param db_name: Database name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_name TargetDb#db_name}
        :param db_server_certificates: Set of root certificate authorities in base64 encoding used by clients to verify server certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_server_certificates TargetDb#db_server_certificates}
        :param db_server_name: Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is provided. It is also included in the client's handshake to support virtual hosting unless it is an IP address Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_server_name TargetDb#db_server_name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#description TargetDb#description}
        :param host: Database host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#host TargetDb#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#id TargetDb#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#key TargetDb#key}
        :param mongodb_atlas: Flag, set database type to mongodb and the flag to true to create Mongo Atlas target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas TargetDb#mongodb_atlas}
        :param mongodb_atlas_api_private_key: MongoDB Atlas private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_api_private_key TargetDb#mongodb_atlas_api_private_key}
        :param mongodb_atlas_api_public_key: MongoDB Atlas public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_api_public_key TargetDb#mongodb_atlas_api_public_key}
        :param mongodb_atlas_project_id: MongoDB Atlas project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_project_id TargetDb#mongodb_atlas_project_id}
        :param mongodb_default_auth_db: MongoDB server default authentication database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_default_auth_db TargetDb#mongodb_default_auth_db}
        :param mongodb_uri_options: MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_uri_options TargetDb#mongodb_uri_options}
        :param oracle_service_name: oracle db service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#oracle_service_name TargetDb#oracle_service_name}
        :param port: Database port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#port TargetDb#port}
        :param pwd: Database password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#pwd TargetDb#pwd}
        :param snowflake_account: Snowflake account name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#snowflake_account TargetDb#snowflake_account}
        :param ssl: Enable/Disable SSL [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#ssl TargetDb#ssl}
        :param ssl_certificate: SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#ssl_certificate TargetDb#ssl_certificate}
        :param user_name: Database user name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#user_name TargetDb#user_name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce27b52a60b1beacf141ae4cb9d305574d3c9b2da52165d192b3978508d9adc1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument db_type", value=db_type, expected_type=type_hints["db_type"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument db_name", value=db_name, expected_type=type_hints["db_name"])
            check_type(argname="argument db_server_certificates", value=db_server_certificates, expected_type=type_hints["db_server_certificates"])
            check_type(argname="argument db_server_name", value=db_server_name, expected_type=type_hints["db_server_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument mongodb_atlas", value=mongodb_atlas, expected_type=type_hints["mongodb_atlas"])
            check_type(argname="argument mongodb_atlas_api_private_key", value=mongodb_atlas_api_private_key, expected_type=type_hints["mongodb_atlas_api_private_key"])
            check_type(argname="argument mongodb_atlas_api_public_key", value=mongodb_atlas_api_public_key, expected_type=type_hints["mongodb_atlas_api_public_key"])
            check_type(argname="argument mongodb_atlas_project_id", value=mongodb_atlas_project_id, expected_type=type_hints["mongodb_atlas_project_id"])
            check_type(argname="argument mongodb_default_auth_db", value=mongodb_default_auth_db, expected_type=type_hints["mongodb_default_auth_db"])
            check_type(argname="argument mongodb_uri_options", value=mongodb_uri_options, expected_type=type_hints["mongodb_uri_options"])
            check_type(argname="argument oracle_service_name", value=oracle_service_name, expected_type=type_hints["oracle_service_name"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument pwd", value=pwd, expected_type=type_hints["pwd"])
            check_type(argname="argument snowflake_account", value=snowflake_account, expected_type=type_hints["snowflake_account"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument ssl_certificate", value=ssl_certificate, expected_type=type_hints["ssl_certificate"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "db_type": db_type,
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
        if db_name is not None:
            self._values["db_name"] = db_name
        if db_server_certificates is not None:
            self._values["db_server_certificates"] = db_server_certificates
        if db_server_name is not None:
            self._values["db_server_name"] = db_server_name
        if description is not None:
            self._values["description"] = description
        if host is not None:
            self._values["host"] = host
        if id is not None:
            self._values["id"] = id
        if key is not None:
            self._values["key"] = key
        if mongodb_atlas is not None:
            self._values["mongodb_atlas"] = mongodb_atlas
        if mongodb_atlas_api_private_key is not None:
            self._values["mongodb_atlas_api_private_key"] = mongodb_atlas_api_private_key
        if mongodb_atlas_api_public_key is not None:
            self._values["mongodb_atlas_api_public_key"] = mongodb_atlas_api_public_key
        if mongodb_atlas_project_id is not None:
            self._values["mongodb_atlas_project_id"] = mongodb_atlas_project_id
        if mongodb_default_auth_db is not None:
            self._values["mongodb_default_auth_db"] = mongodb_default_auth_db
        if mongodb_uri_options is not None:
            self._values["mongodb_uri_options"] = mongodb_uri_options
        if oracle_service_name is not None:
            self._values["oracle_service_name"] = oracle_service_name
        if port is not None:
            self._values["port"] = port
        if pwd is not None:
            self._values["pwd"] = pwd
        if snowflake_account is not None:
            self._values["snowflake_account"] = snowflake_account
        if ssl is not None:
            self._values["ssl"] = ssl
        if ssl_certificate is not None:
            self._values["ssl_certificate"] = ssl_certificate
        if user_name is not None:
            self._values["user_name"] = user_name

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
    def db_type(self) -> builtins.str:
        '''Database type: mysql/mssql/postgres/mongodb/snowflake/oracle/cassandra/redshift.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_type TargetDb#db_type}
        '''
        result = self._values.get("db_type")
        assert result is not None, "Required property 'db_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Target name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#name TargetDb#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_name(self) -> typing.Optional[builtins.str]:
        '''Database name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_name TargetDb#db_name}
        '''
        result = self._values.get("db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_server_certificates(self) -> typing.Optional[builtins.str]:
        '''Set of root certificate authorities in base64 encoding used by clients to verify server certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_server_certificates TargetDb#db_server_certificates}
        '''
        result = self._values.get("db_server_certificates")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_server_name(self) -> typing.Optional[builtins.str]:
        '''Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is provided.

        It is also included in the client's handshake to support virtual hosting unless it is an IP address

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#db_server_name TargetDb#db_server_name}
        '''
        result = self._values.get("db_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#description TargetDb#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Database host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#host TargetDb#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#id TargetDb#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#key TargetDb#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag, set database type to mongodb and the flag to true to create Mongo Atlas target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas TargetDb#mongodb_atlas}
        '''
        result = self._values.get("mongodb_atlas")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def mongodb_atlas_api_private_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas private key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_api_private_key TargetDb#mongodb_atlas_api_private_key}
        '''
        result = self._values.get("mongodb_atlas_api_private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_api_public_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas public key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_api_public_key TargetDb#mongodb_atlas_api_public_key}
        '''
        result = self._values.get("mongodb_atlas_api_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_project_id(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_atlas_project_id TargetDb#mongodb_atlas_project_id}
        '''
        result = self._values.get("mongodb_atlas_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_default_auth_db(self) -> typing.Optional[builtins.str]:
        '''MongoDB server default authentication database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_default_auth_db TargetDb#mongodb_default_auth_db}
        '''
        result = self._values.get("mongodb_default_auth_db")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_uri_options(self) -> typing.Optional[builtins.str]:
        '''MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#mongodb_uri_options TargetDb#mongodb_uri_options}
        '''
        result = self._values.get("mongodb_uri_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_service_name(self) -> typing.Optional[builtins.str]:
        '''oracle db service name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#oracle_service_name TargetDb#oracle_service_name}
        '''
        result = self._values.get("oracle_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[builtins.str]:
        '''Database port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#port TargetDb#port}
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pwd(self) -> typing.Optional[builtins.str]:
        '''Database password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#pwd TargetDb#pwd}
        '''
        result = self._values.get("pwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snowflake_account(self) -> typing.Optional[builtins.str]:
        '''Snowflake account name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#snowflake_account TargetDb#snowflake_account}
        '''
        result = self._values.get("snowflake_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable/Disable SSL [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#ssl TargetDb#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ssl_certificate(self) -> typing.Optional[builtins.str]:
        '''SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#ssl_certificate TargetDb#ssl_certificate}
        '''
        result = self._values.get("ssl_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Database user name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_db#user_name TargetDb#user_name}
        '''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetDbConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TargetDb",
    "TargetDbConfig",
]

publication.publish()

def _typecheckingstub__04ee075eae61cb54abe3dc00f017184cb0030deae9607e6e73b30acc53cc2126(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    db_type: builtins.str,
    name: builtins.str,
    db_name: typing.Optional[builtins.str] = None,
    db_server_certificates: typing.Optional[builtins.str] = None,
    db_server_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    mongodb_atlas: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
    mongodb_default_auth_db: typing.Optional[builtins.str] = None,
    mongodb_uri_options: typing.Optional[builtins.str] = None,
    oracle_service_name: typing.Optional[builtins.str] = None,
    port: typing.Optional[builtins.str] = None,
    pwd: typing.Optional[builtins.str] = None,
    snowflake_account: typing.Optional[builtins.str] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ssl_certificate: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__26747a1e62a55b0076642ab77d5b590c88d2aa437c34aad73d1f692b1eb37d84(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__046cd7002d32efa9afc4022d447c1edac4d5afd660bd66bbcdc47b961fa48d23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a7046bec191393e72f3d70b139eab77e13d8616059e1af04706e78036cd074a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab1f2a0c37c9f3d3f6d643361500338b081ab8abd2d17e091c83cde1b4e6a472(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a976017014c1c81795b6cff69b77c0e27fd1d15edcfa75e1710ba6736fd12f0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e727d9f2289e2c2edf56844c2b14d002fe6555fc2400e29fe3e2afcc4930181e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86a29c6497fdf69d0838d97b45ebeed3f9168d58dd60ebc75869ba9f79ad9fcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e5a929dae341bbee72a3c3eb50ebb2699c053561318284beb11cddeaee96681(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dda047976deb350766cc710e2c299bbcd3c76b4a65ffc2063a1fd42f191b8f35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dffb39913171e38bf640a22ace5ab2fd0bb921f280aa929817f2815a9d5f856(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b578eaeb9f7086a07dd290643e960a3ebac03a47dd54499cf91ee39260e19167(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bcd83441bd63de03f3216386917615e3c86dfd03162b0473aea51b8a6f0ec53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da26de7b59c65c2c2e03ed7974d2578a6bf719114cb285592372be2ae3cfd27e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbea5e23e94b867822d342aca86add6586aa2890931a5263e044cadcc52743bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb5f844dd9591ad45141da587e313d9a02d9df574f3202675e48dfd69c3738e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b515a6f658f6e1cab74b44fc47a1ba4504885d5656a46271ee38302671043a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6684d16e15cb119462c1d0c667eb4e24e79aee0216befeb64a59dadf0c522397(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__274ca015bd76a169122a9ed73b8499893d4f8e5bbd5dd3aae6975f0d087c3e49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bda53c72e854b59f38ae15d4d6ee8f3002ae5b84d418d6ad9f017063d06ed963(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4874536baada0e340002f2a38bd9f4f335f80786dba36594720d44ba7cdd4aa0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a56bcc29ef90ccbe0d4e518d3714147a56d72433cf2e2239799cbc5b2e567709(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__268620d2cd4435a525be5211a0a60992a4714fcbe6d79a527dba40c27dae65f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa26313425b45e5f1457d685f36f8c2dc85c555df54a90a732489270a6e4655b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce27b52a60b1beacf141ae4cb9d305574d3c9b2da52165d192b3978508d9adc1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    db_type: builtins.str,
    name: builtins.str,
    db_name: typing.Optional[builtins.str] = None,
    db_server_certificates: typing.Optional[builtins.str] = None,
    db_server_name: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    mongodb_atlas: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
    mongodb_default_auth_db: typing.Optional[builtins.str] = None,
    mongodb_uri_options: typing.Optional[builtins.str] = None,
    oracle_service_name: typing.Optional[builtins.str] = None,
    port: typing.Optional[builtins.str] = None,
    pwd: typing.Optional[builtins.str] = None,
    snowflake_account: typing.Optional[builtins.str] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ssl_certificate: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
