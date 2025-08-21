'''
# `akeyless_producer_custom`

Refer to the Terraform Registry for docs: [`akeyless_producer_custom`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom).
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


class ProducerCustom(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerCustom.ProducerCustom",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom akeyless_producer_custom}.'''

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
        id: typing.Optional[builtins.str] = None,
        payload: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom akeyless_producer_custom} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param create_sync_url: URL of an endpoint that implements /sync/create method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#create_sync_url ProducerCustom#create_sync_url}
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#name ProducerCustom#name}
        :param revoke_sync_url: URL of an endpoint that implements /sync/revoke method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#revoke_sync_url ProducerCustom#revoke_sync_url}
        :param admin_rotation_interval_days: Rotation period in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#admin_rotation_interval_days ProducerCustom#admin_rotation_interval_days}
        :param enable_admin_rotation: Enable automatic admin credentials rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#enable_admin_rotation ProducerCustom#enable_admin_rotation}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#id ProducerCustom#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param payload: Secret payload to be sent with each create/revoke webhook request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#payload ProducerCustom#payload}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#producer_encryption_key_name ProducerCustom#producer_encryption_key_name}
        :param rotate_sync_url: URL of an endpoint that implements /sync/rotate method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#rotate_sync_url ProducerCustom#rotate_sync_url}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#tags ProducerCustom#tags}
        :param timeout_sec: Maximum allowed time in seconds for the webhook to return the results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#timeout_sec ProducerCustom#timeout_sec}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#user_ttl ProducerCustom#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a2e51135cac4693d2aa108498bc5ba2ce7e1d8ad9ad503ff8ce31b88ae39d91)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerCustomConfig(
            create_sync_url=create_sync_url,
            name=name,
            revoke_sync_url=revoke_sync_url,
            admin_rotation_interval_days=admin_rotation_interval_days,
            enable_admin_rotation=enable_admin_rotation,
            id=id,
            payload=payload,
            producer_encryption_key_name=producer_encryption_key_name,
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
        '''Generates CDKTF code for importing a ProducerCustom resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerCustom to import.
        :param import_from_id: The id of the existing ProducerCustom that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerCustom to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6212c3a794060cbbebd1b69b29336f6e9fe599b98ab6a8d7d5b882f7337b4c2)
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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPayload")
    def reset_payload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPayload", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

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
    @jsii.member(jsii_name="producerEncryptionKeyNameInput")
    def producer_encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "producerEncryptionKeyNameInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__a26493643b71224fdb1f05295fba275fe7a1bdc781b95b9ca5bf56b171522f00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminRotationIntervalDays", value)

    @builtins.property
    @jsii.member(jsii_name="createSyncUrl")
    def create_sync_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createSyncUrl"))

    @create_sync_url.setter
    def create_sync_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37d1d66ad5de104f88d6694285e966fb22f9646dda8d36ce8bc41c42a87c8138)
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
            type_hints = typing.get_type_hints(_typecheckingstub__047e23e5fc0a7ed878c044a392312bb23ca00b33ff3c9112cddfe10c9e8c62dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableAdminRotation", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d000639749154fabd13cbaa7b3e34f11f69aa1c8aa4062d432914fafc65c97b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c40f3f4e96b32c8053e2dd699564f4d61c3c820a31aa502fef7c548297ef23d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="payload")
    def payload(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "payload"))

    @payload.setter
    def payload(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf43bafe3335b93b64b453bc2397d61d79f8f206283d9dde2de9a6939f4c0cc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "payload", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54cf31d0ceb801a279bf504323cc0658a8049e7d4943c4c6f208700a00d4689b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="revokeSyncUrl")
    def revoke_sync_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "revokeSyncUrl"))

    @revoke_sync_url.setter
    def revoke_sync_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__715a0aed2232300cf3a483c917939e94dfc9a625701025ede62d20309b23c607)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokeSyncUrl", value)

    @builtins.property
    @jsii.member(jsii_name="rotateSyncUrl")
    def rotate_sync_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotateSyncUrl"))

    @rotate_sync_url.setter
    def rotate_sync_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c101ca474fc35e99833eb2ecec2d0c10da33e1a1e4ec0c637a50ed787c49107)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotateSyncUrl", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b9ae66100dd8b8c8972f3a7ba44799ebec814edf78958fcb3ab6d6486a27f6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="timeoutSec")
    def timeout_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSec"))

    @timeout_sec.setter
    def timeout_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__000b10154c3d30578c865b667271e60be07495a9aa4f5b13210d6dee497fcfca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeoutSec", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56082cc24c7263c787e3c4ecff1e0d1764d7dcf9d3813293b08a5c12081fe0be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerCustom.ProducerCustomConfig",
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
        "id": "id",
        "payload": "payload",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "rotate_sync_url": "rotateSyncUrl",
        "tags": "tags",
        "timeout_sec": "timeoutSec",
        "user_ttl": "userTtl",
    },
)
class ProducerCustomConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        payload: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
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
        :param create_sync_url: URL of an endpoint that implements /sync/create method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#create_sync_url ProducerCustom#create_sync_url}
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#name ProducerCustom#name}
        :param revoke_sync_url: URL of an endpoint that implements /sync/revoke method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#revoke_sync_url ProducerCustom#revoke_sync_url}
        :param admin_rotation_interval_days: Rotation period in days. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#admin_rotation_interval_days ProducerCustom#admin_rotation_interval_days}
        :param enable_admin_rotation: Enable automatic admin credentials rotation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#enable_admin_rotation ProducerCustom#enable_admin_rotation}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#id ProducerCustom#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param payload: Secret payload to be sent with each create/revoke webhook request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#payload ProducerCustom#payload}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#producer_encryption_key_name ProducerCustom#producer_encryption_key_name}
        :param rotate_sync_url: URL of an endpoint that implements /sync/rotate method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#rotate_sync_url ProducerCustom#rotate_sync_url}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#tags ProducerCustom#tags}
        :param timeout_sec: Maximum allowed time in seconds for the webhook to return the results. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#timeout_sec ProducerCustom#timeout_sec}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#user_ttl ProducerCustom#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dc0cf65afee8095a20528c044317c4768566d10085085df7aed69e2f29b547f)
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
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument payload", value=payload, expected_type=type_hints["payload"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
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
        if id is not None:
            self._values["id"] = id
        if payload is not None:
            self._values["payload"] = payload
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#create_sync_url ProducerCustom#create_sync_url}
        '''
        result = self._values.get("create_sync_url")
        assert result is not None, "Required property 'create_sync_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Producer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#name ProducerCustom#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revoke_sync_url(self) -> builtins.str:
        '''URL of an endpoint that implements /sync/revoke method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#revoke_sync_url ProducerCustom#revoke_sync_url}
        '''
        result = self._values.get("revoke_sync_url")
        assert result is not None, "Required property 'revoke_sync_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_rotation_interval_days(self) -> typing.Optional[jsii.Number]:
        '''Rotation period in days.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#admin_rotation_interval_days ProducerCustom#admin_rotation_interval_days}
        '''
        result = self._values.get("admin_rotation_interval_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_admin_rotation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable automatic admin credentials rotation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#enable_admin_rotation ProducerCustom#enable_admin_rotation}
        '''
        result = self._values.get("enable_admin_rotation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#id ProducerCustom#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def payload(self) -> typing.Optional[builtins.str]:
        '''Secret payload to be sent with each create/revoke webhook request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#payload ProducerCustom#payload}
        '''
        result = self._values.get("payload")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#producer_encryption_key_name ProducerCustom#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotate_sync_url(self) -> typing.Optional[builtins.str]:
        '''URL of an endpoint that implements /sync/rotate method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#rotate_sync_url ProducerCustom#rotate_sync_url}
        '''
        result = self._values.get("rotate_sync_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#tags ProducerCustom#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timeout_sec(self) -> typing.Optional[jsii.Number]:
        '''Maximum allowed time in seconds for the webhook to return the results.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#timeout_sec ProducerCustom#timeout_sec}
        '''
        result = self._values.get("timeout_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_custom#user_ttl ProducerCustom#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerCustomConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerCustom",
    "ProducerCustomConfig",
]

publication.publish()

def _typecheckingstub__3a2e51135cac4693d2aa108498bc5ba2ce7e1d8ad9ad503ff8ce31b88ae39d91(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    create_sync_url: builtins.str,
    name: builtins.str,
    revoke_sync_url: builtins.str,
    admin_rotation_interval_days: typing.Optional[jsii.Number] = None,
    enable_admin_rotation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    payload: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__f6212c3a794060cbbebd1b69b29336f6e9fe599b98ab6a8d7d5b882f7337b4c2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a26493643b71224fdb1f05295fba275fe7a1bdc781b95b9ca5bf56b171522f00(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37d1d66ad5de104f88d6694285e966fb22f9646dda8d36ce8bc41c42a87c8138(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__047e23e5fc0a7ed878c044a392312bb23ca00b33ff3c9112cddfe10c9e8c62dc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d000639749154fabd13cbaa7b3e34f11f69aa1c8aa4062d432914fafc65c97b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c40f3f4e96b32c8053e2dd699564f4d61c3c820a31aa502fef7c548297ef23d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf43bafe3335b93b64b453bc2397d61d79f8f206283d9dde2de9a6939f4c0cc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54cf31d0ceb801a279bf504323cc0658a8049e7d4943c4c6f208700a00d4689b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__715a0aed2232300cf3a483c917939e94dfc9a625701025ede62d20309b23c607(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c101ca474fc35e99833eb2ecec2d0c10da33e1a1e4ec0c637a50ed787c49107(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b9ae66100dd8b8c8972f3a7ba44799ebec814edf78958fcb3ab6d6486a27f6b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__000b10154c3d30578c865b667271e60be07495a9aa4f5b13210d6dee497fcfca(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56082cc24c7263c787e3c4ecff1e0d1764d7dcf9d3813293b08a5c12081fe0be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dc0cf65afee8095a20528c044317c4768566d10085085df7aed69e2f29b547f(
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
    id: typing.Optional[builtins.str] = None,
    payload: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    rotate_sync_url: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    timeout_sec: typing.Optional[jsii.Number] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
