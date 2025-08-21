'''
# `akeyless_target_zerossl`

Refer to the Terraform Registry for docs: [`akeyless_target_zerossl`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl).
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


class TargetZerossl(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.targetZerossl.TargetZerossl",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl akeyless_target_zerossl}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        api_key: builtins.str,
        imap_fqdn: builtins.str,
        imap_password: builtins.str,
        imap_username: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        imap_port: typing.Optional[builtins.str] = None,
        imap_target_email: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl akeyless_target_zerossl} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_key: API Key of the ZeroSSLTarget account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#api_key TargetZerossl#api_key}
        :param imap_fqdn: FQDN of the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_fqdn TargetZerossl#imap_fqdn}
        :param imap_password: Password to access the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_password TargetZerossl#imap_password}
        :param imap_username: Username to access the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_username TargetZerossl#imap_username}
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#name TargetZerossl#name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#description TargetZerossl#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#id TargetZerossl#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param imap_port: Port of the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_port TargetZerossl#imap_port}
        :param imap_target_email: Email to use when asking ZeroSSL to send a validation email, if empty will use username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_target_email TargetZerossl#imap_target_email}
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#key TargetZerossl#key}
        :param timeout: Timeout waiting for certificate validation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#timeout TargetZerossl#timeout}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e0f12be2eb564f0211b7c34ac79e9281d06deb67aa2d38b42054362ba7ed4b9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TargetZerosslConfig(
            api_key=api_key,
            imap_fqdn=imap_fqdn,
            imap_password=imap_password,
            imap_username=imap_username,
            name=name,
            description=description,
            id=id,
            imap_port=imap_port,
            imap_target_email=imap_target_email,
            key=key,
            timeout=timeout,
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
        '''Generates CDKTF code for importing a TargetZerossl resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TargetZerossl to import.
        :param import_from_id: The id of the existing TargetZerossl that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TargetZerossl to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3834134f906fbb183ed7d431c2af9674f7436ba47a9a68b2796f5092ac9547a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetImapPort")
    def reset_imap_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImapPort", []))

    @jsii.member(jsii_name="resetImapTargetEmail")
    def reset_imap_target_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImapTargetEmail", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

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
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="imapFqdnInput")
    def imap_fqdn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imapFqdnInput"))

    @builtins.property
    @jsii.member(jsii_name="imapPasswordInput")
    def imap_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imapPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="imapPortInput")
    def imap_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imapPortInput"))

    @builtins.property
    @jsii.member(jsii_name="imapTargetEmailInput")
    def imap_target_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imapTargetEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="imapUsernameInput")
    def imap_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imapUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4f2dc7409517d57f1918146bda353c3ea4ca3cae3bce7fa6bc0a2d58e0e9e5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa440560673ad77938d4fcaeaa5656cb45feb79f4aeb681aff5aaaeb15081736)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c601ffe9cc8518da30564d681fda6d33cfa349a426bd9f2df25665260e7f7174)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="imapFqdn")
    def imap_fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imapFqdn"))

    @imap_fqdn.setter
    def imap_fqdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af00033dd998a5d70491ec5a2f1364f4547f978e08365a253dc9cd7119b2d18d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imapFqdn", value)

    @builtins.property
    @jsii.member(jsii_name="imapPassword")
    def imap_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imapPassword"))

    @imap_password.setter
    def imap_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80b9de828cc99cb33ccce1aac5f104666f2a27db399fdc5c6be5377771f3d413)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imapPassword", value)

    @builtins.property
    @jsii.member(jsii_name="imapPort")
    def imap_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imapPort"))

    @imap_port.setter
    def imap_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ba0e098070509d328c7c361ccdd709f8722361859656143befa2bae43c03622)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imapPort", value)

    @builtins.property
    @jsii.member(jsii_name="imapTargetEmail")
    def imap_target_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imapTargetEmail"))

    @imap_target_email.setter
    def imap_target_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbc0bee64a90422005ebeac01395ad8ed9df8d678dd838295cae2d7cd1a2525e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imapTargetEmail", value)

    @builtins.property
    @jsii.member(jsii_name="imapUsername")
    def imap_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imapUsername"))

    @imap_username.setter
    def imap_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa39992d0e41f7a74c7cd74d9a9025d463387df40e7e3eaf755a768b975d342f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imapUsername", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5fe87d1e3613902ac9e5edfa6450a98dfe1ef03b15edd53009354ae8ebba9d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e91d7d2552030c321659ebc6efe1a232615921fd5533ebdfe35e09cdb1db259c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95291182259e76e7cbeb61409da9663cd8e9f3b49dfe43a063a9856cc7edcaac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value)


@jsii.data_type(
    jsii_type="akeyless.targetZerossl.TargetZerosslConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "api_key": "apiKey",
        "imap_fqdn": "imapFqdn",
        "imap_password": "imapPassword",
        "imap_username": "imapUsername",
        "name": "name",
        "description": "description",
        "id": "id",
        "imap_port": "imapPort",
        "imap_target_email": "imapTargetEmail",
        "key": "key",
        "timeout": "timeout",
    },
)
class TargetZerosslConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        api_key: builtins.str,
        imap_fqdn: builtins.str,
        imap_password: builtins.str,
        imap_username: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        imap_port: typing.Optional[builtins.str] = None,
        imap_target_email: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param api_key: API Key of the ZeroSSLTarget account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#api_key TargetZerossl#api_key}
        :param imap_fqdn: FQDN of the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_fqdn TargetZerossl#imap_fqdn}
        :param imap_password: Password to access the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_password TargetZerossl#imap_password}
        :param imap_username: Username to access the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_username TargetZerossl#imap_username}
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#name TargetZerossl#name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#description TargetZerossl#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#id TargetZerossl#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param imap_port: Port of the IMAP service. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_port TargetZerossl#imap_port}
        :param imap_target_email: Email to use when asking ZeroSSL to send a validation email, if empty will use username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_target_email TargetZerossl#imap_target_email}
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#key TargetZerossl#key}
        :param timeout: Timeout waiting for certificate validation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#timeout TargetZerossl#timeout}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de7794ffb8e675e5cc5527a6fd5c349d66c389237d5cfa3591cb14b9bfc103ea)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument imap_fqdn", value=imap_fqdn, expected_type=type_hints["imap_fqdn"])
            check_type(argname="argument imap_password", value=imap_password, expected_type=type_hints["imap_password"])
            check_type(argname="argument imap_username", value=imap_username, expected_type=type_hints["imap_username"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument imap_port", value=imap_port, expected_type=type_hints["imap_port"])
            check_type(argname="argument imap_target_email", value=imap_target_email, expected_type=type_hints["imap_target_email"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_key": api_key,
            "imap_fqdn": imap_fqdn,
            "imap_password": imap_password,
            "imap_username": imap_username,
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
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if imap_port is not None:
            self._values["imap_port"] = imap_port
        if imap_target_email is not None:
            self._values["imap_target_email"] = imap_target_email
        if key is not None:
            self._values["key"] = key
        if timeout is not None:
            self._values["timeout"] = timeout

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
    def api_key(self) -> builtins.str:
        '''API Key of the ZeroSSLTarget account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#api_key TargetZerossl#api_key}
        '''
        result = self._values.get("api_key")
        assert result is not None, "Required property 'api_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def imap_fqdn(self) -> builtins.str:
        '''FQDN of the IMAP service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_fqdn TargetZerossl#imap_fqdn}
        '''
        result = self._values.get("imap_fqdn")
        assert result is not None, "Required property 'imap_fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def imap_password(self) -> builtins.str:
        '''Password to access the IMAP service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_password TargetZerossl#imap_password}
        '''
        result = self._values.get("imap_password")
        assert result is not None, "Required property 'imap_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def imap_username(self) -> builtins.str:
        '''Username to access the IMAP service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_username TargetZerossl#imap_username}
        '''
        result = self._values.get("imap_username")
        assert result is not None, "Required property 'imap_username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Target name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#name TargetZerossl#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#description TargetZerossl#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#id TargetZerossl#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def imap_port(self) -> typing.Optional[builtins.str]:
        '''Port of the IMAP service.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_port TargetZerossl#imap_port}
        '''
        result = self._values.get("imap_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def imap_target_email(self) -> typing.Optional[builtins.str]:
        '''Email to use when asking ZeroSSL to send a validation email, if empty will use username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#imap_target_email TargetZerossl#imap_target_email}
        '''
        result = self._values.get("imap_target_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#key TargetZerossl#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''Timeout waiting for certificate validation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_zerossl#timeout TargetZerossl#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetZerosslConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TargetZerossl",
    "TargetZerosslConfig",
]

publication.publish()

def _typecheckingstub__4e0f12be2eb564f0211b7c34ac79e9281d06deb67aa2d38b42054362ba7ed4b9(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    api_key: builtins.str,
    imap_fqdn: builtins.str,
    imap_password: builtins.str,
    imap_username: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    imap_port: typing.Optional[builtins.str] = None,
    imap_target_email: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__f3834134f906fbb183ed7d431c2af9674f7436ba47a9a68b2796f5092ac9547a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f2dc7409517d57f1918146bda353c3ea4ca3cae3bce7fa6bc0a2d58e0e9e5c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa440560673ad77938d4fcaeaa5656cb45feb79f4aeb681aff5aaaeb15081736(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c601ffe9cc8518da30564d681fda6d33cfa349a426bd9f2df25665260e7f7174(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af00033dd998a5d70491ec5a2f1364f4547f978e08365a253dc9cd7119b2d18d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b9de828cc99cb33ccce1aac5f104666f2a27db399fdc5c6be5377771f3d413(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba0e098070509d328c7c361ccdd709f8722361859656143befa2bae43c03622(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbc0bee64a90422005ebeac01395ad8ed9df8d678dd838295cae2d7cd1a2525e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa39992d0e41f7a74c7cd74d9a9025d463387df40e7e3eaf755a768b975d342f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5fe87d1e3613902ac9e5edfa6450a98dfe1ef03b15edd53009354ae8ebba9d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e91d7d2552030c321659ebc6efe1a232615921fd5533ebdfe35e09cdb1db259c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95291182259e76e7cbeb61409da9663cd8e9f3b49dfe43a063a9856cc7edcaac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7794ffb8e675e5cc5527a6fd5c349d66c389237d5cfa3591cb14b9bfc103ea(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key: builtins.str,
    imap_fqdn: builtins.str,
    imap_password: builtins.str,
    imap_username: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    imap_port: typing.Optional[builtins.str] = None,
    imap_target_email: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    timeout: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
