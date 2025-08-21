'''
# `akeyless_rotated_secret_gcp`

Refer to the Terraform Registry for docs: [`akeyless_rotated_secret_gcp`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp).
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


class RotatedSecretGcp(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.rotatedSecretGcp.RotatedSecretGcp",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp akeyless_rotated_secret_gcp}.'''

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
        gcp_key: typing.Optional[builtins.str] = None,
        gcp_service_account_email: typing.Optional[builtins.str] = None,
        gcp_service_account_key_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp akeyless_rotated_secret_gcp} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#name RotatedSecretGcp#name}
        :param rotator_type: The rotator type [target/service-account-rotator]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotator_type RotatedSecretGcp#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#target_name RotatedSecretGcp#target_name}
        :param authentication_credentials: The credentials to connect with [use-self-creds/use-target-creds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#authentication_credentials RotatedSecretGcp#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#auto_rotate RotatedSecretGcp#auto_rotate}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#description RotatedSecretGcp#description}
        :param gcp_key: Base64-encoded service account private key text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_key RotatedSecretGcp#gcp_key}
        :param gcp_service_account_email: The email of the gcp service account to rotate (relevant only when rotator-type=servcie-account-rotator). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_service_account_email RotatedSecretGcp#gcp_service_account_email}
        :param gcp_service_account_key_id: The key id of the gcp service account to rotate (relevant only when rotator-type=servcie-account-rotator). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_service_account_key_id RotatedSecretGcp#gcp_service_account_key_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#id RotatedSecretGcp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#key RotatedSecretGcp#key}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#password_length RotatedSecretGcp#password_length}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotation_hour RotatedSecretGcp#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotation_interval RotatedSecretGcp#rotation_interval}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#tags RotatedSecretGcp#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2098efd29d815aae1054c2aecb811e7b9073501f5b997d8441bd72808dd9623)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RotatedSecretGcpConfig(
            name=name,
            rotator_type=rotator_type,
            target_name=target_name,
            authentication_credentials=authentication_credentials,
            auto_rotate=auto_rotate,
            description=description,
            gcp_key=gcp_key,
            gcp_service_account_email=gcp_service_account_email,
            gcp_service_account_key_id=gcp_service_account_key_id,
            id=id,
            key=key,
            password_length=password_length,
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
        '''Generates CDKTF code for importing a RotatedSecretGcp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the RotatedSecretGcp to import.
        :param import_from_id: The id of the existing RotatedSecretGcp that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the RotatedSecretGcp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b484d19970e4663e0d3264159755904bd4c9ebb3f39622bd87bfdf8e9c40aa0d)
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

    @jsii.member(jsii_name="resetGcpKey")
    def reset_gcp_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpKey", []))

    @jsii.member(jsii_name="resetGcpServiceAccountEmail")
    def reset_gcp_service_account_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpServiceAccountEmail", []))

    @jsii.member(jsii_name="resetGcpServiceAccountKeyId")
    def reset_gcp_service_account_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpServiceAccountKeyId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

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
    @jsii.member(jsii_name="gcpKeyInput")
    def gcp_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountEmailInput")
    def gcp_service_account_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpServiceAccountEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountKeyIdInput")
    def gcp_service_account_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpServiceAccountKeyIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__38111138fa66dd3a532f6bc06205ce5d0186f11824a291acfdaaa72d6c00b637)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationCredentials", value)

    @builtins.property
    @jsii.member(jsii_name="autoRotate")
    def auto_rotate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRotate"))

    @auto_rotate.setter
    def auto_rotate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__061144d387776601c4c0e6997c5734b1f323239b4f1b650b2159bc6b22b3652c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotate", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d606858a022229a493c35fcfacc9d4e94e03aa13fe5e56ced8acabb975d72263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="gcpKey")
    def gcp_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpKey"))

    @gcp_key.setter
    def gcp_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee3dffb32013a4e645a84ed3cdb5e09dc4d726286d72467ab7d890a1b95c7c09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpKey", value)

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountEmail")
    def gcp_service_account_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpServiceAccountEmail"))

    @gcp_service_account_email.setter
    def gcp_service_account_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__841d0bde5ecf47897d7369334b1a833faddda2200f13c0f93c2946e66ee1afa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpServiceAccountEmail", value)

    @builtins.property
    @jsii.member(jsii_name="gcpServiceAccountKeyId")
    def gcp_service_account_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpServiceAccountKeyId"))

    @gcp_service_account_key_id.setter
    def gcp_service_account_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59e05a2c30afd8ebdccda52a6a02b4988a8e590b2f823b34e09682a370e0434b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpServiceAccountKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f19d97fd6bf9e2dbef179b497518f7721cb0c785059a50f508d17422ab3a3268)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e3586fd0884fbc44c64624820f8d222c7b1b0fef31b4b63a0a6ce25087d07c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52d85e9457cf0b7055923e0ec7fb134af0c12d36b20bd8a23cad3c635a7333f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3802c7af5d2e990fc66c3d2f6f034f06ef9ae05eb2ef3cf7f212e8bfcb2a42ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="rotationHour")
    def rotation_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rotationHour"))

    @rotation_hour.setter
    def rotation_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec8957ad04b5035d0cb7c18a935f34e7a0081ec396f7f54885de28c0e7749aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationHour", value)

    @builtins.property
    @jsii.member(jsii_name="rotationInterval")
    def rotation_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationInterval"))

    @rotation_interval.setter
    def rotation_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ed0a9f8d54c6a660856610f2220e920b34ab89ca33f0c509f9572d4f104417c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationInterval", value)

    @builtins.property
    @jsii.member(jsii_name="rotatorType")
    def rotator_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotatorType"))

    @rotator_type.setter
    def rotator_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f23f51235030e52e6961ef2d9836612a2ca13a617fbf5add18467691fb4445ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotatorType", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e71e1a853c04ecf9669fbbed7889d5d527a8fc1d717df01c4c81d8c72ee890fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2378c97c4e975c89baa107d5053ca63fc75b6b135b8f45db26f1d39b407fabda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)


@jsii.data_type(
    jsii_type="akeyless.rotatedSecretGcp.RotatedSecretGcpConfig",
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
        "gcp_key": "gcpKey",
        "gcp_service_account_email": "gcpServiceAccountEmail",
        "gcp_service_account_key_id": "gcpServiceAccountKeyId",
        "id": "id",
        "key": "key",
        "password_length": "passwordLength",
        "rotation_hour": "rotationHour",
        "rotation_interval": "rotationInterval",
        "tags": "tags",
    },
)
class RotatedSecretGcpConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        gcp_key: typing.Optional[builtins.str] = None,
        gcp_service_account_email: typing.Optional[builtins.str] = None,
        gcp_service_account_key_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
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
        :param name: Secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#name RotatedSecretGcp#name}
        :param rotator_type: The rotator type [target/service-account-rotator]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotator_type RotatedSecretGcp#rotator_type}
        :param target_name: The target name to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#target_name RotatedSecretGcp#target_name}
        :param authentication_credentials: The credentials to connect with [use-self-creds/use-target-creds]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#authentication_credentials RotatedSecretGcp#authentication_credentials}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#auto_rotate RotatedSecretGcp#auto_rotate}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#description RotatedSecretGcp#description}
        :param gcp_key: Base64-encoded service account private key text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_key RotatedSecretGcp#gcp_key}
        :param gcp_service_account_email: The email of the gcp service account to rotate (relevant only when rotator-type=servcie-account-rotator). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_service_account_email RotatedSecretGcp#gcp_service_account_email}
        :param gcp_service_account_key_id: The key id of the gcp service account to rotate (relevant only when rotator-type=servcie-account-rotator). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_service_account_key_id RotatedSecretGcp#gcp_service_account_key_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#id RotatedSecretGcp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#key RotatedSecretGcp#key}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#password_length RotatedSecretGcp#password_length}
        :param rotation_hour: The Hour of the rotation in UTC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotation_hour RotatedSecretGcp#rotation_hour}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotation_interval RotatedSecretGcp#rotation_interval}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#tags RotatedSecretGcp#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08f6cd4eff70b39d13ae86c4fc4eced08c428061e9e05db701c01f0e58e40a2a)
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
            check_type(argname="argument gcp_key", value=gcp_key, expected_type=type_hints["gcp_key"])
            check_type(argname="argument gcp_service_account_email", value=gcp_service_account_email, expected_type=type_hints["gcp_service_account_email"])
            check_type(argname="argument gcp_service_account_key_id", value=gcp_service_account_key_id, expected_type=type_hints["gcp_service_account_key_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
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
        if gcp_key is not None:
            self._values["gcp_key"] = gcp_key
        if gcp_service_account_email is not None:
            self._values["gcp_service_account_email"] = gcp_service_account_email
        if gcp_service_account_key_id is not None:
            self._values["gcp_service_account_key_id"] = gcp_service_account_key_id
        if id is not None:
            self._values["id"] = id
        if key is not None:
            self._values["key"] = key
        if password_length is not None:
            self._values["password_length"] = password_length
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#name RotatedSecretGcp#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rotator_type(self) -> builtins.str:
        '''The rotator type [target/service-account-rotator].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotator_type RotatedSecretGcp#rotator_type}
        '''
        result = self._values.get("rotator_type")
        assert result is not None, "Required property 'rotator_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_name(self) -> builtins.str:
        '''The target name to associate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#target_name RotatedSecretGcp#target_name}
        '''
        result = self._values.get("target_name")
        assert result is not None, "Required property 'target_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_credentials(self) -> typing.Optional[builtins.str]:
        '''The credentials to connect with [use-self-creds/use-target-creds].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#authentication_credentials RotatedSecretGcp#authentication_credentials}
        '''
        result = self._values.get("authentication_credentials")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_rotate(self) -> typing.Optional[builtins.str]:
        '''Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#auto_rotate RotatedSecretGcp#auto_rotate}
        '''
        result = self._values.get("auto_rotate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#description RotatedSecretGcp#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_key(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded service account private key text.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_key RotatedSecretGcp#gcp_key}
        '''
        result = self._values.get("gcp_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_service_account_email(self) -> typing.Optional[builtins.str]:
        '''The email of the gcp service account to rotate (relevant only when rotator-type=servcie-account-rotator).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_service_account_email RotatedSecretGcp#gcp_service_account_email}
        '''
        result = self._values.get("gcp_service_account_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_service_account_key_id(self) -> typing.Optional[builtins.str]:
        '''The key id of the gcp service account to rotate (relevant only when rotator-type=servcie-account-rotator).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#gcp_service_account_key_id RotatedSecretGcp#gcp_service_account_key_id}
        '''
        result = self._values.get("gcp_service_account_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#id RotatedSecretGcp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#key RotatedSecretGcp#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#password_length RotatedSecretGcp#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_hour(self) -> typing.Optional[jsii.Number]:
        '''The Hour of the rotation in UTC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotation_hour RotatedSecretGcp#rotation_hour}
        '''
        result = self._values.get("rotation_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rotation_interval(self) -> typing.Optional[builtins.str]:
        '''The number of days to wait between every automatic rotation (1-365),custom rotator interval will be set in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#rotation_interval RotatedSecretGcp#rotation_interval}
        '''
        result = self._values.get("rotation_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/rotated_secret_gcp#tags RotatedSecretGcp#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RotatedSecretGcpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "RotatedSecretGcp",
    "RotatedSecretGcpConfig",
]

publication.publish()

def _typecheckingstub__a2098efd29d815aae1054c2aecb811e7b9073501f5b997d8441bd72808dd9623(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    rotator_type: builtins.str,
    target_name: builtins.str,
    authentication_credentials: typing.Optional[builtins.str] = None,
    auto_rotate: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    gcp_key: typing.Optional[builtins.str] = None,
    gcp_service_account_email: typing.Optional[builtins.str] = None,
    gcp_service_account_key_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__b484d19970e4663e0d3264159755904bd4c9ebb3f39622bd87bfdf8e9c40aa0d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38111138fa66dd3a532f6bc06205ce5d0186f11824a291acfdaaa72d6c00b637(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__061144d387776601c4c0e6997c5734b1f323239b4f1b650b2159bc6b22b3652c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d606858a022229a493c35fcfacc9d4e94e03aa13fe5e56ced8acabb975d72263(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee3dffb32013a4e645a84ed3cdb5e09dc4d726286d72467ab7d890a1b95c7c09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__841d0bde5ecf47897d7369334b1a833faddda2200f13c0f93c2946e66ee1afa9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59e05a2c30afd8ebdccda52a6a02b4988a8e590b2f823b34e09682a370e0434b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f19d97fd6bf9e2dbef179b497518f7721cb0c785059a50f508d17422ab3a3268(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e3586fd0884fbc44c64624820f8d222c7b1b0fef31b4b63a0a6ce25087d07c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52d85e9457cf0b7055923e0ec7fb134af0c12d36b20bd8a23cad3c635a7333f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3802c7af5d2e990fc66c3d2f6f034f06ef9ae05eb2ef3cf7f212e8bfcb2a42ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec8957ad04b5035d0cb7c18a935f34e7a0081ec396f7f54885de28c0e7749aee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ed0a9f8d54c6a660856610f2220e920b34ab89ca33f0c509f9572d4f104417c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f23f51235030e52e6961ef2d9836612a2ca13a617fbf5add18467691fb4445ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71e1a853c04ecf9669fbbed7889d5d527a8fc1d717df01c4c81d8c72ee890fe(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2378c97c4e975c89baa107d5053ca63fc75b6b135b8f45db26f1d39b407fabda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08f6cd4eff70b39d13ae86c4fc4eced08c428061e9e05db701c01f0e58e40a2a(
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
    gcp_key: typing.Optional[builtins.str] = None,
    gcp_service_account_email: typing.Optional[builtins.str] = None,
    gcp_service_account_key_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    rotation_hour: typing.Optional[jsii.Number] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
