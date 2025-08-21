'''
# `akeyless_producer_oracle`

Refer to the Terraform Registry for docs: [`akeyless_producer_oracle`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle).
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


class ProducerOracle(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerOracle.ProducerOracle",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle akeyless_producer_oracle}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        db_server_certificates: typing.Optional[builtins.str] = None,
        db_server_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        oracle_host: typing.Optional[builtins.str] = None,
        oracle_password: typing.Optional[builtins.str] = None,
        oracle_port: typing.Optional[builtins.str] = None,
        oracle_screation_statements: typing.Optional[builtins.str] = None,
        oracle_service_name: typing.Optional[builtins.str] = None,
        oracle_username: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle akeyless_producer_oracle} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#name ProducerOracle#name}
        :param db_server_certificates: the set of root certificate authorities in base64 encoding that clients use when verifying server certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#db_server_certificates ProducerOracle#db_server_certificates}
        :param db_server_name: Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is given. It is also included in the client's handshake to support virtual hosting unless it is an IP address Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#db_server_name ProducerOracle#db_server_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#id ProducerOracle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param oracle_host: Oracle host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_host ProducerOracle#oracle_host}
        :param oracle_password: Oracle password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_password ProducerOracle#oracle_password}
        :param oracle_port: Oracle port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_port ProducerOracle#oracle_port}
        :param oracle_screation_statements: Oracle Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_screation_statements ProducerOracle#oracle_screation_statements}
        :param oracle_service_name: Oracle service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_service_name ProducerOracle#oracle_service_name}
        :param oracle_username: Oracle user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_username ProducerOracle#oracle_username}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#producer_encryption_key_name ProducerOracle#producer_encryption_key_name}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#tags ProducerOracle#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#target_name ProducerOracle#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#user_ttl ProducerOracle#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c809c3865a8c85aca8e5c794fe758976d187a3fbd10308bd49c7a2076091d12)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerOracleConfig(
            name=name,
            db_server_certificates=db_server_certificates,
            db_server_name=db_server_name,
            id=id,
            oracle_host=oracle_host,
            oracle_password=oracle_password,
            oracle_port=oracle_port,
            oracle_screation_statements=oracle_screation_statements,
            oracle_service_name=oracle_service_name,
            oracle_username=oracle_username,
            producer_encryption_key_name=producer_encryption_key_name,
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
        '''Generates CDKTF code for importing a ProducerOracle resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerOracle to import.
        :param import_from_id: The id of the existing ProducerOracle that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerOracle to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b824c37cd99e41fbc95aeac055a1cbe5137eb17b7eb99000d0dbf0c3de114ca5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDbServerCertificates")
    def reset_db_server_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbServerCertificates", []))

    @jsii.member(jsii_name="resetDbServerName")
    def reset_db_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbServerName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOracleHost")
    def reset_oracle_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleHost", []))

    @jsii.member(jsii_name="resetOraclePassword")
    def reset_oracle_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOraclePassword", []))

    @jsii.member(jsii_name="resetOraclePort")
    def reset_oracle_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOraclePort", []))

    @jsii.member(jsii_name="resetOracleScreationStatements")
    def reset_oracle_screation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleScreationStatements", []))

    @jsii.member(jsii_name="resetOracleServiceName")
    def reset_oracle_service_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleServiceName", []))

    @jsii.member(jsii_name="resetOracleUsername")
    def reset_oracle_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleUsername", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

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
    @jsii.member(jsii_name="dbServerCertificatesInput")
    def db_server_certificates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbServerCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="dbServerNameInput")
    def db_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleHostInput")
    def oracle_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleHostInput"))

    @builtins.property
    @jsii.member(jsii_name="oraclePasswordInput")
    def oracle_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oraclePasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="oraclePortInput")
    def oracle_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oraclePortInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleScreationStatementsInput")
    def oracle_screation_statements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleScreationStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleServiceNameInput")
    def oracle_service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleServiceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleUsernameInput")
    def oracle_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyNameInput")
    def producer_encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "producerEncryptionKeyNameInput"))

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
    @jsii.member(jsii_name="dbServerCertificates")
    def db_server_certificates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbServerCertificates"))

    @db_server_certificates.setter
    def db_server_certificates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d3c00fd0d138d8160150bcc0cadd066d6995f0ac9c3338b7a46fc1a3abf3056)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbServerCertificates", value)

    @builtins.property
    @jsii.member(jsii_name="dbServerName")
    def db_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbServerName"))

    @db_server_name.setter
    def db_server_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3eafc3813a05e9228e66254c1d7926f748f6a90266fe00bf511b590e9c4c691)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbServerName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3766ea675df15f05df1cc2414a2f33d0cb4a83375cd25d344198c2e3759fb4a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75fb6d8590cdba50cc7f68c1ed3e27adfd61364447853821d8970604c8b6fd75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="oracleHost")
    def oracle_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleHost"))

    @oracle_host.setter
    def oracle_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0f68791476c05e61a641c5cec80245191d90ac37607ddb56b3c8106fb6fdbea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleHost", value)

    @builtins.property
    @jsii.member(jsii_name="oraclePassword")
    def oracle_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oraclePassword"))

    @oracle_password.setter
    def oracle_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__643ccbbd3fd9b1c258ca486932b96012d295a59db19420f40e74852280e43279)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oraclePassword", value)

    @builtins.property
    @jsii.member(jsii_name="oraclePort")
    def oracle_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oraclePort"))

    @oracle_port.setter
    def oracle_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__019c37ed5ee93429d3c6a1f371dd9a427051af4f9cf2089ba76393f28484cdf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oraclePort", value)

    @builtins.property
    @jsii.member(jsii_name="oracleScreationStatements")
    def oracle_screation_statements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleScreationStatements"))

    @oracle_screation_statements.setter
    def oracle_screation_statements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ff4267175206c031355300d0412368e23b470ab59ba1f73ccaca2699fa47d0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleScreationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="oracleServiceName")
    def oracle_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleServiceName"))

    @oracle_service_name.setter
    def oracle_service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9cee170bf7ebe6679d3a99b88c2696275d295243d4fbda990b6e460c991650)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleServiceName", value)

    @builtins.property
    @jsii.member(jsii_name="oracleUsername")
    def oracle_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleUsername"))

    @oracle_username.setter
    def oracle_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7150828117fb0f4fd98de4b0cc80fe3db71100589a766b21a9743bc29d449b46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleUsername", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49650553b011aa23fd104c32735f73ff38b056cb777dadbea78d9ef25d990ed5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__255f3d24f8aac18392ef167e8c2d59099d0cd01a805ae67684bd3799c21bfc59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77dc833dba1821a410d7d7d219565b0dfc3f2314b815547ac6406036cfd0ce56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d42f5862d011e395613220d44b5f20934b81b5fa855c4391c0e6b39b74e23b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerOracle.ProducerOracleConfig",
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
        "db_server_certificates": "dbServerCertificates",
        "db_server_name": "dbServerName",
        "id": "id",
        "oracle_host": "oracleHost",
        "oracle_password": "oraclePassword",
        "oracle_port": "oraclePort",
        "oracle_screation_statements": "oracleScreationStatements",
        "oracle_service_name": "oracleServiceName",
        "oracle_username": "oracleUsername",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerOracleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        db_server_certificates: typing.Optional[builtins.str] = None,
        db_server_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        oracle_host: typing.Optional[builtins.str] = None,
        oracle_password: typing.Optional[builtins.str] = None,
        oracle_port: typing.Optional[builtins.str] = None,
        oracle_screation_statements: typing.Optional[builtins.str] = None,
        oracle_service_name: typing.Optional[builtins.str] = None,
        oracle_username: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#name ProducerOracle#name}
        :param db_server_certificates: the set of root certificate authorities in base64 encoding that clients use when verifying server certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#db_server_certificates ProducerOracle#db_server_certificates}
        :param db_server_name: Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is given. It is also included in the client's handshake to support virtual hosting unless it is an IP address Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#db_server_name ProducerOracle#db_server_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#id ProducerOracle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param oracle_host: Oracle host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_host ProducerOracle#oracle_host}
        :param oracle_password: Oracle password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_password ProducerOracle#oracle_password}
        :param oracle_port: Oracle port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_port ProducerOracle#oracle_port}
        :param oracle_screation_statements: Oracle Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_screation_statements ProducerOracle#oracle_screation_statements}
        :param oracle_service_name: Oracle service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_service_name ProducerOracle#oracle_service_name}
        :param oracle_username: Oracle user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_username ProducerOracle#oracle_username}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#producer_encryption_key_name ProducerOracle#producer_encryption_key_name}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#tags ProducerOracle#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#target_name ProducerOracle#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#user_ttl ProducerOracle#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30bf654bb2cd00532a6a3484c6a2292ec4d6ab67543c6e32d9ad21ddba9dfd31)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument db_server_certificates", value=db_server_certificates, expected_type=type_hints["db_server_certificates"])
            check_type(argname="argument db_server_name", value=db_server_name, expected_type=type_hints["db_server_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument oracle_host", value=oracle_host, expected_type=type_hints["oracle_host"])
            check_type(argname="argument oracle_password", value=oracle_password, expected_type=type_hints["oracle_password"])
            check_type(argname="argument oracle_port", value=oracle_port, expected_type=type_hints["oracle_port"])
            check_type(argname="argument oracle_screation_statements", value=oracle_screation_statements, expected_type=type_hints["oracle_screation_statements"])
            check_type(argname="argument oracle_service_name", value=oracle_service_name, expected_type=type_hints["oracle_service_name"])
            check_type(argname="argument oracle_username", value=oracle_username, expected_type=type_hints["oracle_username"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
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
        if db_server_certificates is not None:
            self._values["db_server_certificates"] = db_server_certificates
        if db_server_name is not None:
            self._values["db_server_name"] = db_server_name
        if id is not None:
            self._values["id"] = id
        if oracle_host is not None:
            self._values["oracle_host"] = oracle_host
        if oracle_password is not None:
            self._values["oracle_password"] = oracle_password
        if oracle_port is not None:
            self._values["oracle_port"] = oracle_port
        if oracle_screation_statements is not None:
            self._values["oracle_screation_statements"] = oracle_screation_statements
        if oracle_service_name is not None:
            self._values["oracle_service_name"] = oracle_service_name
        if oracle_username is not None:
            self._values["oracle_username"] = oracle_username
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#name ProducerOracle#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_server_certificates(self) -> typing.Optional[builtins.str]:
        '''the set of root certificate authorities in base64 encoding that clients use when verifying server certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#db_server_certificates ProducerOracle#db_server_certificates}
        '''
        result = self._values.get("db_server_certificates")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_server_name(self) -> typing.Optional[builtins.str]:
        '''Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is given.

        It is also included in the client's handshake to support virtual hosting unless it is an IP address

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#db_server_name ProducerOracle#db_server_name}
        '''
        result = self._values.get("db_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#id ProducerOracle#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_host(self) -> typing.Optional[builtins.str]:
        '''Oracle host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_host ProducerOracle#oracle_host}
        '''
        result = self._values.get("oracle_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_password(self) -> typing.Optional[builtins.str]:
        '''Oracle password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_password ProducerOracle#oracle_password}
        '''
        result = self._values.get("oracle_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_port(self) -> typing.Optional[builtins.str]:
        '''Oracle port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_port ProducerOracle#oracle_port}
        '''
        result = self._values.get("oracle_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_screation_statements(self) -> typing.Optional[builtins.str]:
        '''Oracle Creation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_screation_statements ProducerOracle#oracle_screation_statements}
        '''
        result = self._values.get("oracle_screation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_service_name(self) -> typing.Optional[builtins.str]:
        '''Oracle service name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_service_name ProducerOracle#oracle_service_name}
        '''
        result = self._values.get("oracle_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_username(self) -> typing.Optional[builtins.str]:
        '''Oracle user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#oracle_username ProducerOracle#oracle_username}
        '''
        result = self._values.get("oracle_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#producer_encryption_key_name ProducerOracle#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#tags ProducerOracle#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#target_name ProducerOracle#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_oracle#user_ttl ProducerOracle#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerOracleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerOracle",
    "ProducerOracleConfig",
]

publication.publish()

def _typecheckingstub__6c809c3865a8c85aca8e5c794fe758976d187a3fbd10308bd49c7a2076091d12(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    db_server_certificates: typing.Optional[builtins.str] = None,
    db_server_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    oracle_host: typing.Optional[builtins.str] = None,
    oracle_password: typing.Optional[builtins.str] = None,
    oracle_port: typing.Optional[builtins.str] = None,
    oracle_screation_statements: typing.Optional[builtins.str] = None,
    oracle_service_name: typing.Optional[builtins.str] = None,
    oracle_username: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__b824c37cd99e41fbc95aeac055a1cbe5137eb17b7eb99000d0dbf0c3de114ca5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d3c00fd0d138d8160150bcc0cadd066d6995f0ac9c3338b7a46fc1a3abf3056(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3eafc3813a05e9228e66254c1d7926f748f6a90266fe00bf511b590e9c4c691(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3766ea675df15f05df1cc2414a2f33d0cb4a83375cd25d344198c2e3759fb4a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75fb6d8590cdba50cc7f68c1ed3e27adfd61364447853821d8970604c8b6fd75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0f68791476c05e61a641c5cec80245191d90ac37607ddb56b3c8106fb6fdbea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__643ccbbd3fd9b1c258ca486932b96012d295a59db19420f40e74852280e43279(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__019c37ed5ee93429d3c6a1f371dd9a427051af4f9cf2089ba76393f28484cdf3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ff4267175206c031355300d0412368e23b470ab59ba1f73ccaca2699fa47d0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9cee170bf7ebe6679d3a99b88c2696275d295243d4fbda990b6e460c991650(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7150828117fb0f4fd98de4b0cc80fe3db71100589a766b21a9743bc29d449b46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49650553b011aa23fd104c32735f73ff38b056cb777dadbea78d9ef25d990ed5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__255f3d24f8aac18392ef167e8c2d59099d0cd01a805ae67684bd3799c21bfc59(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77dc833dba1821a410d7d7d219565b0dfc3f2314b815547ac6406036cfd0ce56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d42f5862d011e395613220d44b5f20934b81b5fa855c4391c0e6b39b74e23b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30bf654bb2cd00532a6a3484c6a2292ec4d6ab67543c6e32d9ad21ddba9dfd31(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    db_server_certificates: typing.Optional[builtins.str] = None,
    db_server_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    oracle_host: typing.Optional[builtins.str] = None,
    oracle_password: typing.Optional[builtins.str] = None,
    oracle_port: typing.Optional[builtins.str] = None,
    oracle_screation_statements: typing.Optional[builtins.str] = None,
    oracle_service_name: typing.Optional[builtins.str] = None,
    oracle_username: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
