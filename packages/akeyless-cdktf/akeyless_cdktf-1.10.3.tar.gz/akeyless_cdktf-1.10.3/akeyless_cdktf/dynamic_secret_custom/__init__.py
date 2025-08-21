'''
# `akeyless_dynamic_secret_custom`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_custom`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom).
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


class DynamicSecretCustom(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretCustom.DynamicSecretCustom",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom akeyless_dynamic_secret_custom}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        create_sync_url: builtins.str,
        name: builtins.str,
        revoke_sync_url: builtins.str,
        admin_rotation_interval_days: typing.Optional[jsii.Number] = None,
        enable_admin_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        payload: typing.Optional[builtins.str] = None,
        rotate_sync_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeout_sec: typing.Optional[jsii.Number] = None,
        user_ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom akeyless_dynamic_secret_custom} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param create_sync_url: URL of an endpoint that implements /sync/create method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#create_sync_url DynamicSecretCustom#create_sync_url}
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#name DynamicSecretCustom#name}
        :param revoke_sync_url: URL of an endpoint that implements /sync/revoke method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#revoke_sync_url DynamicSecretCustom#revoke_sync_url}
        :param admin_rotation_interval_days: Rotation period in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#admin_rotation_interval_days DynamicSecretCustom#admin_rotation_interval_days}
        :param enable_admin_rotation: Enable automatic admin credentials rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#enable_admin_rotation DynamicSecretCustom#enable_admin_rotation}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#encryption_key_name DynamicSecretCustom#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#id DynamicSecretCustom#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param payload: Secret payload to be sent with each create/revoke webhook request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#payload DynamicSecretCustom#payload}
        :param rotate_sync_url: URL of an endpoint that implements /sync/rotate method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#rotate_sync_url DynamicSecretCustom#rotate_sync_url}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#tags DynamicSecretCustom#tags}
        :param timeout_sec: Maximum allowed time in seconds for the webhook to return the results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#timeout_sec DynamicSecretCustom#timeout_sec}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#user_ttl DynamicSecretCustom#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfb5afe8e5beb94b881c017ae565ef14cfdf8457e5550a0a1def6479e239a732)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretCustomConfig(
            create_sync_url=create_sync_url,
            name=name,
            revoke_sync_url=revoke_sync_url,
            admin_rotation_interval_days=admin_rotation_interval_days,
            enable_admin_rotation=enable_admin_rotation,
            encryption_key_name=encryption_key_name,
            id=id,
            payload=payload,
            rotate_sync_url=rotate_sync_url,
            tags=tags,
            timeout_sec=timeout_sec,
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
        '''Generates CDKTF code for importing a DynamicSecretCustom resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretCustom to import.
        :param import_from_id: The id of the existing DynamicSecretCustom that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretCustom to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94d122bed89ad440d2b41f6dc1d63742d13ebfc4484cf6e752a4302d9a40b452)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAdminRotationIntervalDays")
    def reset_admin_rotation_interval_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminRotationIntervalDays", []))

    @jsii.member(jsii_name="resetEnableAdminRotation")
    def reset_enable_admin_rotation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAdminRotation", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPayload")
    def reset_payload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayload", []))

    @jsii.member(jsii_name="resetRotateSyncUrl")
    def reset_rotate_sync_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotateSyncUrl", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTimeoutSec")
    def reset_timeout_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutSec", []))

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
    @jsii.member(jsii_name="adminRotationIntervalDaysInput")
    def admin_rotation_interval_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "adminRotationIntervalDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="createSyncUrlInput")
    def create_sync_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createSyncUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="enableAdminRotationInput")
    def enable_admin_rotation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableAdminRotationInput"))

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
    @jsii.member(jsii_name="payloadInput")
    def payload_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "payloadInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeSyncUrlInput")
    def revoke_sync_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "revokeSyncUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="rotateSyncUrlInput")
    def rotate_sync_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotateSyncUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutSecInput")
    def timeout_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutSecInput"))

    @builtins.property
    @jsii.member(jsii_name="userTtlInput")
    def user_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="adminRotationIntervalDays")
    def admin_rotation_interval_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "adminRotationIntervalDays"))

    @admin_rotation_interval_days.setter
    def admin_rotation_interval_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ef99ec296d124dd94379742c8f9972c50a773938d72ff7623c40a04f409f4ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminRotationIntervalDays", value)

    @builtins.property
    @jsii.member(jsii_name="createSyncUrl")
    def create_sync_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createSyncUrl"))

    @create_sync_url.setter
    def create_sync_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c07948bf9293ec77175cd1d8ddafc294ab377668a6cfeaf0c21d644486929242)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createSyncUrl", value)

    @builtins.property
    @jsii.member(jsii_name="enableAdminRotation")
    def enable_admin_rotation(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableAdminRotation"))

    @enable_admin_rotation.setter
    def enable_admin_rotation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d0d9601cfdb9ac298575f49fc90fb88f851133dc889cefe8a4067112e9704b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableAdminRotation", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e792ba3eedf76a5df6770704b9ae27a4a1a0784ab249c99c660d29ff6a58dbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28c24843f6dfde96223e353eb487a504b089a3a01890acb0ad4260c3fbb02b9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__797f81c9b7383ccbba8ea3994a17cf06f5d3b68967cab06f447e3c0e13ad331e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="payload")
    def payload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payload"))

    @payload.setter
    def payload(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13c4d50b781101fa8264319876e21b11fbe4f63eedafcdbbf88de3b61eb468ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payload", value)

    @builtins.property
    @jsii.member(jsii_name="revokeSyncUrl")
    def revoke_sync_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokeSyncUrl"))

    @revoke_sync_url.setter
    def revoke_sync_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1745344c20447f27abf0419e250829bac44be5531efb9cae82b41af6b83e7092)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokeSyncUrl", value)

    @builtins.property
    @jsii.member(jsii_name="rotateSyncUrl")
    def rotate_sync_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotateSyncUrl"))

    @rotate_sync_url.setter
    def rotate_sync_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59486d41097e82929a63a7da1ae52f7f2c83b259717a58cb687e065a094b8f42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotateSyncUrl", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a76008710198d7b864e982991266c1babf4ad8b3657bf89462fff2d18e96358c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="timeoutSec")
    def timeout_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSec"))

    @timeout_sec.setter
    def timeout_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f85fb8fb065e215fbf246667017f230ed7957b02bde7d5888731d034ed194b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutSec", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2036f81e2a46286fc0fd84a8500f2e284d166cd57afed7061b620b0f75a5e56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretCustom.DynamicSecretCustomConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "create_sync_url": "createSyncUrl",
        "name": "name",
        "revoke_sync_url": "revokeSyncUrl",
        "admin_rotation_interval_days": "adminRotationIntervalDays",
        "enable_admin_rotation": "enableAdminRotation",
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
        "payload": "payload",
        "rotate_sync_url": "rotateSyncUrl",
        "tags": "tags",
        "timeout_sec": "timeoutSec",
        "user_ttl": "userTtl",
    },
)
class DynamicSecretCustomConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        create_sync_url: builtins.str,
        name: builtins.str,
        revoke_sync_url: builtins.str,
        admin_rotation_interval_days: typing.Optional[jsii.Number] = None,
        enable_admin_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        payload: typing.Optional[builtins.str] = None,
        rotate_sync_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeout_sec: typing.Optional[jsii.Number] = None,
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
        :param create_sync_url: URL of an endpoint that implements /sync/create method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#create_sync_url DynamicSecretCustom#create_sync_url}
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#name DynamicSecretCustom#name}
        :param revoke_sync_url: URL of an endpoint that implements /sync/revoke method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#revoke_sync_url DynamicSecretCustom#revoke_sync_url}
        :param admin_rotation_interval_days: Rotation period in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#admin_rotation_interval_days DynamicSecretCustom#admin_rotation_interval_days}
        :param enable_admin_rotation: Enable automatic admin credentials rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#enable_admin_rotation DynamicSecretCustom#enable_admin_rotation}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#encryption_key_name DynamicSecretCustom#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#id DynamicSecretCustom#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param payload: Secret payload to be sent with each create/revoke webhook request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#payload DynamicSecretCustom#payload}
        :param rotate_sync_url: URL of an endpoint that implements /sync/rotate method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#rotate_sync_url DynamicSecretCustom#rotate_sync_url}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#tags DynamicSecretCustom#tags}
        :param timeout_sec: Maximum allowed time in seconds for the webhook to return the results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#timeout_sec DynamicSecretCustom#timeout_sec}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#user_ttl DynamicSecretCustom#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9999b16311fb9922f1c80e07f45c1514c433f057f1d60d5bc33f3d7dd860f914)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument create_sync_url", value=create_sync_url, expected_type=type_hints["create_sync_url"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument revoke_sync_url", value=revoke_sync_url, expected_type=type_hints["revoke_sync_url"])
            check_type(argname="argument admin_rotation_interval_days", value=admin_rotation_interval_days, expected_type=type_hints["admin_rotation_interval_days"])
            check_type(argname="argument enable_admin_rotation", value=enable_admin_rotation, expected_type=type_hints["enable_admin_rotation"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument rotate_sync_url", value=rotate_sync_url, expected_type=type_hints["rotate_sync_url"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument timeout_sec", value=timeout_sec, expected_type=type_hints["timeout_sec"])
            check_type(argname="argument user_ttl", value=user_ttl, expected_type=type_hints["user_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "create_sync_url": create_sync_url,
            "name": name,
            "revoke_sync_url": revoke_sync_url,
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
        if admin_rotation_interval_days is not None:
            self._values["admin_rotation_interval_days"] = admin_rotation_interval_days
        if enable_admin_rotation is not None:
            self._values["enable_admin_rotation"] = enable_admin_rotation
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
        if payload is not None:
            self._values["payload"] = payload
        if rotate_sync_url is not None:
            self._values["rotate_sync_url"] = rotate_sync_url
        if tags is not None:
            self._values["tags"] = tags
        if timeout_sec is not None:
            self._values["timeout_sec"] = timeout_sec
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
    def create_sync_url(self) -> builtins.str:
        '''URL of an endpoint that implements /sync/create method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#create_sync_url DynamicSecretCustom#create_sync_url}
        '''
        result = self._values.get("create_sync_url")
        assert result is not None, "Required property 'create_sync_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Dynamic secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#name DynamicSecretCustom#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revoke_sync_url(self) -> builtins.str:
        '''URL of an endpoint that implements /sync/revoke method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#revoke_sync_url DynamicSecretCustom#revoke_sync_url}
        '''
        result = self._values.get("revoke_sync_url")
        assert result is not None, "Required property 'revoke_sync_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_rotation_interval_days(self) -> typing.Optional[jsii.Number]:
        '''Rotation period in days.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#admin_rotation_interval_days DynamicSecretCustom#admin_rotation_interval_days}
        '''
        result = self._values.get("admin_rotation_interval_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_admin_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable automatic admin credentials rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#enable_admin_rotation DynamicSecretCustom#enable_admin_rotation}
        '''
        result = self._values.get("enable_admin_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#encryption_key_name DynamicSecretCustom#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#id DynamicSecretCustom#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload(self) -> typing.Optional[builtins.str]:
        '''Secret payload to be sent with each create/revoke webhook request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#payload DynamicSecretCustom#payload}
        '''
        result = self._values.get("payload")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotate_sync_url(self) -> typing.Optional[builtins.str]:
        '''URL of an endpoint that implements /sync/rotate method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#rotate_sync_url DynamicSecretCustom#rotate_sync_url}
        '''
        result = self._values.get("rotate_sync_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#tags DynamicSecretCustom#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timeout_sec(self) -> typing.Optional[jsii.Number]:
        '''Maximum allowed time in seconds for the webhook to return the results.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#timeout_sec DynamicSecretCustom#timeout_sec}
        '''
        result = self._values.get("timeout_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_custom#user_ttl DynamicSecretCustom#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretCustomConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretCustom",
    "DynamicSecretCustomConfig",
]

publication.publish()

def _typecheckingstub__dfb5afe8e5beb94b881c017ae565ef14cfdf8457e5550a0a1def6479e239a732(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    create_sync_url: builtins.str,
    name: builtins.str,
    revoke_sync_url: builtins.str,
    admin_rotation_interval_days: typing.Optional[jsii.Number] = None,
    enable_admin_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    payload: typing.Optional[builtins.str] = None,
    rotate_sync_url: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeout_sec: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__94d122bed89ad440d2b41f6dc1d63742d13ebfc4484cf6e752a4302d9a40b452(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ef99ec296d124dd94379742c8f9972c50a773938d72ff7623c40a04f409f4ee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c07948bf9293ec77175cd1d8ddafc294ab377668a6cfeaf0c21d644486929242(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d0d9601cfdb9ac298575f49fc90fb88f851133dc889cefe8a4067112e9704b7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e792ba3eedf76a5df6770704b9ae27a4a1a0784ab249c99c660d29ff6a58dbb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28c24843f6dfde96223e353eb487a504b089a3a01890acb0ad4260c3fbb02b9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__797f81c9b7383ccbba8ea3994a17cf06f5d3b68967cab06f447e3c0e13ad331e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13c4d50b781101fa8264319876e21b11fbe4f63eedafcdbbf88de3b61eb468ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1745344c20447f27abf0419e250829bac44be5531efb9cae82b41af6b83e7092(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59486d41097e82929a63a7da1ae52f7f2c83b259717a58cb687e065a094b8f42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a76008710198d7b864e982991266c1babf4ad8b3657bf89462fff2d18e96358c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f85fb8fb065e215fbf246667017f230ed7957b02bde7d5888731d034ed194b9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2036f81e2a46286fc0fd84a8500f2e284d166cd57afed7061b620b0f75a5e56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9999b16311fb9922f1c80e07f45c1514c433f057f1d60d5bc33f3d7dd860f914(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    create_sync_url: builtins.str,
    name: builtins.str,
    revoke_sync_url: builtins.str,
    admin_rotation_interval_days: typing.Optional[jsii.Number] = None,
    enable_admin_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    payload: typing.Optional[builtins.str] = None,
    rotate_sync_url: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeout_sec: typing.Optional[jsii.Number] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
