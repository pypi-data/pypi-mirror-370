'''
# `akeyless_dynamic_secret_cassandra`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_cassandra`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra).
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


class DynamicSecretCassandra(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretCassandra.DynamicSecretCassandra",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra akeyless_dynamic_secret_cassandra}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        cassandra_creation_statements: typing.Optional[builtins.str] = None,
        cassandra_hosts: typing.Optional[builtins.str] = None,
        cassandra_password: typing.Optional[builtins.str] = None,
        cassandra_port: typing.Optional[builtins.str] = None,
        cassandra_username: typing.Optional[builtins.str] = None,
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ssl_certificate: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra akeyless_dynamic_secret_cassandra} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#name DynamicSecretCassandra#name}
        :param cassandra_creation_statements: Cassandra Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_creation_statements DynamicSecretCassandra#cassandra_creation_statements}
        :param cassandra_hosts: Cassandra hosts names or IP addresses, comma separated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_hosts DynamicSecretCassandra#cassandra_hosts}
        :param cassandra_password: Cassandra superuser password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_password DynamicSecretCassandra#cassandra_password}
        :param cassandra_port: Cassandra port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_port DynamicSecretCassandra#cassandra_port}
        :param cassandra_username: Cassandra superuser user name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_username DynamicSecretCassandra#cassandra_username}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#custom_username_template DynamicSecretCassandra#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#encryption_key_name DynamicSecretCassandra#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#id DynamicSecretCassandra#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#password_length DynamicSecretCassandra#password_length}
        :param ssl: Enable/Disable SSL [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#ssl DynamicSecretCassandra#ssl}
        :param ssl_certificate: SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#ssl_certificate DynamicSecretCassandra#ssl_certificate}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#tags DynamicSecretCassandra#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#target_name DynamicSecretCassandra#target_name}
        :param user_ttl: User TTL (<=60m for access token). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#user_ttl DynamicSecretCassandra#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d76fd6a9a35c63ba744b389a4fbc3bdcc8b06aca069d035707770994f85e489)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretCassandraConfig(
            name=name,
            cassandra_creation_statements=cassandra_creation_statements,
            cassandra_hosts=cassandra_hosts,
            cassandra_password=cassandra_password,
            cassandra_port=cassandra_port,
            cassandra_username=cassandra_username,
            custom_username_template=custom_username_template,
            encryption_key_name=encryption_key_name,
            id=id,
            password_length=password_length,
            ssl=ssl,
            ssl_certificate=ssl_certificate,
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
        '''Generates CDKTF code for importing a DynamicSecretCassandra resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretCassandra to import.
        :param import_from_id: The id of the existing DynamicSecretCassandra that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretCassandra to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95cd9c8709f4c15282a404e8761f8c6228ea2b4baa7884e8318b8d9aa3128855)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCassandraCreationStatements")
    def reset_cassandra_creation_statements(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCassandraCreationStatements", []))

    @jsii.member(jsii_name="resetCassandraHosts")
    def reset_cassandra_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCassandraHosts", []))

    @jsii.member(jsii_name="resetCassandraPassword")
    def reset_cassandra_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCassandraPassword", []))

    @jsii.member(jsii_name="resetCassandraPort")
    def reset_cassandra_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCassandraPort", []))

    @jsii.member(jsii_name="resetCassandraUsername")
    def reset_cassandra_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCassandraUsername", []))

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

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetSslCertificate")
    def reset_ssl_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslCertificate", []))

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
    @jsii.member(jsii_name="cassandraCreationStatementsInput")
    def cassandra_creation_statements_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cassandraCreationStatementsInput"))

    @builtins.property
    @jsii.member(jsii_name="cassandraHostsInput")
    def cassandra_hosts_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cassandraHostsInput"))

    @builtins.property
    @jsii.member(jsii_name="cassandraPasswordInput")
    def cassandra_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cassandraPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="cassandraPortInput")
    def cassandra_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cassandraPortInput"))

    @builtins.property
    @jsii.member(jsii_name="cassandraUsernameInput")
    def cassandra_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cassandraUsernameInput"))

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
    @jsii.member(jsii_name="cassandraCreationStatements")
    def cassandra_creation_statements(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cassandraCreationStatements"))

    @cassandra_creation_statements.setter
    def cassandra_creation_statements(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f929fb723db6b48792d267880d91e1806497ca01d0a9cba8f8cdb06b4f6d9cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cassandraCreationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="cassandraHosts")
    def cassandra_hosts(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cassandraHosts"))

    @cassandra_hosts.setter
    def cassandra_hosts(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be09ba64a9e9da7090048fb1b960d7b61b4ed3b32e2cda70dc0b9dd661875577)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cassandraHosts", value)

    @builtins.property
    @jsii.member(jsii_name="cassandraPassword")
    def cassandra_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cassandraPassword"))

    @cassandra_password.setter
    def cassandra_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__882f4f615b38af3618e7433f56f736ae0ea7800e193c03d7225d5e09f5012c14)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cassandraPassword", value)

    @builtins.property
    @jsii.member(jsii_name="cassandraPort")
    def cassandra_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cassandraPort"))

    @cassandra_port.setter
    def cassandra_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605ad85dbe09dafa667819986fcd9ac1db723a154ef03654d148f21f4f7a3e4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cassandraPort", value)

    @builtins.property
    @jsii.member(jsii_name="cassandraUsername")
    def cassandra_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cassandraUsername"))

    @cassandra_username.setter
    def cassandra_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf5cd1c02836ced60582b245bcb831c4a4e0742c5d6d8a280449dc65efa5b8af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cassandraUsername", value)

    @builtins.property
    @jsii.member(jsii_name="customUsernameTemplate")
    def custom_username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customUsernameTemplate"))

    @custom_username_template.setter
    def custom_username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7716fc4cecf6781128372f8724eb7874fa1edce3ad1a653a74d0ee4d39388cec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customUsernameTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__101efc7df9d2039101bb7d4fbd80d264cbb035444d3c342ee3e7986005b6086c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccd933a73d4b26bee5c8472fc720594c28cd09b504c6f1ea9a230d6c3e201f09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b2d92e472bdfbdba56c6f9c1a9a53e7cac8d2471e2eb9c8d5aa8d85c9604e4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1aadb39942b21dc5d87fdc436db76d88f43d99f2e15512cac7ea8a4ba336029)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__bf384f68669c8a9c89ce78740580f05d4b3d9186f64c1eed7cde84799e95db09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value)

    @builtins.property
    @jsii.member(jsii_name="sslCertificate")
    def ssl_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslCertificate"))

    @ssl_certificate.setter
    def ssl_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__257ffc5bfc61b6784f4c49eb4a88a2b5a553e1866199253dfe3a06b9cbc6bbcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sslCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab3c5cb1928eb6ee1555c9db6b505112ba421ed71f5df8259f331ac046db2a54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03e746c69d183ffeae90ae71c7812e9c52dc1b243143d174c49abd65d7dd58df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12aa1a237af8c9c45df01ca29a376d2e4ddbbeb80fbf8535f8e4bb07aeed485e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretCassandra.DynamicSecretCassandraConfig",
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
        "cassandra_creation_statements": "cassandraCreationStatements",
        "cassandra_hosts": "cassandraHosts",
        "cassandra_password": "cassandraPassword",
        "cassandra_port": "cassandraPort",
        "cassandra_username": "cassandraUsername",
        "custom_username_template": "customUsernameTemplate",
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
        "password_length": "passwordLength",
        "ssl": "ssl",
        "ssl_certificate": "sslCertificate",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class DynamicSecretCassandraConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cassandra_creation_statements: typing.Optional[builtins.str] = None,
        cassandra_hosts: typing.Optional[builtins.str] = None,
        cassandra_password: typing.Optional[builtins.str] = None,
        cassandra_port: typing.Optional[builtins.str] = None,
        cassandra_username: typing.Optional[builtins.str] = None,
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ssl_certificate: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#name DynamicSecretCassandra#name}
        :param cassandra_creation_statements: Cassandra Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_creation_statements DynamicSecretCassandra#cassandra_creation_statements}
        :param cassandra_hosts: Cassandra hosts names or IP addresses, comma separated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_hosts DynamicSecretCassandra#cassandra_hosts}
        :param cassandra_password: Cassandra superuser password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_password DynamicSecretCassandra#cassandra_password}
        :param cassandra_port: Cassandra port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_port DynamicSecretCassandra#cassandra_port}
        :param cassandra_username: Cassandra superuser user name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_username DynamicSecretCassandra#cassandra_username}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#custom_username_template DynamicSecretCassandra#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#encryption_key_name DynamicSecretCassandra#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#id DynamicSecretCassandra#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#password_length DynamicSecretCassandra#password_length}
        :param ssl: Enable/Disable SSL [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#ssl DynamicSecretCassandra#ssl}
        :param ssl_certificate: SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#ssl_certificate DynamicSecretCassandra#ssl_certificate}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#tags DynamicSecretCassandra#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#target_name DynamicSecretCassandra#target_name}
        :param user_ttl: User TTL (<=60m for access token). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#user_ttl DynamicSecretCassandra#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c5401cc8e6208370dfdda9c1e9425259ea5f9ece6e7e209be7fb1b5f6e8994e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument cassandra_creation_statements", value=cassandra_creation_statements, expected_type=type_hints["cassandra_creation_statements"])
            check_type(argname="argument cassandra_hosts", value=cassandra_hosts, expected_type=type_hints["cassandra_hosts"])
            check_type(argname="argument cassandra_password", value=cassandra_password, expected_type=type_hints["cassandra_password"])
            check_type(argname="argument cassandra_port", value=cassandra_port, expected_type=type_hints["cassandra_port"])
            check_type(argname="argument cassandra_username", value=cassandra_username, expected_type=type_hints["cassandra_username"])
            check_type(argname="argument custom_username_template", value=custom_username_template, expected_type=type_hints["custom_username_template"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument ssl_certificate", value=ssl_certificate, expected_type=type_hints["ssl_certificate"])
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
        if cassandra_creation_statements is not None:
            self._values["cassandra_creation_statements"] = cassandra_creation_statements
        if cassandra_hosts is not None:
            self._values["cassandra_hosts"] = cassandra_hosts
        if cassandra_password is not None:
            self._values["cassandra_password"] = cassandra_password
        if cassandra_port is not None:
            self._values["cassandra_port"] = cassandra_port
        if cassandra_username is not None:
            self._values["cassandra_username"] = cassandra_username
        if custom_username_template is not None:
            self._values["custom_username_template"] = custom_username_template
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
        if password_length is not None:
            self._values["password_length"] = password_length
        if ssl is not None:
            self._values["ssl"] = ssl
        if ssl_certificate is not None:
            self._values["ssl_certificate"] = ssl_certificate
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#name DynamicSecretCassandra#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cassandra_creation_statements(self) -> typing.Optional[builtins.str]:
        '''Cassandra Creation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_creation_statements DynamicSecretCassandra#cassandra_creation_statements}
        '''
        result = self._values.get("cassandra_creation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cassandra_hosts(self) -> typing.Optional[builtins.str]:
        '''Cassandra hosts names or IP addresses, comma separated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_hosts DynamicSecretCassandra#cassandra_hosts}
        '''
        result = self._values.get("cassandra_hosts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cassandra_password(self) -> typing.Optional[builtins.str]:
        '''Cassandra superuser password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_password DynamicSecretCassandra#cassandra_password}
        '''
        result = self._values.get("cassandra_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cassandra_port(self) -> typing.Optional[builtins.str]:
        '''Cassandra port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_port DynamicSecretCassandra#cassandra_port}
        '''
        result = self._values.get("cassandra_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cassandra_username(self) -> typing.Optional[builtins.str]:
        '''Cassandra superuser user name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#cassandra_username DynamicSecretCassandra#cassandra_username}
        '''
        result = self._values.get("cassandra_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_username_template(self) -> typing.Optional[builtins.str]:
        '''Customize how temporary usernames are generated using go template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#custom_username_template DynamicSecretCassandra#custom_username_template}
        '''
        result = self._values.get("custom_username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#encryption_key_name DynamicSecretCassandra#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#id DynamicSecretCassandra#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#password_length DynamicSecretCassandra#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable/Disable SSL [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#ssl DynamicSecretCassandra#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ssl_certificate(self) -> typing.Optional[builtins.str]:
        '''SSL CA certificate in base64 encoding generated from a trusted Certificate Authority (CA).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#ssl_certificate DynamicSecretCassandra#ssl_certificate}
        '''
        result = self._values.get("ssl_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#tags DynamicSecretCassandra#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#target_name DynamicSecretCassandra#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL (<=60m for access token).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_cassandra#user_ttl DynamicSecretCassandra#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretCassandraConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretCassandra",
    "DynamicSecretCassandraConfig",
]

publication.publish()

def _typecheckingstub__5d76fd6a9a35c63ba744b389a4fbc3bdcc8b06aca069d035707770994f85e489(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    cassandra_creation_statements: typing.Optional[builtins.str] = None,
    cassandra_hosts: typing.Optional[builtins.str] = None,
    cassandra_password: typing.Optional[builtins.str] = None,
    cassandra_port: typing.Optional[builtins.str] = None,
    cassandra_username: typing.Optional[builtins.str] = None,
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ssl_certificate: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__95cd9c8709f4c15282a404e8761f8c6228ea2b4baa7884e8318b8d9aa3128855(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f929fb723db6b48792d267880d91e1806497ca01d0a9cba8f8cdb06b4f6d9cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be09ba64a9e9da7090048fb1b960d7b61b4ed3b32e2cda70dc0b9dd661875577(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__882f4f615b38af3618e7433f56f736ae0ea7800e193c03d7225d5e09f5012c14(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605ad85dbe09dafa667819986fcd9ac1db723a154ef03654d148f21f4f7a3e4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf5cd1c02836ced60582b245bcb831c4a4e0742c5d6d8a280449dc65efa5b8af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7716fc4cecf6781128372f8724eb7874fa1edce3ad1a653a74d0ee4d39388cec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101efc7df9d2039101bb7d4fbd80d264cbb035444d3c342ee3e7986005b6086c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccd933a73d4b26bee5c8472fc720594c28cd09b504c6f1ea9a230d6c3e201f09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b2d92e472bdfbdba56c6f9c1a9a53e7cac8d2471e2eb9c8d5aa8d85c9604e4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1aadb39942b21dc5d87fdc436db76d88f43d99f2e15512cac7ea8a4ba336029(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf384f68669c8a9c89ce78740580f05d4b3d9186f64c1eed7cde84799e95db09(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__257ffc5bfc61b6784f4c49eb4a88a2b5a553e1866199253dfe3a06b9cbc6bbcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab3c5cb1928eb6ee1555c9db6b505112ba421ed71f5df8259f331ac046db2a54(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03e746c69d183ffeae90ae71c7812e9c52dc1b243143d174c49abd65d7dd58df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12aa1a237af8c9c45df01ca29a376d2e4ddbbeb80fbf8535f8e4bb07aeed485e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c5401cc8e6208370dfdda9c1e9425259ea5f9ece6e7e209be7fb1b5f6e8994e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    cassandra_creation_statements: typing.Optional[builtins.str] = None,
    cassandra_hosts: typing.Optional[builtins.str] = None,
    cassandra_password: typing.Optional[builtins.str] = None,
    cassandra_port: typing.Optional[builtins.str] = None,
    cassandra_username: typing.Optional[builtins.str] = None,
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ssl_certificate: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
