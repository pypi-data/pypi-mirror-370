'''
# `akeyless_event_forwarder_slack`

Refer to the Terraform Registry for docs: [`akeyless_event_forwarder_slack`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack).
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


class EventForwarderSlack(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.eventForwarderSlack.EventForwarderSlack",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack akeyless_event_forwarder_slack}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        url: builtins.str,
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack akeyless_event_forwarder_slack} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#name EventForwarderSlack#name}
        :param url: Slack Webhook URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#url EventForwarderSlack#url}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#auth_methods_event_source_locations EventForwarderSlack#auth_methods_event_source_locations}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#description EventForwarderSlack#description}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#event_types EventForwarderSlack#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#every EventForwarderSlack#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#gateways_event_source_locations EventForwarderSlack#gateways_event_source_locations}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#id EventForwarderSlack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#items_event_source_locations EventForwarderSlack#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#key EventForwarderSlack#key}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#runner_type EventForwarderSlack#runner_type}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#targets_event_source_locations EventForwarderSlack#targets_event_source_locations}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b7ca926862c5093d45de286b8273acf66adfaac2b92e14ff11659a878def32)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = EventForwarderSlackConfig(
            name=name,
            url=url,
            auth_methods_event_source_locations=auth_methods_event_source_locations,
            description=description,
            event_types=event_types,
            every=every,
            gateways_event_source_locations=gateways_event_source_locations,
            id=id,
            items_event_source_locations=items_event_source_locations,
            key=key,
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
        '''Generates CDKTF code for importing a EventForwarderSlack resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EventForwarderSlack to import.
        :param import_from_id: The id of the existing EventForwarderSlack that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EventForwarderSlack to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d31a39862e7aae8d703955a95848b6c140e815f595a9aa2022eab0e1585b1805)
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

    @jsii.member(jsii_name="resetItemsEventSourceLocations")
    def reset_items_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItemsEventSourceLocations", []))

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

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
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__59ecfd9abf6f13b47be2638b6f4003457fde3bc81e21ad57a8596299a22f2f60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethodsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96074a81aa25c86e526407e896b33ade154b2fe68d10859a0972bed110109f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="eventTypes")
    def event_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventTypes"))

    @event_types.setter
    def event_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__109ac2ebf50c56694f52f191b6cc7d4913c971cb95e924582772ea4b45acdfb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventTypes", value)

    @builtins.property
    @jsii.member(jsii_name="every")
    def every(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "every"))

    @every.setter
    def every(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7de5ff580d7eecd231155ab114bae337fac5e2dac2d68a666c5f7c684a68718a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "every", value)

    @builtins.property
    @jsii.member(jsii_name="gatewaysEventSourceLocations")
    def gateways_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gatewaysEventSourceLocations"))

    @gateways_event_source_locations.setter
    def gateways_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__955ebd72904b1b91ee77b6191cc21a939edc540f8a4fac1559511ff18d058bbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewaysEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__585fed0db8d13e1232aa702d97fb4ef63a2cf8ed8b98fa7acae188a92f488046)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="itemsEventSourceLocations")
    def items_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "itemsEventSourceLocations"))

    @items_event_source_locations.setter
    def items_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52f870f5e151b89f5881cfa5968c231fd6c45411eb55e6bbacfecbadcd70dbb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__784d902a8a4ecf6bdab5af52f768152588197fd6648d2dacabb33d2414506143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8d4b3b367afe896fd48bc11004f59195e76ebb167747780cbf669b230723c68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="runnerType")
    def runner_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runnerType"))

    @runner_type.setter
    def runner_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfda2da2bf35f404d37bd8c0701c013d87b678dd3c123a8b28a97b1a10cbe8ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerType", value)

    @builtins.property
    @jsii.member(jsii_name="targetsEventSourceLocations")
    def targets_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetsEventSourceLocations"))

    @targets_event_source_locations.setter
    def targets_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__015dfdacf2efd87ce7c89106480a96e108791344a61da8f59586c86bb9d0b273)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b441399eb87a04094c6a36603674daad013ad1001dd404694ec575213e6115d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value)


@jsii.data_type(
    jsii_type="akeyless.eventForwarderSlack.EventForwarderSlackConfig",
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
        "url": "url",
        "auth_methods_event_source_locations": "authMethodsEventSourceLocations",
        "description": "description",
        "event_types": "eventTypes",
        "every": "every",
        "gateways_event_source_locations": "gatewaysEventSourceLocations",
        "id": "id",
        "items_event_source_locations": "itemsEventSourceLocations",
        "key": "key",
        "runner_type": "runnerType",
        "targets_event_source_locations": "targetsEventSourceLocations",
    },
)
class EventForwarderSlackConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        url: builtins.str,
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
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
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#name EventForwarderSlack#name}
        :param url: Slack Webhook URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#url EventForwarderSlack#url}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#auth_methods_event_source_locations EventForwarderSlack#auth_methods_event_source_locations}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#description EventForwarderSlack#description}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#event_types EventForwarderSlack#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#every EventForwarderSlack#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#gateways_event_source_locations EventForwarderSlack#gateways_event_source_locations}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#id EventForwarderSlack#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#items_event_source_locations EventForwarderSlack#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#key EventForwarderSlack#key}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#runner_type EventForwarderSlack#runner_type}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#targets_event_source_locations EventForwarderSlack#targets_event_source_locations}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a572f9c7f62ab4dd1a1b4a25302464e7bff985a7705060bc8c6dc0b384b02403)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument auth_methods_event_source_locations", value=auth_methods_event_source_locations, expected_type=type_hints["auth_methods_event_source_locations"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_types", value=event_types, expected_type=type_hints["event_types"])
            check_type(argname="argument every", value=every, expected_type=type_hints["every"])
            check_type(argname="argument gateways_event_source_locations", value=gateways_event_source_locations, expected_type=type_hints["gateways_event_source_locations"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument items_event_source_locations", value=items_event_source_locations, expected_type=type_hints["items_event_source_locations"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument runner_type", value=runner_type, expected_type=type_hints["runner_type"])
            check_type(argname="argument targets_event_source_locations", value=targets_event_source_locations, expected_type=type_hints["targets_event_source_locations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "url": url,
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
        if event_types is not None:
            self._values["event_types"] = event_types
        if every is not None:
            self._values["every"] = every
        if gateways_event_source_locations is not None:
            self._values["gateways_event_source_locations"] = gateways_event_source_locations
        if id is not None:
            self._values["id"] = id
        if items_event_source_locations is not None:
            self._values["items_event_source_locations"] = items_event_source_locations
        if key is not None:
            self._values["key"] = key
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#name EventForwarderSlack#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Slack Webhook URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#url EventForwarderSlack#url}
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_methods_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Auth Methods event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#auth_methods_event_source_locations EventForwarderSlack#auth_methods_event_source_locations}
        '''
        result = self._values.get("auth_methods_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#description EventForwarderSlack#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated list of types of events to notify about.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#event_types EventForwarderSlack#event_types}
        '''
        result = self._values.get("event_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def every(self) -> typing.Optional[builtins.str]:
        '''Rate of periodic runner repetition in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#every EventForwarderSlack#every}
        '''
        result = self._values.get("every")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateways_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#gateways_event_source_locations EventForwarderSlack#gateways_event_source_locations}
        '''
        result = self._values.get("gateways_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#id EventForwarderSlack#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def items_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Items event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#items_event_source_locations EventForwarderSlack#items_event_source_locations}
        '''
        result = self._values.get("items_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#key EventForwarderSlack#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runner_type(self) -> typing.Optional[builtins.str]:
        '''Event Forwarder runner type [immediate/periodic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#runner_type EventForwarderSlack#runner_type}
        '''
        result = self._values.get("runner_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Targets event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_slack#targets_event_source_locations EventForwarderSlack#targets_event_source_locations}
        '''
        result = self._values.get("targets_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventForwarderSlackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EventForwarderSlack",
    "EventForwarderSlackConfig",
]

publication.publish()

def _typecheckingstub__89b7ca926862c5093d45de286b8273acf66adfaac2b92e14ff11659a878def32(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    url: builtins.str,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d31a39862e7aae8d703955a95848b6c140e815f595a9aa2022eab0e1585b1805(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59ecfd9abf6f13b47be2638b6f4003457fde3bc81e21ad57a8596299a22f2f60(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96074a81aa25c86e526407e896b33ade154b2fe68d10859a0972bed110109f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__109ac2ebf50c56694f52f191b6cc7d4913c971cb95e924582772ea4b45acdfb2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7de5ff580d7eecd231155ab114bae337fac5e2dac2d68a666c5f7c684a68718a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__955ebd72904b1b91ee77b6191cc21a939edc540f8a4fac1559511ff18d058bbc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__585fed0db8d13e1232aa702d97fb4ef63a2cf8ed8b98fa7acae188a92f488046(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52f870f5e151b89f5881cfa5968c231fd6c45411eb55e6bbacfecbadcd70dbb3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__784d902a8a4ecf6bdab5af52f768152588197fd6648d2dacabb33d2414506143(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8d4b3b367afe896fd48bc11004f59195e76ebb167747780cbf669b230723c68(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfda2da2bf35f404d37bd8c0701c013d87b678dd3c123a8b28a97b1a10cbe8ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__015dfdacf2efd87ce7c89106480a96e108791344a61da8f59586c86bb9d0b273(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b441399eb87a04094c6a36603674daad013ad1001dd404694ec575213e6115d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a572f9c7f62ab4dd1a1b4a25302464e7bff985a7705060bc8c6dc0b384b02403(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    url: builtins.str,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    description: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
