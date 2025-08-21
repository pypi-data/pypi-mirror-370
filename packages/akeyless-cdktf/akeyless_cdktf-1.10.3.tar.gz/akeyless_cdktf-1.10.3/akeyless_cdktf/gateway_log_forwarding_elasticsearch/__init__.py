'''
# `akeyless_gateway_log_forwarding_elasticsearch`

Refer to the Terraform Registry for docs: [`akeyless_gateway_log_forwarding_elasticsearch`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch).
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


class GatewayLogForwardingElasticsearch(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayLogForwardingElasticsearch.GatewayLogForwardingElasticsearch",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch akeyless_gateway_log_forwarding_elasticsearch}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        api_key: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        cloud_id: typing.Optional[builtins.str] = None,
        enable: typing.Optional[builtins.str] = None,
        enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        index: typing.Optional[builtins.str] = None,
        nodes: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        server_type: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch akeyless_gateway_log_forwarding_elasticsearch} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_key: Elasticsearch api key relevant only for api_key auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#api_key GatewayLogForwardingElasticsearch#api_key}
        :param auth_type: Elasticsearch auth type [api_key/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#auth_type GatewayLogForwardingElasticsearch#auth_type}
        :param cloud_id: Elasticsearch cloud id relevant only for cloud server-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#cloud_id GatewayLogForwardingElasticsearch#cloud_id}
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#enable GatewayLogForwardingElasticsearch#enable}
        :param enable_tls: Enable tls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#enable_tls GatewayLogForwardingElasticsearch#enable_tls}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#id GatewayLogForwardingElasticsearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Elasticsearch index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#index GatewayLogForwardingElasticsearch#index}
        :param nodes: Elasticsearch nodes relevant only for nodes server-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#nodes GatewayLogForwardingElasticsearch#nodes}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#output_format GatewayLogForwardingElasticsearch#output_format}
        :param password: Elasticsearch password relevant only for password auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#password GatewayLogForwardingElasticsearch#password}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#pull_interval GatewayLogForwardingElasticsearch#pull_interval}
        :param server_type: Elasticsearch server type [nodes/cloud]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#server_type GatewayLogForwardingElasticsearch#server_type}
        :param tls_certificate: Elasticsearch tls certificate (PEM format) in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#tls_certificate GatewayLogForwardingElasticsearch#tls_certificate}
        :param user_name: Elasticsearch user name relevant only for password auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#user_name GatewayLogForwardingElasticsearch#user_name}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3279fd001c58c0e972c2239b17bd3c74910956a09de0cdf6daaf99f67026ceb3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayLogForwardingElasticsearchConfig(
            api_key=api_key,
            auth_type=auth_type,
            cloud_id=cloud_id,
            enable=enable,
            enable_tls=enable_tls,
            id=id,
            index=index,
            nodes=nodes,
            output_format=output_format,
            password=password,
            pull_interval=pull_interval,
            server_type=server_type,
            tls_certificate=tls_certificate,
            user_name=user_name,
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
        '''Generates CDKTF code for importing a GatewayLogForwardingElasticsearch resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayLogForwardingElasticsearch to import.
        :param import_from_id: The id of the existing GatewayLogForwardingElasticsearch that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayLogForwardingElasticsearch to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55abc202cbf140fff8c020bae57535087063118a8a32f828535a4babea65ac7c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetAuthType")
    def reset_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthType", []))

    @jsii.member(jsii_name="resetCloudId")
    def reset_cloud_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudId", []))

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

    @jsii.member(jsii_name="resetNodes")
    def reset_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodes", []))

    @jsii.member(jsii_name="resetOutputFormat")
    def reset_output_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFormat", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetPullInterval")
    def reset_pull_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullInterval", []))

    @jsii.member(jsii_name="resetServerType")
    def reset_server_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerType", []))

    @jsii.member(jsii_name="resetTlsCertificate")
    def reset_tls_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCertificate", []))

    @jsii.member(jsii_name="resetUserName")
    def reset_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserName", []))

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
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="authTypeInput")
    def auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudIdInput")
    def cloud_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudIdInput"))

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
    @jsii.member(jsii_name="nodesInput")
    def nodes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodesInput"))

    @builtins.property
    @jsii.member(jsii_name="outputFormatInput")
    def output_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="pullIntervalInput")
    def pull_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="serverTypeInput")
    def server_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCertificateInput")
    def tls_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7911605af485e99b2c9843c065fa88dfc8d2dac2b51556b8539a466f2c1c2bbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value)

    @builtins.property
    @jsii.member(jsii_name="authType")
    def auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authType"))

    @auth_type.setter
    def auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3d8bc960bfb5d78e368fca1968aaafd60da221d3f11b6b3c85534561a6f94a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authType", value)

    @builtins.property
    @jsii.member(jsii_name="cloudId")
    def cloud_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudId"))

    @cloud_id.setter
    def cloud_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23bff6501922895e3150497b8c113a9fcb97c8bd9e157c060c2d847460d9f6e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudId", value)

    @builtins.property
    @jsii.member(jsii_name="enable")
    def enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enable"))

    @enable.setter
    def enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9479b9a802598f515a303fcfd1e84650d41c81f2c6730a34084dba00bbdd38ba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__67f630d88abc61aa0daa214d6ec2eb970f6bef5dbfcbe4ec72a4c4303aa2c9f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableTls", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c8b07a6fa9ddf50725b3fb8bf9a71c5a6f28800a17bb056966b80cac9bfe3e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="index")
    def index(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "index"))

    @index.setter
    def index(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6970d75b55987cfc1adb8508f05e48cfab9dca2464241578fdcfd79ae1346036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "index", value)

    @builtins.property
    @jsii.member(jsii_name="nodes")
    def nodes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodes"))

    @nodes.setter
    def nodes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75e3fe4a5b2a5a40842a9b4f1f548367be0dadc845e1535cd7569772a6fbcd76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodes", value)

    @builtins.property
    @jsii.member(jsii_name="outputFormat")
    def output_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFormat"))

    @output_format.setter
    def output_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc3e2db18295e5b7a3024349e47fa6f1428431a42a78102f60dda7d661e25d87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "outputFormat", value)

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a53de760d7b4822650c78e521953e1d59cc719bfdf96c833508c0da76d7b089)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property
    @jsii.member(jsii_name="pullInterval")
    def pull_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullInterval"))

    @pull_interval.setter
    def pull_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62e015925bd63ec0290e19b1f58253f583ea7c6c1645b4f4f9cfb2bd62234e4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pullInterval", value)

    @builtins.property
    @jsii.member(jsii_name="serverType")
    def server_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverType"))

    @server_type.setter
    def server_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a952c517e8350ef9432a70b770caa10038eb6271ef35ef1ae99b5f0382a0cc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverType", value)

    @builtins.property
    @jsii.member(jsii_name="tlsCertificate")
    def tls_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCertificate"))

    @tls_certificate.setter
    def tls_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38167985099ba8fdfb13858a4d4dfa1f20bd0a66d9f487be85b7980769f0c3c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e90d1b484d48f51575de139b274afea046480df31265be2696ee8b1a0c60fe1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayLogForwardingElasticsearch.GatewayLogForwardingElasticsearchConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "api_key": "apiKey",
        "auth_type": "authType",
        "cloud_id": "cloudId",
        "enable": "enable",
        "enable_tls": "enableTls",
        "id": "id",
        "index": "index",
        "nodes": "nodes",
        "output_format": "outputFormat",
        "password": "password",
        "pull_interval": "pullInterval",
        "server_type": "serverType",
        "tls_certificate": "tlsCertificate",
        "user_name": "userName",
    },
)
class GatewayLogForwardingElasticsearchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        api_key: typing.Optional[builtins.str] = None,
        auth_type: typing.Optional[builtins.str] = None,
        cloud_id: typing.Optional[builtins.str] = None,
        enable: typing.Optional[builtins.str] = None,
        enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        index: typing.Optional[builtins.str] = None,
        nodes: typing.Optional[builtins.str] = None,
        output_format: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        pull_interval: typing.Optional[builtins.str] = None,
        server_type: typing.Optional[builtins.str] = None,
        tls_certificate: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param api_key: Elasticsearch api key relevant only for api_key auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#api_key GatewayLogForwardingElasticsearch#api_key}
        :param auth_type: Elasticsearch auth type [api_key/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#auth_type GatewayLogForwardingElasticsearch#auth_type}
        :param cloud_id: Elasticsearch cloud id relevant only for cloud server-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#cloud_id GatewayLogForwardingElasticsearch#cloud_id}
        :param enable: Enable Log Forwarding [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#enable GatewayLogForwardingElasticsearch#enable}
        :param enable_tls: Enable tls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#enable_tls GatewayLogForwardingElasticsearch#enable_tls}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#id GatewayLogForwardingElasticsearch#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param index: Elasticsearch index. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#index GatewayLogForwardingElasticsearch#index}
        :param nodes: Elasticsearch nodes relevant only for nodes server-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#nodes GatewayLogForwardingElasticsearch#nodes}
        :param output_format: Logs format [text/json]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#output_format GatewayLogForwardingElasticsearch#output_format}
        :param password: Elasticsearch password relevant only for password auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#password GatewayLogForwardingElasticsearch#password}
        :param pull_interval: Pull interval in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#pull_interval GatewayLogForwardingElasticsearch#pull_interval}
        :param server_type: Elasticsearch server type [nodes/cloud]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#server_type GatewayLogForwardingElasticsearch#server_type}
        :param tls_certificate: Elasticsearch tls certificate (PEM format) in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#tls_certificate GatewayLogForwardingElasticsearch#tls_certificate}
        :param user_name: Elasticsearch user name relevant only for password auth-type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#user_name GatewayLogForwardingElasticsearch#user_name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbe82974128cd0ae9e8245029cee2e75ff5e1150353476a740ce9c5e37d213d5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument auth_type", value=auth_type, expected_type=type_hints["auth_type"])
            check_type(argname="argument cloud_id", value=cloud_id, expected_type=type_hints["cloud_id"])
            check_type(argname="argument enable", value=enable, expected_type=type_hints["enable"])
            check_type(argname="argument enable_tls", value=enable_tls, expected_type=type_hints["enable_tls"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
            check_type(argname="argument nodes", value=nodes, expected_type=type_hints["nodes"])
            check_type(argname="argument output_format", value=output_format, expected_type=type_hints["output_format"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument pull_interval", value=pull_interval, expected_type=type_hints["pull_interval"])
            check_type(argname="argument server_type", value=server_type, expected_type=type_hints["server_type"])
            check_type(argname="argument tls_certificate", value=tls_certificate, expected_type=type_hints["tls_certificate"])
            check_type(argname="argument user_name", value=user_name, expected_type=type_hints["user_name"])
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
        if api_key is not None:
            self._values["api_key"] = api_key
        if auth_type is not None:
            self._values["auth_type"] = auth_type
        if cloud_id is not None:
            self._values["cloud_id"] = cloud_id
        if enable is not None:
            self._values["enable"] = enable
        if enable_tls is not None:
            self._values["enable_tls"] = enable_tls
        if id is not None:
            self._values["id"] = id
        if index is not None:
            self._values["index"] = index
        if nodes is not None:
            self._values["nodes"] = nodes
        if output_format is not None:
            self._values["output_format"] = output_format
        if password is not None:
            self._values["password"] = password
        if pull_interval is not None:
            self._values["pull_interval"] = pull_interval
        if server_type is not None:
            self._values["server_type"] = server_type
        if tls_certificate is not None:
            self._values["tls_certificate"] = tls_certificate
        if user_name is not None:
            self._values["user_name"] = user_name

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
    def api_key(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch api key relevant only for api_key auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#api_key GatewayLogForwardingElasticsearch#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_type(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch auth type [api_key/password].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#auth_type GatewayLogForwardingElasticsearch#auth_type}
        '''
        result = self._values.get("auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_id(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch cloud id relevant only for cloud server-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#cloud_id GatewayLogForwardingElasticsearch#cloud_id}
        '''
        result = self._values.get("cloud_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable(self) -> typing.Optional[builtins.str]:
        '''Enable Log Forwarding [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#enable GatewayLogForwardingElasticsearch#enable}
        '''
        result = self._values.get("enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_tls(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable tls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#enable_tls GatewayLogForwardingElasticsearch#enable_tls}
        '''
        result = self._values.get("enable_tls")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#id GatewayLogForwardingElasticsearch#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch index.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#index GatewayLogForwardingElasticsearch#index}
        '''
        result = self._values.get("index")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nodes(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch nodes relevant only for nodes server-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#nodes GatewayLogForwardingElasticsearch#nodes}
        '''
        result = self._values.get("nodes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_format(self) -> typing.Optional[builtins.str]:
        '''Logs format [text/json].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#output_format GatewayLogForwardingElasticsearch#output_format}
        '''
        result = self._values.get("output_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch password relevant only for password auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#password GatewayLogForwardingElasticsearch#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_interval(self) -> typing.Optional[builtins.str]:
        '''Pull interval in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#pull_interval GatewayLogForwardingElasticsearch#pull_interval}
        '''
        result = self._values.get("pull_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_type(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch server type [nodes/cloud].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#server_type GatewayLogForwardingElasticsearch#server_type}
        '''
        result = self._values.get("server_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_certificate(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch tls certificate (PEM format) in a Base64 format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#tls_certificate GatewayLogForwardingElasticsearch#tls_certificate}
        '''
        result = self._values.get("tls_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''Elasticsearch user name relevant only for password auth-type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_log_forwarding_elasticsearch#user_name GatewayLogForwardingElasticsearch#user_name}
        '''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayLogForwardingElasticsearchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayLogForwardingElasticsearch",
    "GatewayLogForwardingElasticsearchConfig",
]

publication.publish()

def _typecheckingstub__3279fd001c58c0e972c2239b17bd3c74910956a09de0cdf6daaf99f67026ceb3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    api_key: typing.Optional[builtins.str] = None,
    auth_type: typing.Optional[builtins.str] = None,
    cloud_id: typing.Optional[builtins.str] = None,
    enable: typing.Optional[builtins.str] = None,
    enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    index: typing.Optional[builtins.str] = None,
    nodes: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    server_type: typing.Optional[builtins.str] = None,
    tls_certificate: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__55abc202cbf140fff8c020bae57535087063118a8a32f828535a4babea65ac7c(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7911605af485e99b2c9843c065fa88dfc8d2dac2b51556b8539a466f2c1c2bbf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3d8bc960bfb5d78e368fca1968aaafd60da221d3f11b6b3c85534561a6f94a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23bff6501922895e3150497b8c113a9fcb97c8bd9e157c060c2d847460d9f6e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9479b9a802598f515a303fcfd1e84650d41c81f2c6730a34084dba00bbdd38ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67f630d88abc61aa0daa214d6ec2eb970f6bef5dbfcbe4ec72a4c4303aa2c9f3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c8b07a6fa9ddf50725b3fb8bf9a71c5a6f28800a17bb056966b80cac9bfe3e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6970d75b55987cfc1adb8508f05e48cfab9dca2464241578fdcfd79ae1346036(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75e3fe4a5b2a5a40842a9b4f1f548367be0dadc845e1535cd7569772a6fbcd76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc3e2db18295e5b7a3024349e47fa6f1428431a42a78102f60dda7d661e25d87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a53de760d7b4822650c78e521953e1d59cc719bfdf96c833508c0da76d7b089(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62e015925bd63ec0290e19b1f58253f583ea7c6c1645b4f4f9cfb2bd62234e4b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a952c517e8350ef9432a70b770caa10038eb6271ef35ef1ae99b5f0382a0cc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38167985099ba8fdfb13858a4d4dfa1f20bd0a66d9f487be85b7980769f0c3c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e90d1b484d48f51575de139b274afea046480df31265be2696ee8b1a0c60fe1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbe82974128cd0ae9e8245029cee2e75ff5e1150353476a740ce9c5e37d213d5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key: typing.Optional[builtins.str] = None,
    auth_type: typing.Optional[builtins.str] = None,
    cloud_id: typing.Optional[builtins.str] = None,
    enable: typing.Optional[builtins.str] = None,
    enable_tls: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    index: typing.Optional[builtins.str] = None,
    nodes: typing.Optional[builtins.str] = None,
    output_format: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    pull_interval: typing.Optional[builtins.str] = None,
    server_type: typing.Optional[builtins.str] = None,
    tls_certificate: typing.Optional[builtins.str] = None,
    user_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
