'''
# `akeyless_producer_postgres`

Refer to the Terraform Registry for docs: [`akeyless_producer_postgres`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres).
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


class ProducerPostgres(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerPostgres.ProducerPostgres",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres akeyless_producer_postgres}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        creation_statements: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        postgresql_db_name: typing.Optional[builtins.str] = None,
        postgresql_host: typing.Optional[builtins.str] = None,
        postgresql_password: typing.Optional[builtins.str] = None,
        postgresql_port: typing.Optional[builtins.str] = None,
        postgresql_username: typing.Optional[builtins.str] = None,
        producer_encryption_key: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
        secure_access_db_schema: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        user_ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres akeyless_producer_postgres} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#name ProducerPostgres#name}
        :param creation_statements: PostgreSQL Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#creation_statements ProducerPostgres#creation_statements}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#id ProducerPostgres#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param postgresql_db_name: PostgreSQL DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_db_name ProducerPostgres#postgresql_db_name}
        :param postgresql_host: PostgreSQL host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_host ProducerPostgres#postgresql_host}
        :param postgresql_password: PostgreSQL password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_password ProducerPostgres#postgresql_password}
        :param postgresql_port: PostgreSQL port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_port ProducerPostgres#postgresql_port}
        :param postgresql_username: PostgreSQL user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_username ProducerPostgres#postgresql_username}
        :param producer_encryption_key: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#producer_encryption_key ProducerPostgres#producer_encryption_key}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_bastion_issuer ProducerPostgres#secure_access_bastion_issuer}
        :param secure_access_db_name: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_db_name ProducerPostgres#secure_access_db_name}
        :param secure_access_db_schema: The db schema. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_db_schema ProducerPostgres#secure_access_db_schema}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_enable ProducerPostgres#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_host ProducerPostgres#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_web ProducerPostgres#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#tags ProducerPostgres#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#target_name ProducerPostgres#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#user_ttl ProducerPostgres#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f72dd7b8a2c4e290967e728cf9bd3499dccb8d201c77f97ff4c812b9c7b3d2da)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerPostgresConfig(
            name=name,
            creation_statements=creation_statements,
            id=id,
            postgresql_db_name=postgresql_db_name,
            postgresql_host=postgresql_host,
            postgresql_password=postgresql_password,
            postgresql_port=postgresql_port,
            postgresql_username=postgresql_username,
            producer_encryption_key=producer_encryption_key,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_db_name=secure_access_db_name,
            secure_access_db_schema=secure_access_db_schema,
            secure_access_enable=secure_access_enable,
            secure_access_host=secure_access_host,
            secure_access_web=secure_access_web,
            tags=tags,
            target_name=target_name,
            user_ttl=user_ttl,
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
        '''Generates CDKTF code for importing a ProducerPostgres resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerPostgres to import.
        :param import_from_id: The id of the existing ProducerPostgres that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerPostgres to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a86dac74a10b1c887cef515a8969803a320ce29933059f6d61811e951e3fbf14)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCreationStatements")
    def reset_creation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationStatements", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPostgresqlDbName")
    def reset_postgresql_db_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresqlDbName", []))

    @jsii.member(jsii_name="resetPostgresqlHost")
    def reset_postgresql_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresqlHost", []))

    @jsii.member(jsii_name="resetPostgresqlPassword")
    def reset_postgresql_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresqlPassword", []))

    @jsii.member(jsii_name="resetPostgresqlPort")
    def reset_postgresql_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresqlPort", []))

    @jsii.member(jsii_name="resetPostgresqlUsername")
    def reset_postgresql_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostgresqlUsername", []))

    @jsii.member(jsii_name="resetProducerEncryptionKey")
    def reset_producer_encryption_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKey", []))

    @jsii.member(jsii_name="resetSecureAccessBastionIssuer")
    def reset_secure_access_bastion_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionIssuer", []))

    @jsii.member(jsii_name="resetSecureAccessDbName")
    def reset_secure_access_db_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessDbName", []))

    @jsii.member(jsii_name="resetSecureAccessDbSchema")
    def reset_secure_access_db_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessDbSchema", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessHost")
    def reset_secure_access_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessHost", []))

    @jsii.member(jsii_name="resetSecureAccessWeb")
    def reset_secure_access_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWeb", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTargetName")
    def reset_target_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetName", []))

    @jsii.member(jsii_name="resetUserTtl")
    def reset_user_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserTtl", []))

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
    @jsii.member(jsii_name="creationStatementsInput")
    def creation_statements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creationStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresqlDbNameInput")
    def postgresql_db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postgresqlDbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresqlHostInput")
    def postgresql_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postgresqlHostInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresqlPasswordInput")
    def postgresql_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postgresqlPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresqlPortInput")
    def postgresql_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postgresqlPortInput"))

    @builtins.property
    @jsii.member(jsii_name="postgresqlUsernameInput")
    def postgresql_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postgresqlUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyInput")
    def producer_encryption_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "producerEncryptionKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuerInput")
    def secure_access_bastion_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbNameInput")
    def secure_access_db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessDbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbSchemaInput")
    def secure_access_db_schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessDbSchemaInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessHostInput")
    def secure_access_host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secureAccessHostInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessWebInput")
    def secure_access_web_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessWebInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userTtlInput")
    def user_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="creationStatements")
    def creation_statements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "creationStatements"))

    @creation_statements.setter
    def creation_statements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e92b05f3ee1f1478c6d0339cc4895603e442beebe25ecdf38a30525ff29e2c8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d62a8900bd00f4ecf63058c5ec2edd4f68b2f526128da59b16785ead5b6ed22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__606ca678b6cadfab043fcd5c4d55b352de4dd6b89a949fb805f86b2331c090c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlDbName")
    def postgresql_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlDbName"))

    @postgresql_db_name.setter
    def postgresql_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__903f958b36e0f68b760dadbb5e9873249320c45777bb22b00d694c24a877928e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlDbName", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlHost")
    def postgresql_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlHost"))

    @postgresql_host.setter
    def postgresql_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49f4ac62f316b1d916b37901545ed981c6891cae5a6a9457f41711294cabf659)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlHost", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlPassword")
    def postgresql_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlPassword"))

    @postgresql_password.setter
    def postgresql_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754fe8fa17c749d2023f622c3abe7ed497a14bae470a8fc8d744efd9840d8a59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlPassword", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlPort")
    def postgresql_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlPort"))

    @postgresql_port.setter
    def postgresql_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ebd2512fa3249762d686799d6b26377542f2ed89ece2eeb43c598663042f97c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlPort", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlUsername")
    def postgresql_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlUsername"))

    @postgresql_username.setter
    def postgresql_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50c71fc1c9b5e6d636e756c9e44935f19d162a38471f7220cb3ad39a7058a0b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlUsername", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKey")
    def producer_encryption_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKey"))

    @producer_encryption_key.setter
    def producer_encryption_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e18668f76592ceed8b6d3d24343703742fac277d802e2d763ebb7a229c97270)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKey", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d4cc990b832e564432f9b6ebb8f64b62c275fb9e467628f8f8af7cefae2750f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbName")
    def secure_access_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbName"))

    @secure_access_db_name.setter
    def secure_access_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e57b2855baf9f539f5d1a3c087f7d6fd51d5f94d237dc7fb789043432f5f4ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbSchema")
    def secure_access_db_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbSchema"))

    @secure_access_db_schema.setter
    def secure_access_db_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5531a5e4851518083e33c27bbfc4518e69ee5f228e7243fc97f78cfa7162761)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbSchema", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed2ac6043f2b8f52d9420d2a22bab49e5af8241ded1f24076bbc003edf56af7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ea3b0c3f4756b50b9204a185df64005e328b27673f9e2576a7aa3af7f05b2d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessHost", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessWeb")
    def secure_access_web(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessWeb"))

    @secure_access_web.setter
    def secure_access_web(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409d50c8562530a28dc34ecf946a7b8ec52e4461c2342e78ed807c6ce1822e9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed5eab6aa7a3a3b2bbb0b29a079f35097e793a464dfd5d6bf1b0fd606f95c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4602cf667279cd896f527a5e818b8b4c5b4e53e8115a14278c4f457776ca604)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__620908d502e280e8c209fff865750c4a0713aaced76943a7762e39a66f3918d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerPostgres.ProducerPostgresConfig",
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
        "creation_statements": "creationStatements",
        "id": "id",
        "postgresql_db_name": "postgresqlDbName",
        "postgresql_host": "postgresqlHost",
        "postgresql_password": "postgresqlPassword",
        "postgresql_port": "postgresqlPort",
        "postgresql_username": "postgresqlUsername",
        "producer_encryption_key": "producerEncryptionKey",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_db_name": "secureAccessDbName",
        "secure_access_db_schema": "secureAccessDbSchema",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_web": "secureAccessWeb",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerPostgresConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        creation_statements: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        postgresql_db_name: typing.Optional[builtins.str] = None,
        postgresql_host: typing.Optional[builtins.str] = None,
        postgresql_password: typing.Optional[builtins.str] = None,
        postgresql_port: typing.Optional[builtins.str] = None,
        postgresql_username: typing.Optional[builtins.str] = None,
        producer_encryption_key: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
        secure_access_db_schema: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        user_ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#name ProducerPostgres#name}
        :param creation_statements: PostgreSQL Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#creation_statements ProducerPostgres#creation_statements}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#id ProducerPostgres#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param postgresql_db_name: PostgreSQL DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_db_name ProducerPostgres#postgresql_db_name}
        :param postgresql_host: PostgreSQL host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_host ProducerPostgres#postgresql_host}
        :param postgresql_password: PostgreSQL password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_password ProducerPostgres#postgresql_password}
        :param postgresql_port: PostgreSQL port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_port ProducerPostgres#postgresql_port}
        :param postgresql_username: PostgreSQL user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_username ProducerPostgres#postgresql_username}
        :param producer_encryption_key: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#producer_encryption_key ProducerPostgres#producer_encryption_key}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_bastion_issuer ProducerPostgres#secure_access_bastion_issuer}
        :param secure_access_db_name: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_db_name ProducerPostgres#secure_access_db_name}
        :param secure_access_db_schema: The db schema. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_db_schema ProducerPostgres#secure_access_db_schema}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_enable ProducerPostgres#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_host ProducerPostgres#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_web ProducerPostgres#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#tags ProducerPostgres#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#target_name ProducerPostgres#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#user_ttl ProducerPostgres#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8575da669704bc4b0eb4a369266ca98deb92b723f9242939acef616d13caeed)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument creation_statements", value=creation_statements, expected_type=type_hints["creation_statements"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument postgresql_db_name", value=postgresql_db_name, expected_type=type_hints["postgresql_db_name"])
            check_type(argname="argument postgresql_host", value=postgresql_host, expected_type=type_hints["postgresql_host"])
            check_type(argname="argument postgresql_password", value=postgresql_password, expected_type=type_hints["postgresql_password"])
            check_type(argname="argument postgresql_port", value=postgresql_port, expected_type=type_hints["postgresql_port"])
            check_type(argname="argument postgresql_username", value=postgresql_username, expected_type=type_hints["postgresql_username"])
            check_type(argname="argument producer_encryption_key", value=producer_encryption_key, expected_type=type_hints["producer_encryption_key"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_db_name", value=secure_access_db_name, expected_type=type_hints["secure_access_db_name"])
            check_type(argname="argument secure_access_db_schema", value=secure_access_db_schema, expected_type=type_hints["secure_access_db_schema"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_host", value=secure_access_host, expected_type=type_hints["secure_access_host"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument user_ttl", value=user_ttl, expected_type=type_hints["user_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if creation_statements is not None:
            self._values["creation_statements"] = creation_statements
        if id is not None:
            self._values["id"] = id
        if postgresql_db_name is not None:
            self._values["postgresql_db_name"] = postgresql_db_name
        if postgresql_host is not None:
            self._values["postgresql_host"] = postgresql_host
        if postgresql_password is not None:
            self._values["postgresql_password"] = postgresql_password
        if postgresql_port is not None:
            self._values["postgresql_port"] = postgresql_port
        if postgresql_username is not None:
            self._values["postgresql_username"] = postgresql_username
        if producer_encryption_key is not None:
            self._values["producer_encryption_key"] = producer_encryption_key
        if secure_access_bastion_issuer is not None:
            self._values["secure_access_bastion_issuer"] = secure_access_bastion_issuer
        if secure_access_db_name is not None:
            self._values["secure_access_db_name"] = secure_access_db_name
        if secure_access_db_schema is not None:
            self._values["secure_access_db_schema"] = secure_access_db_schema
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_host is not None:
            self._values["secure_access_host"] = secure_access_host
        if secure_access_web is not None:
            self._values["secure_access_web"] = secure_access_web
        if tags is not None:
            self._values["tags"] = tags
        if target_name is not None:
            self._values["target_name"] = target_name
        if user_ttl is not None:
            self._values["user_ttl"] = user_ttl

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
        '''Producer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#name ProducerPostgres#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def creation_statements(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL Creation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#creation_statements ProducerPostgres#creation_statements}
        '''
        result = self._values.get("creation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#id ProducerPostgres#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_db_name(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL DB name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_db_name ProducerPostgres#postgresql_db_name}
        '''
        result = self._values.get("postgresql_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_host(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_host ProducerPostgres#postgresql_host}
        '''
        result = self._values.get("postgresql_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_password(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_password ProducerPostgres#postgresql_password}
        '''
        result = self._values.get("postgresql_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_port(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_port ProducerPostgres#postgresql_port}
        '''
        result = self._values.get("postgresql_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_username(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#postgresql_username ProducerPostgres#postgresql_username}
        '''
        result = self._values.get("postgresql_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#producer_encryption_key ProducerPostgres#producer_encryption_key}
        '''
        result = self._values.get("producer_encryption_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_bastion_issuer ProducerPostgres#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_name(self) -> typing.Optional[builtins.str]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_db_name ProducerPostgres#secure_access_db_name}
        '''
        result = self._values.get("secure_access_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_schema(self) -> typing.Optional[builtins.str]:
        '''The db schema.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_db_schema ProducerPostgres#secure_access_db_schema}
        '''
        result = self._values.get("secure_access_db_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_enable ProducerPostgres#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target DB servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_host ProducerPostgres#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#secure_access_web ProducerPostgres#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#tags ProducerPostgres#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#target_name ProducerPostgres#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_postgres#user_ttl ProducerPostgres#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerPostgresConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerPostgres",
    "ProducerPostgresConfig",
]

publication.publish()

def _typecheckingstub__f72dd7b8a2c4e290967e728cf9bd3499dccb8d201c77f97ff4c812b9c7b3d2da(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    creation_statements: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    postgresql_db_name: typing.Optional[builtins.str] = None,
    postgresql_host: typing.Optional[builtins.str] = None,
    postgresql_password: typing.Optional[builtins.str] = None,
    postgresql_port: typing.Optional[builtins.str] = None,
    postgresql_username: typing.Optional[builtins.str] = None,
    producer_encryption_key: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_db_schema: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a86dac74a10b1c887cef515a8969803a320ce29933059f6d61811e951e3fbf14(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e92b05f3ee1f1478c6d0339cc4895603e442beebe25ecdf38a30525ff29e2c8a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d62a8900bd00f4ecf63058c5ec2edd4f68b2f526128da59b16785ead5b6ed22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__606ca678b6cadfab043fcd5c4d55b352de4dd6b89a949fb805f86b2331c090c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__903f958b36e0f68b760dadbb5e9873249320c45777bb22b00d694c24a877928e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49f4ac62f316b1d916b37901545ed981c6891cae5a6a9457f41711294cabf659(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754fe8fa17c749d2023f622c3abe7ed497a14bae470a8fc8d744efd9840d8a59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ebd2512fa3249762d686799d6b26377542f2ed89ece2eeb43c598663042f97c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c71fc1c9b5e6d636e756c9e44935f19d162a38471f7220cb3ad39a7058a0b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e18668f76592ceed8b6d3d24343703742fac277d802e2d763ebb7a229c97270(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d4cc990b832e564432f9b6ebb8f64b62c275fb9e467628f8f8af7cefae2750f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e57b2855baf9f539f5d1a3c087f7d6fd51d5f94d237dc7fb789043432f5f4ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5531a5e4851518083e33c27bbfc4518e69ee5f228e7243fc97f78cfa7162761(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed2ac6043f2b8f52d9420d2a22bab49e5af8241ded1f24076bbc003edf56af7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ea3b0c3f4756b50b9204a185df64005e328b27673f9e2576a7aa3af7f05b2d2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409d50c8562530a28dc34ecf946a7b8ec52e4461c2342e78ed807c6ce1822e9a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ed5eab6aa7a3a3b2bbb0b29a079f35097e793a464dfd5d6bf1b0fd606f95c7c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4602cf667279cd896f527a5e818b8b4c5b4e53e8115a14278c4f457776ca604(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__620908d502e280e8c209fff865750c4a0713aaced76943a7762e39a66f3918d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8575da669704bc4b0eb4a369266ca98deb92b723f9242939acef616d13caeed(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    creation_statements: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    postgresql_db_name: typing.Optional[builtins.str] = None,
    postgresql_host: typing.Optional[builtins.str] = None,
    postgresql_password: typing.Optional[builtins.str] = None,
    postgresql_port: typing.Optional[builtins.str] = None,
    postgresql_username: typing.Optional[builtins.str] = None,
    producer_encryption_key: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_db_schema: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
