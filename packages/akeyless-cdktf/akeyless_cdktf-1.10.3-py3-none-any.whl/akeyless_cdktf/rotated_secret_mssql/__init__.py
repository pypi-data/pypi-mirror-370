'''
# `akeyless_rotated_secret_mssql`

Refer to the Terraform Registry for docs: [`akeyless_rotated_secret_mssql`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql).
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


class RotatedSecretMssql(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.rotatedSecretMssql.RotatedSecretMssql",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql akeyless_rotated_secret_mssql}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        rotator_type: builtins.str,
        target_name: builtins.str,
        authentication_credentials: typing.Optional[builtins.str] = None,
        auto_rotate: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        rotated_password: typing.Optional[builtins.str] = None,
        rotated_username: typing.Optional[builtins.str] = None,
        rotation_hour: typing.Optional[jsii.Number] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql akeyless_rotated_secret_mssql} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#name RotatedSecretMssql#name}
        :param rotator_type: The rotator type [target/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotator_type RotatedSecretMssql#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#target_name RotatedSecretMssql#target_name}
        :param authentication_credentials: The credentials to connect with [use-self-creds/use-target-creds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#authentication_credentials RotatedSecretMssql#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#auto_rotate RotatedSecretMssql#auto_rotate}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#description RotatedSecretMssql#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#id RotatedSecretMssql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#key RotatedSecretMssql#key}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#password_length RotatedSecretMssql#password_length}
        :param rotated_password: rotated-username password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotated_password RotatedSecretMssql#rotated_password}
        :param rotated_username: username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotated_username RotatedSecretMssql#rotated_username}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotation_hour RotatedSecretMssql#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotation_interval RotatedSecretMssql#rotation_interval}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#tags RotatedSecretMssql#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30e4b946063030d38f168d645714b7d967a272cae12f30df869ddb986dd3097e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RotatedSecretMssqlConfig(
            name=name,
            rotator_type=rotator_type,
            target_name=target_name,
            authentication_credentials=authentication_credentials,
            auto_rotate=auto_rotate,
            description=description,
            id=id,
            key=key,
            password_length=password_length,
            rotated_password=rotated_password,
            rotated_username=rotated_username,
            rotation_hour=rotation_hour,
            rotation_interval=rotation_interval,
            tags=tags,
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
        '''Generates CDKTF code for importing a RotatedSecretMssql resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RotatedSecretMssql to import.
        :param import_from_id: The id of the existing RotatedSecretMssql that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RotatedSecretMssql to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028d72ae82c6965ac43c63676d2899c6290dd3818fc1ac26d06732e1e28f08d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAuthenticationCredentials")
    def reset_authentication_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationCredentials", []))

    @jsii.member(jsii_name="resetAutoRotate")
    def reset_auto_rotate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRotate", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

    @jsii.member(jsii_name="resetRotatedPassword")
    def reset_rotated_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotatedPassword", []))

    @jsii.member(jsii_name="resetRotatedUsername")
    def reset_rotated_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotatedUsername", []))

    @jsii.member(jsii_name="resetRotationHour")
    def reset_rotation_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationHour", []))

    @jsii.member(jsii_name="resetRotationInterval")
    def reset_rotation_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationInterval", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="authenticationCredentialsInput")
    def authentication_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationCredentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRotateInput")
    def auto_rotate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoRotateInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordLengthInput")
    def password_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="rotatedPasswordInput")
    def rotated_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotatedPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="rotatedUsernameInput")
    def rotated_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotatedUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationHourInput")
    def rotation_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rotationHourInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationIntervalInput")
    def rotation_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="rotatorTypeInput")
    def rotator_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotatorTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationCredentials")
    def authentication_credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationCredentials"))

    @authentication_credentials.setter
    def authentication_credentials(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cec7005b7f5129b7db141a8eb79139f1405754ec47be4b213740785b54a3617)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationCredentials", value)

    @builtins.property
    @jsii.member(jsii_name="autoRotate")
    def auto_rotate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRotate"))

    @auto_rotate.setter
    def auto_rotate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b2d1f44c5e3a84a8caabe5a891195bb1a0aff4fa36f178d40a99746ca84dc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotate", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e397a8e709985f7c7434c5f1b5b83170f3aac3f8072c131a610b1a3dc23d9412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b30d202d2a6e3cc1838b43d497197e2e5f1a41bc0769209844463b193d4b8412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6f990ad099184818d756715f26cac02b7111918dd27428ea8b582a867ff2667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ddaf64d8e3e88b49218b45cba7bb9a37023e5789fa4d888576a4961762f4db4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50ea63897fdf32fdb7514bc9a8ec3dbc782730c1b0a7f19ef6f32307f8f70acb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="rotatedPassword")
    def rotated_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatedPassword"))

    @rotated_password.setter
    def rotated_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9cf52bd615046a7d776bf01d3da53804c4605a1a768d44141a95d3423144470)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatedPassword", value)

    @builtins.property
    @jsii.member(jsii_name="rotatedUsername")
    def rotated_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatedUsername"))

    @rotated_username.setter
    def rotated_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4c909750f687b1658e52263d6d1e0e0d6760a92f141564774fbbc5910b53ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatedUsername", value)

    @builtins.property
    @jsii.member(jsii_name="rotationHour")
    def rotation_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationHour"))

    @rotation_hour.setter
    def rotation_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f64ebc5b87c3ac06185caef78b7a3e1d0b755b5208a5ac0d64d566c527059d85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationHour", value)

    @builtins.property
    @jsii.member(jsii_name="rotationInterval")
    def rotation_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationInterval"))

    @rotation_interval.setter
    def rotation_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abe5ff10d7c08379d2f0fb3befc19f55892f5781cde3c973eba59b147c31f7af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationInterval", value)

    @builtins.property
    @jsii.member(jsii_name="rotatorType")
    def rotator_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatorType"))

    @rotator_type.setter
    def rotator_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44d39ddfff1b569d74cb2d56cd6133968d29e4286370f264a3e9426ca03a5a2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatorType", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f336fa4cd0cce768b50935dd50e0b36ea42e42a1abf1cd6c034fd5be73ab4fa0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf2ac7527d3b1bb8406bbc32a0eeba2699607daf19185618dd44a5e9ae7f1148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)


@jsii.data_type(
    jsii_type="akeyless.rotatedSecretMssql.RotatedSecretMssqlConfig",
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
        "rotator_type": "rotatorType",
        "target_name": "targetName",
        "authentication_credentials": "authenticationCredentials",
        "auto_rotate": "autoRotate",
        "description": "description",
        "id": "id",
        "key": "key",
        "password_length": "passwordLength",
        "rotated_password": "rotatedPassword",
        "rotated_username": "rotatedUsername",
        "rotation_hour": "rotationHour",
        "rotation_interval": "rotationInterval",
        "tags": "tags",
    },
)
class RotatedSecretMssqlConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        rotator_type: builtins.str,
        target_name: builtins.str,
        authentication_credentials: typing.Optional[builtins.str] = None,
        auto_rotate: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        rotated_password: typing.Optional[builtins.str] = None,
        rotated_username: typing.Optional[builtins.str] = None,
        rotation_hour: typing.Optional[jsii.Number] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#name RotatedSecretMssql#name}
        :param rotator_type: The rotator type [target/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotator_type RotatedSecretMssql#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#target_name RotatedSecretMssql#target_name}
        :param authentication_credentials: The credentials to connect with [use-self-creds/use-target-creds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#authentication_credentials RotatedSecretMssql#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#auto_rotate RotatedSecretMssql#auto_rotate}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#description RotatedSecretMssql#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#id RotatedSecretMssql#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#key RotatedSecretMssql#key}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#password_length RotatedSecretMssql#password_length}
        :param rotated_password: rotated-username password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotated_password RotatedSecretMssql#rotated_password}
        :param rotated_username: username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotated_username RotatedSecretMssql#rotated_username}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotation_hour RotatedSecretMssql#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotation_interval RotatedSecretMssql#rotation_interval}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#tags RotatedSecretMssql#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2b015c8cbbb7e4261eeaaa02cfb766d3f3ed8a12d995270f91de3e9b0cc5aaf)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rotator_type", value=rotator_type, expected_type=type_hints["rotator_type"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument authentication_credentials", value=authentication_credentials, expected_type=type_hints["authentication_credentials"])
            check_type(argname="argument auto_rotate", value=auto_rotate, expected_type=type_hints["auto_rotate"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
            check_type(argname="argument rotated_password", value=rotated_password, expected_type=type_hints["rotated_password"])
            check_type(argname="argument rotated_username", value=rotated_username, expected_type=type_hints["rotated_username"])
            check_type(argname="argument rotation_hour", value=rotation_hour, expected_type=type_hints["rotation_hour"])
            check_type(argname="argument rotation_interval", value=rotation_interval, expected_type=type_hints["rotation_interval"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "rotator_type": rotator_type,
            "target_name": target_name,
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
        if authentication_credentials is not None:
            self._values["authentication_credentials"] = authentication_credentials
        if auto_rotate is not None:
            self._values["auto_rotate"] = auto_rotate
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if key is not None:
            self._values["key"] = key
        if password_length is not None:
            self._values["password_length"] = password_length
        if rotated_password is not None:
            self._values["rotated_password"] = rotated_password
        if rotated_username is not None:
            self._values["rotated_username"] = rotated_username
        if rotation_hour is not None:
            self._values["rotation_hour"] = rotation_hour
        if rotation_interval is not None:
            self._values["rotation_interval"] = rotation_interval
        if tags is not None:
            self._values["tags"] = tags

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
        '''Secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#name RotatedSecretMssql#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rotator_type(self) -> builtins.str:
        '''The rotator type [target/password].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotator_type RotatedSecretMssql#rotator_type}
        '''
        result = self._values.get("rotator_type")
        assert result is not None, "Required property 'rotator_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''The target name to associate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#target_name RotatedSecretMssql#target_name}
        '''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_credentials(self) -> typing.Optional[builtins.str]:
        '''The credentials to connect with [use-self-creds/use-target-creds].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#authentication_credentials RotatedSecretMssql#authentication_credentials}
        '''
        result = self._values.get("authentication_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_rotate(self) -> typing.Optional[builtins.str]:
        '''Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#auto_rotate RotatedSecretMssql#auto_rotate}
        '''
        result = self._values.get("auto_rotate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#description RotatedSecretMssql#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#id RotatedSecretMssql#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#key RotatedSecretMssql#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#password_length RotatedSecretMssql#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotated_password(self) -> typing.Optional[builtins.str]:
        '''rotated-username password (relevant only for rotator-type=password).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotated_password RotatedSecretMssql#rotated_password}
        '''
        result = self._values.get("rotated_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotated_username(self) -> typing.Optional[builtins.str]:
        '''username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotated_username RotatedSecretMssql#rotated_username}
        '''
        result = self._values.get("rotated_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_hour(self) -> typing.Optional[jsii.Number]:
        '''The Hour of the rotation in UTC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotation_hour RotatedSecretMssql#rotation_hour}
        '''
        result = self._values.get("rotation_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_interval(self) -> typing.Optional[builtins.str]:
        '''The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#rotation_interval RotatedSecretMssql#rotation_interval}
        '''
        result = self._values.get("rotation_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_mssql#tags RotatedSecretMssql#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotatedSecretMssqlConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RotatedSecretMssql",
    "RotatedSecretMssqlConfig",
]

publication.publish()

def _typecheckingstub__30e4b946063030d38f168d645714b7d967a272cae12f30df869ddb986dd3097e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    rotator_type: builtins.str,
    target_name: builtins.str,
    authentication_credentials: typing.Optional[builtins.str] = None,
    auto_rotate: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    rotated_password: typing.Optional[builtins.str] = None,
    rotated_username: typing.Optional[builtins.str] = None,
    rotation_hour: typing.Optional[jsii.Number] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__028d72ae82c6965ac43c63676d2899c6290dd3818fc1ac26d06732e1e28f08d5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cec7005b7f5129b7db141a8eb79139f1405754ec47be4b213740785b54a3617(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b2d1f44c5e3a84a8caabe5a891195bb1a0aff4fa36f178d40a99746ca84dc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e397a8e709985f7c7434c5f1b5b83170f3aac3f8072c131a610b1a3dc23d9412(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b30d202d2a6e3cc1838b43d497197e2e5f1a41bc0769209844463b193d4b8412(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f990ad099184818d756715f26cac02b7111918dd27428ea8b582a867ff2667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ddaf64d8e3e88b49218b45cba7bb9a37023e5789fa4d888576a4961762f4db4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50ea63897fdf32fdb7514bc9a8ec3dbc782730c1b0a7f19ef6f32307f8f70acb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9cf52bd615046a7d776bf01d3da53804c4605a1a768d44141a95d3423144470(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4c909750f687b1658e52263d6d1e0e0d6760a92f141564774fbbc5910b53ae7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f64ebc5b87c3ac06185caef78b7a3e1d0b755b5208a5ac0d64d566c527059d85(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abe5ff10d7c08379d2f0fb3befc19f55892f5781cde3c973eba59b147c31f7af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44d39ddfff1b569d74cb2d56cd6133968d29e4286370f264a3e9426ca03a5a2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f336fa4cd0cce768b50935dd50e0b36ea42e42a1abf1cd6c034fd5be73ab4fa0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf2ac7527d3b1bb8406bbc32a0eeba2699607daf19185618dd44a5e9ae7f1148(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2b015c8cbbb7e4261eeaaa02cfb766d3f3ed8a12d995270f91de3e9b0cc5aaf(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    rotator_type: builtins.str,
    target_name: builtins.str,
    authentication_credentials: typing.Optional[builtins.str] = None,
    auto_rotate: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    rotated_password: typing.Optional[builtins.str] = None,
    rotated_username: typing.Optional[builtins.str] = None,
    rotation_hour: typing.Optional[jsii.Number] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
