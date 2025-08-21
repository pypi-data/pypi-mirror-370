'''
# `akeyless_event_forwarder_service_now`

Refer to the Terraform Registry for docs: [`akeyless_event_forwarder_service_now`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now).
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


class EventForwarderServiceNow(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.eventForwarderServiceNow.EventForwarderServiceNow",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now akeyless_event_forwarder_service_now}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        admin_name: typing.Optional[builtins.str] = None,
        admin_pwd: typing.Optional[builtins.str] = None,
        app_private_key_base64: typing.Optional[builtins.str] = None,
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        auth_type: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        host: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
        runner_type: typing.Optional[builtins.str] = None,
        targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_email: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now akeyless_event_forwarder_service_now} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#name EventForwarderServiceNow#name}
        :param admin_name: Workstation Admin Name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#admin_name EventForwarderServiceNow#admin_name}
        :param admin_pwd: Workstation Admin Password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#admin_pwd EventForwarderServiceNow#admin_pwd}
        :param app_private_key_base64: The RSA Private Key to use when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#app_private_key_base64 EventForwarderServiceNow#app_private_key_base64}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#auth_methods_event_source_locations EventForwarderServiceNow#auth_methods_event_source_locations}
        :param auth_type: The authentication type to use [user-pass/jwt]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#auth_type EventForwarderServiceNow#auth_type}
        :param client_id: The client ID to use when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#client_id EventForwarderServiceNow#client_id}
        :param client_secret: The client secret to use when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#client_secret EventForwarderServiceNow#client_secret}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#description EventForwarderServiceNow#description}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#event_types EventForwarderServiceNow#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#every EventForwarderServiceNow#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#gateways_event_source_locations EventForwarderServiceNow#gateways_event_source_locations}
        :param host: Workstation Host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#host EventForwarderServiceNow#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#id EventForwarderServiceNow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#items_event_source_locations EventForwarderServiceNow#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#key EventForwarderServiceNow#key}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#runner_type EventForwarderServiceNow#runner_type}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#targets_event_source_locations EventForwarderServiceNow#targets_event_source_locations}
        :param user_email: The user email to identify with when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#user_email EventForwarderServiceNow#user_email}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e750892615fa744ee4d6203cb83dccb328d7d63f9370da53b1b36495af63161e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = EventForwarderServiceNowConfig(
            name=name,
            admin_name=admin_name,
            admin_pwd=admin_pwd,
            app_private_key_base64=app_private_key_base64,
            auth_methods_event_source_locations=auth_methods_event_source_locations,
            auth_type=auth_type,
            client_id=client_id,
            client_secret=client_secret,
            description=description,
            event_types=event_types,
            every=every,
            gateways_event_source_locations=gateways_event_source_locations,
            host=host,
            id=id,
            items_event_source_locations=items_event_source_locations,
            key=key,
            runner_type=runner_type,
            targets_event_source_locations=targets_event_source_locations,
            user_email=user_email,
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
        '''Generates CDKTF code for importing a EventForwarderServiceNow resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EventForwarderServiceNow to import.
        :param import_from_id: The id of the existing EventForwarderServiceNow that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EventForwarderServiceNow to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8ffbf1b1e8cc2570241bfd15eb1f917359695931cf54e7f5f90bea5c6a2c47b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAdminName")
    def reset_admin_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminName", []))

    @jsii.member(jsii_name="resetAdminPwd")
    def reset_admin_pwd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdminPwd", []))

    @jsii.member(jsii_name="resetAppPrivateKeyBase64")
    def reset_app_private_key_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppPrivateKeyBase64", []))

    @jsii.member(jsii_name="resetAuthMethodsEventSourceLocations")
    def reset_auth_methods_event_source_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthMethodsEventSourceLocations", []))

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

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

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

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

    @jsii.member(jsii_name="resetUserEmail")
    def reset_user_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserEmail", []))

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
    @jsii.member(jsii_name="adminNameInput")
    def admin_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminNameInput"))

    @builtins.property
    @jsii.member(jsii_name="adminPwdInput")
    def admin_pwd_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminPwdInput"))

    @builtins.property
    @jsii.member(jsii_name="appPrivateKeyBase64Input")
    def app_private_key_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appPrivateKeyBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="authMethodsEventSourceLocationsInput")
    def auth_methods_event_source_locations_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "authMethodsEventSourceLocationsInput"))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

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
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

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
    @jsii.member(jsii_name="userEmailInput")
    def user_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="adminName")
    def admin_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminName"))

    @admin_name.setter
    def admin_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b25cb148dd18c95a2b2dd053978c1c19fc8c0e5cfb9a099da27a579ce1dff64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminName", value)

    @builtins.property
    @jsii.member(jsii_name="adminPwd")
    def admin_pwd(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPwd"))

    @admin_pwd.setter
    def admin_pwd(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4c7289898a22d1454cd0229eecc07c1bb9fe32f2ec199d91031f4425b325f7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminPwd", value)

    @builtins.property
    @jsii.member(jsii_name="appPrivateKeyBase64")
    def app_private_key_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appPrivateKeyBase64"))

    @app_private_key_base64.setter
    def app_private_key_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecca7ef7c5fb501ffcd78938aac9daa57ea66f31f365dec4a2af0a96eb386f6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appPrivateKeyBase64", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__422714066f4199638900e081e099d2423a6625c5c5887305b3bca5545b3cacfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authMethodsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11dce9617b634a564d49d192fbef5e2f7eeac2a9be80f7dfd0b1596f34c36cdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value)

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09aeefba8bfe23731287081a0382a2dccccfb7c8ff909aa376181c37baacf15c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c0c04430cf345261b6d384b4b6f4ad958a57708612c64634aaa80089297935)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f6ade8d510e5325be3f66626481ac809b8a6e27b64f9dfbafdb8423c47acc3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="eventTypes")
    def event_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eventTypes"))

    @event_types.setter
    def event_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f84fd12f99c4621844b36490004927fc8a7f7be10f257d211d717a0c1806fd68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventTypes", value)

    @builtins.property
    @jsii.member(jsii_name="every")
    def every(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "every"))

    @every.setter
    def every(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f983432ff3fadb7fba80d4e3f0d78e7493fff1658433ad324a669a93f22e259)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "every", value)

    @builtins.property
    @jsii.member(jsii_name="gatewaysEventSourceLocations")
    def gateways_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gatewaysEventSourceLocations"))

    @gateways_event_source_locations.setter
    def gateways_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6512c48c37bf537fb62eaa6a731044ff9b237db363f9273bbfdeaf11317ba62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewaysEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4749eeea62b01951a18130346922ae517640d7208e52481edca1f1fcfe0ef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5d8ca679f4ca6d3a517575dd4e7e3e02db0046b71f223ef290155202f93eb9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="itemsEventSourceLocations")
    def items_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "itemsEventSourceLocations"))

    @items_event_source_locations.setter
    def items_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcdb50c0ad0c14678019341831657be2fe7b581b60323a1d6834f0a46f8587fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3ad7337f4897e016f65ce8a51aa5fb2a92f9a37b0dafd20c0f1a1263b30d842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a74b3eb9f8ad21bafa06fe3c5f1a3046c52d42726cdae61480664169c3fe00be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="runnerType")
    def runner_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runnerType"))

    @runner_type.setter
    def runner_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__481878abd44e0c453d668bb6aedb85007e897156a699b947db63ba7ed9e2e36c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runnerType", value)

    @builtins.property
    @jsii.member(jsii_name="targetsEventSourceLocations")
    def targets_event_source_locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetsEventSourceLocations"))

    @targets_event_source_locations.setter
    def targets_event_source_locations(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24bfadd2c4c14edb55783c7d38f84fc5b153198a718d7b5df47faaa544630439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetsEventSourceLocations", value)

    @builtins.property
    @jsii.member(jsii_name="userEmail")
    def user_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userEmail"))

    @user_email.setter
    def user_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5105845549b92f5761d600b90731cac41748f04314339921fdb19365a5c8ef9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userEmail", value)


@jsii.data_type(
    jsii_type="akeyless.eventForwarderServiceNow.EventForwarderServiceNowConfig",
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
        "admin_name": "adminName",
        "admin_pwd": "adminPwd",
        "app_private_key_base64": "appPrivateKeyBase64",
        "auth_methods_event_source_locations": "authMethodsEventSourceLocations",
        "auth_type": "authType",
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "description": "description",
        "event_types": "eventTypes",
        "every": "every",
        "gateways_event_source_locations": "gatewaysEventSourceLocations",
        "host": "host",
        "id": "id",
        "items_event_source_locations": "itemsEventSourceLocations",
        "key": "key",
        "runner_type": "runnerType",
        "targets_event_source_locations": "targetsEventSourceLocations",
        "user_email": "userEmail",
    },
)
class EventForwarderServiceNowConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        admin_name: typing.Optional[builtins.str] = None,
        admin_pwd: typing.Optional[builtins.str] = None,
        app_private_key_base64: typing.Optional[builtins.str] = None,
        auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        auth_type: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        every: typing.Optional[builtins.str] = None,
        gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        host: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        key: typing.Optional[builtins.str] = None,
        runner_type: typing.Optional[builtins.str] = None,
        targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_email: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Event Forwarder name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#name EventForwarderServiceNow#name}
        :param admin_name: Workstation Admin Name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#admin_name EventForwarderServiceNow#admin_name}
        :param admin_pwd: Workstation Admin Password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#admin_pwd EventForwarderServiceNow#admin_pwd}
        :param app_private_key_base64: The RSA Private Key to use when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#app_private_key_base64 EventForwarderServiceNow#app_private_key_base64}
        :param auth_methods_event_source_locations: Auth Methods event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#auth_methods_event_source_locations EventForwarderServiceNow#auth_methods_event_source_locations}
        :param auth_type: The authentication type to use [user-pass/jwt]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#auth_type EventForwarderServiceNow#auth_type}
        :param client_id: The client ID to use when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#client_id EventForwarderServiceNow#client_id}
        :param client_secret: The client secret to use when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#client_secret EventForwarderServiceNow#client_secret}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#description EventForwarderServiceNow#description}
        :param event_types: A comma-separated list of types of events to notify about. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#event_types EventForwarderServiceNow#event_types}
        :param every: Rate of periodic runner repetition in hours. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#every EventForwarderServiceNow#every}
        :param gateways_event_source_locations: Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#gateways_event_source_locations EventForwarderServiceNow#gateways_event_source_locations}
        :param host: Workstation Host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#host EventForwarderServiceNow#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#id EventForwarderServiceNow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param items_event_source_locations: Items event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#items_event_source_locations EventForwarderServiceNow#items_event_source_locations}
        :param key: Key name. The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#key EventForwarderServiceNow#key}
        :param runner_type: Event Forwarder runner type [immediate/periodic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#runner_type EventForwarderServiceNow#runner_type}
        :param targets_event_source_locations: Targets event sources to forward events about, for example: /abc/*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#targets_event_source_locations EventForwarderServiceNow#targets_event_source_locations}
        :param user_email: The user email to identify with when connecting with jwt authentication. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#user_email EventForwarderServiceNow#user_email}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64f8ac11bcaa8ada33c36bf25743c2147e91b39a5be8084d7d387c466cbecd2a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument admin_name", value=admin_name, expected_type=type_hints["admin_name"])
            check_type(argname="argument admin_pwd", value=admin_pwd, expected_type=type_hints["admin_pwd"])
            check_type(argname="argument app_private_key_base64", value=app_private_key_base64, expected_type=type_hints["app_private_key_base64"])
            check_type(argname="argument auth_methods_event_source_locations", value=auth_methods_event_source_locations, expected_type=type_hints["auth_methods_event_source_locations"])
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_types", value=event_types, expected_type=type_hints["event_types"])
            check_type(argname="argument every", value=every, expected_type=type_hints["every"])
            check_type(argname="argument gateways_event_source_locations", value=gateways_event_source_locations, expected_type=type_hints["gateways_event_source_locations"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument items_event_source_locations", value=items_event_source_locations, expected_type=type_hints["items_event_source_locations"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument runner_type", value=runner_type, expected_type=type_hints["runner_type"])
            check_type(argname="argument targets_event_source_locations", value=targets_event_source_locations, expected_type=type_hints["targets_event_source_locations"])
            check_type(argname="argument user_email", value=user_email, expected_type=type_hints["user_email"])
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
        if admin_name is not None:
            self._values["admin_name"] = admin_name
        if admin_pwd is not None:
            self._values["admin_pwd"] = admin_pwd
        if app_private_key_base64 is not None:
            self._values["app_private_key_base64"] = app_private_key_base64
        if auth_methods_event_source_locations is not None:
            self._values["auth_methods_event_source_locations"] = auth_methods_event_source_locations
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if description is not None:
            self._values["description"] = description
        if event_types is not None:
            self._values["event_types"] = event_types
        if every is not None:
            self._values["every"] = every
        if gateways_event_source_locations is not None:
            self._values["gateways_event_source_locations"] = gateways_event_source_locations
        if host is not None:
            self._values["host"] = host
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
        if user_email is not None:
            self._values["user_email"] = user_email

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#name EventForwarderServiceNow#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_name(self) -> typing.Optional[builtins.str]:
        '''Workstation Admin Name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#admin_name EventForwarderServiceNow#admin_name}
        '''
        result = self._values.get("admin_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def admin_pwd(self) -> typing.Optional[builtins.str]:
        '''Workstation Admin Password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#admin_pwd EventForwarderServiceNow#admin_pwd}
        '''
        result = self._values.get("admin_pwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_private_key_base64(self) -> typing.Optional[builtins.str]:
        '''The RSA Private Key to use when connecting with jwt authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#app_private_key_base64 EventForwarderServiceNow#app_private_key_base64}
        '''
        result = self._values.get("app_private_key_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_methods_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Auth Methods event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#auth_methods_event_source_locations EventForwarderServiceNow#auth_methods_event_source_locations}
        '''
        result = self._values.get("auth_methods_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''The authentication type to use [user-pass/jwt].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#auth_type EventForwarderServiceNow#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''The client ID to use when connecting with jwt authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#client_id EventForwarderServiceNow#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''The client secret to use when connecting with jwt authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#client_secret EventForwarderServiceNow#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#description EventForwarderServiceNow#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated list of types of events to notify about.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#event_types EventForwarderServiceNow#event_types}
        '''
        result = self._values.get("event_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def every(self) -> typing.Optional[builtins.str]:
        '''Rate of periodic runner repetition in hours.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#every EventForwarderServiceNow#every}
        '''
        result = self._values.get("every")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gateways_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Gateways event sources to forward events about,for example the relevant Gateways cluster urls,: http://localhost:8000.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#gateways_event_source_locations EventForwarderServiceNow#gateways_event_source_locations}
        '''
        result = self._values.get("gateways_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Workstation Host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#host EventForwarderServiceNow#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#id EventForwarderServiceNow#id}.

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#items_event_source_locations EventForwarderServiceNow#items_event_source_locations}
        '''
        result = self._values.get("items_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the Event Forwarder secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#key EventForwarderServiceNow#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runner_type(self) -> typing.Optional[builtins.str]:
        '''Event Forwarder runner type [immediate/periodic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#runner_type EventForwarderServiceNow#runner_type}
        '''
        result = self._values.get("runner_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def targets_event_source_locations(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Targets event sources to forward events about, for example: /abc/*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#targets_event_source_locations EventForwarderServiceNow#targets_event_source_locations}
        '''
        result = self._values.get("targets_event_source_locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_email(self) -> typing.Optional[builtins.str]:
        '''The user email to identify with when connecting with jwt authentication.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/event_forwarder_service_now#user_email EventForwarderServiceNow#user_email}
        '''
        result = self._values.get("user_email")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventForwarderServiceNowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "EventForwarderServiceNow",
    "EventForwarderServiceNowConfig",
]

publication.publish()

def _typecheckingstub__e750892615fa744ee4d6203cb83dccb328d7d63f9370da53b1b36495af63161e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    admin_name: typing.Optional[builtins.str] = None,
    admin_pwd: typing.Optional[builtins.str] = None,
    app_private_key_base64: typing.Optional[builtins.str] = None,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    auth_type: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    host: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_email: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e8ffbf1b1e8cc2570241bfd15eb1f917359695931cf54e7f5f90bea5c6a2c47b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b25cb148dd18c95a2b2dd053978c1c19fc8c0e5cfb9a099da27a579ce1dff64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4c7289898a22d1454cd0229eecc07c1bb9fe32f2ec199d91031f4425b325f7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecca7ef7c5fb501ffcd78938aac9daa57ea66f31f365dec4a2af0a96eb386f6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__422714066f4199638900e081e099d2423a6625c5c5887305b3bca5545b3cacfb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11dce9617b634a564d49d192fbef5e2f7eeac2a9be80f7dfd0b1596f34c36cdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09aeefba8bfe23731287081a0382a2dccccfb7c8ff909aa376181c37baacf15c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c0c04430cf345261b6d384b4b6f4ad958a57708612c64634aaa80089297935(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f6ade8d510e5325be3f66626481ac809b8a6e27b64f9dfbafdb8423c47acc3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f84fd12f99c4621844b36490004927fc8a7f7be10f257d211d717a0c1806fd68(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f983432ff3fadb7fba80d4e3f0d78e7493fff1658433ad324a669a93f22e259(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6512c48c37bf537fb62eaa6a731044ff9b237db363f9273bbfdeaf11317ba62(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4749eeea62b01951a18130346922ae517640d7208e52481edca1f1fcfe0ef5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5d8ca679f4ca6d3a517575dd4e7e3e02db0046b71f223ef290155202f93eb9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcdb50c0ad0c14678019341831657be2fe7b581b60323a1d6834f0a46f8587fc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3ad7337f4897e016f65ce8a51aa5fb2a92f9a37b0dafd20c0f1a1263b30d842(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a74b3eb9f8ad21bafa06fe3c5f1a3046c52d42726cdae61480664169c3fe00be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__481878abd44e0c453d668bb6aedb85007e897156a699b947db63ba7ed9e2e36c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24bfadd2c4c14edb55783c7d38f84fc5b153198a718d7b5df47faaa544630439(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5105845549b92f5761d600b90731cac41748f04314339921fdb19365a5c8ef9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64f8ac11bcaa8ada33c36bf25743c2147e91b39a5be8084d7d387c466cbecd2a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    admin_name: typing.Optional[builtins.str] = None,
    admin_pwd: typing.Optional[builtins.str] = None,
    app_private_key_base64: typing.Optional[builtins.str] = None,
    auth_methods_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    auth_type: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    event_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    every: typing.Optional[builtins.str] = None,
    gateways_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    host: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    items_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    key: typing.Optional[builtins.str] = None,
    runner_type: typing.Optional[builtins.str] = None,
    targets_event_source_locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_email: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
