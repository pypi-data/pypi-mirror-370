'''
# `data_akeyless_pki_certificate`

Refer to the Terraform Registry for docs: [`data_akeyless_pki_certificate`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate).
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


class DataAkeylessPkiCertificate(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessPkiCertificate.DataAkeylessPkiCertificate",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate akeyless_pki_certificate}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cert_issuer_name: builtins.str,
        alt_names: typing.Optional[builtins.str] = None,
        common_name: typing.Optional[builtins.str] = None,
        csr_data_base64: typing.Optional[builtins.str] = None,
        extended_key_usage: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_data_base64: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
        uri_sans: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate akeyless_pki_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cert_issuer_name: The name of the PKI certificate issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#cert_issuer_name DataAkeylessPkiCertificate#cert_issuer_name}
        :param alt_names: The Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#alt_names DataAkeylessPkiCertificate#alt_names}
        :param common_name: The common name to be included in the PKI certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#common_name DataAkeylessPkiCertificate#common_name}
        :param csr_data_base64: Certificate Signing Request contents encoded in base64 to generate the certificate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#csr_data_base64 DataAkeylessPkiCertificate#csr_data_base64}
        :param extended_key_usage: A comma-separated list of extended key usage requests which will be used for certificate issuance. Supported values: 'clientauth', 'serverauth'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#extended_key_usage DataAkeylessPkiCertificate#extended_key_usage}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#id DataAkeylessPkiCertificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_data_base64: pki key file contents encoded using Base64. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#key_data_base64 DataAkeylessPkiCertificate#key_data_base64}
        :param ttl: Updated certificate lifetime in seconds (must be less than the Certificate Issuer default TTL). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#ttl DataAkeylessPkiCertificate#ttl}
        :param uri_sans: The URI Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#uri_sans DataAkeylessPkiCertificate#uri_sans}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d396b82e29e1c3a9e7a62408dec78502c88f273914b2cdae3d9b68a3f0438bc4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAkeylessPkiCertificateConfig(
            cert_issuer_name=cert_issuer_name,
            alt_names=alt_names,
            common_name=common_name,
            csr_data_base64=csr_data_base64,
            extended_key_usage=extended_key_usage,
            id=id,
            key_data_base64=key_data_base64,
            ttl=ttl,
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
        '''Generates CDKTF code for importing a DataAkeylessPkiCertificate resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataAkeylessPkiCertificate to import.
        :param import_from_id: The id of the existing DataAkeylessPkiCertificate that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataAkeylessPkiCertificate to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a57c367cedf25806a8100d9a730d91f123f6546c8c073a7e2816bc169ef0701)
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

    @jsii.member(jsii_name="resetCsrDataBase64")
    def reset_csr_data_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCsrDataBase64", []))

    @jsii.member(jsii_name="resetExtendedKeyUsage")
    def reset_extended_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtendedKeyUsage", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyDataBase64")
    def reset_key_data_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyDataBase64", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="certDisplayId")
    def cert_display_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certDisplayId"))

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="parentCert")
    def parent_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentCert"))

    @builtins.property
    @jsii.member(jsii_name="readingToken")
    def reading_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readingToken"))

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
    @jsii.member(jsii_name="csrDataBase64Input")
    def csr_data_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "csrDataBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="extendedKeyUsageInput")
    def extended_key_usage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "extendedKeyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyDataBase64Input")
    def key_data_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyDataBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__dd73ad196b92b013fdfccab43c1537fa72936a269f46c0097047621cc39f6906)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value)

    @builtins.property
    @jsii.member(jsii_name="certIssuerName")
    def cert_issuer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certIssuerName"))

    @cert_issuer_name.setter
    def cert_issuer_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__514ee90cdb3ac035666bf1b92bbf54be2a76feaf0b90655af5d5eb1c042a4746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certIssuerName", value)

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a3af91a0a184677d59b2a4e27f4a80fc9142ed24efc0a2d28aa5043c02036b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value)

    @builtins.property
    @jsii.member(jsii_name="csrDataBase64")
    def csr_data_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "csrDataBase64"))

    @csr_data_base64.setter
    def csr_data_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca6c5be576a096c7955707fa70737170f2f38433c64ad42ffab20ac84afef0a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "csrDataBase64", value)

    @builtins.property
    @jsii.member(jsii_name="extendedKeyUsage")
    def extended_key_usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "extendedKeyUsage"))

    @extended_key_usage.setter
    def extended_key_usage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0af4885a9e36c517fd7008b24f9e45dfd9e857edb12fb490ac157cec463bb3a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extendedKeyUsage", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__180fd0c2e1d5f643dcffd75a74cae4bb4adb7b18fb17fa8b624fe9810c209496)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="keyDataBase64")
    def key_data_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyDataBase64"))

    @key_data_base64.setter
    def key_data_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e94ccd524d2f78201037a16690e0e14b173febfb799f7ea9bdceba2fd30e9e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyDataBase64", value)

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa7a88b175474d635d3fb381a9f36d7ee3404b6655d0887a671926c8b08666c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value)

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__916c5c9daeddcf33851ba1e35e33bf9bcab6efe7a789a50d70d8e5701d6388be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessPkiCertificate.DataAkeylessPkiCertificateConfig",
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
        "csr_data_base64": "csrDataBase64",
        "extended_key_usage": "extendedKeyUsage",
        "id": "id",
        "key_data_base64": "keyDataBase64",
        "ttl": "ttl",
        "uri_sans": "uriSans",
    },
)
class DataAkeylessPkiCertificateConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        csr_data_base64: typing.Optional[builtins.str] = None,
        extended_key_usage: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_data_base64: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[jsii.Number] = None,
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
        :param cert_issuer_name: The name of the PKI certificate issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#cert_issuer_name DataAkeylessPkiCertificate#cert_issuer_name}
        :param alt_names: The Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#alt_names DataAkeylessPkiCertificate#alt_names}
        :param common_name: The common name to be included in the PKI certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#common_name DataAkeylessPkiCertificate#common_name}
        :param csr_data_base64: Certificate Signing Request contents encoded in base64 to generate the certificate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#csr_data_base64 DataAkeylessPkiCertificate#csr_data_base64}
        :param extended_key_usage: A comma-separated list of extended key usage requests which will be used for certificate issuance. Supported values: 'clientauth', 'serverauth'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#extended_key_usage DataAkeylessPkiCertificate#extended_key_usage}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#id DataAkeylessPkiCertificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_data_base64: pki key file contents encoded using Base64. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#key_data_base64 DataAkeylessPkiCertificate#key_data_base64}
        :param ttl: Updated certificate lifetime in seconds (must be less than the Certificate Issuer default TTL). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#ttl DataAkeylessPkiCertificate#ttl}
        :param uri_sans: The URI Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#uri_sans DataAkeylessPkiCertificate#uri_sans}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__521c239b41e1ae9866388275113c60a4a99d355bfffa9f939ea588290698e792)
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
            check_type(argname="argument csr_data_base64", value=csr_data_base64, expected_type=type_hints["csr_data_base64"])
            check_type(argname="argument extended_key_usage", value=extended_key_usage, expected_type=type_hints["extended_key_usage"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_data_base64", value=key_data_base64, expected_type=type_hints["key_data_base64"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
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
        if csr_data_base64 is not None:
            self._values["csr_data_base64"] = csr_data_base64
        if extended_key_usage is not None:
            self._values["extended_key_usage"] = extended_key_usage
        if id is not None:
            self._values["id"] = id
        if key_data_base64 is not None:
            self._values["key_data_base64"] = key_data_base64
        if ttl is not None:
            self._values["ttl"] = ttl
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#cert_issuer_name DataAkeylessPkiCertificate#cert_issuer_name}
        '''
        result = self._values.get("cert_issuer_name")
        assert result is not None, "Required property 'cert_issuer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alt_names(self) -> typing.Optional[builtins.str]:
        '''The Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#alt_names DataAkeylessPkiCertificate#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''The common name to be included in the PKI certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#common_name DataAkeylessPkiCertificate#common_name}
        '''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def csr_data_base64(self) -> typing.Optional[builtins.str]:
        '''Certificate Signing Request contents encoded in base64 to generate the certificate with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#csr_data_base64 DataAkeylessPkiCertificate#csr_data_base64}
        '''
        result = self._values.get("csr_data_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extended_key_usage(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of extended key usage requests which will be used for certificate issuance. Supported values: 'clientauth', 'serverauth'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#extended_key_usage DataAkeylessPkiCertificate#extended_key_usage}
        '''
        result = self._values.get("extended_key_usage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#id DataAkeylessPkiCertificate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_data_base64(self) -> typing.Optional[builtins.str]:
        '''pki key file contents encoded using Base64.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#key_data_base64 DataAkeylessPkiCertificate#key_data_base64}
        '''
        result = self._values.get("key_data_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[jsii.Number]:
        '''Updated certificate lifetime in seconds (must be less than the Certificate Issuer default TTL).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#ttl DataAkeylessPkiCertificate#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[builtins.str]:
        '''The URI Subject Alternative Names to be included in the PKI certificate (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/pki_certificate#uri_sans DataAkeylessPkiCertificate#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessPkiCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAkeylessPkiCertificate",
    "DataAkeylessPkiCertificateConfig",
]

publication.publish()

def _typecheckingstub__d396b82e29e1c3a9e7a62408dec78502c88f273914b2cdae3d9b68a3f0438bc4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cert_issuer_name: builtins.str,
    alt_names: typing.Optional[builtins.str] = None,
    common_name: typing.Optional[builtins.str] = None,
    csr_data_base64: typing.Optional[builtins.str] = None,
    extended_key_usage: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_data_base64: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__1a57c367cedf25806a8100d9a730d91f123f6546c8c073a7e2816bc169ef0701(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd73ad196b92b013fdfccab43c1537fa72936a269f46c0097047621cc39f6906(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__514ee90cdb3ac035666bf1b92bbf54be2a76feaf0b90655af5d5eb1c042a4746(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a3af91a0a184677d59b2a4e27f4a80fc9142ed24efc0a2d28aa5043c02036b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca6c5be576a096c7955707fa70737170f2f38433c64ad42ffab20ac84afef0a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0af4885a9e36c517fd7008b24f9e45dfd9e857edb12fb490ac157cec463bb3a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__180fd0c2e1d5f643dcffd75a74cae4bb4adb7b18fb17fa8b624fe9810c209496(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e94ccd524d2f78201037a16690e0e14b173febfb799f7ea9bdceba2fd30e9e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa7a88b175474d635d3fb381a9f36d7ee3404b6655d0887a671926c8b08666c8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__916c5c9daeddcf33851ba1e35e33bf9bcab6efe7a789a50d70d8e5701d6388be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__521c239b41e1ae9866388275113c60a4a99d355bfffa9f939ea588290698e792(
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
    csr_data_base64: typing.Optional[builtins.str] = None,
    extended_key_usage: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_data_base64: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[jsii.Number] = None,
    uri_sans: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
