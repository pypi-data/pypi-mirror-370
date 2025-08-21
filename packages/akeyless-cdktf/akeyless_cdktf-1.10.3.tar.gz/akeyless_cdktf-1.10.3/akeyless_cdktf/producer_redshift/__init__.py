'''
# `akeyless_producer_redshift`

Refer to the Terraform Registry for docs: [`akeyless_producer_redshift`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift).
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


class ProducerRedshift(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerRedshift.ProducerRedshift",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift akeyless_producer_redshift}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        creation_statements: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key: typing.Optional[builtins.str] = None,
        redshift_db_name: typing.Optional[builtins.str] = None,
        redshift_host: typing.Optional[builtins.str] = None,
        redshift_password: typing.Optional[builtins.str] = None,
        redshift_port: typing.Optional[builtins.str] = None,
        redshift_username: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift akeyless_producer_redshift} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#name ProducerRedshift#name}
        :param creation_statements: Redshift Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#creation_statements ProducerRedshift#creation_statements}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#id ProducerRedshift#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#producer_encryption_key ProducerRedshift#producer_encryption_key}
        :param redshift_db_name: Redshift DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_db_name ProducerRedshift#redshift_db_name}
        :param redshift_host: Redshift host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_host ProducerRedshift#redshift_host}
        :param redshift_password: Redshift password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_password ProducerRedshift#redshift_password}
        :param redshift_port: Redshift port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_port ProducerRedshift#redshift_port}
        :param redshift_username: redshiftL user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_username ProducerRedshift#redshift_username}
        :param secure_access_db_name: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_db_name ProducerRedshift#secure_access_db_name}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_enable ProducerRedshift#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_host ProducerRedshift#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_web ProducerRedshift#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#tags ProducerRedshift#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#target_name ProducerRedshift#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#user_ttl ProducerRedshift#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ee7c49f8ec9b73be53559bd90f07882e62446e8abfb7028350da4eaf2f803fb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerRedshiftConfig(
            name=name,
            creation_statements=creation_statements,
            id=id,
            producer_encryption_key=producer_encryption_key,
            redshift_db_name=redshift_db_name,
            redshift_host=redshift_host,
            redshift_password=redshift_password,
            redshift_port=redshift_port,
            redshift_username=redshift_username,
            secure_access_db_name=secure_access_db_name,
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
        '''Generates CDKTF code for importing a ProducerRedshift resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerRedshift to import.
        :param import_from_id: The id of the existing ProducerRedshift that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerRedshift to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6a7d228f0c3a5f2a422958647f91dff1e59b82b2fe1d2c57ad60dfc5802c4b2)
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

    @jsii.member(jsii_name="resetProducerEncryptionKey")
    def reset_producer_encryption_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKey", []))

    @jsii.member(jsii_name="resetRedshiftDbName")
    def reset_redshift_db_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshiftDbName", []))

    @jsii.member(jsii_name="resetRedshiftHost")
    def reset_redshift_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshiftHost", []))

    @jsii.member(jsii_name="resetRedshiftPassword")
    def reset_redshift_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshiftPassword", []))

    @jsii.member(jsii_name="resetRedshiftPort")
    def reset_redshift_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshiftPort", []))

    @jsii.member(jsii_name="resetRedshiftUsername")
    def reset_redshift_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedshiftUsername", []))

    @jsii.member(jsii_name="resetSecureAccessDbName")
    def reset_secure_access_db_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessDbName", []))

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
    @jsii.member(jsii_name="producerEncryptionKeyInput")
    def producer_encryption_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "producerEncryptionKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="redshiftDbNameInput")
    def redshift_db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redshiftDbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="redshiftHostInput")
    def redshift_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redshiftHostInput"))

    @builtins.property
    @jsii.member(jsii_name="redshiftPasswordInput")
    def redshift_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redshiftPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="redshiftPortInput")
    def redshift_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redshiftPortInput"))

    @builtins.property
    @jsii.member(jsii_name="redshiftUsernameInput")
    def redshift_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redshiftUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbNameInput")
    def secure_access_db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessDbNameInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__101bd9c85d2a6e838b5365511d049de685696a2b55663d7a6115b49dfcfc7742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "creationStatements", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dae9f5644abedafe08523e16fcb36a8aea42523eb30225899257c8ee45639ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c471f7398d5d9d9ffcf2536d8c234d659f776f9c802fbf4f4a6d53e02b7f840)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKey")
    def producer_encryption_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKey"))

    @producer_encryption_key.setter
    def producer_encryption_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc8164cb18fee0b656004a05cd9be3d5f6bf427339445c46030473b36caa9b28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKey", value)

    @builtins.property
    @jsii.member(jsii_name="redshiftDbName")
    def redshift_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redshiftDbName"))

    @redshift_db_name.setter
    def redshift_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959de7425cc6a115aba2daabef97ed2cae8b0562cf8b832a7e96433db4d4af53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redshiftDbName", value)

    @builtins.property
    @jsii.member(jsii_name="redshiftHost")
    def redshift_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redshiftHost"))

    @redshift_host.setter
    def redshift_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eada8a2a308992dada1c369d427647f994e34a8482ee48dfe6fcb267642eab3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redshiftHost", value)

    @builtins.property
    @jsii.member(jsii_name="redshiftPassword")
    def redshift_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redshiftPassword"))

    @redshift_password.setter
    def redshift_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7d53ec6d04e8ac2ef9b7b3087bc74f709de7fe6dda6ec096c6f1272afcdcb35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redshiftPassword", value)

    @builtins.property
    @jsii.member(jsii_name="redshiftPort")
    def redshift_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redshiftPort"))

    @redshift_port.setter
    def redshift_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__750c401837b8c2a248215ef7e6dac7b2bb9ff6bc10ee560e87c872543189e91b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redshiftPort", value)

    @builtins.property
    @jsii.member(jsii_name="redshiftUsername")
    def redshift_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redshiftUsername"))

    @redshift_username.setter
    def redshift_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__876e48161b77ac6d5c3b5af80765d689b7f1494907858e5c67420e3beaec7cd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redshiftUsername", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbName")
    def secure_access_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbName"))

    @secure_access_db_name.setter
    def secure_access_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed8e658c7127848d638a9b28e2d685f29ea7d4d8b773259d97f1a0926eb8595)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec538f3100d9b542ef3ea10ddae9878fc902666d998941b448e0d6ca2f5570d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555afdf4399afdef9c8e466eed8ca7cde8a96594bd0c3a6e69c28e5e0689af5d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__020b9dc30c1a21561978e669ac0bd4a4349e170880a330946286280c32814de9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dca122289078d39b1dc39e8388be7da1a7d548e16c6518f6e8e6b0b8b757aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4362de1adcda7770eb828f4e3bf9e56a65fc52564b5c6c4effcdb93f50c49f6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__322b049d9c9b5f853107fb41dbb74b3e6925a3e0f2d0a47692845c67e114cac8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerRedshift.ProducerRedshiftConfig",
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
        "producer_encryption_key": "producerEncryptionKey",
        "redshift_db_name": "redshiftDbName",
        "redshift_host": "redshiftHost",
        "redshift_password": "redshiftPassword",
        "redshift_port": "redshiftPort",
        "redshift_username": "redshiftUsername",
        "secure_access_db_name": "secureAccessDbName",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_web": "secureAccessWeb",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerRedshiftConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        producer_encryption_key: typing.Optional[builtins.str] = None,
        redshift_db_name: typing.Optional[builtins.str] = None,
        redshift_host: typing.Optional[builtins.str] = None,
        redshift_password: typing.Optional[builtins.str] = None,
        redshift_port: typing.Optional[builtins.str] = None,
        redshift_username: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#name ProducerRedshift#name}
        :param creation_statements: Redshift Creation Statements. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#creation_statements ProducerRedshift#creation_statements}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#id ProducerRedshift#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#producer_encryption_key ProducerRedshift#producer_encryption_key}
        :param redshift_db_name: Redshift DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_db_name ProducerRedshift#redshift_db_name}
        :param redshift_host: Redshift host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_host ProducerRedshift#redshift_host}
        :param redshift_password: Redshift password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_password ProducerRedshift#redshift_password}
        :param redshift_port: Redshift port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_port ProducerRedshift#redshift_port}
        :param redshift_username: redshiftL user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_username ProducerRedshift#redshift_username}
        :param secure_access_db_name: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_db_name ProducerRedshift#secure_access_db_name}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_enable ProducerRedshift#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_host ProducerRedshift#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_web ProducerRedshift#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#tags ProducerRedshift#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#target_name ProducerRedshift#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#user_ttl ProducerRedshift#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a40f3fb640b1da0273a0e82fc3120c83b1be47f3d64c0be5f54bc8bac664c90d)
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
            check_type(argname="argument producer_encryption_key", value=producer_encryption_key, expected_type=type_hints["producer_encryption_key"])
            check_type(argname="argument redshift_db_name", value=redshift_db_name, expected_type=type_hints["redshift_db_name"])
            check_type(argname="argument redshift_host", value=redshift_host, expected_type=type_hints["redshift_host"])
            check_type(argname="argument redshift_password", value=redshift_password, expected_type=type_hints["redshift_password"])
            check_type(argname="argument redshift_port", value=redshift_port, expected_type=type_hints["redshift_port"])
            check_type(argname="argument redshift_username", value=redshift_username, expected_type=type_hints["redshift_username"])
            check_type(argname="argument secure_access_db_name", value=secure_access_db_name, expected_type=type_hints["secure_access_db_name"])
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
        if producer_encryption_key is not None:
            self._values["producer_encryption_key"] = producer_encryption_key
        if redshift_db_name is not None:
            self._values["redshift_db_name"] = redshift_db_name
        if redshift_host is not None:
            self._values["redshift_host"] = redshift_host
        if redshift_password is not None:
            self._values["redshift_password"] = redshift_password
        if redshift_port is not None:
            self._values["redshift_port"] = redshift_port
        if redshift_username is not None:
            self._values["redshift_username"] = redshift_username
        if secure_access_db_name is not None:
            self._values["secure_access_db_name"] = secure_access_db_name
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#name ProducerRedshift#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def creation_statements(self) -> typing.Optional[builtins.str]:
        '''Redshift Creation Statements.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#creation_statements ProducerRedshift#creation_statements}
        '''
        result = self._values.get("creation_statements")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#id ProducerRedshift#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#producer_encryption_key ProducerRedshift#producer_encryption_key}
        '''
        result = self._values.get("producer_encryption_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_db_name(self) -> typing.Optional[builtins.str]:
        '''Redshift DB name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_db_name ProducerRedshift#redshift_db_name}
        '''
        result = self._values.get("redshift_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_host(self) -> typing.Optional[builtins.str]:
        '''Redshift host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_host ProducerRedshift#redshift_host}
        '''
        result = self._values.get("redshift_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_password(self) -> typing.Optional[builtins.str]:
        '''Redshift password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_password ProducerRedshift#redshift_password}
        '''
        result = self._values.get("redshift_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_port(self) -> typing.Optional[builtins.str]:
        '''Redshift port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_port ProducerRedshift#redshift_port}
        '''
        result = self._values.get("redshift_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift_username(self) -> typing.Optional[builtins.str]:
        '''redshiftL user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#redshift_username ProducerRedshift#redshift_username}
        '''
        result = self._values.get("redshift_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_name(self) -> typing.Optional[builtins.str]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_db_name ProducerRedshift#secure_access_db_name}
        '''
        result = self._values.get("secure_access_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_enable ProducerRedshift#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target DB servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_host ProducerRedshift#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#secure_access_web ProducerRedshift#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#tags ProducerRedshift#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#target_name ProducerRedshift#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_redshift#user_ttl ProducerRedshift#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerRedshiftConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerRedshift",
    "ProducerRedshiftConfig",
]

publication.publish()

def _typecheckingstub__2ee7c49f8ec9b73be53559bd90f07882e62446e8abfb7028350da4eaf2f803fb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    creation_statements: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key: typing.Optional[builtins.str] = None,
    redshift_db_name: typing.Optional[builtins.str] = None,
    redshift_host: typing.Optional[builtins.str] = None,
    redshift_password: typing.Optional[builtins.str] = None,
    redshift_port: typing.Optional[builtins.str] = None,
    redshift_username: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__f6a7d228f0c3a5f2a422958647f91dff1e59b82b2fe1d2c57ad60dfc5802c4b2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__101bd9c85d2a6e838b5365511d049de685696a2b55663d7a6115b49dfcfc7742(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dae9f5644abedafe08523e16fcb36a8aea42523eb30225899257c8ee45639ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c471f7398d5d9d9ffcf2536d8c234d659f776f9c802fbf4f4a6d53e02b7f840(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc8164cb18fee0b656004a05cd9be3d5f6bf427339445c46030473b36caa9b28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__959de7425cc6a115aba2daabef97ed2cae8b0562cf8b832a7e96433db4d4af53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eada8a2a308992dada1c369d427647f994e34a8482ee48dfe6fcb267642eab3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7d53ec6d04e8ac2ef9b7b3087bc74f709de7fe6dda6ec096c6f1272afcdcb35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__750c401837b8c2a248215ef7e6dac7b2bb9ff6bc10ee560e87c872543189e91b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__876e48161b77ac6d5c3b5af80765d689b7f1494907858e5c67420e3beaec7cd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed8e658c7127848d638a9b28e2d685f29ea7d4d8b773259d97f1a0926eb8595(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec538f3100d9b542ef3ea10ddae9878fc902666d998941b448e0d6ca2f5570d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555afdf4399afdef9c8e466eed8ca7cde8a96594bd0c3a6e69c28e5e0689af5d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020b9dc30c1a21561978e669ac0bd4a4349e170880a330946286280c32814de9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dca122289078d39b1dc39e8388be7da1a7d548e16c6518f6e8e6b0b8b757aeb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4362de1adcda7770eb828f4e3bf9e56a65fc52564b5c6c4effcdb93f50c49f6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__322b049d9c9b5f853107fb41dbb74b3e6925a3e0f2d0a47692845c67e114cac8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a40f3fb640b1da0273a0e82fc3120c83b1be47f3d64c0be5f54bc8bac664c90d(
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
    producer_encryption_key: typing.Optional[builtins.str] = None,
    redshift_db_name: typing.Optional[builtins.str] = None,
    redshift_host: typing.Optional[builtins.str] = None,
    redshift_password: typing.Optional[builtins.str] = None,
    redshift_port: typing.Optional[builtins.str] = None,
    redshift_username: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
