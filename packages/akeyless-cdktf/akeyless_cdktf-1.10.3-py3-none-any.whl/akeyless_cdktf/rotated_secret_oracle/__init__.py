'''
# `akeyless_rotated_secret_oracle`

Refer to the Terraform Registry for docs: [`akeyless_rotated_secret_oracle`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle).
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


class RotatedSecretOracle(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.rotatedSecretOracle.RotatedSecretOracle",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle akeyless_rotated_secret_oracle}.'''

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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle akeyless_rotated_secret_oracle} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#name RotatedSecretOracle#name}
        :param rotator_type: The rotator type [target/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotator_type RotatedSecretOracle#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#target_name RotatedSecretOracle#target_name}
        :param authentication_credentials: The credentials to connect with [use-self-creds/use-target-creds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#authentication_credentials RotatedSecretOracle#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#auto_rotate RotatedSecretOracle#auto_rotate}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#description RotatedSecretOracle#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#id RotatedSecretOracle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#key RotatedSecretOracle#key}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#password_length RotatedSecretOracle#password_length}
        :param rotated_password: rotated-username password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotated_password RotatedSecretOracle#rotated_password}
        :param rotated_username: username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotated_username RotatedSecretOracle#rotated_username}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotation_hour RotatedSecretOracle#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotation_interval RotatedSecretOracle#rotation_interval}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#tags RotatedSecretOracle#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2214fe512bdec8a7008a27bf1e848418f4ec3d692479b8b091a54eddc6b8fbe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RotatedSecretOracleConfig(
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
        '''Generates CDKTF code for importing a RotatedSecretOracle resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RotatedSecretOracle to import.
        :param import_from_id: The id of the existing RotatedSecretOracle that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RotatedSecretOracle to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb30a7bda30ec3af26e401fbbf4d48d4f5393ae7c69c9aa9ee2f96169ec1b644)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c0eb0cc13eefdaf13e6f98419ecf82682b46a18ba55c34ab7670022bf915167b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationCredentials", value)

    @builtins.property
    @jsii.member(jsii_name="autoRotate")
    def auto_rotate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRotate"))

    @auto_rotate.setter
    def auto_rotate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f08b9a857c3e5c356bc31ab2e6c7de27c42a206eb7c5e35e729d799cd81da96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotate", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb117d2485f45cc215411a5d7da4a9bf1b9c50befbd311abac802b96329b8dac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae4d0479b2f5870fd72fa1d128688e14f75bfe3fc0142e00d6535f373f7dbde7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86fe75df912e5b998d9b0f93cb0f6cb8ee33d7049d776f34692ee5c7b3c6d0cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63a4c70c0a13609009158a32f4c1dda3f6a883ba3a11f5a703e15e905c380cb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ee9c574ab5fbf34430c9405bae3fb2c255171f6966690039a7a6b2cb6ddea76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="rotatedPassword")
    def rotated_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatedPassword"))

    @rotated_password.setter
    def rotated_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19d0004e47b50e0ee5ce126b6f9a182bea9276c3a50af1f97ad0597e533d79fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatedPassword", value)

    @builtins.property
    @jsii.member(jsii_name="rotatedUsername")
    def rotated_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatedUsername"))

    @rotated_username.setter
    def rotated_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83023ce3d62f8e5e29c93e858effa63da51ad236f6c4f57e198d15c23edb0671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatedUsername", value)

    @builtins.property
    @jsii.member(jsii_name="rotationHour")
    def rotation_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationHour"))

    @rotation_hour.setter
    def rotation_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3492277e52e35f133239dd87ef77e66032daa8ae83f7d68868a037d34dacda05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationHour", value)

    @builtins.property
    @jsii.member(jsii_name="rotationInterval")
    def rotation_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationInterval"))

    @rotation_interval.setter
    def rotation_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d7251b906175fc4f46bb68addf9de47983aed76fd70904a778b6fa913c33c31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationInterval", value)

    @builtins.property
    @jsii.member(jsii_name="rotatorType")
    def rotator_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatorType"))

    @rotator_type.setter
    def rotator_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__242826a6c8005bf431cccfb48dab3f488edf0dc446741745bfab9fa126685812)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatorType", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bfeae2664a47bd4678d35ae7c9c22bd24d7a6a4120bfd5b7d22b81493fdc7ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__317f7a5eb3ea8a9f9cdc8de080361b408c2b6a32f44d500268b82d8ecfa4eadf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)


@jsii.data_type(
    jsii_type="akeyless.rotatedSecretOracle.RotatedSecretOracleConfig",
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
class RotatedSecretOracleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#name RotatedSecretOracle#name}
        :param rotator_type: The rotator type [target/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotator_type RotatedSecretOracle#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#target_name RotatedSecretOracle#target_name}
        :param authentication_credentials: The credentials to connect with [use-self-creds/use-target-creds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#authentication_credentials RotatedSecretOracle#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#auto_rotate RotatedSecretOracle#auto_rotate}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#description RotatedSecretOracle#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#id RotatedSecretOracle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#key RotatedSecretOracle#key}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#password_length RotatedSecretOracle#password_length}
        :param rotated_password: rotated-username password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotated_password RotatedSecretOracle#rotated_password}
        :param rotated_username: username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotated_username RotatedSecretOracle#rotated_username}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotation_hour RotatedSecretOracle#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotation_interval RotatedSecretOracle#rotation_interval}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#tags RotatedSecretOracle#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f778cdb411ed63d5cd4018a1c171f41fcf730c2c059ff70169538ba2841ec43)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#name RotatedSecretOracle#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rotator_type(self) -> builtins.str:
        '''The rotator type [target/password].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotator_type RotatedSecretOracle#rotator_type}
        '''
        result = self._values.get("rotator_type")
        assert result is not None, "Required property 'rotator_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''The target name to associate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#target_name RotatedSecretOracle#target_name}
        '''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_credentials(self) -> typing.Optional[builtins.str]:
        '''The credentials to connect with [use-self-creds/use-target-creds].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#authentication_credentials RotatedSecretOracle#authentication_credentials}
        '''
        result = self._values.get("authentication_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_rotate(self) -> typing.Optional[builtins.str]:
        '''Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#auto_rotate RotatedSecretOracle#auto_rotate}
        '''
        result = self._values.get("auto_rotate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#description RotatedSecretOracle#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#id RotatedSecretOracle#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#key RotatedSecretOracle#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#password_length RotatedSecretOracle#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotated_password(self) -> typing.Optional[builtins.str]:
        '''rotated-username password (relevant only for rotator-type=password).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotated_password RotatedSecretOracle#rotated_password}
        '''
        result = self._values.get("rotated_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotated_username(self) -> typing.Optional[builtins.str]:
        '''username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotated_username RotatedSecretOracle#rotated_username}
        '''
        result = self._values.get("rotated_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_hour(self) -> typing.Optional[jsii.Number]:
        '''The Hour of the rotation in UTC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotation_hour RotatedSecretOracle#rotation_hour}
        '''
        result = self._values.get("rotation_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_interval(self) -> typing.Optional[builtins.str]:
        '''The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#rotation_interval RotatedSecretOracle#rotation_interval}
        '''
        result = self._values.get("rotation_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_oracle#tags RotatedSecretOracle#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotatedSecretOracleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RotatedSecretOracle",
    "RotatedSecretOracleConfig",
]

publication.publish()

def _typecheckingstub__b2214fe512bdec8a7008a27bf1e848418f4ec3d692479b8b091a54eddc6b8fbe(
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

def _typecheckingstub__bb30a7bda30ec3af26e401fbbf4d48d4f5393ae7c69c9aa9ee2f96169ec1b644(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0eb0cc13eefdaf13e6f98419ecf82682b46a18ba55c34ab7670022bf915167b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f08b9a857c3e5c356bc31ab2e6c7de27c42a206eb7c5e35e729d799cd81da96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb117d2485f45cc215411a5d7da4a9bf1b9c50befbd311abac802b96329b8dac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae4d0479b2f5870fd72fa1d128688e14f75bfe3fc0142e00d6535f373f7dbde7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86fe75df912e5b998d9b0f93cb0f6cb8ee33d7049d776f34692ee5c7b3c6d0cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63a4c70c0a13609009158a32f4c1dda3f6a883ba3a11f5a703e15e905c380cb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ee9c574ab5fbf34430c9405bae3fb2c255171f6966690039a7a6b2cb6ddea76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19d0004e47b50e0ee5ce126b6f9a182bea9276c3a50af1f97ad0597e533d79fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83023ce3d62f8e5e29c93e858effa63da51ad236f6c4f57e198d15c23edb0671(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3492277e52e35f133239dd87ef77e66032daa8ae83f7d68868a037d34dacda05(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d7251b906175fc4f46bb68addf9de47983aed76fd70904a778b6fa913c33c31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__242826a6c8005bf431cccfb48dab3f488edf0dc446741745bfab9fa126685812(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bfeae2664a47bd4678d35ae7c9c22bd24d7a6a4120bfd5b7d22b81493fdc7ef(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__317f7a5eb3ea8a9f9cdc8de080361b408c2b6a32f44d500268b82d8ecfa4eadf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f778cdb411ed63d5cd4018a1c171f41fcf730c2c059ff70169538ba2841ec43(
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
