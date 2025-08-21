'''
# `akeyless_target_rabbit`

Refer to the Terraform Registry for docs: [`akeyless_target_rabbit`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit).
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


class TargetRabbit(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.targetRabbit.TargetRabbit",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit akeyless_target_rabbit}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        rabbitmq_server_uri: builtins.str,
        rabbitmq_server_user: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        rabbitmq_server_password: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit akeyless_target_rabbit} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#name TargetRabbit#name}
        :param rabbitmq_server_uri: RabbitMQ server URI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_uri TargetRabbit#rabbitmq_server_uri}
        :param rabbitmq_server_user: RabbitMQ server user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_user TargetRabbit#rabbitmq_server_user}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#description TargetRabbit#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#id TargetRabbit#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#key TargetRabbit#key}
        :param rabbitmq_server_password: RabbitMQ server password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_password TargetRabbit#rabbitmq_server_password}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959f15b5fc751b9ef5cfd0c50700bfdf6ef0ab73d44117718f3431c18a4f040a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TargetRabbitConfig(
            name=name,
            rabbitmq_server_uri=rabbitmq_server_uri,
            rabbitmq_server_user=rabbitmq_server_user,
            description=description,
            id=id,
            key=key,
            rabbitmq_server_password=rabbitmq_server_password,
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
        '''Generates CDKTF code for importing a TargetRabbit resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TargetRabbit to import.
        :param import_from_id: The id of the existing TargetRabbit that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TargetRabbit to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff670067887eba8f0e052af1449114650d2bb61aeba1bab52f19540369657072)
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

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetRabbitmqServerPassword")
    def reset_rabbitmq_server_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRabbitmqServerPassword", []))

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
    @jsii.member(jsii_name="rabbitmqServerPasswordInput")
    def rabbitmq_server_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rabbitmqServerPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="rabbitmqServerUriInput")
    def rabbitmq_server_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rabbitmqServerUriInput"))

    @builtins.property
    @jsii.member(jsii_name="rabbitmqServerUserInput")
    def rabbitmq_server_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rabbitmqServerUserInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b13933d13dd8d0968db93911b63ffff73945426874da0c9565852bf5b76413a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5aa097b66eb51449de6cbd31c99b706100bdd0bdff2ea8b9be1ce2dacb21372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ded86288b1cfe74f1d5378e97c242f10ba34b08ad90f1c07cf2e439f788d6a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebcdf99beda647db8f3f9aff136db2354d68eb956439e3b59da2831c3e54bf94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="rabbitmqServerPassword")
    def rabbitmq_server_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rabbitmqServerPassword"))

    @rabbitmq_server_password.setter
    def rabbitmq_server_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f05beb5a3ab8e853d28dff601e5512b8d423fe41099a8a8639c8b558ccd05c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rabbitmqServerPassword", value)

    @builtins.property
    @jsii.member(jsii_name="rabbitmqServerUri")
    def rabbitmq_server_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rabbitmqServerUri"))

    @rabbitmq_server_uri.setter
    def rabbitmq_server_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65fb041d15b3fe18ec94c39cc01203d22262433a438031bc3b4e401f0fd9c7e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rabbitmqServerUri", value)

    @builtins.property
    @jsii.member(jsii_name="rabbitmqServerUser")
    def rabbitmq_server_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rabbitmqServerUser"))

    @rabbitmq_server_user.setter
    def rabbitmq_server_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2136bf4aeee141a951a3f58ba5c55e76516f4fed544c394ab7f84873321cb8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rabbitmqServerUser", value)


@jsii.data_type(
    jsii_type="akeyless.targetRabbit.TargetRabbitConfig",
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
        "rabbitmq_server_uri": "rabbitmqServerUri",
        "rabbitmq_server_user": "rabbitmqServerUser",
        "description": "description",
        "id": "id",
        "key": "key",
        "rabbitmq_server_password": "rabbitmqServerPassword",
    },
)
class TargetRabbitConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        rabbitmq_server_uri: builtins.str,
        rabbitmq_server_user: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        rabbitmq_server_password: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#name TargetRabbit#name}
        :param rabbitmq_server_uri: RabbitMQ server URI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_uri TargetRabbit#rabbitmq_server_uri}
        :param rabbitmq_server_user: RabbitMQ server user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_user TargetRabbit#rabbitmq_server_user}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#description TargetRabbit#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#id TargetRabbit#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#key TargetRabbit#key}
        :param rabbitmq_server_password: RabbitMQ server password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_password TargetRabbit#rabbitmq_server_password}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4a66a9425be05d6020d08d43e94d08412bc24a3cb4f3bedd7931647711e0ff)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rabbitmq_server_uri", value=rabbitmq_server_uri, expected_type=type_hints["rabbitmq_server_uri"])
            check_type(argname="argument rabbitmq_server_user", value=rabbitmq_server_user, expected_type=type_hints["rabbitmq_server_user"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument rabbitmq_server_password", value=rabbitmq_server_password, expected_type=type_hints["rabbitmq_server_password"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "rabbitmq_server_uri": rabbitmq_server_uri,
            "rabbitmq_server_user": rabbitmq_server_user,
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
        if key is not None:
            self._values["key"] = key
        if rabbitmq_server_password is not None:
            self._values["rabbitmq_server_password"] = rabbitmq_server_password

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
        '''Target name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#name TargetRabbit#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rabbitmq_server_uri(self) -> builtins.str:
        '''RabbitMQ server URI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_uri TargetRabbit#rabbitmq_server_uri}
        '''
        result = self._values.get("rabbitmq_server_uri")
        assert result is not None, "Required property 'rabbitmq_server_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rabbitmq_server_user(self) -> builtins.str:
        '''RabbitMQ server user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_user TargetRabbit#rabbitmq_server_user}
        '''
        result = self._values.get("rabbitmq_server_user")
        assert result is not None, "Required property 'rabbitmq_server_user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#description TargetRabbit#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#id TargetRabbit#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#key TargetRabbit#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rabbitmq_server_password(self) -> typing.Optional[builtins.str]:
        '''RabbitMQ server password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_rabbit#rabbitmq_server_password TargetRabbit#rabbitmq_server_password}
        '''
        result = self._values.get("rabbitmq_server_password")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetRabbitConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TargetRabbit",
    "TargetRabbitConfig",
]

publication.publish()

def _typecheckingstub__959f15b5fc751b9ef5cfd0c50700bfdf6ef0ab73d44117718f3431c18a4f040a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    rabbitmq_server_uri: builtins.str,
    rabbitmq_server_user: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    rabbitmq_server_password: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__ff670067887eba8f0e052af1449114650d2bb61aeba1bab52f19540369657072(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b13933d13dd8d0968db93911b63ffff73945426874da0c9565852bf5b76413a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5aa097b66eb51449de6cbd31c99b706100bdd0bdff2ea8b9be1ce2dacb21372(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ded86288b1cfe74f1d5378e97c242f10ba34b08ad90f1c07cf2e439f788d6a23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcdf99beda647db8f3f9aff136db2354d68eb956439e3b59da2831c3e54bf94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f05beb5a3ab8e853d28dff601e5512b8d423fe41099a8a8639c8b558ccd05c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65fb041d15b3fe18ec94c39cc01203d22262433a438031bc3b4e401f0fd9c7e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2136bf4aeee141a951a3f58ba5c55e76516f4fed544c394ab7f84873321cb8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4a66a9425be05d6020d08d43e94d08412bc24a3cb4f3bedd7931647711e0ff(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    rabbitmq_server_uri: builtins.str,
    rabbitmq_server_user: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    rabbitmq_server_password: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
