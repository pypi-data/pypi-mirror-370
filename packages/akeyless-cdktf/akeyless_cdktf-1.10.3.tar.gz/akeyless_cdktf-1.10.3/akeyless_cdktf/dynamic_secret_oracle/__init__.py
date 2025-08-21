'''
# `akeyless_dynamic_secret_oracle`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_oracle`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle).
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


class DynamicSecretOracle(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretOracle.DynamicSecretOracle",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle akeyless_dynamic_secret_oracle}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        custom_username_template: typing.Optional[builtins.str] = None,
        db_server_certificates: typing.Optional[builtins.str] = None,
        db_server_name: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        oracle_creation_statements: typing.Optional[builtins.str] = None,
        oracle_host: typing.Optional[builtins.str] = None,
        oracle_password: typing.Optional[builtins.str] = None,
        oracle_port: typing.Optional[builtins.str] = None,
        oracle_revocation_statements: typing.Optional[builtins.str] = None,
        oracle_service_name: typing.Optional[builtins.str] = None,
        oracle_username: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle akeyless_dynamic_secret_oracle} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#name DynamicSecretOracle#name}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#custom_username_template DynamicSecretOracle#custom_username_template}
        :param db_server_certificates: the set of root certificate authorities in base64 encoding that clients use when verifying server certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#db_server_certificates DynamicSecretOracle#db_server_certificates}
        :param db_server_name: Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is given. It is also included in the client's handshake to support virtual hosting unless it is an IP address Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#db_server_name DynamicSecretOracle#db_server_name}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#encryption_key_name DynamicSecretOracle#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#id DynamicSecretOracle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param oracle_creation_statements: Oracle Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_creation_statements DynamicSecretOracle#oracle_creation_statements}
        :param oracle_host: Oracle host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_host DynamicSecretOracle#oracle_host}
        :param oracle_password: Oracle password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_password DynamicSecretOracle#oracle_password}
        :param oracle_port: Oracle port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_port DynamicSecretOracle#oracle_port}
        :param oracle_revocation_statements: Oracle Revocation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_revocation_statements DynamicSecretOracle#oracle_revocation_statements}
        :param oracle_service_name: Oracle service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_service_name DynamicSecretOracle#oracle_service_name}
        :param oracle_username: Oracle user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_username DynamicSecretOracle#oracle_username}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#password_length DynamicSecretOracle#password_length}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#tags DynamicSecretOracle#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#target_name DynamicSecretOracle#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#user_ttl DynamicSecretOracle#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0ca7363d7d60275083fc53bb9fe0ea7e7761b7d2c497a5b6989d1e8ba5e933d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretOracleConfig(
            name=name,
            custom_username_template=custom_username_template,
            db_server_certificates=db_server_certificates,
            db_server_name=db_server_name,
            encryption_key_name=encryption_key_name,
            id=id,
            oracle_creation_statements=oracle_creation_statements,
            oracle_host=oracle_host,
            oracle_password=oracle_password,
            oracle_port=oracle_port,
            oracle_revocation_statements=oracle_revocation_statements,
            oracle_service_name=oracle_service_name,
            oracle_username=oracle_username,
            password_length=password_length,
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
        '''Generates CDKTF code for importing a DynamicSecretOracle resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretOracle to import.
        :param import_from_id: The id of the existing DynamicSecretOracle that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretOracle to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__202e7b5291be57808e1bceedc9b320c99abe7a68c8f3a8de480d70783f913baf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomUsernameTemplate")
    def reset_custom_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUsernameTemplate", []))

    @jsii.member(jsii_name="resetDbServerCertificates")
    def reset_db_server_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbServerCertificates", []))

    @jsii.member(jsii_name="resetDbServerName")
    def reset_db_server_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbServerName", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOracleCreationStatements")
    def reset_oracle_creation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleCreationStatements", []))

    @jsii.member(jsii_name="resetOracleHost")
    def reset_oracle_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleHost", []))

    @jsii.member(jsii_name="resetOraclePassword")
    def reset_oracle_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOraclePassword", []))

    @jsii.member(jsii_name="resetOraclePort")
    def reset_oracle_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOraclePort", []))

    @jsii.member(jsii_name="resetOracleRevocationStatements")
    def reset_oracle_revocation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleRevocationStatements", []))

    @jsii.member(jsii_name="resetOracleServiceName")
    def reset_oracle_service_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleServiceName", []))

    @jsii.member(jsii_name="resetOracleUsername")
    def reset_oracle_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOracleUsername", []))

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

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
    @jsii.member(jsii_name="customUsernameTemplateInput")
    def custom_username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customUsernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="dbServerCertificatesInput")
    def db_server_certificates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbServerCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="dbServerNameInput")
    def db_server_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbServerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyNameInput")
    def encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleCreationStatementsInput")
    def oracle_creation_statements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleCreationStatementsInput"))

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
    @jsii.member(jsii_name="oracleRevocationStatementsInput")
    def oracle_revocation_statements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleRevocationStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleServiceNameInput")
    def oracle_service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleServiceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="oracleUsernameInput")
    def oracle_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oracleUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordLengthInput")
    def password_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordLengthInput"))

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
    @jsii.member(jsii_name="customUsernameTemplate")
    def custom_username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customUsernameTemplate"))

    @custom_username_template.setter
    def custom_username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f01818ddafd2db34be37d6c53bb2b7063fb2ce62736fb49635ea40cdf3afcfeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customUsernameTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="dbServerCertificates")
    def db_server_certificates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbServerCertificates"))

    @db_server_certificates.setter
    def db_server_certificates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce2fb1af0a86ea02488945637748bc35af8e4abdc672575cbe8cabcd3262dea3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbServerCertificates", value)

    @builtins.property
    @jsii.member(jsii_name="dbServerName")
    def db_server_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbServerName"))

    @db_server_name.setter
    def db_server_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__331cd083ea94e7abb026e92b9fcb440ea92b4b02fcb8fc9d446c143c8e987ffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbServerName", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fe3deb76cbf189c9647d491f8dd68fbcb61cf1353553b4ef4cf378dd45afd50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71fbb46347a1a649c147395d5742637ccd8df15079ed60868bad56198faf755c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2554348e5b40fd83794ec39002ce6783606e0fef075696ab2b20f3c8431d3e34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="oracleCreationStatements")
    def oracle_creation_statements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleCreationStatements"))

    @oracle_creation_statements.setter
    def oracle_creation_statements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__863fc3df9c9f8e8b0977da598f38cdc0a68ba6fc844bcd02caebdcef1ff208e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleCreationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="oracleHost")
    def oracle_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleHost"))

    @oracle_host.setter
    def oracle_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d49cbe045caed4b56be7f96b947a4f88434e7c86282d0f7ea78750a6bb92922e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleHost", value)

    @builtins.property
    @jsii.member(jsii_name="oraclePassword")
    def oracle_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oraclePassword"))

    @oracle_password.setter
    def oracle_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed6d67d405f0b19a55f4d3d56c4e2ee13214dc5cb261a8b695b0d92a9b68f570)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oraclePassword", value)

    @builtins.property
    @jsii.member(jsii_name="oraclePort")
    def oracle_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oraclePort"))

    @oracle_port.setter
    def oracle_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a68292ecef968651c956f6c05bbbaaddbeeaa9def6e10cebd1be17cc32c386e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oraclePort", value)

    @builtins.property
    @jsii.member(jsii_name="oracleRevocationStatements")
    def oracle_revocation_statements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleRevocationStatements"))

    @oracle_revocation_statements.setter
    def oracle_revocation_statements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed394894c1757cde12eeeeeb54b0392b0f4d5dde0cb656403b4720caae9095be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleRevocationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="oracleServiceName")
    def oracle_service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleServiceName"))

    @oracle_service_name.setter
    def oracle_service_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__455e7e3962229d777dad5a14b95de1c561acf6a033a552779f89c9e8b7811b1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleServiceName", value)

    @builtins.property
    @jsii.member(jsii_name="oracleUsername")
    def oracle_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oracleUsername"))

    @oracle_username.setter
    def oracle_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e05735eaca4a1142b2ecd17c6a4c53d4367786d5f62a4563db447d91c1ac2d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oracleUsername", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5be46cf93c58f901616dd199e93becbe34dca1f073c45718c70a3ab79c31caba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fd9c32de24e2889e9ba322a8decfb60b51cdcebc138a27fba1e406ad1cdd31a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f87b5a2376cf69ff7f4a33a76f61eda12b5cbdfa409f26844aef5acd59848a6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__076f37a0160a255132671ee0c9905263b94d693069d301e03532015f941e41b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretOracle.DynamicSecretOracleConfig",
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
        "custom_username_template": "customUsernameTemplate",
        "db_server_certificates": "dbServerCertificates",
        "db_server_name": "dbServerName",
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
        "oracle_creation_statements": "oracleCreationStatements",
        "oracle_host": "oracleHost",
        "oracle_password": "oraclePassword",
        "oracle_port": "oraclePort",
        "oracle_revocation_statements": "oracleRevocationStatements",
        "oracle_service_name": "oracleServiceName",
        "oracle_username": "oracleUsername",
        "password_length": "passwordLength",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class DynamicSecretOracleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        custom_username_template: typing.Optional[builtins.str] = None,
        db_server_certificates: typing.Optional[builtins.str] = None,
        db_server_name: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        oracle_creation_statements: typing.Optional[builtins.str] = None,
        oracle_host: typing.Optional[builtins.str] = None,
        oracle_password: typing.Optional[builtins.str] = None,
        oracle_port: typing.Optional[builtins.str] = None,
        oracle_revocation_statements: typing.Optional[builtins.str] = None,
        oracle_service_name: typing.Optional[builtins.str] = None,
        oracle_username: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#name DynamicSecretOracle#name}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#custom_username_template DynamicSecretOracle#custom_username_template}
        :param db_server_certificates: the set of root certificate authorities in base64 encoding that clients use when verifying server certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#db_server_certificates DynamicSecretOracle#db_server_certificates}
        :param db_server_name: Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is given. It is also included in the client's handshake to support virtual hosting unless it is an IP address Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#db_server_name DynamicSecretOracle#db_server_name}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#encryption_key_name DynamicSecretOracle#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#id DynamicSecretOracle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param oracle_creation_statements: Oracle Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_creation_statements DynamicSecretOracle#oracle_creation_statements}
        :param oracle_host: Oracle host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_host DynamicSecretOracle#oracle_host}
        :param oracle_password: Oracle password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_password DynamicSecretOracle#oracle_password}
        :param oracle_port: Oracle port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_port DynamicSecretOracle#oracle_port}
        :param oracle_revocation_statements: Oracle Revocation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_revocation_statements DynamicSecretOracle#oracle_revocation_statements}
        :param oracle_service_name: Oracle service name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_service_name DynamicSecretOracle#oracle_service_name}
        :param oracle_username: Oracle user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_username DynamicSecretOracle#oracle_username}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#password_length DynamicSecretOracle#password_length}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#tags DynamicSecretOracle#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#target_name DynamicSecretOracle#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#user_ttl DynamicSecretOracle#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4032f60e0f7aafa5ff1272d4e6e2ad42794e143a322a1bc927cc1f26648bd283)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument custom_username_template", value=custom_username_template, expected_type=type_hints["custom_username_template"])
            check_type(argname="argument db_server_certificates", value=db_server_certificates, expected_type=type_hints["db_server_certificates"])
            check_type(argname="argument db_server_name", value=db_server_name, expected_type=type_hints["db_server_name"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument oracle_creation_statements", value=oracle_creation_statements, expected_type=type_hints["oracle_creation_statements"])
            check_type(argname="argument oracle_host", value=oracle_host, expected_type=type_hints["oracle_host"])
            check_type(argname="argument oracle_password", value=oracle_password, expected_type=type_hints["oracle_password"])
            check_type(argname="argument oracle_port", value=oracle_port, expected_type=type_hints["oracle_port"])
            check_type(argname="argument oracle_revocation_statements", value=oracle_revocation_statements, expected_type=type_hints["oracle_revocation_statements"])
            check_type(argname="argument oracle_service_name", value=oracle_service_name, expected_type=type_hints["oracle_service_name"])
            check_type(argname="argument oracle_username", value=oracle_username, expected_type=type_hints["oracle_username"])
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
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
        if custom_username_template is not None:
            self._values["custom_username_template"] = custom_username_template
        if db_server_certificates is not None:
            self._values["db_server_certificates"] = db_server_certificates
        if db_server_name is not None:
            self._values["db_server_name"] = db_server_name
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
        if oracle_creation_statements is not None:
            self._values["oracle_creation_statements"] = oracle_creation_statements
        if oracle_host is not None:
            self._values["oracle_host"] = oracle_host
        if oracle_password is not None:
            self._values["oracle_password"] = oracle_password
        if oracle_port is not None:
            self._values["oracle_port"] = oracle_port
        if oracle_revocation_statements is not None:
            self._values["oracle_revocation_statements"] = oracle_revocation_statements
        if oracle_service_name is not None:
            self._values["oracle_service_name"] = oracle_service_name
        if oracle_username is not None:
            self._values["oracle_username"] = oracle_username
        if password_length is not None:
            self._values["password_length"] = password_length
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
        '''Dynamic secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#name DynamicSecretOracle#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_username_template(self) -> typing.Optional[builtins.str]:
        '''Customize how temporary usernames are generated using go template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#custom_username_template DynamicSecretOracle#custom_username_template}
        '''
        result = self._values.get("custom_username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_server_certificates(self) -> typing.Optional[builtins.str]:
        '''the set of root certificate authorities in base64 encoding that clients use when verifying server certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#db_server_certificates DynamicSecretOracle#db_server_certificates}
        '''
        result = self._values.get("db_server_certificates")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def db_server_name(self) -> typing.Optional[builtins.str]:
        '''Server name is used to verify the hostname on the returned certificates unless InsecureSkipVerify is given.

        It is also included in the client's handshake to support virtual hosting unless it is an IP address

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#db_server_name DynamicSecretOracle#db_server_name}
        '''
        result = self._values.get("db_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#encryption_key_name DynamicSecretOracle#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#id DynamicSecretOracle#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_creation_statements(self) -> typing.Optional[builtins.str]:
        '''Oracle Creation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_creation_statements DynamicSecretOracle#oracle_creation_statements}
        '''
        result = self._values.get("oracle_creation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_host(self) -> typing.Optional[builtins.str]:
        '''Oracle host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_host DynamicSecretOracle#oracle_host}
        '''
        result = self._values.get("oracle_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_password(self) -> typing.Optional[builtins.str]:
        '''Oracle password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_password DynamicSecretOracle#oracle_password}
        '''
        result = self._values.get("oracle_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_port(self) -> typing.Optional[builtins.str]:
        '''Oracle port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_port DynamicSecretOracle#oracle_port}
        '''
        result = self._values.get("oracle_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_revocation_statements(self) -> typing.Optional[builtins.str]:
        '''Oracle Revocation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_revocation_statements DynamicSecretOracle#oracle_revocation_statements}
        '''
        result = self._values.get("oracle_revocation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_service_name(self) -> typing.Optional[builtins.str]:
        '''Oracle service name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_service_name DynamicSecretOracle#oracle_service_name}
        '''
        result = self._values.get("oracle_service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oracle_username(self) -> typing.Optional[builtins.str]:
        '''Oracle user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#oracle_username DynamicSecretOracle#oracle_username}
        '''
        result = self._values.get("oracle_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#password_length DynamicSecretOracle#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#tags DynamicSecretOracle#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#target_name DynamicSecretOracle#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_oracle#user_ttl DynamicSecretOracle#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretOracleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretOracle",
    "DynamicSecretOracleConfig",
]

publication.publish()

def _typecheckingstub__e0ca7363d7d60275083fc53bb9fe0ea7e7761b7d2c497a5b6989d1e8ba5e933d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    custom_username_template: typing.Optional[builtins.str] = None,
    db_server_certificates: typing.Optional[builtins.str] = None,
    db_server_name: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    oracle_creation_statements: typing.Optional[builtins.str] = None,
    oracle_host: typing.Optional[builtins.str] = None,
    oracle_password: typing.Optional[builtins.str] = None,
    oracle_port: typing.Optional[builtins.str] = None,
    oracle_revocation_statements: typing.Optional[builtins.str] = None,
    oracle_service_name: typing.Optional[builtins.str] = None,
    oracle_username: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__202e7b5291be57808e1bceedc9b320c99abe7a68c8f3a8de480d70783f913baf(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f01818ddafd2db34be37d6c53bb2b7063fb2ce62736fb49635ea40cdf3afcfeb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce2fb1af0a86ea02488945637748bc35af8e4abdc672575cbe8cabcd3262dea3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__331cd083ea94e7abb026e92b9fcb440ea92b4b02fcb8fc9d446c143c8e987ffd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fe3deb76cbf189c9647d491f8dd68fbcb61cf1353553b4ef4cf378dd45afd50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71fbb46347a1a649c147395d5742637ccd8df15079ed60868bad56198faf755c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2554348e5b40fd83794ec39002ce6783606e0fef075696ab2b20f3c8431d3e34(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__863fc3df9c9f8e8b0977da598f38cdc0a68ba6fc844bcd02caebdcef1ff208e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d49cbe045caed4b56be7f96b947a4f88434e7c86282d0f7ea78750a6bb92922e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6d67d405f0b19a55f4d3d56c4e2ee13214dc5cb261a8b695b0d92a9b68f570(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a68292ecef968651c956f6c05bbbaaddbeeaa9def6e10cebd1be17cc32c386e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed394894c1757cde12eeeeeb54b0392b0f4d5dde0cb656403b4720caae9095be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__455e7e3962229d777dad5a14b95de1c561acf6a033a552779f89c9e8b7811b1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e05735eaca4a1142b2ecd17c6a4c53d4367786d5f62a4563db447d91c1ac2d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5be46cf93c58f901616dd199e93becbe34dca1f073c45718c70a3ab79c31caba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fd9c32de24e2889e9ba322a8decfb60b51cdcebc138a27fba1e406ad1cdd31a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f87b5a2376cf69ff7f4a33a76f61eda12b5cbdfa409f26844aef5acd59848a6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__076f37a0160a255132671ee0c9905263b94d693069d301e03532015f941e41b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4032f60e0f7aafa5ff1272d4e6e2ad42794e143a322a1bc927cc1f26648bd283(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    custom_username_template: typing.Optional[builtins.str] = None,
    db_server_certificates: typing.Optional[builtins.str] = None,
    db_server_name: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    oracle_creation_statements: typing.Optional[builtins.str] = None,
    oracle_host: typing.Optional[builtins.str] = None,
    oracle_password: typing.Optional[builtins.str] = None,
    oracle_port: typing.Optional[builtins.str] = None,
    oracle_revocation_statements: typing.Optional[builtins.str] = None,
    oracle_service_name: typing.Optional[builtins.str] = None,
    oracle_username: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
