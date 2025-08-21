'''
# `data_akeyless_kube_exec_creds`

Refer to the Terraform Registry for docs: [`data_akeyless_kube_exec_creds`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds).
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


class DataAkeylessKubeExecCreds(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessKubeExecCreds.DataAkeylessKubeExecCreds",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds akeyless_kube_exec_creds}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cert_issuer_name: builtins.str,
        alt_names: typing.Optional[builtins.str] = None,
        common_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_data_base64: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds akeyless_kube_exec_creds} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cert_issuer_name: The name of the PKI certificate issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#cert_issuer_name DataAkeylessKubeExecCreds#cert_issuer_name}
        :param alt_names: The Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#alt_names DataAkeylessKubeExecCreds#alt_names}
        :param common_name: The common name to be included in the PKI certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#common_name DataAkeylessKubeExecCreds#common_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#id DataAkeylessKubeExecCreds#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_data_base64: pki key file contents encoded using Base64. If this option is used, the certificate will be printed to stdout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#key_data_base64 DataAkeylessKubeExecCreds#key_data_base64}
        :param uri_sans: The URI Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#uri_sans DataAkeylessKubeExecCreds#uri_sans}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246006fbb3b071e774ba8628256b058d12fc9f483167558a877f1807cd71380f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAkeylessKubeExecCredsConfig(
            cert_issuer_name=cert_issuer_name,
            alt_names=alt_names,
            common_name=common_name,
            id=id,
            key_data_base64=key_data_base64,
            uri_sans=uri_sans,
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
        '''Generates CDKTF code for importing a DataAkeylessKubeExecCreds resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataAkeylessKubeExecCreds to import.
        :param import_from_id: The id of the existing DataAkeylessKubeExecCreds that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataAkeylessKubeExecCreds to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2ec2ca635acbfae10fdd6c4f9b38558996842f28000f330c3297fdf411e0e76)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAltNames")
    def reset_alt_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAltNames", []))

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyDataBase64")
    def reset_key_data_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyDataBase64", []))

    @jsii.member(jsii_name="resetUriSans")
    def reset_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUriSans", []))

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
    @jsii.member(jsii_name="apiVersion")
    def api_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiVersion"))

    @builtins.property
    @jsii.member(jsii_name="clientCertificateData")
    def client_certificate_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientCertificateData"))

    @builtins.property
    @jsii.member(jsii_name="clientKeyData")
    def client_key_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientKeyData"))

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @builtins.property
    @jsii.member(jsii_name="parentCertificateData")
    def parent_certificate_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentCertificateData"))

    @builtins.property
    @jsii.member(jsii_name="altNamesInput")
    def alt_names_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "altNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="certIssuerNameInput")
    def cert_issuer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certIssuerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyDataBase64Input")
    def key_data_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyDataBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="uriSansInput")
    def uri_sans_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="altNames")
    def alt_names(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "altNames"))

    @alt_names.setter
    def alt_names(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1905733059557f26a0380f689133d6ac1dee99bdf60bce33e2e66847563253b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value)

    @builtins.property
    @jsii.member(jsii_name="certIssuerName")
    def cert_issuer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certIssuerName"))

    @cert_issuer_name.setter
    def cert_issuer_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09a8437ec76af49ff82b4ad823ca1122d5dc2876b17fc0d0746c19aa3c273270)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certIssuerName", value)

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23181c4e2933dd8fded43137719308dea6d9acadb452ffa969bc83e923b70b42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b930962bef77f12e2a15a0b78f215608fb4a6215317a0ed1eac16c6fc05b84e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="keyDataBase64")
    def key_data_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyDataBase64"))

    @key_data_base64.setter
    def key_data_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b7f1de4abc255125edc90923bec6e8febc3ee2bcbbbd2a549d50afcbbf47ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyDataBase64", value)

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__235bd29fdc2a5b63d612ba3d25d805c1a76e6bce4bd6e245d3be052daacacc5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessKubeExecCreds.DataAkeylessKubeExecCredsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cert_issuer_name": "certIssuerName",
        "alt_names": "altNames",
        "common_name": "commonName",
        "id": "id",
        "key_data_base64": "keyDataBase64",
        "uri_sans": "uriSans",
    },
)
class DataAkeylessKubeExecCredsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cert_issuer_name: builtins.str,
        alt_names: typing.Optional[builtins.str] = None,
        common_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_data_base64: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cert_issuer_name: The name of the PKI certificate issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#cert_issuer_name DataAkeylessKubeExecCreds#cert_issuer_name}
        :param alt_names: The Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#alt_names DataAkeylessKubeExecCreds#alt_names}
        :param common_name: The common name to be included in the PKI certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#common_name DataAkeylessKubeExecCreds#common_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#id DataAkeylessKubeExecCreds#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_data_base64: pki key file contents encoded using Base64. If this option is used, the certificate will be printed to stdout. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#key_data_base64 DataAkeylessKubeExecCreds#key_data_base64}
        :param uri_sans: The URI Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#uri_sans DataAkeylessKubeExecCreds#uri_sans}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b850b4cb9c9114b1aadcbdff16ec9c47cc92a28939edbcd4152641939d85a10f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cert_issuer_name", value=cert_issuer_name, expected_type=type_hints["cert_issuer_name"])
            check_type(argname="argument alt_names", value=alt_names, expected_type=type_hints["alt_names"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_data_base64", value=key_data_base64, expected_type=type_hints["key_data_base64"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cert_issuer_name": cert_issuer_name,
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
        if alt_names is not None:
            self._values["alt_names"] = alt_names
        if common_name is not None:
            self._values["common_name"] = common_name
        if id is not None:
            self._values["id"] = id
        if key_data_base64 is not None:
            self._values["key_data_base64"] = key_data_base64
        if uri_sans is not None:
            self._values["uri_sans"] = uri_sans

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
    def cert_issuer_name(self) -> builtins.str:
        '''The name of the PKI certificate issuer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#cert_issuer_name DataAkeylessKubeExecCreds#cert_issuer_name}
        '''
        result = self._values.get("cert_issuer_name")
        assert result is not None, "Required property 'cert_issuer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alt_names(self) -> typing.Optional[builtins.str]:
        '''The Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#alt_names DataAkeylessKubeExecCreds#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''The common name to be included in the PKI certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#common_name DataAkeylessKubeExecCreds#common_name}
        '''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#id DataAkeylessKubeExecCreds#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_data_base64(self) -> typing.Optional[builtins.str]:
        '''pki key file contents encoded using Base64. If this option is used, the certificate will be printed to stdout.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#key_data_base64 DataAkeylessKubeExecCreds#key_data_base64}
        '''
        result = self._values.get("key_data_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[builtins.str]:
        '''The URI Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/kube_exec_creds#uri_sans DataAkeylessKubeExecCreds#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessKubeExecCredsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAkeylessKubeExecCreds",
    "DataAkeylessKubeExecCredsConfig",
]

publication.publish()

def _typecheckingstub__246006fbb3b071e774ba8628256b058d12fc9f483167558a877f1807cd71380f(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cert_issuer_name: builtins.str,
    alt_names: typing.Optional[builtins.str] = None,
    common_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_data_base64: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__c2ec2ca635acbfae10fdd6c4f9b38558996842f28000f330c3297fdf411e0e76(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1905733059557f26a0380f689133d6ac1dee99bdf60bce33e2e66847563253b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09a8437ec76af49ff82b4ad823ca1122d5dc2876b17fc0d0746c19aa3c273270(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23181c4e2933dd8fded43137719308dea6d9acadb452ffa969bc83e923b70b42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b930962bef77f12e2a15a0b78f215608fb4a6215317a0ed1eac16c6fc05b84e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b7f1de4abc255125edc90923bec6e8febc3ee2bcbbbd2a549d50afcbbf47ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__235bd29fdc2a5b63d612ba3d25d805c1a76e6bce4bd6e245d3be052daacacc5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b850b4cb9c9114b1aadcbdff16ec9c47cc92a28939edbcd4152641939d85a10f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cert_issuer_name: builtins.str,
    alt_names: typing.Optional[builtins.str] = None,
    common_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_data_base64: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
