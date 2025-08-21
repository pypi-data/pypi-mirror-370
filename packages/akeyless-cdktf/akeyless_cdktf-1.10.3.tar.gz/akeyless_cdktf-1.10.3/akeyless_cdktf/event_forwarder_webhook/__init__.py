'''
# `akeyless_event_forwarder_webhook`

Refer to the Terraform Registry for docs: [`akeyless_event_forwarder_webhook`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook).
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


class EventForwarderWebhook(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.eventForwarderWebhook.EventForwarderWebhook",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook akeyless_event_forwarder_webhook}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        auth_token: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        client_cert_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        private_key_data: typing.Optional[builtins.str] = None,
        runner_type: typing.Optional[builtins.str] = None,
        server_certificates: typing.Optional[builtins.str] = None,
        targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        url: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook akeyless_event_forwarder_webhook} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#name EventForwarderWebhook#name}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_methods_event_source_locations EventForwarderWebhook#auth_methods_event_source_locations}
        :param auth_token: Base64 encoded Token string relevant for token auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_token EventForwarderWebhook#auth_token}
        :param auth_type: The Webhook authentication type [user-pass, bearer-token, certificate]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_type EventForwarderWebhook#auth_type}
        :param client_cert_data: Base64 encoded PEM certificate, relevant for certificate auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#client_cert_data EventForwarderWebhook#client_cert_data}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#description EventForwarderWebhook#description}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#event_types EventForwarderWebhook#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#every EventForwarderWebhook#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#gateways_event_source_locations EventForwarderWebhook#gateways_event_source_locations}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#id EventForwarderWebhook#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#items_event_source_locations EventForwarderWebhook#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#key EventForwarderWebhook#key}
        :param password: Password for authentication relevant for user-pass auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#password EventForwarderWebhook#password}
        :param private_key_data: Base64 encoded PEM RSA Private Key, relevant for certificate auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#private_key_data EventForwarderWebhook#private_key_data}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#runner_type EventForwarderWebhook#runner_type}
        :param server_certificates: Base64 encoded PEM certificate of the Webhook. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#server_certificates EventForwarderWebhook#server_certificates}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#targets_event_source_locations EventForwarderWebhook#targets_event_source_locations}
        :param url: Webhook URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#url EventForwarderWebhook#url}
        :param username: Username for authentication relevant for user-pass auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#username EventForwarderWebhook#username}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69aa8328df654df04be8487e009262af78d43d075d0d07a20e42759f0bea521b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = EventForwarderWebhookConfig(
            name=name,
            auth_methods_event_source_locations=auth_methods_event_source_locations,
            auth_token=auth_token,
            auth_type=auth_type,
            client_cert_data=client_cert_data,
            description=description,
            event_types=event_types,
            every=every,
            gateways_event_source_locations=gateways_event_source_locations,
            id=id,
            items_event_source_locations=items_event_source_locations,
            key=key,
            password=password,
            private_key_data=private_key_data,
            runner_type=runner_type,
            server_certificates=server_certificates,
            targets_event_source_locations=targets_event_source_locations,
            url=url,
            username=username,
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
        '''Generates CDKTF code for importing a EventForwarderWebhook resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EventForwarderWebhook to import.
        :param import_from_id: The id of the existing EventForwarderWebhook that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EventForwarderWebhook to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__575f191320618091daa17b768da5efc69b6214a2ef03b5fdab56e1f38cfdd9c2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAuthMethodsEventSourceLocations")
    def reset_auth_methods_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethodsEventSourceLocations", []))

    @jsii.member(jsii_name="resetAuthToken")
    def reset_auth_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthToken", []))

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetClientCertData")
    def reset_client_cert_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientCertData", []))

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

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPrivateKeyData")
    def reset_private_key_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyData", []))

    @jsii.member(jsii_name="resetRunnerType")
    def reset_runner_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunnerType", []))

    @jsii.member(jsii_name="resetServerCertificates")
    def reset_server_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerCertificates", []))

    @jsii.member(jsii_name="resetTargetsEventSourceLocations")
    def reset_targets_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetsEventSourceLocations", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

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
    @jsii.member(jsii_name="authTokenInput")
    def auth_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="clientCertDataInput")
    def client_cert_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientCertDataInput"))

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
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyDataInput")
    def private_key_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyDataInput"))

    @builtins.property
    @jsii.member(jsii_name="runnerTypeInput")
    def runner_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runnerTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="serverCertificatesInput")
    def server_certificates_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverCertificatesInput"))

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
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__ad544cbba9e869d76ce63d258e0110cc53a5ed1f6c5b4b64b03b885e8e6b5ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethodsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="authToken")
    def auth_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authToken"))

    @auth_token.setter
    def auth_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7217e82582078720b19b40696eab1a6ff3d76177116b59813230bf5b0c6bff8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authToken", value)

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b24b222cb421d69d6179b19a65897cdb087a77723ad2c51c367d333ce7561247)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value)

    @builtins.property
    @jsii.member(jsii_name="clientCertData")
    def client_cert_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientCertData"))

    @client_cert_data.setter
    def client_cert_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c250d0eab05eee50e577cc8f6898f76a6e1e9f392b82b69698fcc00f2550d82e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientCertData", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f711ad52e21c784e60c59948c100744003a7997b30d18dd7ff0c82b2a5dfad3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="eventTypes")
    def event_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventTypes"))

    @event_types.setter
    def event_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3d0a44a4b3a4abca62d5b6d6cf1a1d6a02c9c5f50c15159b7fcb9a0deb8919d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventTypes", value)

    @builtins.property
    @jsii.member(jsii_name="every")
    def every(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "every"))

    @every.setter
    def every(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2d13b4c953abc4f4571988b4c43df7b1cc6ea84b132dbd880491a29fa6467bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "every", value)

    @builtins.property
    @jsii.member(jsii_name="gatewaysEventSourceLocations")
    def gateways_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gatewaysEventSourceLocations"))

    @gateways_event_source_locations.setter
    def gateways_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04adf34887ec136baccaf2d17df9e71a36adb89b1cf148fe93e44b6ea280eb5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewaysEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8736094e00297dc908a4c53aefd2d54026cadf4355c911ebcb1c461872d91b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="itemsEventSourceLocations")
    def items_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "itemsEventSourceLocations"))

    @items_event_source_locations.setter
    def items_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb8c33bcedf9e6e133879ad3ed01aec590ae0808cb1e89ce2629f970d5409c77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__199f7253e950ca8a423c46daab20d8ce1cb1b340856d5bcefafda2433d57ca53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f3ebf8a1976e4ab842c2f450ffc854a813bba74cef9ce9d715caeff9c91f2b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3c0b26ace787bc5482650883c8deaa77025d3ed1461d2c099c0cc4519244577)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property
    @jsii.member(jsii_name="privateKeyData")
    def private_key_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyData"))

    @private_key_data.setter
    def private_key_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5152013d03fdaab6ce451830eeae983b6e75fc3907698cc026d336c1d6ae052c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKeyData", value)

    @builtins.property
    @jsii.member(jsii_name="runnerType")
    def runner_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runnerType"))

    @runner_type.setter
    def runner_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68afd48a811abfb4a0f9b97da9d96d36168e1f0f72b738ccd4fcafcde079359f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerType", value)

    @builtins.property
    @jsii.member(jsii_name="serverCertificates")
    def server_certificates(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverCertificates"))

    @server_certificates.setter
    def server_certificates(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c954aad6489af15cebe739c9f52d6bffde1db1fb8ff37cc5ad229dd1ff52fc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverCertificates", value)

    @builtins.property
    @jsii.member(jsii_name="targetsEventSourceLocations")
    def targets_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetsEventSourceLocations"))

    @targets_event_source_locations.setter
    def targets_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aac47c27510e8fe2d16dc91cee8ec54a1e0de52d3095590fe9aec7fa96c5453)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f860001701a2fd6a4b4d1b6cce28bb578a93919b7944da07b405af0145b464b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value)

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__515605f1ad6ef8217115f2d9dcc43e124af328343bd6e9f24a4748acc662d457)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="akeyless.eventForwarderWebhook.EventForwarderWebhookConfig",
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
        "auth_token": "authToken",
        "auth_type": "authType",
        "client_cert_data": "clientCertData",
        "description": "description",
        "event_types": "eventTypes",
        "every": "every",
        "gateways_event_source_locations": "gatewaysEventSourceLocations",
        "id": "id",
        "items_event_source_locations": "itemsEventSourceLocations",
        "key": "key",
        "password": "password",
        "private_key_data": "privateKeyData",
        "runner_type": "runnerType",
        "server_certificates": "serverCertificates",
        "targets_event_source_locations": "targetsEventSourceLocations",
        "url": "url",
        "username": "username",
    },
)
class EventForwarderWebhookConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        auth_token: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        client_cert_data: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        private_key_data: typing.Optional[builtins.str] = None,
        runner_type: typing.Optional[builtins.str] = None,
        server_certificates: typing.Optional[builtins.str] = None,
        targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        url: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#name EventForwarderWebhook#name}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_methods_event_source_locations EventForwarderWebhook#auth_methods_event_source_locations}
        :param auth_token: Base64 encoded Token string relevant for token auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_token EventForwarderWebhook#auth_token}
        :param auth_type: The Webhook authentication type [user-pass, bearer-token, certificate]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_type EventForwarderWebhook#auth_type}
        :param client_cert_data: Base64 encoded PEM certificate, relevant for certificate auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#client_cert_data EventForwarderWebhook#client_cert_data}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#description EventForwarderWebhook#description}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#event_types EventForwarderWebhook#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#every EventForwarderWebhook#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#gateways_event_source_locations EventForwarderWebhook#gateways_event_source_locations}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#id EventForwarderWebhook#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#items_event_source_locations EventForwarderWebhook#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#key EventForwarderWebhook#key}
        :param password: Password for authentication relevant for user-pass auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#password EventForwarderWebhook#password}
        :param private_key_data: Base64 encoded PEM RSA Private Key, relevant for certificate auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#private_key_data EventForwarderWebhook#private_key_data}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#runner_type EventForwarderWebhook#runner_type}
        :param server_certificates: Base64 encoded PEM certificate of the Webhook. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#server_certificates EventForwarderWebhook#server_certificates}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#targets_event_source_locations EventForwarderWebhook#targets_event_source_locations}
        :param url: Webhook URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#url EventForwarderWebhook#url}
        :param username: Username for authentication relevant for user-pass auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#username EventForwarderWebhook#username}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__780ab0e2cf66fb5cc312bb6251278e19d5c3c1a0e37ab8e35285c54e21b7921d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auth_methods_event_source_locations", value=auth_methods_event_source_locations, expected_type=type_hints["auth_methods_event_source_locations"])
            check_type(argname="argument auth_token", value=auth_token, expected_type=type_hints["auth_token"])
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument client_cert_data", value=client_cert_data, expected_type=type_hints["client_cert_data"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_types", value=event_types, expected_type=type_hints["event_types"])
            check_type(argname="argument every", value=every, expected_type=type_hints["every"])
            check_type(argname="argument gateways_event_source_locations", value=gateways_event_source_locations, expected_type=type_hints["gateways_event_source_locations"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument items_event_source_locations", value=items_event_source_locations, expected_type=type_hints["items_event_source_locations"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument private_key_data", value=private_key_data, expected_type=type_hints["private_key_data"])
            check_type(argname="argument runner_type", value=runner_type, expected_type=type_hints["runner_type"])
            check_type(argname="argument server_certificates", value=server_certificates, expected_type=type_hints["server_certificates"])
            check_type(argname="argument targets_event_source_locations", value=targets_event_source_locations, expected_type=type_hints["targets_event_source_locations"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
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
        if auth_token is not None:
            self._values["auth_token"] = auth_token
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if client_cert_data is not None:
            self._values["client_cert_data"] = client_cert_data
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
        if password is not None:
            self._values["password"] = password
        if private_key_data is not None:
            self._values["private_key_data"] = private_key_data
        if runner_type is not None:
            self._values["runner_type"] = runner_type
        if server_certificates is not None:
            self._values["server_certificates"] = server_certificates
        if targets_event_source_locations is not None:
            self._values["targets_event_source_locations"] = targets_event_source_locations
        if url is not None:
            self._values["url"] = url
        if username is not None:
            self._values["username"] = username

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#name EventForwarderWebhook#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_methods_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Auth Methods event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_methods_event_source_locations EventForwarderWebhook#auth_methods_event_source_locations}
        '''
        result = self._values.get("auth_methods_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auth_token(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded Token string relevant for token auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_token EventForwarderWebhook#auth_token}
        '''
        result = self._values.get("auth_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''The Webhook authentication type [user-pass, bearer-token, certificate].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#auth_type EventForwarderWebhook#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_cert_data(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded PEM certificate, relevant for certificate auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#client_cert_data EventForwarderWebhook#client_cert_data}
        '''
        result = self._values.get("client_cert_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#description EventForwarderWebhook#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated list of types of events to notify about.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#event_types EventForwarderWebhook#event_types}
        '''
        result = self._values.get("event_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def every(self) -> typing.Optional[builtins.str]:
        '''Rate of periodic runner repetition in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#every EventForwarderWebhook#every}
        '''
        result = self._values.get("every")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateways_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#gateways_event_source_locations EventForwarderWebhook#gateways_event_source_locations}
        '''
        result = self._values.get("gateways_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#id EventForwarderWebhook#id}.

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#items_event_source_locations EventForwarderWebhook#items_event_source_locations}
        '''
        result = self._values.get("items_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#key EventForwarderWebhook#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for authentication relevant for user-pass auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#password EventForwarderWebhook#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_data(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded PEM RSA Private Key, relevant for certificate auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#private_key_data EventForwarderWebhook#private_key_data}
        '''
        result = self._values.get("private_key_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runner_type(self) -> typing.Optional[builtins.str]:
        '''Event Forwarder runner type [immediate/periodic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#runner_type EventForwarderWebhook#runner_type}
        '''
        result = self._values.get("runner_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_certificates(self) -> typing.Optional[builtins.str]:
        '''Base64 encoded PEM certificate of the Webhook.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#server_certificates EventForwarderWebhook#server_certificates}
        '''
        result = self._values.get("server_certificates")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Targets event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#targets_event_source_locations EventForwarderWebhook#targets_event_source_locations}
        '''
        result = self._values.get("targets_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Webhook URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#url EventForwarderWebhook#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Username for authentication relevant for user-pass auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_webhook#username EventForwarderWebhook#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventForwarderWebhookConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EventForwarderWebhook",
    "EventForwarderWebhookConfig",
]

publication.publish()

def _typecheckingstub__69aa8328df654df04be8487e009262af78d43d075d0d07a20e42759f0bea521b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    auth_token: typing.Optional[builtins.str] = None,
    auth_type: typing.Optional[builtins.str] = None,
    client_cert_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    private_key_data: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    server_certificates: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    url: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__575f191320618091daa17b768da5efc69b6214a2ef03b5fdab56e1f38cfdd9c2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad544cbba9e869d76ce63d258e0110cc53a5ed1f6c5b4b64b03b885e8e6b5ef3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7217e82582078720b19b40696eab1a6ff3d76177116b59813230bf5b0c6bff8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b24b222cb421d69d6179b19a65897cdb087a77723ad2c51c367d333ce7561247(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c250d0eab05eee50e577cc8f6898f76a6e1e9f392b82b69698fcc00f2550d82e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f711ad52e21c784e60c59948c100744003a7997b30d18dd7ff0c82b2a5dfad3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d0a44a4b3a4abca62d5b6d6cf1a1d6a02c9c5f50c15159b7fcb9a0deb8919d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2d13b4c953abc4f4571988b4c43df7b1cc6ea84b132dbd880491a29fa6467bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04adf34887ec136baccaf2d17df9e71a36adb89b1cf148fe93e44b6ea280eb5e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8736094e00297dc908a4c53aefd2d54026cadf4355c911ebcb1c461872d91b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb8c33bcedf9e6e133879ad3ed01aec590ae0808cb1e89ce2629f970d5409c77(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__199f7253e950ca8a423c46daab20d8ce1cb1b340856d5bcefafda2433d57ca53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f3ebf8a1976e4ab842c2f450ffc854a813bba74cef9ce9d715caeff9c91f2b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c0b26ace787bc5482650883c8deaa77025d3ed1461d2c099c0cc4519244577(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5152013d03fdaab6ce451830eeae983b6e75fc3907698cc026d336c1d6ae052c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68afd48a811abfb4a0f9b97da9d96d36168e1f0f72b738ccd4fcafcde079359f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c954aad6489af15cebe739c9f52d6bffde1db1fb8ff37cc5ad229dd1ff52fc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aac47c27510e8fe2d16dc91cee8ec54a1e0de52d3095590fe9aec7fa96c5453(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f860001701a2fd6a4b4d1b6cce28bb578a93919b7944da07b405af0145b464b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__515605f1ad6ef8217115f2d9dcc43e124af328343bd6e9f24a4748acc662d457(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__780ab0e2cf66fb5cc312bb6251278e19d5c3c1a0e37ab8e35285c54e21b7921d(
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
    auth_token: typing.Optional[builtins.str] = None,
    auth_type: typing.Optional[builtins.str] = None,
    client_cert_data: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    private_key_data: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    server_certificates: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    url: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
