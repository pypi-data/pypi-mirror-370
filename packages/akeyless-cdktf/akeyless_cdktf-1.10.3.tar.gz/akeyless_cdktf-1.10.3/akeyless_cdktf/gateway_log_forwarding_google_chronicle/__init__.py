'''
# `akeyless_gateway_log_forwarding_google_chronicle`

Refer to the Terraform Registry for docs: [`akeyless_gateway_log_forwarding_google_chronicle`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle).
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


class GatewayLogForwardingGoogleChronicle(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayLogForwardingGoogleChronicle.GatewayLogForwardingGoogleChronicle",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle akeyless_gateway_log_forwarding_google_chronicle}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        customer_id: typing.Optional[builtins.str] = None,
        enable: typing.Optional[builtins.str] = None,
        gcp_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        log_type: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle akeyless_gateway_log_forwarding_google_chronicle} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param customer_id: Google chronicle customer id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#customer_id GatewayLogForwardingGoogleChronicle#customer_id}
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#enable GatewayLogForwardingGoogleChronicle#enable}
        :param gcp_key: Base64-encoded service account private key text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#gcp_key GatewayLogForwardingGoogleChronicle#gcp_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#id GatewayLogForwardingGoogleChronicle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_type: Google chronicle log type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#log_type GatewayLogForwardingGoogleChronicle#log_type}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#output_format GatewayLogForwardingGoogleChronicle#output_format}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#pull_interval GatewayLogForwardingGoogleChronicle#pull_interval}
        :param region: Google chronicle region [eu_multi_region/london/us_multi_region/singapore/tel_aviv]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#region GatewayLogForwardingGoogleChronicle#region}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a81f0594179a44b1daadaa72c5e2e62572dd25678e3e81109883efe9c922ea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayLogForwardingGoogleChronicleConfig(
            customer_id=customer_id,
            enable=enable,
            gcp_key=gcp_key,
            id=id,
            log_type=log_type,
            output_format=output_format,
            pull_interval=pull_interval,
            region=region,
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
        '''Generates CDKTF code for importing a GatewayLogForwardingGoogleChronicle resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayLogForwardingGoogleChronicle to import.
        :param import_from_id: The id of the existing GatewayLogForwardingGoogleChronicle that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayLogForwardingGoogleChronicle to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__969b00b499eadf166a430c67d953f007ee5212e5b33166bf3adad2d4c2cf2132)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomerId")
    def reset_customer_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerId", []))

    @jsii.member(jsii_name="resetEnable")
    def reset_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnable", []))

    @jsii.member(jsii_name="resetGcpKey")
    def reset_gcp_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLogType")
    def reset_log_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogType", []))

    @jsii.member(jsii_name="resetOutputFormat")
    def reset_output_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFormat", []))

    @jsii.member(jsii_name="resetPullInterval")
    def reset_pull_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullInterval", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

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
    @jsii.member(jsii_name="customerIdInput")
    def customer_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enableInput")
    def enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enableInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpKeyInput")
    def gcp_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="logTypeInput")
    def log_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="outputFormatInput")
    def output_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="pullIntervalInput")
    def pull_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="customerId")
    def customer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerId"))

    @customer_id.setter
    def customer_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6f952b44f1911233782ca2e0ab014cf01f36dea827eaae7fb8b2f8beaf403ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerId", value)

    @builtins.property
    @jsii.member(jsii_name="enable")
    def enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32814baee0c067fabfc5f3bcc317d9adbbdc10b3231fbf19fe2232b5ab9aaa91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enable", value)

    @builtins.property
    @jsii.member(jsii_name="gcpKey")
    def gcp_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpKey"))

    @gcp_key.setter
    def gcp_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6f5f83202def55a8346e7498f53cbd5e8904e22c6b538e5f0ab73f2922b7a73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpKey", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d69c12cb9dc0ada58b0a4406cea3272975993398d6e49cf74a60ffeb0afdb26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="logType")
    def log_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logType"))

    @log_type.setter
    def log_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f35cd1ff7d15b9b0508afefb3accac415cc0a5fc7dc1aa08055385ed2e6dcf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logType", value)

    @builtins.property
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFormat"))

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__736f2d5b9dcfc24dd10a427aae30165cab9ea69b53964a5e014f2807ed21a29d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputFormat", value)

    @builtins.property
    @jsii.member(jsii_name="pullInterval")
    def pull_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullInterval"))

    @pull_interval.setter
    def pull_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d786efe0a46f4c11184dfa72fa7acbbb122ee4918ffcdbaa252687a4643097c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pullInterval", value)

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25771fe1b1c1aeb18531ecefc5897638aa6e9553093ebe0b4f14682de17f7667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayLogForwardingGoogleChronicle.GatewayLogForwardingGoogleChronicleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "customer_id": "customerId",
        "enable": "enable",
        "gcp_key": "gcpKey",
        "id": "id",
        "log_type": "logType",
        "output_format": "outputFormat",
        "pull_interval": "pullInterval",
        "region": "region",
    },
)
class GatewayLogForwardingGoogleChronicleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        customer_id: typing.Optional[builtins.str] = None,
        enable: typing.Optional[builtins.str] = None,
        gcp_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        log_type: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param customer_id: Google chronicle customer id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#customer_id GatewayLogForwardingGoogleChronicle#customer_id}
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#enable GatewayLogForwardingGoogleChronicle#enable}
        :param gcp_key: Base64-encoded service account private key text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#gcp_key GatewayLogForwardingGoogleChronicle#gcp_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#id GatewayLogForwardingGoogleChronicle#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_type: Google chronicle log type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#log_type GatewayLogForwardingGoogleChronicle#log_type}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#output_format GatewayLogForwardingGoogleChronicle#output_format}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#pull_interval GatewayLogForwardingGoogleChronicle#pull_interval}
        :param region: Google chronicle region [eu_multi_region/london/us_multi_region/singapore/tel_aviv]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#region GatewayLogForwardingGoogleChronicle#region}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c07c911bb86202fa659b0b8f5eb01ffecb7f33116674be3d0ae9be12fdefb06)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument customer_id", value=customer_id, expected_type=type_hints["customer_id"])
            check_type(argname="argument enable", value=enable, expected_type=type_hints["enable"])
            check_type(argname="argument gcp_key", value=gcp_key, expected_type=type_hints["gcp_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument log_type", value=log_type, expected_type=type_hints["log_type"])
            check_type(argname="argument output_format", value=output_format, expected_type=type_hints["output_format"])
            check_type(argname="argument pull_interval", value=pull_interval, expected_type=type_hints["pull_interval"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if customer_id is not None:
            self._values["customer_id"] = customer_id
        if enable is not None:
            self._values["enable"] = enable
        if gcp_key is not None:
            self._values["gcp_key"] = gcp_key
        if id is not None:
            self._values["id"] = id
        if log_type is not None:
            self._values["log_type"] = log_type
        if output_format is not None:
            self._values["output_format"] = output_format
        if pull_interval is not None:
            self._values["pull_interval"] = pull_interval
        if region is not None:
            self._values["region"] = region

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
    def customer_id(self) -> typing.Optional[builtins.str]:
        '''Google chronicle customer id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#customer_id GatewayLogForwardingGoogleChronicle#customer_id}
        '''
        result = self._values.get("customer_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable(self) -> typing.Optional[builtins.str]:
        '''Enable Log Forwarding [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#enable GatewayLogForwardingGoogleChronicle#enable}
        '''
        result = self._values.get("enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_key(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded service account private key text.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#gcp_key GatewayLogForwardingGoogleChronicle#gcp_key}
        '''
        result = self._values.get("gcp_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#id GatewayLogForwardingGoogleChronicle#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_type(self) -> typing.Optional[builtins.str]:
        '''Google chronicle log type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#log_type GatewayLogForwardingGoogleChronicle#log_type}
        '''
        result = self._values.get("log_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_format(self) -> typing.Optional[builtins.str]:
        '''Logs format [text/json].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#output_format GatewayLogForwardingGoogleChronicle#output_format}
        '''
        result = self._values.get("output_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_interval(self) -> typing.Optional[builtins.str]:
        '''Pull interval in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#pull_interval GatewayLogForwardingGoogleChronicle#pull_interval}
        '''
        result = self._values.get("pull_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Google chronicle region [eu_multi_region/london/us_multi_region/singapore/tel_aviv].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_google_chronicle#region GatewayLogForwardingGoogleChronicle#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayLogForwardingGoogleChronicleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayLogForwardingGoogleChronicle",
    "GatewayLogForwardingGoogleChronicleConfig",
]

publication.publish()

def _typecheckingstub__b4a81f0594179a44b1daadaa72c5e2e62572dd25678e3e81109883efe9c922ea(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    customer_id: typing.Optional[builtins.str] = None,
    enable: typing.Optional[builtins.str] = None,
    gcp_key: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    log_type: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__969b00b499eadf166a430c67d953f007ee5212e5b33166bf3adad2d4c2cf2132(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6f952b44f1911233782ca2e0ab014cf01f36dea827eaae7fb8b2f8beaf403ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32814baee0c067fabfc5f3bcc317d9adbbdc10b3231fbf19fe2232b5ab9aaa91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6f5f83202def55a8346e7498f53cbd5e8904e22c6b538e5f0ab73f2922b7a73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d69c12cb9dc0ada58b0a4406cea3272975993398d6e49cf74a60ffeb0afdb26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f35cd1ff7d15b9b0508afefb3accac415cc0a5fc7dc1aa08055385ed2e6dcf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__736f2d5b9dcfc24dd10a427aae30165cab9ea69b53964a5e014f2807ed21a29d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d786efe0a46f4c11184dfa72fa7acbbb122ee4918ffcdbaa252687a4643097c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25771fe1b1c1aeb18531ecefc5897638aa6e9553093ebe0b4f14682de17f7667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c07c911bb86202fa659b0b8f5eb01ffecb7f33116674be3d0ae9be12fdefb06(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    customer_id: typing.Optional[builtins.str] = None,
    enable: typing.Optional[builtins.str] = None,
    gcp_key: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    log_type: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
