'''
# `akeyless_gateway_log_forwarding_splunk`

Refer to the Terraform Registry for docs: [`akeyless_gateway_log_forwarding_splunk`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk).
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


class GatewayLogForwardingSplunk(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayLogForwardingSplunk.GatewayLogForwardingSplunk",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk akeyless_gateway_log_forwarding_splunk}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        enable: typing.Optional[builtins.str] = None,
        enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        index: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        source_type: typing.Optional[builtins.str] = None,
        splunk_token: typing.Optional[builtins.str] = None,
        splunk_url: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk akeyless_gateway_log_forwarding_splunk} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#enable GatewayLogForwardingSplunk#enable}
        :param enable_tls: Enable tls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#enable_tls GatewayLogForwardingSplunk#enable_tls}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#id GatewayLogForwardingSplunk#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Splunk index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#index GatewayLogForwardingSplunk#index}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#output_format GatewayLogForwardingSplunk#output_format}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#pull_interval GatewayLogForwardingSplunk#pull_interval}
        :param source: Splunk source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#source GatewayLogForwardingSplunk#source}
        :param source_type: Splunk source type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#source_type GatewayLogForwardingSplunk#source_type}
        :param splunk_token: Splunk token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#splunk_token GatewayLogForwardingSplunk#splunk_token}
        :param splunk_url: Splunk server URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#splunk_url GatewayLogForwardingSplunk#splunk_url}
        :param tls_certificate: Splunk tls certificate (PEM format) in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#tls_certificate GatewayLogForwardingSplunk#tls_certificate}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__255532094f9335105b03c005705bfc57f8e0847ae32df45a7d5bdbbda5f23cf5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayLogForwardingSplunkConfig(
            enable=enable,
            enable_tls=enable_tls,
            id=id,
            index=index,
            output_format=output_format,
            pull_interval=pull_interval,
            source=source,
            source_type=source_type,
            splunk_token=splunk_token,
            splunk_url=splunk_url,
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
        '''Generates CDKTF code for importing a GatewayLogForwardingSplunk resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayLogForwardingSplunk to import.
        :param import_from_id: The id of the existing GatewayLogForwardingSplunk that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayLogForwardingSplunk to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72d0fe0282cd668ca812dff67f24bb5396ef353b95ad7a087079be526848e5ae)
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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIndex")
    def reset_index(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndex", []))

    @jsii.member(jsii_name="resetOutputFormat")
    def reset_output_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFormat", []))

    @jsii.member(jsii_name="resetPullInterval")
    def reset_pull_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullInterval", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourceType")
    def reset_source_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceType", []))

    @jsii.member(jsii_name="resetSplunkToken")
    def reset_splunk_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSplunkToken", []))

    @jsii.member(jsii_name="resetSplunkUrl")
    def reset_splunk_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSplunkUrl", []))

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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="indexInput")
    def index_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexInput"))

    @builtins.property
    @jsii.member(jsii_name="outputFormatInput")
    def output_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="pullIntervalInput")
    def pull_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceTypeInput")
    def source_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="splunkTokenInput")
    def splunk_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "splunkTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="splunkUrlInput")
    def splunk_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "splunkUrlInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__f3aaac26ea42c50f558e84544b92ae6d53b3562c1ff27932d6de984a53ac6dea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2cb033afe183b96f727d0fbd7dfc8df2f4ac2e3a98a19300adcb130d2d95ed8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableTls", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e651836616f9737f097bdffcc67c0a0f70073283b6a913bc33f0fb8b53ce810f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="index")
    def index(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "index"))

    @index.setter
    def index(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0a75e16ada605f467db0ae0f89afd030f4f9916e087ebdf4f52917c97849409)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "index", value)

    @builtins.property
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFormat"))

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0ab8269dcea261b193eae43234626b4599b390cd53b6930f3cf001b831888e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputFormat", value)

    @builtins.property
    @jsii.member(jsii_name="pullInterval")
    def pull_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullInterval"))

    @pull_interval.setter
    def pull_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e43aded99daa17a63cf4a3d57a73d606149fb30956c1db0026a116a0ad7c5a11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pullInterval", value)

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @source.setter
    def source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2e796a64430c2811ca401bd1e1da619b11d86a49505d8b71304cc41545e395b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "source", value)

    @builtins.property
    @jsii.member(jsii_name="sourceType")
    def source_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceType"))

    @source_type.setter
    def source_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaf01dff0125a1170e1795ae49e72dec2057c021219a1d2cd73be0b123501cb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceType", value)

    @builtins.property
    @jsii.member(jsii_name="splunkToken")
    def splunk_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "splunkToken"))

    @splunk_token.setter
    def splunk_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7afbf0691c9c3412fc763f068b1c6fe8f89ce193d12d12b59d2d388cf7fd755)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "splunkToken", value)

    @builtins.property
    @jsii.member(jsii_name="splunkUrl")
    def splunk_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "splunkUrl"))

    @splunk_url.setter
    def splunk_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3e46a9b04c41bf06535f9cf09db1f21e802210af07a549dc7e032b762156093)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "splunkUrl", value)

    @builtins.property
    @jsii.member(jsii_name="tlsCertificate")
    def tls_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificate"))

    @tls_certificate.setter
    def tls_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__987dd4dd1d1a73327fa3b5e47079bffe184277ad96278e1e892363bc491b696b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificate", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayLogForwardingSplunk.GatewayLogForwardingSplunkConfig",
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
        "id": "id",
        "index": "index",
        "output_format": "outputFormat",
        "pull_interval": "pullInterval",
        "source": "source",
        "source_type": "sourceType",
        "splunk_token": "splunkToken",
        "splunk_url": "splunkUrl",
        "tls_certificate": "tlsCertificate",
    },
)
class GatewayLogForwardingSplunkConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        index: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        source: typing.Optional[builtins.str] = None,
        source_type: typing.Optional[builtins.str] = None,
        splunk_token: typing.Optional[builtins.str] = None,
        splunk_url: typing.Optional[builtins.str] = None,
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
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#enable GatewayLogForwardingSplunk#enable}
        :param enable_tls: Enable tls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#enable_tls GatewayLogForwardingSplunk#enable_tls}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#id GatewayLogForwardingSplunk#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Splunk index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#index GatewayLogForwardingSplunk#index}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#output_format GatewayLogForwardingSplunk#output_format}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#pull_interval GatewayLogForwardingSplunk#pull_interval}
        :param source: Splunk source. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#source GatewayLogForwardingSplunk#source}
        :param source_type: Splunk source type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#source_type GatewayLogForwardingSplunk#source_type}
        :param splunk_token: Splunk token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#splunk_token GatewayLogForwardingSplunk#splunk_token}
        :param splunk_url: Splunk server URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#splunk_url GatewayLogForwardingSplunk#splunk_url}
        :param tls_certificate: Splunk tls certificate (PEM format) in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#tls_certificate GatewayLogForwardingSplunk#tls_certificate}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf1094e33a7f76f49b9666672d8467324ff75d218f62521c2026568ed259dea)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument enable", value=enable, expected_type=type_hints["enable"])
            check_type(argname="argument enable_tls", value=enable_tls, expected_type=type_hints["enable_tls"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
            check_type(argname="argument output_format", value=output_format, expected_type=type_hints["output_format"])
            check_type(argname="argument pull_interval", value=pull_interval, expected_type=type_hints["pull_interval"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument source_type", value=source_type, expected_type=type_hints["source_type"])
            check_type(argname="argument splunk_token", value=splunk_token, expected_type=type_hints["splunk_token"])
            check_type(argname="argument splunk_url", value=splunk_url, expected_type=type_hints["splunk_url"])
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
        if id is not None:
            self._values["id"] = id
        if index is not None:
            self._values["index"] = index
        if output_format is not None:
            self._values["output_format"] = output_format
        if pull_interval is not None:
            self._values["pull_interval"] = pull_interval
        if source is not None:
            self._values["source"] = source
        if source_type is not None:
            self._values["source_type"] = source_type
        if splunk_token is not None:
            self._values["splunk_token"] = splunk_token
        if splunk_url is not None:
            self._values["splunk_url"] = splunk_url
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#enable GatewayLogForwardingSplunk#enable}
        '''
        result = self._values.get("enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable tls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#enable_tls GatewayLogForwardingSplunk#enable_tls}
        '''
        result = self._values.get("enable_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#id GatewayLogForwardingSplunk#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index(self) -> typing.Optional[builtins.str]:
        '''Splunk index.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#index GatewayLogForwardingSplunk#index}
        '''
        result = self._values.get("index")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_format(self) -> typing.Optional[builtins.str]:
        '''Logs format [text/json].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#output_format GatewayLogForwardingSplunk#output_format}
        '''
        result = self._values.get("output_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_interval(self) -> typing.Optional[builtins.str]:
        '''Pull interval in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#pull_interval GatewayLogForwardingSplunk#pull_interval}
        '''
        result = self._values.get("pull_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Splunk source.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#source GatewayLogForwardingSplunk#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_type(self) -> typing.Optional[builtins.str]:
        '''Splunk source type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#source_type GatewayLogForwardingSplunk#source_type}
        '''
        result = self._values.get("source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def splunk_token(self) -> typing.Optional[builtins.str]:
        '''Splunk token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#splunk_token GatewayLogForwardingSplunk#splunk_token}
        '''
        result = self._values.get("splunk_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def splunk_url(self) -> typing.Optional[builtins.str]:
        '''Splunk server URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#splunk_url GatewayLogForwardingSplunk#splunk_url}
        '''
        result = self._values.get("splunk_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate(self) -> typing.Optional[builtins.str]:
        '''Splunk tls certificate (PEM format) in a Base64 format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_splunk#tls_certificate GatewayLogForwardingSplunk#tls_certificate}
        '''
        result = self._values.get("tls_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayLogForwardingSplunkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayLogForwardingSplunk",
    "GatewayLogForwardingSplunkConfig",
]

publication.publish()

def _typecheckingstub__255532094f9335105b03c005705bfc57f8e0847ae32df45a7d5bdbbda5f23cf5(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    enable: typing.Optional[builtins.str] = None,
    enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    index: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    source: typing.Optional[builtins.str] = None,
    source_type: typing.Optional[builtins.str] = None,
    splunk_token: typing.Optional[builtins.str] = None,
    splunk_url: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__72d0fe0282cd668ca812dff67f24bb5396ef353b95ad7a087079be526848e5ae(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3aaac26ea42c50f558e84544b92ae6d53b3562c1ff27932d6de984a53ac6dea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb033afe183b96f727d0fbd7dfc8df2f4ac2e3a98a19300adcb130d2d95ed8e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e651836616f9737f097bdffcc67c0a0f70073283b6a913bc33f0fb8b53ce810f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a75e16ada605f467db0ae0f89afd030f4f9916e087ebdf4f52917c97849409(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0ab8269dcea261b193eae43234626b4599b390cd53b6930f3cf001b831888e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e43aded99daa17a63cf4a3d57a73d606149fb30956c1db0026a116a0ad7c5a11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2e796a64430c2811ca401bd1e1da619b11d86a49505d8b71304cc41545e395b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaf01dff0125a1170e1795ae49e72dec2057c021219a1d2cd73be0b123501cb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7afbf0691c9c3412fc763f068b1c6fe8f89ce193d12d12b59d2d388cf7fd755(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3e46a9b04c41bf06535f9cf09db1f21e802210af07a549dc7e032b762156093(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__987dd4dd1d1a73327fa3b5e47079bffe184277ad96278e1e892363bc491b696b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf1094e33a7f76f49b9666672d8467324ff75d218f62521c2026568ed259dea(
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
    id: typing.Optional[builtins.str] = None,
    index: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    source: typing.Optional[builtins.str] = None,
    source_type: typing.Optional[builtins.str] = None,
    splunk_token: typing.Optional[builtins.str] = None,
    splunk_url: typing.Optional[builtins.str] = None,
    tls_certificate: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
