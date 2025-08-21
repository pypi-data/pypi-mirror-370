'''
# `akeyless_gateway_log_forwarding_syslog`

Refer to the Terraform Registry for docs: [`akeyless_gateway_log_forwarding_syslog`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog).
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


class GatewayLogForwardingSyslog(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayLogForwardingSyslog.GatewayLogForwardingSyslog",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog akeyless_gateway_log_forwarding_syslog}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        enable: typing.Optional[builtins.str] = None,
        enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        formatter: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        network: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        target_tag: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog akeyless_gateway_log_forwarding_syslog} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#enable GatewayLogForwardingSyslog#enable}
        :param enable_tls: Enable tls relevant only for network type TCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#enable_tls GatewayLogForwardingSyslog#enable_tls}
        :param formatter: Syslog formatter [text/cef]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#formatter GatewayLogForwardingSyslog#formatter}
        :param host: Syslog host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#host GatewayLogForwardingSyslog#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#id GatewayLogForwardingSyslog#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network: Syslog network [tcp/udp]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#network GatewayLogForwardingSyslog#network}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#output_format GatewayLogForwardingSyslog#output_format}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#pull_interval GatewayLogForwardingSyslog#pull_interval}
        :param target_tag: Syslog target tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#target_tag GatewayLogForwardingSyslog#target_tag}
        :param tls_certificate: Syslog tls certificate (PEM format) in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#tls_certificate GatewayLogForwardingSyslog#tls_certificate}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03ccda678e08b19335a1525dde35602c29976844e1916d3560685c8d36072e29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayLogForwardingSyslogConfig(
            enable=enable,
            enable_tls=enable_tls,
            formatter=formatter,
            host=host,
            id=id,
            network=network,
            output_format=output_format,
            pull_interval=pull_interval,
            target_tag=target_tag,
            tls_certificate=tls_certificate,
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
        '''Generates CDKTF code for importing a GatewayLogForwardingSyslog resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayLogForwardingSyslog to import.
        :param import_from_id: The id of the existing GatewayLogForwardingSyslog that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayLogForwardingSyslog to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6675584eafc4a20c4758d656e90fe7dc8b51e3c81e2ba98d0a2a3b179b0f3cb8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetEnable")
    def reset_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnable", []))

    @jsii.member(jsii_name="resetEnableTls")
    def reset_enable_tls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableTls", []))

    @jsii.member(jsii_name="resetFormatter")
    def reset_formatter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormatter", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetOutputFormat")
    def reset_output_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFormat", []))

    @jsii.member(jsii_name="resetPullInterval")
    def reset_pull_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullInterval", []))

    @jsii.member(jsii_name="resetTargetTag")
    def reset_target_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetTag", []))

    @jsii.member(jsii_name="resetTlsCertificate")
    def reset_tls_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificate", []))

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
    @jsii.member(jsii_name="enableInput")
    def enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enableInput"))

    @builtins.property
    @jsii.member(jsii_name="enableTlsInput")
    def enable_tls_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableTlsInput"))

    @builtins.property
    @jsii.member(jsii_name="formatterInput")
    def formatter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatterInput"))

    @builtins.property
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="outputFormatInput")
    def output_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="pullIntervalInput")
    def pull_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="targetTagInput")
    def target_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetTagInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateInput")
    def tls_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="enable")
    def enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ec09b1704bdd689604bfbbbb388c7c8f568c0856d3454ef2f8679a60e130ba9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enable", value)

    @builtins.property
    @jsii.member(jsii_name="enableTls")
    def enable_tls(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableTls"))

    @enable_tls.setter
    def enable_tls(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9d5ecb581bf68869fa359d1587ee1433aea33e40dc2137fd60499650e500752)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableTls", value)

    @builtins.property
    @jsii.member(jsii_name="formatter")
    def formatter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "formatter"))

    @formatter.setter
    def formatter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72006e707193dcd43315bce50c094bf5006aef4eb72858c33e3ad61da6102361)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "formatter", value)

    @builtins.property
    @jsii.member(jsii_name="host")
    def host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "host"))

    @host.setter
    def host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da1348df9b8a50443f28d83d73f954ab8088ba42690cc65e5a8641e371cf13a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "host", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9875ebf77ea651f234ff2e84bcdfc6ca0080c139877c8793e282363df0ed0b4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c383f5e4b617875f45feef6cc64a4351ff3fc496ba7e469d4a8906681a1d52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value)

    @builtins.property
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFormat"))

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19678d295132b619e9cfd90b7a97b2c994c9519f87bcb3cf07d65d90c6b8406b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputFormat", value)

    @builtins.property
    @jsii.member(jsii_name="pullInterval")
    def pull_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullInterval"))

    @pull_interval.setter
    def pull_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1e4cb2bbf7aaa8465bdf6af2f78c113809540b918a6434364febd0b8c1c72a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pullInterval", value)

    @builtins.property
    @jsii.member(jsii_name="targetTag")
    def target_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetTag"))

    @target_tag.setter
    def target_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75f42ae2b3bfc2ee51d4627d70c1248d940ba839ca81682256887cc71fbb9f9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetTag", value)

    @builtins.property
    @jsii.member(jsii_name="tlsCertificate")
    def tls_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificate"))

    @tls_certificate.setter
    def tls_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__928b70c3348dfc81ee8fea0e42fbe7d8c4dac6106f78f6d4657de9a09ed6d39c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificate", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayLogForwardingSyslog.GatewayLogForwardingSyslogConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "enable": "enable",
        "enable_tls": "enableTls",
        "formatter": "formatter",
        "host": "host",
        "id": "id",
        "network": "network",
        "output_format": "outputFormat",
        "pull_interval": "pullInterval",
        "target_tag": "targetTag",
        "tls_certificate": "tlsCertificate",
    },
)
class GatewayLogForwardingSyslogConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        enable: typing.Optional[builtins.str] = None,
        enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        formatter: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        network: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        target_tag: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#enable GatewayLogForwardingSyslog#enable}
        :param enable_tls: Enable tls relevant only for network type TCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#enable_tls GatewayLogForwardingSyslog#enable_tls}
        :param formatter: Syslog formatter [text/cef]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#formatter GatewayLogForwardingSyslog#formatter}
        :param host: Syslog host. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#host GatewayLogForwardingSyslog#host}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#id GatewayLogForwardingSyslog#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network: Syslog network [tcp/udp]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#network GatewayLogForwardingSyslog#network}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#output_format GatewayLogForwardingSyslog#output_format}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#pull_interval GatewayLogForwardingSyslog#pull_interval}
        :param target_tag: Syslog target tag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#target_tag GatewayLogForwardingSyslog#target_tag}
        :param tls_certificate: Syslog tls certificate (PEM format) in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#tls_certificate GatewayLogForwardingSyslog#tls_certificate}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bb35b312d3d80526544a1c00978b9d33dce7bdc9d217409748817f53c2291d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument enable", value=enable, expected_type=type_hints["enable"])
            check_type(argname="argument enable_tls", value=enable_tls, expected_type=type_hints["enable_tls"])
            check_type(argname="argument formatter", value=formatter, expected_type=type_hints["formatter"])
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument output_format", value=output_format, expected_type=type_hints["output_format"])
            check_type(argname="argument pull_interval", value=pull_interval, expected_type=type_hints["pull_interval"])
            check_type(argname="argument target_tag", value=target_tag, expected_type=type_hints["target_tag"])
            check_type(argname="argument tls_certificate", value=tls_certificate, expected_type=type_hints["tls_certificate"])
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
        if enable is not None:
            self._values["enable"] = enable
        if enable_tls is not None:
            self._values["enable_tls"] = enable_tls
        if formatter is not None:
            self._values["formatter"] = formatter
        if host is not None:
            self._values["host"] = host
        if id is not None:
            self._values["id"] = id
        if network is not None:
            self._values["network"] = network
        if output_format is not None:
            self._values["output_format"] = output_format
        if pull_interval is not None:
            self._values["pull_interval"] = pull_interval
        if target_tag is not None:
            self._values["target_tag"] = target_tag
        if tls_certificate is not None:
            self._values["tls_certificate"] = tls_certificate

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
    def enable(self) -> typing.Optional[builtins.str]:
        '''Enable Log Forwarding [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#enable GatewayLogForwardingSyslog#enable}
        '''
        result = self._values.get("enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable tls relevant only for network type TCP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#enable_tls GatewayLogForwardingSyslog#enable_tls}
        '''
        result = self._values.get("enable_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def formatter(self) -> typing.Optional[builtins.str]:
        '''Syslog formatter [text/cef].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#formatter GatewayLogForwardingSyslog#formatter}
        '''
        result = self._values.get("formatter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''Syslog host.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#host GatewayLogForwardingSyslog#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#id GatewayLogForwardingSyslog#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(self) -> typing.Optional[builtins.str]:
        '''Syslog network [tcp/udp].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#network GatewayLogForwardingSyslog#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_format(self) -> typing.Optional[builtins.str]:
        '''Logs format [text/json].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#output_format GatewayLogForwardingSyslog#output_format}
        '''
        result = self._values.get("output_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_interval(self) -> typing.Optional[builtins.str]:
        '''Pull interval in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#pull_interval GatewayLogForwardingSyslog#pull_interval}
        '''
        result = self._values.get("pull_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_tag(self) -> typing.Optional[builtins.str]:
        '''Syslog target tag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#target_tag GatewayLogForwardingSyslog#target_tag}
        '''
        result = self._values.get("target_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate(self) -> typing.Optional[builtins.str]:
        '''Syslog tls certificate (PEM format) in a Base64 format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_syslog#tls_certificate GatewayLogForwardingSyslog#tls_certificate}
        '''
        result = self._values.get("tls_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayLogForwardingSyslogConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayLogForwardingSyslog",
    "GatewayLogForwardingSyslogConfig",
]

publication.publish()

def _typecheckingstub__03ccda678e08b19335a1525dde35602c29976844e1916d3560685c8d36072e29(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    enable: typing.Optional[builtins.str] = None,
    enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    formatter: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    network: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    target_tag: typing.Optional[builtins.str] = None,
    tls_certificate: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6675584eafc4a20c4758d656e90fe7dc8b51e3c81e2ba98d0a2a3b179b0f3cb8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ec09b1704bdd689604bfbbbb388c7c8f568c0856d3454ef2f8679a60e130ba9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9d5ecb581bf68869fa359d1587ee1433aea33e40dc2137fd60499650e500752(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72006e707193dcd43315bce50c094bf5006aef4eb72858c33e3ad61da6102361(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da1348df9b8a50443f28d83d73f954ab8088ba42690cc65e5a8641e371cf13a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9875ebf77ea651f234ff2e84bcdfc6ca0080c139877c8793e282363df0ed0b4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c383f5e4b617875f45feef6cc64a4351ff3fc496ba7e469d4a8906681a1d52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19678d295132b619e9cfd90b7a97b2c994c9519f87bcb3cf07d65d90c6b8406b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1e4cb2bbf7aaa8465bdf6af2f78c113809540b918a6434364febd0b8c1c72a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75f42ae2b3bfc2ee51d4627d70c1248d940ba839ca81682256887cc71fbb9f9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__928b70c3348dfc81ee8fea0e42fbe7d8c4dac6106f78f6d4657de9a09ed6d39c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bb35b312d3d80526544a1c00978b9d33dce7bdc9d217409748817f53c2291d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    enable: typing.Optional[builtins.str] = None,
    enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    formatter: typing.Optional[builtins.str] = None,
    host: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    network: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    target_tag: typing.Optional[builtins.str] = None,
    tls_certificate: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
