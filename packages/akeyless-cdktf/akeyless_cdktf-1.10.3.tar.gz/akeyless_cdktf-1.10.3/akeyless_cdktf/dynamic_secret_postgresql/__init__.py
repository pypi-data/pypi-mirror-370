'''
# `akeyless_dynamic_secret_postgresql`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_postgresql`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql).
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


class DynamicSecretPostgresql(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretPostgresql.DynamicSecretPostgresql",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql akeyless_dynamic_secret_postgresql}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        creation_statements: typing.Optional[builtins.str] = None,
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        postgresql_db_name: typing.Optional[builtins.str] = None,
        postgresql_host: typing.Optional[builtins.str] = None,
        postgresql_password: typing.Optional[builtins.str] = None,
        postgresql_port: typing.Optional[builtins.str] = None,
        postgresql_username: typing.Optional[builtins.str] = None,
        revocation_statements: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
        secure_access_db_schema: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql akeyless_dynamic_secret_postgresql} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#name DynamicSecretPostgresql#name}
        :param creation_statements: PostgreSQL Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#creation_statements DynamicSecretPostgresql#creation_statements}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#custom_username_template DynamicSecretPostgresql#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#encryption_key_name DynamicSecretPostgresql#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#id DynamicSecretPostgresql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#password_length DynamicSecretPostgresql#password_length}
        :param postgresql_db_name: PostgreSQL DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_db_name DynamicSecretPostgresql#postgresql_db_name}
        :param postgresql_host: PostgreSQL host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_host DynamicSecretPostgresql#postgresql_host}
        :param postgresql_password: PostgreSQL password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_password DynamicSecretPostgresql#postgresql_password}
        :param postgresql_port: PostgreSQL port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_port DynamicSecretPostgresql#postgresql_port}
        :param postgresql_username: PostgreSQL user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_username DynamicSecretPostgresql#postgresql_username}
        :param revocation_statements: PostgreSQL Revocation Statement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#revocation_statements DynamicSecretPostgresql#revocation_statements}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_bastion_issuer DynamicSecretPostgresql#secure_access_bastion_issuer}
        :param secure_access_db_name: The DB Name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_db_name DynamicSecretPostgresql#secure_access_db_name}
        :param secure_access_db_schema: The db schema. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_db_schema DynamicSecretPostgresql#secure_access_db_schema}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_enable DynamicSecretPostgresql#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_host DynamicSecretPostgresql#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_web DynamicSecretPostgresql#secure_access_web}
        :param ssl: Enable/Disable SSL [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#ssl DynamicSecretPostgresql#ssl}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#tags DynamicSecretPostgresql#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#target_name DynamicSecretPostgresql#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#user_ttl DynamicSecretPostgresql#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65bfff979479a59f73533164cdb43686257842f249f27fde05e5151484a707f9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretPostgresqlConfig(
            name=name,
            creation_statements=creation_statements,
            custom_username_template=custom_username_template,
            encryption_key_name=encryption_key_name,
            id=id,
            password_length=password_length,
            postgresql_db_name=postgresql_db_name,
            postgresql_host=postgresql_host,
            postgresql_password=postgresql_password,
            postgresql_port=postgresql_port,
            postgresql_username=postgresql_username,
            revocation_statements=revocation_statements,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_db_name=secure_access_db_name,
            secure_access_db_schema=secure_access_db_schema,
            secure_access_enable=secure_access_enable,
            secure_access_host=secure_access_host,
            secure_access_web=secure_access_web,
            ssl=ssl,
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
        '''Generates CDKTF code for importing a DynamicSecretPostgresql resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretPostgresql to import.
        :param import_from_id: The id of the existing DynamicSecretPostgresql that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretPostgresql to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bf50e43e4c63886c35e978ed48894f775be160a1dcfa9c67133c100a314fe20)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCreationStatements")
    def reset_creation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreationStatements", []))

    @jsii.member(jsii_name="resetCustomUsernameTemplate")
    def reset_custom_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUsernameTemplate", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

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

    @jsii.member(jsii_name="resetRevocationStatements")
    def reset_revocation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevocationStatements", []))

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

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

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
    @jsii.member(jsii_name="customUsernameTemplateInput")
    def custom_username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customUsernameTemplateInput"))

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
    @jsii.member(jsii_name="passwordLengthInput")
    def password_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordLengthInput"))

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
    @jsii.member(jsii_name="revocationStatementsInput")
    def revocation_statements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "revocationStatementsInput"))

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
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sslInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__84d8ec04536ec4563f26d201b3b50fcdbcf7ceaacd63251ed630558f67de4272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="customUsernameTemplate")
    def custom_username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customUsernameTemplate"))

    @custom_username_template.setter
    def custom_username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fff9c4ad5f80ffbd20336e74b290f02ba5b1dbd5359c215e98ee931c4ec30a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customUsernameTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb49fa8803ce22ba6b1eb8bb2484eceba78fc73f5e58f0703b791503f89b469f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98fab812a000d8bf199e525a6ea6679d33630e0577b0447e405136656c1d33f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a11af814ec17c0592578049e686bfb3d865afdff43866978ff9b7472ffe1bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d2357a433f9b793d16ce5dc2af5c1d8ef97850a6f6fadf18804abb7d4d3fe36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlDbName")
    def postgresql_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlDbName"))

    @postgresql_db_name.setter
    def postgresql_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a06b5b0a78906287b429e1e795aa7091748b193fe0ca8ea3605c663ea15812e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlDbName", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlHost")
    def postgresql_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlHost"))

    @postgresql_host.setter
    def postgresql_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01932e67c800b93c5db694b3dd8641d177828542ad17862c99011202430fb42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlHost", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlPassword")
    def postgresql_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlPassword"))

    @postgresql_password.setter
    def postgresql_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c69ff626f672e14ae224e3ec2cb6fce0d4cbae7b2ac5e152fc477945d8825b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlPassword", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlPort")
    def postgresql_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlPort"))

    @postgresql_port.setter
    def postgresql_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70534c848bb5eb01b1752b950a8052bf77ea639ffb440eadbd250fa6941b34b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlPort", value)

    @builtins.property
    @jsii.member(jsii_name="postgresqlUsername")
    def postgresql_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postgresqlUsername"))

    @postgresql_username.setter
    def postgresql_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b75c4708034e2811ae1f7e4cffb6e49dc34ec0e85040d1092058aaf4847def19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postgresqlUsername", value)

    @builtins.property
    @jsii.member(jsii_name="revocationStatements")
    def revocation_statements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revocationStatements"))

    @revocation_statements.setter
    def revocation_statements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74d60d9abc321282575cc11123ba6b1c3bb59bef10c91a3940c3f3de42bfb1b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revocationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bc582d6772fe5c6b7fbe65d9fbc4192ed5c21198cd6ab3be71cee05ef86bf8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbName")
    def secure_access_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbName"))

    @secure_access_db_name.setter
    def secure_access_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b6302a493b11595c8da5546acd7a1005d25153ee2472c95b97565b24b451d80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbSchema")
    def secure_access_db_schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbSchema"))

    @secure_access_db_schema.setter
    def secure_access_db_schema(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25a4b3e584663c15af63929335cc128f71ca99c111c6ff0a913ff0dd08cca0da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbSchema", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3799a70ed292e60c6dc0bbe1c8b2773dcfa4e22bd46c4d21af168c2b4bb6d40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b73ac90e62ec2842d5b7d4552a0bec4bed6d2f388793acbe2e47256cfc3fe82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1aba7705ac1fbaf1dde39f8401d57794673f56e43d637b67d532ad2b8ab2b9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__4d8f9b0d5b9f517b5a23f7be409da2af62e1d8416fce5d33ff7fb6e1e8dd3ad5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99807821af07a89816c84c79bf6e769a148a12a441f99e018395704db3039674)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98b1429f019e21c35cbd199810e5bad47b3ab2c2fae559738f82101ac0faa2f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29e157cfcb23c1f2de0585ded4a06d63e0757735d0abccd69fef1daa4f5fd117)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretPostgresql.DynamicSecretPostgresqlConfig",
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
        "custom_username_template": "customUsernameTemplate",
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
        "password_length": "passwordLength",
        "postgresql_db_name": "postgresqlDbName",
        "postgresql_host": "postgresqlHost",
        "postgresql_password": "postgresqlPassword",
        "postgresql_port": "postgresqlPort",
        "postgresql_username": "postgresqlUsername",
        "revocation_statements": "revocationStatements",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_db_name": "secureAccessDbName",
        "secure_access_db_schema": "secureAccessDbSchema",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_web": "secureAccessWeb",
        "ssl": "ssl",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class DynamicSecretPostgresqlConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        postgresql_db_name: typing.Optional[builtins.str] = None,
        postgresql_host: typing.Optional[builtins.str] = None,
        postgresql_password: typing.Optional[builtins.str] = None,
        postgresql_port: typing.Optional[builtins.str] = None,
        postgresql_username: typing.Optional[builtins.str] = None,
        revocation_statements: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
        secure_access_db_schema: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#name DynamicSecretPostgresql#name}
        :param creation_statements: PostgreSQL Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#creation_statements DynamicSecretPostgresql#creation_statements}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#custom_username_template DynamicSecretPostgresql#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#encryption_key_name DynamicSecretPostgresql#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#id DynamicSecretPostgresql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#password_length DynamicSecretPostgresql#password_length}
        :param postgresql_db_name: PostgreSQL DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_db_name DynamicSecretPostgresql#postgresql_db_name}
        :param postgresql_host: PostgreSQL host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_host DynamicSecretPostgresql#postgresql_host}
        :param postgresql_password: PostgreSQL password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_password DynamicSecretPostgresql#postgresql_password}
        :param postgresql_port: PostgreSQL port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_port DynamicSecretPostgresql#postgresql_port}
        :param postgresql_username: PostgreSQL user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_username DynamicSecretPostgresql#postgresql_username}
        :param revocation_statements: PostgreSQL Revocation Statement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#revocation_statements DynamicSecretPostgresql#revocation_statements}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_bastion_issuer DynamicSecretPostgresql#secure_access_bastion_issuer}
        :param secure_access_db_name: The DB Name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_db_name DynamicSecretPostgresql#secure_access_db_name}
        :param secure_access_db_schema: The db schema. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_db_schema DynamicSecretPostgresql#secure_access_db_schema}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_enable DynamicSecretPostgresql#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_host DynamicSecretPostgresql#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_web DynamicSecretPostgresql#secure_access_web}
        :param ssl: Enable/Disable SSL [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#ssl DynamicSecretPostgresql#ssl}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#tags DynamicSecretPostgresql#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#target_name DynamicSecretPostgresql#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#user_ttl DynamicSecretPostgresql#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac6aecc96ba573105ed22760b2e35ade0ff3f5a42749316509f8e2fad22b8cec)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument creation_statements", value=creation_statements, expected_type=type_hints["creation_statements"])
            check_type(argname="argument custom_username_template", value=custom_username_template, expected_type=type_hints["custom_username_template"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
            check_type(argname="argument postgresql_db_name", value=postgresql_db_name, expected_type=type_hints["postgresql_db_name"])
            check_type(argname="argument postgresql_host", value=postgresql_host, expected_type=type_hints["postgresql_host"])
            check_type(argname="argument postgresql_password", value=postgresql_password, expected_type=type_hints["postgresql_password"])
            check_type(argname="argument postgresql_port", value=postgresql_port, expected_type=type_hints["postgresql_port"])
            check_type(argname="argument postgresql_username", value=postgresql_username, expected_type=type_hints["postgresql_username"])
            check_type(argname="argument revocation_statements", value=revocation_statements, expected_type=type_hints["revocation_statements"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_db_name", value=secure_access_db_name, expected_type=type_hints["secure_access_db_name"])
            check_type(argname="argument secure_access_db_schema", value=secure_access_db_schema, expected_type=type_hints["secure_access_db_schema"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_host", value=secure_access_host, expected_type=type_hints["secure_access_host"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
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
        if custom_username_template is not None:
            self._values["custom_username_template"] = custom_username_template
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
        if password_length is not None:
            self._values["password_length"] = password_length
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
        if revocation_statements is not None:
            self._values["revocation_statements"] = revocation_statements
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
        if ssl is not None:
            self._values["ssl"] = ssl
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#name DynamicSecretPostgresql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def creation_statements(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL Creation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#creation_statements DynamicSecretPostgresql#creation_statements}
        '''
        result = self._values.get("creation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_username_template(self) -> typing.Optional[builtins.str]:
        '''Customize how temporary usernames are generated using go template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#custom_username_template DynamicSecretPostgresql#custom_username_template}
        '''
        result = self._values.get("custom_username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#encryption_key_name DynamicSecretPostgresql#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#id DynamicSecretPostgresql#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#password_length DynamicSecretPostgresql#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_db_name(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL DB name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_db_name DynamicSecretPostgresql#postgresql_db_name}
        '''
        result = self._values.get("postgresql_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_host(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_host DynamicSecretPostgresql#postgresql_host}
        '''
        result = self._values.get("postgresql_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_password(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_password DynamicSecretPostgresql#postgresql_password}
        '''
        result = self._values.get("postgresql_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_port(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_port DynamicSecretPostgresql#postgresql_port}
        '''
        result = self._values.get("postgresql_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postgresql_username(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#postgresql_username DynamicSecretPostgresql#postgresql_username}
        '''
        result = self._values.get("postgresql_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revocation_statements(self) -> typing.Optional[builtins.str]:
        '''PostgreSQL Revocation Statement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#revocation_statements DynamicSecretPostgresql#revocation_statements}
        '''
        result = self._values.get("revocation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_bastion_issuer DynamicSecretPostgresql#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_name(self) -> typing.Optional[builtins.str]:
        '''The DB Name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_db_name DynamicSecretPostgresql#secure_access_db_name}
        '''
        result = self._values.get("secure_access_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_schema(self) -> typing.Optional[builtins.str]:
        '''The db schema.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_db_schema DynamicSecretPostgresql#secure_access_db_schema}
        '''
        result = self._values.get("secure_access_db_schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_enable DynamicSecretPostgresql#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target DB servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_host DynamicSecretPostgresql#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#secure_access_web DynamicSecretPostgresql#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable/Disable SSL [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#ssl DynamicSecretPostgresql#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#tags DynamicSecretPostgresql#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#target_name DynamicSecretPostgresql#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_postgresql#user_ttl DynamicSecretPostgresql#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretPostgresqlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretPostgresql",
    "DynamicSecretPostgresqlConfig",
]

publication.publish()

def _typecheckingstub__65bfff979479a59f73533164cdb43686257842f249f27fde05e5151484a707f9(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    creation_statements: typing.Optional[builtins.str] = None,
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    postgresql_db_name: typing.Optional[builtins.str] = None,
    postgresql_host: typing.Optional[builtins.str] = None,
    postgresql_password: typing.Optional[builtins.str] = None,
    postgresql_port: typing.Optional[builtins.str] = None,
    postgresql_username: typing.Optional[builtins.str] = None,
    revocation_statements: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_db_schema: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__6bf50e43e4c63886c35e978ed48894f775be160a1dcfa9c67133c100a314fe20(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84d8ec04536ec4563f26d201b3b50fcdbcf7ceaacd63251ed630558f67de4272(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fff9c4ad5f80ffbd20336e74b290f02ba5b1dbd5359c215e98ee931c4ec30a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb49fa8803ce22ba6b1eb8bb2484eceba78fc73f5e58f0703b791503f89b469f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98fab812a000d8bf199e525a6ea6679d33630e0577b0447e405136656c1d33f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a11af814ec17c0592578049e686bfb3d865afdff43866978ff9b7472ffe1bfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d2357a433f9b793d16ce5dc2af5c1d8ef97850a6f6fadf18804abb7d4d3fe36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a06b5b0a78906287b429e1e795aa7091748b193fe0ca8ea3605c663ea15812e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b01932e67c800b93c5db694b3dd8641d177828542ad17862c99011202430fb42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c69ff626f672e14ae224e3ec2cb6fce0d4cbae7b2ac5e152fc477945d8825b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70534c848bb5eb01b1752b950a8052bf77ea639ffb440eadbd250fa6941b34b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b75c4708034e2811ae1f7e4cffb6e49dc34ec0e85040d1092058aaf4847def19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74d60d9abc321282575cc11123ba6b1c3bb59bef10c91a3940c3f3de42bfb1b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bc582d6772fe5c6b7fbe65d9fbc4192ed5c21198cd6ab3be71cee05ef86bf8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b6302a493b11595c8da5546acd7a1005d25153ee2472c95b97565b24b451d80(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25a4b3e584663c15af63929335cc128f71ca99c111c6ff0a913ff0dd08cca0da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3799a70ed292e60c6dc0bbe1c8b2773dcfa4e22bd46c4d21af168c2b4bb6d40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b73ac90e62ec2842d5b7d4552a0bec4bed6d2f388793acbe2e47256cfc3fe82(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1aba7705ac1fbaf1dde39f8401d57794673f56e43d637b67d532ad2b8ab2b9b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d8f9b0d5b9f517b5a23f7be409da2af62e1d8416fce5d33ff7fb6e1e8dd3ad5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99807821af07a89816c84c79bf6e769a148a12a441f99e018395704db3039674(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98b1429f019e21c35cbd199810e5bad47b3ab2c2fae559738f82101ac0faa2f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29e157cfcb23c1f2de0585ded4a06d63e0757735d0abccd69fef1daa4f5fd117(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac6aecc96ba573105ed22760b2e35ade0ff3f5a42749316509f8e2fad22b8cec(
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
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    postgresql_db_name: typing.Optional[builtins.str] = None,
    postgresql_host: typing.Optional[builtins.str] = None,
    postgresql_password: typing.Optional[builtins.str] = None,
    postgresql_port: typing.Optional[builtins.str] = None,
    postgresql_username: typing.Optional[builtins.str] = None,
    revocation_statements: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_db_schema: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
