'''
# `akeyless_gateway_remote_access`

Refer to the Terraform Registry for docs: [`akeyless_gateway_remote_access`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access).
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


class GatewayRemoteAccess(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayRemoteAccess.GatewayRemoteAccess",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access akeyless_gateway_remote_access}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        allowed_urls: typing.Optional[builtins.str] = None,
        hide_session_recording: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kexalgs: typing.Optional[builtins.str] = None,
        keyboard_layout: typing.Optional[builtins.str] = None,
        legacy_ssh_algorithm: typing.Optional[builtins.str] = None,
        rdp_target_configuration: typing.Optional[builtins.str] = None,
        ssh_target_configuration: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access akeyless_gateway_remote_access} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_urls: List of valid URLs to redirect from the Portal back to the remote access server (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#allowed_urls GatewayRemoteAccess#allowed_urls}
        :param hide_session_recording: Specifies whether to show/hide if the session is currently recorded [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#hide_session_recording GatewayRemoteAccess#hide_session_recording}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#id GatewayRemoteAccess#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kexalgs: Decide which algorithm will be used as part of the SSH initial hand-shake process. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#kexalgs GatewayRemoteAccess#kexalgs}
        :param keyboard_layout: Enable support for additional keyboard layouts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#keyboard_layout GatewayRemoteAccess#keyboard_layout}
        :param legacy_ssh_algorithm: Signs SSH certificates using legacy ssh-rsa-cert-01@openssh.com signing algorithm [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#legacy_ssh_algorithm GatewayRemoteAccess#legacy_ssh_algorithm}
        :param rdp_target_configuration: Specify the usernameSubClaim that exists inside the IDP JWT, e.g. email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#rdp_target_configuration GatewayRemoteAccess#rdp_target_configuration}
        :param ssh_target_configuration: Specify the usernameSubClaim that exists inside the IDP JWT, e.g. email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#ssh_target_configuration GatewayRemoteAccess#ssh_target_configuration}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7451310b43537f4af4d8eae60b4a043a14619516f5b567776bbda2e25a2ce73e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayRemoteAccessConfig(
            allowed_urls=allowed_urls,
            hide_session_recording=hide_session_recording,
            id=id,
            kexalgs=kexalgs,
            keyboard_layout=keyboard_layout,
            legacy_ssh_algorithm=legacy_ssh_algorithm,
            rdp_target_configuration=rdp_target_configuration,
            ssh_target_configuration=ssh_target_configuration,
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
        '''Generates CDKTF code for importing a GatewayRemoteAccess resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayRemoteAccess to import.
        :param import_from_id: The id of the existing GatewayRemoteAccess that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayRemoteAccess to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f070a1a40d9b066e85d0ee8f9fa032751c61aae6855fa48ff77c9a8531d81ba3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowedUrls")
    def reset_allowed_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUrls", []))

    @jsii.member(jsii_name="resetHideSessionRecording")
    def reset_hide_session_recording(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHideSessionRecording", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKexalgs")
    def reset_kexalgs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKexalgs", []))

    @jsii.member(jsii_name="resetKeyboardLayout")
    def reset_keyboard_layout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyboardLayout", []))

    @jsii.member(jsii_name="resetLegacySshAlgorithm")
    def reset_legacy_ssh_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLegacySshAlgorithm", []))

    @jsii.member(jsii_name="resetRdpTargetConfiguration")
    def reset_rdp_target_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpTargetConfiguration", []))

    @jsii.member(jsii_name="resetSshTargetConfiguration")
    def reset_ssh_target_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshTargetConfiguration", []))

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
    @jsii.member(jsii_name="allowedUrlsInput")
    def allowed_urls_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedUrlsInput"))

    @builtins.property
    @jsii.member(jsii_name="hideSessionRecordingInput")
    def hide_session_recording_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hideSessionRecordingInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="kexalgsInput")
    def kexalgs_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kexalgsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyboardLayoutInput")
    def keyboard_layout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyboardLayoutInput"))

    @builtins.property
    @jsii.member(jsii_name="legacySshAlgorithmInput")
    def legacy_ssh_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "legacySshAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpTargetConfigurationInput")
    def rdp_target_configuration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpTargetConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="sshTargetConfigurationInput")
    def ssh_target_configuration_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshTargetConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUrls")
    def allowed_urls(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedUrls"))

    @allowed_urls.setter
    def allowed_urls(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f4c3367c89c2274e5877e2556bbe1b6da6b494d12159ef1372145a51b9c0316)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUrls", value)

    @builtins.property
    @jsii.member(jsii_name="hideSessionRecording")
    def hide_session_recording(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hideSessionRecording"))

    @hide_session_recording.setter
    def hide_session_recording(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8954c84cd07d99f2ba620662c20b4d179e0321fce4af2cc8000b7f6114df5009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hideSessionRecording", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__982fe3879a21e90514a797bcbea2e1e4f1cf5e332e5a66945f86d66163639647)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="kexalgs")
    def kexalgs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kexalgs"))

    @kexalgs.setter
    def kexalgs(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f08bd3b950986aff1a9afc0dbe4835442d67bed04fbde8e3c731ae152853723e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kexalgs", value)

    @builtins.property
    @jsii.member(jsii_name="keyboardLayout")
    def keyboard_layout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyboardLayout"))

    @keyboard_layout.setter
    def keyboard_layout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa94ba78d7d2b908a5030e5c1b3b13ac83032f47512dae28db76c418f8df1a83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyboardLayout", value)

    @builtins.property
    @jsii.member(jsii_name="legacySshAlgorithm")
    def legacy_ssh_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "legacySshAlgorithm"))

    @legacy_ssh_algorithm.setter
    def legacy_ssh_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f85f91cf4c87f6bf79da92d82e2076c5bdeb6667ceb39c23401875960c046bdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "legacySshAlgorithm", value)

    @builtins.property
    @jsii.member(jsii_name="rdpTargetConfiguration")
    def rdp_target_configuration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpTargetConfiguration"))

    @rdp_target_configuration.setter
    def rdp_target_configuration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18fd8a32567b494b8672e9e0b2b37e36566df537b7ec2d7866ebf66c4958591a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpTargetConfiguration", value)

    @builtins.property
    @jsii.member(jsii_name="sshTargetConfiguration")
    def ssh_target_configuration(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshTargetConfiguration"))

    @ssh_target_configuration.setter
    def ssh_target_configuration(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb11a1230dc701074fe9a17123d06620c39ef0605d03bfbd9760fc5120af6da0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshTargetConfiguration", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayRemoteAccess.GatewayRemoteAccessConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "allowed_urls": "allowedUrls",
        "hide_session_recording": "hideSessionRecording",
        "id": "id",
        "kexalgs": "kexalgs",
        "keyboard_layout": "keyboardLayout",
        "legacy_ssh_algorithm": "legacySshAlgorithm",
        "rdp_target_configuration": "rdpTargetConfiguration",
        "ssh_target_configuration": "sshTargetConfiguration",
    },
)
class GatewayRemoteAccessConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_urls: typing.Optional[builtins.str] = None,
        hide_session_recording: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        kexalgs: typing.Optional[builtins.str] = None,
        keyboard_layout: typing.Optional[builtins.str] = None,
        legacy_ssh_algorithm: typing.Optional[builtins.str] = None,
        rdp_target_configuration: typing.Optional[builtins.str] = None,
        ssh_target_configuration: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param allowed_urls: List of valid URLs to redirect from the Portal back to the remote access server (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#allowed_urls GatewayRemoteAccess#allowed_urls}
        :param hide_session_recording: Specifies whether to show/hide if the session is currently recorded [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#hide_session_recording GatewayRemoteAccess#hide_session_recording}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#id GatewayRemoteAccess#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param kexalgs: Decide which algorithm will be used as part of the SSH initial hand-shake process. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#kexalgs GatewayRemoteAccess#kexalgs}
        :param keyboard_layout: Enable support for additional keyboard layouts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#keyboard_layout GatewayRemoteAccess#keyboard_layout}
        :param legacy_ssh_algorithm: Signs SSH certificates using legacy ssh-rsa-cert-01@openssh.com signing algorithm [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#legacy_ssh_algorithm GatewayRemoteAccess#legacy_ssh_algorithm}
        :param rdp_target_configuration: Specify the usernameSubClaim that exists inside the IDP JWT, e.g. email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#rdp_target_configuration GatewayRemoteAccess#rdp_target_configuration}
        :param ssh_target_configuration: Specify the usernameSubClaim that exists inside the IDP JWT, e.g. email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#ssh_target_configuration GatewayRemoteAccess#ssh_target_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3055a6c64dc8a9ac618ca5d3f8620345aff11c2017533d6d4414473daac39e0e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument allowed_urls", value=allowed_urls, expected_type=type_hints["allowed_urls"])
            check_type(argname="argument hide_session_recording", value=hide_session_recording, expected_type=type_hints["hide_session_recording"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument kexalgs", value=kexalgs, expected_type=type_hints["kexalgs"])
            check_type(argname="argument keyboard_layout", value=keyboard_layout, expected_type=type_hints["keyboard_layout"])
            check_type(argname="argument legacy_ssh_algorithm", value=legacy_ssh_algorithm, expected_type=type_hints["legacy_ssh_algorithm"])
            check_type(argname="argument rdp_target_configuration", value=rdp_target_configuration, expected_type=type_hints["rdp_target_configuration"])
            check_type(argname="argument ssh_target_configuration", value=ssh_target_configuration, expected_type=type_hints["ssh_target_configuration"])
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
        if allowed_urls is not None:
            self._values["allowed_urls"] = allowed_urls
        if hide_session_recording is not None:
            self._values["hide_session_recording"] = hide_session_recording
        if id is not None:
            self._values["id"] = id
        if kexalgs is not None:
            self._values["kexalgs"] = kexalgs
        if keyboard_layout is not None:
            self._values["keyboard_layout"] = keyboard_layout
        if legacy_ssh_algorithm is not None:
            self._values["legacy_ssh_algorithm"] = legacy_ssh_algorithm
        if rdp_target_configuration is not None:
            self._values["rdp_target_configuration"] = rdp_target_configuration
        if ssh_target_configuration is not None:
            self._values["ssh_target_configuration"] = ssh_target_configuration

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
    def allowed_urls(self) -> typing.Optional[builtins.str]:
        '''List of valid URLs to redirect from the Portal back to the remote access server (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#allowed_urls GatewayRemoteAccess#allowed_urls}
        '''
        result = self._values.get("allowed_urls")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hide_session_recording(self) -> typing.Optional[builtins.str]:
        '''Specifies whether to show/hide if the session is currently recorded [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#hide_session_recording GatewayRemoteAccess#hide_session_recording}
        '''
        result = self._values.get("hide_session_recording")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#id GatewayRemoteAccess#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kexalgs(self) -> typing.Optional[builtins.str]:
        '''Decide which algorithm will be used as part of the SSH initial hand-shake process.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#kexalgs GatewayRemoteAccess#kexalgs}
        '''
        result = self._values.get("kexalgs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def keyboard_layout(self) -> typing.Optional[builtins.str]:
        '''Enable support for additional keyboard layouts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#keyboard_layout GatewayRemoteAccess#keyboard_layout}
        '''
        result = self._values.get("keyboard_layout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def legacy_ssh_algorithm(self) -> typing.Optional[builtins.str]:
        '''Signs SSH certificates using legacy ssh-rsa-cert-01@openssh.com signing algorithm [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#legacy_ssh_algorithm GatewayRemoteAccess#legacy_ssh_algorithm}
        '''
        result = self._values.get("legacy_ssh_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_target_configuration(self) -> typing.Optional[builtins.str]:
        '''Specify the usernameSubClaim that exists inside the IDP JWT, e.g. email.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#rdp_target_configuration GatewayRemoteAccess#rdp_target_configuration}
        '''
        result = self._values.get("rdp_target_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_target_configuration(self) -> typing.Optional[builtins.str]:
        '''Specify the usernameSubClaim that exists inside the IDP JWT, e.g. email.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access#ssh_target_configuration GatewayRemoteAccess#ssh_target_configuration}
        '''
        result = self._values.get("ssh_target_configuration")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayRemoteAccessConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayRemoteAccess",
    "GatewayRemoteAccessConfig",
]

publication.publish()

def _typecheckingstub__7451310b43537f4af4d8eae60b4a043a14619516f5b567776bbda2e25a2ce73e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    allowed_urls: typing.Optional[builtins.str] = None,
    hide_session_recording: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    kexalgs: typing.Optional[builtins.str] = None,
    keyboard_layout: typing.Optional[builtins.str] = None,
    legacy_ssh_algorithm: typing.Optional[builtins.str] = None,
    rdp_target_configuration: typing.Optional[builtins.str] = None,
    ssh_target_configuration: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__f070a1a40d9b066e85d0ee8f9fa032751c61aae6855fa48ff77c9a8531d81ba3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f4c3367c89c2274e5877e2556bbe1b6da6b494d12159ef1372145a51b9c0316(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8954c84cd07d99f2ba620662c20b4d179e0321fce4af2cc8000b7f6114df5009(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__982fe3879a21e90514a797bcbea2e1e4f1cf5e332e5a66945f86d66163639647(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f08bd3b950986aff1a9afc0dbe4835442d67bed04fbde8e3c731ae152853723e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa94ba78d7d2b908a5030e5c1b3b13ac83032f47512dae28db76c418f8df1a83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f85f91cf4c87f6bf79da92d82e2076c5bdeb6667ceb39c23401875960c046bdd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18fd8a32567b494b8672e9e0b2b37e36566df537b7ec2d7866ebf66c4958591a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb11a1230dc701074fe9a17123d06620c39ef0605d03bfbd9760fc5120af6da0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3055a6c64dc8a9ac618ca5d3f8620345aff11c2017533d6d4414473daac39e0e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_urls: typing.Optional[builtins.str] = None,
    hide_session_recording: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    kexalgs: typing.Optional[builtins.str] = None,
    keyboard_layout: typing.Optional[builtins.str] = None,
    legacy_ssh_algorithm: typing.Optional[builtins.str] = None,
    rdp_target_configuration: typing.Optional[builtins.str] = None,
    ssh_target_configuration: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
