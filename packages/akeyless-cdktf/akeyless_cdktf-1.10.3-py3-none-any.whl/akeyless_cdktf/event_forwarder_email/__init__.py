'''
# `akeyless_event_forwarder_email`

Refer to the Terraform Registry for docs: [`akeyless_event_forwarder_email`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email).
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


class EventForwarderEmail(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.eventForwarderEmail.EventForwarderEmail",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email akeyless_event_forwarder_email}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        email_to: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        include_error: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
        override_url: typing.Optional[builtins.str] = None,
        runner_type: typing.Optional[builtins.str] = None,
        targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email akeyless_event_forwarder_email} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#name EventForwarderEmail#name}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#auth_methods_event_source_locations EventForwarderEmail#auth_methods_event_source_locations}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#description EventForwarderEmail#description}
        :param email_to: A comma seperated list of email addresses to send event to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#email_to EventForwarderEmail#email_to}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#event_types EventForwarderEmail#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#every EventForwarderEmail#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#gateways_event_source_locations EventForwarderEmail#gateways_event_source_locations}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#id EventForwarderEmail#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param include_error: Set this option to include event errors details [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#include_error EventForwarderEmail#include_error}
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#items_event_source_locations EventForwarderEmail#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#key EventForwarderEmail#key}
        :param override_url: Override Akeyless default URL with your Gateway url (port 18888). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#override_url EventForwarderEmail#override_url}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#runner_type EventForwarderEmail#runner_type}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#targets_event_source_locations EventForwarderEmail#targets_event_source_locations}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b369eaceed647db2b9386c17f7de628691566c1ef630d3e9864b710fd56d301)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = EventForwarderEmailConfig(
            name=name,
            auth_methods_event_source_locations=auth_methods_event_source_locations,
            description=description,
            email_to=email_to,
            event_types=event_types,
            every=every,
            gateways_event_source_locations=gateways_event_source_locations,
            id=id,
            include_error=include_error,
            items_event_source_locations=items_event_source_locations,
            key=key,
            override_url=override_url,
            runner_type=runner_type,
            targets_event_source_locations=targets_event_source_locations,
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
        '''Generates CDKTF code for importing a EventForwarderEmail resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EventForwarderEmail to import.
        :param import_from_id: The id of the existing EventForwarderEmail that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EventForwarderEmail to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcc2e92f74d319b1b2117bc06358c0c613ac6a0aec46ccb1defeac336acf5d46)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAuthMethodsEventSourceLocations")
    def reset_auth_methods_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethodsEventSourceLocations", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEmailTo")
    def reset_email_to(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailTo", []))

    @jsii.member(jsii_name="resetEventTypes")
    def reset_event_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventTypes", []))

    @jsii.member(jsii_name="resetEvery")
    def reset_every(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEvery", []))

    @jsii.member(jsii_name="resetGatewaysEventSourceLocations")
    def reset_gateways_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewaysEventSourceLocations", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIncludeError")
    def reset_include_error(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeError", []))

    @jsii.member(jsii_name="resetItemsEventSourceLocations")
    def reset_items_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItemsEventSourceLocations", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetOverrideUrl")
    def reset_override_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideUrl", []))

    @jsii.member(jsii_name="resetRunnerType")
    def reset_runner_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunnerType", []))

    @jsii.member(jsii_name="resetTargetsEventSourceLocations")
    def reset_targets_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetsEventSourceLocations", []))

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
    @jsii.member(jsii_name="authMethodsEventSourceLocationsInput")
    def auth_methods_event_source_locations_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authMethodsEventSourceLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="emailToInput")
    def email_to_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailToInput"))

    @builtins.property
    @jsii.member(jsii_name="eventTypesInput")
    def event_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eventTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="everyInput")
    def every_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "everyInput"))

    @builtins.property
    @jsii.member(jsii_name="gatewaysEventSourceLocationsInput")
    def gateways_event_source_locations_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "gatewaysEventSourceLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="includeErrorInput")
    def include_error_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "includeErrorInput"))

    @builtins.property
    @jsii.member(jsii_name="itemsEventSourceLocationsInput")
    def items_event_source_locations_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsEventSourceLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="overrideUrlInput")
    def override_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overrideUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="runnerTypeInput")
    def runner_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runnerTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="targetsEventSourceLocationsInput")
    def targets_event_source_locations_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetsEventSourceLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="authMethodsEventSourceLocations")
    def auth_methods_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authMethodsEventSourceLocations"))

    @auth_methods_event_source_locations.setter
    def auth_methods_event_source_locations(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7d4ba6ffebf04f6aa5212176a3b9671e7ec987fb54448a325312a89250a8640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethodsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2a3196071bf1e0de37ed2c702f43f44828492cd383d40b5ac22aa6cfb350e57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="emailTo")
    def email_to(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailTo"))

    @email_to.setter
    def email_to(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__258566c9de63fff5f1d67ee5f2c7530b2dac4215b75579da0dd9b555121eff79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailTo", value)

    @builtins.property
    @jsii.member(jsii_name="eventTypes")
    def event_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventTypes"))

    @event_types.setter
    def event_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75de70d46c04794e3b97553d2f80742a1f7bfac4860726edd65eb46f368193cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventTypes", value)

    @builtins.property
    @jsii.member(jsii_name="every")
    def every(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "every"))

    @every.setter
    def every(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a33d2c3eef0ca64cd50d1e1f14077e49a2b95e8779fba7f86bfa168440612a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "every", value)

    @builtins.property
    @jsii.member(jsii_name="gatewaysEventSourceLocations")
    def gateways_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gatewaysEventSourceLocations"))

    @gateways_event_source_locations.setter
    def gateways_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__491184a46468ec9cd6958eaa43be0ca173a7497b42ae54fb6fc89d1f4e22e134)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewaysEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e3332810e862dd76c647603562b76097fc416996b114127108270f191842796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="includeError")
    def include_error(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "includeError"))

    @include_error.setter
    def include_error(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d327f83c61359fc29f9461017848481a872f24e43d6f58ed1600a0e983d0b24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeError", value)

    @builtins.property
    @jsii.member(jsii_name="itemsEventSourceLocations")
    def items_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "itemsEventSourceLocations"))

    @items_event_source_locations.setter
    def items_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac6384ad339a011043b27bf799ab78befb2ac387b438e24e38a480184cfafded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eb43cd31b70402ca0f8b46750e42f8f495aed93b27143ec87affda289712b48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb8c6916cd9fca853077f1ee21e33f0dd5d0c80bdc6c0921f7711a52e91b0d7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="overrideUrl")
    def override_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideUrl"))

    @override_url.setter
    def override_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06bd540fb7948e485c3410904627f8f4bf1f337671406fe3af49a0861376eef4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overrideUrl", value)

    @builtins.property
    @jsii.member(jsii_name="runnerType")
    def runner_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runnerType"))

    @runner_type.setter
    def runner_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6a4258819fed9bba724e9761a771d105dd01430f061060539502b207856dad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerType", value)

    @builtins.property
    @jsii.member(jsii_name="targetsEventSourceLocations")
    def targets_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetsEventSourceLocations"))

    @targets_event_source_locations.setter
    def targets_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80b615f14cec43cff6888a311911768837db3b126df024f2aa87b0a5e618691b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetsEventSourceLocations", value)


@jsii.data_type(
    jsii_type="akeyless.eventForwarderEmail.EventForwarderEmailConfig",
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
        "auth_methods_event_source_locations": "authMethodsEventSourceLocations",
        "description": "description",
        "email_to": "emailTo",
        "event_types": "eventTypes",
        "every": "every",
        "gateways_event_source_locations": "gatewaysEventSourceLocations",
        "id": "id",
        "include_error": "includeError",
        "items_event_source_locations": "itemsEventSourceLocations",
        "key": "key",
        "override_url": "overrideUrl",
        "runner_type": "runnerType",
        "targets_event_source_locations": "targetsEventSourceLocations",
    },
)
class EventForwarderEmailConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        email_to: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        include_error: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
        override_url: typing.Optional[builtins.str] = None,
        runner_type: typing.Optional[builtins.str] = None,
        targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#name EventForwarderEmail#name}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#auth_methods_event_source_locations EventForwarderEmail#auth_methods_event_source_locations}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#description EventForwarderEmail#description}
        :param email_to: A comma seperated list of email addresses to send event to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#email_to EventForwarderEmail#email_to}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#event_types EventForwarderEmail#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#every EventForwarderEmail#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#gateways_event_source_locations EventForwarderEmail#gateways_event_source_locations}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#id EventForwarderEmail#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param include_error: Set this option to include event errors details [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#include_error EventForwarderEmail#include_error}
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#items_event_source_locations EventForwarderEmail#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#key EventForwarderEmail#key}
        :param override_url: Override Akeyless default URL with your Gateway url (port 18888). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#override_url EventForwarderEmail#override_url}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#runner_type EventForwarderEmail#runner_type}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#targets_event_source_locations EventForwarderEmail#targets_event_source_locations}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b376a6bc6d8f2267ec3c40a4078672a1cf807956f762e2f03742a5b678f73878)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auth_methods_event_source_locations", value=auth_methods_event_source_locations, expected_type=type_hints["auth_methods_event_source_locations"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument email_to", value=email_to, expected_type=type_hints["email_to"])
            check_type(argname="argument event_types", value=event_types, expected_type=type_hints["event_types"])
            check_type(argname="argument every", value=every, expected_type=type_hints["every"])
            check_type(argname="argument gateways_event_source_locations", value=gateways_event_source_locations, expected_type=type_hints["gateways_event_source_locations"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument include_error", value=include_error, expected_type=type_hints["include_error"])
            check_type(argname="argument items_event_source_locations", value=items_event_source_locations, expected_type=type_hints["items_event_source_locations"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument override_url", value=override_url, expected_type=type_hints["override_url"])
            check_type(argname="argument runner_type", value=runner_type, expected_type=type_hints["runner_type"])
            check_type(argname="argument targets_event_source_locations", value=targets_event_source_locations, expected_type=type_hints["targets_event_source_locations"])
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
        if auth_methods_event_source_locations is not None:
            self._values["auth_methods_event_source_locations"] = auth_methods_event_source_locations
        if description is not None:
            self._values["description"] = description
        if email_to is not None:
            self._values["email_to"] = email_to
        if event_types is not None:
            self._values["event_types"] = event_types
        if every is not None:
            self._values["every"] = every
        if gateways_event_source_locations is not None:
            self._values["gateways_event_source_locations"] = gateways_event_source_locations
        if id is not None:
            self._values["id"] = id
        if include_error is not None:
            self._values["include_error"] = include_error
        if items_event_source_locations is not None:
            self._values["items_event_source_locations"] = items_event_source_locations
        if key is not None:
            self._values["key"] = key
        if override_url is not None:
            self._values["override_url"] = override_url
        if runner_type is not None:
            self._values["runner_type"] = runner_type
        if targets_event_source_locations is not None:
            self._values["targets_event_source_locations"] = targets_event_source_locations

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
        '''Event Forwarder name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#name EventForwarderEmail#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_methods_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Auth Methods event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#auth_methods_event_source_locations EventForwarderEmail#auth_methods_event_source_locations}
        '''
        result = self._values.get("auth_methods_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#description EventForwarderEmail#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_to(self) -> typing.Optional[builtins.str]:
        '''A comma seperated list of email addresses to send event to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#email_to EventForwarderEmail#email_to}
        '''
        result = self._values.get("email_to")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated list of types of events to notify about.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#event_types EventForwarderEmail#event_types}
        '''
        result = self._values.get("event_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def every(self) -> typing.Optional[builtins.str]:
        '''Rate of periodic runner repetition in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#every EventForwarderEmail#every}
        '''
        result = self._values.get("every")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateways_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#gateways_event_source_locations EventForwarderEmail#gateways_event_source_locations}
        '''
        result = self._values.get("gateways_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#id EventForwarderEmail#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_error(self) -> typing.Optional[builtins.str]:
        '''Set this option to include event errors details [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#include_error EventForwarderEmail#include_error}
        '''
        result = self._values.get("include_error")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def items_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Items event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#items_event_source_locations EventForwarderEmail#items_event_source_locations}
        '''
        result = self._values.get("items_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#key EventForwarderEmail#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def override_url(self) -> typing.Optional[builtins.str]:
        '''Override Akeyless default URL with your Gateway url (port 18888).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#override_url EventForwarderEmail#override_url}
        '''
        result = self._values.get("override_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runner_type(self) -> typing.Optional[builtins.str]:
        '''Event Forwarder runner type [immediate/periodic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#runner_type EventForwarderEmail#runner_type}
        '''
        result = self._values.get("runner_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Targets event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_email#targets_event_source_locations EventForwarderEmail#targets_event_source_locations}
        '''
        result = self._values.get("targets_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventForwarderEmailConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EventForwarderEmail",
    "EventForwarderEmailConfig",
]

publication.publish()

def _typecheckingstub__5b369eaceed647db2b9386c17f7de628691566c1ef630d3e9864b710fd56d301(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    email_to: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    include_error: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    override_url: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__fcc2e92f74d319b1b2117bc06358c0c613ac6a0aec46ccb1defeac336acf5d46(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7d4ba6ffebf04f6aa5212176a3b9671e7ec987fb54448a325312a89250a8640(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2a3196071bf1e0de37ed2c702f43f44828492cd383d40b5ac22aa6cfb350e57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__258566c9de63fff5f1d67ee5f2c7530b2dac4215b75579da0dd9b555121eff79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75de70d46c04794e3b97553d2f80742a1f7bfac4860726edd65eb46f368193cb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a33d2c3eef0ca64cd50d1e1f14077e49a2b95e8779fba7f86bfa168440612a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__491184a46468ec9cd6958eaa43be0ca173a7497b42ae54fb6fc89d1f4e22e134(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e3332810e862dd76c647603562b76097fc416996b114127108270f191842796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d327f83c61359fc29f9461017848481a872f24e43d6f58ed1600a0e983d0b24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac6384ad339a011043b27bf799ab78befb2ac387b438e24e38a480184cfafded(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eb43cd31b70402ca0f8b46750e42f8f495aed93b27143ec87affda289712b48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb8c6916cd9fca853077f1ee21e33f0dd5d0c80bdc6c0921f7711a52e91b0d7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06bd540fb7948e485c3410904627f8f4bf1f337671406fe3af49a0861376eef4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a4258819fed9bba724e9761a771d105dd01430f061060539502b207856dad9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80b615f14cec43cff6888a311911768837db3b126df024f2aa87b0a5e618691b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b376a6bc6d8f2267ec3c40a4078672a1cf807956f762e2f03742a5b678f73878(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    email_to: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    include_error: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    override_url: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
