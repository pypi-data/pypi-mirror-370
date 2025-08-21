'''
# `akeyless_rotated_secret`

Refer to the Terraform Registry for docs: [`akeyless_rotated_secret`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret).
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


class RotatedSecret(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.rotatedSecret.RotatedSecret",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret akeyless_rotated_secret}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        rotator_type: builtins.str,
        target_name: builtins.str,
        api_id: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        authentication_credentials: typing.Optional[builtins.str] = None,
        auto_rotate: typing.Optional[builtins.str] = None,
        custom_payload: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        rotated_password: typing.Optional[builtins.str] = None,
        rotated_username: typing.Optional[builtins.str] = None,
        rotation_hour: typing.Optional[jsii.Number] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        rotator_custom_cmd: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_attribute: typing.Optional[builtins.str] = None,
        user_dn: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret akeyless_rotated_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#name RotatedSecret#name}
        :param rotator_type: The rotator type password/target/api-key/ldap/custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotator_type RotatedSecret#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#target_name RotatedSecret#target_name}
        :param api_id: API ID to rotate (relevant only for rotator-type=api-key). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#api_id RotatedSecret#api_id}
        :param api_key: API key to rotate (relevant only for rotator-type=api-key). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#api_key RotatedSecret#api_key}
        :param authentication_credentials: The credentials to connect with use-user-creds/use-target-creds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#authentication_credentials RotatedSecret#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#auto_rotate RotatedSecret#auto_rotate}
        :param custom_payload: Secret payload to be sent with rotation request (relevant only for rotator-type=custom). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#custom_payload RotatedSecret#custom_payload}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#description RotatedSecret#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#id RotatedSecret#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#key RotatedSecret#key}
        :param rotated_password: rotated-username password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotated_password RotatedSecret#rotated_password}
        :param rotated_username: username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotated_username RotatedSecret#rotated_username}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotation_hour RotatedSecret#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotation_interval RotatedSecret#rotation_interval}
        :param rotator_custom_cmd: Custom rotation command (relevant only for ssh target). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotator_custom_cmd RotatedSecret#rotator_custom_cmd}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#tags RotatedSecret#tags}
        :param user_attribute: LDAP User Attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#user_attribute RotatedSecret#user_attribute}
        :param user_dn: Base DN to Perform User Search. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#user_dn RotatedSecret#user_dn}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__201902411666063d7e1d343ba6baeed3715b4dc5854ec3155cb55d97bd7f62db)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RotatedSecretConfig(
            name=name,
            rotator_type=rotator_type,
            target_name=target_name,
            api_id=api_id,
            api_key=api_key,
            authentication_credentials=authentication_credentials,
            auto_rotate=auto_rotate,
            custom_payload=custom_payload,
            description=description,
            id=id,
            key=key,
            rotated_password=rotated_password,
            rotated_username=rotated_username,
            rotation_hour=rotation_hour,
            rotation_interval=rotation_interval,
            rotator_custom_cmd=rotator_custom_cmd,
            tags=tags,
            user_attribute=user_attribute,
            user_dn=user_dn,
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
        '''Generates CDKTF code for importing a RotatedSecret resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RotatedSecret to import.
        :param import_from_id: The id of the existing RotatedSecret that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RotatedSecret to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b142cbdd1520d53df52b12579cc5906f7ae966eb27030939a3471d46b63727)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetApiId")
    def reset_api_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiId", []))

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetAuthenticationCredentials")
    def reset_authentication_credentials(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationCredentials", []))

    @jsii.member(jsii_name="resetAutoRotate")
    def reset_auto_rotate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRotate", []))

    @jsii.member(jsii_name="resetCustomPayload")
    def reset_custom_payload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomPayload", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

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

    @jsii.member(jsii_name="resetRotatorCustomCmd")
    def reset_rotator_custom_cmd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotatorCustomCmd", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUserAttribute")
    def reset_user_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserAttribute", []))

    @jsii.member(jsii_name="resetUserDn")
    def reset_user_dn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserDn", []))

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
    @jsii.member(jsii_name="apiIdInput")
    def api_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiIdInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationCredentialsInput")
    def authentication_credentials_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationCredentialsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRotateInput")
    def auto_rotate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoRotateInput"))

    @builtins.property
    @jsii.member(jsii_name="customPayloadInput")
    def custom_payload_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customPayloadInput"))

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
    @jsii.member(jsii_name="rotatorCustomCmdInput")
    def rotator_custom_cmd_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotatorCustomCmdInput"))

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
    @jsii.member(jsii_name="userAttributeInput")
    def user_attribute_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userAttributeInput"))

    @builtins.property
    @jsii.member(jsii_name="userDnInput")
    def user_dn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDnInput"))

    @builtins.property
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @api_id.setter
    def api_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c238d212bd981beb0e297436fb9d69b78eb9b5ab2a83c47cc64f982dde6929f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiId", value)

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__502d0dbb15407ea297e404eb56772f797ea0af56eb863dd108bd70d37278ed68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value)

    @builtins.property
    @jsii.member(jsii_name="authenticationCredentials")
    def authentication_credentials(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationCredentials"))

    @authentication_credentials.setter
    def authentication_credentials(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb8b56a34b6f6ef3e2a231faddabd2ca900b60c2f8c3da5cd2595ee75f209ba6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationCredentials", value)

    @builtins.property
    @jsii.member(jsii_name="autoRotate")
    def auto_rotate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRotate"))

    @auto_rotate.setter
    def auto_rotate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ea2586804e6200303ec0fa0aeb71727f0d6fe449f8ed71b4ab9e513fa63f2af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotate", value)

    @builtins.property
    @jsii.member(jsii_name="customPayload")
    def custom_payload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customPayload"))

    @custom_payload.setter
    def custom_payload(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4b243e71884bdb87090ba14939af3644e47153ddf8269565e3265fe73c70a7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customPayload", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af5af5655c9eb361287b9e9a79263d4ca0dc72afc94d1d9e2e49aff56249526d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c794e7257145b14040e865404bf0a94a151acef1ff0353efc9e8fdd4242aa6cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c3861dd545b56200044a1553df819f251ad281b147605bbcd059f5e7d312029)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__116d210615cc3f3d98b26b66da8d6bf50c6739da91b272d9e3f78fa7505bf8fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="rotatedPassword")
    def rotated_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatedPassword"))

    @rotated_password.setter
    def rotated_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aefe8e908a30f68c5e9054e0c1ff6fa3f203abee84b861e50b5a9b1bf169ae19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatedPassword", value)

    @builtins.property
    @jsii.member(jsii_name="rotatedUsername")
    def rotated_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatedUsername"))

    @rotated_username.setter
    def rotated_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f84226da74bcda546736e7af450011c655ce1cd0945e43b1e1da89bd26e536a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatedUsername", value)

    @builtins.property
    @jsii.member(jsii_name="rotationHour")
    def rotation_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationHour"))

    @rotation_hour.setter
    def rotation_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85bc0e2a1a5cc915d80efc46eb979e04d6a790748fa5f9afd5bbbb20e7082e90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationHour", value)

    @builtins.property
    @jsii.member(jsii_name="rotationInterval")
    def rotation_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationInterval"))

    @rotation_interval.setter
    def rotation_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff86112a2d2ec82b37d08241df56d0dbe53d9afcfd5f6c2570470b80abbc14e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationInterval", value)

    @builtins.property
    @jsii.member(jsii_name="rotatorCustomCmd")
    def rotator_custom_cmd(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatorCustomCmd"))

    @rotator_custom_cmd.setter
    def rotator_custom_cmd(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76d3723fe586a344eec0eebea35b9192b938e6bd0b86507c5a425f97ca4530f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatorCustomCmd", value)

    @builtins.property
    @jsii.member(jsii_name="rotatorType")
    def rotator_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatorType"))

    @rotator_type.setter
    def rotator_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f409e175371641e27dd6490dcf8e525868eaf392be1ab7fd04e1dfc4febf7ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatorType", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5a66f749e97f160247fd69ca91bb3fa97144e6e2893d3d498597cef086a0708)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__296e0320c0d070053ccb7bb217ac7a1acfec138ab5736eee321c174c2e835563)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userAttribute")
    def user_attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userAttribute"))

    @user_attribute.setter
    def user_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e1dcce4dc5c914a9b08d861e48b0351e10792a621a66a1baf71294f38792cb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="userDn")
    def user_dn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userDn"))

    @user_dn.setter
    def user_dn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a8ce5eaa72ce43af33fb98bd0d22a41649d12d9db887759e8db75d75e2770da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userDn", value)


@jsii.data_type(
    jsii_type="akeyless.rotatedSecret.RotatedSecretConfig",
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
        "api_id": "apiId",
        "api_key": "apiKey",
        "authentication_credentials": "authenticationCredentials",
        "auto_rotate": "autoRotate",
        "custom_payload": "customPayload",
        "description": "description",
        "id": "id",
        "key": "key",
        "rotated_password": "rotatedPassword",
        "rotated_username": "rotatedUsername",
        "rotation_hour": "rotationHour",
        "rotation_interval": "rotationInterval",
        "rotator_custom_cmd": "rotatorCustomCmd",
        "tags": "tags",
        "user_attribute": "userAttribute",
        "user_dn": "userDn",
    },
)
class RotatedSecretConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        api_id: typing.Optional[builtins.str] = None,
        api_key: typing.Optional[builtins.str] = None,
        authentication_credentials: typing.Optional[builtins.str] = None,
        auto_rotate: typing.Optional[builtins.str] = None,
        custom_payload: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        rotated_password: typing.Optional[builtins.str] = None,
        rotated_username: typing.Optional[builtins.str] = None,
        rotation_hour: typing.Optional[jsii.Number] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        rotator_custom_cmd: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_attribute: typing.Optional[builtins.str] = None,
        user_dn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#name RotatedSecret#name}
        :param rotator_type: The rotator type password/target/api-key/ldap/custom. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotator_type RotatedSecret#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#target_name RotatedSecret#target_name}
        :param api_id: API ID to rotate (relevant only for rotator-type=api-key). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#api_id RotatedSecret#api_id}
        :param api_key: API key to rotate (relevant only for rotator-type=api-key). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#api_key RotatedSecret#api_key}
        :param authentication_credentials: The credentials to connect with use-user-creds/use-target-creds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#authentication_credentials RotatedSecret#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#auto_rotate RotatedSecret#auto_rotate}
        :param custom_payload: Secret payload to be sent with rotation request (relevant only for rotator-type=custom). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#custom_payload RotatedSecret#custom_payload}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#description RotatedSecret#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#id RotatedSecret#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#key RotatedSecret#key}
        :param rotated_password: rotated-username password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotated_password RotatedSecret#rotated_password}
        :param rotated_username: username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotated_username RotatedSecret#rotated_username}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotation_hour RotatedSecret#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotation_interval RotatedSecret#rotation_interval}
        :param rotator_custom_cmd: Custom rotation command (relevant only for ssh target). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotator_custom_cmd RotatedSecret#rotator_custom_cmd}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#tags RotatedSecret#tags}
        :param user_attribute: LDAP User Attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#user_attribute RotatedSecret#user_attribute}
        :param user_dn: Base DN to Perform User Search. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#user_dn RotatedSecret#user_dn}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23049b997d55f1337f789b415d699778a97f3385956ad0a824fa6a8b0320d3d5)
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
            check_type(argname="argument api_id", value=api_id, expected_type=type_hints["api_id"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument authentication_credentials", value=authentication_credentials, expected_type=type_hints["authentication_credentials"])
            check_type(argname="argument auto_rotate", value=auto_rotate, expected_type=type_hints["auto_rotate"])
            check_type(argname="argument custom_payload", value=custom_payload, expected_type=type_hints["custom_payload"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument rotated_password", value=rotated_password, expected_type=type_hints["rotated_password"])
            check_type(argname="argument rotated_username", value=rotated_username, expected_type=type_hints["rotated_username"])
            check_type(argname="argument rotation_hour", value=rotation_hour, expected_type=type_hints["rotation_hour"])
            check_type(argname="argument rotation_interval", value=rotation_interval, expected_type=type_hints["rotation_interval"])
            check_type(argname="argument rotator_custom_cmd", value=rotator_custom_cmd, expected_type=type_hints["rotator_custom_cmd"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument user_attribute", value=user_attribute, expected_type=type_hints["user_attribute"])
            check_type(argname="argument user_dn", value=user_dn, expected_type=type_hints["user_dn"])
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
        if api_id is not None:
            self._values["api_id"] = api_id
        if api_key is not None:
            self._values["api_key"] = api_key
        if authentication_credentials is not None:
            self._values["authentication_credentials"] = authentication_credentials
        if auto_rotate is not None:
            self._values["auto_rotate"] = auto_rotate
        if custom_payload is not None:
            self._values["custom_payload"] = custom_payload
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if key is not None:
            self._values["key"] = key
        if rotated_password is not None:
            self._values["rotated_password"] = rotated_password
        if rotated_username is not None:
            self._values["rotated_username"] = rotated_username
        if rotation_hour is not None:
            self._values["rotation_hour"] = rotation_hour
        if rotation_interval is not None:
            self._values["rotation_interval"] = rotation_interval
        if rotator_custom_cmd is not None:
            self._values["rotator_custom_cmd"] = rotator_custom_cmd
        if tags is not None:
            self._values["tags"] = tags
        if user_attribute is not None:
            self._values["user_attribute"] = user_attribute
        if user_dn is not None:
            self._values["user_dn"] = user_dn

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#name RotatedSecret#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rotator_type(self) -> builtins.str:
        '''The rotator type password/target/api-key/ldap/custom.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotator_type RotatedSecret#rotator_type}
        '''
        result = self._values.get("rotator_type")
        assert result is not None, "Required property 'rotator_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''The target name to associate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#target_name RotatedSecret#target_name}
        '''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_id(self) -> typing.Optional[builtins.str]:
        '''API ID to rotate (relevant only for rotator-type=api-key).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#api_id RotatedSecret#api_id}
        '''
        result = self._values.get("api_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''API key to rotate (relevant only for rotator-type=api-key).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#api_key RotatedSecret#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authentication_credentials(self) -> typing.Optional[builtins.str]:
        '''The credentials to connect with use-user-creds/use-target-creds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#authentication_credentials RotatedSecret#authentication_credentials}
        '''
        result = self._values.get("authentication_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_rotate(self) -> typing.Optional[builtins.str]:
        '''Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#auto_rotate RotatedSecret#auto_rotate}
        '''
        result = self._values.get("auto_rotate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_payload(self) -> typing.Optional[builtins.str]:
        '''Secret payload to be sent with rotation request (relevant only for rotator-type=custom).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#custom_payload RotatedSecret#custom_payload}
        '''
        result = self._values.get("custom_payload")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#description RotatedSecret#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#id RotatedSecret#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#key RotatedSecret#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotated_password(self) -> typing.Optional[builtins.str]:
        '''rotated-username password (relevant only for rotator-type=password).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotated_password RotatedSecret#rotated_password}
        '''
        result = self._values.get("rotated_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotated_username(self) -> typing.Optional[builtins.str]:
        '''username to be rotated, if selected use-self-creds at rotator-creds-type, this username will try to rotate it's own password, if use-target-creds is selected, target credentials will be use to rotate the rotated-password (relevant only for rotator-type=password).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotated_username RotatedSecret#rotated_username}
        '''
        result = self._values.get("rotated_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_hour(self) -> typing.Optional[jsii.Number]:
        '''The Hour of the rotation in UTC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotation_hour RotatedSecret#rotation_hour}
        '''
        result = self._values.get("rotation_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_interval(self) -> typing.Optional[builtins.str]:
        '''The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotation_interval RotatedSecret#rotation_interval}
        '''
        result = self._values.get("rotation_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotator_custom_cmd(self) -> typing.Optional[builtins.str]:
        '''Custom rotation command (relevant only for ssh target).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#rotator_custom_cmd RotatedSecret#rotator_custom_cmd}
        '''
        result = self._values.get("rotator_custom_cmd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#tags RotatedSecret#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_attribute(self) -> typing.Optional[builtins.str]:
        '''LDAP User Attribute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#user_attribute RotatedSecret#user_attribute}
        '''
        result = self._values.get("user_attribute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_dn(self) -> typing.Optional[builtins.str]:
        '''Base DN to Perform User Search.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret#user_dn RotatedSecret#user_dn}
        '''
        result = self._values.get("user_dn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotatedSecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RotatedSecret",
    "RotatedSecretConfig",
]

publication.publish()

def _typecheckingstub__201902411666063d7e1d343ba6baeed3715b4dc5854ec3155cb55d97bd7f62db(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    rotator_type: builtins.str,
    target_name: builtins.str,
    api_id: typing.Optional[builtins.str] = None,
    api_key: typing.Optional[builtins.str] = None,
    authentication_credentials: typing.Optional[builtins.str] = None,
    auto_rotate: typing.Optional[builtins.str] = None,
    custom_payload: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    rotated_password: typing.Optional[builtins.str] = None,
    rotated_username: typing.Optional[builtins.str] = None,
    rotation_hour: typing.Optional[jsii.Number] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    rotator_custom_cmd: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_attribute: typing.Optional[builtins.str] = None,
    user_dn: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__68b142cbdd1520d53df52b12579cc5906f7ae966eb27030939a3471d46b63727(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c238d212bd981beb0e297436fb9d69b78eb9b5ab2a83c47cc64f982dde6929f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__502d0dbb15407ea297e404eb56772f797ea0af56eb863dd108bd70d37278ed68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb8b56a34b6f6ef3e2a231faddabd2ca900b60c2f8c3da5cd2595ee75f209ba6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ea2586804e6200303ec0fa0aeb71727f0d6fe449f8ed71b4ab9e513fa63f2af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4b243e71884bdb87090ba14939af3644e47153ddf8269565e3265fe73c70a7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af5af5655c9eb361287b9e9a79263d4ca0dc72afc94d1d9e2e49aff56249526d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c794e7257145b14040e865404bf0a94a151acef1ff0353efc9e8fdd4242aa6cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c3861dd545b56200044a1553df819f251ad281b147605bbcd059f5e7d312029(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__116d210615cc3f3d98b26b66da8d6bf50c6739da91b272d9e3f78fa7505bf8fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aefe8e908a30f68c5e9054e0c1ff6fa3f203abee84b861e50b5a9b1bf169ae19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f84226da74bcda546736e7af450011c655ce1cd0945e43b1e1da89bd26e536a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85bc0e2a1a5cc915d80efc46eb979e04d6a790748fa5f9afd5bbbb20e7082e90(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff86112a2d2ec82b37d08241df56d0dbe53d9afcfd5f6c2570470b80abbc14e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76d3723fe586a344eec0eebea35b9192b938e6bd0b86507c5a425f97ca4530f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f409e175371641e27dd6490dcf8e525868eaf392be1ab7fd04e1dfc4febf7ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5a66f749e97f160247fd69ca91bb3fa97144e6e2893d3d498597cef086a0708(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__296e0320c0d070053ccb7bb217ac7a1acfec138ab5736eee321c174c2e835563(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e1dcce4dc5c914a9b08d861e48b0351e10792a621a66a1baf71294f38792cb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a8ce5eaa72ce43af33fb98bd0d22a41649d12d9db887759e8db75d75e2770da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23049b997d55f1337f789b415d699778a97f3385956ad0a824fa6a8b0320d3d5(
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
    api_id: typing.Optional[builtins.str] = None,
    api_key: typing.Optional[builtins.str] = None,
    authentication_credentials: typing.Optional[builtins.str] = None,
    auto_rotate: typing.Optional[builtins.str] = None,
    custom_payload: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    rotated_password: typing.Optional[builtins.str] = None,
    rotated_username: typing.Optional[builtins.str] = None,
    rotation_hour: typing.Optional[jsii.Number] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    rotator_custom_cmd: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_attribute: typing.Optional[builtins.str] = None,
    user_dn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
